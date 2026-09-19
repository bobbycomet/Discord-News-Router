"""Matching logic and message delivery shared by the setup and router cogs."""

import asyncio
import json
import re

import discord

MAX_USER_IDS = 10
MAX_SOURCE_IDS = 20

# Specificity tiers. A message is delivered to every mapping in the *highest*
# tier it matched, so two equally-specific mappings both get a copy, but a
# broad catch-all mapping never steals a post from a precisely-targeted one.
TIER_SOURCE = 3   # matched because the post came from a declared source server/channel
TIER_KEYWORD = 2  # matched because a keyword hit
TIER_AUTHOR = 1   # matched on author ID alone


def row_get(row, key, default=None):
    """sqlite3.Row has no .get(); also tolerates a pre-migration row."""
    try:
        value = row[key]
    except (IndexError, KeyError):
        return default
    return default if value is None else value


def _parse_int_list(raw: str, limit: int) -> list[int]:
    ids = []
    for chunk in re.split(r"[,\s]+", (raw or "").strip()):
        if not chunk:
            continue
        chunk = chunk.strip("<@!#>")
        if chunk.isdigit():
            ids.append(int(chunk))
    return list(dict.fromkeys(ids))[:limit]


def parse_user_ids(raw: str) -> list[int]:
    """Parse a free-text blob of user IDs (comma/space/mention separated) into up to 10 ints."""
    return _parse_int_list(raw, MAX_USER_IDS)


def parse_source_ids(raw: str) -> list[int]:
    """Parse source *server* and/or *channel* IDs. Either kind may be listed."""
    return _parse_int_list(raw, MAX_SOURCE_IDS)


def parse_keywords(raw: str) -> list[str]:
    if not raw:
        return []
    return [k.strip() for k in raw.split(",") if k.strip()]


def parse_mapping_ids(raw: str) -> list[int] | None:
    """Parse a comma/space-separated list of mapping IDs for bulk commands.

    Returns None for "all" (case-insensitive) or an empty/blank string,
    meaning "every mapping" — the caller decides what that means.
    """
    raw = (raw or "").strip()
    if not raw or raw.lower() == "all":
        return None
    ids = []
    for chunk in re.split(r"[,\s]+", raw):
        if chunk.isdigit():
            ids.append(int(chunk))
    return ids


async def resolve_user_label(bot: discord.Client, user_id: int) -> str:
    """Best-effort "Name (`id`)" label for a raw user ID.

    Tries the client cache first, then a live fetch (works even for users the
    bot shares no server with — user profiles are public). Falls back to just
    the ID if the account no longer exists or Discord can't be reached.
    """
    user = bot.get_user(user_id)
    if user is None:
        try:
            user = await bot.fetch_user(user_id)
        except (discord.NotFound, discord.HTTPException):
            return f"`{user_id}`"
    name = getattr(user, "global_name", None) or user.name
    return f"{name} (`{user_id}`)"


async def resolve_user_labels(bot: discord.Client, user_ids) -> dict:
    """resolve_user_label for many IDs at once, deduplicated, fetched concurrently."""
    unique = list(dict.fromkeys(user_ids))
    results = await asyncio.gather(*(resolve_user_label(bot, uid) for uid in unique))
    return dict(zip(unique, results))


# ---------------------------------------------------------------- inspection


def message_snapshots(message: discord.Message):
    """Payloads of a forwarded message. Empty list on older discord.py or a
    normal (non-forwarded) message."""
    return list(getattr(message, "message_snapshots", None) or [])


def _text_parts(obj) -> list[str]:
    parts = [getattr(obj, "content", "") or ""]
    for embed in getattr(obj, "embeds", None) or []:
        if embed.title:
            parts.append(str(embed.title))
        if embed.description:
            parts.append(str(embed.description))
        if embed.author and embed.author.name:
            parts.append(str(embed.author.name))
        if embed.footer and embed.footer.text:
            parts.append(str(embed.footer.text))
        for field in embed.fields:
            parts.append(f"{field.name} {field.value}")
        if embed.url:
            parts.append(str(embed.url))
    return parts


def message_text_blob(message: discord.Message) -> str:
    """All searchable text on a message, *including* the payload of a forward.

    A Discord "Forward" carries no content of its own — the real text lives in
    `message_snapshots`. Ignoring that was one reason keyword matching silently
    did nothing on forwarded posts.
    """
    parts = _text_parts(message)
    for snap in message_snapshots(message):
        parts.extend(_text_parts(snap))
    return "\n".join(p for p in parts if p).lower()


def message_origin(message: discord.Message) -> tuple[int | None, int | None]:
    """Where the post actually came from, as (guild_id, channel_id).

    Both a channel-follow crosspost and a user forward set `message.reference`
    to the *original* message, so this resolves to the source server/channel
    rather than the hub. Falls back to the hub itself for a locally posted
    message.
    """
    ref = message.reference
    if ref is not None and ref.channel_id:
        guild_id = ref.guild_id
        if guild_id is None and message.guild is not None:
            guild_id = message.guild.id
        return guild_id, ref.channel_id
    return (message.guild.id if message.guild else None), message.channel.id


def origin_ids(message: discord.Message) -> set[int]:
    return {i for i in message_origin(message) if i}


def describe_origin(message: discord.Message) -> str:
    guild_id, channel_id = message_origin(message)
    return f"server `{guild_id or '?'}` / channel `{channel_id or '?'}`"


# ------------------------------------------------------------------ matching


def evaluate_mapping(mapping, message: discord.Message, origins: set[int], text: str) -> int | None:
    """Return the specificity tier this mapping matched at, or None."""
    user_ids = json.loads(row_get(mapping, "user_ids", "[]"))
    source_ids = json.loads(row_get(mapping, "source_ids", "[]"))
    if not user_ids and not source_ids:
        return None  # a mapping with no filters at all would swallow everything

    if user_ids and message.author.id not in user_ids:
        return None

    source_hit = False
    if source_ids:
        if not (origins & set(source_ids)):
            return None
        source_hit = True

    keywords = [k.lower() for k in json.loads(row_get(mapping, "keywords", "[]"))]
    keyword_hit = any(kw in text for kw in keywords) if keywords else False
    if row_get(mapping, "keyword_mode", 0) and keywords and not keyword_hit:
        return None

    if source_hit:
        return TIER_SOURCE
    if keyword_hit:
        return TIER_KEYWORD
    return TIER_AUTHOR


def find_matching_mappings(mappings, message: discord.Message) -> list:
    """Every mapping that should receive this message.

    Returns all matches at the highest tier reached — so fan-out to several
    destinations works, while a broad author-only mapping is skipped whenever a
    source- or keyword-specific mapping also matched.
    """
    origins = origin_ids(message)
    text = message_text_blob(message)

    by_tier: dict[int, list] = {}
    for mapping in mappings:
        tier = evaluate_mapping(mapping, message, origins, text)
        if tier is not None:
            by_tier.setdefault(tier, []).append(mapping)

    if not by_tier:
        return []
    return by_tier[max(by_tier)]


def explain_matching(mappings, message: discord.Message) -> list[tuple]:
    """(mapping, tier_or_None) for every mapping — used by /test and /scan."""
    origins = origin_ids(message)
    text = message_text_blob(message)
    return [(m, evaluate_mapping(m, message, origins, text)) for m in mappings]


def tier_label(tier: int | None) -> str:
    return {
        TIER_SOURCE: "source match",
        TIER_KEYWORD: "keyword match",
        TIER_AUTHOR: "author only",
    }.get(tier, "no match")


# ------------------------------------------------------------------ delivery


def build_thread_name(message: discord.Message) -> str:
    base = (message.content or "").strip()
    if not base:
        for snap in message_snapshots(message):
            base = (getattr(snap, "content", "") or "").strip()
            if base:
                break
    if not base and message.embeds:
        base = message.embeds[0].title or message.embeds[0].description or ""
    base = base.replace("\n", " ").strip()
    if not base:
        base = f"Update {message.created_at:%Y-%m-%d %H:%M}"
    return base[:95]


def _payload(message: discord.Message):
    """Content/embeds/attachments to copy, preferring a forward's snapshot."""
    content = message.content or ""
    embeds = list(message.embeds)
    attachments = list(message.attachments)
    if not content and not embeds:
        for snap in message_snapshots(message):
            content = getattr(snap, "content", "") or ""
            embeds = list(getattr(snap, "embeds", None) or [])
            attachments = list(getattr(snap, "attachments", None) or [])
            if content or embeds or attachments:
                break
    return content, embeds, attachments


async def deliver_message(bot: discord.Client, message: discord.Message, destination_channel_id: int):
    """
    Forward/copy a hub message into one mapped destination.

    Returns (ok: bool, info: str).
    """
    destination = bot.get_channel(destination_channel_id)
    if destination is None:
        try:
            destination = await bot.fetch_channel(destination_channel_id)
        except discord.HTTPException as e:
            return False, f"Could not access destination channel {destination_channel_id}: {e}"

    try:
        if isinstance(destination, discord.ForumChannel):
            content, embeds, attachments = _payload(message)
            files = [await a.to_file() for a in attachments]
            thread_with_message = await destination.create_thread(
                name=build_thread_name(message),
                content=content or (None if embeds else "\u200b"),
                embeds=embeds or discord.utils.MISSING,
                files=files or discord.utils.MISSING,
            )
            return True, f"Created forum post {thread_with_message.thread.mention} in {destination.mention}"

        try:
            await message.forward(destination)
            return True, f"Forwarded to {destination.mention}"
        except AttributeError:
            pass  # older discord.py without native forward support
        except discord.HTTPException:
            pass  # fall through to manual copy

        content, embeds, attachments = _payload(message)
        files = [await a.to_file() for a in attachments]
        await destination.send(
            content=content or None,
            embeds=embeds or None,
            files=files or None,
        )
        return True, f"Copied to {destination.mention}"

    except discord.Forbidden:
        return False, "Missing permissions to post in the destination channel."
    except discord.HTTPException as e:
        return False, f"Discord error while delivering: {e}"


async def deliver_to_mappings(bot: discord.Client, message: discord.Message, mappings) -> list[tuple]:
    """Deliver one message to every matched mapping, de-duplicating destinations.

    Returns [(mapping, ok, info), ...].
    """
    results = []
    seen: dict[int, str] = {}
    for mapping in mappings:
        dest_id = mapping["destination_channel_id"]
        if dest_id in seen:
            results.append((mapping, True, f"Skipped — same destination as {seen[dest_id]}"))
            continue
        ok, info = await deliver_message(bot, message, dest_id)
        if ok:
            seen[dest_id] = f"mapping #{mapping['id']}"
        results.append((mapping, ok, info))
    return results

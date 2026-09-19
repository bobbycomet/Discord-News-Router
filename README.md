# Discord News Router Bot

## What this bot does

Discord's **Follow Channel** feature lets your server subscribe to another
server's announcement channel. The catch: Discord only lets you follow into a
regular text channel. It will not let you follow into a **forum channel** or a
thread.

This bot works around that. You follow the source channels into one ordinary
"hub" text channel, and the bot watches the hub. Every time a post lands there,
the bot automatically sends it on to wherever you want it to go: a new post in
a forum, an existing thread, or a normal text channel. Set it up once per channel
you want tracked (mapped), and let the bot handle the rest.

> This bot is meant to be hosted per server, and is not hosted at the moment for 
multiple servers by anyone. It lives as source code. If the bot grows in community 
need and funding is available for it, then I will do so at that time.

A few things worth knowing up front:

- **It only routes.** It doesn't lock you into forums. If you'd rather have
  news land in a plain text channel, point the rule at a text channel and the
  post is forwarded there instead.
- **One hub in, many destinations out.** Every followed server funnels into the
  same hub, and the bot sorts posts by *who* posted them and *where they came
  from*.
- **You manage it from Discord.** Slash commands and pop-up forms create and
  edit the routing rules. There are no config files to hand-edit.
- **It has a manual failsafe.** If Discord's automated follow ever hiccups,
  your mods, admins, and server owner can forward a post into the hub by hand
  and the bot still routes it (see
  [Adding mods, admins and server owner](#adding-mods-admins-and-server-owner)).

```
Source server's news channel
        │  (Follow Channel, done by a human, no bot involved)
        ▼
  Your hub channel  ──▶  the bot reads it  ──▶  forum post, thread, or text channel
```

---

## Table of contents

**Getting started**

- [Setting up the bot](#setting-up-the-bot)
- [Using the bot in Discord](#using-the-bot-in-discord)
- [Getting the user ID right](#getting-the-user-id-right)

**How it behaves**

- [How routing decides](#how-routing-decides)
- [Adding mods, admins and server owner](#adding-mods-admins-and-server-owner)
- [Commands](#commands)
- [Troubleshooting](#troubleshooting)

**Technical details**

- [Architecture](#architecture)
- [Storage](#storage)
- [Deploying with systemd](#deploying-with-systemd)
- [Modifying the code](#modifying-the-code)

---

## Setting up the bot

Requires **Python 3.10+** (`X | Y` union hints) and **discord.py 2.5+** for
forward-snapshot support. On older discord.py the snapshot code is skipped
safely, origin matching still works, but keyword matching can't see the text
of forwarded posts.

### 1. Create the bot in the Discord Developer Portal

1. Create an application at https://discord.com/developers/applications.
2. **Bot** tab → Reset Token → copy it; you'll paste it into `.env` in a
   moment as `DISCORD_TOKEN`.
3. Still on the **Bot** tab, enable the **Message Content Intent**, required,
   the bot reads hub message content to route it.
4. **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `View Channels`, `Send Messages`, `Embed Links`,
     `Attach Files`, `Read Message History`, `Create Public Threads`,
     `Send Messages in Threads`, `Manage Messages`
5. Open the generated URL and invite the bot, **only to the server that
   receives the follows.**

### 2. Install and run it

```bash
cd discord-news-router

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env   # DISCORD_TOKEN, optionally GUILD_ID for instant command sync

python bot.py
```

With `GUILD_ID` set, slash commands appear in that server instantly. Without
it, they sync globally and can take up to an hour to show up the first time.

To keep the bot running permanently on a Linux server, see
[Deploying with systemd](#deploying-with-systemd).

---

## Using the bot in Discord

### 1. Follow the source channels

In each *source* server, right-click their announcement/news channel →
**Follow** → pick your hub channel. Repeat for every server you want to track.
They all funnel into one hub channel here.

> The bot does **not** need to be in the source servers. Following is a human
> action performed with Manage Webhooks permission in *your* server. The bot
> only ever reads your hub.

### 2. Point the bot at the hub

```
/newsrouter sethub channel:#news-hub
```

### 3. Wait for real posts, then scan

Let at least one real post arrive from each source, then run:

```
/newsrouter scan limit:100
```

This lists every distinct (author, origin server, origin channel) seen in
recent hub history, with counts, and flags forwarded posts. These are the
actual IDs your rules need, **don't guess them** (see the next section).

### 4. Create a mapping per destination

```
/newsrouter addmapping destination:#game-news-forum
```

A modal opens:

- **Mapping name**, anything readable; it's what `listmappings` and error
  notices show.
- **Source user ID(s)**, paste from `/newsrouter scan`.
- **Origin server and/or channel ID(s) (Channel IDs are recommended for full control)**, 
  paste from `/newsrouter scan`. Use the *server* ID to capture everything that 
  server publishes; use the *channel* ID when one server has several news channels 
  you want split apart.
- **Keywords**, optional, only if you need to split one source's posts by
  topic.
- **Thread ID**, optional; overrides the destination picker to target one
  specific existing forum thread. Right-click the thread → **Copy Thread ID**
  (Developer Mode on).
- **Why are Channel IDs recommended?** Because having the server ID post everything
  means everything, and you may not want things like the devlogs. By doing a mapping 
  per channel, you can add a gift code mapping, announcement mapping, socials mapping, etc.
  They can all go to the same location, but this allows you to control what
  and where things are posted.

If the destination is a **forum channel**, each routed post becomes a new forum
thread. If it's a text channel or a specific thread, the post is forwarded 1:1.

### 5. Verify before relying on it

```
/test user_id:<id> dry_run:true
```

This prints the origin of the newest post from that ID, then every mapping,
whether it matched, at what tier, and which would receive it, without posting
anything. Drop `dry_run` to actually route it.

### 6. Adjust

`/newsrouter listmappings` to review, `/newsrouter settings <id>` to reopen the
modal and edit filters, `/newsrouter editmapping <id>` (simple numbers are the 
ID, so 1, 2, 3, etc.) to also change the destination.

---

## Getting the user ID right

**This is the single most common setup mistake.** The author ID you see in the
source server is usually *not* the author ID that arrives in your hub.

Many servers don't post announcements from a staff account, they use an
announcement bot. So in the source server, the post is authored by something
like **"announce"**. But Discord's channel-follow feature crossposts through a
webhook, and the identity that lands in your hub is the *source channel's*
identity, not the bot's. Concretely:

| Where you look | Who appears as the author |
|---|---|
| In the **Aniimo** server's news channel | `announce` (their announcement bot) |
| In **your hub channel**, after following | **Aniimo** |

If you copy the `announce` bot's ID, your mapping will never match anything,
that bot doesn't exist in your server and its ID never appears in your hub.
You need **Aniimo's** ID: the one attached to the message sitting in *your*
channel.

### Getting it right

1. Enable **Developer Mode** (User Settings → Advanced → Developer Mode).
2. Wait for a real post to arrive in your hub channel, a test post from the
   source, or just the next genuine announcement.
3. Right-click **that message in your hub** → **Copy User ID**. Never copy from
   the source server.
4. Or skip the right-clicking entirely and run `/newsrouter scan`, which reads
   the IDs straight off the messages already in your hub.
5. Confirm with `/test user_id:<id> dry_run:true` before you rely on it.

The same principle applies to the origin fields: those IDs describe the
*source* server and channel and are read out of the crosspost payload, which is
why `/newsrouter scan` can report them even though the bot isn't a member
there. It can only show you the raw numbers, not the server names, name your
mappings clearly so you can tell them apart later.

Because origin IDs now do most of the separating work, you can often leave the
user ID field empty and match purely on origin channel. That's the cleanest
setup when one followed channel maps to exactly one destination, and it's
immune to a source server changing which identity publishes their news.

> **Removing a mod** Just use the `/newsrouter removeuser user_id:<id> mapping_ids:all` 
  and remove their ID, or to add them if you get new team members 
  `/newsrouter adduser user_id:<id> mapping_ids:all`. You won't have to do them one by one.

---

## How routing decides

Every mapping has three optional filters. A mapping matches only if **all** the
filters it actually sets are satisfied:

| Filter | Meaning | Leave empty to… |
|---|---|---|
| **User IDs** | up to 10 author IDs, as they appear in *your hub* | match any author |
| **Origin IDs** | source server and/or source channel IDs the post must come from | match any origin |
| **Keywords** | comma-separated; at least one must appear in the text | not require keywords |

A mapping must set at least one filter, a rule with none would swallow every
post in the hub, so it's rejected.

Matches are then ranked by **specificity tier**:

| Tier | Matched because |
|---|---|
| **3** | the post came from one of the mapping's origin IDs |
| **2** | a keyword hit |
| **1** | author ID alone |

**The message is delivered to every mapping in the highest tier reached.**

That matters when the same person or announcement identity feeds several
mappings:

- Two mappings pinned to different source servers never compete, each only
  matches its own origin, so both destinations stay live.
- Two mappings at the *same* tier both receive a copy (fan-out), deduplicated
  by destination.
- A broad author-only catch-all never steals a post from a source-pinned
  mapping, but still catches anything the specific rules missed.

Keyword matching is implicit: list keywords and a hit is required; leave the
field blank and keywords are ignored entirely.

---

## Adding mods, admins and server owner

Discord's automated channel follow is reliable, but it isn't perfect. Every so
often a crosspost can be delayed or dropped, for example because of rate
limiting or a Discord-side hiccup. This section is the **failsafe** for those
rare moments.

You can add the user IDs of your own **mods, admins, and server owner** to your
mappings. When one of those people **manually forwards** a post into the hub
channel, the bot picks it up like any other hub post and automatically
forwards it on to the destination that mapping points at. The person doing the
forwarding only has to get the message into the hub; the bot handles the rest.

### Setting it up

1. **Collect the IDs.** With Developer Mode on, right-click each mod, admin, or
   yourself → **Copy User ID**. These are the same IDs Discord uses everywhere,
   so you can copy them from any message or the member list.
2. **Add them to the mapping.** Put the IDs in the mapping's **Source user
   ID(s) (the same location as the author ID)** field, either when creating it 
   with `/newsrouter addmapping` or by editing it later with `/newsrouter settings <id>`. 
   A mapping holds up to 10 user IDs.
3. **Keep the original ID in the list too.** Leave the followed channel's
   identity (the ID from [Getting the user ID right](#getting-the-user-id-right))
   in the same field, so automated posts keep routing exactly as before. The
   list is "any of these", so mods and the automated identity can sit side by
   side.
4. **Repeat for each destination** a mod should be able to trigger. IDs are set
   per mapping, so a mod only fills in for the mappings they're listed on.

### Using the failsafe

When a post didn't arrive automatically, a listed mod, admin, or the owner
takes the original message, chooses **Forward**, and sends it to the hub
channel. The bot sees a post from a trusted ID and routes it to the designated
destination, forum post, thread, or text channel, just as it would have for the
automated crosspost.

### Things to keep in mind

- **Origin filters still apply.** A forwarded message carries the location of
  the original post, so if a mapping has Origin IDs set, the forward matches as
  long as it came from that source channel. If you want a mod to be able to
  forward something from anywhere, make sure they are added in the same field as 
  the Author IDs.
- **Only add people you trust.** The bot matches on user IDs alone; it doesn't
  check roles or permissions. Anyone whose ID is on a mapping can route posts
  through it. Remove an ID by editing the mapping.
- **Keep the hub for follows and forwards.** Because listed IDs are routed
  automatically, a listed person chatting in the hub could be routed too. Ask
  your team to use the hub only for forwarding.
- **Watch for double posts.** If Discord's delayed crosspost arrives *after* a
  manual forward, the destination gets both. Check the destination first and
  forward only if the post really is missing.
- **Test it.** `/test user_id:<mod id> dry_run:true` shows how a forward from
  that person would be matched and where it would go, without posting.

---

## Commands

All commands require the **Manage Server** permission. All replies are
ephemeral.

| Command | Purpose |
|---|---|
| `/newsrouter sethub` | Set the hub channel (native channel picker) |
| `/newsrouter scan` | List author + origin server/channel IDs seen in recent hub history |
| `/newsrouter addmapping` | Add a routing rule (channel picker + modal) |
| `/newsrouter editmapping` | Edit a rule, including its destination |
| `/newsrouter removemapping` | Delete a rule by ID |
| `/newsrouter listmappings` |Show all rules with their filters (user IDs shown with user names, if no name is present, it is the origin server user the posts come from) |
| `/newsrouter settings` | Edit a rule's filters without touching the destination |
| `/newsrouter adduser` | Add one user ID to several mappings (or all) in one command |
| `/newsrouter removeuser` | Remove one user ID from several mappings (or all) in one command |
| `/test` | Replay the newest hub post from a user ID; `dry_run:true` reports matches without posting |

---

## Troubleshooting

**Nothing routes at all.** Check the hub is set (`/newsrouter listmappings`
won't tell you, `/newsrouter scan` will fail loudly if it isn't), and that the
Message Content intent is enabled in the Developer Portal, not just in code.

**A mapping never fires.** Almost always the wrong user ID, see the
announcement-bot section above. Run `/newsrouter scan` and compare against what
`listmappings` shows.

**A manual forward from a mod or admin isn't routing.** Confirm their user ID
is in the mapping's user ID field (`/newsrouter listmappings`), and that the
mapping's origin filter, if it has one, matches where the forwarded post came
from. Then run `/test user_id:<their id> dry_run:true` to see exactly how it's
being matched.

**One mapping receives everything.** That mapping is matching at a higher tier
than the others, or it's the only one matching at all. Run
`/test user_id:<id> dry_run:true`, it prints each mapping's tier and marks
anything matched-but-outranked.

**Posts land in two places.** Two mappings are tied at the same tier. Add an
origin ID to the one that should be more specific, or narrow its keywords.

**Forum posts appear with an empty title.** The source post had no text content
and no embed title to build a thread name from; the bot falls back to a
timestamped name.

**Permission errors in the hub.** The bot posts failure notices into the hub
channel (auto-deleting after 30s). Give it Send Messages there, and Create
Public Threads plus Send Messages in Threads on every destination forum.

---

# Technical details

Everything below is for people who want to understand, modify, or host the bot.
You don't need any of it to use it.

## Architecture

```
discord-news-router/
├── bot.py                  # entrypoint: intents, cog loading, slash-command sync
├── database.py             # aiosqlite access layer + schema migrations
├── utils.py                # origin extraction, matching tiers, delivery
├── cogs/
│   ├── setup_cog.py        # /newsrouter group, sethub, addmapping, editmapping,
│   │                       #   removemapping, listmappings, settings, scan
│   └── router_cog.py       # on_message hub watcher + /test
├── requirements.txt
├── .env.example
├── .gitignore
└── systemd/
    └── discord-news-router.service
```

### The pieces

**`bot.py`**, subclasses `commands.Bot`. In `setup_hook()` it opens the
database, loads both cogs, then syncs the command tree (to a single guild if
`GUILD_ID` is set, which is instant; globally otherwise, which can take up to
an hour to propagate). It needs the **Message Content intent**, because
routing decisions read the text of hub posts. A tree-level error handler turns
permission failures and unhandled exceptions into ephemeral replies instead of
silent no-ops.

**`database.py`**, a thin async wrapper over one SQLite file. Two tables:
`settings` (one row per guild, holding the hub channel ID) and `mappings` (one
row per routing rule). List-shaped fields, user IDs, origin IDs, keywords,
are stored as JSON arrays inside TEXT columns, so you get a durable database
without a second file to keep in sync. `connect()` runs `PRAGMA table_info`
and applies any missing column migrations in place, so upgrading is just
restarting the bot.

**`utils.py`**, the brain, kept out of the cogs so both the automatic watcher
and `/test` run the exact same logic:

- `message_origin()` reads `message.reference` to recover the **source** guild
  and channel a post came from. Both channel-follow crossposts and user
  forwards populate this with the original message's location, so the bot can
  tell two sources apart without ever being in those servers.
- `message_text_blob()` gathers searchable text: content, embed titles,
  descriptions, authors, footers, and fields, plus `message_snapshots`, which
  is where a forwarded message's real content lives (it is *not* in
  `message.content`).
- `evaluate_mapping()` / `find_matching_mappings()` score every rule and return
  all winners (see [How routing decides](#how-routing-decides)).
- `deliver_message()` / `deliver_to_mappings()` do the posting: a new forum
  post if the destination is a forum, otherwise a native `Message.forward()`
  for 1:1 fidelity, falling back to a manual content/embeds/attachments copy.
  Destinations are deduplicated so two matching rules pointing at the same
  channel don't double-post.

**`cogs/setup_cog.py`**, all configuration. Destinations are picked with
Discord's native channel-select option on the slash command; everything else
comes from a modal (Discord modals are text-input only, max five fields).
Threads inside a forum can't appear in a channel picker at all, an API
limitation, so targeting one specific existing thread is done by pasting its
ID into the modal, which overrides the picker.

**`cogs/router_cog.py`**, the `on_message` listener that ignores everything
outside the hub channel, plus `/test`, which replays the newest matching hub
post through the real pipeline and reports per-mapping results.

### Request flow

```
Source server's announcement channel
        │  (a human clicks Follow, the bot is NOT involved)
        ▼
Discord webhook crossposts into your hub channel
        │                          (failsafe: a listed mod/admin/owner
        │                           forwards the post into the hub by hand)
        ▼
on_message  ── is this the hub channel? ── no ──▶ ignore
        │ yes
        ▼
db.list_mappings(guild)
        ▼
find_matching_mappings()
   ├── author ID filter
   ├── origin server/channel filter   ← from message.reference
   └── keyword filter                 ← from content + embeds + snapshots
        ▼
highest-tier matches (may be several)
        ▼
deliver_to_mappings() ──▶ forum post / forward / copy
```

---

## Storage

- **SQLite** (`router.db` by default) is the single source of truth, the hub
  channel setting plus every mapping row.
- User IDs, origin IDs, and keywords are **JSON arrays inside TEXT columns**
  (max 10 user IDs and 20 origin IDs per mapping), so the ID lists stay
  JSON-structured without a separate file to keep in sync.
- Schema changes are applied on connect via `PRAGMA table_info`; upgrading is
  just restarting the bot. Existing mappings keep working with empty origin
  lists, matching at tier 1.
- Secrets and config (bot token, optional dev guild ID, DB path) live in `.env`,
  never committed.

---

## Deploying with systemd

```bash
sudo mkdir -p /opt/discord-news-router
sudo cp -r . /opt/discord-news-router
cd /opt/discord-news-router

python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt

cp .env.example .env   # then edit with the real token
```

### Pick a user to run it as, and give that user permission

The service runs as a specific Linux user, and that user needs read access to
the venv and code and write access to `router.db`. You can reuse your own
login, or create a dedicated one:

```bash
# either: a dedicated system user (recommended)
sudo useradd --system --no-create-home discordbot

# or: your own user, skip useradd and just use your existing username below
```

Then hand that user (and its group) ownership of the whole deployment:

```bash
sudo chown -R discordbot:discordbot /opt/discord-news-router
# if using your own account instead, e.g.: sudo chown -R billy:billy /opt/discord-news-router
```

### Install and edit the unit file

```bash
sudo cp systemd/discord-news-router.service /etc/systemd/system/
sudo nano /etc/systemd/system/discord-news-router.service
```

Two placeholders in the file need editing before it will start:

- `User=`, the same user you `chown`'d the directory to above (e.g.
  `discordbot`, or use the `billy` example). Leaving this unset or wrong means the process
  can't read the venv/code or write `router.db`, and the service fails
  immediately.
- `WorkingDirectory=`, already set to `/opt/discord-news-router`; only change
  it if you deployed somewhere else, and update `EnvironmentFile=`/`ExecStart=`
  to match.

The bot's own secrets don't go in the unit file, `EnvironmentFile=` points at
your existing `.env`, so `DISCORD_TOKEN` etc. are loaded from there.

### Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now discord-news-router

sudo systemctl status discord-news-router
sudo journalctl -u discord-news-router -f
```

`systemctl enable` starts it on boot (`WantedBy=multi-user.target` plus
`After=`/`Wants=network-online.target` in the unit file mean it waits for
networking first); `Restart=on-failure` with `RestartSec=5` restarts it a few
seconds after a crash.

## Modifying the code

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. This was a deliberate choice to keep the project open and to prevent modified versions from being turned into closed-source hosted services.

You are free to modify and self-host the bot, subject to the terms of the AGPL-3.0. If you modify the bot and provide the modified version to users over a network, the AGPL's corresponding-source requirements apply to those modifications.

If you modify or redistribute this project, please retain the original copyright and license notices and credit the **Discord News Router** project. If you build a larger hosted service around it, I would appreciate clear attribution to this project as well.

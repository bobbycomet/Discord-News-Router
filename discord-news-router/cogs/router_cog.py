import json

import discord
from discord import app_commands
from discord.ext import commands

from utils import deliver_message, find_matching_mapping


class RouterCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Automatic operation: watch the hub channel and route matching posts."""
        if message.guild is None or message.author.id == self.bot.user.id:
            return

        hub_id = await self.bot.db.get_hub_channel(message.guild.id)
        if hub_id is None or message.channel.id != hub_id:
            return

        mappings = await self.bot.db.list_mappings(message.guild.id)
        mapping = find_matching_mapping(mappings, message)
        if mapping is None:
            return

        ok, info = await deliver_message(self.bot, message, mapping["destination_channel_id"])
        if not ok:
            try:
                await message.channel.send(
                    f"⚠️ Failed to route a message matched to mapping "
                    f"**#{mapping['id']} {mapping['name']}**: {info}",
                    delete_after=30,
                )
            except discord.HTTPException:
                pass

    @app_commands.command(
        name="test",
        description="Find the newest hub post from a given user ID and route it, to verify setup",
    )
    @app_commands.describe(user_id="The Discord user ID to search for in the hub channel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def test(self, interaction: discord.Interaction, user_id: str):
        await interaction.response.defer(ephemeral=True, thinking=True)

        if not user_id.isdigit():
            await interaction.followup.send("`user_id` must be a numeric Discord ID.", ephemeral=True)
            return
        uid = int(user_id)

        hub_id = await self.bot.db.get_hub_channel(interaction.guild_id)
        if hub_id is None:
            await interaction.followup.send(
                "No hub channel set yet. Run `/newsrouter sethub` first.", ephemeral=True
            )
            return

        hub_channel = interaction.guild.get_channel(hub_id)
        if hub_channel is None:
            try:
                hub_channel = await self.bot.fetch_channel(hub_id)
            except discord.HTTPException as e:
                await interaction.followup.send(f"Couldn't access the hub channel: {e}", ephemeral=True)
                return

        mappings = await self.bot.db.list_mappings(interaction.guild_id)
        matches_some_mapping = any(uid in json.loads(m["user_ids"]) for m in mappings)
        if not matches_some_mapping:
            await interaction.followup.send(
                f"No mapping currently contains user ID `{uid}`. Add one with `/newsrouter addmapping`.",
                ephemeral=True,
            )
            return

        found = None
        async for msg in hub_channel.history(limit=100):
            if msg.author.id == uid:
                found = msg
                break

        if found is None:
            await interaction.followup.send(
                f"Scanned the last 100 messages in {hub_channel.mention} and found none authored by ID `{uid}`.\n\n"
                f"**Note:** Discord's channel-follow feature crossposts messages via a webhook, which can "
                f"carry a different author ID than the original poster's account. Right-click a real crossposted "
                f"message in the hub and use *Copy User ID* (or check the author shown) to get the ID that will "
                f"actually appear here, then map that ID instead.",
                ephemeral=True,
            )
            return

        mapping = find_matching_mapping(mappings, found)
        if mapping is None:
            await interaction.followup.send(
                f"Found a message from `{uid}` but couldn't resolve it to a single mapping (ambiguous — "
                f"multiple mappings share this ID and keyword matching didn't find a hit). Adjust keywords "
                f"via `/newsrouter settings`.",
                ephemeral=True,
            )
            return

        ok, info = await deliver_message(self.bot, found, mapping["destination_channel_id"])
        status = "✅" if ok else "❌"
        await interaction.followup.send(
            f"{status} Test run on mapping **#{mapping['id']} {mapping['name']}**: {info}",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(RouterCog(bot))

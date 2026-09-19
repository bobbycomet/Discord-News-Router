import logging
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from database import Database

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")  # optional: speeds up slash command sync during dev/testing
DB_PATH = os.getenv("DB_PATH", "router.db")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("news_router")

intents = discord.Intents.default()
intents.message_content = True  # required: the bot reads content of hub-channel posts
intents.guilds = True


class NewsRouterBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!newsrouter-unused!", intents=intents, help_command=None)
        self.db: Database | None = None

    async def setup_hook(self):
        self.db = Database(DB_PATH)
        await self.db.connect()

        for ext in ("cogs.setup_cog", "cogs.router_cog"):
            await self.load_extension(ext)

        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            log.info("Synced %d commands to guild %s (instant)", len(synced), GUILD_ID)
        else:
            synced = await self.tree.sync()
            log.info("Synced %d global commands (can take up to ~1hr to propagate)", len(synced))

    async def close(self):
        if self.db:
            await self.db.close()
        await super().close()


bot = NewsRouterBot()


@bot.event
async def on_ready():
    log.info("Logged in as %s (%s)", bot.user, bot.user.id)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        msg = "You need the **Manage Server** permission to use this command."
    elif isinstance(error, app_commands.CommandOnCooldown):
        msg = str(error)
    else:
        msg = f"Something went wrong running that command: `{error}`"
        log.exception("Unhandled app command error", exc_info=error)

    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except discord.HTTPException:
        pass


def main():
    if not TOKEN:
        raise SystemExit("DISCORD_TOKEN is not set. Copy .env.example to .env and fill it in.")
    bot.run(TOKEN, log_handler=None)


if __name__ == "__main__":
    main()

"""
SQLite storage for the news router bot.

Design note: per-mapping user IDs, source IDs and keywords are stored as
JSON-encoded lists inside SQLite TEXT columns (rather than as separate
normalized rows or a flat JSON file on disk). This keeps everything in one
durable SQLite file while still giving you the "IDs live in JSON" structure.
"""

import json
from datetime import datetime, timezone

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    guild_id INTEGER PRIMARY KEY,
    hub_channel_id INTEGER
);

CREATE TABLE IF NOT EXISTS mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    destination_channel_id INTEGER NOT NULL,
    user_ids TEXT NOT NULL DEFAULT '[]',
    source_ids TEXT NOT NULL DEFAULT '[]',
    keyword_mode INTEGER NOT NULL DEFAULT 0,
    keywords TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL
);
"""

# Columns added after the first release, applied to existing router.db files.
MIGRATIONS = {
    "source_ids": "ALTER TABLE mappings ADD COLUMN source_ids TEXT NOT NULL DEFAULT '[]'",
}

MAX_USER_IDS = 10
MAX_SOURCE_IDS = 20


class Database:
    def __init__(self, path: str):
        self.path = path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self):
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        await self._migrate()
        await self._conn.commit()

    async def _migrate(self):
        cur = await self._conn.execute("PRAGMA table_info(mappings)")
        existing = {row["name"] for row in await cur.fetchall()}
        for column, statement in MIGRATIONS.items():
            if column not in existing:
                await self._conn.execute(statement)

    async def close(self):
        if self._conn:
            await self._conn.close()

    # ---------------- settings ----------------

    async def set_hub_channel(self, guild_id: int, channel_id: int):
        await self._conn.execute(
            "INSERT INTO settings (guild_id, hub_channel_id) VALUES (?, ?) "
            "ON CONFLICT(guild_id) DO UPDATE SET hub_channel_id = excluded.hub_channel_id",
            (guild_id, channel_id),
        )
        await self._conn.commit()

    async def get_hub_channel(self, guild_id: int) -> int | None:
        cur = await self._conn.execute(
            "SELECT hub_channel_id FROM settings WHERE guild_id = ?", (guild_id,)
        )
        row = await cur.fetchone()
        return row["hub_channel_id"] if row else None

    # ---------------- mappings ----------------

    async def add_mapping(
        self,
        guild_id: int,
        name: str,
        destination_channel_id: int,
        user_ids: list[int],
        keyword_mode: bool,
        keywords: list[str],
        source_ids: list[int] | None = None,
    ) -> int:
        cur = await self._conn.execute(
            "INSERT INTO mappings "
            "(guild_id, name, destination_channel_id, user_ids, source_ids, keyword_mode, keywords, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                guild_id,
                name,
                destination_channel_id,
                json.dumps(list(user_ids)[:MAX_USER_IDS]),
                json.dumps(list(source_ids or [])[:MAX_SOURCE_IDS]),
                int(keyword_mode),
                json.dumps(keywords),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await self._conn.commit()
        return cur.lastrowid

    async def update_mapping(self, mapping_id: int, **fields):
        if not fields:
            return
        cols, vals = [], []
        for key, value in fields.items():
            if key == "user_ids":
                value = json.dumps(list(value)[:MAX_USER_IDS])
            elif key == "source_ids":
                value = json.dumps(list(value)[:MAX_SOURCE_IDS])
            elif key == "keywords":
                value = json.dumps(list(value))
            elif key == "keyword_mode":
                value = int(value)
            cols.append(f"{key} = ?")
            vals.append(value)
        vals.append(mapping_id)
        await self._conn.execute(f"UPDATE mappings SET {', '.join(cols)} WHERE id = ?", vals)
        await self._conn.commit()

    async def remove_mapping(self, mapping_id: int):
        await self._conn.execute("DELETE FROM mappings WHERE id = ?", (mapping_id,))
        await self._conn.commit()

    async def get_mapping(self, mapping_id: int):
        cur = await self._conn.execute("SELECT * FROM mappings WHERE id = ?", (mapping_id,))
        return await cur.fetchone()

    async def list_mappings(self, guild_id: int):
        cur = await self._conn.execute(
            "SELECT * FROM mappings WHERE guild_id = ? ORDER BY id", (guild_id,)
        )
        return await cur.fetchall()

    # ---------------- bulk user-ID edits ----------------
    #
    # A mod/team member is often listed in several mappings at once (they post
    # news in more than one tracked server). These let you add or remove one
    # user ID everywhere in a guild's mappings in a single command instead of
    # opening each mapping's modal one at a time.

    async def bulk_add_user_id(
        self, guild_id: int, user_id: int, mapping_ids: list[int] | None = None
    ) -> list[int]:
        """Add user_id to every targeted mapping's user_ids list.

        mapping_ids=None means "every mapping in this guild". Returns the IDs
        of mappings that actually changed (already-present IDs are skipped).
        """
        rows = await self.list_mappings(guild_id)
        if mapping_ids is not None:
            wanted = set(mapping_ids)
            rows = [r for r in rows if r["id"] in wanted]

        changed = []
        for row in rows:
            ids = json.loads(row["user_ids"])
            if user_id in ids:
                continue
            ids.append(user_id)
            await self.update_mapping(row["id"], user_ids=ids)
            changed.append(row["id"])
        return changed

    async def bulk_remove_user_id(
        self, guild_id: int, user_id: int, mapping_ids: list[int] | None = None
    ) -> list[int]:
        """Remove user_id from every targeted mapping's user_ids list.

        mapping_ids=None means "every mapping in this guild". Returns the IDs
        of mappings that actually changed.
        """
        rows = await self.list_mappings(guild_id)
        if mapping_ids is not None:
            wanted = set(mapping_ids)
            rows = [r for r in rows if r["id"] in wanted]

        changed = []
        for row in rows:
            ids = json.loads(row["user_ids"])
            if user_id not in ids:
                continue
            ids = [i for i in ids if i != user_id]
            await self.update_mapping(row["id"], user_ids=ids)
            changed.append(row["id"])
        return changed

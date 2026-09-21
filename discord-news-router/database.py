"""
Per-guild SQLite storage for the news router bot.

Each Discord server gets its own folder and its own SQLite file:

    data/
      <guild_id>/
        router.db

Mapping IDs are the file's own AUTOINCREMENT column, so they're sequential
and independent per server: a brand-new server's first mapping is always
#1, never #11 because some other server already has ten. No guild_id column
is needed anywhere in here — a Database instance is already scoped to one
guild by which file it opened.
"""

import json
import os
from datetime import datetime, timezone

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    hub_channel_id INTEGER
);

CREATE TABLE IF NOT EXISTS mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    destination_channel_id INTEGER NOT NULL,
    user_ids TEXT NOT NULL DEFAULT '[]',
    source_ids TEXT NOT NULL DEFAULT '[]',
    keyword_mode INTEGER NOT NULL DEFAULT 0,
    keywords TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL
);
"""

MAX_USER_IDS = 10
MAX_SOURCE_IDS = 20


class Database:
    """One connection, scoped to a single guild's SQLite file."""

    def __init__(self, path: str):
        self.path = path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self):
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        await self._conn.commit()

    async def close(self):
        if self._conn:
            await self._conn.close()

    # ---------------- settings ----------------

    async def set_hub_channel(self, channel_id: int):
        await self._conn.execute(
            "INSERT INTO settings (id, hub_channel_id) VALUES (1, ?) "
            "ON CONFLICT(id) DO UPDATE SET hub_channel_id = excluded.hub_channel_id",
            (channel_id,),
        )
        await self._conn.commit()

    async def get_hub_channel(self) -> int | None:
        cur = await self._conn.execute("SELECT hub_channel_id FROM settings WHERE id = 1")
        row = await cur.fetchone()
        return row["hub_channel_id"] if row else None

    # ---------------- mappings ----------------

    async def add_mapping(
        self,
        name: str,
        destination_channel_id: int,
        user_ids: list[int],
        keyword_mode: bool,
        keywords: list[str],
        source_ids: list[int] | None = None,
    ) -> int:
        cur = await self._conn.execute(
            "INSERT INTO mappings "
            "(name, destination_channel_id, user_ids, source_ids, keyword_mode, keywords, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
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

    async def list_mappings(self):
        cur = await self._conn.execute("SELECT * FROM mappings ORDER BY id")
        return await cur.fetchall()

    # ---------------- bulk user-ID edits ----------------
    #
    # A mod/team member is often listed in several mappings at once. These
    # add or remove one user ID across many mappings in a single call instead
    # of opening each mapping's modal one at a time.

    async def bulk_add_user_id(self, user_id: int, mapping_ids: list[int] | None = None) -> list[int]:
        """mapping_ids=None means every mapping in this guild's file.
        Returns the IDs of mappings that actually changed."""
        rows = await self.list_mappings()
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

    async def bulk_remove_user_id(self, user_id: int, mapping_ids: list[int] | None = None) -> list[int]:
        """mapping_ids=None means every mapping in this guild's file.
        Returns the IDs of mappings that actually changed."""
        rows = await self.list_mappings()
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


class DatabaseManager:
    """Owns one Database per guild, opened lazily on first use and cached.

    A guild's file lives at ``<data_root>/<guild_id>/router.db``; the folder
    is created automatically the first time that guild touches the bot. This
    is the only thing that makes the bot multi-server-safe — matching and
    delivery in utils.py don't change at all, since each connection only ever
    sees one guild's rows to begin with.
    """

    def __init__(self, data_root: str = "data"):
        self.data_root = data_root
        self._dbs: dict[int, Database] = {}

    def _path_for(self, guild_id: int) -> str:
        guild_dir = os.path.join(self.data_root, str(guild_id))
        os.makedirs(guild_dir, exist_ok=True)
        return os.path.join(guild_dir, "router.db")

    async def get(self, guild_id: int) -> Database:
        db = self._dbs.get(guild_id)
        if db is None:
            db = Database(self._path_for(guild_id))
            await db.connect()
            self._dbs[guild_id] = db
        return db

    async def close_all(self):
        for db in self._dbs.values():
            await db.close()
        self._dbs.clear()

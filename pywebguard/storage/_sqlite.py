"""
SQLite3 storage backend for PyWebGuard with both sync and async support.
"""

import json
import sqlite3
import time
from typing import Any, Dict, Optional, Union

# Check if aiosqlite is installed
try:
    import aiosqlite

    AIOSQLITE_AVAILABLE = True
except ImportError:
    AIOSQLITE_AVAILABLE = False

from pywebguard.storage.base import BaseStorage, AsyncBaseStorage


class SQLiteStorage(BaseStorage):
    """
    SQLite3 storage backend (synchronous).
    """

    def __init__(
        self,
        db_path: str = ":memory:",
        table_name: str = "pywebguard",
        check_same_thread: bool = True,
    ):
        """
        Initialize the SQLite storage.

        Args:
            db_path: Path to SQLite database file (use :memory: for in-memory database)
            table_name: Name of the table to store values
            check_same_thread: If True, only the creating thread may use the connection
        """
        self.db_path = db_path
        self.table_name = table_name
        self.check_same_thread = check_same_thread
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database and create the table if it doesn't exist."""
        with sqlite3.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expiry REAL
                )
            """
            )
            conn.commit()

    def _clean_expired(self) -> None:
        """Remove expired entries from storage."""
        with sqlite3.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as conn:
            conn.execute(
                f"DELETE FROM {self.table_name} WHERE expiry <= ?", (time.time(),)
            )
            conn.commit()

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from storage.

        Args:
            key: The key to retrieve

        Returns:
            The stored value or None if not found
        """
        self._clean_expired()

        with sqlite3.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as conn:
            cursor = conn.execute(
                f"SELECT value FROM {self.table_name} WHERE key = ?", (key,)
            )
            result = cursor.fetchone()

            if result is None:
                return None

            try:
                return json.loads(result[0])
            except (json.JSONDecodeError, TypeError):
                return result[0]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage.

        Args:
            key: The key to store
            value: The value to store
            ttl: Time to live in seconds
        """
        # Convert complex types to JSON
        if not isinstance(value, (str, int, float, bool)) and value is not None:
            value = json.dumps(value)

        expiry = time.time() + ttl if ttl is not None else None

        with sqlite3.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as conn:
            conn.execute(
                f"""
                INSERT OR REPLACE INTO {self.table_name} (key, value, expiry)
                VALUES (?, ?, ?)
                """,
                (key, str(value), expiry),
            )
            conn.commit()

    def delete(self, key: str) -> None:
        """
        Delete a value from storage.

        Args:
            key: The key to delete
        """
        with sqlite3.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as conn:
            conn.execute(f"DELETE FROM {self.table_name} WHERE key = ?", (key,))
            conn.commit()

    def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter in storage.

        Args:
            key: The key to increment
            amount: The amount to increment by

        Returns:
            The new value
        """
        current = self.get(key) or 0
        if not isinstance(current, (int, float)):
            current = 0

        new_value = current + amount
        self.set(key, new_value)
        return new_value

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        self._clean_expired()

        with sqlite3.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as conn:
            cursor = conn.execute(
                f"SELECT 1 FROM {self.table_name} WHERE key = ?", (key,)
            )
            return cursor.fetchone() is not None

    def clear(self) -> None:
        """Clear all values from storage."""
        with sqlite3.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as conn:
            conn.execute(f"DELETE FROM {self.table_name}")
            conn.commit()


class AsyncSQLiteStorage(AsyncBaseStorage):
    """
    SQLite3 storage backend (asynchronous).
    """

    def __init__(
        self,
        db_path: str = ":memory:",
        table_name: str = "pywebguard",
        check_same_thread: bool = True,
    ):
        """
        Initialize the async SQLite storage.

        Args:
            db_path: Path to SQLite database file (use :memory: for in-memory database)
            table_name: Name of the table to store values
            check_same_thread: If True, only the creating thread may use the connection
        """
        if not AIOSQLITE_AVAILABLE:
            raise ImportError(
                "aiosqlite is not installed. Install it with 'pip install pywebguard[sqlite]' "
                "or 'pip install aiosqlite>=0.17.0'"
            )

        self.db_path = db_path
        self.table_name = table_name
        self.check_same_thread = check_same_thread
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Ensure the database is initialized."""
        if not self._initialized:
            await self._init_db()
            self._initialized = True

    async def _init_db(self) -> None:
        """Initialize the database and create the table if it doesn't exist."""
        async with aiosqlite.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as db:
            await db.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expiry REAL
                )
            """
            )
            await db.commit()

    async def _clean_expired(self) -> None:
        """Remove expired entries from storage."""
        await self._ensure_initialized()
        async with aiosqlite.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as db:
            await db.execute(
                f"DELETE FROM {self.table_name} WHERE expiry <= ?", (time.time(),)
            )
            await db.commit()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from storage asynchronously.

        Args:
            key: The key to retrieve

        Returns:
            The stored value or None if not found
        """
        await self._ensure_initialized()
        await self._clean_expired()

        async with aiosqlite.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as db:
            async with db.execute(
                f"SELECT value FROM {self.table_name} WHERE key = ?", (key,)
            ) as cursor:
                result = await cursor.fetchone()

                if result is None:
                    return None

                try:
                    return json.loads(result[0])
                except (json.JSONDecodeError, TypeError):
                    return result[0]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage asynchronously.

        Args:
            key: The key to store
            value: The value to store
            ttl: Time to live in seconds
        """
        await self._ensure_initialized()

        # Convert complex types to JSON
        if not isinstance(value, (str, int, float, bool)) and value is not None:
            value = json.dumps(value)

        expiry = time.time() + ttl if ttl is not None else None

        async with aiosqlite.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as db:
            await db.execute(
                f"""
                INSERT OR REPLACE INTO {self.table_name} (key, value, expiry)
                VALUES (?, ?, ?)
                """,
                (key, str(value), expiry),
            )
            await db.commit()

    async def delete(self, key: str) -> None:
        """
        Delete a value from storage asynchronously.

        Args:
            key: The key to delete
        """
        await self._ensure_initialized()

        async with aiosqlite.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as db:
            await db.execute(f"DELETE FROM {self.table_name} WHERE key = ?", (key,))
            await db.commit()

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter in storage asynchronously.

        Args:
            key: The key to increment
            amount: The amount to increment by

        Returns:
            The new value
        """
        await self._ensure_initialized()

        current = await self.get(key) or 0
        if not isinstance(current, (int, float)):
            current = 0

        new_value = current + amount
        await self.set(key, new_value)
        return new_value

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage asynchronously.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        await self._ensure_initialized()
        await self._clean_expired()

        async with aiosqlite.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as db:
            async with db.execute(
                f"SELECT 1 FROM {self.table_name} WHERE key = ?", (key,)
            ) as cursor:
                result = await cursor.fetchone()
                return result is not None

    async def clear(self) -> None:
        """Clear all values from storage."""
        await self._ensure_initialized()

        async with aiosqlite.connect(
            self.db_path, check_same_thread=self.check_same_thread
        ) as db:
            await db.execute(f"DELETE FROM {self.table_name}")
            await db.commit()

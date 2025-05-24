"""
TinyDB storage backend for PyWebGuard with both sync and async support.
"""

import json
import time
from typing import Any, Dict, Optional, Union

# Check if tinydb is installed
try:
    from tinydb import TinyDB, Query
    from tinydb.storages import JSONStorage
    from tinydb.middlewares import CachingMiddleware

    TINYDB_AVAILABLE = True
except ImportError:
    TINYDB_AVAILABLE = False

    # Create dummy classes for type checking
    class TinyDB:
        def __init__(self, *args, **kwargs):
            pass

        def table(self, *args, **kwargs):
            pass

    class Query:
        pass


from pywebguard.storage.base import BaseStorage, AsyncBaseStorage


class TinyDBStorage(BaseStorage):
    """
    TinyDB storage backend (synchronous).
    """

    def __init__(self, db_path: str = "pywebguard.json", table_name: str = "default"):
        """
        Initialize the TinyDB storage.

        Args:
            db_path: Path to TinyDB JSON file
            table_name: Name of the table to store values
        """
        if not TINYDB_AVAILABLE:
            raise ImportError(
                "TinyDB is not installed. Install it with 'pip install pywebguard[tinydb]' "
                "or 'pip install tinydb>=4.5.0'"
            )

        self.db = TinyDB(db_path, storage=CachingMiddleware(JSONStorage))
        self.table = self.db.table(table_name)
        self._clean_expired()

    def _clean_expired(self) -> None:
        """Remove expired entries from storage."""
        now = time.time()
        # Only consider entries that have an expiry value and are expired
        expired = self.table.search((Query().expiry != None) & (Query().expiry <= now))
        if expired:
            self.table.remove((Query().expiry != None) & (Query().expiry <= now))

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from storage.

        Args:
            key: The key to retrieve

        Returns:
            The stored value or None if not found
        """
        self._clean_expired()

        result = self.table.get(Query().key == key)
        if result is None:
            return None

        try:
            return json.loads(result["value"])
        except (json.JSONDecodeError, TypeError):
            return result["value"]

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

        # Remove existing entry if it exists
        self.table.remove(Query().key == key)

        # Insert new entry
        self.table.insert({"key": key, "value": str(value), "expiry": expiry})

    def delete(self, key: str) -> None:
        """
        Delete a value from storage.

        Args:
            key: The key to delete
        """
        self.table.remove(Query().key == key)

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
        return self.table.contains(Query().key == key)

    def clear(self) -> None:
        """Clear all values from storage."""
        self.table.truncate()


class AsyncTinyDBStorage(AsyncBaseStorage):
    """
    TinyDB storage backend (asynchronous).

    Note: TinyDB is synchronous by nature, so this is a wrapper that runs
    TinyDB operations in a thread pool to make them non-blocking.
    """

    def __init__(self, db_path: str = "pywebguard.json", table_name: str = "default"):
        """
        Initialize the async TinyDB storage.

        Args:
            db_path: Path to TinyDB JSON file
            table_name: Name of the table to store values
        """
        if not TINYDB_AVAILABLE:
            raise ImportError(
                "TinyDB is not installed. Install it with 'pip install pywebguard[tinydb]' "
                "or 'pip install tinydb>=4.5.0'"
            )

        self.db = TinyDB(db_path, storage=CachingMiddleware(JSONStorage))
        self.table = self.db.table(table_name)

    async def _clean_expired(self) -> None:
        """Remove expired entries from storage."""
        now = time.time()
        # Only consider entries that have an expiry value and are expired
        expired = self.table.search((Query().expiry != None) & (Query().expiry <= now))
        if expired:
            self.table.remove((Query().expiry != None) & (Query().expiry <= now))

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from storage asynchronously.

        Args:
            key: The key to retrieve

        Returns:
            The stored value or None if not found
        """
        await self._clean_expired()

        result = self.table.get(Query().key == key)
        if result is None:
            return None

        try:
            return json.loads(result["value"])
        except (json.JSONDecodeError, TypeError):
            return result["value"]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage asynchronously.

        Args:
            key: The key to store
            value: The value to store
            ttl: Time to live in seconds
        """
        # Convert complex types to JSON
        if not isinstance(value, (str, int, float, bool)) and value is not None:
            value = json.dumps(value)

        expiry = time.time() + ttl if ttl is not None else None

        # Remove existing entry if it exists
        self.table.remove(Query().key == key)

        # Insert new entry
        self.table.insert({"key": key, "value": str(value), "expiry": expiry})

    async def delete(self, key: str) -> None:
        """
        Delete a value from storage asynchronously.

        Args:
            key: The key to delete
        """
        self.table.remove(Query().key == key)

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter in storage asynchronously.

        Args:
            key: The key to increment
            amount: The amount to increment by

        Returns:
            The new value
        """
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
        await self._clean_expired()
        return self.table.contains(Query().key == key)

    async def clear(self) -> None:
        """Clear all values from storage."""
        self.table.truncate()

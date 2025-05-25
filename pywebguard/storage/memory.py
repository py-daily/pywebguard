"""
In-memory storage backend for PyWebGuard with both sync and async support.

This module provides in-memory storage implementations for PyWebGuard.
The in-memory storage is fast but not persistent across application restarts.

Classes:
    MemoryStorage: In-memory storage backend (synchronous)
    AsyncMemoryStorage: In-memory storage backend (asynchronous)
"""

import time
from typing import Any, Dict, Optional

from pywebguard.storage.base import BaseStorage, AsyncBaseStorage


class MemoryStorage(BaseStorage):
    """
    In-memory storage backend (synchronous).

    This storage backend stores data in memory, which makes it fast but not
    persistent across application restarts. It's suitable for development
    and testing, or for applications that don't need persistence.
    """

    def __init__(self) -> None:
        """
        Initialize the in-memory storage.

        Creates empty dictionaries for storing values and TTLs.
        """
        self._storage: Dict[str, Any] = {}
        self._ttls: Dict[str, float] = {}

    def _clean_expired(self) -> None:
        """
        Remove expired entries from storage.

        This method is called before read operations to ensure that
        expired entries are not returned.
        """
        now = time.time()
        expired = [k for k, ttl in self._ttls.items() if ttl <= now]
        if expired:
            for k in expired:
                del self._storage[k]
                del self._ttls[k]

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from storage.

        Args:
            key: The key to retrieve

        Returns:
            The value if found and not expired, None otherwise
        """
        self._clean_expired()
        if key not in self._storage:
            return None
        if key in self._ttls and self._ttls[key] <= time.time():
            del self._storage[key]
            del self._ttls[key]
            return None
        value = self._storage[key]
        ttl = self._ttls.get(key)
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage.

        Args:
            key: The key to store
            value: The value to store
            ttl: Time to live in seconds
        """
        self._clean_expired()
        self._storage[key] = value

        if ttl is not None:
            self._ttls[key] = time.time() + ttl
        else:
            self._ttls.pop(key, None)

    def delete(self, key: str) -> None:
        """
        Delete a value from storage.

        Args:
            key: The key to delete
        """
        self._storage.pop(key, None)
        self._ttls.pop(key, None)

    def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """
        Increment a counter in storage.

        Args:
            key: The key to increment
            amount: The amount to increment by
            ttl: Time to live in seconds

        Returns:
            The new value

        Raises:
            ValueError: If the current value is not numeric
        """
        self._clean_expired()
        is_new = key not in self._storage
        current = self._storage.get(key, 0)
        if not isinstance(current, (int, float)):
            raise ValueError(f"Current value for key {key} is not numeric")

        new_value = current + amount
        self._storage[key] = new_value

        if ttl is not None:
            self._ttls[key] = time.time() + ttl
        elif is_new:
            # If it's a new key and no TTL provided, use a default TTL
            self._ttls[key] = time.time() + 60  # Default 60 second TTL

        return new_value

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage.

        Args:
            key: The key to check

        Returns:
            True if the key exists and is not expired, False otherwise
        """
        self._clean_expired()
        if key not in self._storage:
            return False
        if key in self._ttls and self._ttls[key] <= time.time():
            del self._storage[key]
            del self._ttls[key]
            return False
        return True

    def clear(self) -> None:
        """
        Clear all values from storage.

        This method removes all keys and values from the storage.
        """
        self._storage.clear()
        self._ttls.clear()


class AsyncMemoryStorage(AsyncBaseStorage):
    """
    In-memory storage backend (asynchronous).

    This is a wrapper around the synchronous MemoryStorage that provides
    async methods. Since memory operations are fast, we can just use the
    synchronous implementation under the hood.
    """

    def __init__(self) -> None:
        """
        Initialize the async in-memory storage.

        Creates a synchronous MemoryStorage instance to handle the actual storage.
        """
        self._storage = MemoryStorage()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from storage asynchronously.

        Args:
            key: The key to retrieve

        Returns:
            The stored value or None if not found
        """
        return self._storage.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage asynchronously.

        Args:
            key: The key to store
            value: The value to store
            ttl: Time to live in seconds
        """
        self._storage.set(key, value, ttl)

    async def delete(self, key: str) -> None:
        """
        Delete a value from storage asynchronously.

        Args:
            key: The key to delete
        """
        self._storage.delete(key)

    async def increment(
        self, key: str, amount: int = 1, ttl: Optional[int] = None
    ) -> int:
        """
        Increment a counter in storage asynchronously.

        Args:
            key: The key to increment
            amount: The amount to increment by
            ttl: Time to live in seconds

        Returns:
            The new value

        Raises:
            ValueError: If the current value is not numeric
        """
        return self._storage.increment(key, amount, ttl)

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage asynchronously.

        Args:
            key: The key to check

        Returns:
            True if the key exists and is not expired, False otherwise
        """
        return self._storage.exists(key)

    async def clear(self) -> None:
        """
        Clear all values from storage asynchronously.

        This method removes all keys and values from the storage.
        """
        self._storage.clear()

"""
Redis storage backend for PyWebGuard with both sync and async support.

This module provides Redis storage implementations for PyWebGuard.
Redis storage is persistent and suitable for production environments.

Classes:
    RedisStorage: Redis storage backend (synchronous)
    AsyncRedisStorage: Redis storage backend (asynchronous)
"""

import json
from typing import Any, Dict, Optional, Union, List, cast

# Check if redis is installed
try:
    import redis
    import redis.asyncio

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

    # Create dummy classes for type checking
    class redis:
        class Redis:
            pass

        class asyncio:
            class Redis:
                pass


from pywebguard.storage.base import BaseStorage, AsyncBaseStorage


class RedisStorage(BaseStorage):
    """
    Redis storage backend (synchronous).

    This storage backend uses Redis for persistent storage. It's suitable for
    production environments and distributed applications.
    """

    def __init__(
        self, url: str = "redis://localhost:6379/0", prefix: str = "pywebguard:"
    ):
        """
        Initialize the Redis storage.

        Args:
            url: Redis connection URL
            prefix: Key prefix for all stored values

        Raises:
            ImportError: If Redis is not installed
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "Redis is not installed. Install it with 'pip install pywebguard[redis]' "
                "or 'pip install redis>=4.0.0'"
            )

        self.redis = redis.from_url(url)
        self.prefix = prefix

    def _get_key(self, key: str) -> str:
        """
        Get the prefixed key for Redis.

        Args:
            key: The original key

        Returns:
            The prefixed key
        """
        return f"{self.prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from storage.

        Args:
            key: The key to retrieve

        Returns:
            The stored value or None if not found
        """
        prefixed_key = self._get_key(key)
        value = self.redis.get(prefixed_key)

        if value is None:
            return None

        try:
            # Try to decode as JSON
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # If not JSON, return as string
            return value.decode("utf-8") if isinstance(value, bytes) else value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage.

        Args:
            key: The key to store
            value: The value to store
            ttl: Time to live in seconds
        """
        prefixed_key = self._get_key(key)

        # Convert complex types to JSON
        if not isinstance(value, (str, int, float, bool)) and value is not None:
            value = json.dumps(value)

        if ttl is not None:
            self.redis.setex(prefixed_key, ttl, value)
        else:
            self.redis.set(prefixed_key, value)

    def delete(self, key: str) -> None:
        """
        Delete a value from storage.

        Args:
            key: The key to delete
        """
        prefixed_key = self._get_key(key)
        self.redis.delete(prefixed_key)

    def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """
        Increment a counter in storage.

        Args:
            key: The key to increment
            amount: The amount to increment by
            ttl: Time to live in seconds

        Returns:
            The new value
        """
        prefixed_key = self._get_key(key)
        pipe = self.redis.pipeline()
        pipe.incrby(prefixed_key, amount)
        if ttl is not None:
            pipe.expire(prefixed_key, ttl)
        result = pipe.execute()
        return result[0]

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        prefixed_key = self._get_key(key)
        return bool(self.redis.exists(prefixed_key))

    def clear(self) -> None:
        """
        Clear all values from storage.

        This method removes all keys with the configured prefix.
        """
        keys = self.redis.keys(f"{self.prefix}*")
        if keys:
            self.redis.delete(*keys)


class AsyncRedisStorage(AsyncBaseStorage):
    """
    Redis storage backend (asynchronous).

    This storage backend uses Redis for persistent storage with async support.
    It's suitable for asynchronous web frameworks like FastAPI.
    """

    def __init__(
        self, url: str = "redis://localhost:6379/0", prefix: str = "pywebguard:"
    ):
        """
        Initialize the async Redis storage.

        Args:
            url: Redis connection URL
            prefix: Key prefix for all stored values

        Raises:
            ImportError: If Redis is not installed
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "Redis is not installed. Install it with 'pip install pywebguard[redis]' "
                "or 'pip install redis>=4.0.0'"
            )

        self.redis = redis.asyncio.from_url(url)
        self.prefix = prefix

    def _get_key(self, key: str) -> str:
        """
        Get the prefixed key for Redis.

        Args:
            key: The original key

        Returns:
            The prefixed key
        """
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from storage asynchronously.

        Args:
            key: The key to retrieve

        Returns:
            The stored value or None if not found
        """
        prefixed_key = self._get_key(key)
        value = await self.redis.get(prefixed_key)

        if value is None:
            return None

        try:
            # Try to decode as JSON
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # If not JSON, return as string
            return value.decode("utf-8") if isinstance(value, bytes) else value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage asynchronously.

        Args:
            key: The key to store
            value: The value to store
            ttl: Time to live in seconds
        """
        prefixed_key = self._get_key(key)

        # Convert complex types to JSON
        if not isinstance(value, (str, int, float, bool)) and value is not None:
            value = json.dumps(value)

        if ttl is not None:
            await self.redis.setex(prefixed_key, ttl, value)
        else:
            await self.redis.set(prefixed_key, value)

    async def delete(self, key: str) -> None:
        """
        Delete a value from storage asynchronously.

        Args:
            key: The key to delete
        """
        prefixed_key = self._get_key(key)
        await self.redis.delete(prefixed_key)

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
        """
        prefixed_key = self._get_key(key)
        pipe = self.redis.pipeline()
        pipe.incrby(prefixed_key, amount)
        if ttl is not None:
            pipe.expire(prefixed_key, ttl)
        result = await pipe.execute()
        return result[0]

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage asynchronously.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        prefixed_key = self._get_key(key)
        return bool(await self.redis.exists(prefixed_key))

    async def clear(self) -> None:
        """
        Clear all values from storage asynchronously.

        This method removes all keys with the configured prefix.
        """
        keys = await self.redis.keys(f"{self.prefix}*")
        if keys:
            await self.redis.delete(*keys)

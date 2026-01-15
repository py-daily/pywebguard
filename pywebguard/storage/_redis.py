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
    from redis.exceptions import (
        ConnectionError,
        TimeoutError,
        RedisError,
        ConnectionPoolError,
    )

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

    class ConnectionError(Exception):
        pass

    class TimeoutError(Exception):
        pass

    class RedisError(Exception):
        pass

    class ConnectionPoolError(Exception):
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

        # Configure connection pool with health checks and retry logic
        # Use try-except to handle systems that don't support socket keepalive options
        try:
            self.redis = redis.from_url(
                url,
                retry_on_timeout=True,
                health_check_interval=30,  # Check connection health every 30 seconds
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE: start keepalive after 1 second of inactivity
                    2: 1,  # TCP_KEEPINTVL: send keepalive probe every 1 second
                    3: 3,  # TCP_KEEPCNT: send 3 probes before considering connection dead
                },
                decode_responses=False,  # Keep bytes for compatibility
            )
        except (OSError, ConnectionError):
            # Fallback to simpler connection if keepalive options fail
            self.redis = redis.from_url(
                url,
                retry_on_timeout=True,
                health_check_interval=30,
                socket_keepalive=True,
                decode_responses=False,
            )
        self.prefix = prefix
        self.url = url

    def _ensure_connection(self) -> None:
        """
        Ensure the Redis connection is healthy. Reconnect if necessary.

        This method reconnects the Redis client to handle stale or broken connections.
        This helps prevent connection issues in long-running applications.
        """
        try:
            # Close the connection pool first to clean up stale connections
            if hasattr(self.redis, "connection_pool") and self.redis.connection_pool:
                try:
                    self.redis.connection_pool.disconnect()
                except Exception:
                    pass

            # Try to close the existing connection
            self.redis.close()
        except Exception:
            pass  # Ignore errors when closing

        # Recreate the connection with the same settings
        # Use try-except to handle systems that don't support socket keepalive options
        try:
            self.redis = redis.from_url(
                self.url,
                retry_on_timeout=True,
                health_check_interval=30,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,
                    2: 1,
                    3: 3,
                },
                decode_responses=False,
            )
        except (OSError, ConnectionError):
            # Fallback to simpler connection if keepalive options fail
            self.redis = redis.from_url(
                self.url,
                retry_on_timeout=True,
                health_check_interval=30,
                socket_keepalive=True,
                decode_responses=False,
            )

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

        # Retry logic for connection issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                value = self.redis.get(prefixed_key)
                break
            except (ConnectionError, TimeoutError, AttributeError, RedisError, OSError):
                if attempt < max_retries - 1:
                    self._ensure_connection()
                    continue
                raise

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

        # Retry logic for connection issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                if ttl is not None:
                    self.redis.setex(prefixed_key, ttl, value)
                else:
                    self.redis.set(prefixed_key, value)
                break
            except (ConnectionError, TimeoutError, AttributeError, RedisError, OSError):
                if attempt < max_retries - 1:
                    self._ensure_connection()
                    continue
                raise

    def delete(self, key: str) -> None:
        """
        Delete a value from storage.

        Args:
            key: The key to delete
        """
        prefixed_key = self._get_key(key)

        # Retry logic for connection issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                self.redis.delete(prefixed_key)
                break
            except (ConnectionError, TimeoutError, AttributeError, RedisError, OSError):
                if attempt < max_retries - 1:
                    self._ensure_connection()
                    continue
                raise

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

        # Retry logic for connection issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                pipe = self.redis.pipeline()
                pipe.incrby(prefixed_key, amount)
                if ttl is not None:
                    pipe.expire(prefixed_key, ttl)
                result = pipe.execute()
                return result[0]
            except (ConnectionError, TimeoutError, AttributeError, RedisError, OSError):
                if attempt < max_retries - 1:
                    self._ensure_connection()
                    continue
                raise

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        prefixed_key = self._get_key(key)

        # Retry logic for connection issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                return bool(self.redis.exists(prefixed_key))
            except (ConnectionError, TimeoutError, AttributeError, RedisError, OSError):
                if attempt < max_retries - 1:
                    self._ensure_connection()
                    continue
                raise

    def clear(self) -> None:
        """
        Clear all values from storage.

        This method removes all keys with the configured prefix.
        """
        # Retry logic for connection issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                keys = self.redis.keys(f"{self.prefix}*")
                if keys:
                    self.redis.delete(*keys)
                break
            except (ConnectionError, TimeoutError, AttributeError, RedisError, OSError):
                if attempt < max_retries - 1:
                    self._ensure_connection()
                    continue
                raise


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

        # Configure connection pool with health checks and retry logic
        # Use try-except to handle systems that don't support socket keepalive options
        try:
            self.redis = redis.asyncio.from_url(
                url,
                retry_on_timeout=True,
                health_check_interval=30,  # Check connection health every 30 seconds
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE: start keepalive after 1 second of inactivity
                    2: 1,  # TCP_KEEPINTVL: send keepalive probe every 1 second
                    3: 3,  # TCP_KEEPCNT: send 3 probes before considering connection dead
                },
                decode_responses=False,  # Keep bytes for compatibility
            )
        except (OSError, ConnectionError):
            # Fallback to simpler connection if keepalive options fail
            self.redis = redis.asyncio.from_url(
                url,
                retry_on_timeout=True,
                health_check_interval=30,
                socket_keepalive=True,
                decode_responses=False,
            )
        self.prefix = prefix
        self.url = url

    async def _ensure_connection(self) -> None:
        """
        Ensure the Redis connection is healthy. Reconnect if necessary.

        This method reconnects the Redis client to handle stale or broken connections.
        This helps prevent connection issues in long-running applications.
        """
        try:
            # Close the connection pool first to clean up stale connections
            if hasattr(self.redis, "connection_pool") and self.redis.connection_pool:
                try:
                    await self.redis.connection_pool.disconnect()
                except Exception:
                    pass

            # Try to close the existing connection
            # Try both close() and aclose() methods for compatibility
            if hasattr(self.redis, "aclose"):
                await self.redis.aclose()
            elif hasattr(self.redis, "close"):
                close_method = self.redis.close()
                if hasattr(close_method, "__await__"):
                    await close_method
                else:
                    close_method()
        except Exception:
            pass  # Ignore errors when closing

        # Recreate the connection with the same settings
        # Use try-except to handle systems that don't support socket keepalive options
        try:
            self.redis = redis.asyncio.from_url(
                self.url,
                retry_on_timeout=True,
                health_check_interval=30,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,
                    2: 1,
                    3: 3,
                },
                decode_responses=False,
            )
        except (OSError, ConnectionError):
            # Fallback to simpler connection if keepalive options fail
            self.redis = redis.asyncio.from_url(
                self.url,
                retry_on_timeout=True,
                health_check_interval=30,
                socket_keepalive=True,
                decode_responses=False,
            )

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

        # Retry logic for connection issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                value = await self.redis.get(prefixed_key)
                break
            except (ConnectionError, TimeoutError, AttributeError, RedisError, OSError):
                if attempt < max_retries - 1:
                    await self._ensure_connection()
                    continue
                raise

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

        # Retry logic for connection issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                if ttl is not None:
                    await self.redis.setex(prefixed_key, ttl, value)
                else:
                    await self.redis.set(prefixed_key, value)
                break
            except (ConnectionError, TimeoutError, AttributeError, RedisError, OSError):
                if attempt < max_retries - 1:
                    await self._ensure_connection()
                    continue
                raise

    async def delete(self, key: str) -> None:
        """
        Delete a value from storage asynchronously.

        Args:
            key: The key to delete
        """
        prefixed_key = self._get_key(key)

        # Retry logic for connection issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                await self.redis.delete(prefixed_key)
                break
            except (ConnectionError, TimeoutError, AttributeError, RedisError, OSError):
                if attempt < max_retries - 1:
                    await self._ensure_connection()
                    continue
                raise

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

        # Retry logic for connection issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                pipe = self.redis.pipeline()
                pipe.incrby(prefixed_key, amount)
                if ttl is not None:
                    pipe.expire(prefixed_key, ttl)
                result = await pipe.execute()
                return result[0]
            except (ConnectionError, TimeoutError, AttributeError, RedisError, OSError):
                if attempt < max_retries - 1:
                    await self._ensure_connection()
                    continue
                raise

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage asynchronously.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        prefixed_key = self._get_key(key)

        # Retry logic for connection issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                return bool(await self.redis.exists(prefixed_key))
            except (ConnectionError, TimeoutError, AttributeError, RedisError, OSError):
                if attempt < max_retries - 1:
                    await self._ensure_connection()
                    continue
                raise

    async def clear(self) -> None:
        """
        Clear all values from storage asynchronously.

        This method removes all keys with the configured prefix.
        """
        # Retry logic for connection issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                keys = await self.redis.keys(f"{self.prefix}*")
                if keys:
                    await self.redis.delete(*keys)
                break
            except (ConnectionError, TimeoutError, AttributeError, RedisError, OSError):
                if attempt < max_retries - 1:
                    await self._ensure_connection()
                    continue
                raise

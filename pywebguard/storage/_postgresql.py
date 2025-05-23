"""
PostgreSQL storage backend for PyWebGuard.

This module provides both synchronous and asynchronous PostgreSQL storage
implementations for PyWebGuard. It requires the psycopg2 package for
synchronous operations and asyncpg for asynchronous operations.
"""

import time
import json
from typing import Any, Dict, Optional, Union, List, TYPE_CHECKING, TypeVar, cast
from datetime import datetime, timedelta

from pywebguard.storage.base import BaseStorage, AsyncBaseStorage

# Try to import psycopg2 for synchronous operations
ASYNCPG_AVAILABLE = False
PSYCOPG2_AVAILABLE = False
try:
    import psycopg2
    import psycopg2.extras

    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Try to import asyncpg for asynchronous operations
if TYPE_CHECKING:
    import asyncpg

    Pool = asyncpg.Pool
else:
    try:
        import asyncpg

        Pool = asyncpg.Pool
        ASYNCPG_AVAILABLE = True
    except ImportError:
        ASYNCPG_AVAILABLE = False
        Pool = Any  # type: ignore


class PostgreSQLStorage(BaseStorage):
    """
    PostgreSQL storage backend for PyWebGuard (synchronous).

    This class provides a PostgreSQL-based storage backend for PyWebGuard.
    It stores data in a PostgreSQL table with TTL support.

    Attributes:
        conn: PostgreSQL connection
        table_name: Name of the table to use
        ttl: Default TTL for stored data in seconds
    """

    def __init__(
        self,
        url: str = "postgresql://postgres:postgres@localhost:5432/pywebguard",
        table_name: str = "pywebguard",
        ttl: int = 3600,
        **kwargs: Any,
    ) -> None:
        """
        Initialize PostgreSQL storage.

        Args:
            url: PostgreSQL connection URL
            table_name: Name of the table to use
            ttl: Default TTL for stored data in seconds
            **kwargs: Additional arguments to pass to psycopg2.connect

        Raises:
            ImportError: If psycopg2 is not installed
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError(
                "PostgreSQL storage requires psycopg2. Install it with 'pip install psycopg2-binary'"
            )

        self.conn = psycopg2.connect(url, **kwargs)
        self.table_name = table_name
        self.ttl = ttl

        # Create table if it doesn't exist
        self._create_table()

    def _create_table(self) -> None:
        """Create the storage table if it doesn't exist."""
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    key TEXT PRIMARY KEY,
                    value JSONB NOT NULL,
                    expires_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """
            )

            # Create index on expires_at for TTL cleanup
            cur.execute(
                f"""
                CREATE INDEX IF NOT EXISTS {self.table_name}_expires_at_idx
                ON {self.table_name} (expires_at)
            """
            )

            self.conn.commit()

    def _cleanup_expired(self) -> None:
        """Clean up expired entries."""
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                DELETE FROM {self.table_name}
                WHERE expires_at IS NOT NULL AND expires_at < NOW()
            """
            )
            self.conn.commit()

    def get(self, key: str) -> Any:
        """
        Get a value from storage.

        Args:
            key: Key to retrieve

        Returns:
            The stored value, or None if the key doesn't exist or has expired
        """
        self._cleanup_expired()

        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT value FROM {self.table_name}
                WHERE key = %s
            """,
                (key,),
            )

            result = cur.fetchone()
            if result:
                return result[0]
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage.

        Args:
            key: Key to store
            value: Value to store
            ttl: Time-to-live in seconds (None for default)
        """
        expires_at = None
        if ttl is not None and ttl > 0:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        elif self.ttl > 0:
            expires_at = datetime.now() + timedelta(seconds=self.ttl)

        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {self.table_name} (key, value, expires_at, updated_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (key) DO UPDATE
                SET value = %s, expires_at = %s, updated_at = NOW()
            """,
                (
                    key,
                    psycopg2.extras.Json(value),
                    expires_at,
                    psycopg2.extras.Json(value),
                    expires_at,
                ),
            )

            self.conn.commit()

    def delete(self, key: str) -> None:
        """
        Delete a value from storage.

        Args:
            key: Key to delete
        """
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                DELETE FROM {self.table_name}
                WHERE key = %s
            """,
                (key,),
            )

            self.conn.commit()

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage.

        Args:
            key: Key to check

        Returns:
            True if the key exists and has not expired, False otherwise
        """
        self._cleanup_expired()

        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT 1 FROM {self.table_name}
                WHERE key = %s
            """,
                (key,),
            )

            return cur.fetchone() is not None

    def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter in storage.

        Args:
            key: Key to increment
            amount: Amount to increment by

        Returns:
            The new value of the counter
        """
        # Check if the key exists
        if not self.exists(key):
            self.set(key, 0)

        with self.conn.cursor() as cur:
            # Get the current value
            cur.execute(
                f"""
                SELECT value FROM {self.table_name}
                WHERE key = %s
            """,
                (key,),
            )

            result = cur.fetchone()
            current_value = result[0] if result else 0

            # Increment the value
            new_value = current_value + amount

            # Update the value
            cur.execute(
                f"""
                UPDATE {self.table_name}
                SET value = %s, updated_at = NOW()
                WHERE key = %s
            """,
                (new_value, key),
            )

            self.conn.commit()

            return new_value

    def clear(self) -> None:
        """Clear all data from storage."""
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                TRUNCATE TABLE {self.table_name}
            """
            )

            self.conn.commit()

    def close(self) -> None:
        """Close the PostgreSQL connection."""
        if hasattr(self, "conn") and self.conn:
            self.conn.close()


class AsyncPostgreSQLStorage(AsyncBaseStorage):
    """
    PostgreSQL storage backend for PyWebGuard (asynchronous).

    This class provides an asynchronous PostgreSQL-based storage backend for PyWebGuard.
    It stores data in a PostgreSQL table with TTL support.

    Attributes:
        pool: AsyncPG connection pool
        table_name: Name of the table to use
        ttl: Default TTL for stored data in seconds
    """

    def __init__(
        self,
        url: str = "postgresql://postgres:postgres@localhost:5432/pywebguard",
        table_name: str = "pywebguard",
        ttl: int = 3600,
        **kwargs: Any,
    ) -> None:
        """
        Initialize async PostgreSQL storage.

        Args:
            url: PostgreSQL connection URL
            table_name: Name of the table to use
            ttl: Default TTL for stored data in seconds
            **kwargs: Additional arguments to pass to asyncpg.create_pool

        Raises:
            ImportError: If asyncpg is not installed
        """
        if not ASYNCPG_AVAILABLE:
            raise ImportError(
                "Async PostgreSQL storage requires asyncpg. Install it with 'pip install asyncpg'"
            )

        self.url = url
        self.table_name = table_name
        self.ttl = ttl
        self.pool_kwargs = kwargs
        self.pool: Optional[Pool] = None
        self._initialized = False

    async def _get_pool(self) -> Pool:
        """Get or create the connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.url, **self.pool_kwargs)
        return self.pool

    async def initialize(self) -> None:
        """Initialize the storage (create table and indexes)."""
        if self._initialized:
            return

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # Create table if it doesn't exist
            await conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    key TEXT PRIMARY KEY,
                    value JSONB NOT NULL,
                    expires_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """
            )

            # Create index on expires_at for TTL cleanup
            await conn.execute(
                f"""
                CREATE INDEX IF NOT EXISTS {self.table_name}_expires_at_idx
                ON {self.table_name} (expires_at)
            """
            )

            self._initialized = True

    async def _cleanup_expired(self) -> None:
        """Clean up expired entries asynchronously."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                f"""
                DELETE FROM {self.table_name}
                WHERE expires_at IS NOT NULL AND expires_at < NOW()
            """
            )

    async def get(self, key: str) -> Any:
        """
        Get a value from storage asynchronously.

        Args:
            key: Key to retrieve

        Returns:
            The stored value, or None if the key doesn't exist or has expired
        """
        await self.initialize()
        await self._cleanup_expired()

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchval(
                f"""
                SELECT value FROM {self.table_name}
                WHERE key = $1
            """,
                key,
            )

            return result

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage asynchronously.

        Args:
            key: Key to store
            value: Value to store
            ttl: Time-to-live in seconds (None for default)
        """
        await self.initialize()

        expires_at = None
        if ttl is not None and ttl > 0:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        elif self.ttl > 0:
            expires_at = datetime.now() + timedelta(seconds=self.ttl)

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                f"""
                INSERT INTO {self.table_name} (key, value, expires_at, updated_at)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (key) DO UPDATE
                SET value = $2, expires_at = $3, updated_at = NOW()
            """,
                key,
                json.dumps(value),
                expires_at,
            )

    async def delete(self, key: str) -> None:
        """
        Delete a value from storage asynchronously.

        Args:
            key: Key to delete
        """
        await self.initialize()

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                f"""
                DELETE FROM {self.table_name}
                WHERE key = $1
            """,
                key,
            )

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage asynchronously.

        Args:
            key: Key to check

        Returns:
            True if the key exists and has not expired, False otherwise
        """
        await self.initialize()
        await self._cleanup_expired()

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchval(
                f"""
                SELECT 1 FROM {self.table_name}
                WHERE key = $1
            """,
                key,
            )

            return result is not None

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter in storage asynchronously.

        Args:
            key: Key to increment
            amount: Amount to increment by

        Returns:
            The new value of the counter
        """
        await self.initialize()

        # Check if the key exists
        if not await self.exists(key):
            await self.set(key, 0)

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # Get the current value
            current_value = await conn.fetchval(
                f"""
                SELECT value FROM {self.table_name}
                WHERE key = $1
            """,
                key,
            )

            current_value = current_value if current_value is not None else 0

            # Increment the value
            new_value = current_value + amount

            # Update the value
            await conn.execute(
                f"""
                UPDATE {self.table_name}
                SET value = $1, updated_at = NOW()
                WHERE key = $2
            """,
                json.dumps(new_value),
                key,
            )

            return new_value

    async def clear(self) -> None:
        """Clear all data from storage asynchronously."""
        await self.initialize()

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                f"""
                TRUNCATE TABLE {self.table_name}
            """
            )

    async def close(self) -> None:
        """Close the PostgreSQL connection pool asynchronously."""
        if self.pool:
            await self.pool.close()
            self.pool = None

"""
Tests for PostgreSQL storage backend.

This module contains tests for both synchronous and asynchronous PostgreSQL
storage implementations. Tests are skipped if psycopg2 or asyncpg are not installed.
"""

import pytest
import time
from datetime import datetime, timedelta
import asyncio
from typing import Any, Dict, Optional, Union, List

from pywebguard.storage.base import BaseStorage, AsyncBaseStorage

# Check if psycopg2 is available for synchronous tests
try:
    import psycopg2
    from pywebguard.storage._postgresql import PostgreSQLStorage

    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Check if asyncpg is available for asynchronous tests
try:
    import asyncpg
    from pywebguard.storage._postgresql import AsyncPostgreSQLStorage

    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False


@pytest.mark.skipif(
    not PSYCOPG2_AVAILABLE, reason="PostgreSQL storage tests require psycopg2"
)
class TestPostgreSQLStorage:
    """Tests for synchronous PostgreSQL storage."""

    @pytest.fixture
    def storage(self) -> PostgreSQLStorage:
        """Create a PostgreSQL storage instance for testing."""
        storage = PostgreSQLStorage(
            url="postgresql://postgres:postgres@localhost:5432/postgres",
            table_name="pywebguard_test",
            ttl=60,
        )
        # Clear storage before each test
        storage.clear()
        yield storage
        # Clean up after tests
        storage.clear()
        storage.close()

    def test_get_set(self, storage: PostgreSQLStorage) -> None:
        """Test getting and setting values."""
        # Test with string value
        storage.set("test_key", "test_value")
        assert storage.get("test_key") == "test_value"

        # Test with dict value
        storage.set("test_dict", {"foo": "bar", "baz": 123})
        assert storage.get("test_dict") == {"foo": "bar", "baz": 123}

        # Test with list value
        storage.set("test_list", [1, 2, 3, "four"])
        assert storage.get("test_list") == [1, 2, 3, "four"]

        # Test with None value
        storage.set("test_none", None)
        assert storage.get("test_none") is None

        # Test non-existent key
        assert storage.get("non_existent") is None

    def test_delete(self, storage: PostgreSQLStorage) -> None:
        """Test deleting values."""
        storage.set("test_key", "test_value")
        assert storage.get("test_key") == "test_value"

        storage.delete("test_key")
        assert storage.get("test_key") is None

        # Deleting non-existent key should not raise an error
        storage.delete("non_existent")

    def test_exists(self, storage: PostgreSQLStorage) -> None:
        """Test checking if a key exists."""
        storage.set("test_key", "test_value")
        assert storage.exists("test_key") is True
        assert storage.exists("non_existent") is False

        storage.delete("test_key")
        assert storage.exists("test_key") is False

    def test_increment(self, storage: PostgreSQLStorage) -> None:
        """Test incrementing a counter."""
        # Test with non-existent key
        assert storage.increment("counter") == 1
        assert storage.get("counter") == 1

        # Test with existing key
        assert storage.increment("counter") == 2
        assert storage.get("counter") == 2

        # Test with custom amount
        assert storage.increment("counter", 5) == 7
        assert storage.get("counter") == 7

        # Test with negative amount
        assert storage.increment("counter", -3) == 4
        assert storage.get("counter") == 4

    def test_clear(self, storage: PostgreSQLStorage) -> None:
        """Test clearing all data."""
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        assert storage.get("key1") == "value1"
        assert storage.get("key2") == "value2"

        storage.clear()

        assert storage.get("key1") is None
        assert storage.get("key2") is None

    def test_ttl(self, storage: PostgreSQLStorage) -> None:
        """Test time-to-live functionality."""
        # Set a key with a short TTL
        storage.set("short_ttl", "expires_soon", ttl=1)
        assert storage.get("short_ttl") == "expires_soon"

        # Set a key with a longer TTL
        storage.set("long_ttl", "expires_later", ttl=60)
        assert storage.get("long_ttl") == "expires_later"

        # Wait for the short TTL to expire
        time.sleep(2)

        # The short TTL key should be gone
        assert storage.get("short_ttl") is None

        # The long TTL key should still be there
        assert storage.get("long_ttl") == "expires_later"


@pytest.mark.skipif(
    not ASYNCPG_AVAILABLE, reason="Async PostgreSQL storage tests require asyncpg"
)
@pytest.mark.asyncio
class TestAsyncPostgreSQLStorage:
    """Tests for asynchronous PostgreSQL storage."""

    @pytest.fixture
    async def storage(self) -> AsyncPostgreSQLStorage:
        """Create an async PostgreSQL storage instance for testing."""
        storage = AsyncPostgreSQLStorage(
            url="postgresql://postgres:postgres@localhost:5432/postgres",
            table_name="pywebguard_async_test",
            ttl=60,
        )
        # Initialize and clear storage before each test
        await storage.initialize()
        await storage.clear()
        yield storage
        # Clean up after tests
        await storage.clear()
        await storage.close()

    async def test_get_set(self, storage: AsyncPostgreSQLStorage) -> None:
        """Test getting and setting values asynchronously."""
        # Test with string value
        await storage.set("test_key", "test_value")
        assert await storage.get("test_key") == "test_value"

        # Test with dict value
        await storage.set("test_dict", {"foo": "bar", "baz": 123})
        assert await storage.get("test_dict") == {"foo": "bar", "baz": 123}

        # Test with list value
        await storage.set("test_list", [1, 2, 3, "four"])
        assert await storage.get("test_list") == [1, 2, 3, "four"]

        # Test with None value
        await storage.set("test_none", None)
        assert await storage.get("test_none") is None

        # Test non-existent key
        assert await storage.get("non_existent") is None

    async def test_delete(self, storage: AsyncPostgreSQLStorage) -> None:
        """Test deleting values asynchronously."""
        await storage.set("test_key", "test_value")
        assert await storage.get("test_key") == "test_value"

        await storage.delete("test_key")
        assert await storage.get("test_key") is None

        # Deleting non-existent key should not raise an error
        await storage.delete("non_existent")

    async def test_exists(self, storage: AsyncPostgreSQLStorage) -> None:
        """Test checking if a key exists asynchronously."""
        await storage.set("test_key", "test_value")
        assert await storage.exists("test_key") is True
        assert await storage.exists("non_existent") is False

        await storage.delete("test_key")
        assert await storage.exists("test_key") is False

    async def test_increment(self, storage: AsyncPostgreSQLStorage) -> None:
        """Test incrementing a counter asynchronously."""
        # Test with non-existent key
        assert await storage.increment("counter") == 1
        assert await storage.get("counter") == 1

        # Test with existing key
        assert await storage.increment("counter") == 2
        assert await storage.get("counter") == 2

        # Test with custom amount
        assert await storage.increment("counter", 5) == 7
        assert await storage.get("counter") == 7

        # Test with negative amount
        assert await storage.increment("counter", -3) == 4
        assert await storage.get("counter") == 4

    async def test_clear(self, storage: AsyncPostgreSQLStorage) -> None:
        """Test clearing all data asynchronously."""
        await storage.set("key1", "value1")
        await storage.set("key2", "value2")

        assert await storage.get("key1") == "value1"
        assert await storage.get("key2") == "value2"

        await storage.clear()

        assert await storage.get("key1") is None
        assert await storage.get("key2") is None

    async def test_ttl(self, storage: AsyncPostgreSQLStorage) -> None:
        """Test time-to-live functionality asynchronously."""
        # Set a key with a short TTL
        await storage.set("short_ttl", "expires_soon", ttl=1)
        assert await storage.get("short_ttl") == "expires_soon"

        # Set a key with a longer TTL
        await storage.set("long_ttl", "expires_later", ttl=60)
        assert await storage.get("long_ttl") == "expires_later"

        # Wait for the short TTL to expire
        await asyncio.sleep(2)

        # The short TTL key should be gone
        assert await storage.get("short_ttl") is None

        # The long TTL key should still be there
        assert await storage.get("long_ttl") == "expires_later"

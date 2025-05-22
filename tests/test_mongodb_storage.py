"""
Tests for MongoDB storage backend.

This module contains tests for both synchronous and asynchronous MongoDB
storage implementations. Tests are skipped if pymongo is not installed.
"""

import pytest
import time
from datetime import datetime, timedelta
import asyncio
from typing import Any, Dict, Optional, Union, List

from pywebguard.storage.base import BaseStorage, AsyncBaseStorage

# Check if pymongo is available
try:
    import pymongo
    from pywebguard.storage._mongodb import MongoDBStorage, AsyncMongoDBStorage

    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

# Skip all tests if pymongo is not available
pytestmark = pytest.mark.skipif(
    not MONGODB_AVAILABLE, reason="MongoDB storage tests require pymongo"
)


class TestMongoDBStorage:
    """Tests for synchronous MongoDB storage."""

    @pytest.fixture
    def storage(self) -> MongoDBStorage:
        """Create a MongoDB storage instance for testing."""
        storage = MongoDBStorage(
            url="mongodb://localhost:27017/pywebguard_test",
            collection_name="test_collection",
            ttl=60,
        )
        # Clear storage before each test
        storage.clear()
        yield storage
        # Clean up after tests
        storage.clear()
        storage.close()

    def test_get_set(self, storage: MongoDBStorage) -> None:
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

    def test_delete(self, storage: MongoDBStorage) -> None:
        """Test deleting values."""
        storage.set("test_key", "test_value")
        assert storage.get("test_key") == "test_value"

        storage.delete("test_key")
        assert storage.get("test_key") is None

        # Deleting non-existent key should not raise an error
        storage.delete("non_existent")

    def test_exists(self, storage: MongoDBStorage) -> None:
        """Test checking if a key exists."""
        storage.set("test_key", "test_value")
        assert storage.exists("test_key") is True
        assert storage.exists("non_existent") is False

        storage.delete("test_key")
        assert storage.exists("test_key") is False

    def test_increment(self, storage: MongoDBStorage) -> None:
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

    def test_clear(self, storage: MongoDBStorage) -> None:
        """Test clearing all data."""
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        assert storage.get("key1") == "value1"
        assert storage.get("key2") == "value2"

        storage.clear()

        assert storage.get("key1") is None
        assert storage.get("key2") is None

    def test_ttl(self, storage: MongoDBStorage) -> None:
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


@pytest.mark.asyncio
class TestAsyncMongoDBStorage:
    """Tests for asynchronous MongoDB storage."""

    @pytest.fixture
    async def storage(self) -> AsyncMongoDBStorage:
        """Create an async MongoDB storage instance for testing."""
        storage = AsyncMongoDBStorage(
            url="mongodb://localhost:27017/pywebguard_test",
            collection_name="test_async_collection",
            ttl=60,
        )
        # Initialize and clear storage before each test
        await storage.initialize()
        await storage.clear()
        yield storage
        # Clean up after tests
        await storage.clear()
        await storage.close()

    async def test_get_set(self, storage: AsyncMongoDBStorage) -> None:
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

    async def test_delete(self, storage: AsyncMongoDBStorage) -> None:
        """Test deleting values asynchronously."""
        await storage.set("test_key", "test_value")
        assert await storage.get("test_key") == "test_value"

        await storage.delete("test_key")
        assert await storage.get("test_key") is None

        # Deleting non-existent key should not raise an error
        await storage.delete("non_existent")

    async def test_exists(self, storage: AsyncMongoDBStorage) -> None:
        """Test checking if a key exists asynchronously."""
        await storage.set("test_key", "test_value")
        assert await storage.exists("test_key") is True
        assert await storage.exists("non_existent") is False

        await storage.delete("test_key")
        assert await storage.exists("test_key") is False

    async def test_increment(self, storage: AsyncMongoDBStorage) -> None:
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

    async def test_clear(self, storage: AsyncMongoDBStorage) -> None:
        """Test clearing all data asynchronously."""
        await storage.set("key1", "value1")
        await storage.set("key2", "value2")

        assert await storage.get("key1") == "value1"
        assert await storage.get("key2") == "value2"

        await storage.clear()

        assert await storage.get("key1") is None
        assert await storage.get("key2") is None

    async def test_ttl(self, storage: AsyncMongoDBStorage) -> None:
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

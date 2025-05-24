"""Base/shared tests for PyWebGuard storage implementations.

This file should only contain tests that are required for all storage backends.
Add new base tests here as needed.
"""

import pytest
import time
import pytest_asyncio
from typing import Any, Dict, Type
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage


def test_base_storage_interface():
    """Test that BaseStorage has all required methods."""
    required_methods = {
        "get": 1,  # key
        "set": 3,  # key, value, ttl=None
        "delete": 1,  # key
        "clear": 0,  # no args
        "exists": 1,  # key
        "increment": 3,  # key, amount=1, ttl=None
    }

    for method, arg_count in required_methods.items():
        assert hasattr(
            BaseStorage, method
        ), f"BaseStorage missing required method: {method}"
        method_obj = getattr(BaseStorage, method)
        # co_argcount includes self, so we expect arg_count + 1 total parameters
        assert (
            method_obj.__code__.co_argcount == arg_count + 1
        ), f"{method} has wrong number of parameters (expected {arg_count + 1}, got {method_obj.__code__.co_argcount})"


def test_async_base_storage_interface():
    """Test that AsyncBaseStorage has all required methods."""
    required_methods = {
        "get": 1,  # key
        "set": 3,  # key, value, ttl=None
        "delete": 1,  # key
        "clear": 0,  # no args
        "exists": 1,  # key
        "increment": 3,  # key, amount=1, ttl=None
    }

    for method, arg_count in required_methods.items():
        assert hasattr(
            AsyncBaseStorage, method
        ), f"AsyncBaseStorage missing required method: {method}"
        method_obj = getattr(AsyncBaseStorage, method)
        # co_argcount includes self, so we expect arg_count + 1 total parameters
        assert (
            method_obj.__code__.co_argcount == arg_count + 1
        ), f"{method} has wrong number of parameters (expected {arg_count + 1}, got {method_obj.__code__.co_argcount})"


# Base test classes that can be inherited by specific storage test classes
class BaseStorageTest:
    """Base class for testing storage implementations."""

    storage_class: Type[BaseStorage]

    @pytest.fixture
    def storage(self) -> BaseStorage:
        """Create a storage instance for testing."""
        raise NotImplementedError("Subclasses must implement this fixture")

    def test_initialization(self, storage: BaseStorage):
        """Test that storage is properly initialized."""
        assert isinstance(storage, BaseStorage)

    def test_set_get(self, storage: BaseStorage):
        """Test basic set and get operations."""
        # Test string value
        storage.set("key1", "value1")
        assert storage.get("key1") == "value1"

        # Test dict value
        test_dict = {"key": "value", "nested": {"inner": "value"}}
        storage.set("key2", test_dict)
        assert storage.get("key2") == test_dict

        # Test None value
        storage.set("key3", None)
        assert storage.get("key3") is None

        # Test non-existent key
        assert storage.get("non_existent") is None

    def test_delete(self, storage: BaseStorage):
        """Test delete operation."""
        storage.set("key1", "value1")
        assert storage.get("key1") == "value1"
        storage.delete("key1")
        assert storage.get("key1") is None

        # Test deleting non-existent key
        storage.delete("non_existent")

    def test_clear(self, storage: BaseStorage):
        """Test clear operation."""
        storage.set("key1", "value1")
        storage.set("key2", "value2")
        storage.clear()
        assert storage.get("key1") is None
        assert storage.get("key2") is None

    def test_exists(self, storage: BaseStorage):
        """Test exists operation."""
        assert not storage.exists("key1")
        storage.set("key1", "value1")
        assert storage.exists("key1")
        storage.delete("key1")
        assert not storage.exists("key1")

    def test_increment(self, storage: BaseStorage):
        """Test increment operation."""
        assert storage.increment("counter") == 1
        assert storage.increment("counter") == 2
        assert storage.increment("counter", 5) == 7

    def test_ttl(self, storage: BaseStorage):
        """Test TTL functionality."""
        storage.set("key1", "value1", ttl=1)
        assert storage.get("key1") == "value1"
        time.sleep(1.1)
        assert storage.get("key1") is None


class AsyncBaseStorageTest:
    """Base class for testing async storage implementations."""

    storage_class: Type[AsyncBaseStorage]

    @pytest_asyncio.fixture
    async def storage(self) -> AsyncBaseStorage:
        """Create an async storage instance for testing."""
        raise NotImplementedError("Subclasses must implement this fixture")

    def test_initialization(self, storage: AsyncBaseStorage):
        """Test that storage is properly initialized."""
        assert isinstance(storage, AsyncBaseStorage)

    @pytest.mark.asyncio
    async def test_set_get(self, storage: AsyncBaseStorage):
        """Test basic set and get operations."""
        # Test string value
        await storage.set("key1", "value1")
        assert await storage.get("key1") == "value1"

        # Test dict value
        test_dict = {"key": "value", "nested": {"inner": "value"}}
        await storage.set("key2", test_dict)
        assert await storage.get("key2") == test_dict

        # Test None value
        await storage.set("key3", None)
        assert await storage.get("key3") is None

        # Test non-existent key
        assert await storage.get("non_existent") is None

    @pytest.mark.asyncio
    async def test_delete(self, storage: AsyncBaseStorage):
        """Test delete operation."""
        await storage.set("key1", "value1")
        assert await storage.get("key1") == "value1"
        await storage.delete("key1")
        assert await storage.get("key1") is None

        # Test deleting non-existent key
        await storage.delete("non_existent")

    @pytest.mark.asyncio
    async def test_clear(self, storage: AsyncBaseStorage):
        """Test clear operation."""
        await storage.set("key1", "value1")
        await storage.set("key2", "value2")
        await storage.clear()
        assert await storage.get("key1") is None
        assert await storage.get("key2") is None

    @pytest.mark.asyncio
    async def test_exists(self, storage: AsyncBaseStorage):
        """Test exists operation."""
        assert not await storage.exists("key1")
        await storage.set("key1", "value1")
        assert await storage.exists("key1")
        await storage.delete("key1")
        assert not await storage.exists("key1")

    @pytest.mark.asyncio
    async def test_increment(self, storage: AsyncBaseStorage):
        """Test increment operation."""
        assert await storage.increment("counter") == 1
        assert await storage.increment("counter") == 2
        assert await storage.increment("counter", 5) == 7

    @pytest.mark.asyncio
    async def test_ttl(self, storage: AsyncBaseStorage):
        """Test TTL functionality."""
        await storage.set("key1", "value1", ttl=1)
        assert await storage.get("key1") == "value1"
        time.sleep(1.1)
        assert await storage.get("key1") is None

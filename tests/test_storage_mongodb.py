"""Tests for MongoDB storage backend."""

import pytest
import time
import pytest_asyncio
from typing import Generator, AsyncGenerator
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
from pywebguard.storage._mongodb import (
    MongoDBStorage,
    AsyncMongoDBStorage,
    MONGODB_AVAILABLE,
)

# Skip tests if MongoDB is not available
pytestmark = pytest.mark.skipif(
    not MONGODB_AVAILABLE,
    reason="MongoDB is not installed",
)


class TestMongoDBStorage:
    """Tests for MongoDBStorage."""

    @pytest.fixture
    def mock_collection(self):
        """Create a mock MongoDB collection."""
        collection = MagicMock()
        collection.find_one.return_value = None
        collection.update_one.return_value = None
        collection.delete_one.return_value = None
        collection.delete_many.return_value = None
        return collection

    @pytest.fixture
    def mongodb_storage(self, mock_collection) -> Generator[MongoDBStorage, None, None]:
        """Create a MongoDB storage instance for testing."""
        with patch("pywebguard.storage._mongodb.MongoClient") as mock_client:
            mock_db = MagicMock()
            mock_db.__getitem__.return_value = mock_collection
            mock_client.return_value.__getitem__.return_value = mock_db

            storage = MongoDBStorage(
                url="mongodb://localhost:27017/pywebguard_test",
                collection_name="test_collection",
                ttl=3600,
            )
            storage.collection = mock_collection
            yield storage
            storage.clear()
            storage.close()

    def test_initialization(self):
        """Test storage initialization."""
        with patch("pywebguard.storage._mongodb.MongoClient") as mock_client:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_db.__getitem__.return_value = mock_collection
            mock_client.return_value.__getitem__.return_value = mock_db

            storage = MongoDBStorage()
            assert storage.collection == mock_collection
            assert storage.ttl == 3600
            storage.close()

    def test_get_set(self, mongodb_storage: MongoDBStorage, mock_collection: MagicMock):
        """Test basic get and set operations."""
        # Test string value
        mock_collection.find_one.return_value = {"value": "test_value"}
        mongodb_storage.set("test_key", "test_value")
        assert mongodb_storage.get("test_key") == "test_value"

        # Test dict value
        test_dict = {"key": "value", "nested": {"inner": "value"}}
        mock_collection.find_one.return_value = {"value": test_dict}
        mongodb_storage.set("test_dict", test_dict)
        assert mongodb_storage.get("test_dict") == test_dict

        # Test non-existent key
        mock_collection.find_one.return_value = None
        assert mongodb_storage.get("non_existent") is None

    def test_delete(self, mongodb_storage: MongoDBStorage, mock_collection: MagicMock):
        """Test delete operation."""
        mock_collection.find_one.return_value = {"value": "test_value"}
        mongodb_storage.set("test_key", "test_value")
        assert mongodb_storage.get("test_key") == "test_value"
        mongodb_storage.delete("test_key")
        mock_collection.delete_one.assert_called_once()

    def test_exists(self, mongodb_storage: MongoDBStorage, mock_collection: MagicMock):
        """Test exists operation."""
        mock_collection.find_one.return_value = None
        assert not mongodb_storage.exists("test_key")

        mock_collection.find_one.return_value = {"value": "test_value"}
        assert mongodb_storage.exists("test_key")

    def test_increment(
        self, mongodb_storage: MongoDBStorage, mock_collection: MagicMock
    ):
        """Test increment operation."""
        # Mock find_one_and_update to simulate increment
        mock_collection.find_one_and_update.return_value = {"value": 1}
        assert mongodb_storage.increment("counter") == 1

        mock_collection.find_one_and_update.return_value = {"value": 2}
        assert mongodb_storage.increment("counter") == 2

        mock_collection.find_one_and_update.return_value = {"value": 7}
        assert mongodb_storage.increment("counter", 5) == 7

    def test_ttl(self, mongodb_storage: MongoDBStorage, mock_collection: MagicMock):
        """Test TTL functionality."""
        # Mock document with expiry
        mock_collection.find_one.return_value = {
            "value": "test_value",
            "expires_at": datetime.utcnow() + timedelta(seconds=1),
        }
        mongodb_storage.set("test_key", "test_value", ttl=1)
        assert mongodb_storage.get("test_key") == "test_value"

        # Mock expired document
        mock_collection.find_one.return_value = None
        assert mongodb_storage.get("test_key") is None

    def test_clear(self, mongodb_storage: MongoDBStorage, mock_collection: MagicMock):
        """Test clear operation."""
        mongodb_storage.clear()
        mock_collection.delete_many.assert_called_once_with({})


class TestAsyncMongoDBStorage:
    """Tests for AsyncMongoDBStorage."""

    @pytest.fixture
    def mock_collection(self):
        """Create a mock MongoDB collection."""
        collection = AsyncMock()
        collection.find_one.return_value = None
        collection.update_one.return_value = None
        collection.delete_one.return_value = None
        collection.delete_many.return_value = None
        collection.create_index.return_value = None
        return collection

    @pytest_asyncio.fixture
    async def async_mongodb_storage(
        self, mock_collection
    ) -> AsyncGenerator[AsyncMongoDBStorage, None]:
        """Create an async MongoDB storage instance for testing."""
        with patch("pymongo.AsyncMongoClient") as mock_client:
            mock_db = AsyncMock()
            mock_db.__getitem__.return_value = mock_collection
            mock_client.return_value.__getitem__.return_value = mock_db

            storage = AsyncMongoDBStorage(
                url="mongodb://localhost:27017/pywebguard_test",
                collection_name="test_collection_async",
                ttl=3600,
            )
            storage.collection = mock_collection
            await storage.initialize()
            yield storage
            await storage.clear()
            await storage.close()

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test storage initialization."""
        mock_collection = AsyncMock()
        mock_db = AsyncMock()
        mock_db.__getitem__.return_value = mock_collection

        with patch("pymongo.AsyncMongoClient") as mock_client:
            mock_client.return_value.__getitem__.return_value = mock_db

            storage = AsyncMongoDBStorage()
            storage.collection = mock_collection
            await storage.initialize()

            assert storage.collection == mock_collection
            assert storage.ttl == 3600

    @pytest.mark.asyncio
    async def test_get_set(
        self, async_mongodb_storage: AsyncMongoDBStorage, mock_collection: AsyncMock
    ):
        """Test basic get and set operations."""
        # Test string value
        mock_collection.find_one.return_value = {"value": "test_value"}
        await async_mongodb_storage.set("test_key", "test_value")
        assert await async_mongodb_storage.get("test_key") == "test_value"

        # Test dict value
        test_dict = {"key": "value", "nested": {"inner": "value"}}
        mock_collection.find_one.return_value = {"value": test_dict}
        await async_mongodb_storage.set("test_dict", test_dict)
        assert await async_mongodb_storage.get("test_dict") == test_dict

        # Test non-existent key
        mock_collection.find_one.return_value = None
        assert await async_mongodb_storage.get("non_existent") is None

    @pytest.mark.asyncio
    async def test_delete(
        self, async_mongodb_storage: AsyncMongoDBStorage, mock_collection: AsyncMock
    ):
        """Test delete operation."""
        mock_collection.find_one.return_value = {"value": "test_value"}
        await async_mongodb_storage.set("test_key", "test_value")
        assert await async_mongodb_storage.get("test_key") == "test_value"
        await async_mongodb_storage.delete("test_key")
        mock_collection.delete_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_exists(
        self, async_mongodb_storage: AsyncMongoDBStorage, mock_collection: AsyncMock
    ):
        """Test exists operation."""
        mock_collection.find_one.return_value = None
        assert not await async_mongodb_storage.exists("test_key")

        mock_collection.find_one.return_value = {"value": "test_value"}
        assert await async_mongodb_storage.exists("test_key")

    @pytest.mark.asyncio
    async def test_increment(
        self, async_mongodb_storage: AsyncMongoDBStorage, mock_collection: AsyncMock
    ):
        """Test increment operation."""
        # Mock find_one_and_update to simulate increment
        mock_collection.find_one_and_update.return_value = {"value": 1}
        assert await async_mongodb_storage.increment("counter") == 1

        mock_collection.find_one_and_update.return_value = {"value": 2}
        assert await async_mongodb_storage.increment("counter") == 2

        mock_collection.find_one_and_update.return_value = {"value": 7}
        assert await async_mongodb_storage.increment("counter", 5) == 7

    @pytest.mark.asyncio
    async def test_ttl(
        self, async_mongodb_storage: AsyncMongoDBStorage, mock_collection: AsyncMock
    ):
        """Test TTL functionality."""
        # Mock document with expiry
        mock_collection.find_one.return_value = {
            "value": "test_value",
            "expires_at": datetime.utcnow() + timedelta(seconds=1),
        }
        await async_mongodb_storage.set("test_key", "test_value", ttl=1)
        assert await async_mongodb_storage.get("test_key") == "test_value"

        # Mock expired document
        mock_collection.find_one.return_value = None
        assert await async_mongodb_storage.get("test_key") is None

    @pytest.mark.asyncio
    async def test_clear(
        self, async_mongodb_storage: AsyncMongoDBStorage, mock_collection: AsyncMock
    ):
        """Test clear operation."""
        await async_mongodb_storage.clear()
        mock_collection.delete_many.assert_called_once_with({})

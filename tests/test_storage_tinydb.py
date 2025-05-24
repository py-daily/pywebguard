import pytest
import time
import pytest_asyncio
from typing import Generator, AsyncGenerator
from pywebguard.storage._tinydb import TinyDBStorage, AsyncTinyDBStorage

# NOTE: The TinyDB storage implementation should be updated to handle expiry=None in queries.


class TestTinyDBStorage:
    """Tests for TinyDBStorage."""

    @pytest.fixture
    def tinydb_storage(self) -> Generator[TinyDBStorage, None, None]:
        storage = TinyDBStorage(db_path=":memory:")
        yield storage
        storage.clear()

    def test_initialization(self):
        storage = TinyDBStorage()
        assert storage.db is not None
        assert storage.table is not None

    def test_get_set(self, tinydb_storage: TinyDBStorage):
        tinydb_storage.set("test_key", "test_value")
        assert tinydb_storage.get("test_key") == "test_value"
        tinydb_storage.set("test_dict", {"key": "value"})
        assert tinydb_storage.get("test_dict") == {"key": "value"}
        assert tinydb_storage.get("non_existent") is None

    def test_delete(self, tinydb_storage: TinyDBStorage):
        tinydb_storage.set("test_key", "test_value")
        assert tinydb_storage.get("test_key") == "test_value"
        tinydb_storage.delete("test_key")
        assert tinydb_storage.get("test_key") is None
        tinydb_storage.delete("non_existent")

    def test_exists(self, tinydb_storage: TinyDBStorage):
        tinydb_storage.set("test_key", "test_value")
        assert tinydb_storage.exists("test_key") is True
        assert tinydb_storage.exists("non_existent") is False

    def test_increment(self, tinydb_storage: TinyDBStorage):
        assert tinydb_storage.increment("counter") == 1
        assert tinydb_storage.increment("counter") == 2
        assert tinydb_storage.increment("counter", 5) == 7

    def test_ttl(self, tinydb_storage: TinyDBStorage):
        tinydb_storage.set("test_key", "test_value", ttl=1)
        assert tinydb_storage.get("test_key") == "test_value"
        time.sleep(1.1)
        assert tinydb_storage.get("test_key") is None

    def test_clear(self, tinydb_storage: TinyDBStorage):
        tinydb_storage.set("key1", "value1")
        tinydb_storage.set("key2", "value2")
        tinydb_storage.clear()
        assert tinydb_storage.get("key1") is None
        assert tinydb_storage.get("key2") is None


class TestAsyncTinyDBStorage:
    """Tests for AsyncTinyDBStorage."""

    @pytest_asyncio.fixture
    async def async_tinydb_storage(self) -> AsyncGenerator[AsyncTinyDBStorage, None]:
        storage = AsyncTinyDBStorage(db_path=":memory:")
        yield storage
        await storage.clear()

    def test_initialization(self):
        storage = AsyncTinyDBStorage()
        assert storage.db is not None
        assert storage.table is not None

    @pytest.mark.asyncio
    async def test_get_set(self, async_tinydb_storage: AsyncTinyDBStorage):
        await async_tinydb_storage.set("test_key", "test_value")
        assert await async_tinydb_storage.get("test_key") == "test_value"
        await async_tinydb_storage.set("test_dict", {"key": "value"})
        assert await async_tinydb_storage.get("test_dict") == {"key": "value"}
        assert await async_tinydb_storage.get("non_existent") is None

    @pytest.mark.asyncio
    async def test_delete(self, async_tinydb_storage: AsyncTinyDBStorage):
        await async_tinydb_storage.set("test_key", "test_value")
        assert await async_tinydb_storage.get("test_key") == "test_value"
        await async_tinydb_storage.delete("test_key")
        assert await async_tinydb_storage.get("test_key") is None
        await async_tinydb_storage.delete("non_existent")

    @pytest.mark.asyncio
    async def test_exists(self, async_tinydb_storage: AsyncTinyDBStorage):
        await async_tinydb_storage.set("test_key", "test_value")
        assert await async_tinydb_storage.exists("test_key") is True
        assert await async_tinydb_storage.exists("non_existent") is False

    @pytest.mark.asyncio
    async def test_increment(self, async_tinydb_storage: AsyncTinyDBStorage):
        assert await async_tinydb_storage.increment("counter") == 1
        assert await async_tinydb_storage.increment("counter") == 2
        assert await async_tinydb_storage.increment("counter", 5) == 7

    @pytest.mark.asyncio
    async def test_clear(self, async_tinydb_storage: AsyncTinyDBStorage):
        await async_tinydb_storage.set("key1", "value1")
        await async_tinydb_storage.set("key2", "value2")
        await async_tinydb_storage.clear()
        assert await async_tinydb_storage.get("key1") is None
        assert await async_tinydb_storage.get("key2") is None

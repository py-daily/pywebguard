import pytest
from pywebguard.storage.memory import MemoryStorage, AsyncMemoryStorage
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage


class TestMemoryStorage:
    """Tests for MemoryStorage."""

    @pytest.fixture
    def memory_storage(self) -> MemoryStorage:
        return MemoryStorage()

    def test_initialization(self, memory_storage: MemoryStorage):
        assert isinstance(memory_storage, BaseStorage)
        assert memory_storage._storage == {}
        assert memory_storage._ttls == {}

    def test_set_get(self, memory_storage: MemoryStorage):
        memory_storage.set("key1", "value1")
        assert memory_storage.get("key1") == "value1"

    def test_delete(self, memory_storage: MemoryStorage):
        memory_storage.set("key1", "value1")
        memory_storage.delete("key1")
        assert memory_storage.get("key1") is None

    def test_clear(self, memory_storage: MemoryStorage):
        memory_storage.set("key1", "value1")
        memory_storage.set("key2", "value2")
        memory_storage.clear()
        assert memory_storage._storage == {}
        assert memory_storage._ttls == {}


class TestAsyncMemoryStorage:
    """Tests for AsyncMemoryStorage."""

    @pytest.fixture
    def async_memory_storage(self) -> AsyncMemoryStorage:
        return AsyncMemoryStorage()

    def test_initialization(self, async_memory_storage: AsyncMemoryStorage):
        assert isinstance(async_memory_storage, AsyncBaseStorage)
        assert async_memory_storage._storage._storage == {}
        assert async_memory_storage._storage._ttls == {}

    @pytest.mark.asyncio
    async def test_set_get(self, async_memory_storage: AsyncMemoryStorage):
        await async_memory_storage.set("key1", "value1")
        assert await async_memory_storage.get("key1") == "value1"

    @pytest.mark.asyncio
    async def test_delete(self, async_memory_storage: AsyncMemoryStorage):
        await async_memory_storage.set("key1", "value1")
        await async_memory_storage.delete("key1")
        assert await async_memory_storage.get("key1") is None

    @pytest.mark.asyncio
    async def test_clear(self, async_memory_storage: AsyncMemoryStorage):
        await async_memory_storage.set("key1", "value1")
        await async_memory_storage.set("key2", "value2")
        await async_memory_storage.clear()
        assert async_memory_storage._storage._storage == {}
        assert async_memory_storage._storage._ttls == {}

import pytest
import time
import tempfile
import os
import pytest_asyncio
from typing import Generator, AsyncGenerator
from pywebguard.storage._sqlite import SQLiteStorage, AsyncSQLiteStorage

if __name__ == "__main__":
    pytest.main()


class TestSQLiteStorage:
    """Tests for SQLiteStorage."""

    @pytest.fixture
    def sqlite_storage(self) -> Generator[SQLiteStorage, None, None]:
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmpfile.name
        tmpfile.close()
        storage = SQLiteStorage(db_path=db_path)
        storage._init_db()
        yield storage
        storage.clear()
        os.unlink(db_path)

    def test_initialization(self):
        storage = SQLiteStorage()
        assert storage.db_path == ":memory:"
        assert storage.table_name == "pywebguard"

    def test_get_set(self, sqlite_storage: SQLiteStorage):
        sqlite_storage.set("test_key", "test_value")
        assert sqlite_storage.get("test_key") == "test_value"
        sqlite_storage.set("test_dict", {"key": "value"})
        assert sqlite_storage.get("test_dict") == {"key": "value"}
        assert sqlite_storage.get("non_existent") is None

    def test_delete(self, sqlite_storage: SQLiteStorage):
        sqlite_storage.set("test_key", "test_value")
        assert sqlite_storage.get("test_key") == "test_value"
        sqlite_storage.delete("test_key")
        assert sqlite_storage.get("test_key") is None

    def test_exists(self, sqlite_storage: SQLiteStorage):
        assert not sqlite_storage.exists("test_key")
        sqlite_storage.set("test_key", "test_value")
        assert sqlite_storage.exists("test_key")
        sqlite_storage.delete("test_key")
        assert not sqlite_storage.exists("test_key")

    def test_increment(self, sqlite_storage: SQLiteStorage):
        assert sqlite_storage.increment("counter") == 1
        assert sqlite_storage.increment("counter") == 2
        assert sqlite_storage.increment("counter", 5) == 7

    def test_ttl(self, sqlite_storage: SQLiteStorage):
        sqlite_storage.set("test_key", "test_value", ttl=1)
        assert sqlite_storage.get("test_key") == "test_value"
        time.sleep(1.1)
        assert sqlite_storage.get("test_key") is None

    def test_clear(self, sqlite_storage: SQLiteStorage):
        sqlite_storage.set("key1", "value1")
        sqlite_storage.set("key2", "value2")
        sqlite_storage.clear()
        assert sqlite_storage.get("key1") is None
        assert sqlite_storage.get("key2") is None


class TestAsyncSQLiteStorage:
    """Tests for AsyncSQLiteStorage."""

    @pytest_asyncio.fixture
    async def async_sqlite_storage(self) -> AsyncGenerator[AsyncSQLiteStorage, None]:
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmpfile.name
        tmpfile.close()
        storage = AsyncSQLiteStorage(db_path=db_path)
        await storage._init_db()
        yield storage
        await storage.clear()
        os.unlink(db_path)

    def test_initialization(self):
        storage = AsyncSQLiteStorage()
        assert storage.db_path == ":memory:"
        assert storage.table_name == "pywebguard"

    @pytest.mark.asyncio
    async def test_get_set(self, async_sqlite_storage: AsyncSQLiteStorage):
        await async_sqlite_storage.set("test_key", "test_value")
        assert await async_sqlite_storage.get("test_key") == "test_value"
        await async_sqlite_storage.set("test_dict", {"key": "value"})
        assert await async_sqlite_storage.get("test_dict") == {"key": "value"}
        assert await async_sqlite_storage.get("non_existent") is None

    @pytest.mark.asyncio
    async def test_delete(self, async_sqlite_storage: AsyncSQLiteStorage):
        await async_sqlite_storage.set("test_key", "test_value")
        assert await async_sqlite_storage.get("test_key") == "test_value"
        await async_sqlite_storage.delete("test_key")
        assert await async_sqlite_storage.get("test_key") is None

    @pytest.mark.asyncio
    async def test_exists(self, async_sqlite_storage: AsyncSQLiteStorage):
        assert not await async_sqlite_storage.exists("test_key")
        await async_sqlite_storage.set("test_key", "test_value")
        assert await async_sqlite_storage.exists("test_key")
        await async_sqlite_storage.delete("test_key")
        assert not await async_sqlite_storage.exists("test_key")

    @pytest.mark.asyncio
    async def test_increment(self, async_sqlite_storage: AsyncSQLiteStorage):
        assert await async_sqlite_storage.increment("counter") == 1
        assert await async_sqlite_storage.increment("counter") == 2
        assert await async_sqlite_storage.increment("counter", 5) == 7

    @pytest.mark.asyncio
    async def test_ttl(self, async_sqlite_storage: AsyncSQLiteStorage):
        await async_sqlite_storage.set("test_key", "test_value", ttl=1)
        assert await async_sqlite_storage.get("test_key") == "test_value"
        time.sleep(1.1)
        assert await async_sqlite_storage.get("test_key") is None

    @pytest.mark.asyncio
    async def test_clear(self, async_sqlite_storage: AsyncSQLiteStorage):
        await async_sqlite_storage.set("key1", "value1")
        await async_sqlite_storage.set("key2", "value2")
        await async_sqlite_storage.clear()
        assert await async_sqlite_storage.get("key1") is None
        assert await async_sqlite_storage.get("key2") is None

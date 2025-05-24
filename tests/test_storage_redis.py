import pytest
import time
from pywebguard.storage._redis import RedisStorage, AsyncRedisStorage
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage


class TestRedisStorage:
    """Tests for RedisStorage."""

    @pytest.fixture
    def redis_storage(self) -> RedisStorage:
        """Create a Redis storage for testing using a mock Redis client."""

        class MockRedis:
            def __init__(self):
                self._data = {}
                self._ttls = {}

            def get(self, key):
                if key in self._data:
                    if key in self._ttls and self._ttls[key] < time.time():
                        del self._data[key]
                        del self._ttls[key]
                        return None
                    return self._data[key]
                return None

            def set(self, key, value):
                self._data[key] = value

            def setex(self, key, ttl, value):
                self._data[key] = value
                self._ttls[key] = time.time() + ttl

            def delete(self, *keys):
                for key in keys:
                    self._data.pop(key, None)
                    self._ttls.pop(key, None)

            def incrby(self, key, amount):
                current = int(self._data.get(key, 0) or 0)
                new_value = current + amount
                self._data[key] = str(new_value)
                return new_value

            def exists(self, key):
                return key in self._data

            def keys(self, pattern):
                return [k for k in self._data.keys() if k.startswith(pattern[:-1])]

        mock_redis = MockRedis()
        storage = RedisStorage(url="redis://localhost:6379/0")
        storage.redis = mock_redis
        return storage

    def test_initialization(self, redis_storage: RedisStorage):
        assert isinstance(redis_storage, BaseStorage)

    def test_set_get(self, redis_storage: RedisStorage):
        redis_storage.set("key1", "value1")
        assert redis_storage.get("key1") == "value1"

    def test_delete(self, redis_storage: RedisStorage):
        redis_storage.set("key1", "value1")
        redis_storage.delete("key1")
        assert redis_storage.get("key1") is None

    def test_clear(self, redis_storage: RedisStorage):
        redis_storage.set("key1", "value1")
        redis_storage.set("key2", "value2")
        redis_storage.clear()
        assert redis_storage.get("key1") is None
        assert redis_storage.get("key2") is None


class TestAsyncRedisStorage:
    """Tests for AsyncRedisStorage."""

    @pytest.fixture
    def async_redis_storage(self) -> AsyncRedisStorage:
        class MockRedis:
            def __init__(self):
                self._data = {}
                self._ttls = {}

            async def get(self, key):
                if key in self._data:
                    if key in self._ttls and self._ttls[key] < time.time():
                        del self._data[key]
                        del self._ttls[key]
                        return None
                    return self._data[key]
                return None

            async def set(self, key, value):
                self._data[key] = value

            async def setex(self, key, ttl, value):
                self._data[key] = value
                self._ttls[key] = time.time() + ttl

            async def delete(self, *keys):
                for key in keys:
                    self._data.pop(key, None)
                    self._ttls.pop(key, None)

            async def incrby(self, key, amount):
                current = int(self._data.get(key, 0) or 0)
                new_value = current + amount
                self._data[key] = str(new_value)
                return new_value

            async def exists(self, key):
                return key in self._data

            async def keys(self, pattern):
                return [k for k in self._data.keys() if k.startswith(pattern[:-1])]

        mock_redis = MockRedis()
        storage = AsyncRedisStorage(url="redis://localhost:6379/0")
        storage.redis = mock_redis
        return storage

    def test_initialization(self, async_redis_storage: AsyncRedisStorage):
        assert isinstance(async_redis_storage, AsyncBaseStorage)

    @pytest.mark.asyncio
    async def test_set_get(self, async_redis_storage: AsyncRedisStorage):
        await async_redis_storage.set("key1", "value1")
        assert await async_redis_storage.get("key1") == "value1"

    @pytest.mark.asyncio
    async def test_delete(self, async_redis_storage: AsyncRedisStorage):
        await async_redis_storage.set("key1", "value1")
        await async_redis_storage.delete("key1")
        assert await async_redis_storage.get("key1") is None

    @pytest.mark.asyncio
    async def test_clear(self, async_redis_storage: AsyncRedisStorage):
        await async_redis_storage.set("key1", "value1")
        await async_redis_storage.set("key2", "value2")
        await async_redis_storage.clear()
        assert await async_redis_storage.get("key1") is None
        assert await async_redis_storage.get("key2") is None

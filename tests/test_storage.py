"""Tests for PyWebGuard storage backends."""

import pytest
import time
from typing import Dict, Any, cast, Optional

from pywebguard.storage.memory import MemoryStorage, AsyncMemoryStorage
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage

# Try to import Redis storage if available
try:
    from pywebguard.storage._redis import RedisStorage, AsyncRedisStorage

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Try to import SQLite storage if available
try:
    from pywebguard.storage._sqlite import SQLiteStorage, AsyncSQLiteStorage

    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

# Try to import TinyDB storage if available
try:
    from pywebguard.storage._tinydb import TinyDBStorage, AsyncTinyDBStorage

    TINYDB_AVAILABLE = True
except ImportError:
    TINYDB_AVAILABLE = False


class TestMemoryStorage:
    """Tests for MemoryStorage."""

    def test_initialization(self):
        """Test MemoryStorage initialization."""
        storage = MemoryStorage()
        assert storage._storage == {}
        assert storage._ttls == {}

    def test_get_set(self):
        """Test getting and setting values."""
        storage = MemoryStorage()

        # Test setting and getting a string
        storage.set("test_key", "test_value")
        assert storage.get("test_key") == "test_value"

        # Test setting and getting a dictionary
        storage.set("test_dict", {"key": "value"})
        assert storage.get("test_dict") == {"key": "value"}

        # Test getting a non-existent key
        assert storage.get("non_existent") is None

    def test_delete(self):
        """Test deleting values."""
        storage = MemoryStorage()

        # Set a value
        storage.set("test_key", "test_value")
        assert storage.get("test_key") == "test_value"

        # Delete the value
        storage.delete("test_key")
        assert storage.get("test_key") is None

        # Delete a non-existent key (should not raise an exception)
        storage.delete("non_existent")

    def test_exists(self):
        """Test checking if a key exists."""
        storage = MemoryStorage()

        # Set a value
        storage.set("test_key", "test_value")
        assert storage.exists("test_key") is True

        # Check a non-existent key
        assert storage.exists("non_existent") is False

    def test_increment(self):
        """Test incrementing a counter."""
        storage = MemoryStorage()

        # Increment a non-existent key (should start at 0)
        assert storage.increment("counter") == 1

        # Increment again
        assert storage.increment("counter") == 2

        # Increment by a specific amount
        assert storage.increment("counter", 5) == 7

        # Try to increment a non-numeric value
        storage.set("string", "not_a_number")
        with pytest.raises(ValueError):
            storage.increment("string")

    def test_ttl(self):
        """Test time-to-live functionality."""
        storage = MemoryStorage()

        # Set a value with a short TTL
        storage.set("test_key", "test_value", ttl=1)
        assert storage.get("test_key") == "test_value"

        # Wait for the TTL to expire
        time.sleep(1.1)

        # The value should be gone
        assert storage.get("test_key") is None

    def test_clear(self):
        """Test clearing all values."""
        storage = MemoryStorage()

        # Set some values
        storage.set("key1", "value1")
        storage.set("key2", "value2")

        # Clear all values
        storage.clear()

        # All values should be gone
        assert storage.get("key1") is None
        assert storage.get("key2") is None


class TestAsyncMemoryStorage:
    """Tests for AsyncMemoryStorage."""

    def test_initialization(self):
        """Test AsyncMemoryStorage initialization."""
        storage = AsyncMemoryStorage()
        assert isinstance(storage._storage, MemoryStorage)

    @pytest.mark.asyncio
    async def test_get_set(self):
        """Test getting and setting values asynchronously."""
        storage = AsyncMemoryStorage()

        # Test setting and getting a string
        await storage.set("test_key", "test_value")
        assert await storage.get("test_key") == "test_value"

        # Test setting and getting a dictionary
        await storage.set("test_dict", {"key": "value"})
        assert await storage.get("test_dict") == {"key": "value"}

        # Test getting a non-existent key
        assert await storage.get("non_existent") is None

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test deleting values asynchronously."""
        storage = AsyncMemoryStorage()

        # Set a value
        await storage.set("test_key", "test_value")
        assert await storage.get("test_key") == "test_value"

        # Delete the value
        await storage.delete("test_key")
        assert await storage.get("test_key") is None

        # Delete a non-existent key (should not raise an exception)
        await storage.delete("non_existent")

    @pytest.mark.asyncio
    async def test_exists(self):
        """Test checking if a key exists asynchronously."""
        storage = AsyncMemoryStorage()

        # Set a value
        await storage.set("test_key", "test_value")
        assert await storage.exists("test_key") is True

        # Check a non-existent key
        assert await storage.exists("non_existent") is False

    @pytest.mark.asyncio
    async def test_increment(self):
        """Test incrementing a counter asynchronously."""
        storage = AsyncMemoryStorage()

        # Increment a non-existent key (should start at 0)
        assert await storage.increment("counter") == 1

        # Increment again
        assert await storage.increment("counter") == 2

        # Increment by a specific amount
        assert await storage.increment("counter", 5) == 7

        # Try to increment a non-numeric value
        await storage.set("string", "not_a_number")
        with pytest.raises(ValueError):
            await storage.increment("string")

    @pytest.mark.asyncio
    async def test_clear(self):
        """Test clearing all values asynchronously."""
        storage = AsyncMemoryStorage()

        # Set some values
        await storage.set("key1", "value1")
        await storage.set("key2", "value2")

        # Clear all values
        await storage.clear()

        # All values should be gone
        assert await storage.get("key1") is None
        assert await storage.get("key2") is None


# Only run Redis tests if Redis is available
if REDIS_AVAILABLE:

    class TestRedisStorage:
        """Tests for RedisStorage."""

        @pytest.fixture
        def redis_storage(self) -> RedisStorage:
            """Create a Redis storage instance for testing."""
            # Use a test-specific prefix to avoid conflicts
            storage = RedisStorage(prefix="pywebguard_test:")
            yield storage
            # Clean up after tests
            storage.clear()

        def test_initialization(self):
            """Test RedisStorage initialization."""
            storage = RedisStorage()
            assert storage.prefix == "pywebguard:"

        def test_get_set(self, redis_storage: RedisStorage):
            """Test getting and setting values."""
            # Test setting and getting a string
            redis_storage.set("test_key", "test_value")
            assert redis_storage.get("test_key") == "test_value"

            # Test setting and getting a dictionary
            redis_storage.set("test_dict", {"key": "value"})
            assert redis_storage.get("test_dict") == {"key": "value"}

            # Test getting a non-existent key
            assert redis_storage.get("non_existent") is None

        def test_delete(self, redis_storage: RedisStorage):
            """Test deleting values."""
            # Set a value
            redis_storage.set("test_key", "test_value")
            assert redis_storage.get("test_key") == "test_value"

            # Delete the value
            redis_storage.delete("test_key")
            assert redis_storage.get("test_key") is None

            # Delete a non-existent key (should not raise an exception)
            redis_storage.delete("non_existent")

        def test_exists(self, redis_storage: RedisStorage):
            """Test checking if a key exists."""
            # Set a value
            redis_storage.set("test_key", "test_value")
            assert redis_storage.exists("test_key") is True

            # Check a non-existent key
            assert redis_storage.exists("non_existent") is False

        def test_increment(self, redis_storage: RedisStorage):
            """Test incrementing a counter."""
            # Increment a non-existent key (should start at 0)
            assert redis_storage.increment("counter") == 1

            # Increment again
            assert redis_storage.increment("counter") == 2

            # Increment by a specific amount
            assert redis_storage.increment("counter", 5) == 7

        def test_ttl(self, redis_storage: RedisStorage):
            """Test time-to-live functionality."""
            # Set a value with a short TTL
            redis_storage.set("test_key", "test_value", ttl=1)
            assert redis_storage.get("test_key") == "test_value"

            # Wait for the TTL to expire
            time.sleep(1.1)

            # The value should be gone
            assert redis_storage.get("test_key") is None

        def test_clear(self, redis_storage: RedisStorage):
            """Test clearing all values."""
            # Set some values
            redis_storage.set("key1", "value1")
            redis_storage.set("key2", "value2")

            # Clear all values
            redis_storage.clear()

            # All values should be gone
            assert redis_storage.get("key1") is None
            assert redis_storage.get("key2") is None

    class TestAsyncRedisStorage:
        """Tests for AsyncRedisStorage."""

        @pytest.fixture
        async def async_redis_storage(self) -> AsyncRedisStorage:
            """Create an AsyncRedisStorage instance for testing."""
            # Use a test-specific prefix to avoid conflicts
            storage = AsyncRedisStorage(prefix="pywebguard_test_async:")
            yield storage
            # Clean up after tests
            await storage.clear()

        def test_initialization(self):
            """Test AsyncRedisStorage initialization."""
            storage = AsyncRedisStorage()
            assert storage.prefix == "pywebguard:"

        @pytest.mark.asyncio
        async def test_get_set(self, async_redis_storage: AsyncRedisStorage):
            """Test getting and setting values asynchronously."""
            # Test setting and getting a string
            await async_redis_storage.set("test_key", "test_value")
            assert await async_redis_storage.get("test_key") == "test_value"

            # Test setting and getting a dictionary
            await async_redis_storage.set("test_dict", {"key": "value"})
            assert await async_redis_storage.get("test_dict") == {"key": "value"}

            # Test getting a non-existent key
            assert await async_redis_storage.get("non_existent") is None

        @pytest.mark.asyncio
        async def test_delete(self, async_redis_storage: AsyncRedisStorage):
            """Test deleting values asynchronously."""
            # Set a value
            await async_redis_storage.set("test_key", "test_value")
            assert await async_redis_storage.get("test_key") == "test_value"

            # Delete the value
            await async_redis_storage.delete("test_key")
            assert await async_redis_storage.get("test_key") is None

            # Delete a non-existent key (should not raise an exception)
            await async_redis_storage.delete("non_existent")

        @pytest.mark.asyncio
        async def test_exists(self, async_redis_storage: AsyncRedisStorage):
            """Test checking if a key exists asynchronously."""
            # Set a value
            await async_redis_storage.set("test_key", "test_value")
            assert await async_redis_storage.exists("test_key") is True

            # Check a non-existent key
            assert await async_redis_storage.exists("non_existent") is False

        @pytest.mark.asyncio
        async def test_increment(self, async_redis_storage: AsyncRedisStorage):
            """Test incrementing a counter asynchronously."""
            # Increment a non-existent key (should start at 0)
            assert await async_redis_storage.increment("counter") == 1

            # Increment again
            assert await async_redis_storage.increment("counter") == 2

            # Increment by a specific amount
            assert await async_redis_storage.increment("counter", 5) == 7

        @pytest.mark.asyncio
        async def test_clear(self, async_redis_storage: AsyncRedisStorage):
            """Test clearing all values asynchronously."""
            # Set some values
            await async_redis_storage.set("key1", "value1")
            await async_redis_storage.set("key2", "value2")

            # Clear all values
            await async_redis_storage.clear()

            # All values should be gone
            assert await async_redis_storage.get("key1") is None
            assert await async_redis_storage.get("key2") is None


# Only run SQLite tests if SQLite is available
if SQLITE_AVAILABLE:

    class TestSQLiteStorage:
        """Tests for SQLiteStorage."""

        @pytest.fixture
        def sqlite_storage(self) -> SQLiteStorage:
            """Create a SQLite storage instance for testing."""
            # Use in-memory database for testing
            storage = SQLiteStorage(db_path=":memory:")
            yield storage
            # Clean up after tests
            storage.clear()

        def test_initialization(self):
            """Test SQLiteStorage initialization."""
            storage = SQLiteStorage()
            assert storage.db_path == ":memory:"
            assert storage.table_name == "pywebguard"

        def test_get_set(self, sqlite_storage: SQLiteStorage):
            """Test getting and setting values."""
            # Test setting and getting a string
            sqlite_storage.set("test_key", "test_value")
            assert sqlite_storage.get("test_key") == "test_value"

            # Test setting and getting a dictionary
            sqlite_storage.set("test_dict", {"key": "value"})
            assert sqlite_storage.get("test_dict") == {"key": "value"}

            # Test getting a non-existent key
            assert sqlite_storage.get("non_existent") is None

        def test_delete(self, sqlite_storage: SQLiteStorage):
            """Test deleting values."""
            # Set a value
            sqlite_storage.set("test_key", "test_value")
            assert sqlite_storage.get("test_key") == "test_value"

            # Delete the value
            sqlite_storage.delete("test_key")
            assert sqlite_storage.get("test_key") is None

            # Delete a non-existent key (should not raise an exception)
            sqlite_storage.delete("non_existent")

        def test_exists(self, sqlite_storage: SQLiteStorage):
            """Test checking if a key exists."""
            # Set a value
            sqlite_storage.set("test_key", "test_value")
            assert sqlite_storage.exists("test_key") is True

            # Check a non-existent key
            assert sqlite_storage.exists("non_existent") is False

        def test_increment(self, sqlite_storage: SQLiteStorage):
            """Test incrementing a counter."""
            # Increment a non-existent key (should start at 0)
            assert sqlite_storage.increment("counter") == 1

            # Increment again
            assert sqlite_storage.increment("counter") == 2

            # Increment by a specific amount
            assert sqlite_storage.increment("counter", 5) == 7

        def test_ttl(self, sqlite_storage: SQLiteStorage):
            """Test time-to-live functionality."""
            # Set a value with a short TTL
            sqlite_storage.set("test_key", "test_value", ttl=1)
            assert sqlite_storage.get("test_key") == "test_value"

            # Wait for the TTL to expire
            time.sleep(1.1)

            # The value should be gone
            assert sqlite_storage.get("test_key") is None

        def test_clear(self, sqlite_storage: SQLiteStorage):
            """Test clearing all values."""
            # Set some values
            sqlite_storage.set("key1", "value1")
            sqlite_storage.set("key2", "value2")

            # Clear all values
            sqlite_storage.clear()

            # All values should be gone
            assert sqlite_storage.get("key1") is None
            assert sqlite_storage.get("key2") is None

    class TestAsyncSQLiteStorage:
        """Tests for AsyncSQLiteStorage."""

        @pytest.fixture
        async def async_sqlite_storage(self) -> AsyncSQLiteStorage:
            """Create an AsyncSQLiteStorage instance for testing."""
            # Use in-memory database for testing
            storage = AsyncSQLiteStorage(db_path=":memory:")
            yield storage
            # Clean up after tests
            await storage.clear()

        def test_initialization(self):
            """Test AsyncSQLiteStorage initialization."""
            storage = AsyncSQLiteStorage()
            assert storage.db_path == ":memory:"
            assert storage.table_name == "pywebguard"

        @pytest.mark.asyncio
        async def test_get_set(self, async_sqlite_storage: AsyncSQLiteStorage):
            """Test getting and setting values asynchronously."""
            # Test setting and getting a string
            await async_sqlite_storage.set("test_key", "test_value")
            assert await async_sqlite_storage.get("test_key") == "test_value"

            # Test setting and getting a dictionary
            await async_sqlite_storage.set("test_dict", {"key": "value"})
            assert await async_sqlite_storage.get("test_dict") == {"key": "value"}

            # Test getting a non-existent key
            assert await async_sqlite_storage.get("non_existent") is None

        @pytest.mark.asyncio
        async def test_delete(self, async_sqlite_storage: AsyncSQLiteStorage):
            """Test deleting values asynchronously."""
            # Set a value
            await async_sqlite_storage.set("test_key", "test_value")
            assert await async_sqlite_storage.get("test_key") == "test_value"

            # Delete the value
            await async_sqlite_storage.delete("test_key")
            assert await async_sqlite_storage.get("test_key") is None

            # Delete a non-existent key (should not raise an exception)
            await async_sqlite_storage.delete("non_existent")

        @pytest.mark.asyncio
        async def test_exists(self, async_sqlite_storage: AsyncSQLiteStorage):
            """Test checking if a key exists asynchronously."""
            # Set a value
            await async_sqlite_storage.set("test_key", "test_value")
            assert await async_sqlite_storage.exists("test_key") is True

            # Check a non-existent key
            assert await async_sqlite_storage.exists("non_existent") is False

        @pytest.mark.asyncio
        async def test_increment(self, async_sqlite_storage: AsyncSQLiteStorage):
            """Test incrementing a counter asynchronously."""
            # Increment a non-existent key (should start at 0)
            assert await async_sqlite_storage.increment("counter") == 1

            # Increment again
            assert await async_sqlite_storage.increment("counter") == 2

            # Increment by a specific amount
            assert await async_sqlite_storage.increment("counter", 5) == 7

        @pytest.mark.asyncio
        async def test_clear(self, async_sqlite_storage: AsyncSQLiteStorage):
            """Test clearing all values asynchronously."""
            # Set some values
            await async_sqlite_storage.set("key1", "value1")
            await async_sqlite_storage.set("key2", "value2")

            # Clear all values
            await async_sqlite_storage.clear()

            # All values should be gone
            assert await async_sqlite_storage.get("key1") is None
            assert await async_sqlite_storage.get("key2") is None


# Only run TinyDB tests if TinyDB is available
if TINYDB_AVAILABLE:

    class TestTinyDBStorage:
        """Tests for TinyDBStorage."""

        @pytest.fixture
        def tinydb_storage(self) -> TinyDBStorage:
            """Create a TinyDB storage instance for testing."""
            # Use in-memory database for testing
            storage = TinyDBStorage(db_path=":memory:")
            yield storage
            # Clean up after tests
            storage.clear()

        def test_initialization(self):
            """Test TinyDBStorage initialization."""
            storage = TinyDBStorage()
            assert storage.db_path == "pywebguard.json"
            assert storage.table_name == "default"

        def test_get_set(self, tinydb_storage: TinyDBStorage):
            """Test getting and setting values."""
            # Test setting and getting a string
            tinydb_storage.set("test_key", "test_value")
            assert tinydb_storage.get("test_key") == "test_value"

            # Test setting and getting a dictionary
            tinydb_storage.set("test_dict", {"key": "value"})
            assert tinydb_storage.get("test_dict") == {"key": "value"}

            # Test getting a non-existent key
            assert tinydb_storage.get("non_existent") is None

        def test_delete(self, tinydb_storage: TinyDBStorage):
            """Test deleting values."""
            # Set a value
            tinydb_storage.set("test_key", "test_value")
            assert tinydb_storage.get("test_key") == "test_value"

            # Delete the value
            tinydb_storage.delete("test_key")
            assert tinydb_storage.get("test_key") is None

            # Delete a non-existent key (should not raise an exception)
            tinydb_storage.delete("non_existent")

        def test_exists(self, tinydb_storage: TinyDBStorage):
            """Test checking if a key exists."""
            # Set a value
            tinydb_storage.set("test_key", "test_value")
            assert tinydb_storage.exists("test_key") is True

            # Check a non-existent key
            assert tinydb_storage.exists("non_existent") is False

        def test_increment(self, tinydb_storage: TinyDBStorage):
            """Test incrementing a counter."""
            # Increment a non-existent key (should start at 0)
            assert tinydb_storage.increment("counter") == 1

            # Increment again
            assert tinydb_storage.increment("counter") == 2

            # Increment by a specific amount
            assert tinydb_storage.increment("counter", 5) == 7

        def test_ttl(self, tinydb_storage: TinyDBStorage):
            """Test time-to-live functionality."""
            # Set a value with a short TTL
            tinydb_storage.set("test_key", "test_value", ttl=1)
            assert tinydb_storage.get("test_key") == "test_value"

            # Wait for the TTL to expire
            time.sleep(1.1)

            # The value should be gone
            assert tinydb_storage.get("test_key") is None

        def test_clear(self, tinydb_storage: TinyDBStorage):
            """Test clearing all values."""
            # Set some values
            tinydb_storage.set("key1", "value1")
            tinydb_storage.set("key2", "value2")

            # Clear all values
            tinydb_storage.clear()

            # All values should be gone
            assert tinydb_storage.get("key1") is None
            assert tinydb_storage.get("key2") is None

    class TestAsyncTinyDBStorage:
        """Tests for AsyncTinyDBStorage."""

        @pytest.fixture
        async def async_tinydb_storage(self) -> AsyncTinyDBStorage:
            """Create an AsyncTinyDBStorage instance for testing."""
            # Use in-memory database for testing
            storage = AsyncTinyDBStorage(db_path=":memory:")
            yield storage
            # Clean up after tests
            await storage.clear()

        def test_initialization(self):
            """Test AsyncTinyDBStorage initialization."""
            storage = AsyncTinyDBStorage()
            assert storage.db_path == "pywebguard.json"
            assert storage.table_name == "default"

        @pytest.mark.asyncio
        async def test_get_set(self, async_tinydb_storage: AsyncTinyDBStorage):
            """Test getting and setting values asynchronously."""
            # Test setting and getting a string
            await async_tinydb_storage.set("test_key", "test_value")
            assert await async_tinydb_storage.get("test_key") == "test_value"

            # Test setting and getting a dictionary
            await async_tinydb_storage.set("test_dict", {"key": "value"})
            assert await async_tinydb_storage.get("test_dict") == {"key": "value"}

            # Test getting a non-existent key
            assert await async_tinydb_storage.get("non_existent") is None

        @pytest.mark.asyncio
        async def test_delete(self, async_tinydb_storage: AsyncTinyDBStorage):
            """Test deleting values asynchronously."""
            # Set a value
            await async_tinydb_storage.set("test_key", "test_value")
            assert await async_tinydb_storage.get("test_key") == "test_value"

            # Delete the value
            await async_tinydb_storage.delete("test_key")
            assert await async_tinydb_storage.get("test_key") is None

            # Delete a non-existent key (should not raise an exception)
            await async_tinydb_storage.delete("non_existent")

        @pytest.mark.asyncio
        async def test_exists(self, async_tinydb_storage: AsyncTinyDBStorage):
            """Test checking if a key exists asynchronously."""
            # Set a value
            await async_tinydb_storage.set("test_key", "test_value")
            assert await async_tinydb_storage.exists("test_key") is True

            # Check a non-existent key
            assert await async_tinydb_storage.exists("non_existent") is False

        @pytest.mark.asyncio
        async def test_increment(self, async_tinydb_storage: AsyncTinyDBStorage):
            """Test incrementing a counter asynchronously."""
            # Increment a non-existent key (should start at 0)
            assert await async_tinydb_storage.increment("counter") == 1

            # Increment again
            assert await async_tinydb_storage.increment("counter") == 2

            # Increment by a specific amount
            assert await async_tinydb_storage.increment("counter", 5) == 7

        @pytest.mark.asyncio
        async def test_clear(self, async_tinydb_storage: AsyncTinyDBStorage):
            """Test clearing all values asynchronously."""
            # Set some values
            await async_tinydb_storage.set("key1", "value1")
            await async_tinydb_storage.set("key2", "value2")

            # Clear all values
            await async_tinydb_storage.clear()

            # All values should be gone
            assert await async_tinydb_storage.get("key1") is None
            assert await async_tinydb_storage.get("key2") is None

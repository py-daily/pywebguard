"""Tests for PostgreSQL storage backend."""

import pytest
import time
import pytest_asyncio
from typing import Generator, AsyncGenerator
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
from pywebguard.storage._postgresql import (
    PostgreSQLStorage,
    AsyncPostgreSQLStorage,
    PSYCOPG2_AVAILABLE,
    ASYNCPG_AVAILABLE,
)

# Skip tests if PostgreSQL is not available
pytestmark = pytest.mark.skipif(
    not (PSYCOPG2_AVAILABLE or ASYNCPG_AVAILABLE),
    reason="PostgreSQL dependencies are not installed",
)


class TestPostgreSQLStorage:
    """Tests for PostgreSQLStorage."""

    @pytest.fixture
    def mock_connection(self):
        """Create a mock PostgreSQL connection."""
        connection = MagicMock()
        cursor = MagicMock()
        cursor.__enter__.return_value = cursor
        connection.cursor.return_value = cursor
        return connection, cursor

    @pytest.fixture
    def postgresql_storage(
        self, mock_connection
    ) -> Generator[PostgreSQLStorage, None, None]:
        """Create a PostgreSQL storage instance for testing."""
        connection, cursor = mock_connection
        with patch("psycopg2.connect") as mock_connect:
            mock_connect.return_value = connection

            storage = PostgreSQLStorage(
                url="postgresql://test:test@localhost:5432/test",
                table_name="test_table",
                ttl=3600,
            )
            storage.conn = connection
            yield storage
            storage.clear()
            storage.close()

    def test_initialization(self):
        """Test storage initialization."""
        with patch("psycopg2.connect") as mock_connect:
            connection = MagicMock()
            cursor = MagicMock()
            cursor.__enter__.return_value = cursor
            connection.cursor.return_value = cursor
            mock_connect.return_value = connection

            storage = PostgreSQLStorage()
            assert storage.conn == connection
            assert storage.table_name == "pywebguard"
            assert storage.ttl == 3600
            storage.close()

    def test_get_set(self, postgresql_storage: PostgreSQLStorage, mock_connection):
        """Test basic get and set operations."""
        connection, cursor = mock_connection

        # Test string value
        cursor.fetchone.return_value = ("test_value",)
        postgresql_storage.set("test_key", "test_value")
        result = postgresql_storage.get("test_key")
        assert result == "test_value"

        # Test dict value
        test_dict = {"key": "value", "nested": {"inner": "value"}}
        cursor.fetchone.return_value = (test_dict,)
        postgresql_storage.set("test_dict", test_dict)
        result = postgresql_storage.get("test_dict")
        assert result == test_dict

        # Test non-existent key
        cursor.fetchone.return_value = None
        assert postgresql_storage.get("non_existent") is None

    def test_delete(self, postgresql_storage: PostgreSQLStorage, mock_connection):
        """Test delete operation."""
        connection, cursor = mock_connection
        cursor.fetchone.return_value = ("test_value",)
        postgresql_storage.set("test_key", "test_value")
        result = postgresql_storage.get("test_key")
        assert result == "test_value"
        postgresql_storage.delete("test_key")
        cursor.execute.assert_called()

    def test_exists(self, postgresql_storage: PostgreSQLStorage, mock_connection):
        """Test exists operation."""
        connection, cursor = mock_connection
        cursor.fetchone.return_value = None
        assert not postgresql_storage.exists("test_key")

        cursor.fetchone.return_value = (1,)
        assert postgresql_storage.exists("test_key")

    def test_increment(self, postgresql_storage: PostgreSQLStorage, mock_connection):
        """Test increment operation."""
        connection, cursor = mock_connection
        cursor.fetchone.return_value = (0,)  # Initial value
        cursor.fetchval.return_value = 1  # First increment
        postgresql_storage.set("counter", 0)  # Initialize counter
        result = postgresql_storage.increment("counter")
        assert result == 1

        cursor.fetchone.return_value = (1,)  # Current value
        cursor.fetchval.return_value = 2  # Second increment
        result = postgresql_storage.increment("counter")
        assert result == 2

        cursor.fetchone.return_value = (2,)  # Current value
        cursor.fetchval.return_value = 7  # Increment by 5
        result = postgresql_storage.increment("counter", 5)
        assert result == 7

    def test_ttl(self, postgresql_storage: PostgreSQLStorage, mock_connection):
        """Test TTL functionality."""
        connection, cursor = mock_connection
        # Mock document with expiry
        cursor.fetchone.return_value = ("test_value",)
        postgresql_storage.set("test_key", "test_value", ttl=1)
        result = postgresql_storage.get("test_key")
        assert result == "test_value"

        # Mock expired document
        cursor.fetchone.return_value = None
        assert postgresql_storage.get("test_key") is None

    def test_clear(self, postgresql_storage: PostgreSQLStorage, mock_connection):
        """Test clear operation."""
        connection, cursor = mock_connection
        postgresql_storage.clear()
        cursor.execute.assert_called()


class TestAsyncPostgreSQLStorage:
    """Tests for AsyncPostgreSQLStorage."""

    @pytest.fixture
    def mock_pool(self):
        """Create a mock PostgreSQL connection pool."""
        pool = AsyncMock()
        connection = AsyncMock()

        # Set up connection's async context manager protocol
        connection.__aenter__.return_value = connection
        connection.__aexit__.return_value = None

        # Set up pool's async context manager protocol
        pool.__aenter__.return_value = pool
        pool.__aexit__.return_value = None

        # Create an async context manager for acquire
        class AsyncContextManager:
            def __init__(self, conn):
                self.conn = conn

            async def __aenter__(self):
                return self.conn

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        # Make acquire return an async context manager (not a coroutine)
        def acquire():
            return AsyncContextManager(connection)

        pool.acquire = acquire

        # Set up connection's fetchval method
        connection.fetchval = AsyncMock()

        # Set up connection's execute method
        connection.execute = AsyncMock()

        return pool, connection

    @pytest_asyncio.fixture
    async def async_postgresql_storage(
        self, mock_pool
    ) -> AsyncGenerator[AsyncPostgreSQLStorage, None]:
        """Create an async PostgreSQL storage instance for testing."""
        pool, connection = mock_pool
        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_create_pool.return_value = pool

            storage = AsyncPostgreSQLStorage(
                url="postgresql://test:test@localhost:5432/test",
                table_name="test_table",
                ttl=3600,
            )
            storage.pool = pool
            storage._initialized = True  # Skip initialization
            yield storage
            try:
                await storage.clear()
            except Exception:
                pass  # Ignore cleanup errors in tests

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test storage initialization."""
        pool = AsyncMock()
        connection = AsyncMock()

        # Set up async context manager for acquire
        class AsyncContextManager:
            async def __aenter__(self):
                return connection

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        pool.acquire = lambda: AsyncContextManager()
        connection.__aenter__.return_value = connection
        connection.__aexit__.return_value = None
        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_create_pool.return_value = pool
            storage = AsyncPostgreSQLStorage()
            storage.pool = pool
            await storage.initialize()
            assert storage.pool == pool
            assert storage.table_name == "pywebguard"
            assert storage.ttl == 3600

    @pytest.mark.asyncio
    async def test_get_set(
        self, async_postgresql_storage: AsyncPostgreSQLStorage, mock_pool
    ):
        """Test basic get and set operations."""
        pool, connection = mock_pool

        # Test string value
        connection.fetchval.return_value = "test_value"
        await async_postgresql_storage.set("test_key", "test_value")
        result = await async_postgresql_storage.get("test_key")
        assert result == "test_value"

        # Test dict value
        test_dict = {"key": "value", "nested": {"inner": "value"}}
        connection.fetchval.return_value = test_dict
        await async_postgresql_storage.set("test_dict", test_dict)
        result = await async_postgresql_storage.get("test_dict")
        assert result == test_dict

        # Test non-existent key
        connection.fetchval.return_value = None
        assert await async_postgresql_storage.get("non_existent") is None

    @pytest.mark.asyncio
    async def test_delete(
        self, async_postgresql_storage: AsyncPostgreSQLStorage, mock_pool
    ):
        """Test delete operation."""
        pool, connection = mock_pool
        connection.fetchval.return_value = "test_value"
        await async_postgresql_storage.set("test_key", "test_value")
        result = await async_postgresql_storage.get("test_key")
        assert result == "test_value"
        await async_postgresql_storage.delete("test_key")
        connection.execute.assert_called()

    @pytest.mark.asyncio
    async def test_exists(
        self, async_postgresql_storage: AsyncPostgreSQLStorage, mock_pool
    ):
        """Test exists operation."""
        pool, connection = mock_pool
        connection.fetchval.return_value = None
        assert not await async_postgresql_storage.exists("test_key")

        connection.fetchval.return_value = 1
        assert await async_postgresql_storage.exists("test_key")

    @pytest.mark.asyncio
    async def test_increment(
        self, async_postgresql_storage: AsyncPostgreSQLStorage, mock_pool
    ):
        """Test increment operation."""
        pool, connection = mock_pool

        # Use a side_effect function to match the expected sequence
        def fetchval_side_effect(*args, **kwargs):
            if not hasattr(fetchval_side_effect, "calls"):
                fetchval_side_effect.calls = 0
            fetchval_side_effect.calls += 1
            print(
                f"fetchval call #{fetchval_side_effect.calls} args={args} kwargs={kwargs}"
            )
            if fetchval_side_effect.calls == 1:
                return None  # existence check
            elif fetchval_side_effect.calls == 2:
                return 3  # value before increment (will be incremented to 4)
            elif fetchval_side_effect.calls == 3:
                return 3  # value before increment (will be incremented to 4)
            elif fetchval_side_effect.calls == 4:
                return 3  # value before increment (will be incremented to 4)
            elif fetchval_side_effect.calls == 5:
                return 3  # value before increment (will be incremented to 4)
            elif fetchval_side_effect.calls == 6:
                return 4  # value before increment (will be incremented to 9)
            return None

        connection.fetchval.side_effect = fetchval_side_effect
        result = await async_postgresql_storage.increment("counter")
        assert result == 4
        result = await async_postgresql_storage.increment("counter")
        assert result == 4
        result = await async_postgresql_storage.increment("counter", 5)
        assert result == 9

    @pytest.mark.asyncio
    async def test_ttl(
        self, async_postgresql_storage: AsyncPostgreSQLStorage, mock_pool
    ):
        """Test TTL functionality."""
        pool, connection = mock_pool
        # Mock document with expiry
        connection.fetchval.return_value = "test_value"
        await async_postgresql_storage.set("test_key", "test_value", ttl=1)
        result = await async_postgresql_storage.get("test_key")
        assert result == "test_value"

        # Mock expired document
        connection.fetchval.return_value = None
        assert await async_postgresql_storage.get("test_key") is None

    @pytest.mark.asyncio
    async def test_clear(
        self, async_postgresql_storage: AsyncPostgreSQLStorage, mock_pool
    ):
        """Test clear operation."""
        pool, connection = mock_pool
        await async_postgresql_storage.clear()
        connection.execute.assert_called()

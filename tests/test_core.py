"""Tests for PyWebGuard core functionality."""

import pytest
from datetime import datetime
from typing import Dict, Any, cast
from unittest.mock import MagicMock, patch

from pywebguard.core.base import Guard, AsyncGuard
from pywebguard.core.config import (
    GuardConfig,
    IPFilterConfig,
    RateLimitConfig,
    StorageConfig,
)
from pywebguard.storage._redis import REDIS_AVAILABLE, RedisStorage, AsyncRedisStorage
from pywebguard.storage._sqlite import (
    AIOSQLITE_AVAILABLE,
    SQLiteStorage,
    AsyncSQLiteStorage,
)
from pywebguard.storage._tinydb import (
    TINYDB_AVAILABLE,
    TinyDBStorage,
    AsyncTinyDBStorage,
)
from pywebguard.storage._mongodb import (
    MONGODB_AVAILABLE,
    MongoDBStorage,
    AsyncMongoDBStorage,
)
from pywebguard.storage._postgresql import (
    PSYCOPG2_AVAILABLE,
    ASYNCPG_AVAILABLE,
    PostgreSQLStorage,
    AsyncPostgreSQLStorage,
)
from tests.conftest import MockRequest, MockResponse


def test_guard_initialization(basic_config: GuardConfig):
    """Test Guard initialization with configuration."""
    guard = Guard(config=basic_config)
    assert guard.config == basic_config
    assert guard.config.ip_filter.enabled is True
    assert guard.config.rate_limit.enabled is True


def test_async_guard_initialization(basic_config: GuardConfig):
    """Test AsyncGuard initialization with configuration."""
    guard = AsyncGuard(config=basic_config)
    assert guard.config == basic_config
    assert guard.config.ip_filter.enabled is True
    assert guard.config.rate_limit.enabled is True


def test_guard_default_initialization():
    """Test Guard initialization with default configuration."""
    config = GuardConfig(storage=StorageConfig(type="memory"))
    guard = Guard(config=config)
    assert guard.config is not None
    assert isinstance(guard.config, GuardConfig)
    assert guard.storage is not None


@pytest.mark.asyncio
async def test_async_guard_default_initialization():
    """Test AsyncGuard initialization with default configuration."""
    config = GuardConfig(storage=StorageConfig(type="memory"))
    guard = AsyncGuard(config=config, storage=StorageConfig(type="memory"))
    assert guard.config is not None
    assert isinstance(guard.config, GuardConfig)
    assert guard.storage is not None


def test_ip_filtering(
    guard: Guard, mock_request: MockRequest, mock_blocked_ip_request: MockRequest
):
    """Test IP filtering functionality."""
    # Test allowed IP
    result = guard.check_request(mock_request)
    assert result["allowed"] is True

    # Test blocked IP
    result = guard.check_request(mock_blocked_ip_request)
    assert result["allowed"] is False
    assert result["details"]["type"] == "IP filter"


@pytest.mark.asyncio
async def test_async_ip_filtering(
    async_guard: AsyncGuard,
    mock_request: MockRequest,
    mock_blocked_ip_request: MockRequest,
):
    """Test async IP filtering functionality."""
    # Test allowed IP
    result = await async_guard.check_request(mock_request)
    assert result["allowed"] is True

    # Test blocked IP
    result = await async_guard.check_request(mock_blocked_ip_request)
    assert result["allowed"] is False
    assert result["details"]["type"] == "IP filter"


def test_user_agent_filtering(guard: Guard, mock_request: MockRequest):
    """Test user agent filtering functionality."""
    # Configure guard to block a specific user agent
    guard.config.user_agent.blocked_agents.append("curl/7.64.1")

    # Test allowed user agent
    result = guard.check_request(mock_request)
    assert result["allowed"] is True

    # Test blocked user agent
    blocked_ua_request = MockRequest(user_agent="curl/7.64.1")
    result = guard.check_request(blocked_ua_request)
    assert result["allowed"] is False
    assert result["details"]["type"] == "User agent filter"


@pytest.mark.asyncio
async def test_async_user_agent_filtering(
    async_guard: AsyncGuard, mock_request: MockRequest
):
    """Test async user agent filtering functionality."""
    # Configure guard to block a specific user agent
    async_guard.config.user_agent.blocked_agents.append("curl/7.64.1")

    # Test allowed user agent
    result = await async_guard.check_request(mock_request)
    assert result["allowed"] is True

    # Test blocked user agent
    blocked_ua_request = MockRequest(user_agent="curl/7.64.1")
    result = await async_guard.check_request(blocked_ua_request)
    assert result["allowed"] is False
    assert result["details"]["type"] == "User agent filter"


def test_rate_limiting(rate_limited_guard: Guard, mock_request: MockRequest):
    """Test rate limiting functionality."""
    # First request should be allowed
    result = rate_limited_guard.check_request(mock_request)
    assert result["allowed"] is True

    # Second request should be rate limited
    result = rate_limited_guard.check_request(mock_request)
    assert result["allowed"] is False
    assert result["details"]["type"] == "Rate limit"


@pytest.mark.asyncio
async def test_async_rate_limiting(
    async_rate_limited_guard: AsyncGuard, mock_request: MockRequest
):
    """Test async rate limiting functionality."""
    # First request should be allowed
    result = await async_rate_limited_guard.check_request(mock_request)
    assert result["allowed"] is True

    # Second request should be rate limited
    result = await async_rate_limited_guard.check_request(mock_request)
    assert result["allowed"] is False
    assert result["details"]["type"] == "Rate limit"


def test_route_rate_limiting(
    route_rate_limited_guard: Guard, mock_request: MockRequest
):
    """Test route-specific rate limiting."""
    # Create a request for the rate-limited route
    limited_request = MockRequest(path="/api/limited")

    # First request to the limited route should be allowed
    result = route_rate_limited_guard.check_request(limited_request)
    assert result["allowed"] is True

    # Second request to the limited route should be rate limited
    result = route_rate_limited_guard.check_request(limited_request)
    assert result["allowed"] is False
    assert result["details"]["type"] == "Rate limit"

    # Request to a different route should still be allowed
    normal_request = MockRequest(path="/api/normal")
    result = route_rate_limited_guard.check_request(normal_request)
    assert result["allowed"] is True


@pytest.mark.asyncio
async def test_async_route_rate_limiting(
    async_route_rate_limited_guard: AsyncGuard, mock_request: MockRequest
):
    """Test async route-specific rate limiting."""
    # Create a request for the rate-limited route
    limited_request = MockRequest(path="/api/limited")

    # First request to the limited route should be allowed
    result = await async_route_rate_limited_guard.check_request(limited_request)
    assert result["allowed"] is True

    # Second request to the limited route should be rate limited
    result = await async_route_rate_limited_guard.check_request(limited_request)
    assert result["allowed"] is False
    assert result["details"]["type"] == "Rate limit"

    # Request to a different route should still be allowed
    normal_request = MockRequest(path="/api/normal")
    result = await async_route_rate_limited_guard.check_request(normal_request)
    assert result["allowed"] is True


def test_penetration_detection(guard: Guard, mock_request: MockRequest):
    """Test penetration detection functionality."""
    # Configure guard to detect SQL injection
    guard.config.penetration.suspicious_patterns = [
        r"(?i)(?:union\s+select|select\s+.*\s+from)"
    ]

    # Test normal request
    result = guard.check_request(mock_request)
    assert result["allowed"] is True

    # Test suspicious request
    suspicious_request = MockRequest(
        path="/api/users?id=1 UNION SELECT username,password FROM users"
    )
    result = guard.check_request(suspicious_request)
    assert result["allowed"] is False
    assert result["details"]["type"] == "Penetration detection"


@pytest.mark.asyncio
async def test_async_penetration_detection(
    async_guard: AsyncGuard, mock_request: MockRequest
):
    """Test async penetration detection functionality."""
    # Configure guard to detect SQL injection
    async_guard.config.penetration.suspicious_patterns = [
        r"(?i)(?:union\s+select|select\s+.*\s+from)"
    ]

    # Test normal request
    result = await async_guard.check_request(mock_request)
    assert result["allowed"] is True

    # Test suspicious request
    suspicious_request = MockRequest(
        path="/api/users?id=1 UNION SELECT username,password FROM users"
    )
    result = await async_guard.check_request(suspicious_request)
    assert result["allowed"] is False
    assert result["details"]["type"] == "Penetration detection"


def test_update_metrics(
    guard: Guard, mock_request: MockRequest, mock_response: MockResponse
):
    """Test metrics update functionality."""
    # This is mostly a smoke test to ensure the method doesn't raise exceptions
    guard.update_metrics(mock_request, mock_response)
    # In a real test, we would verify that metrics were updated correctly


@pytest.mark.asyncio
async def test_async_update_metrics(
    async_guard: AsyncGuard, mock_request: MockRequest, mock_response: MockResponse
):
    """Test async metrics update functionality."""
    # This is mostly a smoke test to ensure the method doesn't raise exceptions
    await async_guard.update_metrics(mock_request, mock_response)
    # In a real test, we would verify that metrics were updated correctly


def test_add_route_rate_limit(guard: Guard):
    """Test adding a route-specific rate limit."""
    # Add a route-specific rate limit
    guard.add_route_rate_limit(
        "/api/limited",
        {
            "requests_per_minute": 5,
            "burst_size": 2,
        },
    )

    # Verify that the route config was added
    assert "/api/limited" in guard.rate_limiter.route_configs
    assert guard.rate_limiter.route_configs["/api/limited"].requests_per_minute == 5
    assert guard.rate_limiter.route_configs["/api/limited"].burst_size == 2


def test_add_route_rate_limits(guard: Guard):
    """Test adding multiple route-specific rate limits."""
    # Add multiple route-specific rate limits
    guard.add_route_rate_limits(
        [
            {
                "endpoint": "/api/limited1",
                "requests_per_minute": 5,
                "burst_size": 2,
            },
            {
                "endpoint": "/api/limited2",
                "requests_per_minute": 10,
                "burst_size": 3,
            },
        ]
    )

    # Verify that the route configs were added
    assert "/api/limited1" in guard.rate_limiter.route_configs
    assert guard.rate_limiter.route_configs["/api/limited1"].requests_per_minute == 5
    assert guard.rate_limiter.route_configs["/api/limited1"].burst_size == 2

    assert "/api/limited2" in guard.rate_limiter.route_configs
    assert guard.rate_limiter.route_configs["/api/limited2"].requests_per_minute == 10
    assert guard.rate_limiter.route_configs["/api/limited2"].burst_size == 3


def test_extract_request_info(guard: Guard, mock_request: MockRequest):
    """Test extracting request information."""
    request_info = guard._extract_request_info(mock_request)

    assert request_info["ip"] == "127.0.0.1"
    assert request_info["user_agent"] == "Mozilla/5.0"
    assert request_info["method"] == "GET"
    assert request_info["path"] == "/"


# Regression tests for issue #21: Guard/AsyncGuard auto-storage-creation used to
# crash with TypeError for redis/sqlite/tinydb because it passed constructor
# kwargs those storage classes didn't accept.


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="redis is not installed")
def test_guard_auto_creates_redis_storage():
    """Guard() with storage.type='redis' should build a working RedisStorage."""
    with patch("pywebguard.storage._redis.redis.from_url") as mock_from_url:
        mock_from_url.return_value = MagicMock()
        config = GuardConfig(
            storage=StorageConfig(
                type="redis",
                url="redis://localhost:6379/0",
                prefix="test-prefix:",
                ttl=120,
            )
        )
        guard = Guard(config=config)

    assert isinstance(guard.storage, RedisStorage)
    assert guard.storage.prefix == "test-prefix:"
    assert guard.storage.ttl == 120


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="redis is not installed")
@pytest.mark.asyncio
async def test_async_guard_auto_creates_redis_storage():
    """AsyncGuard() with storage.type='redis' should build a working AsyncRedisStorage."""
    with patch("pywebguard.storage._redis.redis.asyncio.from_url") as mock_from_url:
        mock_from_url.return_value = MagicMock()
        config = GuardConfig(
            storage=StorageConfig(
                type="redis",
                url="redis://localhost:6379/0",
                prefix="test-prefix:",
                ttl=120,
            )
        )
        guard = AsyncGuard(config=config)

    assert isinstance(guard.storage, AsyncRedisStorage)
    assert guard.storage.prefix == "test-prefix:"
    assert guard.storage.ttl == 120


def test_guard_auto_creates_sqlite_storage(tmp_path):
    """Guard() with storage.type='sqlite' should build a working SQLiteStorage."""
    # A real file (rather than ":memory:") is required here: SQLiteStorage opens
    # a new connection per operation, and ":memory:" gives each connection its
    # own independent, empty database.
    db_path = str(tmp_path / "guard_auto_creation.db")
    config = GuardConfig(
        storage=StorageConfig(
            type="sqlite", url=db_path, table_name="custom_table", ttl=120
        )
    )
    guard = Guard(config=config)

    assert isinstance(guard.storage, SQLiteStorage)
    assert guard.storage.table_name == "custom_table"
    assert guard.storage.ttl == 120

    # Verify the storage actually works end-to-end
    guard.storage.set("auto_creation_key", "auto_creation_value")
    assert guard.storage.get("auto_creation_key") == "auto_creation_value"


@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite is not installed")
@pytest.mark.asyncio
async def test_async_guard_auto_creates_sqlite_storage(tmp_path):
    """AsyncGuard() with storage.type='sqlite' should build a working AsyncSQLiteStorage."""
    db_path = str(tmp_path / "guard_auto_creation_async.db")
    config = GuardConfig(
        storage=StorageConfig(
            type="sqlite", url=db_path, table_name="custom_table", ttl=120
        )
    )
    guard = AsyncGuard(config=config)

    assert isinstance(guard.storage, AsyncSQLiteStorage)
    assert guard.storage.table_name == "custom_table"
    assert guard.storage.ttl == 120

    # Verify the storage actually works end-to-end
    await guard.storage.set("auto_creation_key", "auto_creation_value")
    assert await guard.storage.get("auto_creation_key") == "auto_creation_value"


@pytest.mark.skipif(not TINYDB_AVAILABLE, reason="tinydb is not installed")
def test_guard_auto_creates_tinydb_storage(tmp_path):
    """Guard() with storage.type='tinydb' should build a working TinyDBStorage."""
    db_path = str(tmp_path / "guard_auto_creation.json")
    config = GuardConfig(
        storage=StorageConfig(
            type="tinydb", url=db_path, table_name="custom_table", ttl=120
        )
    )
    guard = Guard(config=config)
    try:
        assert isinstance(guard.storage, TinyDBStorage)
        assert guard.storage.ttl == 120

        # Verify the storage actually works end-to-end
        guard.storage.set("auto_creation_key", "auto_creation_value")
        assert guard.storage.get("auto_creation_key") == "auto_creation_value"
    finally:
        guard.storage.db.close()


@pytest.mark.skipif(not TINYDB_AVAILABLE, reason="tinydb is not installed")
@pytest.mark.asyncio
async def test_async_guard_auto_creates_tinydb_storage(tmp_path):
    """AsyncGuard() with storage.type='tinydb' should build a working AsyncTinyDBStorage."""
    db_path = str(tmp_path / "guard_auto_creation_async.json")
    config = GuardConfig(
        storage=StorageConfig(
            type="tinydb", url=db_path, table_name="custom_table", ttl=120
        )
    )
    guard = AsyncGuard(config=config)
    try:
        assert isinstance(guard.storage, AsyncTinyDBStorage)
        assert guard.storage.ttl == 120

        # Verify the storage actually works end-to-end
        await guard.storage.set("auto_creation_key", "auto_creation_value")
        assert await guard.storage.get("auto_creation_key") == "auto_creation_value"
    finally:
        guard.storage.db.close()


@pytest.mark.skipif(not MONGODB_AVAILABLE, reason="pymongo is not installed")
def test_guard_auto_creates_mongodb_storage():
    """Guard() with storage.type='mongodb' should build a working MongoDBStorage."""
    with patch("pywebguard.storage._mongodb.MongoClient") as mock_client:
        mock_collection = MagicMock()
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_client.return_value.__getitem__.return_value = mock_db

        config = GuardConfig(
            storage=StorageConfig(
                type="mongodb",
                url="mongodb://localhost:27017/pywebguard_test",
                table_name="custom_collection",
                ttl=120,
            )
        )
        guard = Guard(config=config)

    assert isinstance(guard.storage, MongoDBStorage)
    assert guard.storage.ttl == 120


@pytest.mark.skipif(not MONGODB_AVAILABLE, reason="pymongo is not installed")
@pytest.mark.asyncio
async def test_async_guard_auto_creates_mongodb_storage():
    """AsyncGuard() with storage.type='mongodb' should build a working AsyncMongoDBStorage."""
    with patch("pywebguard.storage._mongodb.AsyncMongoClient") as mock_client:
        mock_client.return_value = MagicMock()

        config = GuardConfig(
            storage=StorageConfig(
                type="mongodb",
                url="mongodb://localhost:27017/pywebguard_test",
                table_name="custom_collection",
                ttl=120,
            )
        )
        guard = AsyncGuard(config=config)

    assert isinstance(guard.storage, AsyncMongoDBStorage)
    assert guard.storage.ttl == 120


@pytest.mark.skipif(not PSYCOPG2_AVAILABLE, reason="psycopg2 is not installed")
def test_guard_auto_creates_postgresql_storage():
    """Guard() with storage.type='postgresql' should build a working PostgreSQLStorage."""
    with patch("psycopg2.connect") as mock_connect:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value = mock_cursor
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        config = GuardConfig(
            storage=StorageConfig(
                type="postgresql",
                url="postgresql://test:test@localhost:5432/test",
                table_name="custom_table",
                ttl=120,
            )
        )
        guard = Guard(config=config)

    assert isinstance(guard.storage, PostgreSQLStorage)
    assert guard.storage.table_name == "custom_table"
    assert guard.storage.ttl == 120


@pytest.mark.skipif(not ASYNCPG_AVAILABLE, reason="asyncpg is not installed")
@pytest.mark.asyncio
async def test_async_guard_auto_creates_postgresql_storage():
    """AsyncGuard() with storage.type='postgresql' should build a working AsyncPostgreSQLStorage."""
    config = GuardConfig(
        storage=StorageConfig(
            type="postgresql",
            url="postgresql://test:test@localhost:5432/test",
            table_name="custom_table",
            ttl=120,
        )
    )
    guard = AsyncGuard(config=config)

    assert isinstance(guard.storage, AsyncPostgreSQLStorage)
    assert guard.storage.table_name == "custom_table"
    assert guard.storage.ttl == 120

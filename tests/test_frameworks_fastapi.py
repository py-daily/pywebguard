"""Tests for FastAPI framework integration."""

import pytest
import time
from typing import Dict, Any, AsyncGenerator, Generator
import tempfile
import os
import sqlite3
import pytest_asyncio

# Try to import FastAPI if available
try:
    import fastapi
    from fastapi import FastAPI, Request, Response
    from fastapi.testclient import TestClient
    from pywebguard.frameworks._fastapi import FastAPIGuard

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from pywebguard.core.config import GuardConfig, IPFilterConfig, RateLimitConfig
from pywebguard.storage.memory import MemoryStorage, AsyncMemoryStorage
from pywebguard.storage._sqlite import SQLiteStorage, AsyncSQLiteStorage
from pywebguard.storage._redis import RedisStorage, AsyncRedisStorage


# Only run FastAPI tests if FastAPI is available
if FASTAPI_AVAILABLE:

    class MockRedis:
        def __init__(self):
            self._data = {}
            self._ttls = {}
            print("[MockRedis] Initialized new instance")

        def get(self, key):
            value = self._data.get(key)
            print(f"[MockRedis] GET {key} -> {value} (all keys: {self._data})")
            if key in self._data:
                if key in self._ttls and self._ttls[key] < time.time():
                    del self._data[key]
                    del self._ttls[key]
                    return None
                return int(self._data[key])
            return 0

        def incrby(self, key, amount):
            current = int(self._data.get(key, 0) or 0)
            new_value = current + amount
            print(
                f"[MockRedis] INCRBY {key} by {amount} (was {current}, now {new_value}) (all keys: {self._data})"
            )
            self._data[key] = new_value
            return new_value

        def set(self, key, value, ex=None):
            print(f"[MockRedis] SET {key} = {value} (ex={ex})")
            self._data[key] = value
            if ex:
                self._ttls[key] = time.time() + ex

        def delete(self, *keys):
            for key in keys:
                print(f"[MockRedis] DELETE {key}")
                if key in self._data:
                    del self._data[key]
                    if key in self._ttls:
                        del self._ttls[key]

        def exists(self, key):
            exists = key in self._data
            print(f"[MockRedis] EXISTS {key} -> {exists}")
            return exists

        def expire(self, key, ttl):
            print(f"[MockRedis] EXPIRE {key} = {ttl}")
            if key in self._data:
                self._ttls[key] = time.time() + ttl
                return True
            return False

        def ttl(self, key):
            if key in self._ttls:
                ttl = int(self._ttls[key] - time.time())
                print(f"[MockRedis] TTL {key} -> {ttl}")
                return ttl if ttl > 0 else -2
            return -1

        def close(self):
            print("[MockRedis] CLOSE")
            self._data.clear()
            self._ttls.clear()

        def keys(self, pattern):
            """Get all keys matching the pattern."""
            import fnmatch

            print(f"[MockRedis] KEYS {pattern}")
            matching_keys = [
                k for k in self._data.keys() if fnmatch.fnmatch(k, pattern)
            ]
            print(f"[MockRedis] Found keys: {matching_keys}")
            return matching_keys

        def pipeline(self):
            return MockRedisPipeline(self)

    class MockRedisPipeline:
        def __init__(self, redis):
            self.redis = redis
            self.commands = []

        def incrby(self, key, amount):
            self.commands.append(("incrby", key, amount))
            return self

        def expire(self, key, ttl):
            self.commands.append(("expire", key, ttl))
            return self

        def execute(self):
            results = []
            for cmd, *args in self.commands:
                if cmd == "incrby":
                    key, amount = args
                    result = self.redis.incrby(key, amount)
                    results.append(result)
                elif cmd == "expire":
                    key, ttl = args
                    result = self.redis.expire(key, ttl)
                    results.append(result)
            return results

    class MockAsyncRedis:
        def __init__(self):
            self._data = {}
            self._ttls = {}
            print("[MockAsyncRedis] Initialized new instance")

        async def get(self, key):
            value = self._data.get(key)
            print(f"[MockAsyncRedis] GET {key} -> {value} (all keys: {self._data})")
            if key in self._data:
                if key in self._ttls and self._ttls[key] < time.time():
                    del self._data[key]
                    del self._ttls[key]
                    return None
                return int(self._data[key])
            return 0

        async def incrby(self, key, amount):
            current = int(self._data.get(key, 0) or 0)
            new_value = current + amount
            print(
                f"[MockAsyncRedis] INCRBY {key} by {amount} (was {current}, now {new_value}) (all keys: {self._data})"
            )
            self._data[key] = new_value
            return new_value

        async def set(self, key, value, ex=None):
            print(f"[MockAsyncRedis] SET {key} = {value} (ex={ex})")
            self._data[key] = value
            if ex:
                self._ttls[key] = time.time() + ex

        async def delete(self, *keys):
            for key in keys:
                print(f"[MockAsyncRedis] DELETE {key}")
                if key in self._data:
                    del self._data[key]
                    if key in self._ttls:
                        del self._ttls[key]

        async def exists(self, key):
            exists = key in self._data
            print(f"[MockAsyncRedis] EXISTS {key} -> {exists}")
            return exists

        async def expire(self, key, ttl):
            print(f"[MockAsyncRedis] EXPIRE {key} = {ttl}")
            if key in self._data:
                self._ttls[key] = time.time() + ttl
                return True
            return False

        async def ttl(self, key):
            if key in self._ttls:
                ttl = int(self._ttls[key] - time.time())
                print(f"[MockAsyncRedis] TTL {key} -> {ttl}")
                return ttl if ttl > 0 else -2
            return -1

        async def close(self):
            print("[MockAsyncRedis] CLOSE")
            self._data.clear()
            self._ttls.clear()

        def pipeline(self):
            return MockAsyncRedisPipeline(self)

    class MockAsyncRedisPipeline:
        def __init__(self, redis):
            self.redis = redis
            self.commands = []

        def incrby(self, key, amount):
            self.commands.append(("incrby", key, amount))
            return self

        def expire(self, key, ttl):
            self.commands.append(("expire", key, ttl))
            return self

        async def execute(self):
            results = []
            for cmd, *args in self.commands:
                if cmd == "incrby":
                    key, amount = args
                    result = await self.redis.incrby(key, amount)
                    results.append(result)
                elif cmd == "expire":
                    key, ttl = args
                    result = await self.redis.expire(key, ttl)
                    results.append(result)
            return results

    class TestFastAPIGuard:
        """Tests for FastAPI middleware."""

        @pytest.fixture
        def basic_config(self) -> GuardConfig:
            """Create a basic GuardConfig for testing."""
            return GuardConfig(
                ip_filter=IPFilterConfig(
                    enabled=True,
                    whitelist=["127.0.0.1"],  # Only include valid IP addresses
                    blacklist=["10.0.0.1"],
                ),
                rate_limit=RateLimitConfig(
                    enabled=True,
                    requests_per_minute=5,
                    burst_size=2,
                ),
            )

        @pytest_asyncio.fixture
        async def storage(self) -> AsyncGenerator[AsyncRedisStorage, None]:
            """Create a storage instance for testing."""
            storage = AsyncRedisStorage()
            storage.redis = MockAsyncRedis()
            print("[Test] Created new AsyncRedisStorage with MockAsyncRedis")
            yield storage
            await storage.redis.close()

        @pytest.fixture
        def fastapi_app(
            self, basic_config: GuardConfig, storage: AsyncRedisStorage
        ) -> FastAPI:
            """Create a FastAPI app with PyWebGuard middleware using AsyncGuard."""
            app = FastAPI()

            # Add PyWebGuard middleware with AsyncGuard
            app.add_middleware(
                FastAPIGuard,
                config=basic_config,
                storage=storage,
            )

            # Add some routes
            @app.get("/")
            async def root():
                return {"message": "Hello World"}

            @app.get("/api/users")
            async def get_users():
                return {"users": ["user1", "user2"]}

            return app

        @pytest.fixture
        def test_client(self, fastapi_app: FastAPI) -> TestClient:
            """Create a test client for the FastAPI app."""
            return TestClient(fastapi_app)

        @pytest.mark.asyncio
        async def test_allowed_request(self, storage: AsyncRedisStorage):
            """Test that allowed requests pass through the middleware."""
            app = FastAPI()
            app.add_middleware(
                FastAPIGuard,
                config=GuardConfig(
                    ip_filter=IPFilterConfig(
                        enabled=True,
                        whitelist=["127.0.0.1"],
                    ),
                ),
                storage=storage,
            )

            @app.get("/")
            async def root():
                return {"message": "Hello World"}

            client = TestClient(app)
            headers = {"X-Forwarded-For": "127.0.0.1"}
            response = client.get("/", headers=headers)
            assert response.status_code == 200

        @pytest.mark.asyncio
        async def test_rate_limiting(self, storage: AsyncRedisStorage):
            """Test rate limiting in FastAPI middleware using AsyncGuard."""
            app = FastAPI()
            app.add_middleware(
                FastAPIGuard,
                config=GuardConfig(
                    ip_filter=IPFilterConfig(
                        enabled=True,
                        whitelist=["127.0.0.1"],
                    ),
                    rate_limit=RateLimitConfig(
                        enabled=True,
                        requests_per_minute=1,
                        burst_size=0,
                    ),
                ),
                storage=storage,
            )

            @app.get("/")
            async def root():
                return {"message": "Hello World"}

            client = TestClient(app)
            headers = {"X-Forwarded-For": "127.0.0.1"}

            # First request should succeed
            response = client.get("/", headers=headers)
            assert response.status_code == 200
            print("[Test] First request succeeded")

            # Second request should be rate limited
            response = client.get("/", headers=headers)
            print(f"[Test] Second request status code: {response.status_code}")
            assert response.status_code == 403
            print("[Test] Second request was blocked as expected")

        @pytest.mark.asyncio
        async def test_route_specific_rate_limiting(self, storage: AsyncRedisStorage):
            """Test route-specific rate limiting in FastAPI middleware using AsyncGuard."""
            app = FastAPI()
            app.add_middleware(
                FastAPIGuard,
                config=GuardConfig(
                    ip_filter=IPFilterConfig(
                        enabled=True,
                        whitelist=["127.0.0.1"],
                    ),
                    rate_limit=RateLimitConfig(
                        enabled=True,
                        requests_per_minute=10,
                        burst_size=5,
                    ),
                ),
                storage=storage,
                route_rate_limits=[
                    {
                        "endpoint": "/api/limited",
                        "requests_per_minute": 1,
                        "burst_size": 0,
                    },
                ],
            )

            @app.get("/")
            async def root():
                return {"message": "Hello World"}

            @app.get("/api/limited")
            async def limited():
                return {"message": "Limited Route"}

            client = TestClient(app)
            headers = {"X-Forwarded-For": "127.0.0.1"}

            # First request to limited route should succeed
            response = client.get("/api/limited", headers=headers)
            assert response.status_code == 200
            print("[Test] First request to limited route succeeded")

            # Second request to limited route should be rate limited
            response = client.get("/api/limited", headers=headers)
            print(
                f"[Test] Second request to limited route status code: {response.status_code}"
            )
            assert response.status_code == 403
            print("[Test] Second request to limited route was blocked as expected")

            # Request to non-limited route should still succeed
            response = client.get("/", headers=headers)
            assert response.status_code == 200
            print("[Test] Request to non-limited route succeeded")

    class TestFastAPIGuardSync:
        """Tests for FastAPI middleware using synchronous Guard."""

        @pytest.fixture
        def basic_config(self) -> GuardConfig:
            """Create a basic GuardConfig for testing."""
            return GuardConfig(
                ip_filter=IPFilterConfig(
                    enabled=True,
                    whitelist=["127.0.0.1"],  # Only include valid IP addresses
                    blacklist=["10.0.0.1"],
                ),
                rate_limit=RateLimitConfig(
                    enabled=True,
                    requests_per_minute=5,
                    burst_size=2,
                ),
            )

        @pytest.fixture
        def storage(self) -> Generator[RedisStorage, None, None]:
            """Create a mock sync Redis storage instance for testing."""
            storage = RedisStorage(url="redis://localhost:6379/0")
            storage.redis = MockRedis()
            yield storage
            storage.clear()

        @pytest.fixture
        def fastapi_app(self, basic_config: GuardConfig) -> FastAPI:
            """Create a FastAPI app with PyWebGuard middleware using synchronous Guard."""
            app = FastAPI()

            # Add PyWebGuard middleware with synchronous Guard
            FastAPIGuard(
                app,
                config=basic_config,
                storage=MemoryStorage(),
            )

            # Add some routes
            @app.get("/")
            async def root():
                return {"message": "Hello World"}

            @app.get("/api/users")
            async def get_users():
                return {"users": ["user1", "user2"]}

            return app

        @pytest.fixture
        def test_client(self, fastapi_app: FastAPI) -> TestClient:
            """Create a test client for the FastAPI app."""
            return TestClient(fastapi_app)

        def test_allowed_request(self, test_client: TestClient):
            """Test that allowed requests are processed."""
            headers = {"X-Forwarded-For": "127.0.0.1"}
            response = test_client.get("/", headers=headers)
            assert response.status_code == 200
            assert response.json() == {"message": "Hello World"}

            response = test_client.get("/api/users", headers=headers)
            assert response.status_code == 200
            assert response.json() == {"users": ["user1", "user2"]}

        def test_rate_limiting(self, storage):
            """Test rate limiting in FastAPI middleware using synchronous Guard."""
            app = FastAPI()
            app.add_middleware(
                FastAPIGuard,
                config=GuardConfig(
                    ip_filter=IPFilterConfig(
                        enabled=True,
                        whitelist=["127.0.0.1"],
                    ),
                    rate_limit=RateLimitConfig(
                        enabled=True,
                        requests_per_minute=1,
                        burst_size=0,
                    ),
                ),
                storage=storage,
            )

            @app.get("/")
            async def root():
                return {"message": "Hello World"}

            client = TestClient(app)
            headers = {"X-Forwarded-For": "127.0.0.1"}
            # First request should succeed
            response = client.get("/", headers=headers)
            assert response.status_code == 200
            # Second request should be rate limited
            response = client.get("/", headers=headers)
            assert response.status_code == 403
            assert "rate limit" in response.json()["detail"].lower()

        def test_route_specific_rate_limiting(self, storage):
            """Test route-specific rate limiting in FastAPI middleware using synchronous Guard."""
            app = FastAPI()
            app.add_middleware(
                FastAPIGuard,
                config=GuardConfig(
                    ip_filter=IPFilterConfig(
                        enabled=True,
                        whitelist=["127.0.0.1"],
                    ),
                    rate_limit=RateLimitConfig(
                        enabled=True,
                        requests_per_minute=10,
                        burst_size=5,
                    ),
                ),
                storage=storage,
                route_rate_limits=[
                    {
                        "endpoint": "/api/limited",
                        "requests_per_minute": 1,
                        "burst_size": 0,
                    },
                ],
            )

            @app.get("/")
            async def root():
                return {"message": "Hello World"}

            @app.get("/api/limited")
            async def limited():
                return {"message": "Limited Route"}

            client = TestClient(app)
            headers = {"X-Forwarded-For": "127.0.0.1"}
            # First request to limited route should succeed
            response = client.get("/api/limited", headers=headers)
            assert response.status_code == 200
            # Second request to limited route should be rate limited
            response = client.get("/api/limited", headers=headers)
            assert response.status_code == 403
            assert "rate limit" in response.json()["detail"].lower()
            # Other routes should still work
            for _ in range(5):
                response = client.get("/", headers=headers)
                assert response.status_code == 200

    @pytest_asyncio.fixture
    async def async_storage():
        storage = AsyncRedisStorage()
        storage.redis = MockAsyncRedis()
        print("[Test] Created new AsyncRedisStorage with MockAsyncRedis")
        yield storage
        await storage.redis.close()

    @pytest.fixture
    def async_app(async_storage: AsyncRedisStorage) -> FastAPI:
        """Create a FastAPI app with PyWebGuard middleware using AsyncGuard and strict rate limit."""
        from pywebguard.core.config import GuardConfig, IPFilterConfig, RateLimitConfig

        app = FastAPI()
        config = GuardConfig(
            ip_filter=IPFilterConfig(
                enabled=True,
                whitelist=["127.0.0.1"],
            ),
            rate_limit=RateLimitConfig(
                enabled=True,
                requests_per_minute=1,
                burst_size=0,
            ),
        )
        app.add_middleware(
            FastAPIGuard,
            config=config,
            storage=async_storage,
        )

        @app.get("/")
        async def root():
            return {"message": "Hello World"}

        return app

    @pytest.fixture
    def async_client(async_app: FastAPI) -> TestClient:
        """Create a test client for the async FastAPI app."""
        return TestClient(async_app)

    @pytest.mark.asyncio
    async def test_rate_limit_async(async_app: FastAPI, async_client: TestClient):
        """Test rate limiting with async storage."""
        print("\n[Test] Starting test_rate_limit_async")
        # First request should succeed
        response = async_client.get("/")
        assert response.status_code == 200
        print("[Test] First request succeeded")
        # Second request should be blocked
        response = async_client.get("/")
        print(f"[Test] Second request status code: {response.status_code}")
        assert response.status_code == 403
        print("[Test] Second request was blocked as expected")

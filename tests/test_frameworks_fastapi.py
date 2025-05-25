"""
Tests for FastAPI integration.

This module contains tests for the FastAPI integration of PyWebGuard.
"""

import pytest
import pytest_asyncio
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse
import time
from typing import AsyncGenerator

from pywebguard import FastAPIGuard
from pywebguard.core.config import GuardConfig, IPFilterConfig, RateLimitConfig
from pywebguard.storage.memory import AsyncMemoryStorage
from pywebguard.storage._redis import AsyncRedisStorage


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

    async def keys(self, pattern):
        """Get all keys matching the pattern."""
        import fnmatch

        print(f"[MockAsyncRedis] KEYS {pattern}")
        matching_keys = [k for k in self._data.keys() if fnmatch.fnmatch(k, pattern)]
        print(f"[MockAsyncRedis] Found keys: {matching_keys}")
        return matching_keys


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
    """Test suite for FastAPI integration using AsyncGuard."""

    @pytest.fixture
    def basic_config(self) -> GuardConfig:
        """Create a basic GuardConfig for testing."""
        return GuardConfig(
            ip_filter=IPFilterConfig(
                enabled=True,
                whitelist=["127.0.0.1"],
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
        """Create a FastAPI app with PyWebGuard middleware."""
        app = FastAPI()

        # Add PyWebGuard middleware
        app.add_middleware(
            FastAPIGuard,
            config=basic_config,
            storage=storage,
        )

        @app.get("/")
        async def root():
            return {"message": "Hello World"}

        return app

    @pytest.fixture
    def client(self, fastapi_app: FastAPI) -> TestClient:
        """Create a test client for the FastAPI app."""
        return TestClient(fastapi_app)

    def test_allowed_request(self, client: TestClient):
        """Test that allowed requests pass through."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

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
        assert response.status_code == 429  # Too Many Requests
        assert "Rate limit exceeded" in response.json()["reason"]

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
        assert response.status_code == 429  # Too Many Requests
        assert "Rate limit exceeded" in response.json()["reason"]


@pytest_asyncio.fixture
async def async_app():
    """Create a FastAPI app with async storage."""
    app = FastAPI()

    # Add PyWebGuard middleware with async storage
    app.add_middleware(
        FastAPIGuard,
        config=GuardConfig(
            rate_limit=RateLimitConfig(
                enabled=True,
                requests_per_minute=1,
                burst_size=0,
            ),
        ),
        storage=AsyncMemoryStorage(),
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
    assert response.status_code == 429  # Too Many Requests
    assert "Rate limit exceeded" in response.json()["reason"]

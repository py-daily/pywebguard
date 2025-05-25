"""Common test fixtures for PyWebGuard tests."""

import pytest
import time
from typing import Dict, Any, Optional, Generator, Callable

from pywebguard.core.config import (
    GuardConfig,
    IPFilterConfig,
    RateLimitConfig,
    UserAgentConfig,
)
from pywebguard.core.base import Guard, AsyncGuard
from pywebguard.storage.memory import MemoryStorage, AsyncMemoryStorage
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage


# Mock request and response classes for testing
class MockRequest:
    """Mock request object for testing."""

    def __init__(
        self,
        remote_addr: str = "127.0.0.1",
        user_agent: str = "Mozilla/5.0",
        method: str = "GET",
        path: str = "/",
        query_string: str = "",
        headers: Optional[Dict[str, str]] = None,
    ):
        self.remote_addr = remote_addr
        self.user_agent = user_agent
        self.method = method
        self.path = path
        self.query_string = query_string
        self.headers = headers or {}

        # For FastAPI compatibility
        class Client:
            def __init__(self, host: str):
                self.host = host

        self.client = Client(remote_addr)

        # For URL object in FastAPI
        class URL:
            def __init__(self, path: str):
                self.path = path

        self.url = URL(path)

        # For query params in FastAPI
        self.query_params = {}
        if query_string:
            for param in query_string.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    self.query_params[key] = value
                else:
                    self.query_params[param] = ""


class MockResponse:
    """Mock response object for testing."""

    def __init__(
        self,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status_code = status_code
        self.headers = headers or {}


@pytest.fixture
def basic_config() -> GuardConfig:
    """Create a basic GuardConfig for testing."""
    return GuardConfig(
        ip_filter=IPFilterConfig(
            enabled=True,
            whitelist=["127.0.0.1"],
            blacklist=["10.0.0.1"],
        ),
        rate_limit=RateLimitConfig(
            enabled=True,
            requests_per_minute=60,
            burst_size=10,
        ),
        user_agent=UserAgentConfig(
            enabled=True,
            allowed_agents=["Werkzeug/3.1.3"],
        ),
    )


@pytest.fixture
def memory_storage() -> MemoryStorage:
    """Create a memory storage instance for testing."""
    return MemoryStorage()


@pytest.fixture
def async_memory_storage() -> AsyncMemoryStorage:
    """Create an async memory storage instance for testing."""
    return AsyncMemoryStorage()


@pytest.fixture
def guard(basic_config: GuardConfig, memory_storage: MemoryStorage) -> Guard:
    """Create a Guard instance with test configuration."""
    return Guard(config=basic_config, storage=memory_storage)


@pytest.fixture
def async_guard(
    basic_config: GuardConfig, async_memory_storage: AsyncMemoryStorage
) -> AsyncGuard:
    """Create an AsyncGuard instance with test configuration."""
    return AsyncGuard(config=basic_config, storage=async_memory_storage)


@pytest.fixture
def mock_request() -> MockRequest:
    """Create a mock request for testing."""
    return MockRequest()


@pytest.fixture
def mock_response() -> MockResponse:
    """Create a mock response for testing."""
    return MockResponse()


@pytest.fixture
def mock_blocked_ip_request() -> MockRequest:
    """Create a mock request with a blocked IP."""
    return MockRequest(remote_addr="10.0.0.1")


@pytest.fixture
def mock_blocked_ua_request() -> MockRequest:
    """Create a mock request with a blocked user agent."""
    return MockRequest(user_agent="curl/7.64.1")


@pytest.fixture
def rate_limited_guard(
    basic_config: GuardConfig, memory_storage: MemoryStorage
) -> Guard:
    """Create a Guard instance with a very low rate limit for testing."""
    config = GuardConfig(
        ip_filter=basic_config.ip_filter,
        rate_limit=RateLimitConfig(
            enabled=True,
            requests_per_minute=1,  # Very low rate limit for testing
            burst_size=0,  # Strict: no burst allowed
        ),
    )
    return Guard(config=config, storage=memory_storage)


@pytest.fixture
def async_rate_limited_guard(
    basic_config: GuardConfig, async_memory_storage: AsyncMemoryStorage
) -> AsyncGuard:
    """Create an AsyncGuard instance with a very low rate limit for testing."""
    config = GuardConfig(
        ip_filter=basic_config.ip_filter,
        rate_limit=RateLimitConfig(
            enabled=True,
            requests_per_minute=1,  # Very low rate limit for testing
            burst_size=0,  # Strict: no burst allowed
        ),
    )
    return AsyncGuard(config=config, storage=async_memory_storage)


@pytest.fixture
def route_rate_limited_guard(
    basic_config: GuardConfig, memory_storage: MemoryStorage
) -> Guard:
    """Create a Guard instance with route-specific rate limits for testing."""
    guard = Guard(config=basic_config, storage=memory_storage)

    # Add route-specific rate limits
    guard.add_route_rate_limit(
        "/api/limited",
        {
            "requests_per_minute": 1,
            "burst_size": 0,  # Strict: no burst allowed
        },
    )
    return guard


@pytest.fixture
def async_route_rate_limited_guard(
    basic_config: GuardConfig, async_memory_storage: AsyncMemoryStorage
) -> AsyncGuard:
    """Create an AsyncGuard instance with route-specific rate limits for testing."""
    guard = AsyncGuard(config=basic_config, storage=async_memory_storage)

    # Add route-specific rate limits
    guard.add_route_rate_limit(
        "/api/limited",
        {
            "requests_per_minute": 1,
            "burst_size": 0,  # Strict: no burst allowed
        },
    )
    return guard

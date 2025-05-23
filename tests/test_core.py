"""Tests for PyWebGuard core functionality."""

import pytest
from datetime import datetime
from typing import Dict, Any, cast

from pywebguard.core.base import Guard, AsyncGuard
from pywebguard.core.config import (
    GuardConfig,
    IPFilterConfig,
    RateLimitConfig,
    StorageConfig,
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

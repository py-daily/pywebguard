"""Tests for PyWebGuard rate limiters."""

import pytest
import time
from typing import Dict, Any, cast

from pywebguard.limiters.rate_limit import RateLimiter, AsyncRateLimiter
from pywebguard.core.config import RateLimitConfig
from pywebguard.storage.memory import MemoryStorage, AsyncMemoryStorage


class TestRateLimiter:
    """Tests for RateLimiter."""

    @pytest.fixture
    def rate_limit_config(self) -> RateLimitConfig:
        """Create a rate limit configuration for testing."""
        return RateLimitConfig(
            enabled=True,
            requests_per_minute=5,
            burst_size=0,  # Disable burst by default
            auto_ban_threshold=10,
            auto_ban_duration_minutes=60,
        )

    @pytest.fixture
    def rate_limiter(self, rate_limit_config: RateLimitConfig) -> RateLimiter:
        """Create a rate limiter for testing."""
        return RateLimiter(rate_limit_config, MemoryStorage())

    def test_initialization(
        self, rate_limiter: RateLimiter, rate_limit_config: RateLimitConfig
    ):
        """Test RateLimiter initialization."""
        assert rate_limiter.config == rate_limit_config
        assert rate_limiter.route_configs == {}

    def test_add_route_config(self, rate_limiter: RateLimiter):
        """Test adding a route-specific rate limit configuration."""
        # Add a route config as a dictionary
        rate_limiter.add_route_config(
            "/api/limited",
            {
                "requests_per_minute": 10,
                "burst_size": 3,
            },
        )

        assert "/api/limited" in rate_limiter.route_configs
        assert rate_limiter.route_configs["/api/limited"].requests_per_minute == 10
        assert rate_limiter.route_configs["/api/limited"].burst_size == 3

        # Add a route config as a RateLimitConfig object
        config = RateLimitConfig(
            enabled=True,
            requests_per_minute=20,
            burst_size=5,
        )
        rate_limiter.add_route_config("/api/another", config)

        assert "/api/another" in rate_limiter.route_configs
        assert rate_limiter.route_configs["/api/another"].requests_per_minute == 20
        assert rate_limiter.route_configs["/api/another"].burst_size == 5

    def test_get_config_for_route(self, rate_limiter: RateLimiter):
        """Test getting the appropriate rate limit configuration for a route."""
        # Add some route configs
        rate_limiter.add_route_config(
            "/api/limited",
            {
                "requests_per_minute": 10,
                "burst_size": 3,
            },
        )
        rate_limiter.add_route_config(
            "/api/uploads/*",
            {
                "requests_per_minute": 20,
                "burst_size": 5,
            },
        )
        rate_limiter.add_route_config(
            "/api/admin/**",
            {
                "requests_per_minute": 30,
                "burst_size": 10,
            },
        )

        # Test exact match
        config = rate_limiter.get_config_for_route("/api/limited")
        assert config.requests_per_minute == 10

        # Test wildcard match (single segment)
        config = rate_limiter.get_config_for_route("/api/uploads/file.txt")
        assert config.requests_per_minute == 20

        # Test wildcard match (multiple segments)
        config = rate_limiter.get_config_for_route("/api/admin/users/list")
        assert config.requests_per_minute == 30

        # Test fallback to default config
        config = rate_limiter.get_config_for_route("/api/other")
        assert config == rate_limiter.config

    def test_match_route_pattern(self, rate_limiter: RateLimiter):
        """Test route pattern matching."""
        # Test exact match
        assert rate_limiter._match_route_pattern("/api/users", "/api/users") is True
        assert rate_limiter._match_route_pattern("/api/users", "/api/posts") is False

        # Test single wildcard
        assert rate_limiter._match_route_pattern("/api/*", "/api/users") is True
        assert rate_limiter._match_route_pattern("/api/*", "/api/posts") is True
        assert rate_limiter._match_route_pattern("/api/*", "/api/users/list") is False

        # Test double wildcard
        assert rate_limiter._match_route_pattern("/api/**", "/api/users") is True
        assert rate_limiter._match_route_pattern("/api/**", "/api/users/list") is True
        assert rate_limiter._match_route_pattern("/api/users/**", "/api/posts") is False

    def test_check_limit(self, rate_limiter: RateLimiter):
        """Test rate limiting functionality."""
        # Test within rate limit
        result = rate_limiter.check_limit("192.168.1.1")
        assert result["allowed"] is True
        assert result["remaining"] == 4  # 5 - 1

        # Make multiple requests
        for _ in range(4):
            result = rate_limiter.check_limit("192.168.1.1")
            assert result["allowed"] is True

        # Test exceeding rate limit
        result = rate_limiter.check_limit("192.168.1.1")
        assert result["allowed"] is False
        assert result["remaining"] == 0
        assert "reset" in result

        # Test with a different IP
        result = rate_limiter.check_limit("192.168.1.2")  # Different IP
        assert result["allowed"] is True

        # Use up normal capacity
        for _ in range(4):
            result = rate_limiter.check_limit("192.168.1.2")
            assert result["allowed"] is True

        # Exceed normal capacity
        result = rate_limiter.check_limit("192.168.1.2")
        assert result["allowed"] is False

    def test_route_specific_check_limit(self, rate_limiter: RateLimiter):
        """Test route-specific rate limiting."""
        # Add a route-specific rate limit
        rate_limiter.add_route_config(
            "/api/limited",
            {
                "requests_per_minute": 2,
                "burst_size": 0,  # Disable burst for this route
            },
        )

        # Test within rate limit for the specific route
        result = rate_limiter.check_limit("192.168.1.1", "/api/limited")
        assert result["allowed"] is True
        assert result["remaining"] == 1  # 2 - 1

        # Make one more request
        result = rate_limiter.check_limit("192.168.1.1", "/api/limited")
        assert result["allowed"] is True
        assert result["remaining"] == 0

        # Test exceeding rate limit for the specific route
        result = rate_limiter.check_limit("192.168.1.1", "/api/limited")
        assert result["allowed"] is False

        # Test that the default route is still allowed
        result = rate_limiter.check_limit("192.168.1.1", "/api/other")
        assert result["allowed"] is True

    def test_auto_ban(self, rate_limiter: RateLimiter):
        """Test auto-ban functionality."""
        # Configure a very low auto-ban threshold
        rate_limiter.config.auto_ban_threshold = 3

        # Make multiple requests to trigger auto-ban
        for _ in range(5):  # Requests per minute = 5
            rate_limiter.check_limit("192.168.1.1")

        # This should trigger a violation
        result = rate_limiter.check_limit("192.168.1.1")
        assert result["allowed"] is False

        # Make more requests to reach the auto-ban threshold
        for _ in range(2):  # Need 3 violations total
            rate_limiter.check_limit("192.168.1.1")

        # Check if the IP is banned
        assert rate_limiter.storage.exists("banned_ip:192.168.1.1")

        # Try a request from the banned IP
        result = rate_limiter.check_limit("192.168.1.1")
        assert result["allowed"] is False


class TestAsyncRateLimiter:
    """Tests for AsyncRateLimiter."""

    @pytest.fixture
    def rate_limit_config(self) -> RateLimitConfig:
        """Create a rate limit configuration for testing."""
        return RateLimitConfig(
            enabled=True,
            requests_per_minute=5,
            burst_size=0,  # Disable burst by default
            auto_ban_threshold=10,
            auto_ban_duration_minutes=60,
        )

    @pytest.fixture
    def async_rate_limiter(
        self, rate_limit_config: RateLimitConfig
    ) -> AsyncRateLimiter:
        """Create an async rate limiter for testing."""
        return AsyncRateLimiter(rate_limit_config, AsyncMemoryStorage())

    def test_initialization(
        self, async_rate_limiter: AsyncRateLimiter, rate_limit_config: RateLimitConfig
    ):
        """Test AsyncRateLimiter initialization."""
        assert async_rate_limiter.config == rate_limit_config
        assert async_rate_limiter.route_configs == {}

    def test_add_route_config(self, async_rate_limiter: AsyncRateLimiter):
        """Test adding a route-specific rate limit configuration."""
        # Add a route config as a dictionary
        async_rate_limiter.add_route_config(
            "/api/limited",
            {
                "requests_per_minute": 10,
                "burst_size": 3,
            },
        )

        assert "/api/limited" in async_rate_limiter.route_configs
        assert (
            async_rate_limiter.route_configs["/api/limited"].requests_per_minute == 10
        )
        assert async_rate_limiter.route_configs["/api/limited"].burst_size == 3

    def test_get_config_for_route(self, async_rate_limiter: AsyncRateLimiter):
        """Test getting the appropriate rate limit configuration for a route."""
        # Add some route configs
        async_rate_limiter.add_route_config(
            "/api/limited",
            {
                "requests_per_minute": 10,
                "burst_size": 3,
            },
        )
        async_rate_limiter.add_route_config(
            "/api/uploads/*",
            {
                "requests_per_minute": 20,
                "burst_size": 5,
            },
        )

        # Test exact match
        config = async_rate_limiter.get_config_for_route("/api/limited")
        assert config.requests_per_minute == 10

        # Test wildcard match
        config = async_rate_limiter.get_config_for_route("/api/uploads/file.txt")
        assert config.requests_per_minute == 20

        # Test fallback to default config
        config = async_rate_limiter.get_config_for_route("/api/other")
        assert config == async_rate_limiter.config

    def test_match_route_pattern(self, async_rate_limiter: AsyncRateLimiter):
        """Test route pattern matching."""
        # Test exact match
        assert (
            async_rate_limiter._match_route_pattern("/api/users", "/api/users") is True
        )
        assert (
            async_rate_limiter._match_route_pattern("/api/users", "/api/posts") is False
        )

        # Test single wildcard
        assert async_rate_limiter._match_route_pattern("/api/*", "/api/users") is True
        assert (
            async_rate_limiter._match_route_pattern("/api/*", "/api/users/list")
            is False
        )

        # Test double wildcard
        assert (
            async_rate_limiter._match_route_pattern("/api/**", "/api/users/list")
            is True
        )

    @pytest.mark.asyncio
    async def test_check_limit(self, async_rate_limiter: AsyncRateLimiter):
        """Test async rate limiting functionality."""
        # Test within rate limit
        result = await async_rate_limiter.check_limit("192.168.1.1")
        assert result["allowed"] is True
        assert result["remaining"] == 4  # 5 - 1

        # Make multiple requests
        for _ in range(4):
            result = await async_rate_limiter.check_limit("192.168.1.1")
            assert result["allowed"] is True

        # Test exceeding rate limit
        result = await async_rate_limiter.check_limit("192.168.1.1")
        assert result["allowed"] is False
        assert result["remaining"] == 0
        assert "reset" in result

    @pytest.mark.asyncio
    async def test_route_specific_check_limit(
        self, async_rate_limiter: AsyncRateLimiter
    ):
        """Test async route-specific rate limiting."""
        # Add a route-specific rate limit
        async_rate_limiter.add_route_config(
            "/api/limited",
            {
                "requests_per_minute": 2,
                "burst_size": 0,  # Disable burst for this route
            },
        )

        # Test within rate limit for the specific route
        result = await async_rate_limiter.check_limit("192.168.1.1", "/api/limited")
        assert result["allowed"] is True
        assert result["remaining"] == 1  # 2 - 1

        # Make one more request
        result = await async_rate_limiter.check_limit("192.168.1.1", "/api/limited")
        assert result["allowed"] is True
        assert result["remaining"] == 0

        # Test exceeding rate limit for the specific route
        result = await async_rate_limiter.check_limit("192.168.1.1", "/api/limited")
        assert result["allowed"] is False

        # Test that the default route is still allowed
        result = await async_rate_limiter.check_limit("192.168.1.1", "/api/other")
        assert result["allowed"] is True

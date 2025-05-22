"""Tests for PyWebGuard filters."""

import pytest
from typing import Dict, Any, cast

from pywebguard.filters.ip_filter import IPFilter, AsyncIPFilter
from pywebguard.filters.user_agent import UserAgentFilter, AsyncUserAgentFilter
from pywebguard.core.config import IPFilterConfig, UserAgentConfig
from pywebguard.storage.memory import MemoryStorage, AsyncMemoryStorage


class TestIPFilter:
    """Tests for IPFilter."""

    @pytest.fixture
    def ip_filter_config(self) -> IPFilterConfig:
        """Create an IP filter configuration for testing."""
        return IPFilterConfig(
            enabled=True,
            whitelist=["127.0.0.1", "192.168.1.0/24"],
            blacklist=["10.0.0.1", "172.16.0.0/16"],
        )

    @pytest.fixture
    def ip_filter(self, ip_filter_config: IPFilterConfig) -> IPFilter:
        """Create an IP filter for testing."""
        return IPFilter(ip_filter_config, MemoryStorage())

    def test_initialization(
        self, ip_filter: IPFilter, ip_filter_config: IPFilterConfig
    ):
        """Test IPFilter initialization."""
        assert ip_filter.config == ip_filter_config
        assert len(ip_filter.whitelist_networks) == 2
        assert len(ip_filter.blacklist_networks) == 2

    def test_is_allowed(self, ip_filter: IPFilter):
        """Test IP filtering."""
        # Test allowed IP (exact match)
        result = ip_filter.is_allowed("127.0.0.1")
        assert result["allowed"] is True

        # Test allowed IP (CIDR match)
        result = ip_filter.is_allowed("192.168.1.100")
        assert result["allowed"] is True

        # Test blocked IP (exact match)
        result = ip_filter.is_allowed("10.0.0.1")
        assert result["allowed"] is False
        assert result["reason"] == "IP in blacklist"

        # Test blocked IP (CIDR match)
        result = ip_filter.is_allowed("172.16.5.10")
        assert result["allowed"] is False
        assert result["reason"] == "IP in blacklist"

        # Test IP not in whitelist
        ip_filter.config.whitelist = ["192.168.1.0/24"]  # Remove 127.0.0.1
        result = ip_filter.is_allowed("127.0.0.1")
        assert result["allowed"] is False
        assert result["reason"] == "IP not in whitelist"

        # Test invalid IP
        result = ip_filter.is_allowed("invalid_ip")
        assert result["allowed"] is False
        assert result["reason"] == "Invalid IP address"

        # Test with filter disabled
        ip_filter.config.enabled = False
        result = ip_filter.is_allowed("10.0.0.1")  # Blocked IP
        assert result["allowed"] is True

    def test_banned_ip(self, ip_filter: IPFilter):
        """Test banned IP functionality."""
        # Ban an IP
        ip_filter.storage.set("banned_ip:8.8.8.8", {"reason": "Test ban"})

        # Test banned IP
        result = ip_filter.is_allowed("8.8.8.8")
        assert result["allowed"] is False
        assert result["reason"] == "IP is banned"


class TestAsyncIPFilter:
    """Tests for AsyncIPFilter."""

    @pytest.fixture
    def ip_filter_config(self) -> IPFilterConfig:
        """Create an IP filter configuration for testing."""
        return IPFilterConfig(
            enabled=True,
            whitelist=["127.0.0.1", "192.168.1.0/24"],
            blacklist=["10.0.0.1", "172.16.0.0/16"],
        )

    @pytest.fixture
    def async_ip_filter(self, ip_filter_config: IPFilterConfig) -> AsyncIPFilter:
        """Create an async IP filter for testing."""
        return AsyncIPFilter(ip_filter_config, AsyncMemoryStorage())

    def test_initialization(
        self, async_ip_filter: AsyncIPFilter, ip_filter_config: IPFilterConfig
    ):
        """Test AsyncIPFilter initialization."""
        assert async_ip_filter.config == ip_filter_config
        assert len(async_ip_filter.whitelist_networks) == 2
        assert len(async_ip_filter.blacklist_networks) == 2

    @pytest.mark.asyncio
    async def test_is_allowed(self, async_ip_filter: AsyncIPFilter):
        """Test async IP filtering."""
        # Test allowed IP (exact match)
        result = await async_ip_filter.is_allowed("127.0.0.1")
        assert result["allowed"] is True

        # Test allowed IP (CIDR match)
        result = await async_ip_filter.is_allowed("192.168.1.100")
        assert result["allowed"] is True

        # Test blocked IP (exact match)
        result = await async_ip_filter.is_allowed("10.0.0.1")
        assert result["allowed"] is False
        assert result["reason"] == "IP in blacklist"

        # Test blocked IP (CIDR match)
        result = await async_ip_filter.is_allowed("172.16.5.10")
        assert result["allowed"] is False
        assert result["reason"] == "IP in blacklist"

        # Test IP not in whitelist
        async_ip_filter.config.whitelist = ["192.168.1.0/24"]  # Remove 127.0.0.1
        result = await async_ip_filter.is_allowed("127.0.0.1")
        assert result["allowed"] is False
        assert result["reason"] == "IP not in whitelist"

        # Test invalid IP
        result = await async_ip_filter.is_allowed("invalid_ip")
        assert result["allowed"] is False
        assert result["reason"] == "Invalid IP address"

        # Test with filter disabled
        async_ip_filter.config.enabled = False
        result = await async_ip_filter.is_allowed("10.0.0.1")  # Blocked IP
        assert result["allowed"] is True

    @pytest.mark.asyncio
    async def test_banned_ip(self, async_ip_filter: AsyncIPFilter):
        """Test banned IP functionality."""
        # Ban an IP
        await async_ip_filter.storage.set("banned_ip:8.8.8.8", {"reason": "Test ban"})

        # Test banned IP
        result = await async_ip_filter.is_allowed("8.8.8.8")
        assert result["allowed"] is False
        assert result["reason"] == "IP is banned"


class TestUserAgentFilter:
    """Tests for UserAgentFilter."""

    @pytest.fixture
    def ua_filter_config(self) -> UserAgentConfig:
        """Create a user agent filter configuration for testing."""
        return UserAgentConfig(
            enabled=True,
            blocked_agents=["curl", "wget", "python-requests"],
        )

    @pytest.fixture
    def ua_filter(self, ua_filter_config: UserAgentConfig) -> UserAgentFilter:
        """Create a user agent filter for testing."""
        return UserAgentFilter(ua_filter_config, MemoryStorage())

    def test_initialization(
        self, ua_filter: UserAgentFilter, ua_filter_config: UserAgentConfig
    ):
        """Test UserAgentFilter initialization."""
        assert ua_filter.config == ua_filter_config

    def test_is_allowed(self, ua_filter: UserAgentFilter):
        """Test user agent filtering."""
        # Test allowed user agent
        result = ua_filter.is_allowed("Mozilla/5.0")
        assert result["allowed"] is True

        # Test blocked user agent (exact match)
        result = ua_filter.is_allowed("curl/7.64.1")
        assert result["allowed"] is False
        assert result["reason"] == "Blocked user agent: curl"

        # Test blocked user agent (partial match)
        result = ua_filter.is_allowed(
            "Mozilla/5.0 (compatible; python-requests/2.25.1)"
        )
        assert result["allowed"] is False
        assert result["reason"] == "Blocked user agent: python-requests"

        # Test empty user agent
        result = ua_filter.is_allowed("")
        assert result["allowed"] is False
        assert result["reason"] == "Empty user agent"

        # Test with filter disabled
        ua_filter.config.enabled = False
        result = ua_filter.is_allowed("curl/7.64.1")  # Blocked user agent
        assert result["allowed"] is True


class TestAsyncUserAgentFilter:
    """Tests for AsyncUserAgentFilter."""

    @pytest.fixture
    def ua_filter_config(self) -> UserAgentConfig:
        """Create a user agent filter configuration for testing."""
        return UserAgentConfig(
            enabled=True,
            blocked_agents=["curl", "wget", "python-requests"],
        )

    @pytest.fixture
    def async_ua_filter(
        self, ua_filter_config: UserAgentConfig
    ) -> AsyncUserAgentFilter:
        """Create an async user agent filter for testing."""
        return AsyncUserAgentFilter(ua_filter_config, AsyncMemoryStorage())

    def test_initialization(
        self, async_ua_filter: AsyncUserAgentFilter, ua_filter_config: UserAgentConfig
    ):
        """Test AsyncUserAgentFilter initialization."""
        assert async_ua_filter.config == ua_filter_config

    @pytest.mark.asyncio
    async def test_is_allowed(self, async_ua_filter: AsyncUserAgentFilter):
        """Test async user agent filtering."""
        # Test allowed user agent
        result = await async_ua_filter.is_allowed("Mozilla/5.0")
        assert result["allowed"] is True

        # Test blocked user agent (exact match)
        result = await async_ua_filter.is_allowed("curl/7.64.1")
        assert result["allowed"] is False
        assert result["reason"] == "Blocked user agent: curl"

        # Test blocked user agent (partial match)
        result = await async_ua_filter.is_allowed(
            "Mozilla/5.0 (compatible; python-requests/2.25.1)"
        )
        assert result["allowed"] is False
        assert result["reason"] == "Blocked user agent: python-requests"

        # Test empty user agent
        result = await async_ua_filter.is_allowed("")
        assert result["allowed"] is False
        assert result["reason"] == "Empty user agent"

        # Test with filter disabled
        async_ua_filter.config.enabled = False
        result = await async_ua_filter.is_allowed("curl/7.64.1")  # Blocked user agent
        assert result["allowed"] is True

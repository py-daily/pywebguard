"""Tests for PyWebGuard user agent filters."""

import pytest
from typing import Dict, Union

from pywebguard.filters.user_agent import UserAgentFilter, AsyncUserAgentFilter
from pywebguard.core.config import UserAgentConfig
from pywebguard.storage.memory import MemoryStorage, AsyncMemoryStorage


class TestUserAgentFilter:
    """Tests for UserAgentFilter."""

    @pytest.fixture
    def user_agent_config(self) -> UserAgentConfig:
        """Create a user agent filter configuration for testing."""
        return UserAgentConfig(
            enabled=True,
            blocked_agents=[
                "curl",
                "wget",
                "python-requests",
                "bad-bot",
            ],
        )

    @pytest.fixture
    def user_agent_filter(self, user_agent_config: UserAgentConfig) -> UserAgentFilter:
        """Create a user agent filter for testing."""
        return UserAgentFilter(user_agent_config, MemoryStorage())

    def test_initialization(
        self, user_agent_filter: UserAgentFilter, user_agent_config: UserAgentConfig
    ):
        """Test UserAgentFilter initialization."""
        assert user_agent_filter.config == user_agent_config

    def test_allowed_user_agent(self, user_agent_filter: UserAgentFilter):
        """Test that allowed user agents pass through."""
        result = user_agent_filter.is_allowed(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        assert result["allowed"] is True
        assert result["reason"] == ""

    def test_empty_user_agent(self, user_agent_filter: UserAgentFilter):
        """Test that empty user agents are blocked."""
        result = user_agent_filter.is_allowed("")
        assert result["allowed"] is False
        assert result["reason"] == "Empty user agent"

    def test_blocked_user_agent(self, user_agent_filter: UserAgentFilter):
        """Test that blocked user agents are caught."""
        result = user_agent_filter.is_allowed("curl/7.64.1")
        assert result["allowed"] is False
        assert result["reason"] == "Blocked user agent: curl"

    def test_case_insensitive_matching(self, user_agent_filter: UserAgentFilter):
        """Test that user agent matching is case-insensitive."""
        result = user_agent_filter.is_allowed("CURL/7.64.1")
        assert result["allowed"] is False
        assert result["reason"] == "Blocked user agent: curl"

        result = user_agent_filter.is_allowed("Python-Requests/2.28.1")
        assert result["allowed"] is False
        assert result["reason"] == "Blocked user agent: python-requests"

    def test_partial_matching(self, user_agent_filter: UserAgentFilter):
        """Test that partial matches in user agents are caught."""
        # Test that a user agent containing a blocked agent is caught
        result = user_agent_filter.is_allowed("MyBot/bad-bot/1.0")
        assert result["allowed"] is False
        assert result["reason"] == "Blocked user agent: bad-bot"

        # Test that a user agent not containing any blocked agents is allowed
        result = user_agent_filter.is_allowed("MyGoodBot/1.0")
        assert result["allowed"] is True
        assert result["reason"] == ""

    def test_disabled_filter(self, user_agent_filter: UserAgentFilter):
        """Test that disabled filter allows all user agents."""
        user_agent_filter.config.enabled = False
        result = user_agent_filter.is_allowed("curl/7.64.1")
        assert result["allowed"] is True
        assert result["reason"] == ""


class TestAsyncUserAgentFilter:
    """Tests for AsyncUserAgentFilter."""

    @pytest.fixture
    def user_agent_config(self) -> UserAgentConfig:
        """Create a user agent filter configuration for testing."""
        return UserAgentConfig(
            enabled=True,
            blocked_agents=[
                "curl",
                "wget",
                "python-requests",
                "bad-bot",
            ],
        )

    @pytest.fixture
    def async_user_agent_filter(
        self, user_agent_config: UserAgentConfig
    ) -> AsyncUserAgentFilter:
        """Create an async user agent filter for testing."""
        return AsyncUserAgentFilter(user_agent_config, AsyncMemoryStorage())

    def test_initialization(
        self,
        async_user_agent_filter: AsyncUserAgentFilter,
        user_agent_config: UserAgentConfig,
    ):
        """Test AsyncUserAgentFilter initialization."""
        assert async_user_agent_filter.config == user_agent_config

    @pytest.mark.asyncio
    async def test_allowed_user_agent(
        self, async_user_agent_filter: AsyncUserAgentFilter
    ):
        """Test that allowed user agents pass through."""
        result = await async_user_agent_filter.is_allowed(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        assert result["allowed"] is True
        assert result["reason"] == ""

    @pytest.mark.asyncio
    async def test_empty_user_agent(
        self, async_user_agent_filter: AsyncUserAgentFilter
    ):
        """Test that empty user agents are blocked."""
        result = await async_user_agent_filter.is_allowed("")
        assert result["allowed"] is False
        assert result["reason"] == "Empty user agent"

    @pytest.mark.asyncio
    async def test_blocked_user_agent(
        self, async_user_agent_filter: AsyncUserAgentFilter
    ):
        """Test that blocked user agents are caught."""
        result = await async_user_agent_filter.is_allowed("curl/7.64.1")
        assert result["allowed"] is False
        assert result["reason"] == "Blocked user agent: curl"

    @pytest.mark.asyncio
    async def test_case_insensitive_matching(
        self, async_user_agent_filter: AsyncUserAgentFilter
    ):
        """Test that user agent matching is case-insensitive."""
        result = await async_user_agent_filter.is_allowed("CURL/7.64.1")
        assert result["allowed"] is False
        assert result["reason"] == "Blocked user agent: curl"

        result = await async_user_agent_filter.is_allowed("Python-Requests/2.28.1")
        assert result["allowed"] is False
        assert result["reason"] == "Blocked user agent: python-requests"

    @pytest.mark.asyncio
    async def test_partial_matching(
        self, async_user_agent_filter: AsyncUserAgentFilter
    ):
        """Test that partial matches in user agents are caught."""
        # Test that a user agent containing a blocked agent is caught
        result = await async_user_agent_filter.is_allowed("MyBot/bad-bot/1.0")
        assert result["allowed"] is False
        assert result["reason"] == "Blocked user agent: bad-bot"

        # Test that a user agent not containing any blocked agents is allowed
        result = await async_user_agent_filter.is_allowed("MyGoodBot/1.0")
        assert result["allowed"] is True
        assert result["reason"] == ""

    @pytest.mark.asyncio
    async def test_disabled_filter(self, async_user_agent_filter: AsyncUserAgentFilter):
        """Test that disabled filter allows all user agents."""
        async_user_agent_filter.config.enabled = False
        result = await async_user_agent_filter.is_allowed("curl/7.64.1")
        assert result["allowed"] is True
        assert result["reason"] == ""

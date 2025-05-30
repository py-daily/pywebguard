"""
User agent filtering functionality for PyWebGuard with both sync and async support.
"""

from typing import Dict, Optional, Union
from pywebguard.core.config import UserAgentConfig
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage
from pywebguard.filters.base import BaseFilter, AsyncBaseFilter


class UserAgentFilter(BaseFilter):
    """
    Filter requests based on user agent (synchronous).
    """

    def __init__(
        self,
        config: UserAgentConfig,
        storage: BaseStorage,
    ):
        """
        Initialize the user agent filter.

        Args:
            config: User agent filter configuration
            storage: Storage backend for persistent data
        """
        self.config = config
        self.storage = storage

    def is_allowed(
        self, user_agent: str, path: Optional[str] = None
    ) -> Dict[str, Union[bool, str]]:
        """
        Check if a user agent is allowed.

        Args:
            user_agent: The user agent string to check

        Returns:
            Dict with allowed status and reason
        """

        if not self.config.enabled:
            return {"allowed": True, "reason": ""}

        if path in self.config.excluded_paths:
            return {
                "allowed": True,
                "reason": "Path excluded from user-agent filtering",
            }

        if not user_agent:
            return {"allowed": False, "reason": "Empty user agent"}

        # Check if user agent is in blocked list
        for blocked_agent in self.config.blocked_agents:
            if blocked_agent.lower() in user_agent.lower():
                return {
                    "allowed": False,
                    "reason": f"Blocked user agent: {blocked_agent}",
                }

        return {"allowed": True, "reason": ""}


class AsyncUserAgentFilter(AsyncBaseFilter):
    """
    Filter requests based on user agent (asynchronous).
    """

    def __init__(
        self,
        config: UserAgentConfig,
        storage: AsyncBaseStorage,
    ):
        """
        Initialize the async user agent filter.

        Args:
            config: User agent filter configuration
            storage: Async storage backend for persistent data
        """
        self.config = config
        self.storage = storage

    async def is_allowed(
        self, user_agent: str, path: Optional[str] = None
    ) -> Dict[str, Union[bool, str]]:
        """
        Check if a user agent is allowed asynchronously.

        Args:
            user_agent: The user agent string to check

        Returns:
            Dict with allowed status and reason
        """

        if not self.config.enabled:
            return {"allowed": True, "reason": ""}
        if path in self.config.excluded_paths:
            return {
                "allowed": True,
                "reason": "Path excluded from user-agent filtering",
            }
        if not user_agent:
            return {"allowed": False, "reason": "Empty user agent"}

        # Check if user agent is in blocked list
        for blocked_agent in self.config.blocked_agents:
            if blocked_agent.lower() in user_agent.lower():
                return {
                    "allowed": False,
                    "reason": f"Blocked user agent: {blocked_agent}",
                }

        return {"allowed": True, "reason": ""}

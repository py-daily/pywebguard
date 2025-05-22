"""
Base limiter interfaces for PyWebGuard with both sync and async support.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLimiter(ABC):
    """
    Abstract base class for synchronous limiters.
    """

    @abstractmethod
    def check_limit(self, identifier: str, path: str = None) -> Dict[str, Any]:
        """
        Check if a request should be limited.

        Args:
            identifier: The identifier to check
            path: The request path (for route-specific rate limiting)

        Returns:
            Dict with allowed status and details
        """
        pass


class AsyncBaseLimiter(ABC):
    """
    Abstract base class for asynchronous limiters.
    """

    @abstractmethod
    async def check_limit(self, identifier: str, path: str = None) -> Dict[str, Any]:
        """
        Check if a request should be limited asynchronously.

        Args:
            identifier: The identifier to check
            path: The request path (for route-specific rate limiting)

        Returns:
            Dict with allowed status and details
        """
        pass

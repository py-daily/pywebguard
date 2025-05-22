"""
Base security interfaces for PyWebGuard with both sync and async support.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseSecurityComponent(ABC):
    """
    Abstract base class for synchronous security components.
    """

    @abstractmethod
    def check_request(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a request should be allowed.

        Args:
            request_info: Dict with request information

        Returns:
            Dict with allowed status and details
        """
        pass


class AsyncBaseSecurityComponent(ABC):
    """
    Abstract base class for asynchronous security components.
    """

    @abstractmethod
    async def check_request(self, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a request should be allowed asynchronously.

        Args:
            request_info: Dict with request information

        Returns:
            Dict with allowed status and details
        """
        pass

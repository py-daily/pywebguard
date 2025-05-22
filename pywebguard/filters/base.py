"""
Base filter interfaces for PyWebGuard with both sync and async support.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Union


class BaseFilter(ABC):
    """
    Abstract base class for synchronous filters.
    """

    @abstractmethod
    def is_allowed(self, value: Any) -> Dict[str, Union[bool, str]]:
        """
        Check if a value is allowed by the filter.

        Args:
            value: The value to check

        Returns:
            Dict with allowed status and reason
        """
        pass


class AsyncBaseFilter(ABC):
    """
    Abstract base class for asynchronous filters.
    """

    @abstractmethod
    async def is_allowed(self, value: Any) -> Dict[str, Union[bool, str]]:
        """
        Check if a value is allowed by the filter asynchronously.

        Args:
            value: The value to check

        Returns:
            Dict with allowed status and reason
        """
        pass

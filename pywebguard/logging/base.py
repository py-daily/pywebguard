"""
Base logging interface for PyWebGuard.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging


class LoggingBackend(ABC):
    """
    Abstract base class for synchronous logging backends.
    """

    @abstractmethod
    def setup(self, config: Any) -> None:
        """
        Set up the logging backend with the given configuration.

        Args:
            config: Configuration specific to the backend
        """
        pass

    @abstractmethod
    def log_request(self, request_info: Dict[str, Any], response: Any) -> None:
        """
        Log a request.

        Args:
            request_info: Dict with request information
            response: The framework-specific response object
        """
        pass

    @abstractmethod
    def log_blocked_request(
        self, request_info: Dict[str, Any], block_type: str, reason: str
    ) -> None:
        """
        Log a blocked request.

        Args:
            request_info: Dict with request information
            block_type: Type of block (IP filter, rate limit, etc.)
            reason: Reason for blocking
        """
        pass

    @abstractmethod
    def log_security_event(
        self, level: str, message: str, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a security event.

        Args:
            level: Log level (INFO, WARNING, ERROR, etc.)
            message: The log message
            extra: Additional information to log
        """
        pass


class AsyncLoggingBackend(ABC):
    """
    Abstract base class for asynchronous logging backends.
    """

    @abstractmethod
    def setup(self, config: Any) -> None:
        """
        Set up the logging backend with the given configuration.

        Args:
            config: Configuration specific to the backend
        """
        pass

    @abstractmethod
    async def log_request(self, request_info: Dict[str, Any], response: Any) -> None:
        """
        Log a request asynchronously.

        Args:
            request_info: Dict with request information
            response: The framework-specific response object
        """
        pass

    @abstractmethod
    async def log_blocked_request(
        self, request_info: Dict[str, Any], block_type: str, reason: str
    ) -> None:
        """
        Log a blocked request asynchronously.

        Args:
            request_info: Dict with request information
            block_type: Type of block (IP filter, rate limit, etc.)
            reason: Reason for blocking
        """
        pass

    @abstractmethod
    async def log_security_event(
        self, level: str, message: str, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a security event asynchronously.

        Args:
            level: Log level (INFO, WARNING, ERROR, etc.)
            message: The log message
            extra: Additional information to log
        """
        pass

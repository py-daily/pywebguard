"""
Meilisearch logging backend for PyWebGuard.
"""

import time
import logging
from typing import Dict, Any, Optional, TYPE_CHECKING

# Disable urllib3 debug logs
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Try to import meilisearch
try:
    import meilisearch

    MEILISEARCH_AVAILABLE = True
except ImportError:
    MEILISEARCH_AVAILABLE = False
    if TYPE_CHECKING:
        import meilisearch

from ..base import LoggingBackend, AsyncLoggingBackend


class MeilisearchBackend(LoggingBackend):
    """
    Synchronous Meilisearch logging backend implementation.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Meilisearch backend.

        Args:
            config: Configuration dictionary containing:
                - url: Meilisearch server URL
                - api_key: Meilisearch API key
                - index_name: Name of the index to store logs

        Raises:
            ImportError: If meilisearch is not installed
        """
        if not MEILISEARCH_AVAILABLE:
            raise ImportError(
                "Meilisearch backend requires meilisearch. Install it with 'pip install meilisearch'"
            )

        self.config = config
        self.client = None
        self.index = None
        self.setup(config)

    def setup(self, config: Dict[str, Any]) -> None:
        """
        Set up the Meilisearch client and index.

        Args:
            config: Configuration dictionary
        """
        self.client = meilisearch.Client(config["url"], config["api_key"])
        self.index = self.client.index(config["index_name"])

        # Ensure timestamp and other fields are filterable
        self.index.update_filterable_attributes(
            [
                "timestamp",
                "level",
                "ip",
                "method",
                "path",
                "status_code",
                "block_type",
                "reason",
            ]
        )

        self.index.update_sortable_attributes(["timestamp", "level", "status_code"])

    def _create_log_entry(self, **kwargs) -> Dict[str, Any]:
        """
        Create a standardized log entry.

        Returns:
            Dict containing the log entry
        """
        return {
            "id": f"{int(time.time() * 1000)}-{kwargs.get('level', 'INFO')}",
            "timestamp": int(time.time()),
            **kwargs,
        }

    def log_request(self, request_info: Dict[str, Any], response: Any) -> None:
        """
        Log a request to Meilisearch.

        Args:
            request_info: Dict with request information
            response: The framework-specific response object
        """
        log_entry = self._create_log_entry(
            level="INFO",
            ip=request_info.get("ip", "unknown"),
            method=request_info.get("method", "unknown"),
            path=request_info.get("path", "unknown"),
            status_code=self._extract_status_code(response),
            user_agent=request_info.get("user_agent", "unknown"),
            event_type="request",
        )
        self.index.add_documents([log_entry])
        print(f"[MeilisearchBackend::DEBUG] Logged request: {log_entry}")

    def log_blocked_request(
        self, request_info: Dict[str, Any], block_type: str, reason: str
    ) -> None:
        """
        Log a blocked request to Meilisearch.

        Args:
            request_info: Dict with request information
            block_type: Type of block (IP filter, rate limit, etc.)
            reason: Reason for blocking
        """
        log_entry = self._create_log_entry(
            level="WARNING",
            ip=request_info.get("ip", "unknown"),
            method=request_info.get("method", "unknown"),
            path=request_info.get("path", "unknown"),
            block_type=block_type,
            reason=reason,
            user_agent=request_info.get("user_agent", "unknown"),
            event_type="blocked_request",
        )
        self.index.add_documents([log_entry])
        print(f"[MeilisearchBackend::DEBUG] Logged blocked request: {log_entry}")

    def log_security_event(
        self, level: str, message: str, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a security event to Meilisearch.

        Args:
            level: Log level (INFO, WARNING, ERROR, etc.)
            message: The log message
            extra: Additional information to log
        """
        log_entry = self._create_log_entry(
            level=level, message=message, event_type="security_event", **(extra or {})
        )
        self.index.add_documents([log_entry])
        print(f"[MeilisearchBackend::DEBUG] Logged security event: {log_entry}")

    def _extract_status_code(self, response: Any) -> int:
        """
        Extract status code from a response object.

        Args:
            response: The framework-specific response object

        Returns:
            The status code or 0 if not found
        """
        try:
            if hasattr(response, "status_code"):
                return response.status_code
            if isinstance(response, dict) and "status_code" in response:
                return response["status_code"]
        except:
            pass
        return 0


class AsyncMeilisearchBackend(AsyncLoggingBackend):
    """
    Asynchronous Meilisearch logging backend implementation.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the async Meilisearch backend.

        Args:
            config: Configuration dictionary containing:
                - url: Meilisearch server URL
                - api_key: Meilisearch API key
                - index_name: Name of the index to store logs

        Raises:
            ImportError: If meilisearch is not installed
        """
        if not MEILISEARCH_AVAILABLE:
            raise ImportError(
                "Meilisearch backend requires meilisearch. Install it with 'pip install meilisearch'"
            )
        self.config = config
        self.client = meilisearch.Client(config["url"], config["api_key"])
        self.index = self.client.index(config["index_name"])
        self.setup(config)

    def setup(self, config: Dict[str, Any]) -> None:
        """
        Set up the async Meilisearch client and index.

        Args:
            config: Configuration dictionary
        """
        # Ensure timestamp and other fields are filterable
        self.index.update_filterable_attributes(
            [
                "timestamp",
                "level",
                "ip",
                "method",
                "path",
                "status_code",
                "block_type",
                "reason",
            ]
        )
        self.index.update_sortable_attributes(["timestamp", "level", "status_code"])

    def _create_log_entry(self, **kwargs) -> Dict[str, Any]:
        """
        Create a standardized log entry.

        Returns:
            Dict containing the log entry
        """
        return {
            "id": f"{int(time.time() * 1000)}-{kwargs.get('level', 'INFO')}",
            "timestamp": int(time.time()),
            **kwargs,
        }

    async def log_request(self, request_info: Dict[str, Any], response: Any) -> None:
        """
        Log a request to Meilisearch asynchronously.

        Args:
            request_info: Dict with request information
            response: The framework-specific response object
        """
        log_entry = self._create_log_entry(
            level="INFO",
            ip=request_info.get("ip", "unknown"),
            method=request_info.get("method", "unknown"),
            path=request_info.get("path", "unknown"),
            status_code=self._extract_status_code(response),
            user_agent=request_info.get("user_agent", "unknown"),
            event_type="request",
        )
        self.index.add_documents([log_entry])

    async def log_blocked_request(
        self, request_info: Dict[str, Any], block_type: str, reason: str
    ) -> None:
        """
        Log a blocked request to Meilisearch asynchronously.

        Args:
            request_info: Dict with request information
            block_type: Type of block (IP filter, rate limit, etc.)
            reason: Reason for blocking
        """
        log_entry = self._create_log_entry(
            level="WARNING",
            ip=request_info.get("ip", "unknown"),
            method=request_info.get("method", "unknown"),
            path=request_info.get("path", "unknown"),
            block_type=block_type,
            reason=reason,
            user_agent=request_info.get("user_agent", "unknown"),
            event_type="blocked_request",
        )
        self.index.add_documents([log_entry])

    async def log_security_event(
        self, level: str, message: str, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a security event to Meilisearch asynchronously.

        Args:
            level: Log level (INFO, WARNING, ERROR, etc.)
            message: The log message
            extra: Additional information to log
        """
        log_entry = self._create_log_entry(
            level=level, message=message, event_type="security_event", **(extra or {})
        )
        self.index.add_documents([log_entry])

    def _extract_status_code(self, response: Any) -> int:
        """
        Extract status code from a response object.

        Args:
            response: The framework-specific response object

        Returns:
            The status code or 0 if not found
        """
        try:
            if hasattr(response, "status_code"):
                return response.status_code
            if isinstance(response, dict) and "status_code" in response:
                return response["status_code"]
        except:
            pass
        return 0

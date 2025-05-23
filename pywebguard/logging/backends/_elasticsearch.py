"""
Elasticsearch logging backend for PyWebGuard.
"""

import time
import logging
from typing import Dict, Any, Optional
from elasticsearch import Elasticsearch
from ..base import LoggingBackend


class ElasticsearchBackend(LoggingBackend):
    """
    Elasticsearch logging backend implementation.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Elasticsearch backend.

        Args:
            config: Configuration dictionary containing:
                - hosts: List of Elasticsearch hosts
                - index_prefix: Prefix for index names
                - username: Optional username for authentication
                - password: Optional password for authentication
        """
        self.config = config
        self.client = None
        self.index_prefix = config.get("index_prefix", "pywebguard")
        self.setup(config)

    def setup(self, config: Dict[str, Any]) -> None:
        """
        Set up the Elasticsearch client.

        Args:
            config: Configuration dictionary
        """
        auth = None
        if "username" in config and "password" in config:
            auth = (config["username"], config["password"])

        self.client = Elasticsearch(hosts=config["hosts"], basic_auth=auth)

        # Create index template if it doesn't exist
        template_name = f"{self.index_prefix}_template"
        template_body = {
            "index_patterns": [f"{self.index_prefix}-*"],
            "settings": {"number_of_shards": 1, "number_of_replicas": 1},
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "ip": {"type": "ip"},
                    "method": {"type": "keyword"},
                    "path": {"type": "keyword"},
                    "status_code": {"type": "integer"},
                    "block_type": {"type": "keyword"},
                    "reason": {"type": "text"},
                    "user_agent": {"type": "text"},
                    "event_type": {"type": "keyword"},
                    "message": {"type": "text"},
                }
            },
        }

        if not self.client.indices.exists_template(name=template_name):
            self.client.indices.put_template(name=template_name, body=template_body)

    def _get_index_name(self) -> str:
        """
        Get the current index name based on date.

        Returns:
            Index name string
        """
        from datetime import datetime

        date_str = datetime.now().strftime("%Y.%m.%d")
        return f"{self.index_prefix}-{date_str}"

    def _create_log_entry(self, **kwargs) -> Dict[str, Any]:
        """
        Create a standardized log entry.

        Returns:
            Dict containing the log entry
        """
        return {"timestamp": int(time.time() * 1000), **kwargs}  # milliseconds

    def log_request(self, request_info: Dict[str, Any], response: Any) -> None:
        """
        Log a request to Elasticsearch.

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
        self.client.index(index=self._get_index_name(), document=log_entry)

    def log_blocked_request(
        self, request_info: Dict[str, Any], block_type: str, reason: str
    ) -> None:
        """
        Log a blocked request to Elasticsearch.

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
        self.client.index(index=self._get_index_name(), document=log_entry)

    def log_security_event(
        self, level: str, message: str, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a security event to Elasticsearch.

        Args:
            level: Log level (INFO, WARNING, ERROR, etc.)
            message: The log message
            extra: Additional information to log
        """
        log_entry = self._create_log_entry(
            level=level, message=message, event_type="security_event", **(extra or {})
        )
        self.client.index(index=self._get_index_name(), document=log_entry)

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

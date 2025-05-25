# """
# Elasticsearch logging backend for PyWebGuard.
# """

# import time
# import logging
# from typing import Dict, Any, Optional, TYPE_CHECKING

# # Try to import elasticsearch
# try:
#     import elasticsearch
#     from elasticsearch import AsyncElasticsearch

#     ELASTICSEARCH_AVAILABLE = True
# except ImportError:
#     ELASTICSEARCH_AVAILABLE = False
#     if TYPE_CHECKING:
#         import elasticsearch
#         from elasticsearch import AsyncElasticsearch

# from ..base import LoggingBackend, AsyncLoggingBackend


# class ElasticsearchBackend(LoggingBackend):
#     """
#     Synchronous Elasticsearch logging backend implementation.
#     """

#     def __init__(self, config: Dict[str, Any]):
#         """
#         Initialize the Elasticsearch backend.

#         Args:
#             config: Configuration dictionary containing:
#                 - url: Elasticsearch server URL
#                 - username: Elasticsearch username (optional)
#                 - password: Elasticsearch password (optional)
#                 - index_name: Name of the index to store logs

#         Raises:
#             ImportError: If elasticsearch is not installed
#         """
#         if not ELASTICSEARCH_AVAILABLE:
#             raise ImportError(
#                 "Elasticsearch backend requires elasticsearch. Install it with 'pip install elasticsearch'"
#             )

#         self.config = config
#         self.client = None
#         self.setup(config)

#     def setup(self, config: Dict[str, Any]) -> None:
#         """
#         Set up the Elasticsearch client.

#         Args:
#             config: Configuration dictionary
#         """
#         # Create client with authentication if provided
#         if "username" in config and "password" in config:
#             self.client = elasticsearch.Elasticsearch(
#                 config["url"],
#                 basic_auth=(config["username"], config["password"]),
#             )
#         else:
#             self.client = elasticsearch.Elasticsearch(config["url"])

#     def _get_index_name(self) -> str:
#         """
#         Get the index name with date suffix.

#         Returns:
#             Index name with date suffix
#         """
#         return f"{self.config['index_name']}-{time.strftime('%Y.%m.%d')}"

#     def _create_log_entry(self, **kwargs) -> Dict[str, Any]:
#         """
#         Create a standardized log entry.

#         Returns:
#             Dict containing the log entry
#         """
#         return {
#             "@timestamp": time.time(),
#             **kwargs,
#         }

#     def log_request(self, request_info: Dict[str, Any], response: Any) -> None:
#         """
#         Log a request to Elasticsearch.

#         Args:
#             request_info: Dict with request information
#             response: The framework-specific response object
#         """
#         log_entry = self._create_log_entry(
#             level="INFO",
#             ip=request_info.get("ip", "unknown"),
#             method=request_info.get("method", "unknown"),
#             path=request_info.get("path", "unknown"),
#             status_code=self._extract_status_code(response),
#             user_agent=request_info.get("user_agent", "unknown"),
#             event_type="request",
#         )
#         self.client.index(index=self._get_index_name(), document=log_entry)

#     def log_blocked_request(
#         self, request_info: Dict[str, Any], block_type: str, reason: str
#     ) -> None:
#         """
#         Log a blocked request to Elasticsearch.

#         Args:
#             request_info: Dict with request information
#             block_type: Type of block (IP filter, rate limit, etc.)
#             reason: Reason for blocking
#         """
#         log_entry = self._create_log_entry(
#             level="WARNING",
#             ip=request_info.get("ip", "unknown"),
#             method=request_info.get("method", "unknown"),
#             path=request_info.get("path", "unknown"),
#             block_type=block_type,
#             reason=reason,
#             user_agent=request_info.get("user_agent", "unknown"),
#             event_type="blocked_request",
#         )
#         self.client.index(index=self._get_index_name(), document=log_entry)

#     def log_security_event(
#         self, level: str, message: str, extra: Optional[Dict[str, Any]] = None
#     ) -> None:
#         """
#         Log a security event to Elasticsearch.

#         Args:
#             level: Log level (INFO, WARNING, ERROR, etc.)
#             message: The log message
#             extra: Additional information to log
#         """
#         log_entry = self._create_log_entry(
#             level=level, message=message, event_type="security_event", **(extra or {})
#         )
#         self.client.index(index=self._get_index_name(), document=log_entry)

#     def _extract_status_code(self, response: Any) -> int:
#         """
#         Extract status code from a response object.

#         Args:
#             response: The framework-specific response object

#         Returns:
#             The status code or 0 if not found
#         """
#         try:
#             if hasattr(response, "status_code"):
#                 return response.status_code
#             if isinstance(response, dict) and "status_code" in response:
#                 return response["status_code"]
#         except:
#             pass
#         return 0


# class AsyncElasticsearchBackend(AsyncLoggingBackend):
#     """
#     Asynchronous Elasticsearch logging backend implementation.
#     """

#     def __init__(self, config: Dict[str, Any]):
#         """
#         Initialize the async Elasticsearch backend.

#         Args:
#             config: Configuration dictionary containing:
#                 - url: Elasticsearch server URL
#                 - username: Elasticsearch username (optional)
#                 - password: Elasticsearch password (optional)
#                 - index_name: Name of the index to store logs

#         Raises:
#             ImportError: If elasticsearch is not installed
#         """
#         if not ELASTICSEARCH_AVAILABLE:
#             raise ImportError(
#                 "Elasticsearch backend requires elasticsearch. Install it with 'pip install elasticsearch'"
#             )

#         self.config = config
#         self.client = None
#         self.setup(config)

#     def setup(self, config: Dict[str, Any]) -> None:
#         """
#         Set up the async Elasticsearch client.

#         Args:
#             config: Configuration dictionary
#         """
#         # Create client with authentication if provided
#         if "username" in config and "password" in config:
#             self.client = AsyncElasticsearch(
#                 config["url"],
#                 basic_auth=(config["username"], config["password"]),
#             )
#         else:
#             self.client = AsyncElasticsearch(config["url"])

#     def _get_index_name(self) -> str:
#         """
#         Get the index name with date suffix.

#         Returns:
#             Index name with date suffix
#         """
#         return f"{self.config['index_name']}-{time.strftime('%Y.%m.%d')}"

#     def _create_log_entry(self, **kwargs) -> Dict[str, Any]:
#         """
#         Create a standardized log entry.

#         Returns:
#             Dict containing the log entry
#         """
#         return {
#             "@timestamp": time.time(),
#             **kwargs,
#         }

#     async def log_request(self, request_info: Dict[str, Any], response: Any) -> None:
#         """
#         Log a request to Elasticsearch asynchronously.

#         Args:
#             request_info: Dict with request information
#             response: The framework-specific response object
#         """
#         log_entry = self._create_log_entry(
#             level="INFO",
#             ip=request_info.get("ip", "unknown"),
#             method=request_info.get("method", "unknown"),
#             path=request_info.get("path", "unknown"),
#             status_code=self._extract_status_code(response),
#             user_agent=request_info.get("user_agent", "unknown"),
#             event_type="request",
#         )
#         await self.client.index(index=self._get_index_name(), document=log_entry)

#     async def log_blocked_request(
#         self, request_info: Dict[str, Any], block_type: str, reason: str
#     ) -> None:
#         """
#         Log a blocked request to Elasticsearch asynchronously.

#         Args:
#             request_info: Dict with request information
#             block_type: Type of block (IP filter, rate limit, etc.)
#             reason: Reason for blocking
#         """
#         log_entry = self._create_log_entry(
#             level="WARNING",
#             ip=request_info.get("ip", "unknown"),
#             method=request_info.get("method", "unknown"),
#             path=request_info.get("path", "unknown"),
#             block_type=block_type,
#             reason=reason,
#             user_agent=request_info.get("user_agent", "unknown"),
#             event_type="blocked_request",
#         )
#         await self.client.index(index=self._get_index_name(), document=log_entry)

#     async def log_security_event(
#         self, level: str, message: str, extra: Optional[Dict[str, Any]] = None
#     ) -> None:
#         """
#         Log a security event to Elasticsearch asynchronously.

#         Args:
#             level: Log level (INFO, WARNING, ERROR, etc.)
#             message: The log message
#             extra: Additional information to log
#         """
#         log_entry = self._create_log_entry(
#             level=level, message=message, event_type="security_event", **(extra or {})
#         )
#         await self.client.index(index=self._get_index_name(), document=log_entry)

#     def _extract_status_code(self, response: Any) -> int:
#         """
#         Extract status code from a response object.

#         Args:
#             response: The framework-specific response object

#         Returns:
#             The status code or 0 if not found
#         """
#         try:
#             if hasattr(response, "status_code"):
#                 return response.status_code
#             if isinstance(response, dict) and "status_code" in response:
#                 return response["status_code"]
#         except:
#             pass
#         return 0

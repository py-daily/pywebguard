# """
# MongoDB logging backend for PyWebGuard.
# """

# import time
# import logging
# from typing import Dict, Any, Optional, TYPE_CHECKING

# # Try to import pymongo
# try:
#     from pymongo import MongoClient, AsyncMongoClient

#     PYMONGO_AVAILABLE = True
# except ImportError:
#     PYMONGO_AVAILABLE = False
#     if TYPE_CHECKING:
#         from pymongo import MongoClient, AsyncMongoClient

# from ..base import LoggingBackend, AsyncLoggingBackend


# class MongoDBBackend(LoggingBackend):
#     """
#     Synchronous MongoDB logging backend implementation.
#     """

#     def __init__(self, config: Dict[str, Any]):
#         """
#         Initialize the MongoDB backend.

#         Args:
#             config: Configuration dictionary containing:
#                 - uri: MongoDB connection URI
#                 - database: Database name
#                 - collection: Collection name
#                 - username: Optional username for authentication
#                 - password: Optional password for authentication

#         Raises:
#             ImportError: If pymongo is not installed
#         """
#         if not PYMONGO_AVAILABLE:
#             raise ImportError(
#                 "MongoDB backend requires pymongo. Install it with 'pip install pymongo'"
#             )

#         self.config = config
#         self.client = None
#         self.collection = None
#         self.setup(config)

#     def setup(self, config: Dict[str, Any]) -> None:
#         """
#         Set up the MongoDB client and collection.

#         Args:
#             config: Configuration dictionary
#         """
#         # Build connection URI if not provided
#         if "uri" not in config:
#             auth_str = ""
#             if "username" in config and "password" in config:
#                 auth_str = f"{config['username']}:{config['password']}@"
#             config["uri"] = f"mongodb://{auth_str}{config['host']}:{config['port']}"

#         self.client = MongoClient(config["uri"])
#         db = self.client[config["database"]]
#         self.collection = db[config["collection"]]

#         # Create indexes for efficient querying
#         self.collection.create_index("timestamp")
#         self.collection.create_index("level")
#         self.collection.create_index("ip")
#         self.collection.create_index("event_type")
#         self.collection.create_index([("timestamp", -1)])

#     def _create_log_entry(self, **kwargs) -> Dict[str, Any]:
#         """
#         Create a standardized log entry.

#         Returns:
#             Dict containing the log entry
#         """
#         return {"timestamp": int(time.time() * 1000), **kwargs}  # milliseconds

#     def log_request(self, request_info: Dict[str, Any], response: Any) -> None:
#         """
#         Log a request to MongoDB.

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
#         self.collection.insert_one(log_entry)

#     def log_blocked_request(
#         self, request_info: Dict[str, Any], block_type: str, reason: str
#     ) -> None:
#         """
#         Log a blocked request to MongoDB.

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
#         self.collection.insert_one(log_entry)

#     def log_security_event(
#         self, level: str, message: str, extra: Optional[Dict[str, Any]] = None
#     ) -> None:
#         """
#         Log a security event to MongoDB.

#         Args:
#             level: Log level (INFO, WARNING, ERROR, etc.)
#             message: The log message
#             extra: Additional information to log
#         """
#         log_entry = self._create_log_entry(
#             level=level, message=message, event_type="security_event", **(extra or {})
#         )
#         self.collection.insert_one(log_entry)

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


# class AsyncMongoDBBackend(AsyncLoggingBackend):
#     """
#     Asynchronous MongoDB logging backend implementation.
#     """

#     def __init__(self, config: Dict[str, Any]):
#         """
#         Initialize the async MongoDB backend.

#         Args:
#             config: Configuration dictionary containing:
#                 - uri: MongoDB connection URI
#                 - database: Database name
#                 - collection: Collection name
#                 - username: Optional username for authentication
#                 - password: Optional password for authentication

#         Raises:
#             ImportError: If pymongo is not installed
#         """
#         if not PYMONGO_AVAILABLE:
#             raise ImportError(
#                 "MongoDB backend requires pymongo. Install it with 'pip install pymongo'"
#             )

#         self.config = config
#         self.client = None
#         self.collection = None
#         self.setup(config)

#     def setup(self, config: Dict[str, Any]) -> None:
#         """
#         Set up the async MongoDB client and collection.

#         Args:
#             config: Configuration dictionary
#         """
#         # Build connection URI if not provided
#         if "uri" not in config:
#             auth_str = ""
#             if "username" in config and "password" in config:
#                 auth_str = f"{config['username']}:{config['password']}@"
#             config["uri"] = f"mongodb://{auth_str}{config['host']}:{config['port']}"

#         self.client = AsyncMongoClient(config["uri"])
#         db = self.client[config["database"]]
#         self.collection = db[config["collection"]]

#         # Create indexes for efficient querying
#         self.collection.create_index("timestamp")
#         self.collection.create_index("level")
#         self.collection.create_index("ip")
#         self.collection.create_index("event_type")
#         self.collection.create_index([("timestamp", -1)])

#     def _create_log_entry(self, **kwargs) -> Dict[str, Any]:
#         """
#         Create a standardized log entry.

#         Returns:
#             Dict containing the log entry
#         """
#         return {"timestamp": int(time.time() * 1000), **kwargs}  # milliseconds

#     async def log_request(self, request_info: Dict[str, Any], response: Any) -> None:
#         """
#         Log a request to MongoDB asynchronously.

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
#         await self.collection.insert_one(log_entry)

#     async def log_blocked_request(
#         self, request_info: Dict[str, Any], block_type: str, reason: str
#     ) -> None:
#         """
#         Log a blocked request to MongoDB asynchronously.

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
#         await self.collection.insert_one(log_entry)

#     async def log_security_event(
#         self, level: str, message: str, extra: Optional[Dict[str, Any]] = None
#     ) -> None:
#         """
#         Log a security event to MongoDB asynchronously.

#         Args:
#             level: Log level (INFO, WARNING, ERROR, etc.)
#             message: The log message
#             extra: Additional information to log
#         """
#         log_entry = self._create_log_entry(
#             level=level, message=message, event_type="security_event", **(extra or {})
#         )
#         await self.collection.insert_one(log_entry)

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

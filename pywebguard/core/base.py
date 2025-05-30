"""
Base classes for PyWebGuard with both sync and async support.

This module provides the core Guard classes that handle security features
for both synchronous and asynchronous web applications. It includes:
- IP filtering
- User agent filtering
- Rate limiting
- Penetration detection
- CORS handling
- Logging

Classes:
    RequestProtocol: Protocol defining the minimum required attributes for a request object
    ResponseProtocol: Protocol defining the minimum required attributes for a response object
    Guard: Base Guard class for synchronous web applications
    AsyncGuard: Base Guard class for asynchronous web applications
"""

import os
from typing import List, Optional, Dict, Any, Union, Type, Protocol, TypeVar, cast
from datetime import datetime

from pywebguard.core.config import GuardConfig, RateLimitConfig
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage
from pywebguard.storage.memory import MemoryStorage, AsyncMemoryStorage

# Conditional imports to handle optional dependencies
try:
    from pywebguard.storage._redis import RedisStorage, AsyncRedisStorage

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

    # Create dummy classes for type checking
    class RedisStorage(BaseStorage):
        pass

    class AsyncRedisStorage(AsyncBaseStorage):
        pass


try:
    from pywebguard.storage._sqlite import SQLiteStorage, AsyncSQLiteStorage

    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

    # Create dummy classes for type checking
    class SQLiteStorage(BaseStorage):
        pass

    class AsyncSQLiteStorage(AsyncBaseStorage):
        pass


try:
    from pywebguard.storage._tinydb import TinyDBStorage, AsyncTinyDBStorage

    TINYDB_AVAILABLE = True
except ImportError:
    TINYDB_AVAILABLE = False

    # Create dummy classes for type checking
    class TinyDBStorage(BaseStorage):
        pass

    class AsyncTinyDBStorage(AsyncBaseStorage):
        pass


try:
    from pywebguard.storage._mongodb import MongoDBStorage, AsyncMongoDBStorage

    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

    # Create dummy classes for type checking
    class MongoDBStorage(BaseStorage):
        pass

    class AsyncMongoDBStorage(AsyncBaseStorage):
        pass


try:
    from pywebguard.storage._postgresql import PostgreSQLStorage, AsyncPostgreSQLStorage

    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

    # Create dummy classes for type checking
    class PostgreSQLStorage(BaseStorage):
        pass

    class AsyncPostgreSQLStorage(AsyncBaseStorage):
        pass


from pywebguard.filters.ip_filter import IPFilter, AsyncIPFilter
from pywebguard.filters.user_agent import UserAgentFilter, AsyncUserAgentFilter
from pywebguard.limiters.rate_limit import RateLimiter, AsyncRateLimiter
from pywebguard.security.penetration import (
    PenetrationDetector,
    AsyncPenetrationDetector,
)
from pywebguard.security.cors import CORSHandler, AsyncCORSHandler
from pywebguard.logging.logger import SecurityLogger, AsyncSecurityLogger


class RequestProtocol(Protocol):
    """Protocol defining the minimum required attributes for a request object."""

    remote_addr: str
    user_agent: str
    method: str
    path: str
    query_string: str
    headers: Dict[str, str]


class ResponseProtocol(Protocol):
    """Protocol defining the minimum required attributes for a response object."""

    status_code: int
    headers: Dict[str, str]


class Guard:
    """
    Base Guard class that handles security features (synchronous).

    This is the main class that users will interact with for synchronous
    web applications. It provides a unified interface for all security
    features including IP filtering, rate limiting, and more.

    Attributes:
        config: The GuardConfig instance containing all security settings
        storage: The storage backend for persistent data
        ip_filter: IP filtering component
        user_agent_filter: User agent filtering component
        rate_limiter: Rate limiting component
        penetration_detector: Penetration detection component
        cors_handler: CORS handling component
        logger: Security logging component
    """

    def __init__(
        self,
        config: Optional[GuardConfig] = None,
        storage: Optional[BaseStorage] = None,
        route_rate_limits: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Initialize the Guard with configuration and storage.

        Args:
            config: GuardConfig object with security settings. If None, default config is used.
            storage: Storage backend for persistent data. If None, storage is determined from config.
            route_rate_limits: List of dictionaries with route-specific rate limits.
                Each dict should have: endpoint, requests_per_minute, burst_size, auto_ban_threshold (optional)

        Raises:
            ImportError: If the required storage backend is not installed
        """
        # Use environment variables if no config is provided
        if config is None:
            config = GuardConfig.from_env()
        self.config = config

        # Initialize storage
        if storage is not None:
            self.storage = storage
        else:
            self.storage = self._create_storage_from_config()

        # Initialize components based on config
        self._initialize_components()

        # Add route-specific rate limits if provided
        if route_rate_limits:
            self.add_route_rate_limits(route_rate_limits)

    def _create_storage_from_config(self) -> BaseStorage:
        """
        Create a storage backend based on configuration.

        Returns:
            BaseStorage: The storage backend instance

        Raises:
            ImportError: If the required storage backend is not installed
            ValueError: If the storage type is invalid
        """
        storage_type = self.config.storage.type.lower()

        if storage_type == "memory":
            return MemoryStorage()

        elif storage_type == "redis":
            if not REDIS_AVAILABLE:
                raise ImportError(
                    "Redis storage is not available. Install it with 'pip install pywebguard[redis]'"
                )
            return RedisStorage(
                url=self.config.storage.url or "redis://localhost:6379/0",
                prefix=self.config.storage.prefix,
                ttl=self.config.storage.ttl,
            )

        elif storage_type == "sqlite":
            if not SQLITE_AVAILABLE:
                raise ImportError(
                    "SQLite storage is not available. Install it with 'pip install pywebguard[sqlite]'"
                )
            return SQLiteStorage(
                db_path=self.config.storage.url or "pywebguard.db",
                table_prefix=self.config.storage.prefix,
                ttl=self.config.storage.ttl,
            )

        elif storage_type == "tinydb":
            if not TINYDB_AVAILABLE:
                raise ImportError(
                    "TinyDB storage is not available. Install it with 'pip install pywebguard[tinydb]'"
                )
            return TinyDBStorage(
                db_path=self.config.storage.url or "pywebguard.json",
                ttl=self.config.storage.ttl,
            )

        elif storage_type == "mongodb":
            if not MONGODB_AVAILABLE:
                raise ImportError(
                    "MongoDB storage is not available. Install it with 'pip install pywebguard[mongodb]'"
                )
            return MongoDBStorage(
                url=self.config.storage.url or "mongodb://localhost:27017/pywebguard",
                collection_name=self.config.storage.table_name,
                ttl=self.config.storage.ttl,
            )

        elif storage_type == "postgresql":
            if not POSTGRESQL_AVAILABLE:
                raise ImportError(
                    "PostgreSQL storage is not available. Install it with 'pip install pywebguard[postgresql]'"
                )
            return PostgreSQLStorage(
                url=self.config.storage.url
                or "postgresql://postgres:postgres@localhost:5432/pywebguard",
                table_name=self.config.storage.table_name,
                ttl=self.config.storage.ttl,
            )

        else:
            raise ValueError(f"Invalid storage type: {storage_type}")

    def _initialize_components(self) -> None:
        """
        Initialize all security components based on configuration.

        This method sets up all the security components (IP filter, rate limiter,
        etc.) using the configuration provided during initialization.
        """
        self.ip_filter = IPFilter(self.config.ip_filter, self.storage)
        self.user_agent_filter = UserAgentFilter(self.config.user_agent, self.storage)
        self.rate_limiter = RateLimiter(self.config.rate_limit, self.storage)
        self.penetration_detector = PenetrationDetector(
            self.config.penetration, self.storage
        )
        self.cors_handler = CORSHandler(self.config.cors)
        self.logger = SecurityLogger(self.config.logging)

    def add_route_rate_limit(
        self, route_pattern: str, config: Union[RateLimitConfig, Dict[str, Any]]
    ) -> None:
        """
        Add a custom rate limit configuration for a specific route pattern.

        Args:
            route_pattern: The route pattern to match (can include wildcards like * and **)
            config: Custom rate limit configuration for this route
        """
        self.rate_limiter.add_route_config(route_pattern, config)

    def add_route_rate_limits(self, route_configs: List[Dict[str, Any]]) -> None:
        """
        Add multiple custom rate limit configurations for specific route patterns.

        Args:
            route_configs: List of dictionaries with route-specific rate limits.
                Each dict should have: endpoint, requests_per_minute, burst_size, auto_ban_threshold (optional)
        """
        for config in route_configs:
            # Make a deep copy of the config to prevent mutation
            config_copy = {k: v for k, v in config.items()}
            if (
                "endpoint" not in config_copy
                or "requests_per_minute" not in config_copy
            ):
                self.logger.logger.warning(
                    f"Skipping invalid route config: {config_copy}"
                )
                continue
            endpoint = config_copy.pop("endpoint")
            self.add_route_rate_limit(endpoint, config_copy)

    def check_request(self, request: RequestProtocol) -> Dict[str, Any]:
        """
        Check if a request should be allowed based on security rules.

        This method performs all security checks in sequence:
        1. IP filtering
        2. User agent filtering
        3. Rate limiting
        4. Penetration detection

        Args:
            request: The framework-specific request object

        Returns:
            Dict with status and details about the request check:
            {
                "allowed": bool,
                "details": {
                    "type": str,  # Type of check that failed (if any)
                    "reason": str  # Reason for failure (if any)
                }
            }
        """
        # Extract request information
        request_info = self._extract_request_info(request)

        # Check IP filter
        ip_result = self.ip_filter.is_allowed(request_info["ip"])
        if not ip_result["allowed"]:
            self.logger.log_blocked_request(
                request_info, "IP filter", ip_result["reason"]
            )
            return {
                "allowed": False,
                "details": {"type": "IP filter", "reason": ip_result["reason"]},
            }

        # Check user agent filter
        ua_result = self.user_agent_filter.is_allowed(
            request_info["user_agent"], request_info["path"]
        )
        if not ua_result["allowed"]:
            self.logger.log_blocked_request(
                request_info, "User agent filter", ua_result["reason"]
            )
            return {
                "allowed": False,
                "details": {"type": "User agent filter", "reason": ua_result["reason"]},
            }

        # Check rate limit (now with path for route-specific rate limiting)
        rate_result = self.rate_limiter.check_limit(
            request_info["ip"], request_info["path"]
        )
        if not rate_result["allowed"]:
            self.logger.log_blocked_request(
                request_info, "Rate limit", rate_result["reason"]
            )
            return {
                "allowed": False,
                "details": {"type": "Rate limit", "reason": rate_result["reason"]},
            }

        # Check for penetration attempts
        pen_result = self.penetration_detector.check_request(request_info)
        if not pen_result["allowed"]:
            self.logger.log_blocked_request(
                request_info, "Penetration detection", pen_result["reason"]
            )
            return {
                "allowed": False,
                "details": {
                    "type": "Penetration detection",
                    "reason": pen_result["reason"],
                },
            }

        # All checks passed
        return {"allowed": True, "details": {}}

    def update_metrics(
        self, request: RequestProtocol, response: ResponseProtocol
    ) -> None:
        """
        Update metrics based on request and response.

        This method is called after a request has been processed to update
        various metrics and logs.

        Args:
            request: The framework-specific request object
            response: The framework-specific response object
        """
        # Extract request information
        request_info = self._extract_request_info(request)

        # Log the request
        self.logger.log_request(request_info, response)

    def _extract_request_info(
        self, request: Union[RequestProtocol, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract information from a request object.

        This method should be overridden by framework-specific implementations
        to properly extract request information from the framework's request object.

        Args:
            request: The framework-specific request object or a dictionary with request info

        Returns:
            Dict with request information:
            {
                "ip": str,
                "user_agent": str,
                "method": str,
                "path": str,
                "query": Dict[str, str],
                "headers": Dict[str, str]
            }
        """
        if isinstance(request, dict):
            return request

        # Parse query string into a dictionary
        query_dict = {}
        if hasattr(request, "query_string") and request.query_string:
            query_dict = dict(
                pair.split("=")
                for pair in request.query_string.split("&")
                if "=" in pair
            )

        return {
            "ip": getattr(request, "remote_addr", ""),
            "user_agent": getattr(request, "user_agent", ""),
            "method": getattr(request, "method", ""),
            "path": getattr(request, "path", ""),
            "query": query_dict,
            "headers": getattr(request, "headers", {}),
        }

    def is_ip_banned(self, ip: str) -> bool:
        """Return True if the IP is banned, else False."""
        result = self.ip_filter.is_allowed(ip)
        return not result["allowed"] and result["reason"] == "IP is banned"

    def check_rate_limit(self, ip: str, path: str = None) -> Dict[str, Any]:
        """Check if the request is allowed by the rate limiter."""
        return self.rate_limiter.check_limit(ip, path)


class AsyncGuard:
    """
    Base Guard class that handles security features (asynchronous).

    This is the main class that users will interact with for asynchronous
    web applications. It provides a unified interface for all security
    features including IP filtering, rate limiting, and more.

    Attributes:
        config: The GuardConfig instance containing all security settings
        storage: The async storage backend for persistent data
        ip_filter: Async IP filtering component
        user_agent_filter: Async user agent filtering component
        rate_limiter: Async rate limiting component
        penetration_detector: Async penetration detection component
        cors_handler: Async CORS handling component
        logger: Async security logging component
    """

    def __init__(
        self,
        config: Optional[GuardConfig] = None,
        storage: Optional[AsyncBaseStorage] = None,
        route_rate_limits: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Initialize the AsyncGuard with configuration and storage.

        Args:
            config: GuardConfig object with security settings. If None, default config is used.
            storage: Async storage backend for persistent data. If None, storage is determined from config.
            route_rate_limits: List of dictionaries with route-specific rate limits.
                Each dict should have: endpoint, requests_per_minute, burst_size, auto_ban_threshold (optional)

        Raises:
            ImportError: If the required storage backend is not installed
        """
        # Use environment variables if no config is provided
        if config is None:
            config = GuardConfig.from_env()
        self.config = config

        # Initialize storage
        if storage is not None:
            self.storage = storage
        else:
            self.storage = self._create_storage_from_config()

        # Initialize components based on config
        self._initialize_components()

        # Add route-specific rate limits if provided
        if route_rate_limits:
            self.add_route_rate_limits(route_rate_limits)

    def _create_storage_from_config(self) -> AsyncBaseStorage:
        """
        Create an async storage backend based on configuration.

        Returns:
            AsyncBaseStorage: The async storage backend instance

        Raises:
            ImportError: If the required storage backend is not installed
            ValueError: If the storage type is invalid
        """
        storage_type = self.config.storage.type.lower()

        if storage_type == "memory":
            return AsyncMemoryStorage()

        elif storage_type == "redis":
            if not REDIS_AVAILABLE:
                raise ImportError(
                    "Redis storage is not available. Install it with 'pip install pywebguard[redis]'"
                )
            return AsyncRedisStorage(
                url=self.config.storage.url or "redis://localhost:6379/0",
                prefix=self.config.storage.prefix,
                ttl=self.config.storage.ttl,
            )

        elif storage_type == "sqlite":
            if not SQLITE_AVAILABLE:
                raise ImportError(
                    "SQLite storage is not available. Install it with 'pip install pywebguard[sqlite]'"
                )
            return AsyncSQLiteStorage(
                db_path=self.config.storage.url or "pywebguard.db",
                table_prefix=self.config.storage.prefix,
                ttl=self.config.storage.ttl,
            )

        elif storage_type == "tinydb":
            if not TINYDB_AVAILABLE:
                raise ImportError(
                    "TinyDB storage is not available. Install it with 'pip install pywebguard[tinydb]'"
                )
            return AsyncTinyDBStorage(
                db_path=self.config.storage.url or "pywebguard.json",
                ttl=self.config.storage.ttl,
            )

        elif storage_type == "mongodb":
            if not MONGODB_AVAILABLE:
                raise ImportError(
                    "MongoDB storage is not available. Install it with 'pip install pywebguard[mongodb]'"
                )
            return AsyncMongoDBStorage(
                url=self.config.storage.url or "mongodb://localhost:27017/pywebguard",
                collection_name=self.config.storage.table_name,
                ttl=self.config.storage.ttl,
            )

        elif storage_type == "postgresql":
            if not POSTGRESQL_AVAILABLE:
                raise ImportError(
                    "PostgreSQL storage is not available. Install it with 'pip install pywebguard[postgresql]'"
                )
            return AsyncPostgreSQLStorage(
                url=self.config.storage.url
                or "postgresql://postgres:postgres@localhost:5432/pywebguard",
                table_name=self.config.storage.table_name,
                ttl=self.config.storage.ttl,
            )

        else:
            raise ValueError(f"Invalid storage type: {storage_type}")

    def _initialize_components(self) -> None:
        """
        Initialize all security components based on configuration.

        This method sets up all the security components (IP filter, rate limiter,
        etc.) using the configuration provided during initialization.
        """
        self.ip_filter = AsyncIPFilter(self.config.ip_filter, self.storage)
        self.user_agent_filter = AsyncUserAgentFilter(
            self.config.user_agent, self.storage
        )
        self.rate_limiter = AsyncRateLimiter(self.config.rate_limit, self.storage)
        self.penetration_detector = AsyncPenetrationDetector(
            self.config.penetration, self.storage
        )
        self.cors_handler = AsyncCORSHandler(self.config.cors)
        self.logger = AsyncSecurityLogger(self.config.logging)

    def add_route_rate_limit(
        self, route_pattern: str, config: Union[RateLimitConfig, Dict[str, Any]]
    ) -> None:
        """
        Add a custom rate limit configuration for a specific route pattern.

        Args:
            route_pattern: The route pattern to match (can include wildcards like * and **)
            config: Custom rate limit configuration for this route
        """
        self.rate_limiter.add_route_config(route_pattern, config)

    def add_route_rate_limits(self, route_configs: List[Dict[str, Any]]) -> None:
        """
        Add multiple custom rate limit configurations for specific route patterns.

        Args:
            route_configs: List of dictionaries with route-specific rate limits.
                Each dict should have: endpoint, requests_per_minute, burst_size, auto_ban_threshold (optional)
        """
        for config in route_configs:
            # Make a deep copy of the config to prevent mutation
            config_copy = {k: v for k, v in config.items()}
            if (
                "endpoint" not in config_copy
                or "requests_per_minute" not in config_copy
            ):
                self.logger.logger.warning(
                    f"Skipping invalid route config: {config_copy}"
                )
                continue
            endpoint = config_copy.pop("endpoint")
            self.add_route_rate_limit(endpoint, config_copy)

    async def check_request(self, request: RequestProtocol) -> Dict[str, Any]:
        """
        Check if a request should be allowed based on security rules.

        This method performs all security checks in sequence:
        1. IP filtering
        2. User agent filtering
        3. Rate limiting
        4. Penetration detection

        Args:
            request: The framework-specific request object

        Returns:
            Dict with status and details about the request check:
            {
                "allowed": bool,
                "details": {
                    "type": str,  # Type of check that failed (if any)
                    "reason": str  # Reason for failure (if any)
                }
            }
        """
        # Extract request information
        request_info = self._extract_request_info(request)

        # Check IP filter
        ip_result = await self.ip_filter.is_allowed(request_info["ip"])
        if not ip_result["allowed"]:
            await self.logger.log_blocked_request(
                request_info, "IP filter", ip_result["reason"]
            )
            return {
                "allowed": False,
                "details": {"type": "IP filter", "reason": ip_result["reason"]},
            }

        # Check user agent filter
        ua_result = await self.user_agent_filter.is_allowed(
            request_info["user_agent"], path=request_info["path"]
        )
        if not ua_result["allowed"]:
            await self.logger.log_blocked_request(
                request_info, "User agent filter", ua_result["reason"]
            )
            return {
                "allowed": False,
                "details": {"type": "User agent filter", "reason": ua_result["reason"]},
            }

        # Check rate limit (now with path for route-specific rate limiting)
        rate_result = await self.rate_limiter.check_limit(
            request_info["ip"], request_info["path"]
        )
        if not rate_result["allowed"]:
            await self.logger.log_blocked_request(
                request_info, "Rate limit", rate_result["reason"]
            )
            return {
                "allowed": False,
                "details": {"type": "Rate limit", "reason": rate_result["reason"]},
            }

        # Check for penetration attempts
        pen_result = await self.penetration_detector.check_request(request_info)
        if not pen_result["allowed"]:
            await self.logger.log_blocked_request(
                request_info, "Penetration detection", pen_result["reason"]
            )
            return {
                "allowed": False,
                "details": {
                    "type": "Penetration detection",
                    "reason": pen_result["reason"],
                },
            }

        # All checks passed
        return {"allowed": True, "details": {}}

    async def update_metrics(
        self, request: RequestProtocol, response: ResponseProtocol
    ) -> None:
        """
        Update metrics based on request and response.

        This method is called after a request has been processed to update
        various metrics and logs.

        Args:
            request: The framework-specific request object
            response: The framework-specific response object
        """
        # Extract request information
        request_info = self._extract_request_info(request)

        # Log the request
        await self.logger.log_request(request_info, response)

    def _extract_request_info(
        self, request: Union[RequestProtocol, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract information from a request object.

        This method should be overridden by framework-specific implementations
        to properly extract request information from the framework's request object.

        Args:
            request: The framework-specific request object or a dictionary with request info

        Returns:
            Dict with request information:
            {
                "ip": str,
                "user_agent": str,
                "method": str,
                "path": str,
                "query": Dict[str, str],
                "headers": Dict[str, str]
            }
        """
        if isinstance(request, dict):
            return request

        # Parse query string into a dictionary
        query_dict = {}
        if hasattr(request, "query_string") and request.query_string:
            query_dict = dict(
                pair.split("=")
                for pair in request.query_string.split("&")
                if "=" in pair
            )

        return {
            "ip": getattr(request, "remote_addr", ""),
            "user_agent": getattr(request, "user_agent", ""),
            "method": getattr(request, "method", ""),
            "path": getattr(request, "path", ""),
            "query": query_dict,
            "headers": getattr(request, "headers", {}),
        }

    async def is_ip_banned(self, ip: str) -> bool:
        """Return True if the IP is banned, else False (async)."""
        result = await self.ip_filter.is_allowed(ip)
        return not result["allowed"] and result["reason"] == "IP is banned"

    async def check_rate_limit(self, ip: str, path: str = None) -> Dict[str, Any]:
        """Check if the request is allowed by the rate limiter (async)."""
        return await self.rate_limiter.check_limit(ip, path)

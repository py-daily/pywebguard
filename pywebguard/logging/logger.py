"""
Logging functionality for PyWebGuard.
"""

import logging
import json
import time
from typing import Dict, Any, Optional, List, Union
from pywebguard.core.config import LoggingConfig
from .base import LoggingBackend, AsyncLoggingBackend
from .backends import MeilisearchBackend, AsyncMeilisearchBackend


class SecurityLogger:
    """
    Log security events.
    """

    def __init__(self, config: LoggingConfig):
        """
        Initialize the security logger.

        Args:
            config: Logging configuration
        """
        self.config = config
        self.logger = self._setup_logger()
        self.backends: List[LoggingBackend] = self._setup_backends()

    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger.

        Returns:
            Configured logger
        """
        logger = logging.getLogger("pywebguard")

        # Ensure logs propagate to root logger
        logger.propagate = self.config.propagate

        # Set log level
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)

        # Clear existing handlers
        logger.handlers = []

        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Add file handler if configured
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        return logger

    def _setup_backends(self) -> List[LoggingBackend]:
        """
        Set up logging backends based on configuration.

        Returns:
            List of configured logging backends
        """
        backends = []

        # Add Meilisearch backend if configured
        if hasattr(self.config, "meilisearch") and self.config.meilisearch:
            backends.append(MeilisearchBackend(self.config.meilisearch))

        return backends

    def _sanitize_for_json(self, obj):
        if isinstance(obj, dict):
            return {k: self._sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_for_json(v) for v in obj]
        elif isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        else:
            return str(obj)

    def log_request(self, request_info: Dict[str, Any], response: Any) -> None:
        """
        Log a request.

        Args:
            request_info: Dict with request information
            response: The framework-specific response object
        """
        if not self.config.enabled:
            return

        # Extract response status code
        status_code = self._extract_status_code(response)

        # Create log entry
        log_entry = {
            "timestamp": time.time(),
            "ip": request_info.get("ip", "unknown"),
            "method": request_info.get("method", "unknown"),
            "path": request_info.get("path", "unknown"),
            "status_code": status_code,
            "user_agent": request_info.get("user_agent", "unknown"),
        }

        # Log to console/file
        self.logger.info(f"Request: {json.dumps(self._sanitize_for_json(log_entry))}")

        # Log to backends
        for backend in self.backends:
            try:
                backend.log_request(request_info, response)
            except Exception as e:
                self.logger.error(f"Failed to log request to backend: {str(e)}")

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
        if not self.config.enabled:
            return

        # Create log entry
        log_entry = {
            "timestamp": time.time(),
            "ip": request_info.get("ip", "unknown"),
            "method": request_info.get("method", "unknown"),
            "path": request_info.get("path", "unknown"),
            "block_type": block_type,
            "reason": reason,
            "user_agent": request_info.get("user_agent", "unknown"),
        }

        # Log to console/file
        self.logger.warning(
            f"Blocked request: {json.dumps(self._sanitize_for_json(log_entry))}"
        )
        # Log to backends
        for backend in self.backends:
            try:
                backend.log_blocked_request(request_info, block_type, reason)
            except Exception as e:
                self.logger.error(f"Failed to log blocked request to backend: {str(e)}")

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
        if not self.config.enabled:
            return

        # Log to console/file
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message, extra=extra)
        # Log to backends
        for backend in self.backends:
            try:
                backend.log_security_event(level, message, extra)
            except Exception as e:
                self.logger.error(f"Failed to log security event to backend: {str(e)}")

    def _extract_status_code(self, response: Any) -> int:
        """
        Extract status code from a response object.

        Args:
            response: The framework-specific response object

        Returns:
            The status code or 0 if not found
        """
        try:
            # Try to get status code as an attribute
            if hasattr(response, "status_code"):
                return response.status_code

            # Try to get status code as a dict key
            if isinstance(response, dict) and "status_code" in response:
                return response["status_code"]
        except:
            pass

        return 0


class AsyncSecurityLogger:
    """
    Log security events asynchronously.
    """

    def __init__(self, config: LoggingConfig):
        """
        Initialize the security logger.

        Args:
            config: Logging configuration
        """
        self.config = config
        self.logger = self._setup_logger()
        self.backends: List[AsyncLoggingBackend] = self._setup_backends()

    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger.

        Returns:
            Configured logger
        """
        logger = logging.getLogger("pywebguard")

        # Ensure logs propagate to root logger
        logger.propagate = True

        # Set log level
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)

        # Clear existing handlers
        logger.handlers = []

        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Add file handler if configured
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        return logger

    def _setup_backends(self) -> List[AsyncLoggingBackend]:
        """
        Set up logging backends based on configuration.

        Returns:
            List of configured logging backends
        """
        backends = []

        # Add Meilisearch backend if configured
        if hasattr(self.config, "meilisearch") and self.config.meilisearch:
            backends.append(AsyncMeilisearchBackend(self.config.meilisearch))

        return backends

    def _sanitize_for_json(self, obj):
        if isinstance(obj, dict):
            return {k: self._sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_for_json(v) for v in obj]
        elif isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        else:
            return str(obj)

    async def log_request(self, request_info: Dict[str, Any], response: Any) -> None:
        """
        Log a request asynchronously.

        Args:
            request_info: Dict with request information
            response: The framework-specific response object
        """
        if not self.config.enabled:
            return

        # Extract response status code
        status_code = self._extract_status_code(response)

        # Create log entry
        log_entry = {
            "timestamp": time.time(),
            "ip": request_info.get("ip", "unknown"),
            "method": request_info.get("method", "unknown"),
            "path": request_info.get("path", "unknown"),
            "status_code": status_code,
            "user_agent": request_info.get("user_agent", "unknown"),
        }

        # Log to console/file
        self.logger.info(f"Request: {json.dumps(self._sanitize_for_json(log_entry))}")
        # Log to backends
        for backend in self.backends:
            try:
                await backend.log_request(request_info, response)
            except Exception as e:
                self.logger.error(f"Failed to log request to backend: {str(e)}")

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
        if not self.config.enabled:
            return

        # Create log entry
        log_entry = {
            "timestamp": time.time(),
            "ip": request_info.get("ip", "unknown"),
            "method": request_info.get("method", "unknown"),
            "path": request_info.get("path", "unknown"),
            "block_type": block_type,
            "reason": reason,
            "user_agent": request_info.get("user_agent", "unknown"),
        }

        # Log to console/file
        self.logger.warning(
            f"Blocked request: {json.dumps(self._sanitize_for_json(log_entry))}"
        )
        # Log to backends
        for backend in self.backends:
            try:
                await backend.log_blocked_request(request_info, block_type, reason)
            except Exception as e:
                self.logger.error(f"Failed to log blocked request to backend: {str(e)}")

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
        if not self.config.enabled:
            return

        # Log to console/file
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message, extra=extra)
        # Log to backends
        for backend in self.backends:
            try:
                await backend.log_security_event(level, message, extra)
            except Exception as e:
                self.logger.error(f"Failed to log security event to backend: {str(e)}")

    def _extract_status_code(self, response: Any) -> int:
        """
        Extract status code from a response object.

        Args:
            response: The framework-specific response object

        Returns:
            The status code or 0 if not found
        """
        try:
            # Try to get status code as an attribute
            if hasattr(response, "status_code"):
                return response.status_code

            # Try to get status code as a dict key
            if isinstance(response, dict) and "status_code" in response:
                return response["status_code"]
        except:
            pass

        return 0

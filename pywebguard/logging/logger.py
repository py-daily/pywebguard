"""
Logging functionality for PyWebGuard.
"""

import logging
import json
import time
from typing import Dict, Any, Optional
from pywebguard.core.config import LoggingConfig


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

    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger.

        Returns:
            Configured logger
        """
        logger = logging.getLogger("pywebguard")

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

        # Log the entry
        self.logger.info(f"Request: {json.dumps(log_entry)}")

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

        # Log the entry
        self.logger.warning(f"Blocked request: {json.dumps(log_entry)}")

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

    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger.

        Returns:
            Configured logger
        """
        logger = logging.getLogger("pywebguard")

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

        # Log the entry
        self.logger.info(f"Request: {json.dumps(log_entry)}")

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

        # Log the entry
        self.logger.warning(f"Blocked request: {json.dumps(log_entry)}")

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

"""
CORS handling functionality for PyWebGuard.
"""

from typing import Any, Dict
from pywebguard.core.config import CORSConfig


class CORSHandler:
    """
    Handle CORS headers for requests.
    """

    def __init__(self, config: CORSConfig):
        """
        Initialize the CORS handler.

        Args:
            config: CORS configuration
        """
        self.config = config

    def add_cors_headers(self, request: Any, response: Any) -> None:
        """
        Add CORS headers to a response.

        Args:
            request: The framework-specific request object
            response: The framework-specific response object
        """
        if not self.config.enabled:
            return

        # Extract origin from request
        origin = self._get_origin(request)

        # Set CORS headers
        self._set_cors_headers(response, origin)

    def _get_origin(self, request: Any) -> str:
        """
        Get the origin from a request.

        Args:
            request: The framework-specific request object

        Returns:
            The origin header value or "*"
        """
        # This is a generic implementation that should be overridden
        # by framework-specific implementations
        try:
            # Try to get headers as a dict
            headers = getattr(request, "headers", {})
            if isinstance(headers, dict):
                return headers.get("Origin", "*")

            # Try to get headers as an object with get method
            if hasattr(headers, "get"):
                return headers.get("Origin", "*")
        except:
            pass

        return "*"

    def _set_cors_headers(self, response: Any, origin: str) -> None:
        """
        Set CORS headers on a response.

        Args:
            response: The framework-specific response object
            origin: The origin to allow
        """
        # This is a generic implementation that should be overridden
        # by framework-specific implementations
        try:
            # Check if origin is allowed
            allowed_origin = "*"
            if origin != "*" and self.config.allow_origins != ["*"]:
                if origin in self.config.allow_origins:
                    allowed_origin = origin
                else:
                    # Check for wildcard domains
                    for allowed in self.config.allow_origins:
                        if allowed.startswith("*.") and origin.endswith(allowed[1:]):
                            allowed_origin = origin
                            break

            # Set headers
            headers = {
                "Access-Control-Allow-Origin": allowed_origin,
                "Access-Control-Allow-Methods": ", ".join(self.config.allow_methods),
                "Access-Control-Allow-Headers": ", ".join(self.config.allow_headers),
                "Access-Control-Max-Age": str(self.config.max_age),
            }

            if self.config.allow_credentials:
                headers["Access-Control-Allow-Credentials"] = "true"

            # Try to set headers on response
            if hasattr(response, "headers"):
                for key, value in headers.items():
                    response.headers[key] = value
        except:
            pass


class AsyncCORSHandler:
    """
    Handle CORS headers for requests asynchronously.
    """

    def __init__(self, config: CORSConfig):
        """
        Initialize the CORS handler.

        Args:
            config: CORS configuration
        """
        self.config = config

    async def add_cors_headers(self, request: Any, response: Any) -> None:
        """
        Add CORS headers to a response asynchronously.

        Args:
            request: The framework-specific request object
            response: The framework-specific response object
        """
        if not self.config.enabled:
            return

        # Extract origin from request
        origin = self._get_origin(request)

        # Set CORS headers
        self._set_cors_headers(response, origin)

    def _get_origin(self, request: Any) -> str:
        """
        Get the origin from a request.

        Args:
            request: The framework-specific request object

        Returns:
            The origin header value or "*"
        """
        # This is a generic implementation that should be overridden
        # by framework-specific implementations
        try:
            # Try to get headers as a dict
            headers = getattr(request, "headers", {})
            if isinstance(headers, dict):
                return headers.get("Origin", "*")

            # Try to get headers as an object with get method
            if hasattr(headers, "get"):
                return headers.get("Origin", "*")
        except:
            pass

        return "*"

    def _set_cors_headers(self, response: Any, origin: str) -> None:
        """
        Set CORS headers on a response.

        Args:
            response: The framework-specific response object
            origin: The origin to allow
        """
        # This is a generic implementation that should be overridden
        # by framework-specific implementations
        try:
            # Check if origin is allowed
            allowed_origin = "*"
            if origin != "*" and self.config.allow_origins != ["*"]:
                if origin in self.config.allow_origins:
                    allowed_origin = origin
                else:
                    # Check for wildcard domains
                    for allowed in self.config.allow_origins:
                        if allowed.startswith("*.") and origin.endswith(allowed[1:]):
                            allowed_origin = origin
                            break

            # Set headers
            headers = {
                "Access-Control-Allow-Origin": allowed_origin,
                "Access-Control-Allow-Methods": ", ".join(self.config.allow_methods),
                "Access-Control-Allow-Headers": ", ".join(self.config.allow_headers),
                "Access-Control-Max-Age": str(self.config.max_age),
            }

            if self.config.allow_credentials:
                headers["Access-Control-Allow-Credentials"] = "true"

            # Try to set headers on response
            if hasattr(response, "headers"):
                for key, value in headers.items():
                    response.headers[key] = value
        except:
            pass

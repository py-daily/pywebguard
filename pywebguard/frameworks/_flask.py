"""
Flask integration for PyWebGuard.

This module provides an extension for integrating PyWebGuard with Flask applications.
It handles request interception, security checks, and response processing.

Classes:
    FlaskGuard: Flask extension for PyWebGuard
"""

from typing import Optional, Callable, Dict, Any, List, Union, cast
from functools import wraps

# Check if Flask is installed
try:
    from flask import Flask, request, Response, g, jsonify

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

    # Create dummy classes for type checking
    class Flask:
        pass

    class Response:
        pass


from pywebguard.core.base import Guard
from pywebguard.core.config import GuardConfig
from pywebguard.storage.base import BaseStorage


class FlaskGuard:
    """
    Flask extension for PyWebGuard.

    This extension integrates PyWebGuard with Flask applications to provide
    security features like IP filtering, rate limiting, and more.
    """

    def __init__(
        self,
        app: Optional[Flask] = None,
        config: Optional[GuardConfig] = None,
        storage: Optional[BaseStorage] = None,
        route_rate_limits: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize the Flask extension.

        Args:
            app: Flask application (optional, can be initialized later with init_app)
            config: GuardConfig object with security settings
            storage: Storage backend for persistent data
            route_rate_limits: List of dictionaries with route-specific rate limits
                Each dict should have: endpoint, requests_per_minute, burst_size, auto_ban_threshold (optional)

        Raises:
            ImportError: If Flask is not installed
        """
        if not FLASK_AVAILABLE:
            raise ImportError(
                "Flask is not installed. Install it with 'pip install pywebguard[flask]' "
                "or 'pip install flask>=2.0.0'"
            )

        self.guard = Guard(
            config=config, storage=storage, route_rate_limits=route_rate_limits
        )
        # Inject the Flask-specific request info extractor
        self.guard._extract_request_info = self._extract_request_info

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initialize the extension with a Flask application.

        Args:
            app: Flask application
        """

        # Register before_request handler
        @app.before_request
        def before_request() -> Optional[Response]:
            """
            Check if request should be allowed before processing.

            Returns:
                Response object if request is blocked, None otherwise
            """
            # Check if request should be allowed
            result = self.guard.check_request(request)

            if not result["allowed"]:
                # Return error response if request is blocked
                return (
                    jsonify(
                        {
                            "detail": "Request blocked by security policy",
                            "reason": result["details"],
                        }
                    ),
                    403,
                )

            return None

        # Register after_request handler
        @app.after_request
        def after_request(response: Response) -> Response:
            """
            Process response after request handling.

            Args:
                response: Flask response object

            Returns:
                Processed response object
            """
            # Update metrics based on request and response
            self.guard.update_metrics(request, response)

            # Add CORS headers if needed
            if self.guard.cors_handler.config.enabled:
                self.guard.cors_handler.add_cors_headers(request, response)

            return response

    def _extract_request_info(self, request) -> Dict[str, Any]:
        """
        Extract information from a Flask request object.

        Args:
            request: The Flask request object

        Returns:
            Dict with request information
        """
        # Get the real IP from headers if available
        client_host = request.remote_addr
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_host = forwarded_for.split(",")[0].strip()

        # Always use the string representation of request.user_agent
        user_agent = str(request.user_agent)

        # Build headers from environ to avoid UserAgent object
        safe_headers = {}
        for k, v in request.environ.items():
            if k.startswith("HTTP_"):
                header = k[5:].replace("_", "-").title()
                safe_headers[header] = str(v)
        # Add Content-Type and Content-Length if present
        if "CONTENT_TYPE" in request.environ:
            safe_headers["Content-Type"] = str(request.environ["CONTENT_TYPE"])
        if "CONTENT_LENGTH" in request.environ:
            safe_headers["Content-Length"] = str(request.environ["CONTENT_LENGTH"])

        request_info = {
            "ip": client_host,
            "user_agent": str(user_agent),
            "method": request.method,
            "path": request.path,
            "query": request.args.to_dict(),
            "headers": safe_headers,
        }
        return self._sanitize_for_json(request_info)

    def _sanitize_for_json(self, obj):
        if isinstance(obj, dict):
            return {k: self._sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_for_json(v) for v in obj]
        elif isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        else:
            return str(obj)

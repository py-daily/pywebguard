"""
Flask integration for PyWebGuard.

This module provides an extension for integrating PyWebGuard with Flask applications.
It handles request interception, security checks, and response processing.

Classes:
    FlaskGuard: Flask extension for PyWebGuard
"""

from typing import Optional, Callable, Dict, Any, List, Union, cast
from functools import wraps
import time

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
        custom_response_handler: Optional[Callable] = None,
    ):
        """
        Initialize the Flask extension.

        Args:
            app: Flask application (optional, can be initialized later with init_app)
            config: GuardConfig object with security settings
            storage: Storage backend for persistent data
            route_rate_limits: List of dictionaries with route-specific rate limits
                Each dict should have: endpoint, requests_per_minute, burst_size, auto_ban_threshold (optional)
            custom_response_handler: Optional custom response handler for blocked requests

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

        # Set up default response handler if none provided
        if custom_response_handler is None:
            custom_response_handler = self._default_response_handler
        self.custom_response_handler = custom_response_handler

        if app is not None:
            self.init_app(app)

    def _default_response_handler(self, request, reason: str) -> Response:
        """
        Default response handler for blocked requests.

        Args:
            request: The Flask request object
            reason: The reason the request was blocked

        Returns:
            A JSON response with details about why the request was blocked
        """
        status_code = 429 if "rate limit" in reason.lower() else 403

        return jsonify({
            "error": "Request blocked",
            "reason": reason,
            "timestamp": time.time(),
            "path": request.path,
            "method": request.method,
        }), status_code

    def init_app(self, app: Flask) -> None:
        """
        Initialize the extension with a Flask application.

        Args:
            app: Flask application
        """
        # Store the guard instance in the app's config
        app.config["PYWEBGUARD"] = self

        # Register before_request handler
        @app.before_request
        def before_request() -> Optional[Response]:
            """
            Check if request should be allowed before processing.

            Returns:
                Response object if request is blocked, None otherwise
            """
            client_ip = request.remote_addr
            user_agent = request.headers.get("user-agent", "")

            # Handle CORS preflight requests
            if request.method == "OPTIONS" and self.guard.config.cors.enabled:
                return None

            # Check if IP is banned first
            is_banned = self.guard.is_ip_banned(client_ip)
            if is_banned:
                ban_info = self.guard.storage.get(f"banned_ip:{client_ip}")
                response = self.custom_response_handler(
                    request,
                    f"IP is banned: {ban_info.get('reason', 'Unknown reason')}",
                )
                # Log blocked request
                request_info = {
                    "ip": client_ip,
                    "method": request.method,
                    "path": request.path,
                    "user_agent": user_agent,
                }
                self.guard.logger.log_blocked_request(
                    request_info,
                    "ip_ban",
                    f"IP is banned: {ban_info.get('reason', 'Unknown reason')}",
                )
                return response

            # Check user agent
            if self.guard.config.user_agent.enabled:
                user_agent_check = self.guard.user_agent_filter.is_allowed(user_agent)
                if not user_agent_check["allowed"]:
                    response = self.custom_response_handler(
                        request, user_agent_check["reason"]
                    )
                    # Log blocked request
                    request_info = {
                        "ip": client_ip,
                        "method": request.method,
                        "path": request.path,
                        "user_agent": user_agent,
                    }
                    self.guard.logger.log_blocked_request(
                        request_info, "user_agent", user_agent_check["reason"]
                    )
                    return response

            # Check rate limits
            rate_info = self.guard.rate_limiter.check_limit(client_ip, request.path)
            if not rate_info["allowed"]:
                response = self.custom_response_handler(request, rate_info["reason"])
                # Log blocked request
                request_info = {
                    "ip": client_ip,
                    "method": request.method,
                    "path": request.path,
                    "user_agent": user_agent,
                }
                self.guard.logger.log_security_event(
                    "WARNING",
                    f"Blocked request: {request.method} {request.path} - {rate_info['reason']}",
                )
                return response

            # Check for penetration attempts
            if self.guard.config.penetration.enabled:
                request_info = {
                    "ip": client_ip,
                    "method": request.method,
                    "path": request.path,
                    "query": request.args.to_dict(),
                    "headers": dict(request.headers),
                    "user_agent": user_agent,
                }
                penetration_check = self.guard.penetration_detector.check_request(
                    request_info
                )
                if not penetration_check["allowed"]:
                    response = self.custom_response_handler(
                        request, penetration_check["reason"]
                    )
                    # Log blocked request
                    self.guard.logger.log_blocked_request(
                        request_info, "penetration", penetration_check["reason"]
                    )
                    return response

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
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = (
                "geolocation=(), microphone=(), camera=()"
            )

            # Add CORS headers if enabled
            if self.guard.config.cors.enabled:
                self.guard.cors_handler.add_cors_headers(request, response)

            # Log successful request
            request_info = {
                "ip": request.remote_addr,
                "method": request.method,
                "path": request.path,
                "user_agent": request.headers.get("user-agent", ""),
            }
            self.guard.logger.log_request(request_info, response)

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

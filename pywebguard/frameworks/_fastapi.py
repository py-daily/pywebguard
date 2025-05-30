"""
FastAPI integration for PyWebGuard.

This module provides middleware for integrating PyWebGuard with FastAPI applications.
It handles request interception, security checks, and response processing.

Classes:
    FastAPIGuard: FastAPI middleware for PyWebGuard
"""

from typing import Callable, Dict, Any, Optional, List, Union
import time

# Check if FastAPI is installed
try:
    from fastapi import FastAPI, Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware
    from fastapi.responses import JSONResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for type checking
    class BaseHTTPMiddleware:
        def __init__(self, app):
            self.app = app

    class Request:
        pass

    class Response:
        pass

    class JSONResponse:
        pass


from pywebguard.core.base import Guard, AsyncGuard
from pywebguard.core.config import GuardConfig
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage
from pywebguard.storage.memory import MemoryStorage, AsyncMemoryStorage


class FastAPIGuard(BaseHTTPMiddleware):
    """
    FastAPI middleware for PyWebGuard supporting both sync and async guards.
    """

    def __init__(
        self,
        app,
        config: Optional[GuardConfig] = None,
        storage: Optional[Union[AsyncBaseStorage, BaseStorage]] = None,
        route_rate_limits: Optional[List[Dict[str, Any]]] = None,
        custom_response_handler: Optional[Callable] = None,
    ):
        """
        Initialize the FastAPI guard.

        Args:
            app: The FastAPI application
            config: Guard configuration
            storage: Storage backend
            route_rate_limits: Optional list of route-specific rate limits
            custom_response_handler: Optional custom response handler for blocked requests
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError(
                "FastAPI is not installed. Install it with 'pip install pywebguard[fastapi]' "
                "or 'pip install fastapi>=0.68.0 starlette>=0.14.0'"
            )

        super().__init__(app)
        self.app = app

        # Use AsyncGuard instead of Guard
        if isinstance(storage, AsyncBaseStorage):
            self.guard = AsyncGuard(config, storage)
        else:
            raise ValueError(
                "Storage must be an instance of AsyncBaseStorage for FastAPI integration"
            )

        # Add route-specific rate limits if provided
        if route_rate_limits:
            for route in route_rate_limits:
                self.guard.rate_limiter.add_route_config(route["endpoint"], route)

        # Set up default response handler if none provided
        if custom_response_handler is None:
            custom_response_handler = self._default_response_handler
        self.custom_response_handler = custom_response_handler

    async def _default_response_handler(
        self, request: Request, reason: str
    ) -> Response:
        """
        Default response handler for blocked requests.

        Args:
            request: The FastAPI request object
            reason: The reason the request was blocked

        Returns:
            A JSON response with details about why the request was blocked
        """
        status_code = 429 if "rate limit" in reason.lower() else 403

        return JSONResponse(
            status_code=status_code,
            content={
                "error": "Request blocked",
                "reason": reason,
                "timestamp": time.time(),
                "path": request.url.path,
                "method": request.method,
            },
        )

    async def dispatch(self, request: Request, call_next):
        """
        Process the request through the middleware.

        Args:
            request: The FastAPI request object
            call_next: The next middleware/handler in the chain

        Returns:
            The response from the next middleware/handler
        """
        # Store the guard instance in the app's state if not already stored
        if not hasattr(request.app.state, "guard"):
            request.app.state.guard = self

        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")

        # Handle CORS preflight requests
        if request.method == "OPTIONS" and self.guard.config.cors.enabled:
            response = await call_next(request)
            await self.guard.cors_handler.add_cors_headers(request, response)
            return response

        # Check if IP is banned first
        is_banned = await self.guard.is_ip_banned(client_ip)
        if is_banned:
            ban_info = await self.guard.storage.get(f"banned_ip:{client_ip}")
            response = await self.custom_response_handler(
                request,
                f"IP is banned: {ban_info.get('reason', 'Unknown reason')}",
            )
            # Log blocked request
            request_info = {
                "ip": client_ip,
                "method": request.method,
                "path": request.url.path,
                "user_agent": user_agent,
            }
            await self.guard.logger.log_blocked_request(
                request_info,
                "ip_ban",
                f"IP is banned: {ban_info.get('reason', 'Unknown reason')}",
            )
            return response

        # Check user agent
        if self.guard.config.user_agent.enabled:
            user_agent_check = await self.guard.user_agent_filter.is_allowed(
                user_agent, path=request.url.path
            )
            if not user_agent_check["allowed"]:
                response = await self.custom_response_handler(
                    request, user_agent_check["reason"]
                )
                # Log blocked request
                request_info = {
                    "ip": client_ip,
                    "method": request.method,
                    "path": request.url.path,
                    "user_agent": user_agent,
                }
                await self.guard.logger.log_blocked_request(
                    request_info, "user_agent", user_agent_check["reason"]
                )
                return response

        # Check rate limits
        rate_info = await self.guard.rate_limiter.check_limit(
            client_ip, request.url.path
        )
        if not rate_info["allowed"]:
            response = await self.custom_response_handler(request, rate_info["reason"])
            # Log blocked request
            request_info = {
                "ip": client_ip,
                "method": request.method,
                "path": request.url.path,
                "user_agent": user_agent,
            }
            await self.guard.logger.log_security_event(
                "WARNING",
                f"Blocked request: {request.method} {request.url.path} - {rate_info['reason']}",
            )
            return response

        # Check for penetration attempts
        if self.guard.config.penetration.enabled:
            request_info = {
                "ip": client_ip,
                "method": request.method,
                "path": request.url.path,
                "query": dict(request.query_params),
                "headers": dict(request.headers),
                "user_agent": user_agent,
            }
            penetration_check = await self.guard.penetration_detector.check_request(
                request_info
            )
            if not penetration_check["allowed"]:
                response = await self.custom_response_handler(
                    request, penetration_check["reason"]
                )
                # Log blocked request
                await self.guard.logger.log_blocked_request(
                    request_info, "penetration", penetration_check["reason"]
                )
                return response

        # Continue with the request
        response = await call_next(request)

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
            await self.guard.cors_handler.add_cors_headers(request, response)

        # Log successful request
        request_info = {
            "ip": client_ip,
            "method": request.method,
            "path": request.url.path,
            "user_agent": user_agent,
        }
        await self.guard.logger.log_request(request_info, response)

        return response

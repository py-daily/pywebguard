"""
FastAPI integration for PyWebGuard.

This module provides middleware for integrating PyWebGuard with FastAPI applications.
It handles request interception, security checks, and response processing.

Classes:
    FastAPIGuard: FastAPI middleware for PyWebGuard
"""

from typing import Callable, Dict, Any, Optional, List, Union, cast

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


from pywebguard.core.base import AsyncGuard
from pywebguard.core.config import GuardConfig
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage
from pywebguard.storage.memory import AsyncMemoryStorage


class FastAPIGuard(BaseHTTPMiddleware):
    """
    FastAPI middleware for PyWebGuard.

    This middleware intercepts requests to FastAPI applications and applies
    security checks before allowing the request to proceed.
    """

    def __init__(
        self,
        app,
        config: Optional[GuardConfig] = None,
        storage: Optional[Union[AsyncBaseStorage, BaseStorage]] = None,
        route_rate_limits: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize the FastAPI middleware.

        Args:
            app: FastAPI application
            config: GuardConfig object with security settings
            storage: Async storage backend for persistent data
            route_rate_limits: List of dictionaries with route-specific rate limits
                Each dict should have: endpoint, requests_per_minute, burst_size, auto_ban_threshold (optional)

        Raises:
            ImportError: If FastAPI is not installed
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError(
                "FastAPI is not installed. Install it with 'pip install pywebguard[fastapi]' "
                "or 'pip install fastapi>=0.68.0 starlette>=0.14.0'"
            )

        super().__init__(app)
        self.guard = AsyncGuard(
            config=config,
            storage=storage or AsyncMemoryStorage(),
            route_rate_limits=route_rate_limits,
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request through security checks.

        Args:
            request: FastAPI request
            call_next: Function to call the next middleware

        Returns:
            Response object
        """
        # Check if request should be allowed
        result = await self.guard.check_request(request)

        if not result["allowed"]:
            # Return error response if request is blocked
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Request blocked by security policy",
                    "reason": result["details"],
                },
            )

        # Process the request
        response = await call_next(request)

        # Update metrics based on request and response
        await self.guard.update_metrics(request, response)

        # Add CORS headers if needed
        if self.guard.cors_handler.config.enabled:
            await self.guard.cors_handler.add_cors_headers(request, response)

        return response

    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """
        Extract information from a FastAPI request object.

        Args:
            request: The FastAPI request object

        Returns:
            Dict with request information
        """
        client_host = request.client.host if request.client else "0.0.0.0"

        # Get the real IP from headers if available
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_host = forwarded_for.split(",")[0].strip()

        return {
            "ip": client_host,
            "user_agent": request.headers.get("User-Agent", ""),
            "method": request.method,
            "path": request.url.path,
            "query": dict(request.query_params),
            "headers": dict(request.headers),
        }

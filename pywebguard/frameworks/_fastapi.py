"""
FastAPI integration for PyWebGuard.

This module provides middleware for integrating PyWebGuard with FastAPI applications.
It handles request interception, security checks, and response processing.

Classes:
    FastAPIGuard: FastAPI middleware for PyWebGuard
"""

from typing import Callable, Dict, Any, Optional, List, Union, cast
import asyncio
from concurrent.futures import ThreadPoolExecutor

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
        self._executor = ThreadPoolExecutor()
        self.config = config
        self.storage = storage
        self.route_rate_limits = route_rate_limits
        print(
            f"[FastAPIGuard] Initialized with config={config}, storage={storage}, route_rate_limits={route_rate_limits}"
        )

        self._guard_initialized = False
        self._guard_init_args = (config, storage, route_rate_limits)
        # Do not initialize guard here if storage is an async generator
        if not (hasattr(storage, "__anext__") and hasattr(storage, "__aiter__")):
            self._initialize_guard(config, storage, route_rate_limits)

    def _initialize_guard(self, config, storage, route_rate_limits):
        if storage is None:
            self.guard = AsyncGuard(
                config=config,
                storage=AsyncMemoryStorage(),
                route_rate_limits=route_rate_limits,
            )
        elif isinstance(storage, AsyncBaseStorage):
            self.guard = AsyncGuard(
                config=config,
                storage=storage,
                route_rate_limits=route_rate_limits,
            )
        elif isinstance(storage, BaseStorage):
            self.guard = Guard(
                config=config,
                storage=storage,
                route_rate_limits=route_rate_limits,
            )
        self._guard_initialized = True
        print(f"[FastAPIGuard] Created guard: {self.guard}")

    @property
    def _is_async(self):
        guard = getattr(self, "_guard", None)
        from pywebguard.core.base import AsyncGuard

        return isinstance(guard, AsyncGuard)

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

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self._guard_initialized:
            config, storage, route_rate_limits = self._guard_init_args
            if hasattr(storage, "__anext__") and hasattr(storage, "__aiter__"):
                storage_instance = await storage.__anext__()
                storage = storage_instance
            self._initialize_guard(config, storage, route_rate_limits)
        print(f"[FastAPIGuard] dispatch called: {request.method} {request.url.path}")
        try:
            # Get client IP
            client_ip = request.headers.get("X-Forwarded-For", request.client.host)
            print(f"[FastAPIGuard] Client IP: {client_ip}")

            # Check if IP is banned (only for guards that implement it)
            banned = False
            if hasattr(self.guard, "is_ip_banned"):
                is_ip_banned_fn = getattr(self.guard, "is_ip_banned")
                if asyncio.iscoroutinefunction(is_ip_banned_fn):
                    banned = await is_ip_banned_fn(client_ip)
                else:
                    banned = is_ip_banned_fn(client_ip)
            if banned:
                print(f"[FastAPIGuard] IP {client_ip} is banned")
                return JSONResponse(
                    status_code=403,
                    content={"detail": "IP address is banned"},
                )

            # Check rate limits
            if self.guard.config.rate_limit.enabled:
                print(f"[FastAPIGuard] Checking rate limits for {request.url.path}")
                if isinstance(self.guard, AsyncGuard):
                    result = await self.guard.check_rate_limit(
                        client_ip,
                        request.url.path,
                    )
                else:
                    # Run sync guard in thread pool
                    result = await asyncio.get_event_loop().run_in_executor(
                        self._executor,
                        self.guard.check_rate_limit,
                        client_ip,
                        request.url.path,
                    )
                if not result["allowed"]:
                    print(f"[FastAPIGuard] Rate limit exceeded: {result}")
                    return JSONResponse(
                        status_code=403,
                        content={"detail": result["reason"]},
                    )

            # Process request
            response = await call_next(request)
            return response

        except Exception as e:
            print(f"[FastAPIGuard] Error in dispatch: {e}")
            raise

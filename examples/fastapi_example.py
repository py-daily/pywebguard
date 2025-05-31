"""
Example of using PyWebGuard with FastAPI.

This example demonstrates comprehensive integration of PyWebGuard with FastAPI,
including all major features:
- Route-specific rate limiting
- IP filtering
- User agent filtering
- CORS configuration
- Penetration detection
- Metrics and monitoring
- Custom response handling
- Async storage backend

To run this example:
    pip install fastapi uvicorn pywebguard
    python fastapi_example.py
"""

import logging
import sys, os
from dotenv import load_dotenv

load_dotenv()

# Configure root logger first
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True,  # Force reconfiguration of root logger
)

# Now import other modules
from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
from typing import Dict, List, Optional, Union, Any, Callable

# Import PyWebGuard components
from pywebguard import FastAPIGuard, GuardConfig, RateLimitConfig
from pywebguard.storage.memory import AsyncMemoryStorage
from pywebguard.core.config import LoggingConfig

# Uncomment to use Redis storage instead
# from pywebguard.storage.redis import AsyncRedisStorage

# Get logger for this module
logger = logging.getLogger("pywebguard-example")
logger.setLevel(logging.DEBUG)


# Custom response handler for blocked requests
async def custom_response_handler(request: Request, reason: str) -> Response:
    """
    Custom handler for blocked requests.

    Args:
        request: The FastAPI request object
        reason: The reason the request was blocked

    Returns:
        A custom JSON response with details about why the request was blocked
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


# Create FastAPI app
app = FastAPI(
    title="PyWebGuard FastAPI Example",
    description="Example of PyWebGuard integration with FastAPI",
    version="1.0.0",
)

# Configure PyWebGuard
config = GuardConfig(
    ip_filter={
        "enabled": True,
        "whitelist": ["127.0.0.1", "::1"],  # Allow localhost
        "blacklist": [],  # No blacklisted IPs
    },
    rate_limit={
        "enabled": True,
        "requests_per_minute": 60,  # 60 requests per minute
        "burst_size": 10,  # Allow bursts of 10 requests
        "auto_ban_threshold": 100,  # Ban after 100 requests
        "auto_ban_duration": 3600,  # Ban for 1 hour
    },
    user_agent={
        "enabled": True,
        "blocked_agents": ["curl", "wget", "Scrapy"],  # Block common scraping tools
    },
    cors={
        "enabled": True,
        "allow_origins": ["*"],  # Allow all origins for testing
        "allow_methods": ["*"],  # Allow all methods
        "allow_headers": ["*"],  # Allow all headers
    },
    penetration={
        "enabled": True,
        "detect_sql_injection": True,
        "detect_xss": True,
        "detect_path_traversal": True,
    },
    logging={
        "enabled": True,
        "level": "DEBUG",
        "log_blocked_requests": True,
    },
)

# Configure route-specific rate limits
route_rate_limits = [
    {
        "endpoint": "/api/sensitive",
        "requests_per_minute": 10,  # More strict rate limit for sensitive endpoint
        "burst_size": 2,
        "auto_ban_threshold": 20,
        "auto_ban_duration": 7200,  # 2 hours
    }
]

# Initialize storage
storage = AsyncMemoryStorage()

# Uncomment to use Redis storage instead
# storage = AsyncRedisStorage(url="redis://localhost:6379")

# Add PyWebGuard middleware
app.add_middleware(
    FastAPIGuard,
    config=config,
    storage=storage,
    route_rate_limits=route_rate_limits,
)

# Print debug info about route configurations
print("[DEBUG] Route rate limits configuration:")
for route in route_rate_limits:
    print(f"  {route['endpoint']}: {route['requests_per_minute']} req/min")


# Basic routes
@app.get("/")
async def root():
    """Root endpoint with default rate limit"""
    return {"message": "Hello World - Default rate limit (60 req/min)"}


@app.get("/api/sensitive")
async def sensitive_endpoint():
    """Sensitive endpoint with stricter rate limit"""
    return {"message": "This is a sensitive endpoint - Rate limit (10 req/min)"}


@app.get("/api/blocked")
async def blocked_endpoint():
    """This endpoint will be blocked by user agent filter"""
    return {"message": "This endpoint should be blocked for certain user agents"}


@app.get("/protected", tags=["main"])
async def protected(request: Request):
    """Protected endpoint with default rate limit"""
    return {
        "message": "This is a protected endpoint with default rate limit",
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent", "Unknown"),
    }


# Example of a path that might trigger penetration detection
@app.get("/search", tags=["main"])
async def search(q: str):
    """
    Search endpoint that might trigger penetration detection if malicious queries are used

    Args:
        q: Search query

    Returns:
        Search results
    """
    # PyWebGuard will check for SQL injection, XSS, etc. in the query parameter
    return {"results": f"Search results for: {q}"}


# Helper endpoint to check remaining rate limits
@app.get("/rate-limit-status", tags=["helper"])
async def rate_limit_status(request: Request, path: str = "/"):
    """
    Check rate limit status for a specific path

    Args:
        request: The FastAPI request object
        path: The path to check rate limits for (default: /)

    Returns:
        Rate limit information for the specified path
    """
    client_ip = request.client.host

    # Get rate limit info for the specified path
    guard = request.app.state.guard
    rate_info = await guard.guard.rate_limiter.check_limit(client_ip, path)

    return {
        "path": path,
        "allowed": rate_info["allowed"],
        "remaining": rate_info["remaining"],
        "reset": rate_info["reset"],
        "client_ip": client_ip,
    }


# Endpoint to check if an IP is banned
@app.get("/check-ban-status", tags=["helper"])
async def check_ban_status(request: Request, ip: Optional[str] = None):
    """
    Check if an IP is banned

    Args:
        request: The FastAPI request object
        ip: The IP to check (default: client IP)

    Returns:
        Ban status information
    """
    check_ip = ip or request.client.host
    guard = request.app.state.guard
    is_banned = await guard.guard.is_ip_banned(check_ip)

    return {
        "ip": check_ip,
        "is_banned": is_banned,
        "timestamp": time.time(),
    }


# Admin endpoint to get metrics
@app.get("/admin/metrics", tags=["admin"])
async def get_metrics(request: Request):
    """
    Get PyWebGuard metrics

    Args:
        request: The FastAPI request object

    Returns:
        Current metrics from PyWebGuard
    """
    # This would typically be protected by authentication
    guard = request.app.state.guard
    # Get rate limit info for all paths
    rate_limits = {}
    for path in ["/", "/api/sensitive", "/api/blocked"]:
        rate_info = await guard.guard.rate_limiter.check_limit(
            request.client.host, path
        )
        rate_limits[path] = {
            "allowed": rate_info["allowed"],
            "remaining": rate_info["remaining"],
            "reset": rate_info["reset"],
        }

    return {
        "timestamp": time.time(),
        "metrics": {
            "rate_limits": rate_limits,
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent", "Unknown"),
        },
    }


# Admin endpoint to ban an IP
@app.post("/admin/ban-ip", tags=["admin"])
async def ban_ip(request: Request, ip: str, duration: int = 60):
    """
    Ban an IP address

    Args:
        request: The FastAPI request object
        ip: The IP to ban
        duration: Ban duration in seconds (default: 1 hour)

    Returns:
        Ban confirmation
    """
    # This would typically be protected by authentication
    guard = request.app.state.guard
    ban_key = f"banned_ip:{ip}"
    await guard.guard.storage.set(
        ban_key,
        {"reason": "Manually banned via API", "timestamp": time.time()},
        duration,
    )

    return {
        "message": f"IP {ip} banned for {duration} seconds",
        "timestamp": time.time(),
    }


# Admin endpoint to unban an IP
@app.post("/admin/unban-ip", tags=["admin"])
async def unban_ip(request: Request, ip: str):
    """
    Unban an IP address

    Args:
        request: The FastAPI request object
        ip: The IP to unban

    Returns:
        Unban confirmation
    """
    # This would typically be protected by authentication
    guard = request.app.state.guard
    ban_key = f"banned_ip:{ip}"
    await guard.guard.storage.delete(ban_key)

    return {
        "message": f"IP {ip} unbanned",
        "timestamp": time.time(),
    }


if __name__ == "__main__":
    logger.info("Starting PyWebGuard FastAPI example server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

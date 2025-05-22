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

from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import logging
from typing import Dict, List, Optional, Union, Any, Callable

# Import PyWebGuard components
from pywebguard import FastAPIGuard, GuardConfig, RateLimitConfig
from pywebguard.storage.async_memory import AsyncMemoryStorage

# Uncomment to use Redis storage instead
# from pywebguard.storage.async_redis import AsyncRedisStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pywebguard-example")

# Create FastAPI app
app = FastAPI(
    title="PyWebGuard FastAPI Example",
    description="A comprehensive example of PyWebGuard integration with FastAPI",
    version="1.0.0",
)

# Configure PyWebGuard with detailed settings
config = GuardConfig(
    # IP filtering configuration
    ip_filter={
        "enabled": True,
        "whitelist": ["127.0.0.1", "::1", "192.168.1.0/24"],
        "blacklist": ["10.0.0.1", "172.16.0.0/16"],
    },
    # Global rate limiting configuration
    rate_limit={
        "enabled": True,
        "requests_per_minute": 100,
        "burst_size": 20,
        "auto_ban_threshold": 200,
        "auto_ban_duration": 3600,  # 1 hour in seconds
    },
    # User agent filtering
    user_agent={
        "enabled": True,
        "blocked_agents": ["curl/7.*", "wget", "Scrapy", "bot", "Bot"],
    },
    # CORS configuration
    cors={
        "enabled": True,
        "allow_origins": ["http://localhost:3000", "https://example.com"],
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "allow_credentials": True,
        "max_age": 3600,
    },
    # Penetration detection
    penetration={
        "enabled": True,
        "detect_sql_injection": True,
        "detect_xss": True,
        "detect_path_traversal": True,
        "block_suspicious_requests": True,
    },
    # Logging configuration
    logging={
        "enabled": True,
        "level": "INFO",
        "log_blocked_requests": True,
    },
)

# Define route-specific rate limits
route_rate_limits = [
    {
        "endpoint": "/api/limited",
        "requests_per_minute": 5,
        "burst_size": 2,
        "auto_ban_threshold": 10,
        "auto_ban_duration": 1800,  # 30 minutes
    },
    {
        "endpoint": "/api/uploads/*",
        "requests_per_minute": 10,
        "burst_size": 5,
        "auto_ban_duration": 1800,
    },
    {
        "endpoint": "/api/admin/**",
        "requests_per_minute": 20,
        "burst_size": 5,
        "auto_ban_threshold": 50,
        "auto_ban_duration": 7200,  # 2 hours
    },
]

# Initialize storage (async in-memory for this example)
storage = AsyncMemoryStorage()

# Uncomment to use Redis storage instead
# storage = AsyncRedisStorage(
#     host="localhost",
#     port=6379,
#     db=0,
#     password=None,
#     prefix="pywebguard:",
# )


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


# Add PyWebGuard middleware with route-specific rate limits
guard_middleware = FastAPIGuard(
    app,
    config=config,
    storage=storage,
    route_rate_limits=route_rate_limits,
    response_handler=custom_response_handler,
)


# Basic routes
@app.get("/")
async def root():
    """Root endpoint with default rate limit (100 req/min)"""
    return {"message": "Hello World - Default rate limit (100 req/min)"}


@app.get("/api/limited")
async def limited_endpoint():
    """Strictly rate limited endpoint (5 req/min)"""
    return {"message": "This endpoint is strictly rate limited (5 req/min)"}


@app.get("/api/uploads/files")
async def upload_files():
    """File upload endpoint with custom rate limit (10 req/min)"""
    return {"message": "File upload endpoint with custom rate limit (10 req/min)"}


@app.get("/api/admin/dashboard")
async def admin_dashboard():
    """Admin dashboard with custom rate limit (20 req/min)"""
    return {"message": "Admin dashboard with custom rate limit (20 req/min)"}


@app.get("/api/admin/users/list")
async def admin_users():
    """Admin users list with custom rate limit (20 req/min)"""
    return {"message": "Admin users list with custom rate limit (20 req/min)"}


@app.get("/protected")
async def protected(request: Request):
    """Protected endpoint with default rate limit"""
    return {
        "message": "This is a protected endpoint with default rate limit",
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent", "Unknown"),
    }


# Helper endpoint to check remaining rate limits
@app.get("/rate-limit-status")
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
    rate_info = await guard_middleware.guard.rate_limiter.check_limit(client_ip, path)

    return {
        "path": path,
        "allowed": rate_info["allowed"],
        "remaining": rate_info["remaining"],
        "reset": rate_info["reset"],
        "client_ip": client_ip,
    }


# Endpoint to check if an IP is banned
@app.get("/check-ban-status")
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
    is_banned = await guard_middleware.guard.is_ip_banned(check_ip)

    return {
        "ip": check_ip,
        "is_banned": is_banned,
        "timestamp": time.time(),
    }


# Admin endpoint to get metrics
@app.get("/admin/metrics")
async def get_metrics(request: Request):
    """
    Get PyWebGuard metrics

    Args:
        request: The FastAPI request object

    Returns:
        Current metrics from PyWebGuard
    """
    # This would typically be protected by authentication
    metrics = await guard_middleware.guard.get_metrics()

    return {
        "timestamp": time.time(),
        "metrics": metrics,
    }


# Admin endpoint to ban an IP
@app.post("/admin/ban-ip")
async def ban_ip(request: Request, ip: str, duration: int = 3600):
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
    await guard_middleware.guard.ban_ip(ip, duration)

    return {
        "message": f"IP {ip} banned for {duration} seconds",
        "timestamp": time.time(),
    }


# Admin endpoint to unban an IP
@app.post("/admin/unban-ip")
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
    await guard_middleware.guard.unban_ip(ip)

    return {
        "message": f"IP {ip} unbanned",
        "timestamp": time.time(),
    }


# Example of a path that might trigger penetration detection
@app.get("/search")
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


if __name__ == "__main__":
    logger.info("Starting PyWebGuard FastAPI example server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

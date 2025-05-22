"""
Example of using PyWebGuard with FastAPI and MongoDB storage.

This example demonstrates how to use PyWebGuard with FastAPI and MongoDB storage,
including environment variable configuration.

To run this example:
    pip install fastapi uvicorn pywebguard pymongo
    
    # Set environment variables
    export PYWEBGUARD_STORAGE_TYPE=mongodb
    export PYWEBGUARD_STORAGE_URL=mongodb://localhost:27017/pywebguard
    
    python mongodb_example.py
"""

from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import time
import os
import logging
from typing import Dict, List, Optional, Union, Any

# Import PyWebGuard components
from pywebguard import FastAPIGuard, GuardConfig
from pywebguard.storage._mongodb import AsyncMongoDBStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pywebguard-mongodb-example")

# Create FastAPI app
app = FastAPI(
    title="PyWebGuard MongoDB Example",
    description="Example of PyWebGuard with FastAPI and MongoDB storage",
    version="1.0.0",
)

# Load configuration from environment variables
config = GuardConfig.from_env()

# Override with specific settings if needed
config.rate_limit.requests_per_minute = 100
config.rate_limit.burst_size = 20

# Define route-specific rate limits
route_rate_limits = [
    {
        "endpoint": "/api/limited",
        "requests_per_minute": 5,
        "burst_size": 2,
    },
    {
        "endpoint": "/api/admin/*",
        "requests_per_minute": 20,
        "burst_size": 5,
    },
]


# Custom response handler for blocked requests
async def custom_response_handler(request: Request, reason: str) -> Response:
    """Custom handler for blocked requests."""
    status_code = 429 if "rate limit" in reason.lower() else 403

    return JSONResponse(
        status_code=status_code,
        content={
            "error": "Request blocked",
            "reason": reason,
            "timestamp": time.time(),
            "path": request.url.path,
        },
    )


# Initialize PyWebGuard with MongoDB storage
# Note: The storage will be created automatically from environment variables
# if PYWEBGUARD_STORAGE_TYPE and PYWEBGUARD_STORAGE_URL are set
guard_middleware = FastAPIGuard(
    app,
    config=config,
    route_rate_limits=route_rate_limits,
    response_handler=custom_response_handler,
)


# Basic routes
@app.get("/")
async def root():
    """Root endpoint with default rate limit."""
    return {
        "message": "Hello from PyWebGuard with MongoDB storage",
        "storage_type": os.environ.get("PYWEBGUARD_STORAGE_TYPE", "default"),
        "storage_url": os.environ.get("PYWEBGUARD_STORAGE_URL", "default"),
    }


@app.get("/api/limited")
async def limited_endpoint():
    """Strictly rate limited endpoint (5 req/min)."""
    return {"message": "This endpoint is strictly rate limited (5 req/min)"}


@app.get("/api/admin/dashboard")
async def admin_dashboard():
    """Admin dashboard with custom rate limit (20 req/min)."""
    return {"message": "Admin dashboard with custom rate limit (20 req/min)"}


# Helper endpoint to check remaining rate limits
@app.get("/rate-limit-status")
async def rate_limit_status(request: Request, path: str = "/"):
    """Check rate limit status for a specific path."""
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


# Admin endpoint to ban an IP
@app.post("/admin/ban-ip")
async def ban_ip(request: Request, ip: str, duration: int = 3600):
    """Ban an IP address."""
    # This would typically be protected by authentication
    ban_key = f"banned_ip:{ip}"
    await guard_middleware.guard.storage.set(
        ban_key,
        {"reason": "Manually banned via API", "timestamp": time.time()},
        duration,
    )

    return {
        "message": f"IP {ip} banned for {duration} seconds",
        "timestamp": time.time(),
    }


# Admin endpoint to unban an IP
@app.post("/admin/unban-ip")
async def unban_ip(request: Request, ip: str):
    """Unban an IP address."""
    # This would typically be protected by authentication
    ban_key = f"banned_ip:{ip}"
    await guard_middleware.guard.storage.delete(ban_key)

    return {
        "message": f"IP {ip} unbanned",
        "timestamp": time.time(),
    }


if __name__ == "__main__":
    logger.info("Starting PyWebGuard FastAPI example with MongoDB storage...")
    logger.info(f"Storage type: {os.environ.get('PYWEBGUARD_STORAGE_TYPE', 'default')}")
    logger.info(f"Storage URL: {os.environ.get('PYWEBGUARD_STORAGE_URL', 'default')}")
    uvicorn.run(app, host="0.0.0.0", port=8000)

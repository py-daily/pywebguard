# PyWebGuard
[![PyPI version](https://badge.fury.io/py/pywebguard.svg)](https://badge.fury.io/py/pywebguard)
[![Python Versions](https://img.shields.io/pypi/pyversions/pywebguard.svg)](https://pypi.org/project/pywebguard/)
[![License](https://img.shields.io/github/license/py-daily/pywebguard.svg)](https://github.com/py-daily/pywebguard/blob/main/LICENSE)

A comprehensive security library for Python web applications, providing middleware for IP filtering, rate limiting, and other security features with both synchronous and asynchronous support.

For detailed installation instructions and configuration options, see [Installation Guide](docs/installation.md).

## Key Features

- **IP Whitelisting and Blacklisting**: Control access based on IP addresses
- **User Agent Filtering**: Block requests from specific user agents
- **Rate Limiting**: Limit the number of requests from a single IP
  - **Per-Route Rate Limiting**: Set different rate limits for different endpoints
  - **Bulk Configuration**: Configure rate limits for multiple routes at once
  - **Pattern Matching**: Use wildcards to apply rate limits to groups of routes
- **Automatic IP Banning**: Automatically ban IPs after a certain number of suspicious requests
- **Penetration Attempt Detection**: Detect and log potential penetration attempts
- **Custom Logging**: Log security events to a custom file
- **CORS Configuration**: Configure CORS settings for your web application
- **IP Geolocation**: Determine the country of an IP address
- **Flexible Storage**: Redis-enabled distributed storage, nosql, sql or in-memory storage
- **Async/Sync Support**: Works with both synchronous (Flask) and asynchronous (FastAPI) frameworks
- **Logging Backends**: Configurable logging backends with current support for Meilisearch



## Quick Start

```python
from fastapi import FastAPI
from pywebguard import FastAPIGuard, GuardConfig, RateLimitConfig
from pywebguard.storage.memory import AsyncMemoryStorage
from pywebguard.core.config import LoggingConfig

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
        "blocked_agents": ["curl", "wget", "Scrapy", "bot", "Bot"],
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
        "level": "DEBUG",  # Change to DEBUG to see all messages
        "log_blocked_requests": True,
        "stream": True,
        "stream_levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "meilisearch": {
            "url": "https://meilisearch.dev.pydaily.com",
            "api_key": os.getenv("MEILISEARCH_API_KEY"),
            "index_name": "pywebguard",
        },
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

# Uncomment to use Redis storage instead or import any of the storage supports
# storage = AsyncRedisStorage(url="redis://localhost:6379")


# Add PyWebGuard middleware
app.add_middleware(
    FastAPIGuard,
    config=config,
    storage=storage,
    route_rate_limits=route_rate_limits,
)

 Basic routes
@app.get("/", tags=["main"])
async def root():
    """Root endpoint with default rate limit (100 req/min)"""
    return {"message": "Hello World - Default rate limit (100 req/min)"}


@app.get("/api/limited", tags=["main"])
async def limited_endpoint():
    """Strictly rate limited endpoint (5 req/min)"""
    return {"message": "This endpoint is strictly rate limited (5 req/min)"}


@app.get("/api/uploads/files", tags=["main"])
async def upload_files():
    """File upload endpoint with custom rate limit (10 req/min)"""
    return {"message": "File upload endpoint with custom rate limit (10 req/min)"}


@app.get("/api/admin/dashboard", tags=["main"])
async def admin_dashboard():
    """Admin dashboard with custom rate limit (20 req/min)"""
    return {"message": "Admin dashboard with custom rate limit (20 req/min)"}


@app.get("/api/admin/users/list", tags=["main"])
async def admin_users():
    """Admin users list with custom rate limit (20 req/min)"""
    return {"message": "Admin users list with custom rate limit (20 req/min)"}


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
    for path in ["/", "/api/limited", "/api/uploads/*", "/api/admin/**"]:
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
```


## Documentation
- [Installation Guide](docs/installation.md)
- [CLI Usage](docs/cli.md)
- [Core Features](docs/core/)
- [Framework Integration](docs/frameworks/)
- [Storage Backends](docs/storage/)

## Contributors

<a href="https://github.com/py-daily/pywebguard/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=py-daily/pywebguard" width="80" />
</a>


## License

This project is licensed under the [MIT License](LICENSE).


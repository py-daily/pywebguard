# FastAPI Integration

PyWebGuard provides a middleware for FastAPI that adds security features to your application.

!!! warning
    `FastAPIGuard` currently reads the client IP from `request.client.host` directly — it does
    not look at `X-Forwarded-For` or similar proxy headers. If your app sits behind a reverse
    proxy or load balancer, IP whitelisting/blacklisting and rate limiting will key off the
    proxy's IP, not the real client IP, until this is fixed upstream. (The same is true of
    `FlaskGuard`.)

## Installation

To use PyWebGuard with FastAPI, install the FastAPI extra:

```bash
pip install pywebguard[fastapi]
```

## Short Setup

`FastAPIGuard.install()` adds the middleware with a few flat options:

```python
from fastapi import FastAPI
from pywebguard import FastAPIGuard

app = FastAPI()

FastAPIGuard.install(
    app,
    rate_limit="100/minute",
    route_limits={"/api/limited": "5/minute", "/api/admin/**": "20/minute"},
    blocked_agents=["curl", "wget", "bot"],
    ip_blacklist=["10.0.0.1", "172.16.0.0/16"],
)
```

| Option | Meaning |
|--------|---------|
| `rate_limit` | Default rate, `"<count>/second"` or `"<count>/minute"` |
| `route_limits` | Per-route rates; `*` and `**` patterns work as in `route_rate_limits` |
| `blocked_agents` | User-agent substrings to block |
| `ip_whitelist` / `ip_blacklist` | IPs or CIDR ranges |
| `cors_origins` | Allowed CORS origins |
| `storage` | Async storage backend (in-memory if omitted) |
| `config` | A full `GuardConfig` or dict, instead of the flat options |

- Only rate limiting is on by default. IP filtering, user-agent filtering and CORS turn on when you pass their option; penetration detection stays off. Use `config=` for full control.
- A rate string means exactly that rate (burst is disabled). For burst or auto-ban settings use `route_rate_limits` with `app.add_middleware(...)`.
- Without `storage`, counters and bans live in memory and are per-process. A warning is emitted; use Redis or another shared storage with multiple workers.
- Combining `config=` with the flat options raises a `ValueError`.

## Basic Usage

```python
from fastapi import FastAPI
from pywebguard import FastAPIGuard, GuardConfig

app = FastAPI()

# Configure PyWebGuard
config = GuardConfig(
    ip_filter={"whitelist": ["127.0.0.1"]},
    rate_limit={"requests_per_minute": 100}
)

# Add PyWebGuard middleware (storage defaults to in-memory)
app.add_middleware(FastAPIGuard, config=config)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Configuration

The `FastAPIGuard` middleware accepts the following parameters:

- `app`: The FastAPI application
- `config`: A `GuardConfig` object with security settings
- `storage`: An optional storage backend (defaults to in-memory storage)
- `route_rate_limits`: An optional list of dictionaries with route-specific rate limits
- `custom_response_handler`: An optional async callable `(request, reason: str) -> Response` to
  replace the default JSON error response for blocked requests

### Route-Specific Rate Limits

You can configure different rate limits for specific routes:

```python
route_rate_limits = [
    {
        "endpoint": "/api/limited",
        "requests_per_minute": 5,
        "burst_size": 2,
        "auto_ban_threshold": 10
    },
    {
        "endpoint": "/api/uploads/*",
        "requests_per_minute": 10,
        "burst_size": 5
    },
    {
        "endpoint": "/api/admin/**",
        "requests_per_minute": 20,
        "burst_size": 5,
        "auto_ban_threshold": 50
    }
]

guard = FastAPIGuard(app, config=config, route_rate_limits=route_rate_limits)
```

The endpoint patterns support wildcards:
- `*`: Matches a single path segment
- `**`: Matches any number of path segments

## Custom Storage

You can use a custom storage backend:

```python
from pywebguard import FastAPIGuard, GuardConfig, AsyncRedisStorage

app = FastAPI()

# Configure Redis storage
storage = AsyncRedisStorage(url="redis://localhost:6379/0")

# Add PyWebGuard middleware with Redis storage
guard = FastAPIGuard(app, config=config, storage=storage)
```

## Error Responses

When a request is blocked, PyWebGuard returns a JSON response — status `429` if the block reason
mentions a rate limit, `403` otherwise:

```json
{
  "error": "Request blocked",
  "reason": "Rate limit exceeded",
  "timestamp": 1718030400.123,
  "path": "/api/limited",
  "method": "GET"
}
```

Pass `custom_response_handler` to `FastAPIGuard` if you need a different response shape.

## Complete Example

```python
from fastapi import FastAPI, Request, Depends
from pywebguard import FastAPIGuard, GuardConfig, RateLimitConfig, AsyncRedisStorage

# Create FastAPI app
app = FastAPI(title="PyWebGuard FastAPI Example")

# Configure PyWebGuard
config = GuardConfig(
    ip_filter={"whitelist": ["127.0.0.1", "192.168.1.0/24"]},
    rate_limit={"requests_per_minute": 100, "auto_ban_threshold": 200},
    user_agent={"blocked_agents": ["curl", "wget"]},
    cors={"allow_origins": ["*"], "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]},
)

# Define route-specific rate limits
route_rate_limits = [
    {
        "endpoint": "/api/limited",
        "requests_per_minute": 5,
        "burst_size": 2,
        "auto_ban_threshold": 10
    },
    {
        "endpoint": "/api/uploads/*",
        "requests_per_minute": 10,
        "burst_size": 5
    },
    {
        "endpoint": "/api/admin/**",
        "requests_per_minute": 20,
        "burst_size": 5,
        "auto_ban_threshold": 50
    }
]

# Initialize storage (async Redis for this example)
storage = AsyncRedisStorage(url="redis://localhost:6379/0")

# Add PyWebGuard middleware with route-specific rate limits
guard_middleware = FastAPIGuard(
    app, 
    config=config, 
    storage=storage,
    route_rate_limits=route_rate_limits
)

@app.get("/")
async def root():
    return {"message": "Hello World - Default rate limit (100 req/min)"}

@app.get("/api/limited")
async def limited_endpoint():
    return {"message": "This endpoint is strictly rate limited (5 req/min)"}

@app.get("/api/uploads/files")
async def upload_files():
    return {"message": "File upload endpoint with custom rate limit (10 req/min)"}

@app.get("/api/admin/dashboard")
async def admin_dashboard():
    return {"message": "Admin dashboard with custom rate limit (20 req/min)"}

@app.get("/protected")
async def protected(request: Request):
    return {
        "message": "This is a protected endpoint with default rate limit",
        "client_ip": request.client.host,
    }

# Helper endpoint to check remaining rate limits
@app.get("/rate-limit-status")
async def rate_limit_status(request: Request, path: str = "/"):
    client_ip = request.client.host
    
    # Get rate limit info for the specified path
    rate_info = await guard_middleware.guard.rate_limiter.check_limit(client_ip, path)
    
    return {
        "path": path,
        "allowed": rate_info["allowed"],
        "remaining": rate_info["remaining"],
        "reset": rate_info["reset"],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
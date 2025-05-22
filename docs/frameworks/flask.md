# Flask Integration

PyWebGuard provides an extension for Flask that adds security features to your application.

## Installation

To use PyWebGuard with Flask, install the Flask extra:

```bash
pip install pywebguard[flask]
```

## Basic Usage

```python
from flask import Flask
from pywebguard import FlaskGuard, GuardConfig

app = Flask(__name__)

# Configure PyWebGuard
config = GuardConfig(
    ip_filter={"whitelist": ["127.0.0.1"]},
    rate_limit={"requests_per_minute": 100}
)

# Initialize PyWebGuard
guard = FlaskGuard(app, config=config)

@app.route("/")
def root():
    return {"message": "Hello World"}
```

## Configuration

The `FlaskGuard` extension accepts the following parameters:

- `app`: The Flask application (optional, can be initialized later with `init_app`)
- `config`: A `GuardConfig` object with security settings
- `storage`: An optional storage backend (defaults to in-memory storage)
- `route_rate_limits`: An optional list of dictionaries with route-specific rate limits

### Initialization Patterns

You can initialize the extension in two ways:

1. Pass the Flask app during initialization:

```python
guard = FlaskGuard(app, config=config)
```

2. Initialize later with `init_app`:

```python
guard = FlaskGuard(config=config)
# Later...
guard.init_app(app)
```

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

guard = FlaskGuard(app, config=config, route_rate_limits=route_rate_limits)
```

The endpoint patterns support wildcards:
- `*`: Matches a single path segment
- `**`: Matches any number of path segments

## Custom Storage

You can use a custom storage backend:

```python
from pywebguard import FlaskGuard, GuardConfig
from pywebguard.storage._redis import RedisStorage

app = Flask(__name__)

# Configure Redis storage
storage = RedisStorage(url="redis://localhost:6379/0")

# Initialize PyWebGuard with Redis storage
guard = FlaskGuard(app, config=config, storage=storage)
```

## Error Responses

When a request is blocked by PyWebGuard, a JSON response is returned with a 403 status code:

```json
{
  "detail": "Request blocked by security policy",
  "reason": {
    "type": "Rate limit",
    "reason": "Rate limit exceeded for /api/limited"
  }
}
```

## Complete Example

```python
from flask import Flask, request, jsonify
from pywebguard import FlaskGuard, GuardConfig, RateLimitConfig
from pywebguard.storage._redis import RedisStorage

# Create Flask app
app = Flask(__name__)

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

# Initialize storage (Redis for this example)
storage = RedisStorage(url="redis://localhost:6379/0")

# Initialize PyWebGuard with route-specific rate limits
guard = FlaskGuard(
    app, 
    config=config, 
    storage=storage,
    route_rate_limits=route_rate_limits
)

@app.route("/")
def root():
    return jsonify({"message": "Hello World - Default rate limit (100 req/min)"})

@app.route("/api/limited")
def limited_endpoint():
    return jsonify({"message": "This endpoint is strictly rate limited (5 req/min)"})

@app.route("/api/uploads/files")
def upload_files():
    return jsonify({"message": "File upload endpoint with custom rate limit (10 req/min)"})

@app.route("/api/admin/dashboard")
def admin_dashboard():
    return jsonify({"message": "Admin dashboard with custom rate limit (20 req/min)"})

@app.route("/protected")
def protected():
    return jsonify({
        "message": "This is a protected endpoint with default rate limit",
        "client_ip": request.remote_addr,
    })

# Helper endpoint to check remaining rate limits
@app.route("/rate-limit-status")
def rate_limit_status():
    client_ip = request.remote_addr
    path = request.args.get("path", "/")
    
    # Get rate limit info for the specified path
    rate_info = guard.guard.rate_limiter.check_limit(client_ip, path)
    
    return jsonify({
        "path": path,
        "allowed": rate_info["allowed"],
        "remaining": rate_info["remaining"],
        "reset": rate_info["reset"],
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
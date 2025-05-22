# Guard Classes

PyWebGuard provides two main guard classes: `Guard` for synchronous applications and `AsyncGuard` for asynchronous applications. These classes handle security features like IP filtering, rate limiting, and more.

## Overview

The guard classes are the central components of PyWebGuard. They coordinate various security features and provide a unified interface for checking requests against security rules.

## Guard (Synchronous)

The `Guard` class is designed for synchronous web applications like Flask.

### Basic Usage

```python
from pywebguard import Guard, GuardConfig

# Create a guard with default configuration
guard = Guard()

# Or with custom configuration
config = GuardConfig(
    ip_filter={"whitelist": ["127.0.0.1"]},
    rate_limit={"requests_per_minute": 100}
)
guard = Guard(config=config)

# Check a request
result = guard.check_request(request)
if result["allowed"]:
    # Process the request
    pass
else:
    # Block the request
    reason = result["details"]
    print(f"Request blocked: {reason}")
```

### API Reference

```python
class Guard:
    def __init__(
        self,
        config: Optional[GuardConfig] = None,
        storage: Optional[BaseStorage] = None,
        route_rate_limits: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Initialize the Guard with configuration and storage."""
        
    def add_route_rate_limit(
        self,
        route_pattern: str,
        config: Union[RateLimitConfig, Dict[str, Any]]
    ) -> None:
        """Add a custom rate limit configuration for a specific route pattern."""
        
    def add_route_rate_limits(self, route_configs: List[Dict[str, Any]]) -> None:
        """Add multiple custom rate limit configurations for specific route patterns."""
        
    def check_request(self, request: RequestProtocol) -> Dict[str, Any]:
        """Check if a request should be allowed based on security rules."""
        
    def update_metrics(self, request: RequestProtocol, response: ResponseProtocol) -> None:
        """Update metrics based on request and response."""
```

## AsyncGuard (Asynchronous)

The `AsyncGuard` class is designed for asynchronous web applications like FastAPI.

### Basic Usage

```python
from pywebguard import AsyncGuard, GuardConfig

# Create an async guard with default configuration
guard = AsyncGuard()

# Or with custom configuration
config = GuardConfig(
    ip_filter={"whitelist": ["127.0.0.1"]},
    rate_limit={"requests_per_minute": 100}
)
guard = AsyncGuard(config=config)

# Check a request
result = await guard.check_request(request)
if result["allowed"]:
    # Process the request
    pass
else:
    # Block the request
    reason = result["details"]
    print(f"Request blocked: {reason}")
```

### API Reference

```python
class AsyncGuard:
    def __init__(
        self,
        config: Optional[GuardConfig] = None,
        storage: Optional[AsyncBaseStorage] = None,
        route_rate_limits: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Initialize the AsyncGuard with configuration and storage."""
        
    def add_route_rate_limit(
        self,
        route_pattern: str,
        config: Union[RateLimitConfig, Dict[str, Any]]
    ) -> None:
        """Add a custom rate limit configuration for a specific route pattern."""
        
    def add_route_rate_limits(self, route_configs: List[Dict[str, Any]]) -> None:
        """Add multiple custom rate limit configurations for specific route patterns."""
        
    async def check_request(self, request: RequestProtocol) -> Dict[str, Any]:
        """Check if a request should be allowed based on security rules."""
        
    async def update_metrics(self, request: RequestProtocol, response: ResponseProtocol) -> None:
        """Update metrics based on request and response."""
```

## Security Checks

Both guard classes perform the following security checks in sequence:

1. **IP Filtering**: Check if the request IP is allowed
2. **User Agent Filtering**: Check if the request user agent is allowed
3. **Rate Limiting**: Check if the request exceeds rate limits
4. **Penetration Detection**: Check for suspicious patterns in the request

If any check fails, the request is blocked and the reason is returned.

## Route-Specific Rate Limits

You can configure different rate limits for specific routes:

```python
# Add a single route rate limit
guard.add_route_rate_limit(
    "/api/limited",
    {"requests_per_minute": 5, "burst_size": 2}
)

# Add multiple route rate limits
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
    }
]
guard.add_route_rate_limits(route_rate_limits)
```

The endpoint patterns support wildcards:
- `*`: Matches a single path segment
- `**`: Matches any number of path segments

## Components

The guard classes coordinate the following components:

- **IP Filter**: Filters requests based on IP addresses
- **User Agent Filter**: Filters requests based on user agents
- **Rate Limiter**: Limits request rates
- **Penetration Detector**: Detects potential penetration attempts
- **CORS Handler**: Handles Cross-Origin Resource Sharing
- **Logger**: Logs security events

Each component can be configured through the `GuardConfig` object.

## Example with Custom Storage

```python
from pywebguard import Guard, GuardConfig
from pywebguard.storage._redis import RedisStorage

# Create Redis storage
storage = RedisStorage(url="redis://localhost:6379/0")

# Create guard with Redis storage
guard = Guard(config=GuardConfig(), storage=storage)
```

## Framework Integration

For framework-specific integration, see:

- [FastAPI Integration](../frameworks/fastapi.md)
- [Flask Integration](../frameworks/flask.md)

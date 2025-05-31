# Core API Reference

This document provides detailed information about PyWebGuard's core functionality and API.

## WebGuard

The main class for initializing and configuring PyWebGuard.

```python
from pywebguard import WebGuard

guard = WebGuard(app, config=None)
```

### Parameters

- `app`: The web application instance (Flask, FastAPI, etc.)
- `config`: Optional configuration dictionary

### Methods

#### add_middleware

Add a middleware to the application.

```python
guard.add_middleware(middleware_class, **options)
```

Parameters:
- `middleware_class`: The middleware class to add
- `**options`: Middleware-specific options

#### remove_middleware

Remove a middleware from the application.

```python
guard.remove_middleware(middleware_class)
```

Parameters:
- `middleware_class`: The middleware class to remove

## Middleware Classes

### BaseMiddleware

Base class for all middleware.

```python
from pywebguard import BaseMiddleware

class CustomMiddleware(BaseMiddleware):
    def process_request(self, request):
        return request

    def process_response(self, response):
        return response
```

### RateLimitMiddleware

Rate limiting middleware.

```python
from pywebguard import RateLimitMiddleware

middleware = RateLimitMiddleware(
    requests=100,
    window=3600,
    by_ip=True,
    by_user=False
)
```

Parameters:
- `requests`: Number of requests allowed per window
- `window`: Time window in seconds
- `by_ip`: Whether to limit by IP address
- `by_user`: Whether to limit by authenticated user

### SecurityHeadersMiddleware

Security headers middleware.

```python
from pywebguard import SecurityHeadersMiddleware

middleware = SecurityHeadersMiddleware(
    xss_protection=True,
    content_security_policy=True,
    hsts=True,
    frame_options='DENY'
)
```

Parameters:
- `xss_protection`: Enable XSS protection
- `content_security_policy`: Enable CSP
- `hsts`: Enable HSTS
- `frame_options`: Frame options value

### RequestValidationMiddleware

Request validation middleware.

```python
from pywebguard import RequestValidationMiddleware

middleware = RequestValidationMiddleware(
    validate_json=True,
    max_content_length=1024 * 1024,
    allowed_content_types=['application/json']
)
```

Parameters:
- `validate_json`: Whether to validate JSON
- `max_content_length`: Maximum content length
- `allowed_content_types`: List of allowed content types

## Storage Backends

### MemoryStorage

In-memory storage backend.

```python
from pywebguard import MemoryStorage

storage = MemoryStorage()
```

### RedisStorage

Redis storage backend.

```python
from pywebguard import RedisStorage

storage = RedisStorage(
    host='localhost',
    port=6379,
    db=0
)
```

Parameters:
- `host`: Redis host
- `port`: Redis port
- `db`: Redis database number

## Utilities

### Rate Limiter

Rate limiter utility.

```python
from pywebguard import RateLimiter

limiter = RateLimiter(
    storage=MemoryStorage(),
    requests=100,
    window=3600
)
```

### Request Validator

Request validator utility.

```python
from pywebguard import RequestValidator

validator = RequestValidator(
    max_content_length=1024 * 1024,
    allowed_content_types=['application/json']
)
```

## Error Classes

### WebGuardError

Base error class for PyWebGuard.

```python
from pywebguard import WebGuardError

class CustomError(WebGuardError):
    pass
```

### RateLimitExceeded

Raised when rate limit is exceeded.

```python
from pywebguard import RateLimitExceeded

try:
    # Some code
except RateLimitExceeded:
    # Handle rate limit exceeded
```

### ValidationError

Raised when request validation fails.

```python
from pywebguard import ValidationError

try:
    # Some code
except ValidationError:
    # Handle validation error
```

## Configuration Reference

### Rate Limiting

```python
config = {
    'RATE_LIMIT_ENABLED': True,
    'RATE_LIMIT_REQUESTS': 100,
    'RATE_LIMIT_WINDOW': 3600,
    'RATE_LIMIT_BY_IP': True,
    'RATE_LIMIT_BY_USER': False
}
```

### Security Headers

```python
config = {
    'SECURITY_HEADERS_ENABLED': True,
    'XSS_PROTECTION': True,
    'CONTENT_SECURITY_POLICY': True,
    'HSTS': True,
    'FRAME_OPTIONS': 'DENY'
}
```

### Request Validation

```python
config = {
    'VALIDATE_JSON': True,
    'MAX_CONTENT_LENGTH': 1024 * 1024,
    'ALLOWED_CONTENT_TYPES': ['application/json']
}
```

## Next Steps

- Learn about [Middleware Usage](../guides/middleware.md)
- Explore [Security Features](../guides/api-security.md)
- Check out [Examples](../examples/) 
# Using Middleware

PyWebGuard provides a powerful middleware system that can be used to protect your web applications. This guide explains how to use and customize the middleware.

## Basic Usage

### Flask

```python
from flask import Flask
from pywebguard import WebGuard

app = Flask(__name__)
guard = WebGuard(app)

@app.route('/')
def hello():
    return 'Hello, World!'
```

### FastAPI

```python
from fastapi import FastAPI
from pywebguard import WebGuard

app = FastAPI()
guard = WebGuard(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Available Middleware

### 1. Rate Limiting

```python
from pywebguard import WebGuard, RateLimitMiddleware

guard = WebGuard(app)
guard.add_middleware(RateLimitMiddleware, 
    requests=100,
    window=3600
)
```

### 2. Security Headers

```python
from pywebguard import WebGuard, SecurityHeadersMiddleware

guard = WebGuard(app)
guard.add_middleware(SecurityHeadersMiddleware, 
    xss_protection=True,
    content_security_policy=True
)
```

### 3. Request Filtering

```python
from pywebguard import WebGuard, RequestFilterMiddleware

guard = WebGuard(app)
guard.add_middleware(RequestFilterMiddleware,
    allowed_methods=['GET', 'POST'],
    max_content_length=1024 * 1024  # 1MB
)
```

## Custom Middleware

You can create custom middleware by extending the base middleware class:

```python
from pywebguard import BaseMiddleware

class CustomMiddleware(BaseMiddleware):
    def __init__(self, app, **options):
        super().__init__(app)
        self.options = options

    def process_request(self, request):
        # Process the request
        return request

    def process_response(self, response):
        # Process the response
        return response

# Usage
guard = WebGuard(app)
guard.add_middleware(CustomMiddleware, custom_option=True)
```

## Middleware Order

The order of middleware is important. PyWebGuard processes middleware in the order they are added:

```python
guard = WebGuard(app)
guard.add_middleware(SecurityHeadersMiddleware)  # First
guard.add_middleware(RateLimitMiddleware)       # Second
guard.add_middleware(RequestFilterMiddleware)   # Third
```

## Best Practices

1. **Order Matters**: Add middleware in the correct order
2. **Error Handling**: Always handle exceptions in middleware
3. **Performance**: Keep middleware lightweight
4. **Configuration**: Use configuration for middleware settings

## Common Use Cases

### API Protection

```python
guard = WebGuard(app)
guard.add_middleware(RateLimitMiddleware, requests=1000, window=3600)
guard.add_middleware(SecurityHeadersMiddleware)
guard.add_middleware(RequestFilterMiddleware, allowed_methods=['GET', 'POST'])
```

### Web Application Security

```python
guard = WebGuard(app)
guard.add_middleware(SecurityHeadersMiddleware, 
    xss_protection=True,
    content_security_policy=True,
    hsts=True
)
guard.add_middleware(RequestFilterMiddleware,
    max_content_length=1024 * 1024,
    allowed_content_types=['application/json', 'text/html']
)
```

## Next Steps

- Learn about [API Security](../guides/api-security.md)
- Check the [API Reference](../reference/core.md)
- Explore [Examples](../examples/) 
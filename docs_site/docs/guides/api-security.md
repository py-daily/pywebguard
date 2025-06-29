# API Security

PyWebGuard provides comprehensive security features to protect your API endpoints. This guide covers the security features and best practices.

## Security Features

### 1. Rate Limiting

Protect your API from abuse with rate limiting:

```python
from pywebguard import WebGuard, RateLimitMiddleware

guard = WebGuard(app)
guard.add_middleware(RateLimitMiddleware,
    requests=100,      # requests per window
    window=3600,       # time window in seconds
    by_ip=True,        # limit by IP address
    by_user=True       # limit by authenticated user
)
```

### 2. Security Headers

Add security headers to your responses:

```python
from pywebguard import WebGuard, SecurityHeadersMiddleware

guard = WebGuard(app)
guard.add_middleware(SecurityHeadersMiddleware,
    xss_protection=True,
    content_security_policy=True,
    hsts=True,
    frame_options='DENY'
)
```

### 3. Request Validation

Validate incoming requests:

```python
from pywebguard import WebGuard, RequestValidationMiddleware

guard = WebGuard(app)
guard.add_middleware(RequestValidationMiddleware,
    validate_json=True,
    max_content_length=1024 * 1024,  # 1MB
    allowed_content_types=['application/json']
)
```

## Authentication

### Basic Authentication

```python
from pywebguard import WebGuard, BasicAuthMiddleware

guard = WebGuard(app)
guard.add_middleware(BasicAuthMiddleware,
    username='admin',
    password='secret'
)
```

### JWT Authentication

```python
from pywebguard import WebGuard, JWTAuthMiddleware

guard = WebGuard(app)
guard.add_middleware(JWTAuthMiddleware,
    secret_key='your-secret-key',
    algorithm='HS256'
)
```

## CORS Protection

Configure CORS settings:

```python
from pywebguard import WebGuard, CORSMiddleware

guard = WebGuard(app)
guard.add_middleware(CORSMiddleware,
    allowed_origins=['https://example.com'],
    allowed_methods=['GET', 'POST'],
    allowed_headers=['Content-Type', 'Authorization']
)
```

## Security Best Practices

### 1. Input Validation

- Validate all input data
- Use strong typing
- Sanitize user input
- Implement request size limits

### 2. Authentication & Authorization

- Use strong authentication
- Implement proper session management
- Use secure password hashing
- Implement role-based access control

### 3. Data Protection

- Use HTTPS
- Implement proper encryption
- Secure sensitive data
- Use secure headers

### 4. Error Handling

- Don't expose sensitive information in errors
- Log security events
- Implement proper error responses
- Use custom error handlers

## Example Implementation

Here's a complete example of a secure API setup:

```python
from flask import Flask
from pywebguard import WebGuard, RateLimitMiddleware, SecurityHeadersMiddleware
from pywebguard import RequestValidationMiddleware, JWTAuthMiddleware

app = Flask(__name__)
guard = WebGuard(app)

# Add security middleware
guard.add_middleware(SecurityHeadersMiddleware,
    xss_protection=True,
    content_security_policy=True,
    hsts=True
)

guard.add_middleware(RateLimitMiddleware,
    requests=100,
    window=3600,
    by_ip=True
)

guard.add_middleware(RequestValidationMiddleware,
    validate_json=True,
    max_content_length=1024 * 1024
)

guard.add_middleware(JWTAuthMiddleware,
    secret_key='your-secret-key',
    algorithm='HS256'
)

@app.route('/api/protected')
def protected_route():
    return {'message': 'This is a protected endpoint'}
```

## Security Checklist

- [ ] Implement rate limiting
- [ ] Add security headers
- [ ] Validate all input
- [ ] Use proper authentication
- [ ] Configure CORS
- [ ] Enable HTTPS
- [ ] Implement logging
- [ ] Use secure session management
- [ ] Regular security audits
- [ ] Keep dependencies updated

## Next Steps

- Learn about [Middleware Usage](middleware.md)
- Check the [API Reference](../reference/core.md)
- Explore [Examples](../examples/) 
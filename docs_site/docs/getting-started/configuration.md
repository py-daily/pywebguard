# Configuration

PyWebGuard offers extensive configuration options to customize its behavior according to your needs.

## Configuration Methods

### 1. Environment Variables

You can configure PyWebGuard using environment variables:

```bash
export PYWEBGUARD_RATE_LIMIT_ENABLED=true
export PYWEBGUARD_RATE_LIMIT_REQUESTS=100
export PYWEBGUARD_RATE_LIMIT_WINDOW=3600
export PYWEBGUARD_LOG_LEVEL=INFO
```

### 2. Configuration Dictionary

```python
from pywebguard import WebGuard

config = {
    'RATE_LIMIT_ENABLED': True,
    'RATE_LIMIT_REQUESTS': 100,
    'RATE_LIMIT_WINDOW': 3600,
    'LOG_LEVEL': 'INFO'
}

guard = WebGuard(app, config=config)
```

## Available Settings

### Rate Limiting

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `RATE_LIMIT_ENABLED` | bool | `True` | Enable/disable rate limiting |
| `RATE_LIMIT_REQUESTS` | int | `100` | Number of requests allowed per window |
| `RATE_LIMIT_WINDOW` | int | `3600` | Time window in seconds |

### Security

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `SECURITY_HEADERS_ENABLED` | bool | `True` | Enable security headers |
| `CORS_ENABLED` | bool | `True` | Enable CORS protection |
| `XSS_PROTECTION` | bool | `True` | Enable XSS protection |

### Logging

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `LOG_LEVEL` | str | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | str | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Log format string |

### Storage

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `STORAGE_BACKEND` | str | `memory` | Storage backend (memory, redis, etc.) |
| `STORAGE_URL` | str | `None` | Storage connection URL |

## Framework-Specific Configuration

### Flask

```python
from flask import Flask
from pywebguard import WebGuard

app = Flask(__name__)
app.config['PYWEBGUARD_RATE_LIMIT_ENABLED'] = True
guard = WebGuard(app)
```

### FastAPI

```python
from fastapi import FastAPI
from pywebguard import WebGuard

app = FastAPI()
config = {
    'RATE_LIMIT_ENABLED': True,
    'RATE_LIMIT_REQUESTS': 100
}
guard = WebGuard(app, config=config)
```

## Best Practices

1. **Environment Variables**: Use environment variables for sensitive configuration
2. **Default Values**: Only override settings that differ from defaults
3. **Validation**: Validate configuration values before use
4. **Documentation**: Document your configuration choices

## Next Steps

- Learn about [Middleware Usage](../guides/middleware.md)
- Explore [Security Features](../guides/api-security.md)
- Check the [API Reference](../reference/core.md) 
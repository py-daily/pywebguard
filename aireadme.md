# PyWebGuard

A comprehensive security middleware for Python web applications, providing protection against common web threats with both synchronous and asynchronous support.

[![PyPI version](https://badge.fury.io/py/pywebguard.svg)](https://badge.fury.io/py/pywebguard)
[![Python Versions](https://img.shields.io/pypi/pyversions/pywebguard.svg)](https://pypi.org/project/pywebguard/)
[![License](https://img.shields.io/github/license/pywebguard/pywebguard.svg)](https://github.com/pywebguard/pywebguard/blob/main/LICENSE)

## Features

- **IP Filtering**: Whitelist and blacklist IP addresses and CIDR ranges
- **Rate Limiting**: Protect against brute force and DoS attacks
  - Global and per-route rate limits
  - Burst capacity for handling traffic spikes
  - Automatic IP banning for persistent offenders
- **User Agent Filtering**: Block requests from suspicious user agents
- **Penetration Detection**: Identify and block common attack patterns
  - SQL injection attempts
  - XSS attack vectors
  - Path traversal exploits
  - Common admin path probing
- **CORS Handling**: Configurable Cross-Origin Resource Sharing
- **Comprehensive Logging**: Detailed logging of security events
- **Multiple Storage Backends**:
  - In-memory (default)
  - Redis
  - SQLite
  - TinyDB
  - MongoDB
  - PostgreSQL
- **Framework Integration**:
  - Flask (synchronous)
  - FastAPI (asynchronous)
- **Environment Variable Configuration**: Easy deployment in containerized environments

## Installation

```bash
# Basic installation
pip install pywebguard

# With Redis support
pip install pywebguard[redis]

# With SQLite support
pip install pywebguard[sqlite]

# With TinyDB support
pip install pywebguard[tinydb]

# With MongoDB support
pip install pywebguard[mongodb]

# With PostgreSQL support
pip install pywebguard[postgresql]

# With Flask support
pip install pywebguard[flask]

# With FastAPI support
pip install pywebguard[fastapi]

# Full installation with all dependencies
pip install pywebguard[all]
```

## Quick Start

### Flask Integration

```python
from flask import Flask
from pywebguard import FlaskGuard, GuardConfig

app = Flask(__name__)

# Initialize with default configuration
guard = FlaskGuard(app)

# Or with custom configuration
config = GuardConfig(
    rate_limit={"requests_per_minute": 100, "burst_size": 20},
    ip_filter={"whitelist": ["127.0.0.1", "192.168.1.0/24"]}
)
guard = FlaskGuard(app, config=config)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
```

### FastAPI Integration

```python
from fastapi import FastAPI
from pywebguard import FastAPIGuard, GuardConfig

app = FastAPI()

# Initialize with default configuration
guard = FastAPIGuard(app)

# Or with custom configuration
config = GuardConfig(
    rate_limit={"requests_per_minute": 100, "burst_size": 20},
    ip_filter={"whitelist": ["127.0.0.1", "192.168.1.0/24"]}
)
guard = FastAPIGuard(app, config=config)

@app.get('/')
async def root():
    return {'message': 'Hello World'}
```

## Route-Specific Rate Limiting

You can set different rate limits for different routes:

```python
# Flask example
from flask import Flask
from pywebguard import FlaskGuard

app = Flask(__name__)

# Define route-specific rate limits
route_rate_limits = [
    {
        "endpoint": "/api/login",
        "requests_per_minute": 5,
        "burst_size": 2,
        "auto_ban_threshold": 10
    },
    {
        "endpoint": "/api/public/*",
        "requests_per_minute": 100,
        "burst_size": 20
    },
    {
        "endpoint": "/api/admin/**",
        "requests_per_minute": 20,
        "burst_size": 5
    }
]

# Initialize with route-specific rate limits
guard = FlaskGuard(app, route_rate_limits=route_rate_limits)

@app.route('/api/login')
def login():
    return 'Login page (rate limited to 5 req/min)'

@app.route('/api/public/data')
def public_data():
    return 'Public data (rate limited to 100 req/min)'

@app.route('/api/admin/dashboard')
def admin_dashboard():
    return 'Admin dashboard (rate limited to 20 req/min)'
```

## Storage Backends

PyWebGuard supports multiple storage backends for persistence:

```python
from pywebguard import FlaskGuard, GuardConfig
from pywebguard.storage.redis import RedisStorage

# Redis storage
redis_storage = RedisStorage(url="redis://localhost:6379/0")
guard = FlaskGuard(app, storage=redis_storage)

# Or configure via GuardConfig
config = GuardConfig(
    storage={
        "type": "redis",
        "url": "redis://localhost:6379/0",
        "prefix": "myapp:",
        "ttl": 3600
    }
)
guard = FlaskGuard(app, config=config)
```

## Environment Variable Configuration

PyWebGuard can be configured using environment variables, which is ideal for containerized environments:

```bash
# Set environment variables
export PYWEBGUARD_STORAGE_TYPE=redis
export PYWEBGUARD_STORAGE_URL=redis://localhost:6379/0
export PYWEBGUARD_RATE_LIMIT_RPM=100
export PYWEBGUARD_IP_FILTER_WHITELIST=127.0.0.1,192.168.1.0/24
```

```python
# Configuration will be loaded from environment variables
from flask import Flask
from pywebguard import FlaskGuard

app = Flask(__name__)
guard = FlaskGuard(app)  # No explicit config needed
```

## Docker Integration

PyWebGuard works seamlessly with Docker:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYWEBGUARD_STORAGE_TYPE=redis
ENV PYWEBGUARD_STORAGE_URL=redis://redis:6379/0
ENV PYWEBGUARD_RATE_LIMIT_RPM=100

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
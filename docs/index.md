# PyWebGuard Documentation

PyWebGuard is a comprehensive security library for Python web applications. It provides middleware and utilities for IP filtering, rate limiting, and other security features for FastAPI and Flask with both synchronous and asynchronous support.

## Features

- **IP Filtering**: Block or allow requests based on IP addresses
- **Rate Limiting**: Limit request rates to prevent abuse
- **User Agent Filtering**: Block requests from specific user agents
- **Penetration Detection**: Detect and block potential penetration attempts
- **CORS Handling**: Configure Cross-Origin Resource Sharing
- **Framework Integration**: Ready-to-use middleware for FastAPI and Flask
- **Storage Options**: Multiple storage backends (Memory, Redis, SQLite, TinyDB)
- **Async Support**: Full support for asynchronous web frameworks

## Quick Start

### Installation

```bash
# Install the core package
pip install pywebguard

# Install with FastAPI support
pip install pywebguard[fastapi]

# Install with Flask support
pip install pywebguard[flask]

# Install with Redis storage
pip install pywebguard[redis]

# Install everything
pip install pywebguard[all]
```

### Basic Usage with FastAPI

```python
from fastapi import FastAPI
from pywebguard import FastAPIGuard, GuardConfig

app = FastAPI()

# Configure PyWebGuard
config = GuardConfig(
    ip_filter={"whitelist": ["127.0.0.1"]},
    rate_limit={"requests_per_minute": 100}
)

# Add PyWebGuard middleware
guard = FastAPIGuard(app, config=config)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Basic Usage with Flask

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

## Documentation Contents

- [Installation](installation.md)
- [Command-Line Interface](cli.md)
- Frameworks
  - [FastAPI Integration](frameworks/fastapi.md)
  - [Flask Integration](frameworks/flask.md)
- Storage Backends
  - [Memory Storage](storage/memory.md)
  - [Redis Storage](storage/redis.md)
  - [SQLite Storage](storage/sqlite.md)
  - [TinyDB Storage](storage/tinydb.md)
- Core Components
  - [Guard Classes](core/guard.md)
  - [Configuration](core/config.md)

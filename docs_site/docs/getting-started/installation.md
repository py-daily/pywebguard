# Installation

## Requirements

- Python 3.8 or higher
- A supported web framework (Flask, FastAPI, etc.)

## Installing PyWebGuard

PyWebGuard can be installed with various optional dependencies depending on your needs:

### Basic Installation

```bash
pip install pywebguard
```

### Storage Backends

```bash
pip install pywebguard[redis]
pip install pywebguard[sqlite]
pip install pywebguard[tinydb]
pip install pywebguard[mongodb]
pip install pywebguard[postgresql]
```

### Framework Support

```bash
pip install pywebguard[flask]
pip install pywebguard[fastapi]
```

### Search Engine Support

```bash
pip install pywebguard[meilisearch]
pip install pywebguard[elasticsearch]
```

### Development Dependencies

```bash
pip install pywebguard[test]
pip install pywebguard[format]
```

### Full Installation

To install all optional dependencies:

```bash
pip install pywebguard[all]
```

### Installing from Source

If you want to install from source:

```bash
git clone https://github.com/py-daily/pywebguard.git
cd pywebguard
pip install -e .
```

## Basic Setup

### Flask Integration

```python
from flask import Flask
from pywebguard import WebGuard

app = Flask(__name__)
guard = WebGuard(app)

# Your routes here
@app.route('/')
def hello():
    return 'Hello, World!'
```

### FastAPI Integration

```python
from fastapi import FastAPI
from pywebguard import WebGuard

app = FastAPI()
guard = WebGuard(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Configuration

PyWebGuard can be configured using environment variables or directly in your code:

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

## Next Steps

- Learn about [Configuration](configuration.md) options
- Read the [Middleware Guide](../guides/middleware.md)
- Check out the [API Reference](../reference/core.md) 
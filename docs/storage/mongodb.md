# MongoDB Storage

PyWebGuard provides MongoDB storage backends for both synchronous and asynchronous applications. This storage option is ideal for applications that already use MongoDB or need a scalable, distributed storage solution.

## Installation

To use MongoDB storage, you need to install PyWebGuard with the MongoDB extra:

```bash
pip install pywebguard[mongodb]
```

This will install the required `pymongo` package.

## Configuration

### Environment Variables

The simplest way to configure MongoDB storage is through environment variables:

```bash
# Set storage type to MongoDB
export PYWEBGUARD_STORAGE_TYPE=mongodb

# Set MongoDB connection URL
export PYWEBGUARD_STORAGE_URL=mongodb://localhost:27017/pywebguard

# Optional: Set collection name (default is "pywebguard")
export PYWEBGUARD_STORAGE_TABLE=pywebguard_collection

# Optional: Set TTL in seconds (default is 3600)
export PYWEBGUARD_STORAGE_TTL=3600
```

### Configuration Object

You can also configure MongoDB storage using the `GuardConfig` object:

```python
from pywebguard import GuardConfig

config = GuardConfig(
    storage={
        "type": "mongodb",
        "url": "mongodb://localhost:27017/pywebguard",
        "table_name": "pywebguard_collection",
        "ttl": 3600
    }
)
```

### Direct Initialization

For more control, you can initialize the MongoDB storage directly:

```python
# Synchronous
from pywebguard.storage._mongodb import MongoDBStorage

storage = MongoDBStorage(
    url="mongodb://localhost:27017/pywebguard",
    collection_name="pywebguard_collection",
    ttl=3600
)

# Asynchronous
from pywebguard.storage._mongodb import AsyncMongoDBStorage

storage = AsyncMongoDBStorage(
    url="mongodb://localhost:27017/pywebguard",
    collection_name="pywebguard_collection",
    ttl=3600
)
```

## Usage with FastAPI

```python
from fastapi import FastAPI
from pywebguard import FastAPIGuard, GuardConfig
from pywebguard.storage._mongodb import AsyncMongoDBStorage

app = FastAPI()

# Option 1: Use environment variables
config = GuardConfig.from_env()

# Option 2: Configure directly
config = GuardConfig(
    storage={
        "type": "mongodb",
        "url": "mongodb://localhost:27017/pywebguard",
        "table_name": "pywebguard_collection",
        "ttl": 3600
    }
)

# Option 3: Create storage manually
storage = AsyncMongoDBStorage(
    url="mongodb://localhost:27017/pywebguard",
    collection_name="pywebguard_collection",
    ttl=3600
)

# Initialize with automatic storage creation from config
guard = FastAPIGuard(app, config=config)

# Or initialize with manual storage
guard = FastAPIGuard(app, config=config, storage=storage)
```

## Usage with Flask

```python
from flask import Flask
from pywebguard import FlaskGuard, GuardConfig
from pywebguard.storage._mongodb import MongoDBStorage

app = Flask(__name__)

# Option 1: Use environment variables
config = GuardConfig.from_env()

# Option 2: Configure directly
config = GuardConfig(
    storage={
        "type": "mongodb",
        "url": "mongodb://localhost:27017/pywebguard",
        "table_name": "pywebguard_collection",
        "ttl": 3600
    }
)

# Option 3: Create storage manually
storage = MongoDBStorage(
    url="mongodb://localhost:27017/pywebguard",
    collection_name="pywebguard_collection",
    ttl=3600
)

# Initialize with automatic storage creation from config
guard = FlaskGuard(app, config=config)

# Or initialize with manual storage
guard = FlaskGuard(app, config=config, storage=storage)
```

## Connection URL Format

The MongoDB connection URL follows the standard MongoDB URI format:

```
mongodb://[username:password@]host[:port]/database
```

Examples:
- `mongodb://localhost:27017/pywebguard`
- `mongodb://user:pass@mongodb.example.com:27017/pywebguard`
- `mongodb+srv://user:pass@cluster0.mongodb.net/pywebguard`

## Storage Schema

The MongoDB storage backend creates the following schema:

- Collection: The name specified in `collection_name` (default: "pywebguard")
- Document structure:
  ```json
  {
    "key": "string",
    "value": "any",
    "expires_at": "ISODate",
    "updated_at": "ISODate"
  }
  ```

## Indexes

The MongoDB storage backend creates the following indexes:

1. TTL index on `expires_at` field for automatic document expiration
2. Index on `key` field for faster lookups

## Advanced Configuration

### Connection Pooling

You can pass additional parameters to the MongoDB client:

```python
from pywebguard.storage._mongodb import MongoDBStorage

storage = MongoDBStorage(
    url="mongodb://localhost:27017/pywebguard",
    collection_name="pywebguard_collection",
    ttl=3600,
    maxPoolSize=100,
    minPoolSize=10,
    maxIdleTimeMS=30000
)
```

### Authentication

For authenticated connections:

```python
from pywebguard.storage._mongodb import MongoDBStorage

storage = MongoDBStorage(
    url="mongodb://user:pass@localhost:27017/pywebguard",
    collection_name="pywebguard_collection",
    ttl=3600,
    authSource="admin",
    authMechanism="SCRAM-SHA-256"
)
```

## Performance Considerations

- MongoDB storage is suitable for distributed applications where multiple instances need to share rate limiting data
- The TTL index ensures automatic cleanup of expired data
- For high-traffic applications, consider using a dedicated MongoDB instance or replica set
- The async implementation is recommended for FastAPI applications to avoid blocking the event loop

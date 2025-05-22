# PostgreSQL Storage

PyWebGuard provides PostgreSQL storage backends for both synchronous and asynchronous applications. This storage option is ideal for applications that already use PostgreSQL or need a robust, relational database storage solution.

## Installation

To use PostgreSQL storage, you need to install PyWebGuard with the PostgreSQL extra:

```bash
# For synchronous applications (Flask)
pip install pywebguard[postgresql]

# For asynchronous applications (FastAPI)
pip install pywebguard[postgresql-async]
```

This will install the required packages:
- `psycopg2-binary` for synchronous operations
- `asyncpg` for asynchronous operations

## Configuration

### Environment Variables

The simplest way to configure PostgreSQL storage is through environment variables:

```bash
# Set storage type to PostgreSQL
export PYWEBGUARD_STORAGE_TYPE=postgresql

# Set PostgreSQL connection URL
export PYWEBGUARD_STORAGE_URL=postgresql://postgres:postgres@localhost:5432/pywebguard

# Optional: Set table name (default is "pywebguard")
export PYWEBGUARD_STORAGE_TABLE=pywebguard_table

# Optional: Set TTL in seconds (default is 3600)
export PYWEBGUARD_STORAGE_TTL=3600
```

### Configuration Object

You can also configure PostgreSQL storage using the `GuardConfig` object:

```python
from pywebguard import GuardConfig

config = GuardConfig(
    storage={
        "type": "postgresql",
        "url": "postgresql://postgres:postgres@localhost:5432/pywebguard",
        "table_name": "pywebguard_table",
        "ttl": 3600
    }
)
```

### Direct Initialization

For more control, you can initialize the PostgreSQL storage directly:

```python
# Synchronous
from pywebguard.storage._postgresql import PostgreSQLStorage

storage = PostgreSQLStorage(
    url="postgresql://postgres:postgres@localhost:5432/pywebguard",
    table_name="pywebguard_table",
    ttl=3600
)

# Asynchronous
from pywebguard.storage._postgresql import AsyncPostgreSQLStorage

storage = AsyncPostgreSQLStorage(
    url="postgresql://postgres:postgres@localhost:5432/pywebguard",
    table_name="pywebguard_table",
    ttl=3600
)
```

## Usage with FastAPI

```python
from fastapi import FastAPI
from pywebguard import FastAPIGuard, GuardConfig
from pywebguard.storage._postgresql import AsyncPostgreSQLStorage

app = FastAPI()

# Option 1: Use environment variables
config = GuardConfig.from_env()

# Option 2: Configure directly
config = GuardConfig(
    storage={
        "type": "postgresql",
        "url": "postgresql://postgres:postgres@localhost:5432/pywebguard",
        "table_name": "pywebguard_table",
        "ttl": 3600
    }
)

# Option 3: Create storage manually
storage = AsyncPostgreSQLStorage(
    url="postgresql://postgres:postgres@localhost:5432/pywebguard",
    table_name="pywebguard_table",
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
from pywebguard.storage._postgresql import PostgreSQLStorage

app = Flask(__name__)

# Option 1: Use environment variables
config = GuardConfig.from_env()

# Option 2: Configure directly
config = GuardConfig(
    storage={
        "type": "postgresql",
        "url": "postgresql://postgres:postgres@localhost:5432/pywebguard",
        "table_name": "pywebguard_table",
        "ttl": 3600
    }
)

# Option 3: Create storage manually
storage = PostgreSQLStorage(
    url="postgresql://postgres:postgres@localhost:5432/pywebguard",
    table_name="pywebguard_table",
    ttl=3600
)

# Initialize with automatic storage creation from config
guard = FlaskGuard(app, config=config)

# Or initialize with manual storage
guard = FlaskGuard(app, config=config, storage=storage)
```

## Connection URL Format

The PostgreSQL connection URL follows the standard PostgreSQL URI format:

```
postgresql://[username:password@]host[:port]/database
```

Examples:
- `postgresql://postgres:postgres@localhost:5432/pywebguard`
- `postgresql://user:pass@postgres.example.com:5432/pywebguard`
- `postgresql://user:pass@localhost/pywebguard?sslmode=require`

## Storage Schema

The PostgreSQL storage backend creates the following table schema:

```sql
CREATE TABLE IF NOT EXISTS {table_name} (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

## Indexes

The PostgreSQL storage backend creates the following indexes:

1. Index on `expires_at` field for efficient TTL cleanup
2. Primary key on `key` field for fast lookups

## Advanced Configuration

### Connection Pooling (Async)

For the asynchronous implementation, you can configure connection pooling:

```python
from pywebguard.storage._postgresql import AsyncPostgreSQLStorage

storage = AsyncPostgreSQLStorage(
    url="postgresql://postgres:postgres@localhost:5432/pywebguard",
    table_name="pywebguard_table",
    ttl=3600,
    min_size=5,
    max_size=20
)
```

### SSL Configuration

For secure connections:

```python
from pywebguard.storage._postgresql import PostgreSQLStorage

storage = PostgreSQLStorage(
    url="postgresql://postgres:postgres@localhost:5432/pywebguard?sslmode=require",
    table_name="pywebguard_table",
    ttl=3600
)
```

## Performance Considerations

- PostgreSQL storage is suitable for applications that need ACID compliance and relational database features
- The storage backend automatically cleans up expired entries
- For high-traffic applications, consider optimizing your PostgreSQL server configuration
- The async implementation is recommended for FastAPI applications to avoid blocking the event loop
- Consider adding appropriate indexes if you're storing a large number of entries

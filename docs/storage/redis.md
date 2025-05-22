# Redis Storage

The Redis storage backend provides persistent storage for PyWebGuard using Redis. It's ideal for distributed applications and high-traffic environments.

## Installation

To use Redis storage, install the Redis extra:

```bash
pip install pywebguard[redis]
```

## Features

- Persistent storage across application restarts
- Distributed storage for multiple application instances
- Fast access to stored data
- Automatic expiration of keys (TTL)
- Available in both synchronous and asynchronous versions

## Usage

### Synchronous Usage

```python
from pywebguard import Guard, GuardConfig
from pywebguard.storage._redis import RedisStorage

# Create Redis storage
storage = RedisStorage(
    url="redis://localhost:6379/0",
    prefix="pywebguard:"
)

# Create Guard with Redis storage
guard = Guard(config=GuardConfig(), storage=storage)
```

### Asynchronous Usage

```python
from pywebguard import AsyncGuard, GuardConfig
from pywebguard.storage._redis import AsyncRedisStorage

# Create async Redis storage
storage = AsyncRedisStorage(
    url="redis://localhost:6379/0",
    prefix="pywebguard:"
)

# Create AsyncGuard with async Redis storage
guard = AsyncGuard(config=GuardConfig(), storage=storage)
```

## Configuration

The Redis storage backend accepts the following parameters:

- `url`: Redis connection URL (default: "redis://localhost:6379/0")
- `prefix`: Key prefix for all stored values (default: "pywebguard:")

### Connection URL Format

The Redis connection URL has the following format:

```
redis://[[username]:[password]@][host][:port][/database]
```

Examples:

- `redis://localhost:6379/0` - Connect to localhost on port 6379, database 0
- `redis://user:password@redis.example.com:6379/1` - Connect with authentication
- `redis://redis.example.com:6379` - Connect to a remote Redis server

## API Reference

### RedisStorage

```python
class RedisStorage:
    def __init__(self, url: str = "redis://localhost:6379/0", prefix: str = "pywebguard:"):
        """Initialize the Redis storage."""
        
    def get(self, key: str) -> Optional[Any]:
        """Get a value from storage."""
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in storage with optional TTL in seconds."""
        
    def delete(self, key: str) -> None:
        """Delete a value from storage."""
        
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in storage."""
        
    def exists(self, key: str) -> bool:
        """Check if a key exists in storage."""
        
    def clear(self) -> None:
        """Clear all values from storage with the configured prefix."""
```

### AsyncRedisStorage

```python
class AsyncRedisStorage:
    def __init__(self, url: str = "redis://localhost:6379/0", prefix: str = "pywebguard:"):
        """Initialize the async Redis storage."""
        
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from storage asynchronously."""
        
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in storage asynchronously with optional TTL in seconds."""
        
    async def delete(self, key: str) -> None:
        """Delete a value from storage asynchronously."""
        
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in storage asynchronously."""
        
    async def exists(self, key: str) -> bool:
        """Check if a key exists in storage asynchronously."""
        
    async def clear(self) -> None:
        """Clear all values from storage asynchronously with the configured prefix."""
```

## Data Serialization

The Redis storage backend automatically serializes and deserializes data:

- Simple types (strings, numbers, booleans) are stored as-is
- Complex types (dictionaries, lists, objects) are serialized to JSON

## When to Use

Redis storage is ideal for:

- Production environments
- Distributed applications (multiple instances)
- High-traffic applications
- When you need persistence across restarts
- When you need automatic key expiration

## Example with Configuration

```python
from pywebguard import GuardConfig
from pywebguard.storage._redis import RedisStorage

# Configure storage in GuardConfig
config = GuardConfig(
    storage={
        "type": "redis",
        "redis_url": "redis://localhost:6379/0",
        "redis_prefix": "myapp:",
        "ttl": 3600  # Default TTL for stored values (1 hour)
    }
)

# The Guard will automatically use Redis storage based on the config
from pywebguard import Guard
guard = Guard(config=config)
```

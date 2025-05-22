# Memory Storage

The memory storage backend is the default storage option for PyWebGuard. It stores data in memory, which makes it fast but not persistent across application restarts.

## Features

- Fast access to stored data
- No external dependencies
- Available in both synchronous and asynchronous versions
- Automatic cleanup of expired entries

## Usage

### Synchronous Usage

```python
from pywebguard import Guard, GuardConfig
from pywebguard.storage.memory import MemoryStorage

# Create memory storage
storage = MemoryStorage()

# Create Guard with memory storage
guard = Guard(config=GuardConfig(), storage=storage)
```

### Asynchronous Usage

```python
from pywebguard import AsyncGuard, GuardConfig
from pywebguard.storage.memory import AsyncMemoryStorage

# Create async memory storage
storage = AsyncMemoryStorage()

# Create AsyncGuard with async memory storage
guard = AsyncGuard(config=GuardConfig(), storage=storage)
```

## API Reference

### MemoryStorage

```python
class MemoryStorage:
    def __init__(self) -> None:
        """Initialize the in-memory storage."""
        
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
        """Clear all values from storage."""
```

### AsyncMemoryStorage

```python
class AsyncMemoryStorage:
    def __init__(self) -> None:
        """Initialize the async in-memory storage."""
        
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from storage asynchronously."""
        
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in storage asynchronously with optional TTL in seconds."""
        
    async def delete(self, key: str) -> bool:
        """Delete a value from storage asynchronously."""
        
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in storage asynchronously."""
        
    async def exists(self, key: str) -> bool:
        """Check if a key exists in storage asynchronously."""
        
    async def clear(self) -> None:
        """Clear all values from storage asynchronously."""
```

## Limitations

- Data is not persistent across application restarts
- Not suitable for distributed applications (each instance has its own storage)
- Memory usage increases with the amount of stored data

## When to Use

Memory storage is ideal for:

- Development and testing
- Single-instance applications
- Applications with low to moderate traffic
- When you don't need persistence across restarts

For production environments with high traffic or distributed applications, consider using a persistent storage backend like Redis, SQLite, or TinyDB.

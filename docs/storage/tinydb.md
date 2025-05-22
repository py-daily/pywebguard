# TinyDB Storage

The TinyDB storage backend provides persistent storage for PyWebGuard using TinyDB, a lightweight document-oriented database. It's ideal for small applications that need persistence without the complexity of a full database system.

## Installation

To use TinyDB storage, install the TinyDB extra:

```bash
pip install pywebguard[tinydb]
```

## Features

- Persistent storage across application restarts
- Document-oriented storage (JSON-based)
- No server required (file-based)
- Automatic cleanup of expired entries
- Available in both synchronous and asynchronous versions

## Usage

### Synchronous Usage

```python
from pywebguard import Guard, GuardConfig
from pywebguard.storage._tinydb import TinyDBStorage

# Create TinyDB storage
storage = TinyDBStorage(
    db_path="pywebguard.json",
    table_name="default"
)

# Create Guard with TinyDB storage
guard = Guard(config=GuardConfig(), storage=storage)
```

### Asynchronous Usage

```python
from pywebguard import AsyncGuard, GuardConfig
from pywebguard.storage._tinydb import AsyncTinyDBStorage

# Create async TinyDB storage
storage = AsyncTinyDBStorage(
    db_path="pywebguard.json",
    table_name="default"
)

# Create AsyncGuard with async TinyDB storage
guard = AsyncGuard(config=GuardConfig(), storage=storage)
```

## Configuration

The TinyDB storage backend accepts the following parameters:

- `db_path`: Path to TinyDB JSON file (default: "pywebguard.json")
- `table_name`: Name of the table to store values (default: "default")

## API Reference

### TinyDBStorage

```python
class TinyDBStorage:
    def __init__(self, db_path: str = "pywebguard.json", table_name: str = "default"):
        """Initialize the TinyDB storage."""
        
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

### AsyncTinyDBStorage

```python
class AsyncTinyDBStorage:
    def __init__(self, db_path: str = "pywebguard.json", table_name: str = "default"):
        """Initialize the async TinyDB storage."""
        
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
        """Clear all values from storage asynchronously."""
```

## Data Structure

The TinyDB storage backend stores data in the following format:

```json
{
  "key": "example_key",
  "value": "example_value",
  "expiry": 1609459200
}
```

- `key`: The storage key
- `value`: The stored value (serialized if necessary)
- `expiry`: The expiration timestamp (or null if no expiration)

## Asynchronous Implementation Note

TinyDB is synchronous by nature. The `AsyncTinyDBStorage` class provides an asynchronous interface but runs TinyDB operations in a thread pool to make them non-blocking. This approach works well for most use cases but may not be as efficient as a truly asynchronous database.

## Limitations

- Not suitable for distributed applications (each instance needs its own database)
- Performance may degrade with large amounts of data
- Not optimized for concurrent access

## When to Use

TinyDB storage is ideal for:

- Small to medium-sized applications
- Single-instance applications
- When you need persistence without a database server
- When you prefer a document-oriented approach
- Development and testing environments

For distributed applications or high-traffic environments, consider using Redis storage instead.

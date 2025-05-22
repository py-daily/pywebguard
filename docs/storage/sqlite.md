# SQLite Storage

The SQLite storage backend provides persistent storage for PyWebGuard using SQLite. It's ideal for single-instance applications that need persistence without external dependencies.

## Installation

To use SQLite storage, install the SQLite extra:

```bash
pip install pywebguard[sqlite]
```

## Features

- Persistent storage across application restarts
- No external dependencies (uses Python's built-in sqlite3 module)
- File-based or in-memory storage
- Automatic cleanup of expired entries
- Available in both synchronous and asynchronous versions

## Usage

### Synchronous Usage

```python
from pywebguard import Guard, GuardConfig
from pywebguard.storage._sqlite import SQLiteStorage

# Create SQLite storage (file-based)
storage = SQLiteStorage(
    db_path="pywebguard.db",
    table_name="pywebguard"
)

# Or create in-memory SQLite storage
memory_storage = SQLiteStorage(
    db_path=":memory:",
    table_name="pywebguard"
)

# Create Guard with SQLite storage
guard = Guard(config=GuardConfig(), storage=storage)
```

### Asynchronous Usage

```python
from pywebguard import AsyncGuard, GuardConfig
from pywebguard.storage._sqlite import AsyncSQLiteStorage

# Create async SQLite storage
storage = AsyncSQLiteStorage(
    db_path="pywebguard.db",
    table_name="pywebguard"
)

# Create AsyncGuard with async SQLite storage
guard = AsyncGuard(config=GuardConfig(), storage=storage)
```

## Configuration

The SQLite storage backend accepts the following parameters:

- `db_path`: Path to SQLite database file (default: ":memory:")
- `table_name`: Name of the table to store values (default: "pywebguard")

## API Reference

### SQLiteStorage

```python
class SQLiteStorage:
    def __init__(self, db_path: str = ":memory:", table_name: str = "pywebguard"):
        """Initialize the SQLite storage."""
        
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

### AsyncSQLiteStorage

```python
class AsyncSQLiteStorage:
    def __init__(self, db_path: str = ":memory:", table_name: str = "pywebguard"):
        """Initialize the async SQLite storage."""
        
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

## Data Serialization

The SQLite storage backend automatically serializes and deserializes data:

- Simple types (strings, numbers, booleans) are stored as-is
- Complex types (dictionaries, lists, objects) are serialized to JSON

## Database Schema

The SQLite storage backend creates a table with the following schema:

```sql
CREATE TABLE IF NOT EXISTS {table_name} (
    key TEXT PRIMARY KEY,
    value TEXT,
    expiry REAL
)
```

- `key`: The storage key
- `value`: The stored value (serialized if necessary)
- `expiry`: The expiration timestamp (or NULL if no expiration)

## Limitations

- Not suitable for distributed applications (each instance needs its own database)
- Performance may degrade with large amounts of data
- Concurrent access may cause contention

## When to Use

SQLite storage is ideal for:

- Single-instance applications
- Applications with low to moderate traffic
- When you need persistence without external dependencies
- Development and testing environments

For distributed applications or high-traffic environments, consider using Redis storage instead.

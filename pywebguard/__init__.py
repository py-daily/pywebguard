"""
PyWebGuard - A comprehensive security library for Python web applications.

This package provides middleware and utilities for IP filtering, rate limiting,
and other security features for FastAPI and Flask with both sync and async support.

Features:
- IP filtering: Block or allow requests based on IP addresses
- Rate limiting: Limit request rates to prevent abuse
- User agent filtering: Block requests from specific user agents
- Penetration detection: Detect and block potential penetration attempts
- CORS handling: Configure Cross-Origin Resource Sharing
- Framework integration: Ready-to-use middleware for FastAPI and Flask
- Storage options: Multiple storage backends (Memory, Redis, SQLite, TinyDB)
- Async support: Full support for asynchronous web frameworks
"""

__version__ = "0.1.0"

# Core components (always available)
from pywebguard.core.base import Guard, AsyncGuard
from pywebguard.core.config import GuardConfig, RateLimitConfig
from pywebguard.storage.memory import MemoryStorage, AsyncMemoryStorage

# Optional storage backends - imported conditionally to avoid import errors
# if the required dependencies are not installed
try:
    from pywebguard.storage._redis import RedisStorage, AsyncRedisStorage
except ImportError:
    pass

try:
    from pywebguard.storage._sqlite import SQLiteStorage, AsyncSQLiteStorage
except ImportError:
    pass

try:
    from pywebguard.storage._tinydb import TinyDBStorage, AsyncTinyDBStorage
except ImportError:
    pass

# Framework-specific imports - imported conditionally to avoid import errors
# if the framework is not installed
try:
    import fastapi
    from pywebguard.frameworks._fastapi import FastAPIGuard
except ImportError:
    pass

try:
    import flask
    from pywebguard.frameworks._flask import FlaskGuard
except ImportError:
    pass

# Define what's available in the namespace
__all__ = [
    # Core components
    "Guard",
    "AsyncGuard",
    "GuardConfig",
    "RateLimitConfig",
    "MemoryStorage",
    "AsyncMemoryStorage",
]

# Dynamically add optional components to __all__ if they're available
import sys

current_module = sys.modules[__name__]

# Optional storage backends
for storage_class in [
    "RedisStorage",
    "AsyncRedisStorage",
    "SQLiteStorage",
    "AsyncSQLiteStorage",
    "TinyDBStorage",
    "AsyncTinyDBStorage",
]:
    if hasattr(current_module, storage_class):
        __all__.append(storage_class)

# Framework integrations
for framework_class in ["FastAPIGuard", "FlaskGuard"]:
    if hasattr(current_module, framework_class):
        __all__.append(framework_class)

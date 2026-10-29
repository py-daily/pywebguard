"""Tests for the top-level pywebguard package namespace (pywebguard/__init__.py)."""

import pywebguard


def test_mongodb_storage_exported_from_top_level():
    """MongoDBStorage/AsyncMongoDBStorage should be importable from the top-level package."""
    assert hasattr(pywebguard, "MongoDBStorage")
    assert hasattr(pywebguard, "AsyncMongoDBStorage")
    assert "MongoDBStorage" in pywebguard.__all__
    assert "AsyncMongoDBStorage" in pywebguard.__all__

    from pywebguard import MongoDBStorage, AsyncMongoDBStorage

    from pywebguard.storage._mongodb import (
        MongoDBStorage as _MongoDBStorage,
        AsyncMongoDBStorage as _AsyncMongoDBStorage,
    )

    assert MongoDBStorage is _MongoDBStorage
    assert AsyncMongoDBStorage is _AsyncMongoDBStorage


def test_postgresql_storage_exported_from_top_level():
    """PostgreSQLStorage/AsyncPostgreSQLStorage should be importable from the top-level package."""
    assert hasattr(pywebguard, "PostgreSQLStorage")
    assert hasattr(pywebguard, "AsyncPostgreSQLStorage")
    assert "PostgreSQLStorage" in pywebguard.__all__
    assert "AsyncPostgreSQLStorage" in pywebguard.__all__

    from pywebguard import PostgreSQLStorage, AsyncPostgreSQLStorage

    from pywebguard.storage._postgresql import (
        PostgreSQLStorage as _PostgreSQLStorage,
        AsyncPostgreSQLStorage as _AsyncPostgreSQLStorage,
    )

    assert PostgreSQLStorage is _PostgreSQLStorage
    assert AsyncPostgreSQLStorage is _AsyncPostgreSQLStorage

"""
MongoDB storage backend for PyWebGuard.

This module provides both synchronous and asynchronous MongoDB storage
implementations for PyWebGuard. It requires the pymongo package.
"""

import time
import json
from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timedelta

from pywebguard.storage.base import BaseStorage, AsyncBaseStorage

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.collection import Collection
    from pymongo.errors import DuplicateKeyError
    from pymongo import AsyncMongoClient

    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

    # Create dummy classes for type checking
    class MongoClient:
        pass

    class AsyncMongoClient:
        pass

    class Collection:
        pass


class MongoDBStorage(BaseStorage):
    """
    MongoDB storage backend for PyWebGuard (synchronous).

    This class provides a MongoDB-based storage backend for PyWebGuard.
    It stores data in a MongoDB collection with TTL support.

    Attributes:
        client: MongoDB client instance
        db: MongoDB database instance
        collection: MongoDB collection instance
        ttl: Default TTL for stored data in seconds
    """

    def __init__(
        self,
        url: str = "mongodb://localhost:27017/pywebguard",
        collection_name: str = "pywebguard",
        ttl: int = 3600,
        **kwargs: Any
    ) -> None:
        """
        Initialize MongoDB storage.

        Args:
            url: MongoDB connection URL (mongodb://host:port/database)
            collection_name: Name of the collection to use
            ttl: Default TTL for stored data in seconds
            **kwargs: Additional arguments to pass to MongoClient

        Raises:
            ImportError: If pymongo is not installed
        """
        if not MONGODB_AVAILABLE:
            raise ImportError(
                "MongoDB storage requires pymongo. Install it with 'pip install pymongo'"
            )

        # Parse URL to extract database name
        if "/" in url:
            parts = url.split("/")
            db_name = parts[-1]
            connection_url = "/".join(parts[:-1]) + "/"
        else:
            db_name = "pywebguard"
            connection_url = url

        self.client = MongoClient(connection_url, **kwargs)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.ttl = ttl

        # Create TTL index if it doesn't exist
        self.collection.create_index(
            "expires_at", expireAfterSeconds=0, background=True
        )

        # Create key index for faster lookups
        self.collection.create_index("key", background=True)

    def get(self, key: str) -> Any:
        """
        Get a value from storage.

        Args:
            key: Key to retrieve

        Returns:
            The stored value, or None if the key doesn't exist or has expired
        """
        doc = self.collection.find_one({"key": key})
        if doc and "value" in doc:
            # Check if the document has expired
            if "expires_at" in doc and doc["expires_at"] < datetime.utcnow():
                self.delete(key)
                return None
            return doc["value"]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage.

        Args:
            key: Key to store
            value: Value to store
            ttl: Time-to-live in seconds (None for default)
        """
        expires_at = None
        if ttl is not None and ttl > 0:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        elif self.ttl > 0:
            expires_at = datetime.utcnow() + timedelta(seconds=self.ttl)

        # Use upsert to handle both insert and update
        self.collection.update_one(
            {"key": key},
            {
                "$set": {
                    "key": key,
                    "value": value,
                    "expires_at": expires_at,
                    "updated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )

    def delete(self, key: str) -> None:
        """
        Delete a value from storage.

        Args:
            key: Key to delete
        """
        self.collection.delete_one({"key": key})

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage.

        Args:
            key: Key to check

        Returns:
            True if the key exists and has not expired, False otherwise
        """
        doc = self.collection.find_one(
            {"key": key}, projection={"_id": 1, "expires_at": 1}
        )
        if doc:
            # Check if the document has expired
            if "expires_at" in doc and doc["expires_at"] < datetime.utcnow():
                self.delete(key)
                return False
            return True
        return False

    def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter in storage.

        Args:
            key: Key to increment
            amount: Amount to increment by

        Returns:
            The new value of the counter
        """
        # Check if the key exists and hasn't expired
        if not self.exists(key):
            self.set(key, 0)

        # Increment the value
        result = self.collection.find_one_and_update(
            {"key": key},
            {"$inc": {"value": amount}},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        return result["value"] if result else amount

    def clear(self) -> None:
        """Clear all data from storage."""
        self.collection.delete_many({})

    def close(self) -> None:
        """Close the MongoDB connection."""
        if hasattr(self, "client") and self.client:
            self.client.close()


class AsyncMongoDBStorage(AsyncBaseStorage):
    """
    MongoDB storage backend for PyWebGuard (asynchronous).

    This class provides an asynchronous MongoDB-based storage backend for PyWebGuard.
    It stores data in a MongoDB collection with TTL support.

    Attributes:
        client: Async MongoDB client instance
        db: MongoDB database instance
        collection: MongoDB collection instance
        ttl: Default TTL for stored data in seconds
    """

    def __init__(
        self,
        url: str = "mongodb://localhost:27017/pywebguard",
        collection_name: str = "pywebguard",
        ttl: int = 3600,
        **kwargs: Any
    ) -> None:
        """
        Initialize async MongoDB storage.

        Args:
            url: MongoDB connection URL (mongodb://host:port/database)
            collection_name: Name of the collection to use
            ttl: Default TTL for stored data in seconds
            **kwargs: Additional arguments to pass to AsyncMongoClient

        Raises:
            ImportError: If pymongo is not installed
        """
        if not MONGODB_AVAILABLE:
            raise ImportError(
                "MongoDB storage requires pymongo. Install it with 'pip install pymongo'"
            )

        # Parse URL to extract database name
        if "/" in url:
            parts = url.split("/")
            db_name = parts[-1]
            connection_url = "/".join(parts[:-1]) + "/"
        else:
            db_name = "pywebguard"
            connection_url = url

        self.client = AsyncMongoClient(connection_url, **kwargs)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.ttl = ttl
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize indexes if not already done."""
        if self._initialized:
            return

        # Create TTL index if it doesn't exist
        await self.collection.create_index(
            "expires_at", expireAfterSeconds=0, background=True
        )

        # Create key index for faster lookups
        await self.collection.create_index("key", background=True)

        self._initialized = True

    async def get(self, key: str) -> Any:
        """
        Get a value from storage asynchronously.

        Args:
            key: Key to retrieve

        Returns:
            The stored value, or None if the key doesn't exist or has expired
        """
        await self.initialize()

        doc = await self.collection.find_one({"key": key})
        if doc and "value" in doc:
            # Check if the document has expired
            if "expires_at" in doc and doc["expires_at"] < datetime.utcnow():
                await self.delete(key)
                return None
            return doc["value"]
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage asynchronously.

        Args:
            key: Key to store
            value: Value to store
            ttl: Time-to-live in seconds (None for default)
        """
        await self.initialize()

        expires_at = None
        if ttl is not None and ttl > 0:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        elif self.ttl > 0:
            expires_at = datetime.utcnow() + timedelta(seconds=self.ttl)

        # Use upsert to handle both insert and update
        await self.collection.update_one(
            {"key": key},
            {
                "$set": {
                    "key": key,
                    "value": value,
                    "expires_at": expires_at,
                    "updated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )

    async def delete(self, key: str) -> None:
        """
        Delete a value from storage asynchronously.

        Args:
            key: Key to delete
        """
        await self.initialize()
        await self.collection.delete_one({"key": key})

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage asynchronously.

        Args:
            key: Key to check

        Returns:
            True if the key exists and has not expired, False otherwise
        """
        await self.initialize()

        doc = await self.collection.find_one(
            {"key": key}, projection={"_id": 1, "expires_at": 1}
        )
        if doc:
            # Check if the document has expired
            if "expires_at" in doc and doc["expires_at"] < datetime.utcnow():
                await self.delete(key)
                return False
            return True
        return False

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter in storage asynchronously.

        Args:
            key: Key to increment
            amount: Amount to increment by

        Returns:
            The new value of the counter
        """
        await self.initialize()

        # Check if the key exists and hasn't expired
        if not await self.exists(key):
            await self.set(key, 0)

        # Increment the value
        result = await self.collection.find_one_and_update(
            {"key": key},
            {"$inc": {"value": amount}},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        return result["value"] if result else amount

    async def clear(self) -> None:
        """Clear all data from storage asynchronously."""
        await self.initialize()
        await self.collection.delete_many({})

    async def close(self) -> None:
        """Close the MongoDB connection asynchronously."""
        if hasattr(self, "client") and self.client:
            await self.client.close()

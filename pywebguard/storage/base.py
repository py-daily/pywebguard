"""
Base storage interface for PyWebGuard with both sync and async support.

This module defines the base storage interfaces that all storage backends must implement.
It provides both synchronous and asynchronous interfaces to support different web frameworks.

Classes:
    StorageProtocol: Protocol defining the minimum required methods for storage implementations
    AsyncStorageProtocol: Protocol defining the minimum required methods for async storage implementations
    BaseStorage: Abstract base class for synchronous storage backends
    AsyncBaseStorage: Abstract base class for asynchronous storage backends
"""

from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    Protocol,
    TypeVar,
    Generic,
    runtime_checkable,
)

T = TypeVar("T")  # Generic type for stored values


@runtime_checkable
class StorageProtocol(Protocol):
    """Protocol defining the minimum required methods for storage implementations."""

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from storage.

        Args:
            key: The key to retrieve

        Returns:
            The stored value or None if not found
        """
        ...

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage.

        Args:
            key: The key to store
            value: The value to store
            ttl: Time to live in seconds
        """
        ...

    def delete(self, key: str) -> None:
        """
        Delete a value from storage.

        Args:
            key: The key to delete
        """
        ...

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        ...

    def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """
        Increment a counter in storage.

        Args:
            key: The key to increment
            amount: The amount to increment by
            ttl: Time to live in seconds

        Returns:
            The new value
        """
        ...

    def clear(self) -> None:
        """
        Clear all values from storage.
        """
        ...


@runtime_checkable
class AsyncStorageProtocol(Protocol):
    """Protocol defining the minimum required methods for async storage implementations."""

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from storage asynchronously.

        Args:
            key: The key to retrieve

        Returns:
            The stored value or None if not found
        """
        ...

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage asynchronously.

        Args:
            key: The key to store
            value: The value to store
            ttl: Time to live in seconds
        """
        ...

    async def delete(self, key: str) -> None:
        """
        Delete a value from storage asynchronously.

        Args:
            key: The key to delete
        """
        ...

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage asynchronously.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        ...

    async def increment(
        self, key: str, amount: int = 1, ttl: Optional[int] = None
    ) -> int:
        """
        Increment a counter in storage asynchronously.

        Args:
            key: The key to increment
            amount: The amount to increment by
            ttl: Time to live in seconds

        Returns:
            The new value
        """
        ...

    async def clear(self) -> None:
        """
        Clear all values from storage asynchronously.
        """
        ...


class BaseStorage(ABC):
    """
    Abstract base class for synchronous storage backends.

    This class defines the interface that all synchronous storage backends must implement.
    Storage backends are responsible for storing and retrieving data used by PyWebGuard.
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from storage.

        Args:
            key: The key to retrieve

        Returns:
            The stored value or None if not found
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage.

        Args:
            key: The key to store
            value: The value to store
            ttl: Time to live in seconds
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete a value from storage.

        Args:
            key: The key to delete
        """
        pass

    @abstractmethod
    def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """
        Increment a counter in storage.

        Args:
            key: The key to increment
            amount: The amount to increment by
            ttl: Time to live in seconds

        Returns:
            The new value
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear all values from storage.
        """
        pass


class AsyncBaseStorage(ABC):
    """
    Abstract base class for asynchronous storage backends.

    This class defines the interface that all asynchronous storage backends must implement.
    Asynchronous storage backends are used with asynchronous web frameworks like FastAPI.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from storage asynchronously.

        Args:
            key: The key to retrieve

        Returns:
            The stored value or None if not found
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in storage asynchronously.

        Args:
            key: The key to store
            value: The value to store
            ttl: Time to live in seconds
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Delete a value from storage asynchronously.

        Args:
            key: The key to delete
        """
        pass

    @abstractmethod
    async def increment(
        self, key: str, amount: int = 1, ttl: Optional[int] = None
    ) -> int:
        """
        Increment a counter in storage asynchronously.

        Args:
            key: The key to increment
            amount: The amount to increment by
            ttl: Time to live in seconds

        Returns:
            The new value
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage asynchronously.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        pass

    @abstractmethod
    async def clear(self) -> None:
        """
        Clear all values from storage asynchronously.
        """
        pass

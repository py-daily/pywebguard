"""
Rate limiting functionality for PyWebGuard with both sync and async support.
Includes support for per-route rate limiting configurations.
"""

from typing import Dict, Any, Optional, Union
import time
from pywebguard.core.config import RateLimitConfig
from pywebguard.storage.base import BaseStorage, AsyncBaseStorage
from pywebguard.limiters.base import BaseLimiter, AsyncBaseLimiter


class RateLimiter(BaseLimiter):
    """
    Limit request rates based on IP address or other identifiers (synchronous).
    Supports both global and per-route rate limiting.
    """

    def __init__(
        self,
        config: RateLimitConfig,
        storage: BaseStorage,
    ):
        """
        Initialize the rate limiter.

        Args:
            config: Rate limit configuration (global default)
            storage: Storage backend for persistent data
        """
        self.config = config
        self.storage = storage
        self.route_configs = {}  # Maps route patterns to custom RateLimitConfig objects

    def add_route_config(
        self, route_pattern: str, config: Union[RateLimitConfig, Dict[str, Any]]
    ):
        """
        Add a custom rate limit configuration for a specific route pattern.

        Args:
            route_pattern: The route pattern to match (can include wildcards like * and **)
            config: Custom rate limit configuration for this route
        """
        if isinstance(config, dict):
            # Convert dict to RateLimitConfig
            route_config = RateLimitConfig(**config)
        else:
            route_config = config

        self.route_configs[route_pattern] = route_config

    def get_config_for_route(self, path: str) -> RateLimitConfig:
        """
        Get the appropriate rate limit configuration for a given path.

        Args:
            path: The request path

        Returns:
            The route-specific config if matched, otherwise the default config
        """
        # Check for exact match first
        if path in self.route_configs:
            return self.route_configs[path]

        # Check for pattern matches
        for pattern, config in self.route_configs.items():
            if self._match_route_pattern(pattern, path):
                return config

        # Fall back to default config
        return self.config

    def _match_route_pattern(self, pattern: str, path: str) -> bool:
        """
        Check if a path matches a route pattern.

        Args:
            pattern: The route pattern (can include wildcards)
            path: The request path

        Returns:
            True if the path matches the pattern, False otherwise
        """
        # Simple wildcard matching implementation
        if pattern == "*":
            return True

        if pattern.endswith("/**"):
            # Match any path that starts with the pattern prefix
            prefix = pattern[:-3]
            return path.startswith(prefix)

        if pattern.endswith("/*"):
            # Match any path that starts with the pattern prefix and has no additional segments
            prefix = pattern[:-2]
            if not path.startswith(prefix):
                return False
            remaining = path[len(prefix) :]
            return remaining == "" or (
                remaining.startswith("/") and "/" not in remaining[1:]
            )

        # Exact match
        return pattern == path

    def check_limit(self, identifier: str, path: str = None) -> Dict[str, Any]:
        """
        Check if a request should be rate limited.

        Args:
            identifier: The identifier to check (usually IP address)
            path: The request path (for route-specific rate limiting)

        Returns:
            Dict with allowed status, remaining requests, and reset time
        """
        # Get the appropriate config for this route
        config = self.config
        if path is not None:
            config = self.get_config_for_route(path)

        if not config.enabled:
            return {"allowed": True, "remaining": -1, "reset": -1}

        current_time = int(time.time())

        # Use path in the rate limit key if provided
        path_suffix = f":{path}" if path else ""
        window_key = f"ratelimit:{identifier}{path_suffix}:{current_time // 60}"

        # Get current count for this minute
        count = self.storage.get(window_key) or 0

        # Check if rate limit is exceeded
        if count >= config.requests_per_minute:
            # Check if burst capacity is available
            burst_key = f"ratelimit:burst:{identifier}{path_suffix}"
            burst_count = self.storage.get(burst_key) or 0

            if burst_count >= config.burst_size:
                # Rate limit exceeded
                reset_time = (current_time // 60 + 1) * 60

                # Check for auto-ban threshold
                if config.auto_ban_threshold > 0:
                    violation_key = f"ratelimit:violations:{identifier}{path_suffix}"
                    violations = self.storage.increment(
                        violation_key, 1, 86400
                    )  # 24 hour TTL

                    if violations >= config.auto_ban_threshold:
                        # Auto-ban the identifier
                        ban_key = f"banned_ip:{identifier}"
                        self.storage.set(
                            ban_key,
                            {
                                "reason": f"Rate limit exceeded for {path or 'global'}",
                                "timestamp": current_time,
                            },
                            config.auto_ban_duration_minutes * 60,
                        )

                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset": reset_time,
                    "reason": f"Rate limit exceeded for {path or 'global'}",
                }

            # Use burst capacity
            self.storage.increment(burst_key, 1, 3600)  # 1 hour TTL

        # Increment the counter
        new_count = self.storage.increment(window_key, 1, 60)  # 1 minute TTL

        # Calculate remaining requests
        remaining = max(0, config.requests_per_minute - new_count)

        # Calculate reset time
        reset_time = (current_time // 60 + 1) * 60

        return {"allowed": True, "remaining": remaining, "reset": reset_time}


class AsyncRateLimiter(AsyncBaseLimiter):
    """
    Limit request rates based on IP address or other identifiers (asynchronous).
    Supports both global and per-route rate limiting.
    """

    def __init__(
        self,
        config: RateLimitConfig,
        storage: AsyncBaseStorage,
    ):
        """
        Initialize the async rate limiter.

        Args:
            config: Rate limit configuration (global default)
            storage: Async storage backend for persistent data
        """
        self.config = config
        self.storage = storage
        self.route_configs = {}  # Maps route patterns to custom RateLimitConfig objects

    def add_route_config(
        self, route_pattern: str, config: Union[RateLimitConfig, Dict[str, Any]]
    ):
        """
        Add a custom rate limit configuration for a specific route pattern.

        Args:
            route_pattern: The route pattern to match (can include wildcards like * and **)
            config: Custom rate limit configuration for this route
        """
        if isinstance(config, dict):
            # Convert dict to RateLimitConfig
            route_config = RateLimitConfig(**config)
        else:
            route_config = config

        self.route_configs[route_pattern] = route_config

    def get_config_for_route(self, path: str) -> RateLimitConfig:
        """
        Get the appropriate rate limit configuration for a given path.

        Args:
            path: The request path

        Returns:
            The route-specific config if matched, otherwise the default config
        """
        # Check for exact match first
        if path in self.route_configs:
            return self.route_configs[path]

        # Check for pattern matches
        for pattern, config in self.route_configs.items():
            if self._match_route_pattern(pattern, path):
                return config

        # Fall back to default config
        return self.config

    def _match_route_pattern(self, pattern: str, path: str) -> bool:
        """
        Check if a path matches a route pattern.

        Args:
            pattern: The route pattern (can include wildcards)
            path: The request path

        Returns:
            True if the path matches the pattern, False otherwise
        """
        # Simple wildcard matching implementation
        if pattern == "*":
            return True

        if pattern.endswith("/**"):
            # Match any path that starts with the pattern prefix
            prefix = pattern[:-3]
            return path.startswith(prefix)

        if pattern.endswith("/*"):
            # Match any path that starts with the pattern prefix and has no additional segments
            prefix = pattern[:-2]
            if not path.startswith(prefix):
                return False
            remaining = path[len(prefix) :]
            return remaining == "" or (
                remaining.startswith("/") and "/" not in remaining[1:]
            )

        # Exact match
        return pattern == path

    async def check_limit(self, identifier: str, path: str = None) -> Dict[str, Any]:
        """
        Check if a request should be rate limited asynchronously.

        Args:
            identifier: The identifier to check (usually IP address)
            path: The request path (for route-specific rate limiting)

        Returns:
            Dict with allowed status, remaining requests, and reset time
        """
        # Get the appropriate config for this route
        config = self.config
        if path is not None:
            config = self.get_config_for_route(path)

        if not config.enabled:
            return {"allowed": True, "remaining": -1, "reset": -1}

        current_time = int(time.time())

        # Use path in the rate limit key if provided
        path_suffix = f":{path}" if path else ""
        window_key = f"ratelimit:{identifier}{path_suffix}:{current_time // 60}"

        # Get current count for this minute
        count = await self.storage.get(window_key) or 0

        # Check if rate limit is exceeded
        if count >= config.requests_per_minute:
            # Check if burst capacity is available
            burst_key = f"ratelimit:burst:{identifier}{path_suffix}"
            burst_count = await self.storage.get(burst_key) or 0

            if burst_count >= config.burst_size:
                # Rate limit exceeded
                reset_time = (current_time // 60 + 1) * 60

                # Check for auto-ban threshold
                if config.auto_ban_threshold > 0:
                    violation_key = f"ratelimit:violations:{identifier}{path_suffix}"
                    violations = await self.storage.increment(
                        violation_key, 1, 86400
                    )  # 24 hour TTL

                    if violations >= config.auto_ban_threshold:
                        # Auto-ban the identifier
                        ban_key = f"banned_ip:{identifier}"
                        await self.storage.set(
                            ban_key,
                            {
                                "reason": f"Rate limit exceeded for {path or 'global'}",
                                "timestamp": current_time,
                            },
                            config.auto_ban_duration_minutes * 60,
                        )

                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset": reset_time,
                    "reason": f"Rate limit exceeded for {path or 'global'}",
                }

            # Use burst capacity
            await self.storage.increment(burst_key, 1, 3600)  # 1 hour TTL

        # Increment the counter
        new_count = await self.storage.increment(window_key, 1, 60)  # 1 minute TTL

        # Calculate remaining requests
        remaining = max(0, config.requests_per_minute - new_count)

        # Calculate reset time
        reset_time = (current_time // 60 + 1) * 60

        return {"allowed": True, "remaining": remaining, "reset": reset_time}

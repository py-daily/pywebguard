"""
Configuration management for PyWebGuard.

This module provides configuration classes for various security features
of PyWebGuard, including IP filtering, rate limiting, user agent filtering,
penetration detection, CORS, logging, and storage.
"""

import os
from typing import List, Dict, Any, Optional, Union, Set
from pydantic import BaseModel, Field, field_validator

from .constants import PENETRATION_DETECTION_SUSPICIOUS_PATTERNS


class IPFilterConfig(BaseModel):
    """Configuration for IP filtering.

    Attributes:
        enabled: Whether IP filtering is enabled
        whitelist: List of allowed IP addresses
        blacklist: List of blocked IP addresses
        block_cloud_providers: Whether to block known cloud provider IPs
        geo_restrictions: Dictionary mapping country codes to allow/block status
    """

    enabled: bool = True
    whitelist: List[str] = Field(default_factory=list)
    blacklist: List[str] = Field(default_factory=list)
    block_cloud_providers: bool = False
    geo_restrictions: Dict[str, bool] = Field(default_factory=dict)

    @field_validator("whitelist", "blacklist")
    def validate_ip_addresses(cls, v: List[str]) -> List[str]:
        """Validate IP addresses in whitelist and blacklist.

        Args:
            v: List of IP addresses to validate

        Returns:
            List of validated IP addresses

        Raises:
            ValueError: If any IP address is invalid
        """
        import ipaddress

        for ip in v:
            try:
                # Handle CIDR notation
                if "/" in ip:
                    ipaddress.ip_network(ip, strict=False)
                else:
                    ipaddress.ip_address(ip)
            except ValueError as e:
                raise ValueError(f"Invalid IP address: {ip}") from e
        return v


class RateLimitConfig(BaseModel):
    """Configuration for rate limiting.

    Attributes:
        enabled: Whether rate limiting is enabled
        requests_per_minute: Maximum number of requests allowed per minute
        burst_size: Maximum number of requests allowed in burst
        auto_ban_threshold: Number of violations before auto-ban
        auto_ban_duration_minutes: Duration of auto-ban in minutes
    """

    enabled: bool = True
    requests_per_minute: int = Field(default=60, ge=1)
    burst_size: int = Field(default=10, ge=0)
    auto_ban_threshold: int = Field(default=100, ge=1)
    auto_ban_duration_minutes: int = Field(default=60, ge=1)


class UserAgentConfig(BaseModel):
    """
    Configuration for user-agent filtering.

    Attributes:
        enabled (bool): Flag to enable or disable user-agent filtering.
        blocked_agents (List[str]): List of user-agent substrings to block (e.g., 'curl', 'wget').
        excluded_paths (List[str]): List of endpoint paths where user-agent filtering should be bypassed.
            Useful for allowing monitoring tools to access health check endpoints like '/ready' or '/healthz'.
    """

    enabled: bool = True
    blocked_agents: List[str] = Field(default_factory=list)
    excluded_paths: List[str] = Field(default_factory=list)


class PenetrationDetectionConfig(BaseModel):
    """Configuration for penetration attempt detection.

    Attributes:
        enabled: Whether penetration detection is enabled
        log_suspicious: Whether to log suspicious activities
        suspicious_patterns: List of patterns to detect suspicious activities
    """

    enabled: bool = True
    log_suspicious: bool = True
    suspicious_patterns: Optional[List[str]] = Field(
        default=PENETRATION_DETECTION_SUSPICIOUS_PATTERNS
    )


class CORSConfig(BaseModel):
    """Configuration for CORS (Cross-Origin Resource Sharing).

    Attributes:
        enabled: Whether CORS is enabled
        allow_origins: List of allowed origins
        allow_methods: List of allowed HTTP methods
        allow_headers: List of allowed headers
        allow_credentials: Whether to allow credentials
        max_age: Maximum age of preflight requests in seconds
    """

    enabled: bool = True
    allow_origins: List[str] = Field(default=["*"])
    allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    allow_headers: List[str] = Field(default=["*"])
    allow_credentials: bool = False
    max_age: int = Field(default=600, ge=0)


class LoggingConfig(BaseModel):
    """Configuration for logging.

    Attributes:
        enabled: Whether logging is enabled
        log_file: Path to log file (None for stdout)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        propagate: Whether to propagate logs to root logger
        stream: Whether to log to stdout
        stream_levels: List of levels to log to stdout
        max_log_size: Maximum log file size in bytes
        max_log_files: Maximum number of log files to keep
        log_format: Log format string
        log_date_format: Log date format string
        log_rotation: Log rotation interval
        log_backup_count: Number of backup log files to keep
        log_encoding: Log file encoding
        meilisearch: Meilisearch backend configuration
        elasticsearch: Elasticsearch backend configuration
        mongodb: MongoDB backend configuration
    """

    enabled: bool = True
    log_file: Optional[str] = None
    log_level: str = Field(default="INFO")
    propagate: bool = True
    stream: bool = False
    stream_levels: List[str] = Field(default_factory=list)
    max_log_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    max_log_files: int = Field(default=2)
    log_format: str = Field(default="{asctime} {levelname} {message}")
    log_date_format: str = Field(default="%Y-%m-%d %H:%M:%S")
    log_rotation: str = Field(default="midnight")
    log_backup_count: int = Field(default=3)
    log_encoding: str = Field(default="utf-8")

    # Backend configurations
    meilisearch: Optional[Dict[str, Any]] = None
    elasticsearch: Optional[Dict[str, Any]] = None
    mongodb: Optional[Dict[str, Any]] = None

    @field_validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate logging level.

        Args:
            v: Logging level to validate

        Returns:
            Validated logging level

        Raises:
            ValueError: If logging level is invalid
        """
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()

    @field_validator("meilisearch")
    def validate_meilisearch(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Validate Meilisearch configuration.

        Args:
            v: Meilisearch configuration to validate

        Returns:
            Validated Meilisearch configuration

        Raises:
            ValueError: If configuration is invalid
        """
        if v is None:
            return None

        required_fields = {"url", "api_key", "index_name"}
        missing_fields = required_fields - set(v.keys())
        if missing_fields:
            raise ValueError(f"Missing required Meilisearch fields: {missing_fields}")
        return v

    @field_validator("elasticsearch")
    def validate_elasticsearch(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Validate Elasticsearch configuration.

        Args:
            v: Elasticsearch configuration to validate

        Returns:
            Validated Elasticsearch configuration

        Raises:
            ValueError: If configuration is invalid
        """
        if v is None:
            return None

        required_fields = {"hosts"}
        missing_fields = required_fields - set(v.keys())
        if missing_fields:
            raise ValueError(f"Missing required Elasticsearch fields: {missing_fields}")
        return v

    @field_validator("mongodb")
    def validate_mongodb(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate MongoDB configuration.

        Args:
            v: MongoDB configuration to validate

        Returns:
            Validated MongoDB configuration

        Raises:
            ValueError: If configuration is invalid
        """
        if v is None:
            return None

        # Check if URI is provided or if host/port are provided
        if "uri" not in v and not all(
            k in v for k in ["host", "port", "database", "collection"]
        ):
            raise ValueError(
                "MongoDB configuration must include either 'uri' or all of 'host', 'port', 'database', and 'collection'"
            )
        return v


class StorageConfig(BaseModel):
    """Configuration for storage.

    Attributes:
        type: Storage type ("memory", "redis", "sqlite", "tinydb", "mongodb", "postgresql")
        url: Connection URL for the storage backend
        prefix: Prefix for storage keys
        ttl: Time-to-live for stored data in seconds
        table_name: Table or collection name (for SQL/MongoDB)
    """

    type: str = Field(default="memory")
    url: Optional[str] = None
    prefix: str = Field(default="pywebguard:")
    ttl: int = Field(default=3600, ge=0)
    table_name: str = Field(default="pywebguard")

    @field_validator("type")
    def validate_storage_type(cls, v: str) -> str:
        """Validate storage type.

        Args:
            v: Storage type to validate

        Returns:
            Validated storage type

        Raises:
            ValueError: If storage type is invalid
        """
        valid_types = {"memory", "redis", "sqlite", "tinydb", "mongodb", "postgresql"}
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid storage type: {v}. Must be one of {valid_types}")
        return v.lower()

    @field_validator("url")
    def validate_url(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        """Validate storage URL.

        Args:
            v: Storage URL to validate
            values: Other field values

        Returns:
            Validated storage URL

        Raises:
            ValueError: If URL is required but not provided
        """
        storage_type = values.get("type", "memory")

        # Memory storage doesn't need a URL
        if storage_type == "memory":
            return None

        # For other storage types, URL is required
        if not v and storage_type != "memory":
            if storage_type == "redis":
                return "redis://localhost:6379/0"
            elif storage_type == "sqlite":
                return "pywebguard.db"
            elif storage_type == "tinydb":
                return "pywebguard.json"
            elif storage_type == "mongodb":
                return "mongodb://localhost:27017/pywebguard"
            elif storage_type == "postgresql":
                return "postgresql://postgres:postgres@localhost:5432/pywebguard"

        return v


class GuardConfig(BaseModel):
    """Main configuration for PyWebGuard.

    This class combines all configuration components into a single configuration
    object that can be used to initialize the WebGuard instance.

    Attributes:
        ip_filter: IP filtering configuration
        rate_limit: Rate limiting configuration
        user_agent: User agent filtering configuration
        penetration: Penetration detection configuration
        cors: CORS configuration
        logging: Logging configuration
        storage: Storage configuration
    """

    ip_filter: IPFilterConfig = Field(default_factory=IPFilterConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    user_agent: UserAgentConfig = Field(default_factory=UserAgentConfig)
    penetration: PenetrationDetectionConfig = Field(
        default_factory=PenetrationDetectionConfig
    )
    cors: CORSConfig = Field(default_factory=CORSConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)

    @classmethod
    def from_env(cls) -> "GuardConfig":
        """Create a GuardConfig instance from environment variables.

        Environment variables:
            PYWEBGUARD_STORAGE_TYPE: Storage type (memory, redis, sqlite, tinydb, mongodb, postgresql)
            PYWEBGUARD_STORAGE_URL: Connection URL for the storage backend
            PYWEBGUARD_STORAGE_PREFIX: Prefix for storage keys
            PYWEBGUARD_STORAGE_TTL: Time-to-live for stored data in seconds
            PYWEBGUARD_STORAGE_TABLE: Table or collection name

            PYWEBGUARD_RATE_LIMIT_ENABLED: Whether rate limiting is enabled (true/false)
            PYWEBGUARD_RATE_LIMIT_RPM: Requests per minute
            PYWEBGUARD_RATE_LIMIT_BURST: Burst size
            PYWEBGUARD_RATE_LIMIT_BAN_THRESHOLD: Auto-ban threshold
            PYWEBGUARD_RATE_LIMIT_BAN_DURATION: Auto-ban duration in minutes

            PYWEBGUARD_IP_FILTER_ENABLED: Whether IP filtering is enabled (true/false)
            PYWEBGUARD_IP_WHITELIST: Comma-separated list of whitelisted IPs
            PYWEBGUARD_IP_BLACKLIST: Comma-separated list of blacklisted IPs

            PYWEBGUARD_LOG_ENABLED: Whether logging is enabled (true/false)
            PYWEBGUARD_LOG_FILE: Path to log file
            PYWEBGUARD_LOG_LEVEL: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Returns:
            GuardConfig: Configuration instance with values from environment variables
        """
        # Create default config
        config = cls()

        # Storage configuration
        storage_type = os.environ.get("PYWEBGUARD_STORAGE_TYPE")
        if storage_type:
            config.storage.type = storage_type.lower()

        storage_url = os.environ.get("PYWEBGUARD_STORAGE_URL")
        if storage_url:
            config.storage.url = storage_url

        storage_prefix = os.environ.get("PYWEBGUARD_STORAGE_PREFIX")
        if storage_prefix:
            config.storage.prefix = storage_prefix

        storage_ttl = os.environ.get("PYWEBGUARD_STORAGE_TTL")
        if storage_ttl and storage_ttl.isdigit():
            config.storage.ttl = int(storage_ttl)

        storage_table = os.environ.get("PYWEBGUARD_STORAGE_TABLE")
        if storage_table:
            config.storage.table_name = storage_table

        # Rate limit configuration
        rate_limit_enabled = os.environ.get("PYWEBGUARD_RATE_LIMIT_ENABLED")
        if rate_limit_enabled is not None:
            config.rate_limit.enabled = rate_limit_enabled.lower() in (
                "true",
                "1",
                "yes",
            )

        rate_limit_rpm = os.environ.get("PYWEBGUARD_RATE_LIMIT_RPM")
        if rate_limit_rpm and rate_limit_rpm.isdigit():
            config.rate_limit.requests_per_minute = int(rate_limit_rpm)

        rate_limit_burst = os.environ.get("PYWEBGUARD_RATE_LIMIT_BURST")
        if rate_limit_burst and rate_limit_burst.isdigit():
            config.rate_limit.burst_size = int(rate_limit_burst)

        rate_limit_ban_threshold = os.environ.get("PYWEBGUARD_RATE_LIMIT_BAN_THRESHOLD")
        if rate_limit_ban_threshold and rate_limit_ban_threshold.isdigit():
            config.rate_limit.auto_ban_threshold = int(rate_limit_ban_threshold)

        rate_limit_ban_duration = os.environ.get("PYWEBGUARD_RATE_LIMIT_BAN_DURATION")
        if rate_limit_ban_duration and rate_limit_ban_duration.isdigit():
            config.rate_limit.auto_ban_duration_minutes = int(rate_limit_ban_duration)

        # IP filter configuration
        ip_filter_enabled = os.environ.get("PYWEBGUARD_IP_FILTER_ENABLED")
        if ip_filter_enabled is not None:
            config.ip_filter.enabled = ip_filter_enabled.lower() in ("true", "1", "yes")

        ip_whitelist = os.environ.get("PYWEBGUARD_IP_WHITELIST")
        if ip_whitelist:
            config.ip_filter.whitelist = [ip.strip() for ip in ip_whitelist.split(",")]

        ip_blacklist = os.environ.get("PYWEBGUARD_IP_BLACKLIST")
        if ip_blacklist:
            config.ip_filter.blacklist = [ip.strip() for ip in ip_blacklist.split(",")]

        # Logging configuration
        log_enabled = os.environ.get("PYWEBGUARD_LOG_ENABLED")
        if log_enabled is not None:
            config.logging.enabled = log_enabled.lower() in ("true", "1", "yes")

        log_file = os.environ.get("PYWEBGUARD_LOG_FILE")
        if log_file:
            config.logging.log_file = log_file

        log_level = os.environ.get("PYWEBGUARD_LOG_LEVEL")
        if log_level:
            config.logging.log_level = log_level.upper()

        return config

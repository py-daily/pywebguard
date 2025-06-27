# Configuration

PyWebGuard uses a configuration system based on Pydantic models. This allows for type checking, validation, and easy serialization/deserialization of configuration.

## GuardConfig

The main configuration class is `GuardConfig`, which combines all configuration components into a single object.

### Basic Usage

```python
from pywebguard import GuardConfig

# Create a configuration with default settings
config = GuardConfig()

# Create a configuration with custom settings
config = GuardConfig(
    ip_filter={"whitelist": ["127.0.0.1"]},
    rate_limit={"requests_per_minute": 100},
    user_agent={"blocked_agents": ["curl", "wget"], "excluded_paths": ["/ready", "/healthz"]}
)
```

### Configuration Components

The `GuardConfig` class contains the following configuration components:

- `ip_filter`: IP filtering configuration
- `rate_limit`: Rate limiting configuration
- `user_agent`: User agent filtering configuration
- `penetration`: Penetration detection configuration
- `cors`: CORS configuration
- `logging`: Logging configuration
- `storage`: Storage configuration

Each component is a Pydantic model with its own set of fields.

## IP Filter Configuration

The `IPFilterConfig` class configures IP filtering.

```python
from pywebguard.core.config import IPFilterConfig

# Create IP filter configuration
ip_filter = IPFilterConfig(
    enabled=True,
    whitelist=["127.0.0.1", "192.168.1.0/24"],
    blacklist=["10.0.0.1"],
    block_cloud_providers=False,
    geo_restrictions={"US": True, "CN": False}
)

# Or as a dictionary
ip_filter_dict = {
    "enabled": True,
    "whitelist": ["127.0.0.1", "192.168.1.0/24"],
    "blacklist": ["10.0.0.1"],
    "block_cloud_providers": False,
    "geo_restrictions": {"US": True, "CN": False}
}
```

### Fields

- `enabled`: Whether IP filtering is enabled (default: `True`)
- `whitelist`: List of allowed IP addresses or CIDR ranges (default: `[]`)
- `blacklist`: List of blocked IP addresses or CIDR ranges (default: `[]`)
- `block_cloud_providers`: Whether to block known cloud provider IPs (default: `False`)
- `geo_restrictions`: Dictionary mapping country codes to allow/block status (default: `{}`)

## Rate Limit Configuration

The `RateLimitConfig` class configures rate limiting.

```python
from pywebguard.core.config import RateLimitConfig

# Create rate limit configuration
rate_limit = RateLimitConfig(
    enabled=True,
    requests_per_minute=60,
    burst_size=10,
    auto_ban_threshold=100,
    auto_ban_duration_minutes=60
)

# Or as a dictionary
rate_limit_dict = {
    "enabled": True,
    "requests_per_minute": 60,
    "burst_size": 10,
    "auto_ban_threshold": 100,
    "auto_ban_duration_minutes": 60,
    "excluded_paths": ["/ready", "/healthz"]
}
```

### Fields

- `enabled`: Whether rate limiting is enabled (default: `True`)
- `requests_per_minute`: Maximum number of requests allowed per minute (default: `60`)
- `burst_size`: Maximum number of requests allowed in burst (default: `10`)
- `auto_ban_threshold`: Number of violations before auto-ban (default: `100`)
- `auto_ban_duration_minutes`: Duration of auto-ban in minutes (default: `60`)

## User Agent Configuration

The `UserAgentConfig` class configures user agent filtering.

```python
from pywebguard.core.config import UserAgentConfig

# Create user agent configuration
user_agent = UserAgentConfig(
    enabled=True,
    blocked_agents=["curl", "wget", "python-requests"],
    excluded_paths= ["/ready", "/healthz"]
)

# Or as a dictionary
user_agent_dict = {
    "enabled": True,
    "blocked_agents": ["curl", "wget", "python-requests"],
     "excluded_paths": ["/ready", "/healthz"]
}
```

### Fields

- `enabled`: Whether user agent filtering is enabled (default: `True`)
- `blocked_agents`: List of blocked user agent strings (default: `[]`)
- `excluded_paths`: List of endpoint paths where user-agent filtering should be bypassed.
        Useful for allowing monitoring tools to access health check endpoints like '/ready' or '/healthz'. (default: `[]`)

## Penetration Detection Configuration

The `PenetrationDetectionConfig` class configures penetration attempt detection.

```python
from pywebguard.core.config import PenetrationDetectionConfig

# Create penetration detection configuration
penetration = PenetrationDetectionConfig(
    enabled=True,
    log_suspicious=True,
    suspicious_patterns=[
        r"(?i)(?:union\s+select|select\s+.*\s+from)",
        r"(?i)(?:<script>|javascript:|onerror=|onload=)"
    ]
)

# Or as a dictionary
penetration_dict = {
    "enabled": True,
    "log_suspicious": True,
    "suspicious_patterns": [
        r"(?i)(?:union\s+select|select\s+.*\s+from)",
        r"(?i)(?:<script>|javascript:|onerror=|onload=)"
    ]
}
```

### Fields

- `enabled`: Whether penetration detection is enabled (default: `True`)
- `log_suspicious`: Whether to log suspicious activities (default: `True`)
- `suspicious_patterns`: List of regex patterns to detect suspicious activities (default: `[]`)

## CORS Configuration

The `CORSConfig` class configures Cross-Origin Resource Sharing (CORS).

```python
from pywebguard.core.config import CORSConfig

# Create CORS configuration
cors = CORSConfig(
    enabled=True,
    allow_origins=["https://example.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True,
    max_age=600
)

# Or as a dictionary
cors_dict = {
    "enabled": True,
    "allow_origins": ["https://example.com"],
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "allow_credentials": True,
    "max_age": 600
}
```

### Fields

- `enabled`: Whether CORS is enabled (default: `True`)
- `allow_origins`: List of allowed origins (default: `["*"]`)
- `allow_methods`: List of allowed HTTP methods (default: `["GET", "POST", "PUT", "DELETE", "OPTIONS"]`)
- `allow_headers`: List of allowed headers (default: `["*"]`)
- `allow_credentials`: Whether to allow credentials (default: `False`)
- `max_age`: Maximum age of preflight requests in seconds (default: `600`)

## Logging Configuration

The `LoggingConfig` class configures logging.

```python
from pywebguard.core.config import LoggingConfig

# Create logging configuration
logging_config = LoggingConfig(
    enabled=True,
    log_file="pywebguard.log",
    log_level="INFO",
    stream=True,
    stream_levels=["ERROR", "CRITICAL"],
    max_log_size=10 * 1024 * 1024,  # 10MB
    max_log_files=2
)

# Or as a dictionary
logging_dict = {
    "enabled": True,
    "log_file": "pywebguard.log",
    "log_level": "INFO",
    "stream": True,
    "stream_levels": ["ERROR", "CRITICAL"],
    "max_log_size": 10 * 1024 * 1024,  # 10MB
    "max_log_files": 2
}
```

### Fields

- `enabled`: Whether logging is enabled (default: `True`)
- `log_file`: Path to log file (default: `None` for stdout)
- `log_level`: Logging level (default: `"INFO"`)
- `stream`: Whether to log to stdout (default: `False`)
- `stream_levels`: List of levels to log to stdout (default: `[]`)
- `max_log_size`: Maximum log file size in bytes (default: `10 * 1024 * 1024` = 10MB)
- `max_log_files`: Maximum number of log files to keep (default: `2`)
- `log_format`: Log format string (default: `"{asctime} {levelname} {message}"`)
- `log_date_format`: Log date format string (default: `"%Y-%m-%d %H:%M:%S"`)
- `log_rotation`: Log rotation interval (default: `"midnight"`)
- `log_backup_count`: Number of backup log files to keep (default: `3`)
- `log_encoding`: Log file encoding (default: `"utf-8"`)

## Storage Configuration

The `StorageConfig` class configures storage.

```python
from pywebguard.core.config import StorageConfig

# Create storage configuration
storage = StorageConfig(
    type="redis",
    redis_url="redis://localhost:6379/0",
    redis_prefix="pywebguard:",
    ttl=3600
)

# Or as a dictionary
storage_dict = {
    "type": "redis",
    "redis_url": "redis://localhost:6379/0",
    "redis_prefix": "pywebguard:",
    "ttl": 3600
}
```

### Fields

- `type`: Storage type (default: `"memory"`, options: `"memory"`, `"redis"`)
- `redis_url`: Redis connection URL (required if type is `"redis"`)
- `redis_prefix`: Prefix for Redis keys (default: `"pywebguard:"`)
- `ttl`: Time-to-live for stored data in seconds (default: `3600`)

## Complete Configuration Example

```python
from pywebguard import GuardConfig

# Create a complete configuration
config = GuardConfig(
    ip_filter={
        "enabled": True,
        "whitelist": ["127.0.0.1", "192.168.1.0/24"],
        "blacklist": ["10.0.0.1"],
        "block_cloud_providers": False,
        "geo_restrictions": {"US": True, "CN": False}
    },
    rate_limit={
        "enabled": True,
        "requests_per_minute": 60,
        "burst_size": 10,
        "auto_ban_threshold": 100,
        "auto_ban_duration_minutes": 60,
        "excluded_paths": ["/ready/*", "/healthz/*"]
    },
    user_agent={
        "enabled": True,
        "blocked_agents": ["curl", "wget", "python-requests"],
         "excluded_paths": ["/ready"]
    },
    penetration={
        "enabled": True,
        "log_suspicious": True,
        "suspicious_patterns": [
            r"(?i)(?:union\s+select|select\s+.*\s+from)",
            r"(?i)(?:<script>|javascript:|onerror=|onload=)"
        ]
    },
    cors={
        "enabled": True,
        "allow_origins": ["https://example.com"],
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "allow_credentials": True,
        "max_age": 600
    },
    logging={
        "enabled": True,
        "log_file": "pywebguard.log",
        "log_level": "INFO"
    },
    storage={
        "type": "redis",
        "redis_url": "redis://localhost:6379/0",
        "redis_prefix": "pywebguard:",
        "ttl": 3600
    }
)
```

## Loading Configuration from File

You can load configuration from a JSON file:

```python
import json
from pywebguard import GuardConfig

# Load configuration from file
with open("pywebguard.json", "r") as f:
    config_data = json.load(f)

# Create GuardConfig from loaded data
config = GuardConfig(**config_data)
```

## Saving Configuration to File

You can save configuration to a JSON file:

```python
import json
from pywebguard import GuardConfig

# Create configuration
config = GuardConfig(
    ip_filter={"whitelist": ["127.0.0.1"]},
    rate_limit={"requests_per_minute": 100}
)

# Convert to dictionary
config_dict = config.dict()

# Save to file
with open("pywebguard.json", "w") as f:
    json.dump(config_dict, f, indent=2)

# Command-Line Interface

PyWebGuard includes a command-line interface (CLI) for common tasks such as initializing configuration files, validating existing configurations, managing banned IPs, and more.

## Installation

The CLI is automatically installed when you install PyWebGuard:

```bash
pip install pywebguard
```

## Usage

### Getting Help

To see available commands and options:

```bash
pywebguard --help
```

### Checking Version

To check the installed version of PyWebGuard:

```bash
pywebguard --version
```

## Configuration Commands

### Initializing a Configuration File

To create a new configuration file with default settings:

```bash
pywebguard init --output pywebguard.json
```

To create a configuration file for a specific framework:

```bash
# For FastAPI
pywebguard init --output pywebguard.json --framework fastapi

# For Flask
pywebguard init --output pywebguard.json --framework flask
```

### Interactive Configuration

To create a configuration file interactively with guided prompts:

```bash
pywebguard interactive
```

This will walk you through the configuration process step by step, asking questions about your preferences for IP filtering, rate limiting, storage, and more.

### Validating a Configuration File

To validate an existing configuration file:

```bash
pywebguard validate pywebguard.json
```

## Storage Commands

### Testing Storage Connection

To test the connection to a storage backend:

```bash
# Test memory storage
pywebguard test memory

# Test Redis storage
pywebguard test redis --connection "redis://localhost:6379/0"

# Test SQLite storage
pywebguard test sqlite --connection "pywebguard.db"

# Test TinyDB storage
pywebguard test tinydb --connection "pywebguard.json"
```

### Clearing Storage

To clear all data from storage:

```bash
pywebguard clear pywebguard.json
```

To skip the confirmation prompt:

```bash
pywebguard clear pywebguard.json --yes
```

## IP Management Commands

### Banning an IP Address

To ban an IP address:

```bash
pywebguard ban pywebguard.json 192.168.1.100
```

To specify the ban duration (in minutes):

```bash
pywebguard ban pywebguard.json 192.168.1.100 --duration 120
```

### Unbanning an IP Address

To unban an IP address:

```bash
pywebguard unban pywebguard.json 192.168.1.100
```

## Status Commands

### Checking Status

To check the status of PyWebGuard and view information about the current configuration:

```bash
pywebguard status pywebguard.json
```

This will display information about:
- Current version
- Storage backend
- Enabled/disabled features
- Banned IPs (if using Redis storage)

## Configuration File Format

The configuration file is a JSON file with the following structure:

```json
{
  "ip_filter": {
    "enabled": true,
    "whitelist": [],
    "blacklist": [],
    "block_cloud_providers": false,
    "geo_restrictions": {}
  },
  "rate_limit": {
    "enabled": true,
    "requests_per_minute": 60,
    "burst_size": 10,
    "auto_ban_threshold": 100,
    "auto_ban_duration_minutes": 60,
    "excluded_paths": ["/ready", "/healthz"]
  },
  "user_agent": {
    "enabled": true,
    "blocked_agents": ["curl", "wget", "python-requests"]
  },
  "penetration": {
    "enabled": true,
    "log_suspicious": true,
    "suspicious_patterns": []
  },
  "cors": {
    "enabled": true,
    "allow_origins": ["*"],
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["*"],
    "allow_credentials": false,
    "max_age": 600
  },
  "logging": {
    "enabled": true,
    "log_file": "pywebguard.log",
    "log_level": "INFO"
  },
  "storage": {
    "type": "memory",
    "redis_url": null,
    "redis_prefix": "pywebguard:",
    "ttl": 3600
  }
}
```

For framework-specific configurations, additional sections will be added:

```json
{
  "framework": {
    "type": "fastapi",
    "route_rate_limits": [
      {
        "endpoint": "/api/limited",
        "requests_per_minute": 5,
        "burst_size": 2
      }
    ]
  }
}
```

## Exit Codes

The CLI returns the following exit codes:

- `0`: Success
- `1`: Error (e.g., invalid configuration file, file not found)

## Examples

### Creating a Configuration File for FastAPI

```bash
pywebguard init --output fastapi-config.json --framework fastapi
```

### Creating a Configuration File Interactively

```bash
pywebguard interactive
```

### Validating a Configuration File

```bash
pywebguard validate fastapi-config.json
```

### Banning an IP Address

```bash
pywebguard ban fastapi-config.json 192.168.1.100 --duration 120
```

### Checking Status

```bash
pywebguard status fastapi-config.json
```

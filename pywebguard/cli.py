"""
Command-line interface for PyWebGuard.

This module provides a command-line interface for managing PyWebGuard configurations,
testing connections, managing banned IPs, and more.
"""

import argparse
import sys
import json
import os
import time
import ipaddress
from typing import Dict, Any, List, Optional, Union, Tuple, NoReturn
from pathlib import Path

from pywebguard import __version__
from pywebguard.core.config import GuardConfig
from pywebguard.storage.memory import MemoryStorage
from pywebguard.logging.logger import SecurityLogger, AsyncSecurityLogger

try:
    from pywebguard.storage._redis import RedisStorage
except ImportError:
    RedisStorage = None
try:
    from pywebguard.storage._sqlite import SQLiteStorage
except ImportError:
    SQLiteStorage = None
try:
    from pywebguard.storage._tinydb import TinyDBStorage
except ImportError:
    TinyDBStorage = None


def main() -> int:
    """
    Main entry point for the CLI.

    Parses command-line arguments and dispatches to the appropriate command handler.

    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        description="PyWebGuard - A comprehensive security library for Python web applications"
    )

    parser.add_argument(
        "--version", "-v", action="store_true", help="Show version and exit"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a configuration file")
    init_parser.add_argument(
        "--output", "-o", default="pywebguard.json", help="Output file path"
    )
    init_parser.add_argument(
        "--framework", "-f", choices=["fastapi", "flask"], help="Framework to use"
    )

    # Interactive init command
    subparsers.add_parser(
        "interactive", help="Interactively create a configuration file"
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate a configuration file"
    )
    validate_parser.add_argument("config_file", help="Path to configuration file")

    # Test connection command
    test_parser = subparsers.add_parser(
        "test", help="Test connection to a storage backend"
    )
    test_parser.add_argument(
        "storage_type",
        choices=["memory", "redis", "sqlite", "tinydb"],
        help="Storage type to test",
    )
    test_parser.add_argument(
        "--connection", "-c", help="Connection string for the storage backend"
    )

    # Ban IP command
    ban_parser = subparsers.add_parser("ban", help="Ban an IP address")
    ban_parser.add_argument("config_file", help="Path to configuration file")
    ban_parser.add_argument("ip_address", help="IP address to ban")
    ban_parser.add_argument(
        "--duration", "-d", type=int, default=60, help="Duration of the ban in minutes"
    )

    # Unban IP command
    unban_parser = subparsers.add_parser("unban", help="Unban an IP address")
    unban_parser.add_argument("config_file", help="Path to configuration file")
    unban_parser.add_argument("ip_address", help="IP address to unban")

    # Clear storage command
    clear_parser = subparsers.add_parser("clear", help="Clear all data from storage")
    clear_parser.add_argument("config_file", help="Path to configuration file")
    clear_parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompt"
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Show status information")
    status_parser.add_argument("config_file", help="Path to configuration file")

    args = parser.parse_args()

    if args.version:
        print(f"PyWebGuard v{__version__}")
        return 0

    if args.command == "init":
        return cmd_init(args.output, args.framework)
    elif args.command == "interactive":
        return cmd_interactive_init()
    elif args.command == "validate":
        return cmd_validate(args.config_file)
    elif args.command == "test":
        return cmd_test_connection(args.storage_type, args.connection)
    elif args.command == "ban":
        return cmd_ban_ip(args.config_file, args.ip_address, args.duration)
    elif args.command == "unban":
        return cmd_unban_ip(args.config_file, args.ip_address)
    elif args.command == "clear":
        return cmd_clear_storage(args.config_file, args.yes)
    elif args.command == "status":
        return cmd_status(args.config_file)
    else:
        parser.print_help()
        return 0


def cmd_init(output_path: str, framework: Optional[str] = None) -> int:
    """
    Initialize a configuration file with default settings.

    Args:
        output_path: Path to output file
        framework: Framework to use (fastapi, flask, or None)

    Returns:
        int: Exit code (0 for success, 1 for error)

    Raises:
        IOError: If the file cannot be written
    """
    # Create default configuration
    config: Dict[str, Any] = {
        "ip_filter": {
            "enabled": True,
            "whitelist": [],
            "blacklist": [],
            "block_cloud_providers": False,
            "geo_restrictions": {},
        },
        "rate_limit": {
            "enabled": True,
            "requests_per_minute": 60,
            "burst_size": 10,
            "auto_ban_threshold": 100,
            "auto_ban_duration_minutes": 60,
        },
        "user_agent": {
            "enabled": True,
            "blocked_agents": ["curl", "wget", "python-requests"],
        },
        "penetration": {
            "enabled": True,
            "log_suspicious": True,
            "suspicious_patterns": [],
        },
        "cors": {
            "enabled": True,
            "allow_origins": ["*"],
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
            "allow_credentials": False,
            "max_age": 600,
        },
        "logging": {
            "enabled": True,
            "log_file": "pywebguard.log",
            "log_level": "INFO",
            "stream": True,
            "stream_levels": ["ERROR", "CRITICAL"],
            "max_log_size": 10 * 1024 * 1024,  # 10MB
            "max_log_files": 2,
            "log_format": "{asctime} {levelname} {message}",
            "log_date_format": "%Y-%m-%d %H:%M:%S",
            "log_rotation": "midnight",
            "log_backup_count": 3,
            "log_encoding": "utf-8",
            "meilisearch": None,
            "elasticsearch": None,
            "mongodb": None,
        },
        "storage": {
            "type": "memory",
            "redis_url": None,
            "redis_prefix": "pywebguard:",
            "ttl": 3600,
        },
    }

    # Add framework-specific configuration
    if framework == "fastapi":
        config["framework"] = {
            "type": "fastapi",
            "route_rate_limits": [
                {"endpoint": "/api/limited", "requests_per_minute": 5, "burst_size": 2}
            ],
        }
    elif framework == "flask":
        config["framework"] = {
            "type": "flask",
            "route_rate_limits": [
                {"endpoint": "/api/limited", "requests_per_minute": 5, "burst_size": 2}
            ],
        }

    # Write configuration to file
    try:
        with open(output_path, "w") as f:
            json.dump(config, f, indent=4)
        print(f"Configuration written to {output_path}")
        return 0
    except IOError as e:
        print(f"Error writing configuration: {e}", file=sys.stderr)
        return 1


def cmd_validate(config_path: str) -> int:
    """
    Validate a configuration file against the PyWebGuard schema.

    Args:
        config_path: Path to configuration file

    Returns:
        int: Exit code (0 for success, 1 for error)

    Raises:
        FileNotFoundError: If the configuration file does not exist
        json.JSONDecodeError: If the configuration file is not valid JSON
        ValueError: If the configuration is not valid
    """
    try:
        # Read configuration from file
        with open(config_path, "r") as f:
            config_data = json.load(f)

        # Validate configuration
        GuardConfig(**config_data)

        print(f"Configuration file {config_path} is valid")
        return 0
    except FileNotFoundError:
        print(f"Configuration file {config_path} not found")
        return 1
    except json.JSONDecodeError:
        print(f"Configuration file {config_path} is not valid JSON")
        return 1
    except Exception as e:
        print(f"Configuration file {config_path} is not valid: {e}")
        return 1


def cmd_test_connection(
    storage_type: str, connection_string: Optional[str] = None
) -> int:
    """
    Test connection to a storage backend.

    Args:
        storage_type: Type of storage backend to test (memory, redis, sqlite, tinydb)
        connection_string: Connection string for the storage backend

    Returns:
        int: Exit code (0 for success, 1 for error)

    Raises:
        ImportError: If the required storage backend is not installed
        ConnectionError: If the connection to the storage backend fails
    """
    print(f"Testing connection to {storage_type} storage...")

    try:
        if storage_type == "memory":
            storage = MemoryStorage()
            storage.set("test_key", "test_value")
            value = storage.get("test_key")
            storage.delete("test_key")
            print("Memory storage test successful")
            return 0

        elif storage_type == "redis":
            if RedisStorage is None:
                print(
                    "Redis storage is not available. Install it with 'pip install pywebguard[redis]'"
                )
                return 1

            if not connection_string:
                connection_string = "redis://localhost:6379/0"

            storage = RedisStorage(url=connection_string)
            storage.set("test_key", "test_value")
            value = storage.get("test_key")
            storage.delete("test_key")
            print(f"Redis connection to {connection_string} successful")
            return 0

        elif storage_type == "sqlite":
            if SQLiteStorage is None:
                print(
                    "SQLite storage is not available. Install it with 'pip install pywebguard[sqlite]'"
                )
                return 1

            if not connection_string:
                connection_string = ":memory:"

            storage = SQLiteStorage(db_path=connection_string)
            storage.set("test_key", "test_value")
            value = storage.get("test_key")
            storage.delete("test_key")
            print(f"SQLite connection to {connection_string} successful")
            return 0

        elif storage_type == "tinydb":
            if TinyDBStorage is None:
                print(
                    "TinyDB storage is not available. Install it with 'pip install pywebguard[tinydb]'"
                )
                return 1

            if not connection_string:
                connection_string = "pywebguard_test.json"

            storage = TinyDBStorage(db_path=connection_string)
            storage.set("test_key", "test_value")
            value = storage.get("test_key")
            storage.delete("test_key")

            # Clean up test file if created
            if (
                os.path.exists(connection_string)
                and connection_string != "pywebguard.json"
            ):
                os.remove(connection_string)

            print(f"TinyDB connection test successful")
            return 0

        else:
            print(f"Unknown storage type: {storage_type}")
            return 1

    except Exception as e:
        print(f"Connection test failed: {e}")
        return 1


def cmd_ban_ip(config_path: str, ip_address: str, duration_minutes: int = 60) -> int:
    """
    Ban an IP address for a specified duration.

    Args:
        config_path: Path to configuration file
        ip_address: IP address to ban
        duration_minutes: Duration of the ban in minutes

    Returns:
        int: Exit code (0 for success, 1 for error)

    Raises:
        FileNotFoundError: If the configuration file does not exist
        json.JSONDecodeError: If the configuration file is not valid JSON
        ValueError: If the IP address is invalid
    """
    try:
        # Validate IP address
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            print(f"Invalid IP address: {ip_address}")
            return 1

        # Read configuration from file
        with open(config_path, "r") as f:
            config_data = json.load(f)

        # Create GuardConfig
        config = GuardConfig(**config_data)

        # Initialize storage
        storage = _get_storage_from_config(config, config_data)

        # Ban the IP
        ban_key = f"banned_ip:{ip_address}"
        storage.set(
            ban_key,
            {"reason": "Manually banned via CLI", "timestamp": time.time()},
            duration_minutes * 60,
        )

        print(f"IP address {ip_address} banned for {duration_minutes} minutes")
        return 0

    except FileNotFoundError:
        print(f"Configuration file {config_path} not found")
        return 1
    except json.JSONDecodeError:
        print(f"Configuration file {config_path} is not valid JSON")
        return 1
    except Exception as e:
        print(f"Error banning IP address: {e}")
        return 1


def cmd_unban_ip(config_path: str, ip_address: str) -> int:
    """
    Unban a previously banned IP address.

    Args:
        config_path: Path to configuration file
        ip_address: IP address to unban

    Returns:
        int: Exit code (0 for success, 1 for error)

    Raises:
        FileNotFoundError: If the configuration file does not exist
        json.JSONDecodeError: If the configuration file is not valid JSON
        ValueError: If the IP address is invalid
    """
    try:
        # Validate IP address
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            print(f"Invalid IP address: {ip_address}")
            return 1

        # Read configuration from file
        with open(config_path, "r") as f:
            config_data = json.load(f)

        # Create GuardConfig
        config = GuardConfig(**config_data)

        # Initialize storage
        storage = _get_storage_from_config(config, config_data)

        # Unban the IP
        ban_key = f"banned_ip:{ip_address}"
        if storage.exists(ban_key):
            storage.delete(ban_key)
            print(f"IP address {ip_address} unbanned")
        else:
            print(f"IP address {ip_address} is not banned")

        return 0

    except FileNotFoundError:
        print(f"Configuration file {config_path} not found")
        return 1
    except json.JSONDecodeError:
        print(f"Configuration file {config_path} is not valid JSON")
        return 1
    except Exception as e:
        print(f"Error unbanning IP address: {e}")
        return 1


def cmd_clear_storage(config_path: str, confirm: bool = False) -> int:
    """
    Clear all data from storage.

    Args:
        config_path: Path to configuration file
        confirm: Whether to skip confirmation prompt

    Returns:
        int: Exit code (0 for success, 1 for error)

    Raises:
        FileNotFoundError: If the configuration file does not exist
        json.JSONDecodeError: If the configuration file is not valid JSON
    """
    try:
        # Read configuration from file
        with open(config_path, "r") as f:
            config_data = json.load(f)

        # Create GuardConfig
        config = GuardConfig(**config_data)

        # Initialize storage and get description
        storage, storage_desc = _get_storage_and_desc_from_config(config, config_data)

        # Confirm action
        if not confirm:
            response = input(
                f"Are you sure you want to clear all data from {storage_desc} storage? [y/N] "
            )
            if response.lower() not in ["y", "yes"]:
                print("Operation cancelled")
                return 0

        # Clear storage
        storage.clear()
        print(f"All data cleared from {storage_desc} storage")
        return 0

    except FileNotFoundError:
        print(f"Configuration file {config_path} not found")
        return 1
    except json.JSONDecodeError:
        print(f"Configuration file {config_path} is not valid JSON")
        return 1
    except Exception as e:
        print(f"Error clearing storage: {e}")
        return 1


def cmd_status(config_path: str) -> int:
    """
    Show status information about PyWebGuard configuration and storage.

    Args:
        config_path: Path to configuration file

    Returns:
        int: Exit code (0 for success, 1 for error)

    Raises:
        FileNotFoundError: If the configuration file does not exist
        json.JSONDecodeError: If the configuration file is not valid JSON
    """
    try:
        # Read configuration from file
        with open(config_path, "r") as f:
            config_data = json.load(f)

        # Create GuardConfig
        config = GuardConfig(**config_data)

        # Initialize storage and get description
        storage, storage_desc = _get_storage_and_desc_from_config(config, config_data)

        # Print status information
        print(f"PyWebGuard v{__version__}")
        print(f"Storage: {storage_desc}")
        print(f"IP Filter: {'Enabled' if config.ip_filter.enabled else 'Disabled'}")
        print(f"Rate Limit: {'Enabled' if config.rate_limit.enabled else 'Disabled'}")
        print(
            f"User Agent Filter: {'Enabled' if config.user_agent.enabled else 'Disabled'}"
        )
        print(
            f"Penetration Detection: {'Enabled' if config.penetration.enabled else 'Disabled'}"
        )
        print(f"CORS: {'Enabled' if config.cors.enabled else 'Disabled'}")
        print(f"Logging: {'Enabled' if config.logging.enabled else 'Disabled'}")

        # Try to get some statistics
        try:
            # Count banned IPs
            banned_ips = []
            if config.storage.type == "redis" and RedisStorage is not None:
                # For Redis, we can use pattern matching
                import redis

                r = redis.from_url(
                    config.storage.redis_url or "redis://localhost:6379/0"
                )
                banned_keys = r.keys(f"{config.storage.redis_prefix}banned_ip:*")
                banned_ips = [key.decode().split(":")[-1] for key in banned_keys]
            else:
                # For other storage types, we can't easily get this information
                pass

            if banned_ips:
                print(f"\nBanned IPs: {len(banned_ips)}")
                for ip in banned_ips[:5]:  # Show first 5
                    print(f"  - {ip}")
                if len(banned_ips) > 5:
                    print(f"  ... and {len(banned_ips) - 5} more")
        except Exception:
            # Ignore errors in getting statistics
            pass

        return 0

    except FileNotFoundError:
        print(f"Configuration file {config_path} not found")
        return 1
    except json.JSONDecodeError:
        print(f"Configuration file {config_path} is not valid JSON")
        return 1
    except Exception as e:
        print(f"Error getting status: {e}")
        return 1


def cmd_interactive_init() -> int:
    """
    Interactively create a configuration file by prompting the user for input.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    print("PyWebGuard Interactive Configuration")
    print("===================================")

    # Initialize default config
    config: Dict[str, Any] = {
        "ip_filter": {
            "enabled": True,
            "whitelist": [],
            "blacklist": [],
            "block_cloud_providers": False,
            "geo_restrictions": {},
        },
        "rate_limit": {
            "enabled": True,
            "requests_per_minute": 60,
            "burst_size": 10,
            "auto_ban_threshold": 100,
            "auto_ban_duration_minutes": 60,
        },
        "user_agent": {
            "enabled": True,
            "blocked_agents": ["curl", "wget", "python-requests"],
        },
        "penetration": {
            "enabled": True,
            "log_suspicious": True,
            "suspicious_patterns": [],
        },
        "cors": {
            "enabled": True,
            "allow_origins": ["*"],
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
            "allow_credentials": False,
            "max_age": 600,
        },
        "logging": {
            "enabled": True,
            "log_file": "pywebguard.log",
            "log_level": "INFO",
            "stream": True,
            "stream_levels": ["ERROR", "CRITICAL"],
            "max_log_size": 10 * 1024 * 1024,  # 10MB
            "max_log_files": 2,
            "log_format": "{asctime} {levelname} {message}",
            "log_date_format": "%Y-%m-%d %H:%M:%S",
            "log_rotation": "midnight",
            "log_backup_count": 3,
            "log_encoding": "utf-8",
            "meilisearch": None,
            "elasticsearch": None,
            "mongodb": None,
        },
        "storage": {
            "type": "memory",
            "redis_url": None,
            "redis_prefix": "pywebguard:",
            "ttl": 3600,
        },
    }

    # IP Filter
    print("\nIP Filter Configuration")
    config["ip_filter"]["enabled"] = input(
        "Enable IP filtering? [Y/n]: "
    ).strip().lower() not in ["n", "no", "0", "false"]

    if config["ip_filter"]["enabled"]:
        whitelist = input("Enter whitelisted IPs (comma-separated): ").strip()
        if whitelist:
            config["ip_filter"]["whitelist"] = [
                ip.strip() for ip in whitelist.split(",")
            ]

        blacklist = input("Enter blacklisted IPs (comma-separated): ").strip()
        if blacklist:
            config["ip_filter"]["blacklist"] = [
                ip.strip() for ip in blacklist.split(",")
            ]

        config["ip_filter"]["block_cloud_providers"] = input(
            "Block cloud provider IPs? [y/N]: "
        ).strip().lower() in ["y", "yes", "1", "true"]

    # Rate Limit
    print("\nRate Limit Configuration")
    config["rate_limit"]["enabled"] = input(
        "Enable rate limiting? [Y/n]: "
    ).strip().lower() not in ["n", "no", "0", "false"]

    if config["rate_limit"]["enabled"]:
        rpm = input("Enter requests per minute [60]: ").strip()
        if rpm:
            config["rate_limit"]["requests_per_minute"] = int(rpm)

        burst = input("Enter burst size [10]: ").strip()
        if burst:
            config["rate_limit"]["burst_size"] = int(burst)

        ban_threshold = input("Enter auto-ban threshold [100]: ").strip()
        if ban_threshold:
            config["rate_limit"]["auto_ban_threshold"] = int(ban_threshold)

        ban_duration = input("Enter auto-ban duration in minutes [60]: ").strip()
        if ban_duration:
            config["rate_limit"]["auto_ban_duration_minutes"] = int(ban_duration)

    # User Agent
    print("\nUser Agent Configuration")
    config["user_agent"]["enabled"] = input(
        "Enable user agent filtering? [Y/n]: "
    ).strip().lower() not in ["n", "no", "0", "false"]

    if config["user_agent"]["enabled"]:
        blocked_agents = input(
            "Enter blocked user agents (comma-separated) [curl,wget,python-requests]: "
        ).strip()
        if blocked_agents:
            config["user_agent"]["blocked_agents"] = [
                agent.strip() for agent in blocked_agents.split(",")
            ]

    # Penetration Detection
    print("\nPenetration Detection Configuration")
    config["penetration"]["enabled"] = input(
        "Enable penetration detection? [Y/n]: "
    ).strip().lower() not in ["n", "no", "0", "false"]

    if config["penetration"]["enabled"]:
        config["penetration"]["log_suspicious"] = input(
            "Log suspicious activities? [Y/n]: "
        ).strip().lower() not in ["n", "no", "0", "false"]

        patterns = input("Enter suspicious patterns (comma-separated): ").strip()
        if patterns:
            config["penetration"]["suspicious_patterns"] = [
                pattern.strip() for pattern in patterns.split(",")
            ]

    # CORS
    print("\nCORS Configuration")
    config["cors"]["enabled"] = input("Enable CORS? [Y/n]: ").strip().lower() not in [
        "n",
        "no",
        "0",
        "false",
    ]

    if config["cors"]["enabled"]:
        origins = input("Enter allowed origins (comma-separated) [*]: ").strip()
        if origins:
            config["cors"]["allow_origins"] = [
                origin.strip() for origin in origins.split(",")
            ]

        methods = input(
            "Enter allowed methods (comma-separated) [GET,POST,PUT,DELETE,OPTIONS]: "
        ).strip()
        if methods:
            config["cors"]["allow_methods"] = [
                method.strip() for method in methods.split(",")
            ]

        headers = input("Enter allowed headers (comma-separated) [*]: ").strip()
        if headers:
            config["cors"]["allow_headers"] = [
                header.strip() for header in headers.split(",")
            ]

        config["cors"]["allow_credentials"] = input(
            "Allow credentials? [y/N]: "
        ).strip().lower() in ["y", "yes", "1", "true"]

        max_age = input("Enter max age in seconds [600]: ").strip()
        if max_age:
            config["cors"]["max_age"] = int(max_age)

    # Storage
    print("\nStorage Configuration")
    print("Storage types:")
    print("1. Memory (default)")
    print("2. Redis")
    print("3. SQLite")
    print("4. TinyDB")

    storage_choice = input("Choose storage type [1]: ").strip() or "1"

    if storage_choice == "2":
        config["storage"]["type"] = "redis"
        redis_url = (
            input("Enter Redis URL [redis://localhost:6379/0]: ").strip()
            or "redis://localhost:6379/0"
        )
        config["storage"]["redis_url"] = redis_url
        redis_prefix = (
            input("Enter Redis key prefix [pywebguard:]: ").strip() or "pywebguard:"
        )
        config["storage"]["redis_prefix"] = redis_prefix
    elif storage_choice == "3":
        config["storage"]["type"] = "sqlite"
        db_path = (
            input("Enter SQLite database path [pywebguard.db]: ").strip()
            or "pywebguard.db"
        )
        config["storage"]["db_path"] = db_path
    elif storage_choice == "4":
        config["storage"]["type"] = "tinydb"
        db_path = (
            input("Enter TinyDB database path [pywebguard.json]: ").strip()
            or "pywebguard.json"
        )
        config["storage"]["db_path"] = db_path

    # Logging
    print("\nLogging Configuration")
    config["logging"]["enabled"] = input(
        "Enable logging? [Y/n]: "
    ).strip().lower() not in ["n", "no", "0", "false"]

    if config["logging"]["enabled"]:
        log_file = (
            input(
                "Enter log file path (leave empty for stdout) [pywebguard.log]: "
            ).strip()
            or "pywebguard.log"
        )
        config["logging"]["log_file"] = log_file

        print("Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL")
        log_level = input("Enter log level [INFO]: ").strip().upper() or "INFO"
        config["logging"]["log_level"] = log_level

        # Configure logging backends
        print("\nLogging Backends")
        print("Available backends:")
        print("1. None (default)")
        print("2. Meilisearch")
        print("3. Elasticsearch")
        print("4. MongoDB")

        backend_choice = input("Choose logging backend [1]: ").strip() or "1"

        if backend_choice == "2":
            config["logging"]["meilisearch"] = {
                "url": input("Enter Meilisearch URL [http://localhost:7700]: ").strip()
                or "http://localhost:7700",
                "api_key": input("Enter Meilisearch API key: ").strip(),
                "index_name": input("Enter index name [pywebguard_logs]: ").strip()
                or "pywebguard_logs",
            }
        elif backend_choice == "3":
            config["logging"]["elasticsearch"] = {
                "hosts": [
                    input("Enter Elasticsearch host [http://localhost:9200]: ").strip()
                    or "http://localhost:9200"
                ],
                "index_prefix": input("Enter index prefix [pywebguard]: ").strip()
                or "pywebguard",
                "username": input("Enter username (optional): ").strip() or None,
                "password": input("Enter password (optional): ").strip() or None,
            }
        elif backend_choice == "4":
            use_uri = input("Use connection URI? [y/N]: ").strip().lower() in [
                "y",
                "yes",
                "1",
                "true",
            ]
            if use_uri:
                config["logging"]["mongodb"] = {
                    "uri": input("Enter MongoDB URI: ").strip(),
                    "database": input("Enter database name [pywebguard]: ").strip()
                    or "pywebguard",
                    "collection": input("Enter collection name [logs]: ").strip()
                    or "logs",
                }
            else:
                config["logging"]["mongodb"] = {
                    "host": input("Enter MongoDB host [localhost]: ").strip()
                    or "localhost",
                    "port": int(
                        input("Enter MongoDB port [27017]: ").strip() or "27017"
                    ),
                    "database": input("Enter database name [pywebguard]: ").strip()
                    or "pywebguard",
                    "collection": input("Enter collection name [logs]: ").strip()
                    or "logs",
                    "username": input("Enter username (optional): ").strip() or None,
                    "password": input("Enter password (optional): ").strip() or None,
                }

    # Output file
    output_path = (
        input("\nEnter output file path [pywebguard.json]: ").strip()
        or "pywebguard.json"
    )

    # Write configuration to file
    try:
        with open(output_path, "w") as f:
            json.dump(config, f, indent=4)
        print(f"Configuration written to {output_path}")
        return 0
    except IOError as e:
        print(f"Error writing configuration: {e}", file=sys.stderr)
        return 1


def _get_storage_from_config(config: GuardConfig, config_data: Dict[str, Any]) -> Any:
    """
    Get a storage instance from a configuration.

    Args:
        config: GuardConfig object
        config_data: Raw configuration data

    Returns:
        Storage instance

    Raises:
        ImportError: If the required storage backend is not installed
        ValueError: If the storage type is unknown
    """
    if config.storage.type == "redis":
        if RedisStorage is None:
            raise ImportError(
                "Redis storage is not available. Install it with 'pip install pywebguard[redis]'"
            )
        return RedisStorage(
            url=config.storage.redis_url or "redis://localhost:6379/0",
            prefix=config.storage.redis_prefix,
        )
    elif config.storage.type == "sqlite":
        if SQLiteStorage is None:
            raise ImportError(
                "SQLite storage is not available. Install it with 'pip install pywebguard[sqlite]'"
            )
        return SQLiteStorage(
            db_path=config_data.get("storage", {}).get("db_path", "pywebguard.db")
        )
    elif config.storage.type == "tinydb":
        if TinyDBStorage is None:
            raise ImportError(
                "TinyDB storage is not available. Install it with 'pip install pywebguard[tinydb]'"
            )
        return TinyDBStorage(
            db_path=config_data.get("storage", {}).get("db_path", "pywebguard.json")
        )
    else:
        return MemoryStorage()


def _get_storage_and_desc_from_config(
    config: GuardConfig, config_data: Dict[str, Any]
) -> Tuple[Any, str]:
    """
    Get a storage instance and description from a configuration.

    Args:
        config: GuardConfig object
        config_data: Raw configuration data

    Returns:
        Tuple of (storage instance, storage description)

    Raises:
        ImportError: If the required storage backend is not installed
        ValueError: If the storage type is unknown
    """
    if config.storage.type == "redis":
        if RedisStorage is None:
            raise ImportError(
                "Redis storage is not available. Install it with 'pip install pywebguard[redis]'"
            )
        storage = RedisStorage(
            url=config.storage.redis_url or "redis://localhost:6379/0",
            prefix=config.storage.redis_prefix,
        )
        storage_desc = f"Redis ({config.storage.redis_url})"
    elif config.storage.type == "sqlite":
        if SQLiteStorage is None:
            raise ImportError(
                "SQLite storage is not available. Install it with 'pip install pywebguard[sqlite]'"
            )
        db_path = config_data.get("storage", {}).get("db_path", "pywebguard.db")
        storage = SQLiteStorage(db_path=db_path)
        storage_desc = f"SQLite ({db_path})"
    elif config.storage.type == "tinydb":
        if TinyDBStorage is None:
            raise ImportError(
                "TinyDB storage is not available. Install it with 'pip install pywebguard[tinydb]'"
            )
        db_path = config_data.get("storage", {}).get("db_path", "pywebguard.json")
        storage = TinyDBStorage(db_path=db_path)
        storage_desc = f"TinyDB ({db_path})"
    else:
        storage = MemoryStorage()
        storage_desc = "Memory"

    return storage, storage_desc


if __name__ == "__main__":
    sys.exit(main())

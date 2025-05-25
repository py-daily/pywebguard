"""Tests for PyWebGuard framework integrations."""

import pytest
from typing import Dict, Any

from pywebguard.core.config import (
    GuardConfig,
    IPFilterConfig,
    RateLimitConfig,
    UserAgentConfig,
    PenetrationDetectionConfig,
    CORSConfig,
    LoggingConfig,
)


class TestBaseFramework:
    """Base tests that any framework should support."""

    @pytest.fixture
    def basic_config(self) -> GuardConfig:
        """Create a basic GuardConfig for testing."""
        return GuardConfig(
            ip_filter=IPFilterConfig(
                enabled=True,
                whitelist=["127.0.0.1"],
                blacklist=["10.0.0.1"],
            ),
            rate_limit=RateLimitConfig(
                enabled=True,
                requests_per_minute=5,
                burst_size=2,
            ),
            user_agent=UserAgentConfig(
                enabled=True,
                blocked_agents=[
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ],
            ),
            penetration=PenetrationDetectionConfig(
                enabled=True,
                log_suspicious=True,
                suspicious_patterns=[
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ],
            ),
            cors=CORSConfig(
                enabled=True,
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
                allow_credentials=False,
            ),
            logging=LoggingConfig(
                enabled=True,
                log_file="test.log",
                log_level="INFO",
                stream=True,
                stream_levels=["INFO", "WARNING", "ERROR", "CRITICAL"],
            ),
        )

    def test_basic_config(self, basic_config: GuardConfig):
        """Test that basic configuration is valid."""
        assert basic_config.ip_filter.enabled is True
        assert "127.0.0.1" in basic_config.ip_filter.whitelist
        assert "10.0.0.1" in basic_config.ip_filter.blacklist
        assert basic_config.rate_limit.enabled is True
        assert basic_config.rate_limit.requests_per_minute == 5
        assert basic_config.rate_limit.burst_size == 2
        assert basic_config.user_agent.enabled is True
        assert basic_config.user_agent.blocked_agents == [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        assert basic_config.penetration.enabled is True
        assert basic_config.penetration.log_suspicious is True
        assert basic_config.cors.enabled is True
        assert basic_config.cors.allow_origins == ["*"]
        assert basic_config.cors.allow_methods == ["*"]
        assert basic_config.cors.allow_headers == ["*"]
        assert basic_config.cors.allow_credentials is False
        assert basic_config.logging.enabled is True
        assert basic_config.logging.log_file == "test.log"
        assert basic_config.logging.log_level == "INFO"
        assert basic_config.logging.stream is True
        assert basic_config.logging.stream_levels == [
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]
        assert basic_config.logging.max_log_size == 10 * 1024 * 1024
        assert basic_config.logging.max_log_files == 2
        assert basic_config.logging.log_format == "{asctime} {levelname} {message}"
        assert basic_config.logging.log_date_format == "%Y-%m-%d %H:%M:%S"
        assert basic_config.logging.log_rotation == "midnight"
        assert basic_config.logging.log_backup_count == 3
        assert basic_config.logging.log_encoding == "utf-8"
        assert basic_config.logging.meilisearch is None
        assert basic_config.logging.elasticsearch is None
        assert basic_config.logging.mongodb is None
        assert basic_config.storage.type == "memory"
        assert basic_config.storage.url is None
        assert basic_config.storage.prefix == "pywebguard:"
        assert basic_config.storage.ttl == 3600
        assert basic_config.storage.table_name == "pywebguard"

    def test_route_specific_config(self, basic_config: GuardConfig):
        """Test that route-specific configuration is valid."""
        route_configs = [
            {
                "endpoint": "/api/limited",
                "requests_per_minute": 1,
                "burst_size": 0,
            },
            {
                "endpoint": "/api/admin",
                "requests_per_minute": 100,
                "burst_size": 100,
            },
        ]

        # Test that route configs are properly formatted
        for config in route_configs:
            assert "endpoint" in config
            assert "requests_per_minute" in config
            assert "burst_size" in config
            assert isinstance(config["endpoint"], str)
            assert isinstance(config["requests_per_minute"], int)
            assert isinstance(config["burst_size"], int)

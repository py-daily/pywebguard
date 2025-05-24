"""Tests for IP utilities."""

import pytest
from pywebguard.utils.ip import (
    is_valid_ip,
    is_valid_cidr,
    get_real_ip,
    is_cloud_provider_ip,
)


class TestIPUtils:
    """Tests for IP utility functions."""

    @pytest.mark.parametrize(
        "ip,expected",
        [
            ("192.168.1.1", True),
            ("10.0.0.1", True),
            ("172.16.0.1", True),
            ("2001:db8::1", True),
            ("invalid", False),
            ("256.256.256.256", False),
            ("192.168.1", False),
            ("", False),
        ],
    )
    def test_is_valid_ip(self, ip: str, expected: bool):
        """Test IP address validation."""
        assert is_valid_ip(ip) == expected

    @pytest.mark.parametrize(
        "cidr,expected",
        [
            ("192.168.1.0/24", True),
            ("10.0.0.0/8", True),
            ("172.16.0.0/12", True),
            ("2001:db8::/32", True),
            ("invalid", False),
            ("192.168.1.0/33", False),
            ("2001:db8::/129", False),
            ("", False),
        ],
    )
    def test_is_valid_cidr(self, cidr: str, expected: bool):
        """Test CIDR range validation."""
        assert is_valid_cidr(cidr) == expected

    @pytest.mark.parametrize(
        "headers,remote_addr,expected",
        [
            # Test X-Forwarded-For
            (
                {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"},
                "127.0.0.1",
                "192.168.1.1",
            ),
            # Test X-Real-IP
            (
                {"X-Real-IP": "192.168.1.2"},
                "127.0.0.1",
                "192.168.1.2",
            ),
            # Test CF-Connecting-IP
            (
                {"CF-Connecting-IP": "192.168.1.3"},
                "127.0.0.1",
                "192.168.1.3",
            ),
            # Test True-Client-IP
            (
                {"True-Client-IP": "192.168.1.4"},
                "127.0.0.1",
                "192.168.1.4",
            ),
            # Test invalid IP in headers
            (
                {"X-Forwarded-For": "invalid"},
                "127.0.0.1",
                "127.0.0.1",
            ),
            # Test empty headers
            (
                {},
                "127.0.0.1",
                "127.0.0.1",
            ),
        ],
    )
    def test_get_real_ip(self, headers: dict, remote_addr: str, expected: str):
        """Test real IP extraction from headers."""
        assert get_real_ip(headers, remote_addr) == expected

    def test_is_cloud_provider_ip(self):
        """Test cloud provider IP detection."""
        # This is a placeholder test since the function is not implemented
        result = is_cloud_provider_ip("192.168.1.1")
        assert isinstance(result, dict)
        assert "is_cloud" in result
        assert "provider" in result
        assert result["is_cloud"] is False
        assert result["provider"] is None

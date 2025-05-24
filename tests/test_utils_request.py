"""Tests for request utilities."""

import pytest
from unittest.mock import MagicMock
from pywebguard.utils.request import (
    extract_request_info,
    is_suspicious_request,
    get_request_path,
)


class TestRequestUtils:
    """Tests for request utility functions."""

    def test_extract_request_info(self):
        """Test request information extraction."""
        # Test with a mock request object
        mock_request = MagicMock()
        mock_request.path = "/test"
        mock_request.method = "GET"
        mock_request.headers = {"User-Agent": "test-agent"}
        mock_request.query = {"param": "value"}

        result = extract_request_info(mock_request)
        assert isinstance(result, dict)
        assert result["ip"] == "0.0.0.0"  # Default value
        assert result["method"] == ""
        assert result["path"] == ""
        assert result["query"] == {}
        assert result["headers"] == {}

    def test_is_suspicious_request(self):
        """Test suspicious request detection."""
        # Test with empty request info
        result = is_suspicious_request({})
        assert isinstance(result, dict)
        assert "suspicious" in result
        assert "reason" in result
        assert result["suspicious"] is False
        assert result["reason"] is None

        # Test with some request info
        request_info = {
            "ip": "192.168.1.1",
            "user_agent": "test-agent",
            "method": "GET",
            "path": "/test",
        }
        result = is_suspicious_request(request_info)
        assert isinstance(result, dict)
        assert "suspicious" in result
        assert "reason" in result
        assert result["suspicious"] is False
        assert result["reason"] is None

    @pytest.mark.parametrize(
        "request_attrs,expected",
        [
            # Test with path attribute
            ({"path": "/test"}, "/test"),
            # Test with url.path attribute
            ({"url": MagicMock(path="/test")}, "/test"),
            # Test with path_info attribute
            ({"path_info": "/test"}, "/test"),
            # Test with no path attributes
            ({}, ""),
        ],
    )
    def test_get_request_path(self, request_attrs, expected):
        """Test request path extraction."""
        mock_request = MagicMock()

        # Configure the mock to return empty string for non-existent attributes
        mock_request.path = ""
        mock_request.path_info = ""
        mock_request.url.path = ""

        # Set up the mock request with the specified attributes
        for attr, value in request_attrs.items():
            if attr == "url":
                # Special handling for url attribute
                mock_url = MagicMock()
                mock_url.path = value.path
                setattr(mock_request, attr, mock_url)
            else:
                # Set the attribute directly
                setattr(mock_request, attr, value)

        result = get_request_path(mock_request)
        assert result == expected

"""Tests for PyWebGuard security components."""

import pytest
from typing import Dict, Any, cast

from pywebguard.security.penetration import (
    PenetrationDetector,
    AsyncPenetrationDetector,
)
from pywebguard.security.cors import CORSHandler, AsyncCORSHandler
from pywebguard.core.config import PenetrationDetectionConfig, CORSConfig
from pywebguard.storage.memory import MemoryStorage, AsyncMemoryStorage
from tests.conftest import MockRequest, MockResponse


class TestPenetrationDetector:
    """Tests for PenetrationDetector."""

    @pytest.fixture
    def penetration_config(self) -> PenetrationDetectionConfig:
        """Create a penetration detection configuration for testing."""
        return PenetrationDetectionConfig(
            enabled=True,
            log_suspicious=True,
            suspicious_patterns=[
                r"(?i)(?:union\s+select|select\s+.*\s+from)",  # SQL injection
                r"(?i)(?:<script>|javascript:|onerror=|onload=)",  # XSS
                r"(?i)(?:\.\.\/|\.\.\\|\/etc\/passwd)",  # Path traversal
            ],
        )

    @pytest.fixture
    def penetration_detector(
        self, penetration_config: PenetrationDetectionConfig
    ) -> PenetrationDetector:
        """Create a penetration detector for testing."""
        return PenetrationDetector(penetration_config, MemoryStorage())

    def test_initialization(
        self,
        penetration_detector: PenetrationDetector,
        penetration_config: PenetrationDetectionConfig,
    ):
        """Test PenetrationDetector initialization."""
        assert penetration_detector.config == penetration_config
        assert len(penetration_detector.patterns) == 3

    def test_check_request(self, penetration_detector: PenetrationDetector):
        """Test penetration detection."""
        # Test normal request
        request_info = {
            "ip": "127.0.0.1",
            "user_agent": "Mozilla/5.0",
            "method": "GET",
            "path": "/api/users",
            "query": {},
            "headers": {},
        }
        result = penetration_detector.check_request(request_info)
        assert result["allowed"] is True

        # Test SQL injection in path
        request_info["path"] = (
            "/api/users?id=1 UNION SELECT username,password FROM users"
        )
        result = penetration_detector.check_request(request_info)
        assert result["allowed"] is False
        assert result["reason"] == "Suspicious path detected"

        # Test XSS in query parameter
        request_info["path"] = "/api/users"
        request_info["query"] = {"name": "<script>alert('XSS')</script>"}
        result = penetration_detector.check_request(request_info)
        assert result["allowed"] is False
        assert result["reason"] == "Suspicious query parameter detected"

        # Test path traversal in header
        request_info["query"] = {}
        request_info["headers"] = {"Referer": "../../etc/passwd"}
        result = penetration_detector.check_request(request_info)
        assert result["allowed"] is False
        assert result["reason"] == "Suspicious header detected"

        # Test with detector disabled
        penetration_detector.config.enabled = False
        request_info["path"] = (
            "/api/users?id=1 UNION SELECT username,password FROM users"
        )
        result = penetration_detector.check_request(request_info)
        assert result["allowed"] is True

    def test_check_suspicious_patterns(self, penetration_detector: PenetrationDetector):
        """Test checking for suspicious patterns."""
        # Test SQL injection
        assert (
            penetration_detector._check_suspicious_patterns("SELECT * FROM users")
            is True
        )
        assert (
            penetration_detector._check_suspicious_patterns(
                "UNION SELECT username,password FROM users"
            )
            is True
        )

        # Test XSS
        assert (
            penetration_detector._check_suspicious_patterns(
                "<script>alert('XSS')</script>"
            )
            is True
        )
        assert (
            penetration_detector._check_suspicious_patterns("javascript:alert('XSS')")
            is True
        )

        # Test path traversal
        assert (
            penetration_detector._check_suspicious_patterns("../../etc/passwd") is True
        )
        assert (
            penetration_detector._check_suspicious_patterns("../../../etc/shadow")
            is True
        )

        # Test normal text
        assert penetration_detector._check_suspicious_patterns("Hello, world!") is False
        assert penetration_detector._check_suspicious_patterns("user123") is False

        # Test empty text
        assert penetration_detector._check_suspicious_patterns("") is False
        assert penetration_detector._check_suspicious_patterns(None) is False

        # Test non-string
        assert penetration_detector._check_suspicious_patterns(123) is False


class TestAsyncPenetrationDetector:
    """Tests for AsyncPenetrationDetector."""

    @pytest.fixture
    def penetration_config(self) -> PenetrationDetectionConfig:
        """Create a penetration detection configuration for testing."""
        return PenetrationDetectionConfig(
            enabled=True,
            log_suspicious=True,
            suspicious_patterns=[
                r"(?i)(?:union\s+select|select\s+.*\s+from)",  # SQL injection
                r"(?i)(?:<script>|javascript:|onerror=|onload=)",  # XSS
                r"(?i)(?:\.\.\/|\.\.\\|\/etc\/passwd)",  # Path traversal
            ],
        )

    @pytest.fixture
    def async_penetration_detector(
        self, penetration_config: PenetrationDetectionConfig
    ) -> AsyncPenetrationDetector:
        """Create an async penetration detector for testing."""
        return AsyncPenetrationDetector(penetration_config, AsyncMemoryStorage())

    def test_initialization(
        self,
        async_penetration_detector: AsyncPenetrationDetector,
        penetration_config: PenetrationDetectionConfig,
    ):
        """Test AsyncPenetrationDetector initialization."""
        assert async_penetration_detector.config == penetration_config
        assert len(async_penetration_detector.patterns) == 3

    @pytest.mark.asyncio
    async def test_check_request(
        self, async_penetration_detector: AsyncPenetrationDetector
    ):
        """Test async penetration detection."""
        # Test normal request
        request_info = {
            "ip": "127.0.0.1",
            "user_agent": "Mozilla/5.0",
            "method": "GET",
            "path": "/api/users",
            "query": {},
            "headers": {},
        }
        result = await async_penetration_detector.check_request(request_info)
        assert result["allowed"] is True

        # Test SQL injection in path
        request_info["path"] = (
            "/api/users?id=1 UNION SELECT username,password FROM users"
        )
        result = await async_penetration_detector.check_request(request_info)
        assert result["allowed"] is False
        assert result["reason"] == "Suspicious path detected"

    def test_check_suspicious_patterns(
        self, async_penetration_detector: AsyncPenetrationDetector
    ):
        """Test checking for suspicious patterns."""
        # Test SQL injection
        assert (
            async_penetration_detector._check_suspicious_patterns("SELECT * FROM users")
            is True
        )

        # Test normal text
        assert (
            async_penetration_detector._check_suspicious_patterns("Hello, world!")
            is False
        )


class TestCORSHandler:
    """Tests for CORSHandler."""

    @pytest.fixture
    def cors_config(self) -> CORSConfig:
        """Create a CORS configuration for testing."""
        return CORSConfig(
            enabled=True,
            allow_origins=["https://example.com", "https://*.test.com"],
            allow_methods=["GET", "POST", "PUT"],
            allow_headers=["Content-Type", "Authorization"],
            allow_credentials=True,
            max_age=600,
        )

    @pytest.fixture
    def cors_handler(self, cors_config: CORSConfig) -> CORSHandler:
        """Create a CORS handler for testing."""
        return CORSHandler(cors_config)

    def test_initialization(self, cors_handler: CORSHandler, cors_config: CORSConfig):
        """Test CORSHandler initialization."""
        assert cors_handler.config == cors_config

    def test_get_origin(self, cors_handler: CORSHandler):
        """Test getting the origin from a request."""
        # Test with origin header
        request = MockRequest(headers={"Origin": "https://example.com"})
        assert cors_handler._get_origin(request) == "https://example.com"

        # Test without origin header
        request = MockRequest()
        assert cors_handler._get_origin(request) == "*"

    def test_set_cors_headers(self, cors_handler: CORSHandler):
        """Test setting CORS headers on a response."""
        response = MockResponse()

        # Test with allowed origin
        cors_handler._set_cors_headers(response, "https://example.com")
        assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"
        assert response.headers["Access-Control-Allow-Methods"] == "GET, POST, PUT"
        assert (
            response.headers["Access-Control-Allow-Headers"]
            == "Content-Type, Authorization"
        )
        assert response.headers["Access-Control-Allow-Credentials"] == "true"
        assert response.headers["Access-Control-Max-Age"] == "600"

        # Test with wildcard domain
        response = MockResponse()
        cors_handler._set_cors_headers(response, "https://sub.test.com")
        assert response.headers["Access-Control-Allow-Origin"] == "*"
        assert response.headers["Access-Control-Allow-Methods"] == "GET, POST, PUT"
        assert (
            response.headers["Access-Control-Allow-Headers"]
            == "Content-Type, Authorization"
        )
        assert response.headers["Access-Control-Allow-Credentials"] == "true"
        assert response.headers["Access-Control-Max-Age"] == "600"

    def test_add_cors_headers(self, cors_handler: CORSHandler):
        """Test adding CORS headers to a response."""
        request = MockRequest(headers={"Origin": "https://example.com"})
        response = MockResponse()

        # Test with enabled CORS
        cors_handler.add_cors_headers(request, response)
        assert "Access-Control-Allow-Origin" in response.headers

        # Test with disabled CORS
        cors_handler.config.enabled = False
        response = MockResponse()
        cors_handler.add_cors_headers(request, response)
        assert "Access-Control-Allow-Origin" not in response.headers


class TestAsyncCORSHandler:
    """Tests for AsyncCORSHandler."""

    @pytest.fixture
    def cors_config(self) -> CORSConfig:
        """Create a CORS configuration for testing."""
        return CORSConfig(
            enabled=True,
            allow_origins=["https://example.com"],
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
            allow_credentials=True,
            max_age=600,
        )

    @pytest.fixture
    def async_cors_handler(self, cors_config: CORSConfig) -> AsyncCORSHandler:
        """Create an async CORS handler for testing."""
        return AsyncCORSHandler(cors_config)

    def test_initialization(
        self, async_cors_handler: AsyncCORSHandler, cors_config: CORSConfig
    ):
        """Test AsyncCORSHandler initialization."""
        assert async_cors_handler.config == cors_config

    @pytest.mark.asyncio
    async def test_add_cors_headers(self, async_cors_handler: AsyncCORSHandler):
        """Test adding CORS headers to a response asynchronously."""
        request = MockRequest(headers={"Origin": "https://example.com"})
        response = MockResponse()

        # Test with enabled CORS
        await async_cors_handler.add_cors_headers(request, response)
        assert "Access-Control-Allow-Origin" in response.headers

        # Test with disabled CORS
        async_cors_handler.config.enabled = False
        response = MockResponse()
        await async_cors_handler.add_cors_headers(request, response)
        assert "Access-Control-Allow-Origin" not in response.headers

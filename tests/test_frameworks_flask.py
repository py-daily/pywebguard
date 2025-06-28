"""Tests for Flask framework integration."""

import pytest
from typing import Dict, Any
import time

# Try to import Flask if available
try:
    import flask
    from flask import Flask, request
    from flask.testing import FlaskClient
    from pywebguard.frameworks._flask import FlaskGuard

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from pywebguard.core.config import (
    GuardConfig,
    IPFilterConfig,
    RateLimitConfig,
    UserAgentConfig,
    CORSConfig,
    PenetrationDetectionConfig,
)
from pywebguard.storage.memory import MemoryStorage


# Only run Flask tests if Flask is available
if FLASK_AVAILABLE:

    class TestFlaskGuard:
        """Tests for FlaskGuard."""

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
            )

        @pytest.fixture
        def flask_app(self, basic_config: GuardConfig) -> Flask:
            """Create a Flask app with PyWebGuard extension."""
            app = Flask(__name__)

            # Add PyWebGuard extension
            FlaskGuard(
                app,
                config=basic_config,
                storage=MemoryStorage(),
            )

            # Add some routes
            @app.route("/")
            def root():
                return {"message": "Hello World"}

            @app.route("/api/users")
            def get_users():
                return {"users": ["user1", "user2"]}

            return app

        @pytest.fixture
        def test_client(self, flask_app: Flask) -> FlaskClient:
            """Create a test client for the Flask app."""
            return flask_app.test_client()

        def test_allowed_request(self, test_client: FlaskClient):
            """Test that allowed requests are processed."""
            response = test_client.get("/")
            assert response.status_code == 200
            assert response.json == {"message": "Hello World"}

            response = test_client.get("/api/users")
            assert response.status_code == 200
            assert response.json == {"users": ["user1", "user2"]}

        def test_rate_limiting(self, test_client: FlaskClient, flask_app: Flask):
            """Test rate limiting in Flask extension."""
            # Create a new app with a very low rate limit
            app = Flask(__name__)

            # Add PyWebGuard extension with a very low rate limit
            FlaskGuard(
                app,
                config=GuardConfig(
                    ip_filter=IPFilterConfig(
                        enabled=True,
                        whitelist=["127.0.0.1"],
                    ),
                    rate_limit=RateLimitConfig(
                        enabled=True,
                        requests_per_minute=1,  # Very low rate limit
                        burst_size=0,
                    ),
                ),
                storage=MemoryStorage(),
            )

            # Add a route
            @app.route("/")
            def root():
                return {"message": "Hello World"}

            # Create a test client
            client = app.test_client()

            # First request should be allowed
            response = client.get("/", headers={"User-Agent": "Test User Agent"})
            assert response.status_code == 200

            # Second request should be rate limited
            response = client.get("/", headers={"User-Agent": "Test User Agent"})
            assert response.status_code == 429
            assert "rate limit" in response.json["reason"].lower()

        def test_route_specific_rate_limiting(
            self, test_client: FlaskClient, flask_app: Flask
        ):
            """Test route-specific rate limiting in Flask extension."""
            # Create a new app with route-specific rate limits
            app = Flask(__name__)

            # Add PyWebGuard extension with route-specific rate limits
            FlaskGuard(
                app,
                config=GuardConfig(
                    ip_filter=IPFilterConfig(
                        enabled=True,
                        whitelist=["127.0.0.1"],
                    ),
                    rate_limit=RateLimitConfig(
                        enabled=True,
                        requests_per_minute=10,  # High default rate limit
                        burst_size=5,
                    ),
                ),
                storage=MemoryStorage(),
                route_rate_limits=[
                    {
                        "endpoint": "/api/limited",
                        "requests_per_minute": 1,  # Very low rate limit for this route
                        "burst_size": 0,
                    },
                ],
            )

            # Add routes
            @app.route("/")
            def root():
                return {"message": "Hello World"}

            @app.route("/api/limited")
            def limited():
                return {"message": "Limited Route"}

            # Create a test client
            client = app.test_client()

            # First request to limited route should be allowed
            response = client.get(
                "/api/limited", headers={"User-Agent": "Test User Agent"}
            )
            assert response.status_code == 200

            # Second request to limited route should be rate limited
            response = client.get(
                "/api/limited", headers={"User-Agent": "Test User Agent"}
            )
            assert response.status_code == 429
            assert "rate limit" in response.json["reason"].lower()

            # Requests to other routes should still be allowed
            for _ in range(5):
                response = client.get("/", headers={"User-Agent": "Test User Agent"})
                assert response.status_code == 200

        def test_ip_filtering(self, flask_app: Flask):
            """Test IP filtering in Flask extension."""
            app = Flask(__name__)

            # Add PyWebGuard extension with IP filtering
            FlaskGuard(
                app,
                config=GuardConfig(
                    ip_filter=IPFilterConfig(
                        enabled=True,
                        whitelist=["127.0.0.1"],
                        blacklist=["10.0.0.1"],
                    ),
                ),
                storage=MemoryStorage(),
            )

            @app.route("/")
            def root():
                return {"message": "Hello World"}

            client = app.test_client()

            # Test whitelisted IP (should be allowed)
            response = client.get("/", environ_base={"REMOTE_ADDR": "127.0.0.1"})
            assert response.status_code == 200

            # Test blacklisted IP (should be blocked)
            response = client.get("/", environ_base={"REMOTE_ADDR": "10.0.0.1"})
            assert response.status_code == 403
            assert "ip in blacklist" in response.json["reason"].lower()

        def test_user_agent_filtering(self, flask_app: Flask):
            """Test user agent filtering in Flask extension."""
            app = Flask(__name__)

            # Add PyWebGuard extension with user agent filtering
            FlaskGuard(
                app,
                config=GuardConfig(
                    user_agent=UserAgentConfig(
                        enabled=True,
                        blocked_agents=["curl", "wget", "bot"],
                    ),
                ),
                storage=MemoryStorage(),
            )

            @app.route("/")
            def root():
                return {"message": "Hello World"}

            client = app.test_client()

            # Test allowed user agent
            response = client.get("/", headers={"User-Agent": "Mozilla/5.0"})
            assert response.status_code == 200

            # Test blocked user agent
            response = client.get("/", headers={"User-Agent": "curl/7.64.1"})
            assert response.status_code == 403
            assert "user agent" in response.json["reason"].lower()

        def test_cors_handling(self, flask_app: Flask):
            """Test CORS handling in Flask extension."""
            app = Flask(__name__)

            # Add PyWebGuard extension with CORS enabled
            FlaskGuard(
                app,
                config=GuardConfig(
                    cors=CORSConfig(
                        enabled=True,
                        allow_origins=["http://localhost:3000"],
                        allow_methods=["GET", "POST"],
                        allow_headers=["Content-Type"],
                    ),
                ),
                storage=MemoryStorage(),
            )

            @app.route("/")
            def root():
                return {"message": "Hello World"}

            client = app.test_client()

            # Test OPTIONS request (preflight)
            response = client.options(
                "/",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                },
            )
            assert response.status_code == 200
            assert "Access-Control-Allow-Origin" in response.headers
            assert (
                response.headers["Access-Control-Allow-Origin"]
                == "http://localhost:3000"
            )

        def test_penetration_detection(self, flask_app: Flask):
            """Test penetration detection in Flask extension."""
            app = Flask(__name__)

            # Add PyWebGuard extension with penetration detection
            FlaskGuard(
                app,
                config=GuardConfig(
                    penetration=PenetrationDetectionConfig(
                        enabled=True,
                        log_suspicious=True,
                    ),
                ),
                storage=MemoryStorage(),
            )

            @app.route("/search")
            def search():
                return {"message": "Search results"}

            client = app.test_client()

            # Test SQL injection attempt
            response = client.get("/search?q=1' OR '1'='1", headers={"User-Agent": "Mozilla/5.0"})
            assert response.status_code == 403
            assert "suspicious query parameter detected" in response.json["reason"].lower()

            # Test XSS attempt
            response = client.get("/search?q=<script>alert('xss')</script>", headers={"User-Agent": "Mozilla/5.0"})
            assert response.status_code == 403
            assert "suspicious query parameter detected" in response.json["reason"].lower()

        def test_custom_response_handler(self, flask_app: Flask):
            """Test custom response handler in Flask extension."""
            app = Flask(__name__)

            def custom_handler(request, reason):
                return {"custom_error": reason, "timestamp": time.time()}, 418

            # Add PyWebGuard extension with custom response handler
            FlaskGuard(
                app,
                config=GuardConfig(
                    rate_limit=RateLimitConfig(
                        enabled=True,
                        requests_per_minute=1,
                        burst_size=0,
                    ),
                ),
                storage=MemoryStorage(),
                custom_response_handler=custom_handler,
            )

            @app.route("/")
            def root():
                return {"message": "Hello World"}

            client = app.test_client()

            # First request should be allowed
            response = client.get("/")
            assert response.status_code == 200

            # Second request should use custom handler
            response = client.get("/")
            assert response.status_code == 418
            assert "custom_error" in response.json
            assert "timestamp" in response.json

        def test_security_headers(self, flask_app: Flask):
            """Test security headers in Flask extension."""
            app = Flask(__name__)

            # Add PyWebGuard extension
            FlaskGuard(
                app,
                config=GuardConfig(),
                storage=MemoryStorage(),
            )

            @app.route("/")
            def root():
                return {"message": "Hello World"}

            client = app.test_client()

            response = client.get("/")
            assert response.status_code == 200
            assert "X-Content-Type-Options" in response.headers
            assert "X-Frame-Options" in response.headers
            assert "X-XSS-Protection" in response.headers
            assert "Referrer-Policy" in response.headers
            assert "Permissions-Policy" in response.headers

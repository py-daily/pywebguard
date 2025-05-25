"""Tests for Flask framework integration."""

import pytest
from typing import Dict, Any

# Try to import Flask if available
try:
    import flask
    from flask import Flask, request
    from flask.testing import FlaskClient
    from pywebguard.frameworks._flask import FlaskGuard

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from pywebguard.core.config import GuardConfig, IPFilterConfig, RateLimitConfig
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
            assert response.status_code == 403
            assert "rate limit" in response.json["reason"]["reason"].lower()

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
            assert response.status_code == 403
            assert "rate limit" in response.json["reason"]["reason"].lower()

            # Requests to other routes should still be allowed
            for _ in range(5):
                response = client.get("/", headers={"User-Agent": "Test User Agent"})
                assert response.status_code == 200

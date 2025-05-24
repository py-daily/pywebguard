"""
Example of using PyWebGuard with Flask and PostgreSQL storage.

This example demonstrates how to use PyWebGuard with Flask and PostgreSQL storage,
including environment variable configuration.

To run this example:
    pip install flask pywebguard psycopg2-binary

    # Set environment variables
    export PYWEBGUARD_STORAGE_TYPE=postgresql
    export PYWEBGUARD_STORAGE_URL=postgresql://postgres:postgres@localhost:5432/pywebguard

    python postgresql_example.py
"""

from flask import Flask, request, jsonify, Response
import time
import os
import logging
from typing import Dict, List, Optional, Union, Any

# Import PyWebGuard components
from pywebguard import FlaskGuard, GuardConfig
from pywebguard.storage._postgresql import PostgreSQLStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pywebguard-postgresql-example")

# Create Flask app
app = Flask(__name__)

# Load configuration from environment variables
config = GuardConfig.from_env()

# Override with specific settings if needed
config.rate_limit.requests_per_minute = 100
config.rate_limit.burst_size = 20

# Define route-specific rate limits
route_rate_limits = [
    {
        "endpoint": "/api/limited",
        "requests_per_minute": 5,
        "burst_size": 2,
    },
    {
        "endpoint": "/api/admin/*",
        "requests_per_minute": 20,
        "burst_size": 5,
    },
]


# Custom response handler for blocked requests
def custom_response_handler(reason: str) -> Response:
    """Custom handler for blocked requests."""
    status_code = 429 if "rate limit" in reason.lower() else 403

    response = jsonify(
        {
            "error": "Request blocked",
            "reason": reason,
            "timestamp": time.time(),
            "path": request.path,
        }
    )
    response.status_code = status_code
    return response


# Initialize PyWebGuard with PostgreSQL storage
# Note: The storage will be created automatically from environment variables
# if PYWEBGUARD_STORAGE_TYPE and PYWEBGUARD_STORAGE_URL are set
guard = FlaskGuard(
    app,
    config=config,
    route_rate_limits=route_rate_limits,
    response_handler=custom_response_handler,
)


# Basic routes
@app.route("/")
def root():
    """Root endpoint with default rate limit."""
    return jsonify(
        {
            "message": "Hello from PyWebGuard with PostgreSQL storage",
            "storage_type": os.environ.get("PYWEBGUARD_STORAGE_TYPE", "default"),
            "storage_url": os.environ.get("PYWEBGUARD_STORAGE_URL", "default"),
        }
    )


@app.route("/api/limited")
def limited_endpoint():
    """Strictly rate limited endpoint (5 req/min)."""
    return jsonify({"message": "This endpoint is strictly rate limited (5 req/min)"})


@app.route("/api/admin/dashboard")
def admin_dashboard():
    """Admin dashboard with custom rate limit (20 req/min)."""
    return jsonify({"message": "Admin dashboard with custom rate limit (20 req/min)"})


# Helper endpoint to check remaining rate limits
@app.route("/rate-limit-status")
def rate_limit_status():
    """Check rate limit status for a specific path."""
    client_ip = request.remote_addr
    path = request.args.get("path", "/")

    # Get rate limit info for the specified path
    rate_info = guard.guard.rate_limiter.check_limit(client_ip, path)

    return jsonify(
        {
            "path": path,
            "allowed": rate_info["allowed"],
            "remaining": rate_info["remaining"],
            "reset": rate_info["reset"],
            "client_ip": client_ip,
        }
    )


# Admin endpoint to ban an IP
@app.route("/admin/ban-ip", methods=["POST"])
def ban_ip():
    """Ban an IP address."""
    # This would typically be protected by authentication
    data = request.get_json()
    ip = data.get("ip")
    duration = data.get("duration", 3600)

    if not ip:
        return jsonify({"error": "IP address is required"}), 400

    ban_key = f"banned_ip:{ip}"
    guard.guard.storage.set(
        ban_key,
        {"reason": "Manually banned via API", "timestamp": time.time()},
        duration,
    )

    return jsonify(
        {
            "message": f"IP {ip} banned for {duration} seconds",
            "timestamp": time.time(),
        }
    )


# Admin endpoint to unban an IP
@app.route("/admin/unban-ip", methods=["POST"])
def unban_ip():
    """Unban an IP address."""
    # This would typically be protected by authentication
    data = request.get_json()
    ip = data.get("ip")

    if not ip:
        return jsonify({"error": "IP address is required"}), 400

    ban_key = f"banned_ip:{ip}"
    guard.guard.storage.delete(ban_key)

    return jsonify(
        {
            "message": f"IP {ip} unbanned",
            "timestamp": time.time(),
        }
    )


if __name__ == "__main__":
    logger.info("Starting PyWebGuard Flask example with PostgreSQL storage...")
    logger.info(f"Storage type: {os.environ.get('PYWEBGUARD_STORAGE_TYPE', 'default')}")
    logger.info(f"Storage URL: {os.environ.get('PYWEBGUARD_STORAGE_URL', 'default')}")
    app.run(host="0.0.0.0", port=8000, debug=True)

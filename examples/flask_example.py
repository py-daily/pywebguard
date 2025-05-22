"""
Example of using PyWebGuard with Flask.

This example demonstrates comprehensive integration of PyWebGuard with Flask,
including all major features:
- Route-specific rate limiting
- IP filtering
- User agent filtering
- CORS configuration
- Penetration detection
- Metrics and monitoring
- Custom response handling
- Storage backend options

To run this example:
    pip install flask pywebguard
    python flask_example.py
"""

from flask import Flask, request, jsonify, Response
import time
import logging
from typing import Dict, List, Optional, Union, Any, Callable

# Import PyWebGuard components
from pywebguard import FlaskGuard, GuardConfig, RateLimitConfig
from pywebguard.storage.memory import MemoryStorage

# Uncomment to use other storage backends
# from pywebguard.storage.redis import RedisStorage
# from pywebguard.storage.sqlite import SQLiteStorage
# from pywebguard.storage.tinydb import TinyDBStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pywebguard-example")

# Create Flask app
app = Flask(__name__)

# Configure PyWebGuard with detailed settings
config = GuardConfig(
    # IP filtering configuration
    ip_filter={
        "enabled": True,
        "whitelist": ["127.0.0.1", "::1", "192.168.1.0/24"],
        "blacklist": ["10.0.0.1", "172.16.0.0/16"],
    },
    # Global rate limiting configuration
    rate_limit={
        "enabled": True,
        "requests_per_minute": 100,
        "burst_size": 20,
        "auto_ban_threshold": 200,
        "auto_ban_duration": 3600,  # 1 hour in seconds
    },
    # User agent filtering
    user_agent={
        "enabled": True,
        "blocked_agents": ["curl/7.*", "wget", "Scrapy", "bot", "Bot"],
    },
    # CORS configuration
    cors={
        "enabled": True,
        "allow_origins": ["http://localhost:3000", "https://example.com"],
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "allow_credentials": True,
        "max_age": 3600,
    },
    # Penetration detection
    penetration={
        "enabled": True,
        "detect_sql_injection": True,
        "detect_xss": True,
        "detect_path_traversal": True,
        "block_suspicious_requests": True,
    },
    # Logging configuration
    logging={
        "enabled": True,
        "level": "INFO",
        "log_blocked_requests": True,
    },
)

# Define route-specific rate limits
route_rate_limits = [
    {
        "endpoint": "/api/limited",
        "requests_per_minute": 5,
        "burst_size": 2,
        "auto_ban_threshold": 10,
        "auto_ban_duration": 1800,  # 30 minutes
    },
    {
        "endpoint": "/api/uploads/*",
        "requests_per_minute": 10,
        "burst_size": 5,
        "auto_ban_duration": 1800,
    },
    {
        "endpoint": "/api/admin/**",
        "requests_per_minute": 20,
        "burst_size": 5,
        "auto_ban_threshold": 50,
        "auto_ban_duration": 7200,  # 2 hours
    },
]

# Initialize storage (in-memory for this example)
storage = MemoryStorage()

# Uncomment to use other storage backends
# Redis Storage
# storage = RedisStorage(
#     host="localhost",
#     port=6379,
#     db=0,
#     password=None,
#     prefix="pywebguard:",
# )

# SQLite Storage
# storage = SQLiteStorage(
#     db_path="pywebguard.db",
#     table_prefix="pywebguard_",
# )

# TinyDB Storage
# storage = TinyDBStorage(
#     db_path="pywebguard.json",
# )


# Custom response handler for blocked requests
def custom_response_handler(reason: str) -> Response:
    """
    Custom handler for blocked requests.

    Args:
        reason: The reason the request was blocked

    Returns:
        A custom JSON response with details about why the request was blocked
    """
    status_code = 429 if "rate limit" in reason.lower() else 403

    response = jsonify(
        {
            "error": "Request blocked",
            "reason": reason,
            "timestamp": time.time(),
            "path": request.path,
            "method": request.method,
        }
    )
    response.status_code = status_code
    return response


# Initialize PyWebGuard with route-specific rate limits
guard = FlaskGuard(
    app,
    config=config,
    storage=storage,
    route_rate_limits=route_rate_limits,
    response_handler=custom_response_handler,
)


# Basic routes
@app.route("/")
def root():
    """Root endpoint with default rate limit (100 req/min)"""
    return jsonify({"message": "Hello World - Default rate limit (100 req/min)"})


@app.route("/api/limited")
def limited_endpoint():
    """Strictly rate limited endpoint (5 req/min)"""
    return jsonify({"message": "This endpoint is strictly rate limited (5 req/min)"})


@app.route("/api/uploads/files")
def upload_files():
    """File upload endpoint with custom rate limit (10 req/min)"""
    return jsonify(
        {"message": "File upload endpoint with custom rate limit (10 req/min)"}
    )


@app.route("/api/admin/dashboard")
def admin_dashboard():
    """Admin dashboard with custom rate limit (20 req/min)"""
    return jsonify({"message": "Admin dashboard with custom rate limit (20 req/min)"})


@app.route("/api/admin/users/list")
def admin_users():
    """Admin users list with custom rate limit (20 req/min)"""
    return jsonify({"message": "Admin users list with custom rate limit (20 req/min)"})


@app.route("/protected")
def protected():
    """Protected endpoint with default rate limit"""
    return jsonify(
        {
            "message": "This is a protected endpoint with default rate limit",
            "client_ip": request.remote_addr,
            "user_agent": request.user_agent.string,
        }
    )


# Helper endpoint to check remaining rate limits
@app.route("/rate-limit-status")
def rate_limit_status():
    """
    Check rate limit status for a specific path

    Returns:
        Rate limit information for the specified path
    """
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


# Endpoint to check if an IP is banned
@app.route("/check-ban-status")
def check_ban_status():
    """
    Check if an IP is banned

    Returns:
        Ban status information
    """
    check_ip = request.args.get("ip", request.remote_addr)
    is_banned = guard.guard.is_ip_banned(check_ip)

    return jsonify(
        {
            "ip": check_ip,
            "is_banned": is_banned,
            "timestamp": time.time(),
        }
    )


# Admin endpoint to get metrics
@app.route("/admin/metrics")
def get_metrics():
    """
    Get PyWebGuard metrics

    Returns:
        Current metrics from PyWebGuard
    """
    # This would typically be protected by authentication
    metrics = guard.guard.get_metrics()

    return jsonify(
        {
            "timestamp": time.time(),
            "metrics": metrics,
        }
    )


# Admin endpoint to ban an IP
@app.route("/admin/ban-ip", methods=["POST"])
def ban_ip():
    """
    Ban an IP address

    Returns:
        Ban confirmation
    """
    # This would typically be protected by authentication
    data = request.get_json()
    ip = data.get("ip")
    duration = data.get("duration", 3600)

    if not ip:
        return jsonify({"error": "IP address is required"}), 400

    guard.guard.ban_ip(ip, duration)

    return jsonify(
        {
            "message": f"IP {ip} banned for {duration} seconds",
            "timestamp": time.time(),
        }
    )


# Admin endpoint to unban an IP
@app.route("/admin/unban-ip", methods=["POST"])
def unban_ip():
    """
    Unban an IP address

    Returns:
        Unban confirmation
    """
    # This would typically be protected by authentication
    data = request.get_json()
    ip = data.get("ip")

    if not ip:
        return jsonify({"error": "IP address is required"}), 400

    guard.guard.unban_ip(ip)

    return jsonify(
        {
            "message": f"IP {ip} unbanned",
            "timestamp": time.time(),
        }
    )


# Example of a path that might trigger penetration detection
@app.route("/search")
def search():
    """
    Search endpoint that might trigger penetration detection if malicious queries are used

    Returns:
        Search results
    """
    # PyWebGuard will check for SQL injection, XSS, etc. in the query parameter
    q = request.args.get("q", "")
    return jsonify({"results": f"Search results for: {q}"})


if __name__ == "__main__":
    logger.info("Starting PyWebGuard Flask example server...")
    app.run(host="0.0.0.0", port=8000, debug=True)

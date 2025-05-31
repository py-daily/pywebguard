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

# Configure PyWebGuard
config = GuardConfig(
    ip_filter={
        "enabled": True,
        "whitelist": ["127.0.0.1", "::1"],  # Allow localhost
        "blacklist": [],  # No blacklisted IPs
    },
    rate_limit={
        "enabled": True,
        "requests_per_minute": 60,  # 60 requests per minute
        "burst_size": 10,  # Allow bursts of 10 requests
        "auto_ban_threshold": 100,  # Ban after 100 requests
        "auto_ban_duration": 3600,  # Ban for 1 hour
    },
    user_agent={
        "enabled": True,
        "blocked_agents": ["curl", "wget", "Scrapy"],  # Block common scraping tools
    },
    cors={
        "enabled": True,
        "allow_origins": ["*"],  # Allow all origins for testing
        "allow_methods": ["*"],  # Allow all methods
        "allow_headers": ["*"],  # Allow all headers
    },
    penetration={
        "enabled": True,
        "detect_sql_injection": True,
        "detect_xss": True,
        "detect_path_traversal": True,
    },
    logging={
        "enabled": True,
        "level": "DEBUG",
        "log_blocked_requests": True,
    },
)

# Configure route-specific rate limits
route_rate_limits = [
    {
        "endpoint": "/api/sensitive",
        "requests_per_minute": 10,  # More strict rate limit for sensitive endpoint
        "burst_size": 2,
        "auto_ban_threshold": 20,
        "auto_ban_duration": 7200,  # 2 hours
    }
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

# Initialize PyWebGuard
guard = FlaskGuard(
    app,
    config=config,
    storage=storage,
    route_rate_limits=route_rate_limits,
)

# Basic routes
@app.route("/")
def root():
    """Root endpoint with default rate limit"""
    return jsonify({"message": "Hello World - Default rate limit (60 req/min)"})

@app.route("/api/sensitive")
def sensitive_endpoint():
    """Sensitive endpoint with stricter rate limit"""
    return jsonify({"message": "This is a sensitive endpoint - Rate limit (10 req/min)"})

@app.route("/api/blocked")
def blocked_endpoint():
    """This endpoint will be blocked by user agent filter"""
    return jsonify({"message": "This endpoint should be blocked for certain user agents"})

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
    """Check rate limit status for a specific path"""
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
    """Check if an IP is banned"""
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
    """Search endpoint that might trigger penetration detection"""
    q = request.args.get("q", "")
    return jsonify({"results": f"Search results for: {q}"})

if __name__ == "__main__":
    logger.info("Starting PyWebGuard Flask example server...")
    app.run(host="0.0.0.0", port=8000, debug=True)

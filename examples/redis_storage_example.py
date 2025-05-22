"""
Example of using PyWebGuard with Redis storage.

This example demonstrates how to use PyWebGuard with Redis storage
for both Flask and FastAPI frameworks.

To run this example:
    pip install flask fastapi uvicorn redis pywebguard
    python redis_storage_example.py
"""

import argparse
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pywebguard-redis-example")

# Import PyWebGuard components
from pywebguard import GuardConfig

# Parse command line arguments
parser = argparse.ArgumentParser(description="PyWebGuard Redis Storage Example")
parser.add_argument(
    "--framework",
    choices=["flask", "fastapi"],
    default="flask",
    help="Web framework to use (flask or fastapi)",
)
parser.add_argument("--host", default="localhost", help="Redis host")
parser.add_argument("--port", type=int, default=6379, help="Redis port")
parser.add_argument("--db", type=int, default=0, help="Redis database number")
parser.add_argument("--password", default=None, help="Redis password")
parser.add_argument("--prefix", default="pywebguard:", help="Redis key prefix")
args = parser.parse_args()

# Common configuration for both frameworks
config = GuardConfig(
    rate_limit={
        "requests_per_minute": 60,
        "burst_size": 10,
        "auto_ban_threshold": 120,
    },
    ip_filter={
        "whitelist": ["127.0.0.1", "::1"],
    },
    logging={
        "enabled": True,
        "level": "INFO",
    },
)

# Route-specific rate limits
route_rate_limits = [
    {
        "endpoint": "/api/*",
        "requests_per_minute": 30,
        "burst_size": 5,
    }
]

# Redis connection parameters
redis_params = {
    "host": args.host,
    "port": args.port,
    "db": args.db,
    "password": args.password,
    "prefix": args.prefix,
}

if args.framework == "flask":
    # Flask implementation
    from flask import Flask, request, jsonify
    from pywebguard import FlaskGuard
    from pywebguard.storage.redis import RedisStorage

    # Create Flask app
    app = Flask(__name__)

    # Initialize Redis storage
    storage = RedisStorage(**redis_params)

    # Initialize PyWebGuard
    guard = FlaskGuard(
        app, config=config, storage=storage, route_rate_limits=route_rate_limits
    )

    @app.route("/")
    def root():
        """Root endpoint"""
        return jsonify(
            {
                "message": "PyWebGuard with Redis Storage (Flask)",
                "client_ip": request.remote_addr,
            }
        )

    @app.route("/api/data")
    def api_data():
        """API endpoint with stricter rate limit"""
        return jsonify(
            {
                "message": "API data endpoint (30 req/min)",
                "timestamp": request.environ.get("REQUEST_TIME", 0),
            }
        )

    @app.route("/status")
    def status():
        """Check rate limit status"""
        client_ip = request.remote_addr
        path = request.args.get("path", "/")
        rate_info = guard.guard.rate_limiter.check_limit(client_ip, path)

        return jsonify(
            {
                "path": path,
                "allowed": rate_info["allowed"],
                "remaining": rate_info["remaining"],
                "reset": rate_info["reset"],
                "storage": "Redis",
                "redis_info": {
                    "host": args.host,
                    "port": args.port,
                    "db": args.db,
                    "prefix": args.prefix,
                },
            }
        )

    logger.info(
        f"Starting Flask server with Redis storage ({args.host}:{args.port}, db={args.db})"
    )
    app.run(host="0.0.0.0", port=8000, debug=True)

else:
    # FastAPI implementation
    import uvicorn
    from fastapi import FastAPI, Request
    from pywebguard import FastAPIGuard
    from pywebguard.storage.async_redis import AsyncRedisStorage

    # Create FastAPI app
    app = FastAPI(
        title="PyWebGuard Redis Storage Example",
        description="Example of using PyWebGuard with Redis storage in FastAPI",
    )

    # Initialize Redis storage
    storage = AsyncRedisStorage(**redis_params)

    # Initialize PyWebGuard
    guard_middleware = FastAPIGuard(
        app, config=config, storage=storage, route_rate_limits=route_rate_limits
    )

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "PyWebGuard with Redis Storage (FastAPI)",
        }

    @app.get("/api/data")
    async def api_data():
        """API endpoint with stricter rate limit"""
        return {
            "message": "API data endpoint (30 req/min)",
        }

    @app.get("/status")
    async def status(request: Request, path: str = "/"):
        """Check rate limit status"""
        client_ip = request.client.host
        rate_info = await guard_middleware.guard.rate_limiter.check_limit(
            client_ip, path
        )

        return {
            "path": path,
            "allowed": rate_info["allowed"],
            "remaining": rate_info["remaining"],
            "reset": rate_info["reset"],
            "storage": "Redis",
            "redis_info": {
                "host": args.host,
                "port": args.port,
                "db": args.db,
                "prefix": args.prefix,
            },
        }

    logger.info(
        f"Starting FastAPI server with Redis storage ({args.host}:{args.port}, db={args.db})"
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
Example comparing synchronous and asynchronous PyWebGuard implementations.

This example demonstrates the differences between synchronous (Flask) and
asynchronous (FastAPI) implementations of PyWebGuard, and how to choose
the appropriate components for each.

To run this example:
    pip install flask fastapi uvicorn pywebguard
    python async_sync_comparison.py [--async]
"""

import argparse
import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pywebguard-comparison")

# Import PyWebGuard components
from pywebguard import GuardConfig

# Parse command line arguments
parser = argparse.ArgumentParser(description="PyWebGuard Async/Sync Comparison")
parser.add_argument(
    "--async",
    dest="use_async",
    action="store_true",
    help="Use asynchronous implementation (FastAPI)",
)
args = parser.parse_args()

# Common configuration for both implementations
config = GuardConfig(
    rate_limit={
        "requests_per_minute": 60,
        "burst_size": 10,
    },
    ip_filter={
        "whitelist": ["127.0.0.1", "::1"],
    },
    logging={
        "enabled": True,
        "level": "INFO",
    },
)

if args.use_async:
    # Asynchronous implementation with FastAPI
    import asyncio
    import uvicorn
    from fastapi import FastAPI, Request
    from pywebguard import FastAPIGuard
    from pywebguard.storage.async_memory import AsyncMemoryStorage

    # Create FastAPI app
    app = FastAPI(
        title="PyWebGuard Async Implementation",
        description="Example of asynchronous PyWebGuard implementation with FastAPI",
    )

    # Initialize storage
    storage = AsyncMemoryStorage()

    # Initialize PyWebGuard
    guard_middleware = FastAPIGuard(app, config=config, storage=storage)

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "PyWebGuard Asynchronous Implementation (FastAPI)",
            "implementation": "async",
        }

    @app.get("/delay/{seconds}")
    async def delay(seconds: int, request: Request):
        """
        Endpoint that simulates an asynchronous delay

        Args:
            seconds: Number of seconds to delay

        Returns:
            Response after the delay
        """
        if seconds > 10:
            seconds = 10  # Cap at 10 seconds for safety

        # This is non-blocking in FastAPI
        await asyncio.sleep(seconds)

        return {
            "message": f"Completed after {seconds} second delay",
            "implementation": "async",
            "client_ip": request.client.host,
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
            "implementation": "async",
            "storage_type": "AsyncMemoryStorage",
        }

    logger.info("Starting FastAPI server with asynchronous PyWebGuard implementation")
    uvicorn.run(app, host="0.0.0.0", port=8000)

else:
    # Synchronous implementation with Flask
    from flask import Flask, request, jsonify
    from pywebguard import FlaskGuard
    from pywebguard.storage.memory import MemoryStorage

    # Create Flask app
    app = Flask(__name__)

    # Initialize storage
    storage = MemoryStorage()

    # Initialize PyWebGuard
    guard = FlaskGuard(app, config=config, storage=storage)

    @app.route("/")
    def root():
        """Root endpoint"""
        return jsonify(
            {
                "message": "PyWebGuard Synchronous Implementation (Flask)",
                "implementation": "sync",
            }
        )

    @app.route("/delay/<int:seconds>")
    def delay(seconds):
        """
        Endpoint that simulates a synchronous delay

        Args:
            seconds: Number of seconds to delay

        Returns:
            Response after the delay
        """
        if seconds > 10:
            seconds = 10  # Cap at 10 seconds for safety

        # This is blocking in Flask
        time.sleep(seconds)

        return jsonify(
            {
                "message": f"Completed after {seconds} second delay",
                "implementation": "sync",
                "client_ip": request.remote_addr,
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
                "implementation": "sync",
                "storage_type": "MemoryStorage",
            }
        )

    logger.info("Starting Flask server with synchronous PyWebGuard implementation")
    app.run(host="0.0.0.0", port=8000, debug=True)

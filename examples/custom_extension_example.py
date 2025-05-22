"""
Example of extending PyWebGuard with custom components.

This example demonstrates how to create custom filters, limiters, and
storage backends by extending the base classes provided by PyWebGuard.

To run this example:
    pip install flask pywebguard
    python custom_extension_example.py
"""

import time
import logging
import random
from typing import Dict, List, Optional, Union, Any, Callable
from flask import Flask, request, jsonify

# Import PyWebGuard components
from pywebguard import FlaskGuard, GuardConfig
from pywebguard.filters.base import BaseFilter
from pywebguard.limiters.base import BaseLimiter
from pywebguard.storage.base import BaseStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pywebguard-custom-example")


# Custom filter implementation
class TimeBasedFilter(BaseFilter):
    """
    Custom filter that blocks requests during specified time periods.

    This filter demonstrates how to create a custom filter by extending
    the BaseFilter class.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the time-based filter.

        Args:
            config: Configuration dictionary with the following keys:
                - enabled: Whether the filter is enabled
                - blocked_hours: List of hours (0-23) during which requests are blocked
                - blocked_days: List of days (0-6, where 0 is Monday) during which requests are blocked
        """
        super().__init__(config)
        self.blocked_hours = config.get("blocked_hours", [])
        self.blocked_days = config.get("blocked_days", [])
        logger.info(
            f"Initialized TimeBasedFilter with blocked hours: {self.blocked_hours}, blocked days: {self.blocked_days}"
        )

    def is_blocked(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if the request should be blocked based on the current time.

        Args:
            request_data: Dictionary containing request data

        Returns:
            Dictionary with 'blocked' and 'reason' keys
        """
        if not self.enabled:
            return {"blocked": False, "reason": None}

        # Get current time
        current_time = time.localtime()
        current_hour = current_time.tm_hour
        current_day = current_time.tm_wday  # 0 is Monday

        # Check if current hour is blocked
        if current_hour in self.blocked_hours:
            return {
                "blocked": True,
                "reason": f"Requests are not allowed during hour {current_hour}",
            }

        # Check if current day is blocked
        if current_day in self.blocked_days:
            return {
                "blocked": True,
                "reason": f"Requests are not allowed on day {current_day}",
            }

        return {"blocked": False, "reason": None}


# Custom limiter implementation
class RandomLimiter(BaseLimiter):
    """
    Custom limiter that randomly blocks requests with a specified probability.

    This limiter demonstrates how to create a custom limiter by extending
    the BaseLimiter class.
    """

    def __init__(self, config: Dict[str, Any], storage: BaseStorage):
        """
        Initialize the random limiter.

        Args:
            config: Configuration dictionary with the following keys:
                - enabled: Whether the limiter is enabled
                - probability: Probability (0-1) of blocking a request
            storage: Storage backend
        """
        super().__init__(config, storage)
        self.probability = config.get(
            "probability", 0.1
        )  # Default 10% chance of blocking
        logger.info(f"Initialized RandomLimiter with probability: {self.probability}")

    def is_limited(self, client_id: str, route: str) -> Dict[str, Any]:
        """
        Check if the request should be limited based on random probability.

        Args:
            client_id: Client identifier (usually IP address)
            route: Request route

        Returns:
            Dictionary with 'limited', 'reason', and other keys
        """
        if not self.enabled:
            return {"limited": False, "reason": None, "remaining": 1, "reset": 0}

        # Generate random number between 0 and 1
        random_value = random.random()

        # Check if request should be blocked
        if random_value < self.probability:
            return {
                "limited": True,
                "reason": f"Randomly limited (probability: {self.probability}, value: {random_value:.4f})",
                "remaining": 0,
                "reset": int(time.time()) + 5,  # Reset in 5 seconds
            }

        return {
            "limited": False,
            "reason": None,
            "remaining": 1,
            "reset": 0,
        }


# Create Flask app
app = Flask(__name__)

# Configure PyWebGuard with custom components
config = GuardConfig(
    # Standard configuration
    rate_limit={
        "enabled": True,
        "requests_per_minute": 60,
    },
    # Custom time-based filter configuration
    time_filter={
        "enabled": True,
        "blocked_hours": [3, 4, 5],  # Block requests from 3 AM to 5 AM
        "blocked_days": [6],  # Block requests on Sunday (day 6)
    },
    # Custom random limiter configuration
    random_limit={
        "enabled": True,
        "probability": 0.05,  # 5% chance of blocking
    },
)

# Initialize PyWebGuard with standard components
guard = FlaskGuard(app, config=config, storage=None)  # Will be set automatically

# Add custom filter to the guard
guard.guard.add_filter("time_filter", TimeBasedFilter(config.get("time_filter", {})))

# Add custom limiter to the guard
guard.guard.add_limiter(
    "random_limiter", RandomLimiter(config.get("random_limit", {}), guard.guard.storage)
)


# Basic routes
@app.route("/")
def root():
    """Root endpoint"""
    return jsonify(
        {
            "message": "PyWebGuard with custom extensions",
            "client_ip": request.remote_addr,
            "timestamp": time.time(),
        }
    )


@app.route("/random-test")
def random_test():
    """Test endpoint for random limiter"""
    return jsonify(
        {
            "message": "If you see this, you weren't randomly limited!",
            "timestamp": time.time(),
        }
    )


@app.route("/time-test")
def time_test():
    """Test endpoint for time-based filter"""
    current_time = time.localtime()
    return jsonify(
        {
            "message": "Time-based filter test",
            "current_hour": current_time.tm_hour,
            "current_day": current_time.tm_wday,
            "blocked_hours": config["time_filter"]["blocked_hours"],
            "blocked_days": config["time_filter"]["blocked_days"],
        }
    )


if __name__ == "__main__":
    logger.info("Starting PyWebGuard custom extensions example server...")
    app.run(host="0.0.0.0", port=8000, debug=True)

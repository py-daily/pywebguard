"""
Minimal example of using PyWebGuard with Flask.

This example demonstrates the simplest possible integration of PyWebGuard
with Flask, using default settings.

To run this example:
    pip install flask pywebguard
    python minimal_example.py
"""

from flask import Flask, request, jsonify
from pywebguard import FlaskGuard, GuardConfig
from pywebguard.storage.memory import MemoryStorage

# Create Flask app
app = Flask(__name__)

# Initialize PyWebGuard with default settings
guard = FlaskGuard(
    app,
    config=GuardConfig(),  # Use default configuration
    storage=MemoryStorage(),  # Use in-memory storage
)


@app.route("/")
def root():
    """Root endpoint with default rate limit"""
    return jsonify(
        {"message": "Hello from PyWebGuard!", "client_ip": request.remote_addr}
    )


@app.route("/status")
def status():
    """Check rate limit status"""
    client_ip = request.remote_addr
    rate_info = guard.guard.rate_limiter.check_limit(client_ip, "/")

    return jsonify(
        {
            "allowed": rate_info["allowed"],
            "remaining": rate_info["remaining"],
            "reset": rate_info["reset"],
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

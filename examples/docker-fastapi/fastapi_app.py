from fastapi import FastAPI, Request
from pywebguard import FastAPIGuard, GuardConfig
from pywebguard.storage.memory import AsyncMemoryStorage

app = FastAPI(
    title="PyWebGuard Demo",
    description="A sample FastAPI application demonstrating PyWebGuard features",
    version="1.0.0",
)

# Configure PyWebGuard
config = GuardConfig(
    ip_filter={
        "enabled": True,
        "whitelist": ["127.0.0.1", "::1"],
    },
    rate_limit={
        "enabled": True,
        "requests_per_minute": 60,
        "burst_size": 10,
    },
    user_agent={
        "enabled": True,
        "blocked_agents": ["curl", "wget", "Scrapy"],
    },
    cors={
        "enabled": True,
        "allow_origins": ["*"],
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    },
)

route_rate_limits = [
    {
        "endpoint": "/api/protected",
        "requests_per_minute": 5,
        "burst_size": 2,
        "auto_ban_threshold": 10,
        "auto_ban_duration": 1800,  # 30 minutes
    },
]

# Initialize storage and middleware
storage = AsyncMemoryStorage()
app.add_middleware(
    FastAPIGuard,
    config=config,
    storage=storage,
)


@app.get("/")
async def root():
    """Root endpoint with default rate limit"""
    return {"message": "Welcome to PyWebGuard Demo!"}


@app.get("/api/protected")
async def protected():
    """Protected endpoint with stricter rate limit"""
    return {"message": "This is a protected endpoint"}


@app.get("/api/status")
async def status():
    """Status endpoint to check if service is running"""
    return {"status": "healthy"}

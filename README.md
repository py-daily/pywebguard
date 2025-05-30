<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/ktechhub/doctoc)*

<!---toc start-->

* [PyWebGuard](#pywebguard)
  * [Key Features](#key-features)
  * [Usage](#usage)
    * [Installation](#installation)
      * [Basic Installation](#basic-installation)
      * [Storage Backends](#storage-backends)
      * [Framework Support](#framework-support)
      * [Search Engine Support](#search-engine-support)
      * [Development Dependencies](#development-dependencies)
      * [Full Installation](#full-installation)
  * [Quick Start](#quick-start)
  * [Documentation](#documentation)
  * [Contributors](#contributors)
  * [Contribution](#contribution)
  * [License](#license)

<!---toc end-->

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
# PyWebGuard
<p align="center">
    <a href="https://badge.fury.io/py/pywebguard"><img src="https://badge.fury.io/py/pywebguard.svg" alt="PyPI version"></a>
    <a href="https://pypi.org/project/pywebguard/"><img src="https://img.shields.io/pypi/pyversions/pywebguard.svg" alt="Python Versions"></a>
    <a href="https://github.com/py-daily/pywebguard/blob/main/LICENSE"><img src="https://img.shields.io/github/license/py-daily/pywebguard.svg" alt="License"></a>
    <a href="#contributors-"><img src="https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square" alt="All Contributors"></a>
    <a href="https://pepy.tech/project/pywebguard"><img src="https://pepy.tech/badge/pywebguard" alt="Downloads"></a>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&amp;logo=Python&amp;logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat&amp;logo=FastAPI&amp;logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/Flask-000000.svg?style=flat&amp;logo=Flask&amp;logoColor=white" alt="Flask">
    <img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&amp;logo=Docker&amp;logoColor=white" alt="Docker">
    <img src="https://img.shields.io/badge/Memory-4CAF50.svg?style=flat&amp;logo=Memory&amp;logoColor=white" alt="Memory">
    <img src="https://img.shields.io/badge/Redis-FF4438.svg?style=flat&amp;logo=Redis&amp;logoColor=white" alt="Redis">
    <img src="https://img.shields.io/badge/SQLite-003B57.svg?style=flat&amp;logo=SQLite&amp;logoColor=white" alt="SQLite">
    <img src="https://img.shields.io/badge/TinyDB-000000.svg?style=flat&amp;logo=TinyDB&amp;logoColor=white" alt="TinyDB">
    <img src="https://img.shields.io/badge/PostgreSQL-336791.svg?style=flat&amp;logo=PostgreSQL&amp;logoColor=white" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/MongoDB-47A248.svg?style=flat&amp;logo=MongoDB&amp;logoColor=white" alt="MongoDB">
    <img src="https://img.shields.io/badge/Meilisearch-000000.svg?style=flat&amp;logo=Meilisearch&amp;logoColor=white" alt="Meilisearch">
    <img src="https://img.shields.io/badge/Elasticsearch-005571.svg?style=flat&amp;logo=Elasticsearch&amp;logoColor=white" alt="Elasticsearch">
    <img src="https://img.shields.io/badge/Pytest-0A9EDC.svg?style=flat&amp;logo=Pytest&amp;logoColor=white" alt="Pytest">
    <img src="https://img.shields.io/badge/Pytest--Cov-0A9EDC.svg?style=flat&amp;logo=Pytest&amp;logoColor=white" alt="Pytest-Cov">
    <img src="https://img.shields.io/badge/Black-000000.svg?style=flat&amp;logo=Python&amp;logoColor=white" alt="Black">
    <img src="https://img.shields.io/badge/CORS-000000.svg?style=flat&amp;logo=CORS&amp;logoColor=white" alt="CORS">
    <img src="https://img.shields.io/badge/GitHub_Actions-2088FF.svg?style=flat&amp;logo=GitHub-Actions&amp;logoColor=white" alt="GitHub Actions">
    <img src="https://img.shields.io/badge/Telegram-26A5E4.svg?style=flat&amp;logo=Telegram&amp;logoColor=white" alt="Telegram">
</p>

A comprehensive security library for Python web applications, providing middleware for IP filtering, rate limiting, and other security features with both synchronous and asynchronous support.

For detailed installation instructions and configuration options, see [Installation Guide](https://github.com/py-daily/pywebguard/blob/main/docs/installation.md).

## Key Features

- **IP Whitelisting and Blacklisting**: Control access based on IP addresses
- **User Agent Filtering**: Block requests from specific user agents
- **Rate Limiting**: Limit the number of requests from a single IP
  - **Per-Route Rate Limiting**: Set different rate limits for different endpoints
  - **Bulk Configuration**: Configure rate limits for multiple routes at once
  - **Pattern Matching**: Use wildcards to apply rate limits to groups of routes
- **Automatic IP Banning**: Automatically ban IPs after a certain number of suspicious requests
- **Penetration Attempt Detection**: Detect and log potential penetration attempts
- **Custom Logging**: Log security events to a custom file
- **CORS Configuration**: Configure CORS settings for your web application
- **IP Geolocation**: Determine the country of an IP address
- **Flexible Storage**: Redis-enabled distributed storage, nosql, sql or in-memory storage
- **Async/Sync Support**: Works with both synchronous (Flask) and asynchronous (FastAPI) frameworks
- **Logging Backends**: Configurable logging backends with current support for Meilisearch


## Usage

### Installation

PyWebGuard can be installed with various optional dependencies depending on your needs:

#### Basic Installation
```bash
pip install pywebguard
```

#### Storage Backends
```bash
pip install pywebguard[redis]

pip install pywebguard[sqlite]

pip install pywebguard[tinydb]

pip install pywebguard[mongodb]

pip install pywebguard[postgresql]
```

#### Framework Support
```bash
pip install pywebguard[flask]

pip install pywebguard[fastapi]
```

#### Search Engine Support
```bash
pip install pywebguard[meilisearch]

pip install pywebguard[elasticsearch]
```

#### Development Dependencies
```bash
pip install pywebguard[test]

pip install pywebguard[format]
```

#### Full Installation
To install all optional dependencies:
```bash
pip install pywebguard[all]
```

## Quick Start

Here's a basic example using FastAPI:

```python
from fastapi import FastAPI
from pywebguard import FastAPIGuard, GuardConfig
from pywebguard.storage.memory import AsyncMemoryStorage

app = FastAPI(
    title="PyWebGuard FastAPI Example",
    description="A comprehensive example of PyWebGuard integration with FastAPI",
    version="1.0.0",
)
config = GuardConfig(
    ip_filter={
        "enabled": True,
        "whitelist": ["127.0.0.1", "::1", "192.168.1.0/24"],
        "blacklist": ["10.0.0.1", "172.16.0.0/16"],
    },
    rate_limit={
        "enabled": True,
        "requests_per_minute": 100,
        "burst_size": 20,
        "auto_ban_threshold": 200,
        "auto_ban_duration": 3600,  # 1 hour in seconds
    },
    user_agent={
        "enabled": True,
        "blocked_agents": ["curl", "wget", "Scrapy", "bot", "Bot"],
        "excluded_paths": ["/ready", "/healthz"]
    },
    cors={
        "enabled": True,
        "allow_origins": ["http://localhost:3000", "https://example.com"],
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "allow_credentials": True,
        "max_age": 3600,
    },
    penetration={
        "enabled": True,
        "detect_sql_injection": True,
        "detect_xss": True,
        "detect_path_traversal": True,
        "block_suspicious_requests": True,
    },
    logging={
        "enabled": True,
        "level": "DEBUG",  # Change to DEBUG to see all messages
        "log_blocked_requests": True,
        "stream": True,
        "stream_levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "meilisearch": {
            "url": "https://meilisearch.dev.ktechhub.com",
            "api_key": os.getenv("MEILISEARCH_API_KEY"),
            "index_name": "pywebguard",
        },
    },
)

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

storage = AsyncMemoryStorage()

app.add_middleware(
    FastAPIGuard,
    config=config,
    storage=storage,
    route_rate_limits=route_rate_limits,
)

@app.get("/", tags=["main"])
async def root():
    """Root endpoint with default rate limit (100 req/min)"""
    return {"message": "Hello World - Default rate limit (100 req/min)"}


@app.get("/api/limited", tags=["main"])
async def limited_endpoint():
    """Strictly rate limited endpoint (5 req/min)"""
    return {"message": "This endpoint is strictly rate limited (5 req/min)"}
```

For more detailed examples, check the [examples](https://github.com/py-daily/pywebguard/tree/main/examples) folder.


## Documentation
- [Installation Guide](https://github.com/py-daily/pywebguard/blob/main/docs/installation.md)
- [CLI Usage](https://github.com/py-daily/pywebguard/blob/main/docs/cli.md)
- [Core Features](https://github.com/py-daily/pywebguard/blob/main/docs/core/)
- [Framework Integration](https://github.com/py-daily/pywebguard/blob/main/docs/frameworks/)
- [Storage Backends](https://github.com/py-daily/pywebguard/blob/main/docs/storage/)

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://www.ktechhub.com"><img src="https://avatars.githubusercontent.com/u/43080869?v=4?s=100" width="100px;" alt="Mumuni Mohammed"/><br /><sub><b>Mumuni Mohammed</b></sub></a><br /><a href="#projectManagement-Kalkulus1" title="Project Management">📆</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/hussein6065"><img src="https://avatars.githubusercontent.com/u/43960479?v=4?s=100" width="100px;" alt="Hussein Baba Fuseini"/><br /><sub><b>Hussein Baba Fuseini</b></sub></a><br /><a href="https://github.com/py-daily/pywebguard/commits?author=hussein6065" title="Documentation">📖</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## Contribution

We welcome contributions from the community! Whether it's bug reports, feature requests, or code contributions, every contribution helps make PyWebGuard better.

Please read our [Contribution Guidelines](https://github.com/py-daily/pywebguard/blob/main/contribution.md) before submitting any changes. This document provides detailed information about:

- How to set up your development environment
- Our coding standards and style guide
- The process for submitting pull requests
- How to report bugs and request features
- Our commit message conventions
- Testing requirements

Join our community and help make PyWebGuard even better! 🚀

## License

This project is licensed under the [MIT License](LICENSE).


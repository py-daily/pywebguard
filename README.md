# PyWebGuard

A comprehensive security library for Python web applications, providing middleware for IP filtering, rate limiting, and other security features with both synchronous and asynchronous support.

## Quick Start

```python
from fastapi import FastAPI
from pywebguard.frameworks import FastAPIGuard

app = FastAPI()
guard = FastAPIGuard(
    config={
        "rate_limit": {"requests": 100, "period": 60},  # 100 requests per minute
        "ip_filter": {"whitelist": ["127.0.0.1"]},
        "logging": {"enabled": True}
    }
)
app.add_middleware(guard)
```

For detailed installation instructions and configuration options, see [Installation Guide](docs/installation.md).

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

## Documentation

- [Installation Guide](docs/installation.md)
- [CLI Usage](docs/cli.md)
- [Core Features](docs/core/)
- [Framework Integration](docs/frameworks/)
- [Storage Backends](docs/storage/)

## Contributors

<a href="https://github.com/py-daily/pywebguard/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=py-daily/pywebguard" />
</a>

## License

This project is licensed under the [MIT License](LICENSE).


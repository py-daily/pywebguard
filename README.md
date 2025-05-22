# PyWebGuard

A comprehensive security library for Python web applications, providing middleware for IP filtering, rate limiting, and other security features with both synchronous and asynchronous support.

## Features

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

## License

MIT

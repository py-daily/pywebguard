<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/ktechhub/doctoc)*

<!---toc start-->

* [PyWebGuard](#pywebguard)
  * [Key Features](#key-features)
  * [Quick Start](#quick-start)
  * [Documentation](#documentation)
  * [Contributors](#contributors)
  * [License](#license)

<!---toc end-->

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
# PyWebGuard
[![PyPI version](https://badge.fury.io/py/pywebguard.svg)](https://badge.fury.io/py/pywebguard)
[![Python Versions](https://img.shields.io/pypi/pyversions/pywebguard.svg)](https://pypi.org/project/pywebguard/)
[![License](https://img.shields.io/github/license/py-daily/pywebguard.svg)](https://github.com/py-daily/pywebguard/blob/main/LICENSE)

A comprehensive security library for Python web applications, providing middleware for IP filtering, rate limiting, and other security features with both synchronous and asynchronous support.

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



## Quick Start
Check the `examples` folder.


## Documentation
- [Installation Guide](docs/installation.md)
- [CLI Usage](docs/cli.md)
- [Core Features](docs/core/)
- [Framework Integration](docs/frameworks/)
- [Storage Backends](docs/storage/)

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->


## License

This project is licensed under the [MIT License](LICENSE).


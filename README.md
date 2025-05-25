<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
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


## License

This project is licensed under the [MIT License](LICENSE).


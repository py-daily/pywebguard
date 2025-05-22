# Installation

PyWebGuard is designed to be modular, allowing you to install only the components you need. The core package provides basic functionality, while additional features can be installed using extras.

## Basic Installation

To install the core package:

```bash
pip install pywebguard
```

This installs the basic functionality, including the core Guard classes and in-memory storage.

## Framework-Specific Installation

### FastAPI

To install PyWebGuard with FastAPI support:

```bash
pip install pywebguard[fastapi]
```

This installs the FastAPI middleware and dependencies.

### Flask

To install PyWebGuard with Flask support:

```bash
pip install pywebguard[flask]
```

This installs the Flask extension and dependencies.

## Storage Backend Installation

### Redis

To install PyWebGuard with Redis storage support:

```bash
pip install pywebguard[redis]
```

### SQLite

To install PyWebGuard with SQLite storage support:

```bash
pip install pywebguard[sqlite]
```

### TinyDB

To install PyWebGuard with TinyDB storage support:

```bash
pip install pywebguard[tinydb]
```

## Combined Installation

### All Storage Backends

To install PyWebGuard with all storage backends:

```bash
pip install pywebguard[all-storage]
```

### All Frameworks

To install PyWebGuard with all framework integrations:

```bash
pip install pywebguard[all-frameworks]
```

### Complete Installation

To install PyWebGuard with all components:

```bash
pip install pywebguard[all]
```

## Development Installation

For development purposes, including testing and code quality tools:

```bash
pip install pywebguard[dev]
```

## From Source

To install from source:

```bash
git clone https://github.com/py-daily/pywebguard.git
cd pywebguard
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

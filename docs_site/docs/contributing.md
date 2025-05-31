# Contributing to PyWebGuard

Thank you for your interest in contributing to PyWebGuard! This guide will help you get started with the contribution process.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/pywebguard.git
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run tests:
   ```bash
   pytest
   ```
4. Run linting:
   ```bash
   flake8
   black .
   ```
5. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a Pull Request

## Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Use Flake8 for linting
- Write docstrings for all functions and classes
- Add type hints to function parameters and return values

## Testing

- Write tests for all new features
- Ensure all tests pass
- Maintain or improve test coverage
- Use pytest for testing

Example test:
```python
def test_rate_limit_middleware():
    app = Flask(__name__)
    guard = WebGuard(app)
    guard.add_middleware(RateLimitMiddleware, requests=100, window=3600)
    
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
```

## Documentation

- Update documentation for all changes
- Follow the existing documentation style
- Include code examples
- Add docstrings to all functions and classes

Example docstring:
```python
def rate_limit(request, limit=100, window=3600):
    """Apply rate limiting to a request.
    
    Args:
        request: The request to rate limit
        limit: Maximum number of requests allowed
        window: Time window in seconds
        
    Returns:
        bool: True if request is allowed, False otherwise
        
    Raises:
        RateLimitExceeded: If rate limit is exceeded
    """
    pass
```

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation
3. Add tests for new functionality
4. Ensure all tests pass
5. Update the changelog
6. The PR will be merged once you have the sign-off of at least one maintainer

## Code Review Process

1. All PRs require at least one review
2. Address all review comments
3. Keep the PR up to date with the main branch
4. Squash commits if requested

## Release Process

1. Update version in `setup.py`
2. Update changelog
3. Create a new release on GitHub
4. Build and upload to PyPI

## Communication

- Use GitHub Issues for bug reports and feature requests
- Use GitHub Discussions for general discussion
- Join our community chat for real-time communication

## Development Tools

### Required Tools

- Python 3.8+
- Git
- Virtual environment
- Code editor with Python support

### Recommended Tools

- VS Code with Python extension
- PyCharm
- Black for formatting
- Flake8 for linting
- MyPy for type checking

## Project Structure

```
pywebguard/
├── pywebguard/
│   ├── core/
│   ├── frameworks/
│   ├── filters/
│   ├── utils/
│   └── __init__.py
├── tests/
├── docs/
├── examples/
└── setup.py
```

## Best Practices

1. **Code Quality**
   - Write clean, maintainable code
   - Follow Python best practices
   - Use type hints
   - Write comprehensive tests

2. **Documentation**
   - Keep documentation up to date
   - Write clear docstrings
   - Include examples
   - Update changelog

3. **Testing**
   - Write unit tests
   - Write integration tests
   - Maintain test coverage
   - Test edge cases

4. **Git Workflow**
   - Use meaningful commit messages
   - Keep PRs focused
   - Respond to review comments
   - Keep branches up to date

## Getting Help

- Check the [documentation](https://py-daily.github.io/pywebguard/)
- Open an issue on GitHub
- Join our community chat
- Ask in GitHub Discussions

## Next Steps

- Read the [Installation Guide](getting-started/installation.md)
- Check the [API Reference](reference/core.md)
- Explore [Examples](examples/) 
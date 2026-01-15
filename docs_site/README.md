# PyWebGuard Documentation

This directory contains the documentation for PyWebGuard, built using MkDocs with the Material theme.

## Prerequisites

Before you start, make sure you have the required dependencies installed:

```bash
pip install mkdocs==1.6.1 mkdocs-material==9.6.14
```

## Running the Documentation Server

To start the documentation server locally:

1. Navigate to the docs_site directory:
   ```bash
   cd docs_site
   ```

2. Start the MkDocs server:
   ```bash
   mkdocs serve
   ```

3. Open your browser and visit:
   ```
   http://127.0.0.1:8000
   ```

The documentation will automatically reload when you make changes to the source files.

## Documentation Structure

```
docs_site/
├── docs/
│   ├── getting-started/
│   │   ├── installation.md
│   │   └── configuration.md
│   ├── guides/
│   │   ├── middleware.md
│   │   └── api-security.md
│   ├── reference/
│   │   ├── core.md
│   │   └── cli.md
│   ├── contributing.md
│   ├── changelog.md
│   └── index.md
└── mkdocs.yml
```

## Contributing to Documentation

1. Make your changes to the Markdown files in the `docs/` directory
2. Test your changes locally using `mkdocs serve`
3. Commit your changes and create a pull request

## Building the Documentation

To build the documentation for production:

```bash
mkdocs build
```

This will create a `site` directory with the built documentation.

## Additional Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Markdown Guide](https://www.markdownguide.org/)

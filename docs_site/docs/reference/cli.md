# CLI Reference

PyWebGuard provides a command-line interface for various operations. This document covers all available CLI commands and options.

## Basic Usage

```bash
pywebguard [command] [options]
```

## Available Commands

### 1. Check

Check the security configuration of your application.

```bash
pywebguard check [options]
```

Options:
- `--config`: Path to configuration file
- `--verbose`: Enable verbose output
- `--format`: Output format (json, yaml, text)

Example:
```bash
pywebguard check --config config.yml --format json
```

### 2. Test

Run security tests on your application.

```bash
pywebguard test [options]
```

Options:
- `--url`: Application URL to test
- `--tests`: Specific tests to run
- `--output`: Output file for results

Example:
```bash
pywebguard test --url http://localhost:5000 --tests rate-limit,xss
```

### 3. Generate

Generate security configuration.

```bash
pywebguard generate [options]
```

Options:
- `--type`: Configuration type (flask, fastapi)
- `--output`: Output file path
- `--template`: Template to use

Example:
```bash
pywebguard generate --type flask --output config.yml
```

### 4. Monitor

Monitor application security in real-time.

```bash
pywebguard monitor [options]
```

Options:
- `--url`: Application URL to monitor
- `--interval`: Check interval in seconds
- `--log`: Log file path

Example:
```bash
pywebguard monitor --url http://localhost:5000 --interval 60
```

## Global Options

These options are available for all commands:

- `--help`: Show help message
- `--version`: Show version information
- `--debug`: Enable debug mode
- `--quiet`: Suppress output

## Configuration File

The CLI can use a configuration file for persistent settings:

```yaml
# config.yml
check:
  verbose: true
  format: json

test:
  url: http://localhost:5000
  tests:
    - rate-limit
    - xss
    - sql-injection

monitor:
  interval: 60
  log: security.log
```

## Output Formats

### JSON

```json
{
  "status": "success",
  "results": {
    "rate-limit": "passed",
    "xss": "passed",
    "sql-injection": "failed"
  }
}
```

### YAML

```yaml
status: success
results:
  rate-limit: passed
  xss: passed
  sql-injection: failed
```

### Text

```
Security Check Results:
----------------------
Rate Limit: PASSED
XSS Protection: PASSED
SQL Injection: FAILED
```

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Configuration error
- `3`: Test failure
- `4`: Connection error

## Examples

### Basic Security Check

```bash
pywebguard check --config config.yml
```

### Run Specific Tests

```bash
pywebguard test --url http://localhost:5000 --tests rate-limit,xss
```

### Generate Flask Configuration

```bash
pywebguard generate --type flask --output config.yml
```

### Monitor Application

```bash
pywebguard monitor --url http://localhost:5000 --interval 60 --log security.log
```

## Best Practices

1. **Configuration Files**: Use configuration files for complex settings
2. **Regular Checks**: Run security checks regularly
3. **Monitoring**: Enable monitoring for production applications
4. **Logging**: Keep logs for security analysis
5. **Updates**: Keep PyWebGuard updated

## Next Steps

- Learn about [Middleware Usage](../guides/middleware.md)
- Explore [Security Features](../guides/api-security.md)
- Check the [Core API Reference](core.md) 
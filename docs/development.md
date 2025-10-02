# Development

Development workflow and guidelines for flext-db-oracle.

## Setup

```bash
cd flext/flext-db-oracle
poetry install
```

## Quality Commands

```bash
# Lint check
make lint

# Type check
make type-check

# Run tests
make test

# All checks
make validate
```

## Implementation Status

### Working Components

- Core database operations (query, execute, schema introspection)
- SQLAlchemy 2.0 integration
- FlextResult error handling
- Configuration management

### Known Issues

- CLI has SimpleNamespace placeholders (client.py:60-67)
- No support (0 methods)
- No DataFrame integration
- Only SQLAlchemy abstraction

## Testing

```bash
# Unit tests only
pytest tests/unit/

# With Oracle XE container
make oracle-start
pytest tests/integration/
```

## Architecture

- api.py: 36 methods in FlextDbOracleApi
- services.py: 8 nested helper classes
- models.py: OracleConfig and data models
- 12 Python files, 4,693 total lines

---

Updated: September 17, 2025 | Version: 0.9.9

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FLEXT DB Oracle is an Oracle Database integration library that serves as infrastructure for the FLEXT ecosystem. Built with Python 3.13+, SQLAlchemy 2.x, and the `oracledb` driver, it implements Clean Architecture patterns and integrates with the broader FLEXT ecosystem of 32+ projects.

**Current Status**: Active development with 0 MyPy errors and comprehensive test coverage (90%+ requirement).

## Architecture

### Core Components

- **Domain Layer**: `metadata.py`, `types.py` - Oracle schema introspection and data models
- **Application Layer**: `api.py` - Main `FlextDbOracleApi` with connection management
- **Infrastructure Layer**: `connection.py`, `config.py` - Database connectivity and configuration
- **Presentation Layer**: `cli.py` - Command-line interface with Rich formatting

### Key Patterns

- **FLEXT Integration**: All classes prefixed with `FlextDbOracle` for ecosystem consistency
- **FlextResult Pattern**: Railway-oriented programming for error handling (`from flext_core import FlextResult`)
- **Clean Architecture**: Clear separation between domain, application, infrastructure, and presentation layers
- **Plugin System**: Extensible architecture in `plugins.py` for validation, monitoring, and security

## Essential Commands

### Development Workflow

```bash
# Project setup
make setup                    # Complete development setup with pre-commit hooks
make install-dev              # Install dependencies including dev tools

# Quality gates (run before committing)
make validate                 # Full validation: lint + type + security + test
make check                    # Quick check: lint + type-check
make test                     # Run tests with 90% coverage requirement
make lint                     # Ruff linting
make type-check               # MyPy strict type checking (currently 0 errors)
make format                   # Auto-format code
```

### Testing

```bash
# Test categories
make test-unit                # Unit tests (no Oracle dependency)
make test-integration         # Integration tests (requires Oracle)
make test-e2e                 # End-to-end workflow tests

# Pytest markers
pytest -m unit                # Fast unit tests with mocking
pytest -m integration         # Tests requiring Oracle connection
pytest -m "not slow"          # Skip slow tests
pytest --cov=src/flext_db_oracle --cov-fail-under=90  # Coverage enforcement
```

### Oracle Development Environment

```bash
# Start Oracle XE 21c for testing
docker-compose -f docker-compose.oracle.yml up -d

# Test Oracle connectivity
make oracle-connect           # Test connection
make oracle-validate          # Validate configuration
export ORACLE_INTEGRATION_TESTS=1  # Enable integration tests

# Environment variables (Singer/Meltano conventions)
export FLEXT_TARGET_ORACLE_HOST="localhost"
export FLEXT_TARGET_ORACLE_PORT="1521"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="XEPDB1"
export FLEXT_TARGET_ORACLE_USERNAME="your_user"
export FLEXT_TARGET_ORACLE_PASSWORD="your_password"
```

## Code Organization

### Source Structure (`src/flext_db_oracle/`)

- `__init__.py` - Public API exports and version info
- `api.py` - Main API class with connection management
- `config.py` - Configuration with Pydantic validation and environment variable support
- `connection.py` - Connection management with pooling and retry logic
- `metadata.py` - Oracle schema introspection (tables, columns, indexes)
- `types.py` - Type definitions and Pydantic models
- `cli.py` - Command-line interface with Click and Rich
- `plugins.py` - Plugin system for extensibility
- `observability.py` - Monitoring and error tracking
- `exceptions.py` - Custom exceptions hierarchy

### Testing Structure (`tests/`)

- `tests/unit/` - Fast unit tests with comprehensive mocking (no Oracle dependency)
- `tests/integration/` - Tests requiring actual Oracle connection
- `tests/e2e/` - End-to-end workflow tests
- `conftest.py` - Shared pytest fixtures with Oracle test configuration

### CLI Commands

Available via `flext-db-oracle` command:

- `connect` - Test database connectivity with parameters
- `connect-env` - Connect using environment variables
- `query --sql "SELECT ..."` - Execute SQL queries with rich formatting
- `schemas` - List database schemas
- `tables --schema SCHEMA_NAME` - List tables
- `health` - Database health check
- `plugins` - Manage Oracle plugins

## Development Patterns

### Error Handling

Always use FlextResult pattern for public APIs:

```python
from flext_core import FlextResult

def some_operation() -> FlextResult[str]:
    try:
        # Operation logic
        return FlextResult[None].ok(result)
    except Exception as e:
        return FlextResult[None].fail(f"Operation failed: {e}")
```

### Configuration

Use Pydantic models with environment variable support:

```python
from flext_db_oracle import FlextDbOracleConfig

# From environment variables
config = FlextDbOracleConfig.from_env()

# Explicit configuration
config = FlextDbOracleConfig(
    host="localhost",
    port=1521,
    service_name="XEPDB1",
    username="user",
    password="password"
)
```

### Testing

- **Unit tests**: Use comprehensive mocking, no external dependencies
- **Integration tests**: Mark with `@pytest.mark.integration`, require Oracle
- **Use fixtures**: Leverage `conftest.py` fixtures for consistent test data
- **Coverage requirement**: Minimum 90% enforced

## Quality Standards

- **Type Safety**: Strict MyPy configuration with 0 errors (currently achieved)
- **Linting**: Ruff with comprehensive rules enabled
- **Security**: Bandit security scanning for all code
- **Coverage**: 90% minimum test coverage enforced
- **Python Version**: 3.13+ only with modern type hints

## Integration Points

### FLEXT Ecosystem Dependencies

- **flext-core**: Foundation patterns (FlextResult, logging, DI container)
- **flext-observability**: Monitoring and health checks
- **flext-cli**: Command-line interface components

All dependencies use local file paths during development:

```toml
flext-core = { path = "../flext-core", develop = true }
```

### Singer Ecosystem Foundation

This library serves as the foundation for Singer ecosystem components:

- **flext-tap-oracle**: Data extraction using this library's connection patterns
- **flext-target-oracle**: Data loading using this library's pooling optimizations
- **flext-dbt-oracle**: Data transformation using this library's metadata capabilities

## Common Development Tasks

### Adding New Features

1. **Domain modeling**: Create types in `types.py` using Pydantic
2. **Business logic**: Implement in appropriate layer returning `FlextResult[T]`
3. **Unit tests**: Add comprehensive tests with mocking
4. **Integration tests**: Add if Oracle interaction required
5. **CLI commands**: Update `cli.py` if user-facing
6. **Validation**: Run `make validate` before committing

### Oracle Connection Development

- **Local testing**: Use `docker-compose.oracle.yml` for Oracle XE 21c
- **Environment variables**: Follow Singer/Meltano conventions
- **Connection pooling**: Always use for multi-operation scenarios
- **Error handling**: Return `FlextResult[None].fail()` with detailed context

### Debugging Oracle Issues

```bash
# Enable SQL logging
export ORACLE_SQL_LOGGING=1

# Connection debugging
make oracle-connect          # Test connectivity
make doctor                  # Comprehensive health check

# Oracle system views for performance (via api.query())
# SELECT * FROM v$session, v$sql, v$sqlarea
```

## Troubleshooting

### Common Issues

**Import Errors**: Ensure FLEXT core dependencies installed: `make install-dev`

**Oracle Connection**: Verify Docker Oracle running: `docker-compose -f docker-compose.oracle.yml ps`

**Type Errors**: Run detailed analysis: `mypy src/ --show-error-codes`

**Test Failures**: Check if integration tests need Oracle: `pytest tests/integration/ --collect-only`

### Docker Oracle Environment

The Oracle XE 21c container takes 2-3 minutes to start. Monitor with:

```bash
docker-compose -f docker-compose.oracle.yml logs -f oracle-xe
```

Use the health check to verify readiness before running integration tests.
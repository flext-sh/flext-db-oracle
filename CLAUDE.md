# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FLEXT DB Oracle is an enterprise Oracle database integration library built on the FLEXT framework. It provides advanced Oracle connectivity, schema management, SQL tools, data operations, and maintenance utilities using modern Python 3.13 patterns and Clean Architecture with Domain-Driven Design (DDD).

## Architecture

This project follows FLEXT standards with Clean Architecture and DDD:

### Core Structure
```
src/flext_db_oracle/
├── __init__.py          # Main exports and API
├── config.py            # Configuration using flext-core BaseConfig
├── simple_api.py        # Simple setup and utility functions
├── application/         # Application services layer
│   └── services.py      # Core Oracle application services
├── domain/              # Domain layer (business logic)
│   └── models.py        # Oracle-specific domain models
├── connection/          # Infrastructure layer - database connectivity
│   ├── config.py        # Connection configuration
│   ├── connection.py    # Oracle connection management
│   ├── pool.py          # Connection pooling
│   └── resilient_connection.py  # Resilient connection handling
├── schema/              # Schema management and analysis
├── compare/             # Data and schema comparison tools
├── maintenance/         # Database health and monitoring
├── sql/                 # SQL parsing and optimization
├── cli/                 # Command-line interface
└── utils/               # Shared utilities and exceptions
```

### Dependencies
- **flext-core**: Foundation framework providing BaseConfig, DDD patterns, ServiceResult
- **flext-observability**: Logging and monitoring (optional)
- **oracledb**: Modern Oracle Python driver (primary)
- **sqlalchemy**: SQL toolkit and ORM
- **alembic**: Database migration tool

## Development Commands

### Environment Setup
```bash
# Development environment setup (uses Poetry)
poetry install           # Install production dependencies
poetry install --with dev  # Install with development dependencies
poetry shell            # Activate virtual environment
```

### Build and Test
```bash
# Testing
make test               # Run pytest tests
make test-cov           # Run tests with coverage report
pytest tests/unit       # Unit tests only
pytest tests/integration # Integration tests (requires Oracle DB)
pytest -m oracle        # Oracle-specific tests
pytest -m "not slow"    # Fast tests only

# Code Quality
make lint               # Run ruff linting (strict)
make lint-fix           # Auto-fix linting issues
make format             # Format code with ruff
poetry run mypy src     # Type checking
```

### CLI Tools
```bash
# Connection testing
make cli-test HOST=localhost PORT=1521 SERVICE=XE USER=hr PASS=hr
./flext-db-oracle --url oracle://hr:hr@localhost:1521/XE test

# Schema operations
make cli-tables URL=oracle://hr:hr@localhost:1521/XE
./flext-db-oracle --host localhost --username hr --password hr tables

# Health checks
make cli-health HOST=localhost USER=system PASS=oracle
./flext-db-oracle --url oracle://system:oracle@localhost:1521/XE health

# SQL queries
make cli-query SQL="SELECT * FROM user_tables" LIMIT=5
./flext-db-oracle --url oracle://hr:hr@localhost:1521/XE query "SELECT * FROM dual"
```

### Package Management
```bash
make build              # Build distributable package
make clean              # Clean build artifacts
make version            # Show current version
make bump-patch         # Increment patch version
make bump-minor         # Increment minor version
```

## Code Patterns

### Configuration
Always use the `OracleConfig` class which extends `flext-core.BaseConfig`:
```python
from flext_db_oracle.config import OracleConfig

config = OracleConfig(
    host="oracle-server.com",
    port=1521,
    service_name="ORCL",
    username="app_user",
    password="secure_password"
)
```

### Application Services
Use the application services from `flext_db_oracle.application.services`:
```python
from flext_db_oracle.application.services import OracleConnectionService

service = OracleConnectionService(config)
result = service.test_connection()  # Returns ServiceResult
```

### Domain Models
All domain models extend flext-core DDD base classes:
```python
from flext_db_oracle.domain.models import OracleConnectionInfo

conn_info = OracleConnectionInfo(
    host="localhost",
    port=1521,
    service_name="XE",
    username="user",
    password="pass"
)
```

### Error Handling
Use `ServiceResult` pattern from flext-core for consistent error handling:
```python
from flext_core.domain.types import ServiceResult

result = some_operation()
if result.is_success:
    value = result.value
else:
    error = result.error
```

## Testing

### Test Structure
```
tests/
├── unit/               # Unit tests (no external dependencies)
├── integration/        # Integration tests (require Oracle DB)
└── e2e/               # End-to-end tests
```

### Test Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.oracle` - Oracle database tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.requires_oracle` - Tests needing Oracle access

### Running Specific Tests
```bash
pytest -m unit                    # Unit tests only
pytest -m "oracle and not slow"  # Oracle tests, exclude slow ones
pytest tests/unit/test_config.py::test_oracle_config  # Specific test
```

## Configuration

### Environment Variables
Uses `FLEXT_TARGET_ORACLE_` prefix for environment variables:
```bash
FLEXT_TARGET_ORACLE_HOST=oracle-server.com
FLEXT_TARGET_ORACLE_PORT=1521
FLEXT_TARGET_ORACLE_SERVICE_NAME=ORCL
FLEXT_TARGET_ORACLE_USERNAME=app_user
FLEXT_TARGET_ORACLE_PASSWORD=secure_password
FLEXT_TARGET_ORACLE_POOL_MIN_SIZE=5
FLEXT_TARGET_ORACLE_POOL_MAX_SIZE=20
```

### Connection Configuration
- Always provide either `service_name` or `sid`
- Use connection pooling for production workloads
- Configure appropriate timeouts for your environment
- Enable retry logic for resilient connections

## Important Notes

### Dependencies
- This project depends on `flext-core` as its foundation
- Optional dependency on `flext-observability` for enhanced logging
- Uses modern `oracledb` driver, not legacy `cx_Oracle`
- Requires Python 3.13+

### Code Quality
- Strict linting with ruff (ALL rules enabled)
- 90% test coverage requirement
- Full type annotations required
- No code duplication allowed (follows flext standards)

### FLEXT Framework Integration
- Follows FLEXT workspace patterns
- Uses shared `.venv` from workspace root
- Integrates with other FLEXT modules (auth, observability, etc.)
- Part of larger FLEXT enterprise framework ecosystem

When working with this codebase, always follow the established patterns, use the provided application services, and ensure your changes integrate properly with the broader FLEXT framework.
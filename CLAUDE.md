# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**flext-db-oracle** is the enterprise Oracle Database integration foundation for the FLEXT ecosystem, providing Oracle connectivity, SQL operations, schema management, and database infrastructure using SQLAlchemy 2 + oracledb with FLEXT patterns.

**Version**: 0.9.0 | **Updated**: 2025-10-10
**Status**: Functional foundation with production-ready Oracle integration · Zero errors across quality gates

**Key Architecture:**
- Single consolidated API class: `FlextDbOracleApi`
- Wraps SQLAlchemy 2.0 and oracledb driver internally
- Uses flext-core patterns: `FlextResult[T]` railway pattern, `FlextService` base class
- Python 3.13+ exclusive with strict type safety
- Poetry-based dependency management

**CRITICAL CONSTRAINT - ZERO TOLERANCE:**
- **api.py** is the ONLY file that may import SQLAlchemy directly
- **All other code must use the FlextDbOracleApi abstraction**
- Breaking this constraint violates the foundation library's core purpose

---

## Essential Commands

### Development Workflow

```bash
# Setup and installation
make setup                   # Install deps + pre-commit hooks
make install                 # Install dependencies with Poetry
make install-dev             # Install with dev dependencies

# Quality gates (MANDATORY before commit)
make validate                # Full validation: lint + type-check + security + test
make check                   # Quick check: lint + type-check only

# Individual checks
make lint                    # Ruff linting (ZERO violations)
make type-check              # Pyrefly type checking (ZERO errors)
make security                # Bandit + pip-audit security scanning
make test                    # Full test suite with 100% coverage requirement
make format                  # Auto-format code with Ruff

# Testing
PYTHONPATH=src poetry run pytest tests/unit/test_api.py -v
PYTHONPATH=src poetry run pytest -m unit              # Unit tests only
PYTHONPATH=src poetry run pytest -m integration       # Integration tests
PYTHONPATH=src poetry run pytest --lf --ff -x         # Last failed, fail fast

# Oracle operations
make oracle-test             # Test Oracle imports and basic functionality
make oracle-connect          # Test Oracle connection
make oracle-operations       # Run all Oracle validations

# Build and maintenance
make build                   # Build package
make clean                   # Clean build artifacts
make reset                   # Complete reset (clean + setup)
```

### Running Single Tests

```bash
# Run specific test file
PYTHONPATH=src poetry run pytest tests/unit/test_api.py -v

# Run specific test class
PYTHONPATH=src poetry run pytest tests/unit/test_models.py::TestFlextDbOracleModels -v

# Run specific test function
PYTHONPATH=src poetry run pytest tests/unit/test_api.py::test_flext_db_oracle_api_init -v

# Run with markers
PYTHONPATH=src poetry run pytest -m unit              # Unit tests only
PYTHONPATH=src poetry run pytest -m integration       # Integration tests
PYTHONPATH=src poetry run pytest -m "not slow"        # Skip slow tests
```

---

## Architecture Overview

### Module Structure and Responsibilities

```
src/flext_db_oracle/
├── __init__.py          # Public API exports (14 classes)
├── __version__.py       # Version information
├── py.typed             # PEP 561 type marker

├── api.py               # FlextDbOracleApi - main facade API (ORACLE ONLY import)
├── cli.py               # FlextDbOracleCli - CLI interface
├── client.py            # FlextDbOracleClient - CLI client operations
├── config.py            # FlextDbOracleConfig - configuration management
├── constants.py         # FlextDbOracleConstants - all system constants
├── dispatcher.py        # FlextDbOracleDispatcher - command dispatching
├── exceptions.py        # FlextDbOracleExceptions - error hierarchy
├── metadata.py          # FlextDbOracleMetadata - schema introspection (DEPRECATED)
├── mixins.py            # FlextDbOracleMixins - reusable behaviors
├── models.py            # FlextDbOracleModels - Pydantic models
├── plugins.py           # FlextDbOraclePlugins - plugin system
├── protocols.py         # FlextDbOracleProtocols - structural typing
├── services.py          # FlextDbOracleServices - SQL query building
├── typings.py           # FlextDbOracleTypes - type aliases
└── utilities.py         # FlextDbOracleUtilities - helper functions

Total: 16 files, ~4,517 lines of production code
```

**Key Module Dependencies:**
- `api.py` → Main entry point, ONLY file that imports SQLAlchemy/oracledb
- `models.py` → Contains ALL Pydantic models (largest module)
- `constants.py` → No external dependencies, used everywhere
- All modules → Extend flext-core patterns and use FlextResult[T]

### Core Classes (Actual Exports)

```python
from flext_db_oracle import (
    FlextDbOracleApi,         # Main Oracle API (SQLAlchemy abstraction)
    FlextDbOracleCli,         # CLI interface
    FlextDbOracleClient,      # CLI client operations
    FlextDbOracleConfig,      # Configuration management
    FlextDbOracleConstants,   # System constants
    FlextDbOracleDispatcher,  # Command dispatching
    FlextDbOracleExceptions,  # Error hierarchy
    FlextDbOracleMetadata,    # Schema introspection (DEPRECATED)
    FlextDbOracleMixins,      # Reusable mixins
    FlextDbOracleModels,      # Pydantic models
    FlextDbOraclePlugins,     # Plugin system
    FlextDbOracleProtocols,   # Protocols
    FlextDbOracleServices,    # SQL services
    FlextDbOracleTypes,       # Type definitions
    FlextDbOracleUtilities,   # Helper utilities
)
```

### Design Patterns

**Railway-Oriented Programming:**
All operations return `FlextResult[T]` for composable error handling:

```python
from flext_db_oracle import FlextDbOracleApi
from flext_core import FlextResult

api = FlextDbOracleApi()

# All operations return FlextResult
result = api.connect({"host": "localhost", "port": 1521})
if result.is_success:
    connection = result.unwrap()
else:
    print(f"Connection failed: {result.error}")
```

**Domain Library Pattern:**
Each module follows the unified class pattern from flext-core:

```python
class FlextDbOracleServices:
    """Single class per module - domain library pattern."""
    # All SQL service functionality consolidated here
```

**SQLAlchemy Abstraction Pattern:**
Never import SQLAlchemy/oracledb directly except in api.py:

```python
# ❌ FORBIDDEN in most files
import sqlalchemy
from sqlalchemy import create_engine

# ✅ CORRECT - Use abstraction layers
from flext_db_oracle import FlextDbOracleApi

api = FlextDbOracleApi()
result = api.execute_query("SELECT * FROM users")
```

---

## Critical Rules

### REQUIRED
- ✅ Use FlextResult[T] for all operations that can fail
- ✅ Import from root module: `from flext_db_oracle import X`
- ✅ api.py is ONLY file that imports SQLAlchemy/oracledb
- ✅ 100% type annotations required
- ✅ All operations return FlextResult[T] for error handling

### FORBIDDEN
- ❌ Direct SQLAlchemy/oracledb imports outside api.py
- ❌ Exception-based error handling in business logic (use FlextResult)
- ❌ Multiple top-level classes per module
- ❌ Lazy imports (imports inside functions)
- ❌ Type ignores without specific codes
- ❌ Any type usage

---

## Testing Strategy

### Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_api.py         # FlextDbOracleApi tests
│   ├── test_models.py      # FlextDbOracleModels tests
│   ├── test_services.py    # FlextDbOracleServices tests
│   └── ...
├── integration/            # Integration tests
└── e2e/                    # End-to-end tests
```

### Test Fixtures

Common fixtures available in all tests (from `conftest.py`):

```python
# Service fixtures (all major classes have fixtures)
flext_db_oracle_api         # FlextDbOracleApi instance
flext_db_oracle_config      # FlextDbOracleConfig instance
flext_db_oracle_models      # FlextDbOracleModels instance
oracle_config_data          # Sample Oracle configuration
mock_oracle_connection      # Mocked Oracle connection
```

### Writing Tests

Follow these patterns for Oracle tests:

```python
import pytest
from flext_db_oracle import FlextDbOracleApi

def test_oracle_operation(flext_db_oracle_api: FlextDbOracleApi):
    """Test Oracle operation with fixture."""
    result = flext_db_oracle_api.validate_config({"host": "localhost"})
    assert result.is_success
    assert result.unwrap() == True

def test_with_mock_connection(mock_oracle_connection, flext_db_oracle_api: FlextDbOracleApi):
    """Test with mocked Oracle connection."""
    result = flext_db_oracle_api.execute_query("SELECT 1", connection=mock_oracle_connection)
    assert result.is_success
```

---

## Code Quality Standards

### Type Safety

- **Pyrefly strict mode** required for all `src/` code
- **100% type annotations** - no `Any` types allowed
- Use `FlextDbOracleTypes` for common type aliases
- All return types must be explicit

```python
from flext_core import FlextResult
from flext_db_oracle import FlextDbOracleTypes

def execute_query(sql: str, params: FlextDbOracleTypes.ParamsDict = None) -> FlextResult[FlextDbOracleTypes.QueryResult]:
    """Complete type annotations required."""
    return FlextResult[FlextDbOracleTypes.QueryResult].ok({"rows": [], "columns": []})
```

### Linting and Formatting

- **Ruff** for linting and formatting (replaces Black, isort, flake8)
- **Line length**: 88 characters (Ruff default)
- **Import organization**: Ruff handles automatically
- Run `make format` before committing

### Error Handling

Always use `FlextResult[T]` pattern - **no bare exceptions** in business logic:

```python
# ✅ CORRECT - Railway pattern
def validate_sql(sql: str) -> FlextResult[bool]:
    if not sql or not sql.strip():
        return FlextResult[bool].fail("SQL query required")
    return FlextResult[bool].ok(True)

# ❌ WRONG - Don't raise exceptions for business logic
def validate_sql(sql: str) -> bool:
    if not sql or not sql.strip():
        raise ValueError("SQL query required")  # Don't do this
    return True
```

---

## Dependencies

### Core Dependencies

- **flext-core** - Foundation library (FlextResult, FlextService, FlextContainer)
- **flext-cli** - CLI foundation (Click/Rich abstraction)
- **SQLAlchemy 2.0+** - ORM and database toolkit (internal abstraction)
- **oracledb 3.2+** - Oracle Database driver (internal abstraction)
- **pydantic 2.11+** - Data validation and configuration
- **structlog** - Structured logging

### Dev Dependencies

- **Ruff 0.12+** - Linting and formatting
- **Pyrefly 0.34+** - Type checking
- **Pytest 8.4+** - Testing framework
- **Bandit 1.8+** - Security scanning

---

## Common Issues and Solutions

### Import Errors

```bash
# If you get "ModuleNotFoundError: No module named 'flext_db_oracle'"
PYTHONPATH=src poetry run python -c "from flext_db_oracle import FlextDbOracleApi"

# Always set PYTHONPATH when running tests or scripts
PYTHONPATH=src poetry run pytest tests/
```

### Oracle Connection Issues

```bash
# Test Oracle connectivity
make oracle-connect

# Check Oracle configuration
PYTHONPATH=src poetry run python -c "
from flext_db_oracle import FlextDbOracleConfig
config = FlextDbOracleConfig()
print(f'Host: {config.oracle_host}, Port: {config.oracle_port}')
"
```

### Type Check Failures

```bash
# Run type check to see errors
make type-check

# Focus on specific modules
PYTHONPATH=src poetry run pyrefly check src/flext_db_oracle/api.py

# Check specific error codes
PYTHONPATH=src poetry run pyrefly check . --show-error-codes
```

### Test Failures

```bash
# Run with verbose output
PYTHONPATH=src poetry run pytest tests/unit/test_api.py -vv --tb=short

# Run last failed tests
PYTHONPATH=src poetry run pytest --lf

# Run with maximum failures control
PYTHONPATH=src poetry run pytest --maxfail=1 -x
```

### Build Issues

```bash
# Clean everything and rebuild
make clean
make setup
make build

# Check Poetry environment
poetry env info
poetry show --tree
```

---

## Integration with FLEXT Ecosystem

This project is part of the FLEXT monorepo workspace. Key integration points:

- **Depends on**: flext-core (foundation), flext-cli (CLI patterns)
- **Used by**: flext-tap-oracle, flext-target-oracle, flext-dbt-oracle
- **Architecture**: Follows workspace-level patterns defined in `../CLAUDE.md`
- **Quality Gates**: Must pass workspace-level validation before commits

See `../CLAUDE.md` for workspace-level standards and `README.md` for project overview.

### Documentation Resources

Additional documentation is available in the workspace:

- **[../CLAUDE.md](../CLAUDE.md)** - Workspace standards and patterns
- **[README.md](README.md)** - Project overview and usage
- **[docs/](docs/)** - Additional documentation (if available)

---

## Key Principles

1. **Use FlextResult[T]** for all operations that can fail
2. **Single class per module** following domain library pattern
3. **Type safety first** - 100% type annotations required
4. **SQLAlchemy abstraction** - Never import SQLAlchemy/oracledb directly
5. **Railway-oriented programming** - Compose operations with FlextResult
6. **Test real functionality** - Avoid excessive mocking
7. **Run quality gates** before every commit: `make validate`

---

## 🔗 MCP SERVER INTEGRATION (MANDATORY)

| MCP Server              | Purpose                                                  | Status          |
| ----------------------- | -------------------------------------------------------- | --------------- |
| **serena**              | Semantic code analysis, symbol manipulation, refactoring | **MANDATORY**   |
| **sequential-thinking** | Oracle architecture and database problem solving         | **RECOMMENDED** |
| **context7**            | Third-party library documentation (SQLAlchemy, oracledb) | **RECOMMENDED** |
| **github**              | Repository operations and Oracle ecosystem PRs           | **ACTIVE**      |

**Usage**: Reference [~/.claude/commands/flext.md](~/.claude/commands/flext.md) for MCP workflows. Use `/flext` command for Oracle database module optimization.

---

## 🎯 FLEXT-DB-ORACLE MISSION (ORACLE DATABASE FOUNDATION AUTHORITY)

**CRITICAL ROLE**: flext-db-oracle is the enterprise-grade Oracle Database integration foundation for the entire FLEXT ecosystem, providing Oracle connectivity, SQL operations, schema management, and database infrastructure using SQLAlchemy 2 + oracledb with FLEXT patterns.

**CURRENT CAPABILITIES**:

- ✅ **Enterprise Oracle Integration**: Production-grade Oracle XE 21c integration with SQLAlchemy 2 and oracledb
- ✅ **FLEXT Ecosystem Integration**: Mandatory use of flext-core foundation exclusively
- ✅ **SQL Operations Management**: Complete SQL query building, execution, and result processing
- ✅ **Schema Management**: Oracle schema introspection, metadata extraction, and DDL operations
- ✅ **Connection Management**: Enterprise connection pooling, failover, and performance optimization
- ✅ **Production Quality**: Zero errors across all quality gates with comprehensive Oracle testing

**ECOSYSTEM IMPACT**:

- **All 32+ FLEXT Projects**: Oracle database foundation for entire ecosystem - NO custom Oracle implementations
- **Singer/Meltano Foundation**: Core library for flext-tap-oracle, flext-target-oracle, flext-dbt-oracle
- **Enterprise Data Integration**: Production-ready Oracle ETL operations and data pipeline management

---

## 🏗️ ARCHITECTURE OVERVIEW

### Clean Architecture with Domain-Driven Design

**Design Philosophy**: Complete enterprise-grade Oracle database operations using Clean Architecture patterns with mandatory FLEXT ecosystem integration for ALL Oracle operations.

### Module Organization

```
src/flext_db_oracle/
├── __init__.py          # Public API exports (14 classes)
├── __version__.py       # Version information
├── py.typed             # PEP 561 type marker

├── api.py               # FlextDbOracleApi - main facade API (ORACLE ONLY import)
├── cli.py               # FlextDbOracleCli - CLI interface
├── client.py            # FlextDbOracleClient - CLI client operations
├── config.py            # FlextDbOracleConfig - configuration management
├── constants.py         # FlextDbOracleConstants - all system constants
├── dispatcher.py        # FlextDbOracleDispatcher - command dispatching
├── exceptions.py        # FlextDbOracleExceptions - error hierarchy
├── metadata.py          # FlextDbOracleMetadata - schema introspection (DEPRECATED)
├── mixins.py            # FlextDbOracleMixins - reusable behaviors
├── models.py            # FlextDbOracleModels - Pydantic models
├── plugins.py           # FlextDbOraclePlugins - plugin system
├── protocols.py         # FlextDbOracleProtocols - structural typing
├── services.py          # FlextDbOracleServices - SQL query building
├── typings.py           # FlextDbOracleTypes - type aliases
└── utilities.py         # FlextDbOracleUtilities - helper functions

Total: 16 files, ~4,517 lines of production code
```

**Key Architectural Points:**
- `api.py` is the ONLY file that imports SQLAlchemy/oracledb
- All other modules use the FlextDbOracleApi abstraction
- Complete FLEXT ecosystem integration (flext-core, flext-cli)
- Railway-oriented programming with FlextResult[T]

---

## 🔧 DEVELOPMENT WORKFLOW

### Essential Commands

```bash
# Quality gates (MANDATORY before commit)
make validate                # Full validation: lint + type-check + security + test
make check                   # Quick check: lint + type-check only

# Individual checks
make lint                    # Ruff linting (ZERO violations)
make type-check              # Pyrefly type checking (ZERO errors)
make security                # Bandit + pip-audit security scanning
make test                    # Full test suite with coverage requirement

# Oracle operations
make oracle-test             # Test Oracle imports and basic functionality
make oracle-connect          # Test Oracle connection
make oracle-operations       # Run all Oracle validations
```

### Running Specific Tests

```bash
# Run specific test file
PYTHONPATH=src poetry run pytest tests/unit/test_api.py -v

# Run specific test class
PYTHONPATH=src poetry run pytest tests/unit/test_models.py::TestFlextDbOracleModels -v

# Run with markers
PYTHONPATH=src poetry run pytest -m unit              # Unit tests only
PYTHONPATH=src poetry run pytest -m integration       # Integration tests
```

---

## 🚨 CRITICAL PATTERNS

### MANDATORY: FlextResult[T] Railway Pattern

ALL operations that can fail MUST return `FlextResult[T]`:

```python
from flext_db_oracle import FlextDbOracleApi
from flext_core import FlextResult

api = FlextDbOracleApi()

# All operations return FlextResult
result = api.connect({"host": "localhost", "port": 1521})
if result.is_success:
    connection = result.unwrap()
else:
    print(f"Connection failed: {result.error}")
```

### FORBIDDEN: Direct SQLAlchemy Imports

```python
# ❌ FORBIDDEN outside api.py
import sqlalchemy
from sqlalchemy import create_engine

# ✅ CORRECT - Use abstraction
from flext_db_oracle import FlextDbOracleApi
api = FlextDbOracleApi()
result = api.execute_query("SELECT * FROM users")
```

### MANDATORY: Root Module Imports

```python
# ✅ CORRECT - Root imports only
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleModels

# ❌ FORBIDDEN - Internal module imports
from flext_db_oracle.api import FlextDbOracleApi
```

---

## 📊 QUALITY STANDARDS

### Type Safety (ZERO TOLERANCE)

- **Pyrefly strict mode** required for all `src/` code
- **100% type annotations** - no `Any` types allowed
- **api.py ONLY** imports SQLAlchemy/oracledb

### Code Quality (ZERO TOLERANCE)

- **Ruff linting**: Zero violations in production code
- **Line length**: 88 characters (Ruff default)
- **Import organization**: Ruff handles automatically

### Testing Standards

- **Coverage Target**: 100% requirement (MANDATORY)
- **Real Oracle Tests**: Integration tests with actual Oracle XE 21c container
- **FLEXT Integration**: All ecosystem patterns tested

---

## 🐳 DEPENDENCIES & INTEGRATION

### Core Dependencies

- **flext-core** - Foundation library (FlextResult[T], railway pattern)
- **flext-cli** - CLI foundation (Click/Rich abstraction)
- **SQLAlchemy 2.0+** - ORM (internal abstraction in api.py)
- **oracledb 3.2+** - Oracle driver (internal abstraction in api.py)
- **pydantic 2.11+** - Data validation and models

### FLEXT Ecosystem Integration

This project is part of the FLEXT monorepo workspace:

- **Depends on**: flext-core, flext-cli
- **Used by**: flext-tap-oracle, flext-target-oracle, flext-dbt-oracle
- **Quality Gates**: Must pass workspace-level validation
- **Architecture**: Follows workspace patterns defined in `../CLAUDE.md`

---

## 🛠️ TROUBLESHOOTING

### Common Issues

**Import Errors:**
```bash
# Always set PYTHONPATH
PYTHONPATH=src poetry run python -c "from flext_db_oracle import FlextDbOracleApi"
```

**Oracle Connection Issues:**
```bash
# Test connectivity
make oracle-connect
PYTHONPATH=src poetry run python -c "
from flext_db_oracle import FlextDbOracleConfig
config = FlextDbOracleConfig()
print(f'Host: {config.oracle_host}, Port: {config.oracle_port}')
"
```

**Type Check Failures:**
```bash
# Run type checking
make type-check
PYTHONPATH=src poetry run pyrefly check src/flext_db_oracle/api.py
```

---

## 📈 CURRENT STATUS (v0.9.0)

### What Works

- ✅ **Enterprise Oracle Integration**: Production-grade Oracle XE 21c with SQLAlchemy 2
- ✅ **FLEXT Ecosystem Integration**: Complete flext-core and flext-cli integration
- ✅ **Type Safety**: Pyrefly strict mode compliance (ZERO errors)
- ✅ **Code Quality**: Ruff linting compliance (ZERO violations)
- ✅ **Testing**: 100% coverage requirement with real Oracle container tests
- ✅ **Architecture**: Clean Architecture with Domain-Driven Design

### Development Priorities

1. **Production Hardening**: Enterprise connection pooling and monitoring
2. **Performance Optimization**: Query optimization and connection management
3. **Security Enhancement**: Advanced Oracle security features
4. **Documentation**: Enterprise Oracle development procedures

---

## 🎯 KEY PRINCIPLES

1. **FlextResult[T] for all operations** that can fail
2. **api.py ONLY imports SQLAlchemy/oracledb**
3. **Zero tolerance for quality issues** (lint, type, test)
4. **Complete FLEXT ecosystem integration**
5. **Railway-oriented programming** throughout
6. **Real Oracle testing** with containers
7. **Root module imports only**

---

**flext-db-oracle v0.9.0** - Enterprise Oracle Database integration foundation for the FLEXT ecosystem using SQLAlchemy 2 + oracledb with Clean Architecture patterns.

**Purpose**: Provide production-ready Oracle database operations for all FLEXT projects with zero custom implementations allowed.

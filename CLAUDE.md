# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FLEXT DB Oracle is a modern Oracle Database integration library built with Python 3.13, SQLAlchemy 2, and the modern `oracledb` driver. It's part of the larger FLEXT ecosystem and implements Clean Architecture, Domain-Driven Design (DDD), and follows strict enterprise-grade quality standards.

## Key Architecture Patterns

### FLEXT Core Integration

- Uses `FlextResult` pattern for error handling and railway-oriented programming
- All classes prefixed with `FlextDbOracle` to supplement (not replace) flext-core functionality
- Imports from flext-core come from root namespace: `from flext_core import FlextResult`
- Dependency injection container pattern for service management

### Clean Architecture Layers

- **Domain**: Core business logic and entities (`metadata.py`, `types.py`)
- **Application**: Use cases and services (`api.py`)
- **Infrastructure**: External concerns (`connection.py`, `config.py`)
- **Presentation**: CLI and external interfaces (`cli.py`)

### SQLAlchemy 2 Integration

- Modern async/await patterns where applicable
- Connection pooling with `FlextDbOracleConnectionPool`
- Proper session management and transaction handling
- Oracle-specific optimizations and type handling

## Development Commands

### Essential Commands

```bash
# Setup development environment
make install-dev              # Install all dependencies including dev tools
make dev-setup                # Complete development setup with pre-commit hooks

# Quality gates (must pass before committing)
make validate                 # Full validation: lint + type + security + test
make check                    # Quick check: lint + type-check + security
make test                     # Run all tests with 90% coverage requirement
make lint                     # Ruff linting with ALL rules enabled
make type-check               # MyPy strict type checking
make format                   # Auto-format code with ruff

# Testing specific patterns
make test-unit                # Unit tests only
make test-integration         # Integration tests (requires Oracle)
make test-coverage            # Generate HTML coverage report
pytest -m "not slow"          # Fast tests only
pytest -m integration         # Integration tests only
```

### Oracle-Specific Commands

```bash
# Oracle connectivity and validation
make oracle-test              # Basic Oracle connectivity test
make oracle-connect           # Test connection to Oracle server
make oracle-validate          # Validate Oracle configuration
make oracle-schema            # Verify Oracle schema
make oracle-operations        # Run all Oracle validations

# Docker Oracle for testing
docker-compose -f docker-compose.oracle.yml up -d  # Start Oracle XE
docker-compose -f docker-compose.oracle.yml down   # Stop Oracle
```

### Test Infrastructure

```bash
# Run specific test categories
pytest tests/unit/ -v                    # Unit tests
pytest tests/integration/ -v             # Integration tests (needs Oracle)
pytest tests/e2e/ -v                     # End-to-end tests

# Coverage and quality
pytest --cov=src/flext_db_oracle --cov-report=html    # HTML coverage
pytest --cov-fail-under=90                            # Enforce 90% coverage
make coverage-html                                     # Generate and open coverage
```

## Code Organization

### Core Components

- `api.py` - Main `FlextDbOracleApi` class for high-level operations
- `config.py` - `FlextDbOracleConfig` with environment variable support
- `connection.py` - Connection management and pooling
- `metadata.py` - Oracle schema introspection and DDL generation
- `types.py` - Type definitions and Pydantic models
- `observability.py` - Monitoring, logging, and error tracking
- `plugins.py` - Plugin system for extending functionality

### Testing Structure

- `tests/unit/` - Fast unit tests with mocks
- `tests/integration/` - Tests requiring actual Oracle connection
- `tests/e2e/` - End-to-end workflow tests
- `conftest.py` - Shared test fixtures and configuration

### Configuration Patterns

Environment variables follow Meltano conventions:

```bash
export FLEXT_TARGET_ORACLE_HOST="localhost"
export FLEXT_TARGET_ORACLE_PORT="1521"
export FLEXT_TARGET_ORACLE_USERNAME="user"
export FLEXT_TARGET_ORACLE_PASSWORD="password"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="ORCLPDB1"
```

## Quality Standards

### Strict Requirements (Zero Tolerance)

- **Coverage**: Minimum 90% test coverage (`--cov-fail-under=90`)
- **Type Safety**: Strict MyPy configuration (`mypy src/ --strict`)
- **Linting**: Ruff with ALL rules enabled (`select = ["ALL"]`)
- **Python**: 3.13+ only with modern type hints
- **Dependencies**: SQLAlchemy 2.x, oracledb 3.x, Pydantic 2.x

### Code Patterns

- All public classes use `FlextDbOracle` prefix
- Use `FlextResult` for error handling, never raise exceptions directly
- Type hints required on all functions and methods
- Async patterns where beneficial (I/O operations)
- Comprehensive docstrings following Google style

### Testing Requirements

- Unit tests must not require external Oracle database
- Integration tests should be marked with `@pytest.mark.integration`
- Use pytest fixtures from `conftest.py` for consistent test data
- Mock external dependencies in unit tests
- Test both success and failure scenarios

## Integration Points

### FLEXT Ecosystem Dependencies

- `flext-core`: Foundation patterns, FlextResult, DI container
- `flext-observability`: Structured logging and metrics
- `flext-plugin`: Plugin architecture support
- `flext-cli`: Command-line interface components

### Oracle-Specific Features

- Connection pooling with proper resource management
- Oracle-specific SQL optimizations and hints
- Schema introspection with complete metadata extraction
- DDL generation for tables, indexes, and constraints
- Performance monitoring using Oracle v$ views

## Common Development Tasks

### Adding New Functionality

1. Create domain models in `types.py` using Pydantic
2. Implement business logic returning `FlextResult`
3. Add comprehensive unit tests with mocks
4. Add integration tests if Oracle interaction required
5. Update CLI if new commands needed
6. Run full validation: `make validate`

### Oracle Connection Testing

- Use `docker-compose.oracle.yml` for local Oracle XE
- Integration tests require `ORACLE_INTEGRATION_TESTS=1` environment variable
- Connection failures return `FlextResult.failure()` with detailed error info
- Always use connection pooling for performance

### Debugging Oracle Issues

- Enable SQL logging: `logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)`
- Use Oracle system views for performance analysis
- Connection errors typically indicate infrastructure issues, not code problems
- Test with minimal Oracle setup first (Oracle XE via Docker)

## Docker Development

### Oracle Test Environment

```bash
# Start Oracle XE for testing
docker-compose -f docker-compose.oracle.yml up -d

# Wait for Oracle to be ready (check logs)
docker-compose -f docker-compose.oracle.yml logs -f oracle-xe

# Run integration tests
export ORACLE_INTEGRATION_TESTS=1
make test-integration

# Cleanup
docker-compose -f docker-compose.oracle.yml down -v
```

## Troubleshooting

### Common Issues

- **Import Errors**: Ensure flext-core dependencies are properly installed
- **Oracle Connection**: Verify Oracle service is running and accessible
- **Type Errors**: Run `make type-check` for detailed MyPy analysis
- **Test Failures**: Check if Oracle integration tests need real database

### Performance Optimization

- Use connection pooling for multiple operations
- Leverage Oracle-specific SQL hints for complex queries
- Monitor query performance through observability components
- Consider async patterns for I/O-heavy operations

## TODO: GAPS DE ARQUITETURA IDENTIFICADOS - PRIORIDADE ALTA

### 🚨 GAP 1: Singer Integration Incomplete

**Status**: ALTO - Oracle DB library não completamente integrado com Singer ecosystem
**Problema**:

- Meltano environment variables seguem convenção mas integration não completa
- Não integra com flext-tap-oracle, flext-target-oracle ecosystem
- Schema introspection não exposta via Singer catalog patterns

**TODO**:

- [ ] Integrar completamente com flext-tap-oracle e flext-target-oracle
- [ ] Implementar Singer catalog generation from Oracle schema introspection
- [ ] Criar Oracle-specific Singer stream patterns
- [ ] Documentar Singer integration patterns

### 🚨 GAP 2: Oracle WMS Integration Gap

**Status**: ALTO - Não integra com flext-oracle-wms especializado
**Problema**:

- Oracle WMS tem library específica (flext-oracle-wms) mas não integra
- WMS-specific patterns não reutilizados
- Duplicação de Oracle connection patterns

**TODO**:

- [ ] Integrar com flext-oracle-wms patterns
- [ ] Criar shared Oracle connection patterns
- [ ] Implementar WMS-specific optimizations quando apropriado
- [ ] Documentar Oracle specialization strategy

### 🚨 GAP 3: Observability Integration Superficial

**Status**: ALTO - Integration com flext-observability mencionada mas não implementada
**Problema**:

- observability.py module exists mas integration não completa
- Oracle performance metrics não exposed via ecosystem monitoring
- Connection pool monitoring não integrated

**TODO**:

- [ ] Implementar complete flext-observability integration
- [ ] Expor Oracle performance metrics via ecosystem monitoring
- [ ] Criar Oracle connection pool monitoring
- [ ] Integrar Oracle diagnostics com ecosystem health checks

### 🚨 GAP 4: CLI Integration Missing

**Status**: ALTO - CLI commands não integrados com flext-cli
**Problema**:

- Oracle-specific make commands não accessible via flext-cli
- Oracle connection testing não available via ecosystem CLI
- Schema operations não integrated com CLI workflow

**TODO**:

- [ ] Integrar Oracle commands com flext-cli
- [ ] Criar oracle command group em flext-cli
- [ ] Implementar Oracle connection testing via CLI
- [ ] Documentar Oracle CLI usage patterns

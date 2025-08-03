# CLAUDE.md - FLEXT DB Oracle Development Guidance

**Version**: 2.0.0 | **Status**: Production Ready | **Documentation Standardized**: 100% | **Enterprise Grade**: ✅

This file provides comprehensive development guidance to Claude Code (claude.ai/code) when working with FLEXT DB Oracle, the enterprise Oracle database integration library for the FLEXT ecosystem.

## 🎯 Project Overview

**FLEXT DB Oracle** is a production-ready Oracle Database integration library that serves as the foundational data infrastructure component for the FLEXT ecosystem. Built with Python 3.13+, SQLAlchemy 2.x, and the modern `oracledb` driver, it implements Clean Architecture, Domain-Driven Design (DDD), and enterprise-grade quality standards.

### **Current Status: Enterprise Production Ready**

- ✅ **Documentation Standardization**: 100% complete across all Python modules
- ✅ **Type Annotation Coverage**: 95%+ with strict MyPy validation
- ✅ **Quality Gates**: Integrated with CI/CD pipelines
- ✅ **FLEXT Ecosystem Integration**: Full compatibility with FLEXT Core patterns
- ✅ **Enterprise Standards**: Professional documentation without marketing content

### **Architecture Role in FLEXT Ecosystem**

FLEXT DB Oracle operates as a critical infrastructure component in the FLEXT ecosystem:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM (32 Projects)                 │
├─────────────────────────────────────────────────────────────────┤
│ Services: FlexCore(Go) | FLEXT Service(Go/Python) | Clients     │
├─────────────────────────────────────────────────────────────────┤
│ Applications: API | Auth | Web | CLI | Quality | Observability  │
├═════════════════════════════════════════════════════════════════┤
│ Infrastructure: [FLEXT-DB-ORACLE] | LDAP | LDIF | gRPC | WMS    │
├─────────────────────────────────────────────────────────────────┤
│ Singer Ecosystem: Taps(5) | Targets(5) | DBT(4) | Extensions(1) │
├─────────────────────────────────────────────────────────────────┤
│ Foundation: FLEXT-CORE (FlextResult | DI | Domain Patterns)     │
└─────────────────────────────────────────────────────────────────┘
```

## 🏗️ Key Architecture Patterns

### **FLEXT Core Integration**

- **FlextResult Pattern**: Type-safe error handling with railway-oriented programming
- **Naming Convention**: All classes prefixed with `FlextDbOracle` for ecosystem consistency
- **Import Pattern**: `from flext_core import FlextResult, get_logger, FlextContainer`
- **Dependency Injection**: Consistent service location via FlextContainer

### **Clean Architecture Implementation**

- **Domain Layer**: Core business logic and entities (`metadata.py`, `types.py`)
- **Application Layer**: Use cases and services (`api.py`)
- **Infrastructure Layer**: External concerns (`connection.py`, `config.py`)
- **Presentation Layer**: CLI and external interfaces (`cli.py`)

### **SOLID Principles Refactoring**

The codebase implements extensive SOLID principles:

- **OracleConnectionManager**: Extracted class handling only connection lifecycle
- **FlextDbOracleObservabilityManager**: Centralized monitoring and error tracking
- **Plugin Architecture**: Extensible plugin system for data validation, performance monitoring, and security auditing
- **Template Method Pattern**: Used for connection retry logic and error handling

### **SQLAlchemy 2 Integration**

- Modern async/await patterns where applicable
- Enterprise connection pooling with `FlextDbOracleConnectionPool`
- Proper session management and transaction handling
- Oracle-specific optimizations and type handling

## 🚀 Development Commands

### **Essential Quality Gates**

```bash
# Setup development environment
make setup                    # Complete development setup with all tools
make install-dev              # Install dependencies including dev tools
make dev-setup                # Development environment with pre-commit hooks

# Quality gates (must pass before committing)
make validate                 # Full validation: lint + type + security + test
make check                    # Quick check: lint + type-check + security
make test                     # Run all tests with 90% coverage requirement
make lint                     # Ruff linting with ALL rules enabled
make type-check               # MyPy strict type checking
make format                   # Auto-format code with ruff
make fix                      # Auto-fix issues with ruff
make security                 # Security scanning with bandit and pip-audit
```

### **Oracle-Specific Operations**

```bash
# Oracle connectivity and validation
make oracle-test              # Basic Oracle connectivity test
make oracle-connect           # Test connection to Oracle server
make oracle-validate          # Validate Oracle configuration
make oracle-schema            # Verify Oracle schema access
make oracle-operations        # Run all Oracle validations

# Docker Oracle for testing
docker-compose -f docker-compose.oracle.yml up -d  # Start Oracle XE
docker-compose -f docker-compose.oracle.yml down   # Stop Oracle
```

### **Testing Infrastructure**

```bash
# Test categories
make test-unit                # Unit tests only (no Oracle dependency)
make test-integration         # Integration tests (requires Oracle)
make test-e2e                 # End-to-end workflow tests
make test-fast                # Fast tests for quick feedback
make coverage-html            # Generate HTML coverage report
make doctor                   # Health check with diagnostics

# Pytest markers
pytest -m unit                # Unit tests (no external dependencies)
pytest -m integration         # Integration tests (requires Oracle)
pytest -m e2e                 # End-to-end tests
pytest -m benchmark           # Performance benchmark tests
pytest -m slow                # Slow tests (excluded by default)
pytest -m smoke               # Smoke tests
pytest -m "not slow"          # Skip slow tests for quick feedback

# Coverage and reports
pytest --cov=src/flext_db_oracle --cov-report=html    # HTML coverage
pytest --cov-fail-under=90                            # Enforce 90% coverage
```

## 📁 Code Organization

### **Core Module Structure**

**Source Code (`src/flext_db_oracle/`)**:

- `__init__.py` - Public API exports and library initialization
- `api.py` - Main `FlextDbOracleApi` class with SOLID refactoring and `OracleConnectionManager`
- `config.py` - `FlextDbOracleConfig` with environment variable support and Pydantic validation
- `connection.py` - Connection management and pooling with `FlextDbOracleConnection`
- `metadata.py` - Oracle schema introspection with complete metadata extraction (tables, columns, indexes)
- `types.py` - Type definitions and Pydantic models for Oracle-specific data structures
- `observability.py` - `FlextDbOracleObservabilityManager` for monitoring and error tracking
- `plugins.py` - Plugin system with data validation, performance monitoring, and security auditing
- `cli.py` - Command-line interface using Click framework with Rich formatting
- `exceptions.py` - Custom exceptions and error handling
- `constants.py` - Constants and configuration defaults

**Testing Structure (`tests/`)**:

- `tests/unit/` - Fast unit tests with comprehensive mocking (18+ test files)
- `tests/integration/` - Tests requiring actual Oracle connection
- `tests/e2e/` - End-to-end workflow tests
- `conftest.py` - Shared pytest fixtures and Oracle test configuration

**Examples (`examples/`)**:

- `01_basic_connection.py` - Simple connection patterns
- `02_configuration_patterns.py` - Configuration management examples
- `03_query_operations.py` - Query execution and result handling
- `04_comprehensive_oracle_usage.py` - Complete feature demonstration with SOLID patterns

**Documentation (`docs/`)**:

- Complete API reference and integration guides
- Architecture documentation with Clean Architecture diagrams
- Performance optimization and troubleshooting guides

### **Plugin System Architecture**

The project implements a comprehensive plugin system:

- **Data Validation Plugin**: Schema validation and data integrity checks
- **Performance Monitor Plugin**: Query performance analysis and optimization suggestions
- **Security Audit Plugin**: Security compliance and access auditing

### **Configuration Management**

Environment variables follow Meltano/Singer conventions:

```bash
# Required Oracle connection parameters
export FLEXT_TARGET_ORACLE_HOST="oracle-server.company.com"
export FLEXT_TARGET_ORACLE_PORT="1521"
export FLEXT_TARGET_ORACLE_USERNAME="app_user"
export FLEXT_TARGET_ORACLE_PASSWORD="secure_password"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="PROD_DB"

# Optional pool and performance parameters
export FLEXT_TARGET_ORACLE_POOL_MIN="5"
export FLEXT_TARGET_ORACLE_POOL_MAX="20"
export FLEXT_TARGET_ORACLE_TIMEOUT="30"
export FLEXT_TARGET_ORACLE_CHARSET="UTF8"

# Development and testing
export ORACLE_INTEGRATION_TESTS="1"  # Enable integration tests
```

## 🏆 Quality Standards

### **Zero Tolerance Quality Gates**

- **Coverage**: Minimum 90% test coverage enforced (`--cov-fail-under=90`)
- **Type Safety**: Strict MyPy configuration with comprehensive rules (`mypy src/ --strict`)
- **Linting**: Ruff with ALL rules enabled (`select = ["ALL"]`)
- **Security**: Bandit security scanning and pip-audit dependency checks
- **Python Version**: 3.13+ only with modern type hints and patterns

### **Enterprise Code Patterns**

- **Naming**: All public classes use `FlextDbOracle` prefix for ecosystem consistency
- **Error Handling**: Use `FlextResult` pattern, never raise exceptions directly in public APIs
- **Type Safety**: Type hints required on all functions and methods
- **SOLID Principles**: Enforcement with extracted classes and single responsibilities
- **Documentation**: Comprehensive docstrings following enterprise standards with business context

### **Testing Requirements**

- **Unit Tests**: Must not require external Oracle database, use comprehensive mocking
- **Integration Tests**: Marked with `@pytest.mark.integration`, require Oracle connection
- **Test Data**: Use pytest fixtures from `conftest.py` for consistent test scenarios
- **Coverage**: Both success and failure scenarios must be tested
- **Performance**: Benchmark tests for critical database operations

## 🔗 Integration Points

### **FLEXT Ecosystem Dependencies**

- **flext-core**: Foundation patterns (FlextResult, FlextContainer, logging)
- **flext-observability**: Structured logging, metrics, and health monitoring (`FlextHealthCheck`)
- **flext-plugin**: Plugin architecture support (`FlextPlugin`)
- **flext-cli**: Command-line interface components and formatting

All dependencies use local file paths for development:

```toml
flext-core = { path = "../flext-core", develop = true }
```

### **Oracle-Specific Features**

- **Connection Management**: Enterprise-grade pooling with retry logic and health checks
- **Schema Introspection**: Complete metadata extraction using SQLAlchemy reflection
- **Performance Monitoring**: Oracle v$ views integration for query analysis
- **DDL Generation**: Automated table, index, and constraint creation
- **Plugin System**: Extensible architecture for validation, monitoring, and auditing

### **Singer Ecosystem Foundation**

FLEXT DB Oracle serves as the foundation for Singer ecosystem components:

- **flext-tap-oracle**: Data extraction using this library's connection patterns
- **flext-target-oracle**: Data loading using this library's pooling and optimization
- **flext-dbt-oracle**: Data transformation using this library's metadata capabilities

## 🛠️ Common Development Tasks

### **Adding New Functionality**

1. **Domain Modeling**: Create domain models in `types.py` using Pydantic with validation
2. **Business Logic**: Implement in appropriate layer returning `FlextResult[T]`
3. **SOLID Refactoring**: Extract classes following Single Responsibility Principle
4. **Unit Testing**: Add comprehensive unit tests with mocking for external dependencies
5. **Integration Testing**: Add integration tests if Oracle interaction required
6. **CLI Integration**: Update CLI commands in `cli.py` if new operations needed
7. **Documentation**: Update module docstrings and examples
8. **Validation**: Run full validation: `make validate`

### **Oracle Connection Development**

- **Local Development**: Use `docker-compose.oracle.yml` for local Oracle XE
- **Integration Testing**: Set `ORACLE_INTEGRATION_TESTS=1` environment variable
- **Error Handling**: Connection failures return `FlextResult.failure()` with detailed context
- **Performance**: Always use connection pooling for multi-operation scenarios
- **Monitoring**: Enable observability integration for connection health tracking

### **Debugging Oracle Issues**

```bash
# Enable comprehensive SQL logging
export ORACLE_SQL_LOGGING=1
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Oracle system views for performance analysis
# Use api.query() to access v$session, v$sql, v$sqlarea for diagnostics

# Connection debugging
make oracle-connect      # Test basic connectivity
make oracle-validate     # Validate configuration
make oracle-test        # Run connection health checks
make doctor             # Comprehensive health check with diagnostics
```

## 🐳 Docker Development Environment

### **Oracle Test Environment**

The Docker environment uses Oracle XE 21c:

- **Container**: `gvenzl/oracle-xe:21-slim`
- **Port**: 1521
- **Default DB**: XEPDB1
- **System Password**: Oracle123
- **Health Check**: Automated with 30s intervals

```bash
# Start Oracle XE 21c for testing
docker-compose -f docker-compose.oracle.yml up -d

# Monitor Oracle startup (takes 2-3 minutes)
docker-compose -f docker-compose.oracle.yml logs -f oracle-xe

# Verify Oracle is ready
docker-compose -f docker-compose.oracle.yml exec oracle-xe sqlplus system/Oracle123@XEPDB1

# Run integration tests
export ORACLE_INTEGRATION_TESTS=1
make test-integration

# Cleanup environment
docker-compose -f docker-compose.oracle.yml down -v
```

### **Development Workflow**

For optimal development experience:

1. **Initial Setup**: `make setup` - installs dependencies and pre-commit hooks
2. **Quality Gates**: `make validate` - comprehensive validation pipeline
3. **Fast Feedback**: `make test-unit` - unit tests without Oracle dependency
4. **Integration Testing**: Start Oracle XE and run `make test-integration`
5. **Continuous Validation**: Pre-commit hooks enforce quality standards

## 🔧 CLI Commands

The project provides multiple CLI entry points:

```bash
flext-db-oracle          # Main CLI interface
flext-oracle-migrate     # Database migration tools
flext-oracle             # Alias for main CLI
```

Available CLI commands:

- `connect` - Connect to Oracle database with parameters
- `connect-env` - Connect using environment variables
- `query` - Execute SQL queries with rich formatting
- `schemas` - List Oracle database schemas
- `tables` - List tables with optional schema filtering
- `plugins` - Manage Oracle database plugins
- `optimize` - Optimize SQL queries using built-in plugins
- `health` - Check Oracle database health status

## 🚨 Troubleshooting

### **Common Issues & Solutions**

**Import Errors**:

```bash
# Ensure FLEXT core dependencies are properly installed
pip install -e ../flext-core
make install-dev
```

**Oracle Connection Issues**:

```bash
# Verify Oracle service is running
docker-compose -f docker-compose.oracle.yml ps

# Check Oracle logs for startup issues
docker-compose -f docker-compose.oracle.yml logs oracle-xe

# Test basic connectivity
make oracle-connect
```

**Type Errors**:

```bash
# Run detailed MyPy analysis
make type-check
mypy src/ --show-error-codes --show-column-numbers
```

**Test Failures**:

```bash
# Check if integration tests need Oracle
pytest tests/integration/ --collect-only

# Run only unit tests (no Oracle dependency)
make test-unit

# Enable debug logging for tests
pytest -v -s --log-cli-level=DEBUG
```

### **Performance Optimization**

- **Connection Pooling**: Use connection pooling for multiple operations
- **Oracle Hints**: Leverage Oracle-specific SQL hints for complex queries
- **Bulk Operations**: Use batch operations for high-volume data processing
- **Monitoring**: Monitor query performance through observability components
- **Async Patterns**: Consider async patterns for I/O-heavy operations

## 📊 Current Project Status

### **✅ Completed Features (Production Ready)**

- **Enterprise Documentation**: 100% docstring standardization complete
- **Type Safety**: 95%+ type annotation coverage with strict MyPy
- **Quality Gates**: Comprehensive linting, testing, and security scanning
- **FLEXT Integration**: Full compatibility with FLEXT Core patterns
- **Oracle Operations**: Complete connection management and query execution
- **CLI Interface**: Rich terminal interface with comprehensive Oracle commands
- **Plugin System**: Extensible architecture for custom functionality
- **Testing Infrastructure**: Unit, integration, and e2e testing strategies (18+ test files)
- **SOLID Architecture**: Extensive refactoring with extracted classes and single responsibilities
- **Docker Environment**: Complete Oracle XE development environment with health checks

### **Key Architectural Achievements**

- **OracleConnectionManager**: Extracted class implementing Template Method pattern for connection lifecycle
- **FlextDbOracleObservabilityManager**: Centralized monitoring and error tracking
- **Plugin Architecture**: Extensible system for adding Oracle-specific functionality
- **FlextResult Pattern**: Railway-oriented programming for consistent error handling

### **🔄 Current Development Focus**

- **Singer Integration**: Completing integration with Singer ecosystem components
- **Performance Optimization**: Oracle-specific query optimization and monitoring
- **Observability Enhancement**: Advanced metrics and health monitoring
- **Documentation Completion**: API reference and integration guides

## 🚨 Critical Architecture Gaps (High Priority)

### **GAP 1: Singer Ecosystem Integration**

**Status**: HIGH PRIORITY - Oracle DB library integration with Singer ecosystem incomplete

**Current Issues**:

- Meltano environment variables follow convention but integration not complete
- Schema introspection not exposed via Singer catalog patterns
- Missing integration with flext-tap-oracle and flext-target-oracle

**Required Actions**:

- [ ] Complete integration with flext-tap-oracle and flext-target-oracle
- [ ] Implement Singer catalog generation from Oracle schema introspection
- [ ] Create Oracle-specific Singer stream patterns and configuration
- [ ] Document Singer integration patterns and best practices

### **GAP 2: Oracle WMS Specialization Integration**

**Status**: HIGH PRIORITY - Missing integration with flext-oracle-wms specialization

**Current Issues**:

- Oracle WMS has specialized library (flext-oracle-wms) but no integration
- WMS-specific patterns not reused, causing duplication
- Oracle connection patterns duplicated across projects

**Required Actions**:

- [ ] Integrate with flext-oracle-wms patterns and configurations
- [ ] Create shared Oracle connection patterns across ecosystem
- [ ] Implement WMS-specific optimizations when appropriate
- [ ] Document Oracle specialization strategy and architecture

### **GAP 3: Advanced Observability Integration**

**Status**: HIGH PRIORITY - Observability integration incomplete

**Current Issues**:

- observability.py module exists but integration not complete
- Oracle performance metrics not exposed via ecosystem monitoring
- Connection pool monitoring not integrated with FLEXT observability stack

**Required Actions**:

- [ ] Complete flext-observability integration with metrics export
- [ ] Expose Oracle performance metrics via ecosystem monitoring
- [ ] Create Oracle connection pool monitoring and alerting
- [ ] Integrate Oracle diagnostics with ecosystem health checks

### **GAP 4: FLEXT CLI Integration**

**Status**: HIGH PRIORITY - CLI commands not integrated with ecosystem CLI

**Current Issues**:

- Oracle-specific make commands not accessible via flext-cli
- Oracle connection testing not available via ecosystem CLI
- Schema operations not integrated with CLI workflow

**Required Actions**:

- [ ] Integrate Oracle commands with flext-cli command groups
- [ ] Create `flext oracle` command group in ecosystem CLI
- [ ] Implement Oracle connection testing via unified CLI interface
- [ ] Document Oracle CLI usage patterns and integration

## 🎯 Development Priorities & Next Steps

### **Immediate Actions (Week 1-2)**

1. **Complete Singer Integration**: Implement catalog generation and stream patterns
2. **Oracle WMS Integration**: Establish shared connection patterns
3. **Advanced Observability**: Complete metrics export and monitoring integration
4. **CLI Unification**: Integrate Oracle commands with flext-cli

### **Medium-term Goals (Month 1-2)**

1. **Performance Optimization**: Implement Oracle-specific query optimization
2. **Advanced Plugin System**: Create extensible plugin architecture
3. **Enhanced Testing**: Add comprehensive benchmark and performance tests
4. **Documentation Completion**: Complete API reference and integration guides

### **Quality Assurance**

- **Every commit** must pass `make validate` quality gates
- **Integration tests** must pass with Oracle XE Docker environment
- **Type coverage** must maintain 95%+ with strict MyPy validation
- **Documentation** must remain 100% enterprise-grade without marketing content

---

**FLEXT DB Oracle** - Enterprise Oracle database integration for the FLEXT data platform. Built with ❤️ following Clean Architecture, DDD, and FLEXT ecosystem patterns.

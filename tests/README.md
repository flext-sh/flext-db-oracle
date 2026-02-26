# FLEXT DB Oracle Test Suite

<!-- TOC START -->

- [🧪 Test Structure](#-test-structure)
  - [**Test Organization**](#test-organization)
  - [**Testing Layers**](#testing-layers)
- [📋 Test Categories](#-test-categories)
  - [**Core Module Tests**](#core-module-tests)
  - [**Infrastructure Tests**](#infrastructure-tests)
- [🏗️ Test Architecture](#-test-architecture)
  - [**Clean Architecture Testing Patterns**](#clean-architecture-testing-patterns)
  - [**Testing Principles**](#testing-principles)
- [🚀 Running Tests](#-running-tests)
  - [**Quick Test Commands**](#quick-test-commands)
  - [**Test Configuration**](#test-configuration)
  - [**Coverage Requirements**](#coverage-requirements)
- [📊 Test Quality Standards](#-test-quality-standards)
  - [**Test Quality Gates**](#test-quality-gates)
  - [**Test Naming Conventions**](#test-naming-conventions)
  - [**Test Documentation Standards**](#test-documentation-standards)
  - [**Assertion Patterns**](#assertion-patterns)
- [🔧 Test Development Guidelines](#-test-development-guidelines)
  - [**Adding New Tests**](#adding-new-tests)
  - [**Test Maintenance**](#test-maintenance)
  - [**Mock Strategy**](#mock-strategy)
- [🧭 Test Execution Strategy](#-test-execution-strategy)
  - [**Development Workflow**](#development-workflow)
  - [**CI/CD Integration**](#cicd-integration)

<!-- TOC END -->

This directory contains the comprehensive test suite for FLEXT DB Oracle, implementing a layered testing strategy with unit, integration, and end-to-end tests following Clean Architecture principles and enterprise testing standards.

## 🧪 Test Structure

### **Test Organization**

The test suite is organized into three distinct layers, each serving specific testing purposes:

```
tests/
├── unit/           # Fast, isolated tests with mocks
├── integration/    # Tests requiring actual Oracle database
├── e2e/           # End-to-end workflow tests
└── conftest.py    # Shared test fixtures and configuration
```

### **Testing Layers**

#### **Unit Tests (`unit/`)**

- **Fast execution** (< 1 second per test)
- **No external dependencies** (database, network, filesystem)
- **High coverage** of business logic and edge cases
- **Mock-based** isolation of external systems
- **Test individual components** in isolation

#### **Integration Tests (`integration/`)**

- **Real Oracle database connection** required
- **Test component interactions** and data flow
- **Database schema validation** and query execution
- **Connection pooling** and resource management
- **Performance benchmarking** for database operations

#### **End-to-End Tests (`e2e/`)**

- **Complete workflow testing** from CLI to database
- **Real-world scenarios** and user journeys
- **Full system integration** including plugins and observability
- **Production-like environment** testing

## 📋 Test Categories

### **Core Module Tests**

#### **API Tests (`test_api*.py`)**

- `test_api.py` - Basic API functionality and error handling
- `test_api_comprehensive.py` - Complete API surface coverage
- `test_api_missing_coverage.py` - Edge cases and error scenarios
- `test_api_real_execution.py` - Real database execution scenarios

#### **Configuration Tests (`test_config.py`)**

- Environment variable loading and validation
- URL parsing and connection string generation
- SSL/TLS configuration validation
- Multi-environment configuration scenarios

#### **Connection Tests (`test_connection*.py`)**

- `test_connection.py` - Basic connection management
- `test_connection_comprehensive.py` - Connection pooling and lifecycle
- `test_connection_focused.py` - Specific connection scenarios
- `test_connection_targeted.py` - Performance and reliability testing

#### **Metadata Tests (`test_metadata.py`)**

- Oracle schema introspection and analysis
- DDL generation and validation
- Table and column metadata extraction
- Domain validation and business rules

#### **Type Tests (`test_types.py`)**

- Domain value object validation and immutability
- Type conversion and Oracle-specific mappings
- Pydantic model validation and serialization
- Domain rule enforcement

### **Infrastructure Tests**

#### **CLI Tests (`test_cli*.py`)**

- `test_cli_simple.py` - Basic CLI command functionality
- `test_cli_comprehensive.py` - Complete CLI command coverage
- `test_cli_targeted.py` - Specific CLI scenarios and error handling

#### **Observability Tests (`test_observability_comprehensive.py`)**

- Metrics collection and reporting
- Distributed tracing and performance monitoring
- Health check implementation and status reporting
- Error handling and observability integration

#### **Plugin Tests (`test_plugins_comprehensive.py`)**

- Plugin registration and lifecycle management
- Performance monitoring plugin functionality
- Security audit plugin validation
- Data validation plugin business rules

## 🏗️ Test Architecture

### **Clean Architecture Testing Patterns**

Our test suite follows Clean Architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                    E2E Tests                                    │
│  Complete workflow testing with real systems                   │
├─────────────────────────────────────────────────────────────────┤
│                Integration Tests                                │
│  Component interaction with real Oracle database               │
├─────────────────────────────────────────────────────────────────┤
│                    Unit Tests                                   │
│  Isolated component testing with mocks                         │
├═════════════════════════════════════════════════════════════════┤
│                  Shared Fixtures                               │
│  conftest.py: Test data, mocks, and utilities                 │
└─────────────────────────────────────────────────────────────────┘
```

### **Testing Principles**

#### **SOLID Testing Patterns**

- **Single Responsibility**: Each test has one clear assertion
- **Open/Closed**: Tests extend behavior without modifying core test infrastructure
- **Liskov Substitution**: Mock implementations conform to real interfaces
- **Interface Segregation**: Focused test fixtures for specific concerns
- **Dependency Inversion**: Tests depend on abstractions, not implementations

#### **DRY Testing Patterns**

- **Shared fixtures** in `conftest.py` eliminate duplication
- **Parameterized tests** for testing multiple scenarios
- **Helper functions** for common test operations
- **Test data builders** for consistent test object creation

## 🚀 Running Tests

### **Quick Test Commands**

```bash
# Run all tests
make test

# Run tests by category
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/e2e/                     # End-to-end tests only

# Run tests by marker
pytest -m "not slow"                  # Fast tests only
pytest -m integration                 # Integration tests only
pytest -m oracle                      # Oracle-specific tests
```

### **Test Configuration**

#### **Environment Variables for Integration Tests**

```bash
# Required for integration tests
export ORACLE_INTEGRATION_TESTS=1
export FLEXT_TARGET_ORACLE_HOST=localhost
export FLEXT_TARGET_ORACLE_PORT=1521
export FLEXT_TARGET_ORACLE_SERVICE_NAME=XEPDB1
export FLEXT_TARGET_ORACLE_USERNAME=test_user
export FLEXT_TARGET_ORACLE_PASSWORD=test_password
```

#### **Docker Test Environment**

```bash
# Start Oracle XE for integration testing
docker-compose -f docker-compose.oracle.yml up -d

# Wait for Oracle to be ready
docker-compose -f docker-compose.oracle.yml logs -f oracle-xe

# Run integration tests
make test-integration

# Cleanup
docker-compose -f docker-compose.oracle.yml down -v
```

### **Coverage Requirements**

All tests must maintain high coverage standards:

```bash
# Generate coverage report
make test

# Detailed coverage report
pytest --cov --cov-report=html --cov-report=term
```

> Coverage thresholds are configured in `pyproject.toml` under `[tool.coverage.report]`.

## 📊 Test Quality Standards

### **Test Quality Gates**

All tests must pass these quality standards:

- **Coverage**: Minimum 90% code coverage across all modules
- **Performance**: Unit tests < 1s, Integration tests < 30s
- **Reliability**: Tests must be deterministic and repeatable
- **Isolation**: Tests cannot depend on external state or order
- **Documentation**: All test functions have clear docstrings

### **Test Naming Conventions**

```python
# Test naming pattern: test_<method>_<scenario>_<expected_result>
def test_connect_with_valid_config_returns_success():
    """Test successful connection with valid configuration."""

def test_query_with_invalid_sql_returns_failure():
    """Test query execution failure with invalid SQL."""

def test_metadata_extraction_with_empty_schema_returns_empty_result():
    """Test metadata extraction returns empty result for empty schema."""
```

### **Test Documentation Standards**

Each test file includes:

- **Module docstring** explaining test scope and purpose
- **Test class docstrings** for grouped test scenarios
- **Individual test docstrings** describing specific test cases
- **Fixture documentation** for shared test utilities

### **Assertion Patterns**

Following FLEXT Core patterns for consistent testing:

```python
# FlextResult pattern testing
result = api.connect()
assert result.success
assert result.value is not None

# Error testing
result = api.connect_with_invalid_config()
assert result.is_failure
assert "Configuration invalid" in result.error

# Domain validation testing
validation_result = entity.validate_domain_rules()
assert validation_result.success
```

## 🔧 Test Development Guidelines

### **Adding New Tests**

1. **Determine test layer**: Unit, Integration, or E2E based on dependencies
1. **Follow naming conventions**: Clear, descriptive test names
1. **Use appropriate fixtures**: Leverage shared fixtures from conftest.py
1. **Test both success and failure scenarios**: Comprehensive edge case coverage
1. **Maintain isolation**: Tests must not affect each other

### **Test Maintenance**

1. **Keep tests simple**: One assertion per test when possible
1. **Update tests with code changes**: Maintain test-code synchronization
1. **Remove obsolete tests**: Clean up tests for removed functionality
1. **Optimize test performance**: Minimize test execution time
1. **Document test intent**: Clear docstrings and comments

### **Mock Strategy**

Use mocks appropriately based on test layer:

```python
# Unit tests: Mock external dependencies
@patch('flext_db_oracle.connection.create_engine')
def test_connection_creation_with_mocked_database():
    """Test connection creation with mocked database engine."""

# Integration tests: Use real Oracle database
def test_connection_with_real_oracle_database():
    """Test connection with actual Oracle database."""

# E2E tests: Full system without mocks
def test_complete_workflow_without_mocks():
    """Test complete workflow from CLI to database."""
```

## 🧭 Test Execution Strategy

### **Development Workflow**

```bash
# Fast feedback loop during development
pytest tests/unit/ -x --tb=short      # Stop on first failure

# Complete validation before commit
make validate                          # Full validation pipeline

# Performance testing
pytest tests/integration/ --benchmark  # Performance benchmarks
```

### **CI/CD Integration**

Tests are integrated into CI/CD pipelines with:

- **Parallel execution** for faster feedback
- **Test result reporting** with detailed coverage
- **Failure analysis** with logs and stack traces
- **Performance regression detection** through benchmarks

______________________________________________________________________

This test suite ensures FLEXT DB Oracle maintains quality standards while providing fast feedback for development and reliable validation for production deployments.

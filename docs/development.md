# Development

<!-- TOC START -->

- [Setup](#setup)
- [Quality Commands](#quality-commands)
- [Implementation Status](#implementation-status)
  - [✅ COMPLETED - Foundation Layer (100%)](#completed-foundation-layer-100)
  - [🚨 BLOCKED - Testing & Quality Assurance (85%)](#blocked-testing-quality-assurance-85)
  - [⚠️ PARTIAL - CLI Layer (60%)](#partial-cli-layer-60)
  - [❌ NOT IMPLEMENTED - Advanced Features (0%)](#not-implemented-advanced-features-0)
- [Testing Strategy](#testing-strategy)
  - [Test Categories](#test-categories)
  - [Test Infrastructure](#test-infrastructure)
  - [Test Environment Setup](#test-environment-setup)
- [Lessons Learned & Best Practices](#lessons-learned-best-practices)
  - [1. **FLEXT-Core Integration Success**](#1-flext-core-integration-success)
  - [2. **SQLAlchemy Abstraction Excellence**](#2-sqlalchemy-abstraction-excellence)
  - [3. **Testing Infrastructure Maturity**](#3-testing-infrastructure-maturity)
  - [4. **Type Safety Achievement**](#4-type-safety-achievement)
  - [5. **Clean Architecture Validation**](#5-clean-architecture-validation)
  - [6. **CLI Architecture Evolution**](#6-cli-architecture-evolution)
- [Development Workflow](#development-workflow)
  - [Daily Development Cycle](#daily-development-cycle)
  - [Code Quality Standards](#code-quality-standards)
- [Troubleshooting](#troubleshooting)
  - [Common Development Issues](#common-development-issues)
  - [Performance Issues](#performance-issues)
  - [Architecture Issues](#architecture-issues)
  - [Current Test Issues Troubleshooting](#current-test-issues-troubleshooting)

<!-- TOC END -->

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

### ✅ COMPLETED - Foundation Layer (100%)

#### Working Components

- ✅ **Core Database Operations**: Query, execute, schema introspection fully functional
- ✅ **SQLAlchemy 2.0 Integration**: Complete abstraction with clean separation
- ✅ **FlextResult Error Handling**: 784+ occurrences, railway pattern throughout
- ✅ **Configuration Management**: Pydantic-based configuration with validation
- ✅ **FLEXT Ecosystem Integration**: Complete flext-core, flext-cli integration
- ✅ **Type Safety**: Pyrefly strict mode compliant (ZERO errors)
- ✅ **Code Quality**: Ruff linting compliant (ZERO violations)
- ⚠️ **Test Coverage**: ~95% (test failures prevent full validation)

#### Production-Ready Features

- ✅ **Connection Pooling**: Enterprise-grade connection management
- ✅ **Transaction Support**: ACID compliance with proper error handling
- ✅ **Schema Introspection**: Complete metadata extraction capabilities
- ✅ **Query Optimization**: Parameter binding and result processing
- ✅ **Error Recovery**: Comprehensive error hierarchy and handling

### 🚨 BLOCKED - Testing & Quality Assurance (85%)

#### Current Issues

- ❌ **Import Failures**: Major test files failing due to flext-core test utility issues
- ❌ **Pydantic Deprecations**: Deprecated class-based config in production code
- ❌ **Constants Validation**: Test failures indicating potential constant misconfigurations
- ❌ **CI/CD Pipeline**: Automated testing blocked by import failures

#### Immediate Priorities

- 🔧 **Fix Test Imports**: Resolve flext-core test utility import errors
- 🔧 **Update Pydantic**: Migrate to ConfigDict pattern for v3 compatibility
- 🔧 **Validate Constants**: Ensure test expectations match actual values
- 🔧 **Test Framework Audit**: Verify all test dependencies work correctly

### ⚠️ PARTIAL - CLI Layer (60%)

#### Implemented Components

- ✅ **CLI Architecture**: Click integration with flext-cli patterns
- ✅ **Command Structure**: Command registration and dispatching
- ✅ **CLI Models**: Pydantic models for CLI operations
- ✅ **Basic Output**: Functional CLI with text-based output

#### Critical Gaps (Phase 2 Priority)

- ❌ **Rich Formatters**: SimpleNamespace placeholders (client.py:60-74)
- ❌ **Table Display**: No Rich table rendering for query results
- ❌ **Progress Indicators**: Missing progress bars for long operations
- ❌ **Interactive Prompts**: Placeholder implementations only
- ❌ **Error Formatting**: Basic error messages, not user-friendly

### ❌ NOT IMPLEMENTED - Advanced Features (0%)

#### Future Features

- ❌ **Async Support**: Synchronous operations only
- ❌ **DataFrame Integration**: No pandas/polars support
- ❌ **Oracle 23ai Features**: Vector types, statement pipelining
- ❌ **Advanced Caching**: No query result caching
- ❌ **Bulk Operations**: No optimized bulk insert/update

## Testing Strategy

### Test Categories

```bash
# Unit tests (no external dependencies)
pytest tests/unit/ -v

# Integration tests (requires Oracle container)
make oracle-start
pytest tests/integration/ -v
make oracle-stop

# End-to-end tests
pytest tests/e2e/ -v

# All tests with coverage
make test  # 100% coverage required
```

### Test Infrastructure

#### Test Framework Features

- **30 Test Files**: 8,633+ lines of comprehensive test code
- **287 Tests**: 286 passing, 1 error (CLI formatter placeholders)
- **100% Coverage**: Mandatory requirement for all production code
- **Pytest Ecosystem**: Markers, fixtures, parametrization, parallel execution

#### Test Categories Implemented

- ✅ **Unit Tests**: Individual component testing (243 tests)
- ✅ **Integration Tests**: Real Oracle XE 21c container testing (32 tests)
- ✅ **E2E Tests**: Complete workflow validation (11 tests)
- ✅ **Performance Tests**: Benchmarking capabilities

### Test Environment Setup

#### Local Development

```bash
# Install test dependencies
poetry install --with test

# Run full test suite
make test

# Run with coverage report
make coverage-html
open htmlcov/index.html
```

#### Oracle Integration Testing

```bash
# Start Oracle container
make oracle-start

# Test connectivity
make oracle-connect

# Run integration tests
pytest tests/integration/ -v

# Clean up
make oracle-stop
```

## Lessons Learned & Best Practices

### 1. **FLEXT-Core Integration Success**

#### Challenge

Integrating with 32+ dependent FLEXT projects while maintaining backward compatibility and performance.

#### Solution Implemented

- **Complete FlextResult Migration**: 784+ occurrences across codebase
- **Backward Compatibility**: Maintained both `.data` and `.value` APIs
- **Type Safety**: Zero Pyrefly errors across entire codebase
- **Clean Architecture**: Clear separation between infrastructure, domain, and application layers

#### Best Practices Established

- **Railway Pattern Throughout**: All operations return `FlextResult[T]`
- **Single Class Per Module**: Unified API per module (FlextDbOracleApi, FlextDbOracleModels, etc.)
- **Root Module Imports**: `from flext_db_oracle import X` only, no internal imports
- **Zero Breaking Changes**: Maintained API compatibility across ecosystem

### 2. **SQLAlchemy Abstraction Excellence**

#### Challenge

Creating clean SQLAlchemy abstraction without leaking implementation details while providing full Oracle functionality.

#### Solution Implemented

- **Single Import Point**: Only `api.py` imports SQLAlchemy/oracledb
- **Complete Abstraction**: All other modules use FlextDbOracleApi
- **Infrastructure Isolation**: Clean separation between domain and infrastructure layers
- **Ecosystem Protection**: Prevents SQLAlchemy version conflicts across 32+ projects

#### Best Practices Established

- **Abstraction Layers**: Domain models never import infrastructure
- **API-First Design**: All database operations through unified API
- **Dependency Isolation**: Infrastructure concerns contained in single module
- **Version Management**: Centralized SQLAlchemy version management

### 3. **Testing Infrastructure Maturity**

#### Challenge

Achieving 100% test coverage with real Oracle integration while maintaining fast execution and CI/CD compatibility.

#### Solution Implemented

- **30 Test Files**: Comprehensive coverage with 8,633+ lines of test code
- **287 Tests**: 286 passing with 45.23s execution time
- **Oracle Container Integration**: Real database testing with Docker
- **Parallel Execution**: pytest-xdist support for faster CI/CD

#### Best Practices Established

- **Fixture-Based Testing**: Reusable fixtures for consistent test setup
- **Parametrized Testing**: Multiple scenarios tested efficiently
- **Mock Strategy**: Minimal mocking, prefer real implementations
- **Performance Benchmarks**: < 30s unit tests, < 60s integration tests

### 4. **Type Safety Achievement**

#### Challenge

Achieving Pyrefly strict mode compliance across large, complex codebase with multiple integrations.

#### Solution Implemented

- **100% Type Annotations**: No `object` types, complete type coverage
- **Pyrefly Strict Compliance**: Zero type checking errors
- **Protocol Usage**: Structural typing for clean interfaces
- **Generic Type Support**: Full support for `FlextResult[T]` generics

#### Best Practices Established

- **Type-Only Imports**: Clear separation of runtime vs type-only imports
- **Protocol Classes**: Structural typing over inheritance
- **Generic Constraints**: Proper generic type usage throughout
- **Type Checking Discipline**: Type issues fixed at source, not suppressed

### 5. **Clean Architecture Validation**

#### Challenge

Implementing Clean Architecture patterns at scale while maintaining practical usability and performance.

#### Solution Implemented

- **Layer Separation**: Strict infrastructure/domain/application separation
- **Dependency Direction**: Only inward dependencies (infrastructure ← domain ← application)
- **API Consolidation**: Single entry point per layer
- **Service Patterns**: Domain services with infrastructure abstraction

#### Best Practices Established

- **Domain-First Design**: Domain models drive infrastructure implementation
- **Service Layer Pattern**: Business logic in dedicated service classes
- **Repository Pattern**: Data access abstraction through services
- **Dependency Injection**: FlextContainer for service management

### 6. **CLI Architecture Evolution**

#### Challenge

Building CLI foundation that integrates with FLEXT ecosystem while preparing for Rich enhancement.

#### Current State

- **Foundation Complete**: Click integration with flext-cli patterns established
- **Placeholder Strategy**: SimpleNamespace allows functional CLI while Rich is developed
- **Architecture Ready**: Clean separation for Rich formatter integration
- **Phase 2 Planned**: Complete Rich integration with professional output

#### Best Practices Established

- **Abstraction Layers**: Separate CLI framework from output formatting
- **Progressive Enhancement**: Functional CLI first, rich features second
- **Pattern Consistency**: Follow flext-cli established patterns
- **Incremental Implementation**: Replace placeholders without breaking existing functionality

## Development Workflow

### Daily Development Cycle

```bash
# Start development session
make setup              # Ensure environment is ready

# Code changes
# ... make changes ...

# Quality checks (MANDATORY before commit)
make check              # Lint + type check (quick)
make test               # Full test suite (100% coverage required)

# Oracle testing (when database changes made)
make oracle-start       # Start Oracle container
make oracle-operations  # Test database operations
make oracle-stop        # Clean up

# Commit with clean quality gates
make validate           # Final validation (lint + type + security + test)
git commit -m "feat: description of changes"
```

### Code Quality Standards

#### Type Safety (ZERO TOLERANCE)

- **Pyrefly strict mode**: All `src/` code must pass without errors
- **100% type annotations**: No `object` types allowed
- **Protocol compliance**: Structural typing over inheritance

#### Code Quality (ZERO TOLERANCE)

- **Ruff linting**: Zero violations in production code
- **Line length**: 88 characters maximum (Ruff default)
- **Import organization**: Ruff handles automatically

#### Testing Standards (MANDATORY)

- **100% coverage**: All production code must be tested
- **Real implementations**: Prefer actual code over excessive mocking
- **Performance**: Tests must complete within time budgets

## Troubleshooting

### Common Development Issues

#### Import Errors

```bash
# Always use PYTHONPATH for proper imports
PYTHONPATH=src poetry run python -c "from flext_db_oracle import FlextDbOracleApi"
```

#### Type Checking Issues

```bash
# Run type check to identify issues
make type-check

# Focus on specific modules
PYTHONPATH=src poetry run pyrefly check src/flext_db_oracle/api.py
```

#### Test Failures

```bash
# Run failing tests with verbose output
PYTHONPATH=src poetry run pytest tests/unit/test_api.py -vv

# Run last failed tests
PYTHONPATH=src poetry run pytest --lf
```

#### Oracle Connection Issues

```bash
# Test Oracle connectivity
make oracle-connect

# Check configuration
PYTHONPATH=src poetry run python -c "
from flext_db_oracle import FlextDbOracleSettings
config = FlextDbOracleSettings()
print(f'Host: {config.oracle_host}:{config.oracle_port}')
"
```

### Performance Issues

#### Slow Test Execution

- Use `pytest-xdist` for parallel execution
- Focus on unit tests for fast feedback
- Run integration tests separately

#### Memory Usage

- Monitor memory usage during testing
- Use fixtures with appropriate scope
- Clean up resources in test teardown

### Architecture Issues

#### Circular Imports

- Maintain layer hierarchy (infrastructure → domain → application)
- Use dependency injection to break circular dependencies
- Import services at runtime when necessary

#### API Compatibility

- Test changes against dependent projects
- Maintain backward compatibility
- Use deprecation warnings for API changes

### Current Test Issues Troubleshooting

#### Import Failures in Test Files

**Issue**: `ImportError: cannot import name 'FlextTestsBuilders' from 'flext_tests.matchers'`

```bash
# Check what's available in flext-core test utilities
PYTHONPATH=src python -c "from flext_tests.matchers import *; print(dir())"

# Fix: Update test imports to use correct flext-core utilities
# Replace: from flext_tests.matchers import FlextTestsBuilders
# With: from flext_tests.matchers import FlextTestsMatchers  # or correct import
```

#### Pydantic Deprecation Warnings

**Issue**: `PydanticDeprecatedSince20: Support for class-based config is deprecated`

```bash
# Current problematic code in src/flext_db_oracle/exceptions.py:28
class ExceptionParams(FlextModels.Entity):
    class Config:  # DEPRECATED
        pass

# Fix: Migrate to ConfigDict
from pydantic import ConfigDict

class ExceptionParams(FlextModels.Entity):
    model_config = ConfigDict()  # MODERN APPROACH
```

#### Constants Test Failures

**Issue**: Network constants test failing (expecting 1024, getting 1)

```bash
# Check actual constant values
PYTHONPATH=src python -c "from flext_db_oracle.constants import FlextDbOracleConstants; print(FlextDbOracleConstants.Network.MIN_PORT)"

# Fix: Either update constants or correct test expectations
# Option 1: Update constant to match test expectation
# Option 2: Update test to match actual constant value
```

#### Test Collection Issues

**Issue**: `collected 11 items / 1 error` - Major test files not loading

```bash
# Run specific working tests first
PYTHONPATH=src poetry run pytest tests/unit/test_constants.py -v

# Debug import issues
PYTHONPATH=src python -c "import tests.unit.test_api" 2>&1

# Check flext-core compatibility
PYTHONPATH=src python -c "import flext_core; print(flext_core.__version__)"
```

---

Updated: October 10, 2025 | Version: 0.9.0

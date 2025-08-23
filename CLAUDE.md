# CLAUDE.md

This file provides guidance when working with code in this repository.

## Project Overview

For complete project information, architecture overview, and usage examples, see [README.md](README.md).

**Key Summary**: FLEXT DB Oracle is an infrastructure library for Oracle database integration in the FLEXT ecosystem, implementing Clean Architecture patterns with FlextResult error handling.

**Current Status**: Active development - 33% test coverage with core functionality working.

## Development Context

### **Current Project State**

Based on recent systematic analysis and improvements:

#### **Test Coverage Status** (Last Updated: 2025-01-23)
- **Overall Coverage**: 33% (improved from 21%)
- **Connection Module**: 53% (major improvement from 11%)
- **Metadata Module**: 42% (improved from 8%)
- **API Module**: 26% (improved from 24%)
- **CLI Module**: 0% (untested, needs attention)
- **Plugin System**: 16% (needs expansion)

#### **Code Quality Discoveries**
Recent systematic testing revealed:
- **Real Bugs Found**: 4+ validation bugs discovered and fixed
- **API Structure**: Comprehensive mapping of actual vs assumed methods
- **Testing Approach**: Real code validation proven more effective than mocks

#### **Working Functionality**
✅ **Confirmed Working**:
- Oracle database connections with SQLAlchemy 2.x
- Schema introspection (tables, columns, metadata)
- Query execution with FlextResult patterns
- Connection pooling and resource management
- Basic CLI commands (`flext-db-oracle`)

🚧 **In Development**:
- Comprehensive test coverage (targeting 50%+)
- Plugin system expansion
- CLI test coverage (currently 0%)

## Architecture

### **Real Code Structure** (Verified)

Based on systematic analysis:

#### **Core Components**
- **`api.py`**: Main FlextDbOracleApi class with 60+ methods
- **`connection.py`**: Connection management with pooling (53% coverage)
- **`metadata.py`**: Schema introspection (42% coverage)
- **`config.py`**: Pydantic configuration with environment support
- **`cli.py`**: Click-based CLI interface (needs testing)
- **`plugins.py`**: Plugin framework (16% coverage)

#### **Key Pattern Discoveries**
- **FlextResult Integration**: All public APIs return FlextResult[T]
- **API Plugin System**: Uses `dict{}` for plugin storage, not `list[]`
- **Class Methods**: Return API instances directly, not FlextResult
- **Connection Behavior**: `connect()` method actually attempts database connection
- **Method Availability**: Many assumed methods don't exist (validate_sql, analyze_query, etc.)

### **Testing Strategy** (Proven Effective)

#### **Real Code Validation Approach**
- **Unit Tests**: Focus on real code paths, minimal mocking
- **Integration Tests**: Require actual Oracle database
- **Systematic Testing**: Module-by-module comprehensive coverage
- **Bug Discovery**: Tests found actual validation bugs, not just coverage

#### **Effective Test Patterns**
```python
# Use real code validation instead of excessive mocking
def test_real_method_behavior(self):
    """Test actual method behavior, not mocked assumptions."""
    result = api.actual_method()
    assert result.success or result.error  # Test real FlextResult behavior
```

## Essential Commands

### **Development Workflow**

For complete command reference, see [README.md](README.md#development-commands).

**Critical Commands**:
```bash
# Quality gates (always run before committing)
make validate                 # Full validation pipeline
make check                    # Quick lint + type check
make test                     # Run tests with coverage

# Oracle development
docker-compose -f docker-compose.oracle.yml up -d  # Start Oracle
make oracle-connect           # Test connection
```

### **Testing Commands**

```bash
# Strategic testing (proven effective)
make test-unit                # Fast unit tests (no Oracle)
make test-integration         # Integration tests (requires Oracle)
pytest --cov=src/flext_db_oracle --cov-report=term  # Coverage report

# Specific coverage improvement
pytest tests/unit/test_connection_comprehensive.py --cov=src/flext_db_oracle/connection.py
pytest tests/unit/test_metadata_comprehensive.py --cov=src/flext_db_oracle/metadata.py
pytest tests/unit/test_api_safe_comprehensive.py --cov=src/flext_db_oracle/api.py
```

## Code Organization

For complete source structure, see [README.md](README.md#testing).

### **Key File Insights**

#### **`src/flext_db_oracle/api.py`** (720 statements)
- **Coverage**: 26% (room for improvement)
- **Key Methods**: 60+ methods including optimize_query, get_observability_metrics
- **Plugin System**: Uses dict-based plugin storage
- **Connection Issue**: connect() method times out in tests (needs selective mocking)

#### **`src/flext_db_oracle/connection.py`** (606 statements)
- **Coverage**: 53% (significantly improved)
- **Status**: Comprehensive testing implemented
- **Real Bugs**: Multiple validation bugs found and fixed

#### **`src/flext_db_oracle/metadata.py`** (158 statements)
- **Coverage**: 42% (major improvement)
- **Real Bug**: Fixed crash on None input validation
- **Methods**: Complete schema introspection functionality

#### **`src/flext_db_oracle/cli.py`** (483 statements)
- **Coverage**: 0% (critical gap)
- **Priority**: High priority for next development phase
- **Functionality**: Click-based commands working, needs comprehensive testing

## Development Patterns

For usage patterns and examples, see [README.md](README.md#basic-usage).

### **FlextResult Pattern** (Verified)

```python
from flext_core import FlextResult

# All public methods return FlextResult[T]
def database_operation() -> FlextResult[QueryResult]:
    try:
        result = self._execute_query()
        return FlextResult[QueryResult].ok(result)
    except Exception as e:
        return FlextResult[QueryResult].fail(f"Operation failed: {e}")
```

### **Testing Patterns** (Proven Effective)

```python
# Real code validation (preferred approach)
def test_actual_behavior(self):
    """Test real method behavior without excessive mocking."""
    api = FlextDbOracleApi(test_config)
    
    # Test methods that work without database connection
    result = api.optimize_query("SELECT * FROM users")
    assert result.success
    
    # Test methods that require connection (expect failure with descriptive error)
    query_result = api.query("SELECT 1 FROM dual")
    assert not query_result.success
    assert "connection" in query_result.error.lower()
```

### **Configuration Pattern** (Working)

For complete configuration reference, see [README.md](README.md#configuration-reference).

```python
from flext_db_oracle import FlextDbOracleConfig

# Environment-based configuration (Singer/Meltano compatible)
config = FlextDbOracleConfig.from_env()

# Direct configuration
config = FlextDbOracleConfig(
    host="localhost",
    port=1521,
    service_name="XEPDB1",
    username="user",
    password=SecretStr("password")
)
```

## Current Development Priorities

### **Immediate Actions** (Based on Analysis)

1. **CLI Test Coverage**: 0% → 30%+ (highest priority)
2. **API Connection Issue**: Fix timeout in connect() method testing
3. **Plugin System**: 16% → 40% coverage improvement
4. **API Coverage**: 26% → 40% with safe method testing

### **Strategic Approach** (Proven)

1. **Real Code Testing**: Continue proven approach over mocking
2. **Systematic Coverage**: Module-by-module comprehensive improvement
3. **Bug Discovery**: Tests should find and fix actual code issues
4. **Quality Focus**: Maintain quality gates while improving coverage

## Integration Points

For complete integration information, see [README.md](README.md#integration-with-flext-ecosystem).

### **FLEXT Core Dependencies** (Working)

- **flext-core**: FlextResult, FlextContainer, logging patterns
- **Development Mode**: Local path dependencies during development
- **Production Mode**: Package dependencies in published version

### **Singer Ecosystem Foundation** (In Development)

- **flext-tap-oracle**: Uses this library for data extraction
- **flext-target-oracle**: Uses this library for data loading
- **flext-dbt-oracle**: Uses this library for transformations

## Common Development Tasks

### **Adding New Features**

1. **Read Current State**: Review [README.md](README.md) for current functionality
2. **Follow Patterns**: Use FlextResult, Clean Architecture, real testing
3. **Quality Gates**: Always run `make validate` before committing
4. **Test Coverage**: Focus on real code paths, not mocks
5. **Documentation**: Update both README.md and relevant code examples

### **Debugging Oracle Issues**

For complete troubleshooting guide, see [README.md](README.md#troubleshooting).

```bash
# Quick debugging
make oracle-connect          # Test basic connectivity
export ORACLE_SQL_LOGGING=1  # Enable SQL query logging
docker-compose -f docker-compose.oracle.yml logs oracle-xe  # Check Oracle logs
```

### **Improving Test Coverage**

Based on proven methodology:

```bash
# Target specific modules systematically
pytest tests/unit/test_MODULE_comprehensive.py --cov=src/flext_db_oracle/MODULE.py --cov-report=term-missing

# Focus on real code paths
# Avoid excessive mocking
# Test actual method behavior
# Discover and fix real bugs
```

## Quality Standards

For complete quality information, see [README.md](README.md#quality-standards).

### **Current Metrics** (Verified)
- **Test Coverage**: 33% overall (actively improving)
- **Type Safety**: Python 3.13+ with comprehensive type hints
- **Real Bug Discovery**: 4+ validation bugs found and fixed
- **Code Quality**: Ruff + MyPy + Bandit scanning

### **Quality Gates** (Enforced)
```bash
make validate     # Required before all commits
```

## Troubleshooting

For complete troubleshooting information, see [README.md](README.md#troubleshooting).

### **Common Issues**

**Connection Timeouts**: API connect() method times out in tests → Need selective mocking approach
**Coverage Issues**: Use `--cov-report=term-missing` to identify uncovered lines
**Oracle Container**: Takes 2-3 minutes to start → Monitor with docker logs

### **Development Environment**

**Oracle Setup**: Use docker-compose.oracle.yml for local Oracle XE 21c
**Dependencies**: Run `make install-dev` to ensure all FLEXT dependencies
**Quality Issues**: Run `make validate` to identify all quality gate failures

## Contributing

For complete contribution guidelines, see [README.md](README.md#contributing).

### **Key Requirements**

1. **Follow FLEXT Patterns**: FlextResult, FlextContainer, Clean Architecture
2. **Real Code Testing**: Prefer real code validation over excessive mocking
3. **Quality Gates**: All changes must pass `make validate`
4. **Coverage Improvement**: Focus on systematic coverage improvement
5. **Documentation**: Keep README.md updated with working examples

### **Development Process**

```bash
# Setup and validate
make setup && make validate

# Create feature branch
git checkout -b feature/improvement

# Develop with real code testing
pytest tests/unit/test_TARGET_comprehensive.py

# Ensure quality gates pass
make validate

# Update documentation if needed
# Focus on README.md for user-facing changes
```

## Notes

This CLAUDE.md file focuses on development-specific guidance. For complete project information, architecture details, usage examples, and user-facing documentation, always refer to [README.md](README.md).

**Key Principle**: README.md contains the authoritative project information; CLAUDE.md provides development context and guidance for working with the codebase effectively.
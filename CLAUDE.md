# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**References**: See [../CLAUDE.md](../CLAUDE.md) for FLEXT ecosystem standards and [README.md](README.md) for project overview.

## Essential Development Commands

### Quality Gates (MANDATORY - Run Before Any Commit)
```bash
make validate          # Complete validation: lint + type + security + test (90% coverage requirement)
make check             # Quick validation: lint + type-check only
make test              # Run tests with 90% minimum coverage requirement
make fix               # Auto-fix linting and formatting issues
```

### Oracle Development Environment
```bash
# Start Oracle XE 21c container (takes 2-3 minutes to initialize)
docker-compose -f docker-compose.oracle.yml up -d

# Monitor Oracle startup (CRITICAL - container needs time to initialize)
docker-compose -f docker-compose.oracle.yml logs -f oracle-xe

# Test connectivity once ready (essential validation)
make oracle-connect

# Complete Oracle operations validation
make oracle-operations  # Validates config, connection, and schema access
```

### Testing Strategy Commands
```bash
# Unit tests (no Oracle dependency)
make test-unit           # Fast unit tests
pytest -m unit -v

# Integration tests (requires Oracle container)
make test-integration    # Full Oracle integration tests
ORACLE_INTEGRATION_TESTS=1 pytest tests/integration/ -v

# Specific module coverage analysis
pytest tests/unit/test_api_safe_comprehensive.py --cov=src/flext_db_oracle/api.py --cov-report=term-missing
pytest tests/unit/test_connection_comprehensive.py --cov=src/flext_db_oracle/connection.py --cov-report=term-missing
```

## Architecture and Code Structure

### Core Module Architecture
```
src/flext_db_oracle/
├── __init__.py         # Public API exports
├── api.py              # Main API class (720 statements) - 26% coverage
├── client.py           # CLI client integration (469 statements)  
├── models.py           # Pydantic models with Oracle validation
├── services.py         # SQL query building services
├── connection.py       # SQLAlchemy connection management (53% coverage)
├── metadata.py         # Oracle schema introspection (42% coverage)
├── exceptions.py       # Oracle-specific exceptions using flext-core patterns
├── constants.py        # Oracle constants and configuration
├── mixins.py           # Advanced validation patterns
├── utilities.py        # Utility functions
└── plugins.py          # Plugin system framework
```

### Key Architectural Patterns

#### FlextResult Pattern (MANDATORY)
All public APIs return `FlextResult[T]` for railway-oriented programming:
```python
from flext_core import FlextResult

def oracle_operation() -> FlextResult[QueryResult]:
    try:
        result = perform_operation()
        return FlextResult[QueryResult].ok(result)
    except Exception as e:
        return FlextResult[QueryResult].fail(f"Oracle operation failed: {e}")
```

#### Validation Using flext-core Patterns
Uses `FlextValidations.Advanced.CompositeValidator` for complex validation chains:
```python
from flext_core.validations import FlextValidations

validators = [
    lambda x: FlextValidations.Core.TypeValidators.validate_string(x),
    lambda x: FlextResult[str].ok(x.strip()) if x and x.strip() else FlextResult[str].fail("Cannot be empty"),
    lambda x: FlextResult[str].ok(x) if len(x) <= MAX_LENGTH else FlextResult[str].fail("Too long"),
]
composite = FlextValidations.Advanced.CompositeValidator(validators)
result = composite.validate(input_value)
```

### Critical Testing Approach (LEARNED FROM EXPERIENCE)

#### **NEVER Assume Code Structure Without Verification**
**Problem**: Tests often fail because they assume API structure without reading source code
**Examples**:
- Assumed `_plugins = []` → Actually `_plugins = {}`  
- Assumed methods exist (`validate_sql`, `analyze_query`) → They don't exist
- Assumed `__repr__` method exists → Uses default Python repr

**Solution**: ALWAYS use `grep`/`Read` tools to verify actual code structure BEFORE writing tests

#### **Real Code Testing > Mocking Everything**
**Proven Effective**: Found 4+ actual bugs through real code validation approach:
- `metadata.py` crash on None input → `.upper()` without validation
- Connection validation bugs discovered through comprehensive testing
- API plugin system structure discovered (dict-based, not list-based)

#### **API Method Categories** (Critical for Testing Strategy)
```python
# Methods that work WITHOUT database connection (safe for unit testing)
safe_methods = [
    'optimize_query', 'get_observability_metrics',
    'from_env', 'from_config', 'with_config', 'from_url',
    'list_plugins', 'get_plugin'  # (fail with descriptive errors when empty)
]

# Methods that REQUIRE database connection (timeout in tests without container)
connection_methods = [
    'connect', 'disconnect', 'test_connection',
    'query', 'query_one', 'execute', 'execute_many',
    'get_schemas', 'get_tables', 'get_columns'
]
```

## Current Development Status & Priorities

### **Test Coverage Status** (Updated Regularly)
- **Overall Coverage**: 33% (improved from 21%) - Target: 90%
- **Connection Module**: 53% (major improvement from 11%)
- **Metadata Module**: 42% (improved from 8%) 
- **API Module**: 26% (improved from 24%)
- **CLI Module**: 0% (CRITICAL GAP - highest priority)
- **Plugin System**: 16% (needs expansion to 40%+)

### **Immediate Development Priorities**

1. **CLI Test Coverage**: 0% → 30%+ (483 statements completely untested)
   - Use Click testing with `CliRunner`, avoid actual Oracle connections
   - Expected to find CLI-specific validation issues

2. **API Connection Testing Strategy**:
   - Problem: `connect()` method timeouts block many tests
   - Solution: Selective mocking for connection layer only, real validation everywhere else
   - Target: 26% → 40% coverage focusing on safe methods

3. **Plugin System Coverage**: 16% → 40%+
   - Current gap: Plugin validation, registration, lifecycle
   - Approach: Real plugin objects, test validation logic

## Oracle-Specific Configuration

### Environment Variables (Singer/Meltano Compatible)
```bash
# Required for integration tests
export ORACLE_INTEGRATION_TESTS=1
export FLEXT_TARGET_ORACLE_HOST="localhost"
export FLEXT_TARGET_ORACLE_PORT="1521"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="XEPDB1"
export FLEXT_TARGET_ORACLE_USERNAME="system"  
export FLEXT_TARGET_ORACLE_PASSWORD="Oracle123"

# Development debugging
export ORACLE_SQL_LOGGING=1                    # Enable SQL query logging
```

### Docker Configuration
- **Image**: `gvenzl/oracle-xe:21-slim` (Oracle XE 21c)
- **Container**: `flext-oracle-test` on port 1521
- **Initialization**: Takes 2-3 minutes for full startup
- **Health Check**: Uses sqlplus connectivity test
- **Setup Script**: Creates test schemas and users via `oracle-init/` directory

## Common Development Mistakes (Based on Real Experience)

### ❌ **Don't Do This**
- **Don't Assume**: API structure, method existence, return types without verification
- **Don't Mock Everything**: Loses real bug discovery opportunities
- **Don't Rush Implementation**: Leads to assumptions and expensive rework  
- **Don't Skip Oracle Container**: Tests require real Oracle for meaningful validation

### ✅ **Always Do This**
- **Always Verify**: Use `grep`, `Read` tools for actual code inspection
- **Selective Mocking**: Only for infrastructure (database connections), real validation everywhere else
- **Analysis First**: Understand code structure completely before implementing
- **Container Health**: Ensure Oracle container is healthy before running integration tests

## Troubleshooting

### Connection Issues
```bash
# Check Oracle container status
docker-compose -f docker-compose.oracle.yml ps
docker-compose -f docker-compose.oracle.yml logs oracle-xe | tail -20

# Test connectivity
make oracle-connect

# Enable debugging
export ORACLE_SQL_LOGGING=1
```

### Testing Issues
```bash
# Run only safe API tests (no connection timeouts)
pytest tests/unit/test_api_safe_comprehensive.py -v

# Integration tests (requires Oracle container)  
ORACLE_INTEGRATION_TESTS=1 pytest tests/integration/ -v

# Coverage analysis for specific modules
pytest tests/unit/test_MODULE_comprehensive.py --cov=src/flext_db_oracle/MODULE.py --cov-report=term-missing
```

### Development Issues
```bash
# Reset development environment completely
make clean-all && make setup

# Run comprehensive health check
make doctor

# Check project diagnostics
make diagnose
```

## Integration with FLEXT Ecosystem

### **flext-core Dependencies**
- **FlextResult**: All operations return `FlextResult[T]` for type-safe error handling
- **FlextValidations**: Uses `CompositeValidator` and validation chains
- **FlextContainer**: Dependency injection via `get_flext_container()`
- **FlextLogger**: Structured logging with `get_logger(__name__)`

### **Singer Ecosystem Foundation**  
This library serves as the foundation for:
- **flext-tap-oracle**: Oracle data extraction
- **flext-target-oracle**: Oracle data loading  
- **flext-dbt-oracle**: Oracle data transformation

### **CLI Integration**
- **Command**: `flext-db-oracle` (primary)
- **Aliases**: `flext-oracle`, `flext-oracle-migrate`
- **Integration**: Uses flext-cli patterns, NO direct click dependencies

## Contributing Requirements

### **Before Contributing**
```bash
# Verify Oracle environment
docker-compose -f docker-compose.oracle.yml up -d
make oracle-connect

# Run quality gates  
make validate

# Test coverage improvement
pytest --cov=src/flext_db_oracle --cov-report=term

# Check for Oracle integration tests
ORACLE_INTEGRATION_TESTS=1 pytest tests/integration/ --collect-only
```

### **Project-Specific Requirements**
1. **Real Oracle Testing**: Must use Oracle XE 21c container, avoid excessive mocking
2. **90% Coverage Requirement**: Minimum coverage enforced by quality gates
3. **Code Structure Analysis**: Always verify actual code before implementing tests
4. **flext-core Integration**: Use existing patterns from flext-core, avoid duplicating functionality
5. **CLI Priority**: 0% CLI coverage is critical gap requiring immediate attention

---

**Project Authority**: This CLAUDE.md covers flext-db-oracle specific development guidance.  
**Ecosystem Standards**: See [../CLAUDE.md](../CLAUDE.md) for FLEXT-wide standards.  
**User Documentation**: See [README.md](README.md) for complete project information.
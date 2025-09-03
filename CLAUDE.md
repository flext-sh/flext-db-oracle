# CLAUDE.md

This file provides development guidance specific to flext-db-oracle project.

**References**: See [../CLAUDE.md](../CLAUDE.md) for FLEXT ecosystem standards and [README.md](README.md) for project overview.

## Project-Specific Development Context

### **Current Project State** (Last Updated: 2025-01-23)

#### **Test Coverage Status**

- **Overall Coverage**: 33% (improved from 21%)
- **Connection Module**: 53% (major improvement from 11%)
- **Metadata Module**: 42% (improved from 8%)
- **API Module**: 26% (improved from 24%)
- **CLI Module**: 0% (critical gap, highest priority)
- **Plugin System**: 16% (needs expansion)

#### **Verified Working Functionality**

✅ **Production-Ready**:

- Oracle database connections with SQLAlchemy 2.x
- Schema introspection (tables, columns, metadata)
- Query execution with FlextResult patterns
- Connection pooling and resource management

🚧 **In Development**:

- CLI comprehensive testing (0% coverage)
- Plugin system expansion (16% → 40%+ target)
- API method coverage improvements

### **Critical Lessons from Recent Development**

#### **NEVER Assume Code Structure Without Verification**

**Problem**: Initial tests assumed API structure without reading source code
**Examples**:

- Assumed `_plugins = []` → Actually `_plugins = {}`
- Assumed methods exist (`validate_sql`, `analyze_query`) → They don't exist
- Assumed `__repr__` method exists → Uses default Python repr

**Solution**: ALWAYS use `grep`/`Read` to verify actual code structure BEFORE writing tests

#### **Real Code Testing > Mocking Everything**

**Proven**: Found 4+ actual bugs through real code validation approach
**Examples**:

- `metadata.py` crash on None input → `.upper()` without validation
- Connection validation bugs discovered through comprehensive testing
- API plugin system structure discovered (dict-based, not list-based)

**Critical**: This approach takes longer initially but finds real bugs that mocks hide

#### **Database Testing Complexity Underestimated**

**Reality**: Oracle connection methods (`connect()`) actually attempt database connection → timeout
**Problem**: Many API tests timeout due to real connection attempts
**Solution**: Selective mocking only where absolutely necessary (connection layer), real validation everywhere else

## Oracle-Specific Development

### **Oracle Development Environment**

```bash
# Start Oracle XE 21c (takes 2-3 minutes to initialize)
docker-compose -f docker-compose.oracle.yml up -d

# Monitor Oracle startup (critical - container takes time)
docker-compose -f docker-compose.oracle.yml logs -f oracle-xe

# Test connectivity once ready
make oracle-connect
```

### **Environment Configuration** (Singer/Meltano Compatible)

```bash
# Required for integration tests
export ORACLE_INTEGRATION_TESTS=1
export FLEXT_TARGET_ORACLE_HOST="localhost"
export FLEXT_TARGET_ORACLE_PORT="1521"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="XEPDB1"
export FLEXT_TARGET_ORACLE_USERNAME="system"
export FLEXT_TARGET_ORACLE_PASSWORD="Oracle123"
```

## Code Structure Reality (Verified Through Testing)

### **API Module Structure** (`src/flext_db_oracle/api.py` - 720 statements)

#### **Working Methods Without Database Connection**

- `optimize_query()` - Query optimization suggestions
- `get_observability_metrics()` - Observability data
- Class methods (`from_env()`, `from_config()`, `with_config()`, `from_url()`) - Return API instances directly
- Property access (`is_connected`, `connection`, `config`)

#### **Methods That Require Database Connection** (Timeout in Tests)

- `connect()` - Actually attempts Oracle connection
- `query()`, `query_one()`, `execute()` - All database operations
- `get_schemas()`, `get_tables()`, `get_columns()` - Schema operations
- `test_connection()` - Connection validation

#### **Plugin System Reality**

- **Storage**: `_plugins = {}` (dict), not list
- **Methods**: `register_plugin()`, `unregister_plugin()`, `list_plugins()`, `get_plugin()`
- **Behavior**: `list_plugins()` fails with "plugin listing returned empty" when no plugins

### **Connection Module** (`src/flext_db_oracle/connection.py` - 606 statements)

- **Coverage**: 53% (significantly improved through comprehensive testing)
- **Bugs Found**: Multiple validation issues discovered and fixed
- **Testing Status**: Comprehensive test suite implemented

### **Metadata Module** (`src/flext_db_oracle/metadata.py` - 158 statements)

- **Coverage**: 42% (major improvement)
- **Critical Bug Fixed**: Crash on None input validation (`None.upper()`)
- **Testing Status**: Systematic testing implemented

### **CLI Module** (`src/flext_db_oracle/cli.py` - 483 statements)

- **Coverage**: 0% (CRITICAL GAP - highest priority)
- **Functionality**: Click-based commands working in practice
- **Commands Available**: `connect`, `connect-env`, `query`, `schemas`, `tables`, `health`

## Project-Specific Testing Strategy

### **Proven Effective Patterns**

#### **Real Code Validation Approach**

```python
def test_real_api_behavior(self):
    """Test actual method behavior without excessive mocking."""
    config = FlextDbOracleConfig(host="test", port=1521, service_name="TEST",
                                 username="test", password=SecretStr("test"))
    api = FlextDbOracleApi(config)

    # Test methods that work without database connection
    result = api.optimize_query("SELECT * FROM users")
    assert result.success

    # Test methods that require connection (expect failure with descriptive error)
    query_result = api.query("SELECT 1 FROM dual")
    assert not query_result.success
    assert "connection" in query_result.error.lower()
```

#### **Systematic Module Coverage**

```bash
# Target specific modules with comprehensive tests
pytest tests/unit/test_connection_comprehensive.py --cov=src/flext_db_oracle/connection.py --cov-report=term-missing
pytest tests/unit/test_metadata_comprehensive.py --cov=src/flext_db_oracle/metadata.py --cov-report=term-missing
pytest tests/unit/test_api_safe_comprehensive.py --cov=src/flext_db_oracle/api.py --cov-report=term-missing
```

#### **Safe API Testing Pattern**

```python
# Methods that work without database connection (safe for testing)
safe_methods = [
    'optimize_query', 'get_observability_metrics',
    'from_env', 'from_config', 'with_config', 'from_url',
    'list_plugins', 'get_plugin'  # (fail with descriptive errors when empty)
]

# Methods that timeout (need selective mocking or integration tests)
connection_methods = [
    'connect', 'disconnect', 'test_connection',
    'query', 'query_one', 'execute', 'execute_many',
    'get_schemas', 'get_tables', 'get_columns'
]
```

## Development Priorities (Based on Analysis)

### **Immediate Actions** (Highest ROI)

1. **CLI Test Coverage**: 0% → 30%+

   - **Why Critical**: 483 statements completely untested
   - **Approach**: Click testing with `CliRunner`, avoid actual Oracle connections
   - **Expected Bugs**: Likely to find CLI-specific validation issues

2. **API Connection Testing Strategy**:

   - **Problem**: `connect()` method timeouts block many tests
   - **Solution**: Selective mocking for connection layer only
   - **Target**: 26% → 40% coverage focusing on safe methods

3. **Plugin System Coverage**: 16% → 40%+
   - **Current Gap**: Plugin validation, registration, lifecycle
   - **Approach**: Real plugin objects, test validation logic

### **Strategic Development Approach** (Lessons Applied)

1. **Code Structure Analysis FIRST**: Always `grep`/`Read` before implementing
2. **Real Code Validation**: Continue proven approach, avoid excessive mocking
3. **Systematic Module Targeting**: Focus on one module at a time for comprehensive coverage
4. **Bug Discovery Focus**: Tests should find actual issues, not just increase coverage numbers

## Oracle-Specific Troubleshooting

### **Connection Issues**

```bash
# Test Oracle container readiness
docker-compose -f docker-compose.oracle.yml ps
docker-compose -f docker-compose.oracle.yml logs oracle-xe | tail -20

# Test basic connectivity
make oracle-connect

# Enable SQL debugging
export ORACLE_SQL_LOGGING=1
```

### **Testing Issues**

```bash
# Coverage analysis for specific modules
pytest tests/unit/test_MODULE_comprehensive.py --cov=src/flext_db_oracle/MODULE.py --cov-report=term-missing

# Run only safe API tests (no connection timeouts)
pytest tests/unit/test_api_safe_comprehensive.py -v

# Integration tests (requires Oracle)
ORACLE_INTEGRATION_TESTS=1 pytest tests/integration/ -v
```

### **Common Development Mistakes** (Based on Experience)

❌ **Don't Assume**: API structure, method existence, return types
✅ **Always Verify**: Use `grep`, `Read`, actual code inspection

❌ **Don't Mock Everything**: Loses real bug discovery
✅ **Selective Mocking**: Only for infrastructure (database connections)

❌ **Don't Rush Implementation**: Leads to assumptions and rework
✅ **Analysis First**: Understand code structure before testing

## Integration with FLEXT Ecosystem

For FLEXT ecosystem standards, see [../CLAUDE.md](../CLAUDE.md).

### **Project-Specific Integration Points**

#### **flext-core Dependency**

```python
from flext_core import FlextResult, FlextContainer, get_logger

# All public APIs return FlextResult[T]
def oracle_operation() -> FlextResult[QueryResult]:
    try:
        result = perform_operation()
        return FlextResult[QueryResult].ok(result)
    except Exception as e:
        return FlextResult[QueryResult].fail(f"Oracle operation failed: {e}")
```

#### **Singer Ecosystem Foundation**

- **flext-tap-oracle**: Uses this library for Oracle data extraction
- **flext-target-oracle**: Uses this library for Oracle data loading
- **flext-dbt-oracle**: Uses this library for Oracle transformations

## Contributing to This Project

For general FLEXT contribution standards, see [../CLAUDE.md](../CLAUDE.md).

### **Project-Specific Requirements**

1. **Oracle Environment**: Must test with real Oracle XE 21c container
2. **Real Code Testing**: Focus on discovering actual bugs, not just coverage
3. **Systematic Approach**: Target modules individually for comprehensive coverage
4. **CLI Priority**: 0% coverage is critical gap that needs immediate attention
5. **Connection Testing**: Understand timeout behavior, use selective mocking appropriately

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

---

**Project Authority**: This CLAUDE.md covers flext-db-oracle specific development guidance.  
**Ecosystem Standards**: See [../CLAUDE.md](../CLAUDE.md) for FLEXT-wide standards.  
**User Documentation**: See [README.md](README.md) for complete project information.

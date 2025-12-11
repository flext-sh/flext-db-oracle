# Integration Tests

This directory contains integration tests for FLEXT DB Oracle that require actual Oracle database connectivity. These tests validate component interactions, database operations, and real-world scenarios with live Oracle instances.

## 🎯 Integration Test Principles

### **Real System Integration**

- **Actual Oracle database** connection required
- **Real network communication** and protocol testing
- **Database schema validation** with actual Oracle metadata
- **Connection pooling** behavior under load
- **Transaction management** with real database commits/rollbacks

### **Test Scope**

- **Component interaction** between modules
- **Database operation validation** with real SQL
- **Performance characteristics** under realistic conditions
- **Error handling** with actual Oracle error codes
- **Schema evolution** and migration scenarios

## 📁 Test Organization

### **Core Integration Tests**

- `test_oracle_integration.py` - Comprehensive Oracle database integration scenarios

### **Test Categories**

#### **Connection Integration**

- Database connection establishment and validation
- Connection pool behavior with multiple concurrent connections
- SSL/TLS connection security validation
- Connection timeout and retry behavior
- Authentication and authorization scenarios

#### **Query Integration**

- SQL query execution with real Oracle database
- Parameterized query handling and injection prevention
- Transaction management and rollback scenarios
- Batch operation performance with large datasets
- Complex query optimization and execution plan analysis

#### **Schema Integration**

- Schema introspection with real Oracle metadata views
- DDL generation and execution validation
- Table creation, modification, and deletion
- Index creation and performance impact measurement
- Constraint validation and foreign key relationships

#### **Plugin Integration**

- Plugin execution with real database operations
- Performance monitoring with actual query timing
- Security audit with real SQL injection scenarios
- Data validation with actual business rule enforcement

## 🚀 Running Integration Tests

### **Prerequisites**

#### **Oracle Database Setup**

```bash
# Start Oracle XE via Docker
docker-compose -f docker-compose.oracle.yml up -d

# Wait for Oracle to be ready
docker-compose -f docker-compose.oracle.yml logs -f oracle-xe

# Verify Oracle is accessible
sqlplus sys/oracle@localhost:1521/XE as sysdba
```

#### **Environment Configuration**

```bash
# Required environment variables
export ORACLE_INTEGRATION_TESTS=1
export FLEXT_TARGET_ORACLE_HOST=localhost
export FLEXT_TARGET_ORACLE_PORT=1521
export FLEXT_TARGET_ORACLE_SERVICE_NAME=XEPDB1
export FLEXT_TARGET_ORACLE_USERNAME=test_user
export FLEXT_TARGET_ORACLE_PASSWORD=test_password
```

### **Test Execution**

```bash
# Run all integration tests
pytest tests/integration/

# Run with Oracle database requirement check
pytest tests/integration/ -m integration

# Run with detailed output
pytest tests/integration/ -v -s

# Run with performance timing
pytest tests/integration/ --durations=10

# Generate coverage report
pytest tests/integration/ --cov=src/flext_db_oracle --cov-report=html
```

### **Test Data Management**

Integration tests use dedicated test schemas and tables:

```sql
-- Test schema setup
CREATE USER flext_test IDENTIFIED BY test_password;
GRANT CONNECT, RESOURCE TO flext_test;
GRANT CREATE TABLE, CREATE VIEW, CREATE SEQUENCE TO flext_test;

-- Test tables for integration scenarios
CREATE TABLE flext_test.employees (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100) NOT NULL,
    email VARCHAR2(150) UNIQUE,
    department_id NUMBER,
    salary NUMBER(10,2),
    hire_date DATE DEFAULT SYSDATE
);

CREATE TABLE flext_test.departments (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100) NOT NULL,
    manager_id NUMBER
);
```

## 🧪 Test Examples

### **Database Connection Testing**

```python
@pytest.mark.integration
def test_oracle_connection_with_real_database():
    """Test Oracle connection with actual database instance."""
    # Arrange
    config = FlextDbOracleSettings.from_env().value
    connection = FlextDbOracleConnection(config)

    # Act
    result = connection.connect()

    # Assert
    assert result.success
    assert connection.is_connected()

    # Cleanup
    connection.disconnect()
```

### **Query Execution Testing**

```python
@pytest.mark.integration
def test_query_execution_with_real_oracle():
    """Test SQL query execution with actual Oracle database."""
    # Arrange
    api = FlextDbOracleApi.from_env()
    test_sql = "SELECT COUNT(*) as employee_count FROM employees"

    # Act
    with api:
        result = api.execute_query(test_sql)

    # Assert
    assert result.success
    assert result.value.row_count >= 0
    assert len(result.value.columns) == 1
    assert result.value.columns[0] == "employee_count"
```

### **Schema Integration Testing**

```python
@pytest.mark.integration
def test_schema_metadata_extraction():
    """Test Oracle schema metadata extraction with real database."""
    # Arrange
    api = FlextDbOracleApi.from_env()
    metadata_manager = FlextDbOracleMetadataManager(api.connection)

    # Act
    with api:
        result = metadata_manager.get_schema_metadata("FLEXT_TEST")

    # Assert
    assert result.success
    schema = result.value
    assert schema.name == "FLEXT_TEST"
    assert len(schema.tables) >= 0

    # Validate table metadata
    if schema.tables:
        table = schema.tables[0]
        assert table.name
        assert table.schema_name == "FLEXT_TEST"
        assert len(table.columns) > 0
```

## 📊 Performance Benchmarking

Integration tests include performance benchmarks for critical operations:

```python
@pytest.mark.integration
@pytest.mark.benchmark
def test_connection_pool_performance():
    """Benchmark connection pool performance under load."""
    # Test concurrent connections
    # Measure connection acquisition time
    # Validate pool sizing behavior
    # Assert performance thresholds
```

## 🔧 Test Environment Management

### **Test Database Schema**

Integration tests use isolated test schemas to avoid conflicts:

- **Schema isolation**: Each test run uses dedicated schemas
- **Data cleanup**: Automatic cleanup after test completion
- **Parallel execution**: Tests can run concurrently with proper isolation

### **Docker Integration**

```bash
# Complete test environment setup
make test-integration-setup     # Start Oracle XE and configure schemas
make test-integration          # Run integration tests
make test-integration-cleanup  # Stop Oracle and cleanup resources
```

### **Continuous Integration**

Integration tests are configured for CI/CD environments:

- **Oracle XE container** for automated testing
- **Schema migration** validation
- **Performance regression** detection
- **Resource cleanup** after test completion

These integration tests ensure FLEXT DB Oracle works correctly with real Oracle databases while maintaining performance and reliability standards in production environments.

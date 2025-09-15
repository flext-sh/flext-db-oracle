# End-to-End Tests

This directory contains end-to-end (E2E) tests for FLEXT DB Oracle that validate complete user workflows and system integration scenarios. These tests use real systems without mocks to ensure the entire application works correctly in production-like environments.

## 🎯 End-to-End Test Principles

### **Complete System Integration**

- **No mocks or stubs** - tests use real components
- **Full workflow validation** from CLI commands to database results
- **Production-like environment** testing with real Oracle databases
- **User journey scenarios** that mirror actual usage patterns
- **Cross-component interaction** validation

### **Test Scope**

- **CLI-to-database workflows** with complete data flow
- **Plugin system integration** with real Oracle operations
- **Configuration and environment** variable integration
- **Error handling and recovery** in realistic failure scenarios
- **Performance characteristics** under production-like loads

## 📁 Test Organization

### **Core E2E Tests**

- `test_oracle_e2e.py` - Complete Oracle database workflow scenarios

### **Test Categories**

#### **CLI Workflow Tests**

- Complete CLI command sequences with real database operations
- Configuration loading from environment variables
- Multi-step operations with state preservation
- Error recovery and user feedback scenarios

#### **API Integration Tests**

- Full API workflows with database operations
- Plugin system integration with real data processing
- Observability and monitoring integration
- Configuration management across multiple environments

#### **Data Pipeline Tests**

- Complete data extraction, transformation, and loading workflows
- Schema evolution and migration scenarios
- Bulk data operations and performance validation
- Error handling and data consistency verification

## 🚀 Running End-to-End Tests

### **Prerequisites**

#### **Complete Oracle Environment**

```bash
# Start full Oracle environment
docker-compose -f docker-compose.oracle-full.yml up -d

# Verify all services are running
docker-compose ps

# Check Oracle database health
docker-compose exec oracle-xe sqlplus sys/oracle@XEPDB1 as sysdba
```

#### **Environment Configuration**

```bash
# Production-like environment variables
export FLEXT_TARGET_ORACLE_HOST=localhost
export FLEXT_TARGET_ORACLE_PORT=1521
export FLEXT_TARGET_ORACLE_SERVICE_NAME=XEPDB1
export FLEXT_TARGET_ORACLE_USERNAME=flext_user
export FLEXT_TARGET_ORACLE_PASSWORD=flext_password

# Enable full integration testing
export ORACLE_E2E_TESTS=1
export FLEXT_OBSERVABILITY_ENABLED=1
export FLEXT_PLUGINS_ENABLED=1
```

### **Test Execution**

```bash
# Run all E2E tests
pytest tests/e2e/

# Run with full output and timing
pytest tests/e2e/ -v -s --durations=0

# Run specific E2E scenarios
pytest tests/e2e/test_oracle_e2e.py::test_complete_cli_workflow

# Run with performance profiling
pytest tests/e2e/ --profile-svg
```

### **Test Data Setup**

E2E tests use realistic test data that mirrors production scenarios:

```sql
-- Create comprehensive test schema
CREATE USER flext_e2e IDENTIFIED BY e2e_password;
GRANT CONNECT, RESOURCE, DBA TO flext_e2e;

-- Create realistic business tables
CREATE TABLE flext_e2e.customers (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100) NOT NULL,
    email VARCHAR2(150) UNIQUE,
    phone VARCHAR2(20),
    address CLOB,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP,
    status VARCHAR2(20) DEFAULT 'ACTIVE'
);

CREATE TABLE flext_e2e.orders (
    id NUMBER PRIMARY KEY,
    customer_id NUMBER REFERENCES flext_e2e.customers(id),
    order_date DATE DEFAULT SYSDATE,
    total_amount NUMBER(10,2),
    status VARCHAR2(20) DEFAULT 'PENDING',
    shipping_address CLOB,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert realistic test data
INSERT INTO flext_e2e.customers (id, name, email, phone, address)
SELECT level,
       'Customer ' || level,
       'customer' || level || '@example.com',
       '+1-555-' || LPAD(level, 4, '0'),
       level || ' Main Street, Anytown, ST 12345'
FROM dual
CONNECT BY level <= 1000;

-- Commit test data
COMMIT;
```

## 🧪 Test Examples

### **Complete CLI Workflow Test**

```python
@pytest.mark.e2e
def test_complete_cli_workflow():
    """Test complete CLI workflow from connection to query execution."""
    runner = CliRunner()

    # Step 1: Test database connection
    connection_result = runner.invoke(oracle_cli, [
        'connect-env'
    ])
    assert connection_result.exit_code == 0
    assert "Connection Successful" in connection_result.output

    # Step 2: Execute data query
    query_result = runner.invoke(oracle_cli, [
        'query',
        '--sql', 'SELECT COUNT(*) as customer_count FROM customers'
    ])
    assert query_result.exit_code == 0
    assert "customer_count" in query_result.output

    # Step 3: List schemas and tables
    schema_result = runner.invoke(oracle_cli, ['schemas'])
    assert schema_result.exit_code == 0

    table_result = runner.invoke(oracle_cli, [
        'tables', '--schema', 'FLEXT_E2E'
    ])
    assert table_result.exit_code == 0
    assert "customers" in table_result.output
    assert "orders" in table_result.output
```

### **API Integration Workflow Test**

```python
@pytest.mark.e2e
def test_api_integration_workflow():
    """Test complete API workflow with real Oracle operations."""
    # Initialize API with real configuration
    api = FlextDbOracleApi.from_env()

    # Test connection and basic operations
    with api:
        # Verify connection
        assert api.is_connected()

        # Test schema operations
        schemas_result = api.get_schemas()
        assert schemas_result.success
        assert "FLEXT_E2E" in schemas_result.value

        # Test table operations
        tables_result = api.get_tables("FLEXT_E2E")
        assert tables_result.success
        assert len(tables_result.value) >= 2

        # Test data query
        query_result = api.execute_query(
            "SELECT c.name, COUNT(o.id) as order_count "
            "FROM customers c LEFT JOIN orders o ON c.id = o.customer_id "
            "GROUP BY c.name ORDER BY order_count DESC"
        )
        assert query_result.success
        assert query_result.value.row_count > 0

        # Test plugin operations
        plugin_result = api.execute_with_plugins("performance_monitor", {
            "sql": "SELECT * FROM customers WHERE status = 'ACTIVE'",
            "threshold_ms": 1000
        })
        assert plugin_result.success
```

### **Data Pipeline Workflow Test**

```python
@pytest.mark.e2e
def test_data_pipeline_workflow():
    """Test complete data pipeline workflow."""
    api = FlextDbOracleApi.from_env()

    with api:
        # Step 1: Extract schema metadata
        metadata_manager = FlextDbOracleMetadataManager(api.connection)
        schema_result = metadata_manager.get_schema_metadata("FLEXT_E2E")
        assert schema_result.success

        schema = schema_result.value
        assert len(schema.tables) >= 2

        # Step 2: Generate and execute DDL
        customers_table = schema.get_table("CUSTOMERS")
        assert customers_table is not None

        # Step 3: Perform bulk operations
        bulk_data = [
            ("Test Customer 1", "test1@example.com", "+1-555-0001"),
            ("Test Customer 2", "test2@example.com", "+1-555-0002"),
            ("Test Customer 3", "test3@example.com", "+1-555-0003")
        ]

        bulk_result = api.bulk_insert(
            schema="FLEXT_E2E",
            table="customers",
            columns=["name", "email", "phone"],
            values=bulk_data
        )
        assert bulk_result.success
        assert bulk_result.value == len(bulk_data)

        # Step 4: Verify data integrity
        verify_result = api.execute_query(
            "SELECT COUNT(*) FROM customers WHERE name LIKE 'Test Customer%'"
        )
        assert verify_result.success:
        assert verify_result.value.rows[0][0] == len(bulk_data)
```

## 📊 Performance and Load Testing

E2E tests include performance validation for production readiness:

```python
@pytest.mark.e2e
@pytest.mark.performance
def test_high_volume_operations():
    """Test system performance under high-volume operations."""
    api = FlextDbOracleApi.from_env()

    with api:
        # Test concurrent connections - WARNING: This is example code only!
        # In production, use SQLAlchemy 2.0 Core API instead of string concatenation
        concurrent_queries = []
        for i in range(10):
            query = f"SELECT * FROM customers WHERE id BETWEEN {i*100} AND {(i+1)*100}"
            concurrent_queries.append(query)

        # Execute queries concurrently and measure performance
        start_time = time.time()
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_query = {
                executor.submit(api.execute_query, query): query
                for query in concurrent_queries
            }

            for future in concurrent.futures.as_completed(future_to_query):
                result = future.result()
                assert result.success
                results.append(result)

        execution_time = time.time() - start_time

        # Performance assertions
        assert execution_time < 30.0  # Should complete within 30 seconds
        assert len(results) == len(concurrent_queries)
        assert all(r.success for r in results)
```

## 🔧 Test Environment Management

### **Docker Compose Setup**

```yaml
# docker-compose.e2e.yml
version: "3.8"
services:
  oracle-xe:
    image: gvenzl/oracle-xe:21-slim
    environment:
      - ORACLE_PASSWORD=oracle
      - APP_USER=flext_e2e
      - APP_USER_PASSWORD=e2e_password
    ports:
      - "1521:1521"
    volumes:
      - ./tests/e2e/init-scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD", "healthcheck.sh"]
      interval: 30s
      timeout: 10s
      retries: 5

  flext-app:
    build: .
    depends_on:
      oracle-xe:
        condition: service_healthy
    environment:
      - FLEXT_TARGET_ORACLE_HOST=oracle-xe
      - FLEXT_TARGET_ORACLE_USERNAME=flext_e2e
      - ORACLE_E2E_TESTS=1
    command: ["pytest", "tests/e2e/", "-v"]
```

### **Test Data Management**

E2E tests include automatic test data setup and cleanup:

```bash
# Setup E2E test environment
make e2e-setup                    # Initialize test database and data
make e2e-test                     # Run E2E tests
make e2e-cleanup                  # Clean up test data and containers

# Full E2E test cycle
make e2e-full                     # Complete setup, test, and cleanup cycle
```

### **Continuous Integration**

E2E tests are configured for CI/CD with:

- **Realistic test data** generation and management
- **Performance benchmarking** and regression detection
- **Test result reporting** with detailed logs
- **Environment cleanup** after test completion

These end-to-end tests ensure FLEXT DB Oracle works correctly in real-world scenarios while maintaining performance and reliability standards expected in production environments.

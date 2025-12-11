# Unit Tests

This directory contains fast, isolated unit tests for FLEXT DB Oracle components. Unit tests use mocks and stubs to eliminate external dependencies, ensuring fast execution and reliable testing of business logic.

## 🎯 Unit Test Principles

### **Isolation and Speed**

- **No external dependencies** (database, network, filesystem)
- **Fast execution** (< 1 second per test)
- **Deterministic results** independent of environment
- **Mock-based isolation** of external systems

### **Coverage Focus**

- **Business logic validation** and domain rules
- **Error handling** and edge case scenarios
- **Input validation** and data transformation
- **Configuration parsing** and validation
- **Type conversion** and mapping logic

## 📁 Test Organization

### **Core API Tests**

- `test_api.py` - Basic API functionality with mocked dependencies
- `test_api_comprehensive.py` - Complete API surface coverage
- `test_api_missing_coverage.py` - Edge cases and error scenarios
- `test_api_real_execution.py` - API behavior with realistic mocked data

### **Configuration Tests**

- `test_config.py` - Configuration loading, validation, and environment variable handling

### **Connection Tests**

- `test_connection.py` - Connection management with mocked database
- `test_connection_comprehensive.py` - Connection pooling and lifecycle
- `test_connection_focused.py` - Specific connection scenarios
- `test_connection_targeted.py` - Connection error handling and recovery

### **Domain Tests**

- `test_metadata.py` - Schema metadata parsing and validation
- `test_types.py` - Domain value objects and business rule validation

### **Infrastructure Tests**

- `test_cli_simple.py` - Basic CLI command functionality
- `test_cli_comprehensive.py` - CLI command coverage with mocked APIs
- `test_cli_targeted.py` - CLI error handling and user interaction

### **Plugin Tests**

- `test_plugins_comprehensive.py` - Plugin system with mocked execution
- `test_observability_comprehensive.py` - Observability components with mocked metrics

## 🚀 Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run specific test modules
pytest tests/unit/test_api.py
pytest tests/unit/test_config.py

# Run with coverage
pytest tests/unit/ --cov=src/flext_db_oracle --cov-report=term

# Fast feedback during development
pytest tests/unit/ -x --tb=short
```

## 🧪 Test Examples

### **Mock-Based Testing**

```python
@patch('flext_db_oracle.connection.create_engine')
def test_connection_with_mocked_engine(mock_create_engine):
    """Test connection creation with mocked SQLAlchemy engine."""
    # Arrange
    mock_engine = Mock()
    mock_create_engine.return_value = mock_engine

    # Act
    connection = FlextDbOracleConnection(config)
    result = connection.connect()

    # Assert
    assert result.success
    mock_create_engine.assert_called_once()
```

### **Domain Logic Testing**

```python
def test_config_validation_with_invalid_host():
    """Test configuration validation fails with empty host."""
    # Arrange
    config = FlextDbOracleSettings(
        host="",  # Invalid empty host
        port=1521,
        username="test_user",
        password=SecretStr("test_pass"),
        service_name="TEST"
    )

    # Act
    result = config.validate_domain_rules()

    # Assert
    assert result.is_failure
    assert "Host cannot be empty" in result.error
```

These unit tests provide the foundation for reliable, fast feedback during development while ensuring comprehensive coverage of business logic and edge cases.

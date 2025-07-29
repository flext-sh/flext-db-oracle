"""Test configuration for flext-db-oracle enterprise test suite."""

import pytest
from unittest.mock import MagicMock

from src.flext_db_oracle import FlextDbOracleConfig, FlextDbOracleApi


@pytest.fixture
def valid_config():
    """Valid Oracle configuration for testing."""
    return FlextDbOracleConfig(
        host="localhost",
        port=1521,
        username="testuser",
        password="testpass",
        service_name="ORCLCDB",
        pool_min=1,
        pool_max=10,
        timeout=30
    )


@pytest.fixture
def invalid_config():
    """Invalid Oracle configuration for error testing."""
    return FlextDbOracleConfig(
        host="",
        port=0,
        username="",
        password="",
        service_name=None,
        sid=None
    )


@pytest.fixture
def mock_connection():
    """Mock Oracle connection for unit tests."""
    mock_conn = MagicMock()
    mock_conn.connect.return_value.is_success = True
    mock_conn.execute.return_value.is_success = True
    mock_conn.execute.return_value.data = [("test_result",)]
    mock_conn.test_connection.return_value.is_success = True
    return mock_conn


@pytest.fixture
def api_with_valid_config(valid_config):
    """FlextDbOracleApi instance with valid configuration."""
    return FlextDbOracleApi(valid_config)


@pytest.fixture
def api_with_invalid_config(invalid_config):
    """FlextDbOracleApi instance with invalid configuration."""
    return FlextDbOracleApi(invalid_config)


@pytest.fixture
def sample_table_metadata():
    """Sample table metadata for testing."""
    return {
        "name": "EMPLOYEES",
        "schema_name": "HR", 
        "columns": [
            {
                "column_name": "EMPLOYEE_ID",
                "data_type": "NUMBER",
                "nullable": False,
                "data_length": None,
                "data_precision": 6,
                "data_scale": 0,
                "column_id": 1
            },
            {
                "column_name": "FIRST_NAME", 
                "data_type": "VARCHAR2",
                "nullable": True,
                "data_length": 20,
                "data_precision": None,
                "data_scale": None,
                "column_id": 2
            }
        ]
    }


@pytest.fixture
def sample_query_result():
    """Sample query result for testing."""
    return [
        (1, "John", "Doe", "john.doe@company.com"),
        (2, "Jane", "Smith", "jane.smith@company.com"),
    ]


@pytest.fixture
def test_environment_variables(monkeypatch):
    """Set test environment variables."""
    test_env = {
        "FLEXT_TARGET_ORACLE_HOST": "test.oracle.com",
        "FLEXT_TARGET_ORACLE_PORT": "1521",
        "FLEXT_TARGET_ORACLE_USERNAME": "testuser",
        "FLEXT_TARGET_ORACLE_PASSWORD": "testpass",
        "FLEXT_TARGET_ORACLE_SERVICE_NAME": "ORCLCDB"
    }
    
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    
    return test_env
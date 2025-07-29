"""Test configuration for flext-db-oracle enterprise test suite."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig


@pytest.fixture
def valid_config() -> FlextDbOracleConfig:
    """Return valid Oracle configuration for testing."""
    return FlextDbOracleConfig(
        host="localhost",
        port=1521,
        username="testuser",
        password="testpass",
        service_name="ORCLCDB",
        pool_min=1,
        pool_max=10,
        timeout=30,
    )


@pytest.fixture
def invalid_config() -> FlextDbOracleConfig:
    """Return Oracle configuration that will fail on connection."""
    # Create a config that passes all validation but uses invalid host for connection failure
    return FlextDbOracleConfig(
        host="invalid.nonexistent.host.example",
        port=1521,
        username="invalid_user",
        password="invalid_password",
        service_name="INVALID_SERVICE",
    )


@pytest.fixture
def mock_connection() -> MagicMock:
    """Return mock Oracle connection for unit tests."""
    mock_conn = MagicMock()
    mock_conn.connect.return_value.is_success = True
    mock_conn.execute.return_value.is_success = True
    mock_conn.execute.return_value.data = [("test_result",)]
    mock_conn.test_connection.return_value.is_success = True
    return mock_conn


@pytest.fixture
def api_with_valid_config(valid_config: FlextDbOracleConfig) -> FlextDbOracleApi:
    """Return FlextDbOracleApi instance with valid configuration."""
    return FlextDbOracleApi(valid_config)


@pytest.fixture
def api_with_invalid_config(invalid_config: FlextDbOracleConfig) -> FlextDbOracleApi:
    """Return FlextDbOracleApi instance with invalid configuration."""
    return FlextDbOracleApi(invalid_config)


@pytest.fixture
def sample_table_metadata() -> dict[str, object]:
    """Return sample table metadata for testing."""
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
                "column_id": 1,
            },
            {
                "column_name": "FIRST_NAME",
                "data_type": "VARCHAR2",
                "nullable": True,
                "data_length": 20,
                "data_precision": None,
                "data_scale": None,
                "column_id": 2,
            },
        ],
    }


@pytest.fixture
def sample_query_result() -> list[tuple[int | str, ...]]:
    """Return sample query result for testing."""
    return [
        (1, "John", "Doe", "john.doe@company.com"),
        (2, "Jane", "Smith", "jane.smith@company.com"),
    ]


@pytest.fixture
def test_environment_variables(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Set test environment variables and return them."""
    test_env = {
        "FLEXT_TARGET_ORACLE_HOST": "test.oracle.com",
        "FLEXT_TARGET_ORACLE_PORT": "1521",
        "FLEXT_TARGET_ORACLE_USERNAME": "testuser",
        "FLEXT_TARGET_ORACLE_PASSWORD": "testpass",
        "FLEXT_TARGET_ORACLE_SERVICE_NAME": "ORCLCDB",
    }

    for key, value in test_env.items():
        monkeypatch.setenv(key, value)

    return test_env

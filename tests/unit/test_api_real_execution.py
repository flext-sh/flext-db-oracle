"""Unit tests for FlextDbOracleApi - Real code execution for coverage.

Tests that actually execute the source code to improve coverage while
maintaining test isolation through controlled inputs and mocking only
external dependencies.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from flext_core import FlextResult

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
)

if TYPE_CHECKING:
    from unittest.mock import Mock


class TestFlextDbOracleApiRealExecution:
    """Tests that execute real API code for coverage improvement."""

    def test_initialization_real_execution(self) -> None:
        """Test API initialization with real code execution."""
        # Test with no config
        api = FlextDbOracleApi()
        assert api._config is None
        assert api._context_name == "oracle"
        assert not api._is_connected
        assert api._connection is None
        assert api._retry_attempts == 3

        # Test with config
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api_with_config = FlextDbOracleApi(config, "test_context")
        assert api_with_config._config == config
        assert api_with_config._context_name == "test_context"
        assert not api_with_config._is_connected

    def test_properties_real_execution(self) -> None:
        """Test property accessors with real code execution."""
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config)

        # Test properties
        assert api.config == config
        assert api.connection is None
        assert not api.is_connected

    @patch.dict(
        "os.environ",
        {
            "FLEXT_TARGET_ORACLE_HOST": "env.oracle.com",
            "FLEXT_TARGET_ORACLE_PORT": "1522",
            "FLEXT_TARGET_ORACLE_USERNAME": "envuser",
            "FLEXT_TARGET_ORACLE_PASSWORD": "envpass",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "ENVDB",
        },
    )
    def test_from_env_real_execution(self) -> None:
        """Test API creation from environment with real code execution."""
        api = FlextDbOracleApi.from_env()

        assert api._config is not None
        assert api._config.host == "env.oracle.com"
        assert api._config.port == 1522
        assert api._config.username == "envuser"
        assert api._config.service_name == "ENVDB"

    def test_from_env_missing_variables(self) -> None:
        """Test from_env behavior when environment variables are missing."""
        # Clear relevant environment variables

        with patch.dict(os.environ, {}, clear=True):
            # This should fail appropriately due to missing configuration
            with pytest.raises(ValueError, match="Configuration loading failed"):
                FlextDbOracleApi.from_env()

    def test_with_config_real_execution(self) -> None:
        """Test API creation with configuration parameters - real execution."""
        api = FlextDbOracleApi.with_config(
            host="param.oracle.com",
            port=1523,
            username="paramuser",
            password="parampass",
            service_name="PARAMDB",
        )

        assert api._config is not None
        assert api._config.host == "param.oracle.com"
        assert api._config.port == 1523
        assert api._config.username == "paramuser"
        assert api._config.service_name == "PARAMDB"

    def test_connect_without_config_real_execution(self) -> None:
        """Test connection attempt without configuration - real execution."""
        api = FlextDbOracleApi()

        with pytest.raises(ValueError, match="No configuration provided"):
            api.connect()

    def test_disconnect_when_not_connected_real_execution(self) -> None:
        """Test disconnect when not connected - real execution."""
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config)
        result = api.disconnect()

        # Should return self for chaining
        assert result == api
        assert not api.is_connected

    def test_query_not_connected_real_execution(self) -> None:
        """Test query when not connected - real execution."""
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config)
        result = api.query("SELECT 1 FROM DUAL")

        assert result.is_failure
        assert result.error is not None
        assert (
            "Database not connected" in result.error
            or "No database connection" in result.error
        )

    def test_query_one_not_connected_real_execution(self) -> None:
        """Test query_one when not connected - real execution."""
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config)
        result = api.query_one("SELECT COUNT(*) FROM DUAL")

        assert result.is_failure
        assert result.error is not None
        assert (
            "Database not connected" in result.error
            or "No database connection" in result.error
        )

    def test_execute_batch_not_connected_real_execution(self) -> None:
        """Test execute_batch when not connected - real execution."""
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config)
        operations = [
            ("SELECT 1 FROM DUAL", None),
            ("SELECT 2 FROM DUAL", None),
        ]

        result = api.execute_batch(operations)

        assert result.is_failure
        assert result.error is not None
        assert (
            "Database not connected" in result.error
            or "No database connection" in result.error
        )

    def test_get_tables_not_connected_real_execution(self) -> None:
        """Test get_tables when not connected - real execution."""
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config)
        result = api.get_tables()

        assert result.is_failure
        assert result.error is not None
        assert (
            "Database not connected" in result.error
            or "No database connection" in result.error
        )

    def test_get_schemas_not_connected_real_execution(self) -> None:
        """Test get_schemas when not connected - real execution."""
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config)
        result = api.get_schemas()

        assert result.is_failure
        assert result.error is not None
        assert (
            "Database not connected" in result.error
            or "No database connection" in result.error
        )

    def test_get_columns_not_connected_real_execution(self) -> None:
        """Test get_columns when not connected - real execution."""
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config)
        result = api.get_columns("TEST_TABLE")

        assert result.is_failure
        assert result.error is not None
        assert (
            "Database not connected" in result.error
            or "No database connection" in result.error
        )

    def test_test_connection_not_connected_real_execution(self) -> None:
        """Test test_connection when not connected - real execution."""
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config)
        result = api.test_connection()

        assert result.is_failure
        assert result.error is not None
        assert "No connection established" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_context_manager_real_execution(
        self,
        mock_connection_class: Mock,
    ) -> None:
        """Test context manager with real API code execution."""
        # Setup mock connection to avoid external dependencies
        mock_connection = MagicMock()
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.disconnect.return_value = FlextResult.ok(data=True)
        mock_connection_class.return_value = mock_connection

        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config)

        # Test context manager - this executes real API code
        with api as connected_api:
            assert connected_api == api
            assert api._is_connected

        # Should auto-disconnect
        assert not api._is_connected

    def test_initialization_observability_setup(self) -> None:
        """Test that observability components are properly initialized."""
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config, "test_observability")

        # Verify observability components exist and are configured
        assert api._observability is not None
        assert api._error_handler is not None
        assert hasattr(api, "_plugin_platform")
        assert api._context_name == "test_observability"

    def test_logger_initialization(self) -> None:
        """Test logger initialization with proper naming."""
        api = FlextDbOracleApi(context_name="test_logger")

        # Logger should be properly named
        assert api._logger is not None
        assert hasattr(api, "_logger")

    def test_container_integration(self) -> None:
        """Test container integration initialization."""
        api = FlextDbOracleApi(context_name="test_container")

        # Container should be initialized
        assert api._container is not None
        assert hasattr(api, "_container")

    def test_default_settings(self) -> None:
        """Test default settings are properly configured."""
        api = FlextDbOracleApi()

        # Default settings should be configured
        assert api._retry_attempts == 3
        assert api._context_name == "oracle"
        assert not api._is_connected

    def test_method_chaining_return_values(self) -> None:
        """Test that methods return self for chaining where appropriate."""
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config)

        # disconnect() should return self for chaining
        result = api.disconnect()
        assert result == api

    def test_string_representation(self) -> None:
        """Test string representation if implemented."""
        config = FlextDbOracleConfig(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
        )

        api = FlextDbOracleApi(config, "repr_test")

        # Should not raise error when converting to string
        str_repr = str(api)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

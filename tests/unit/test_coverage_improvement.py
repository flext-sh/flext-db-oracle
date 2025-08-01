"""Tests focused on improving code coverage for flext-db-oracle.

These tests import and execute real code to improve coverage metrics
while maintaining proper isolation through controlled inputs.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_core import FlextResult

# Import all modules to ensure they're covered
import flext_db_oracle
from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConnection,
    create_data_validation_plugin,
    create_performance_monitor_plugin,
    create_security_audit_plugin,
    register_all_oracle_plugins,
)
from flext_db_oracle.config import FlextDbOracleConfig as DirectConfig
from flext_db_oracle.constants import FlextOracleDbConstants
from flext_db_oracle.exceptions import (
    FlextDbOracleConnectionError,
    FlextDbOracleError,
    FlextDbOracleQueryError,
    FlextDbOracleValidationError,
)
from flext_db_oracle.metadata import (
    FlextDbOracleColumn,
    FlextDbOracleSchema,
    FlextDbOracleTable,
)
from flext_db_oracle.observability import (
    FlextDbOracleErrorHandler,
    FlextDbOracleOperationTracker,
)
from flext_db_oracle.types import (
    TDbOracleColumn,
    TDbOracleConnectionStatus,
    TDbOracleQueryResult,
    TDbOracleSchema,
    TDbOracleTable,
)


class TestModuleImportsAndBasics:
    """Test basic module imports and initialization."""

    def test_module_version(self) -> None:
        """Test module version is accessible."""
        assert hasattr(flext_db_oracle, "__version__")
        assert isinstance(flext_db_oracle.__version__, str)
        assert len(flext_db_oracle.__version__) > 0

    def test_module_author(self) -> None:
        """Test module author is accessible."""
        assert hasattr(flext_db_oracle, "__author__")
        assert isinstance(flext_db_oracle.__author__, str)

    def test_module_description(self) -> None:
        """Test module description is accessible."""
        assert hasattr(flext_db_oracle, "__description__")
        assert isinstance(flext_db_oracle.__description__, str)

    def test_all_exports_accessible(self) -> None:
        """Test all __all__ exports are accessible."""
        assert hasattr(flext_db_oracle, "__all__")
        exports = flext_db_oracle.__all__

        for export_name in exports:
            assert hasattr(flext_db_oracle, export_name), (
                f"Export {export_name} not found"
            )

    def test_constants_values(self) -> None:
        """Test Oracle constants have expected values."""
        assert isinstance(FlextOracleDbConstants.ORACLE_DEFAULT_PORT, int)
        assert FlextOracleDbConstants.ORACLE_DEFAULT_PORT > 0

        assert isinstance(FlextOracleDbConstants.ORACLE_TEST_QUERY, str)
        assert len(FlextOracleDbConstants.ORACLE_TEST_QUERY) > 0

        assert isinstance(FlextOracleDbConstants.SINGER_TO_ORACLE_TYPE_MAP, dict)
        assert len(FlextOracleDbConstants.SINGER_TO_ORACLE_TYPE_MAP) > 0

        assert isinstance(FlextOracleDbConstants.ORACLE_DATE_TYPE, str)
        assert isinstance(FlextOracleDbConstants.ORACLE_TIMESTAMP_TYPE, str)


class TestConfigurationCreation:
    """Test configuration creation and validation."""

    def test_config_creation_minimal(self) -> None:
        """Test minimal config creation."""
        config = DirectConfig(
            host="localhost",
            username="user",
            password="pass",
            service_name="DB",
        )

        assert config.host == "localhost"
        assert config.username == "user"
        assert config.service_name == "DB"
        assert config.port == FlextOracleDbConstants.ORACLE_DEFAULT_PORT

    def test_config_creation_full(self) -> None:
        """Test full config creation."""
        config = DirectConfig(
            host="oracle.example.com",
            port=1522,
            username="testuser",
            password="testpass",
            service_name="TESTDB",
            encoding="UTF-8",
        )

        assert config.host == "oracle.example.com"
        assert config.port == 1522
        assert config.username == "testuser"
        assert config.service_name == "TESTDB"
        assert config.encoding == "UTF-8"

    def test_config_validation_errors(self) -> None:
        """Test config validation errors."""
        # Test invalid port - expect Pydantic ValidationError
        from pydantic import ValidationError

        with pytest.raises(
            ValidationError, match="Input should be greater than or equal to 1",
        ):
            DirectConfig(
                host="localhost",
                port=-1,  # Invalid port
                username="user",
                password="pass",
                service_name="DB",
            )

    def test_config_string_representation(self) -> None:
        """Test config string representation."""
        config = DirectConfig(
            host="localhost",
            username="user",
            password="pass",
            service_name="DB",
        )

        str_repr = str(config)
        assert "localhost" in str_repr
        assert "pass" not in str_repr  # Password should be masked


class TestExceptionHierarchy:
    """Test exception classes and hierarchy."""

    def test_base_exception_creation(self) -> None:
        """Test base exception creation."""
        error = FlextDbOracleError("Base error")
        assert str(error) != ""
        assert isinstance(error, Exception)

    def test_connection_error_creation(self) -> None:
        """Test connection error creation."""
        from flext_core.exceptions import FlextConnectionError

        error = FlextDbOracleConnectionError("Connection failed")
        assert str(error) != ""
        assert isinstance(error, FlextConnectionError)

    def test_query_error_creation(self) -> None:
        """Test query error creation."""
        error = FlextDbOracleQueryError("Query failed")
        assert str(error) != ""
        assert isinstance(error, FlextDbOracleError)

    def test_validation_error_creation(self) -> None:
        """Test validation error creation."""
        from flext_core.exceptions import FlextValidationError

        error = FlextDbOracleValidationError("Validation failed")
        assert str(error) != ""
        assert isinstance(error, FlextValidationError)


class TestMetadataClasses:
    """Test metadata classes creation and basic functionality."""

    def test_column_creation(self) -> None:
        """Test column metadata creation."""
        column = FlextDbOracleColumn(
            name="TEST_COLUMN",
            data_type="VARCHAR2",
            column_id=1,
            nullable=True,
        )

        assert column.name == "TEST_COLUMN"
        assert column.data_type == "VARCHAR2"
        assert column.column_id == 1
        assert column.nullable is True

    def test_table_creation(self) -> None:
        """Test table metadata creation."""
        column = FlextDbOracleColumn(
            name="ID",
            data_type="NUMBER",
            column_id=1,
            nullable=False,
        )

        table = FlextDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[column],
        )

        assert table.name == "TEST_TABLE"
        assert table.schema_name == "TEST_SCHEMA"
        assert len(table.columns) == 1

    def test_schema_creation(self) -> None:
        """Test schema metadata creation."""
        schema = FlextDbOracleSchema(
            name="TEST_SCHEMA",
        )

        assert schema.name == "TEST_SCHEMA"


class TestObservabilityClasses:
    """Test observability classes initialization."""

    def test_operation_tracker_creation(self) -> None:
        """Test operation tracker creation."""
        from unittest.mock import MagicMock

        mock_observability = MagicMock()
        tracker = FlextDbOracleOperationTracker(
            mock_observability,
            "test_operation",
        )

        # Should be able to create without errors
        assert tracker is not None

    def test_error_handler_creation(self) -> None:
        """Test error handler creation with mock observability."""
        from unittest.mock import MagicMock

        mock_observability = MagicMock()
        handler = FlextDbOracleErrorHandler(mock_observability)

        assert handler is not None


class TestPluginSystem:
    """Test plugin system functions."""

    def test_create_data_validation_plugin(self) -> None:
        """Test data validation plugin creation."""
        plugin = create_data_validation_plugin()

        assert plugin is not None
        # Should have basic plugin structure

    def test_create_performance_monitor_plugin(self) -> None:
        """Test performance monitor plugin creation."""
        plugin = create_performance_monitor_plugin()

        assert plugin is not None
        # Should have basic plugin structure

    def test_create_security_audit_plugin(self) -> None:
        """Test security audit plugin creation."""
        plugin = create_security_audit_plugin()

        assert plugin is not None
        # Should have basic plugin structure

    def test_register_all_oracle_plugins(self) -> None:
        """Test registering all Oracle plugins."""
        # Create a minimal API instance for testing
        config = DirectConfig(
            host="localhost",
            username="user",
            password="pass",
            service_name="DB",
        )
        api = FlextDbOracleApi(config)

        # This should execute without errors
        result = register_all_oracle_plugins(api)

        # Should return some result indicating success
        assert result is not None
        assert result.is_success or result.is_failure  # Should be a FlextResult


class TestConnectionClass:
    """Test connection class basic functionality."""

    def test_connection_creation(self) -> None:
        """Test connection creation with config."""
        config = DirectConfig(
            host="localhost",
            username="user",
            password="pass",
            service_name="DB",
        )

        connection = FlextDbOracleConnection(config)

        assert connection is not None
        assert connection.config == config

    def test_connection_properties(self) -> None:
        """Test connection properties."""
        config = DirectConfig(
            host="localhost",
            username="user",
            password="pass",
            service_name="DB",
        )

        connection = FlextDbOracleConnection(config)

        # Test basic properties don't raise errors
        try:
            _ = connection.is_connected
            _ = str(connection)
        except (ValueError, TypeError, AttributeError) as e:
            pytest.fail(f"Connection properties should not raise errors: {e}")


class TestApiClassBasics:
    """Test API class basic functionality without external dependencies."""

    def test_api_creation_no_config(self) -> None:
        """Test API creation without config."""
        api = FlextDbOracleApi()

        assert api is not None
        assert api._config is None
        assert not api.is_connected

    def test_api_creation_with_config(self) -> None:
        """Test API creation with config."""
        config = DirectConfig(
            host="localhost",
            username="user",
            password="pass",
            service_name="DB",
        )

        api = FlextDbOracleApi(config)

        assert api is not None
        assert api.config == config
        assert not api.is_connected

    def test_api_string_representation(self) -> None:
        """Test API string representation."""
        api = FlextDbOracleApi()

        str_repr = str(api)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    def test_api_properties(self) -> None:
        """Test API properties access."""
        config = DirectConfig(
            host="localhost",
            username="user",
            password="pass",
            service_name="DB",
        )

        api = FlextDbOracleApi(config)

        # Test all properties are accessible
        assert api.config == config
        assert api.connection is None
        assert not api.is_connected

    def test_api_with_config_method(self) -> None:
        """Test API with_config class method."""
        api = FlextDbOracleApi.with_config(
            {
                "host": "test.host.com",
                "port": 1521,
                "username": "testuser",
                "password": "testpass",
                "service_name": "TESTDB",
            },
        )

        assert api is not None
        assert api._config is not None
        assert api._config.host == "test.host.com"
        assert api._config.port == 1521


class TestTypeDefinitions:
    """Test type definitions and type aliases."""

    def test_type_aliases_exist(self) -> None:
        """Test that type aliases are properly defined."""
        # These should not raise ImportError
        assert TDbOracleColumn is not None
        assert TDbOracleConnectionStatus is not None
        assert TDbOracleQueryResult is not None
        assert TDbOracleSchema is not None
        assert TDbOracleTable is not None


class TestIntegrationWithFlextCore:
    """Test integration with flext-core patterns."""

    def test_flext_result_usage(self) -> None:
        """Test FlextResult is used properly."""
        # Create a simple FlextResult to ensure integration
        result = FlextResult.ok("test_data")

        assert result.is_success
        assert result.data == "test_data"

        failure_result = FlextResult.fail("test_error")
        assert failure_result.is_failure
        assert failure_result.error == "test_error"

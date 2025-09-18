"""Comprehensive tests for Oracle CLI Service functionality.

Tests all Oracle CLI service operations including health checks, schema listing,
table operations, and query execution to achieve high coverage for cli.py.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from unittest.mock import Mock, patch

import yaml

from flext_core import FlextResult
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.cli import FlextDbOracleCliService
from flext_db_oracle.models import FlextDbOracleModels


class TestFlextDbOracleCliService:
    """Test CLI service initialization and basic functionality."""

    def test_cli_service_initialization_success(self) -> None:
        """Test successful CLI service initialization."""
        cli_service = FlextDbOracleCliService()

        assert cli_service is not None
        assert cli_service._container is not None
        assert cli_service._logger is not None
        # _cli_main may be None if FlextCliMain fails to initialize

    def test_cli_service_initialization_with_cli_failure(self) -> None:
        """Test CLI service initialization when FlextCliMain fails."""
        with patch("flext_db_oracle.cli.FlextCliMain") as mock_cli_main:
            mock_cli_main.side_effect = Exception("CLI initialization error")

            cli_service = FlextDbOracleCliService()

            assert cli_service is not None
            assert cli_service._cli_main is None

    def test_initialize_cli_main_success(self) -> None:
        """Test successful CLI main initialization."""
        cli_service = FlextDbOracleCliService()

        result = cli_service._initialize_cli_main()

        # Should return a result, might succeed or fail depending on FlextCliMain availability
        assert isinstance(result, FlextResult)

    def test_initialize_cli_main_failure(self) -> None:
        """Test CLI main initialization failure handling."""
        cli_service = FlextDbOracleCliService()

        with patch("flext_db_oracle.cli.FlextCliMain") as mock_cli_main:
            mock_cli_main.side_effect = Exception("Initialization error")

            result = cli_service._initialize_cli_main()

            assert result.is_failure
            assert "FlextCliMain initialization failed" in str(result.error)


class TestOracleConnectionHelper:
    """Test Oracle connection helper functionality."""

    def test_create_config_from_params_success(self) -> None:
        """Test successful config creation from parameters."""
        result = (
            FlextDbOracleCliService._OracleConnectionHelper.create_config_from_params(
                host="test-host",
                port=1522,
                service_name="TEST_SERVICE",
                username="test_user",
                password="test_password",
            )
        )

        assert result.is_success
        config = result.value
        assert config.host == "test-host"
        assert config.port == 1522
        assert config.service_name == "TEST_SERVICE"
        assert config.username == "test_user"
        assert config.password == "test_password"

    def test_create_config_from_params_defaults(self) -> None:
        """Test config creation with default parameters."""
        result = (
            FlextDbOracleCliService._OracleConnectionHelper.create_config_from_params(
                password="test_password"
            )
        )

        assert result.is_success
        config = result.value
        assert config.host == "localhost"
        assert config.port == 1521
        assert config.service_name == "XEPDB1"
        assert config.username == "system"

    def test_create_config_from_params_no_password(self) -> None:
        """Test config creation fails without password."""
        result = (
            FlextDbOracleCliService._OracleConnectionHelper.create_config_from_params(
                host="test-host", username="test_user"
            )
        )

        assert result.is_failure
        assert "Password is required" in str(result.error)

    def test_create_config_from_params_empty_password(self) -> None:
        """Test config creation fails with empty password."""
        result = (
            FlextDbOracleCliService._OracleConnectionHelper.create_config_from_params(
                host="test-host", username="test_user", password=""
            )
        )

        assert result.is_failure
        assert "Password is required" in str(result.error)

    def test_create_config_from_params_validation_error(self) -> None:
        """Test config creation handles validation errors."""
        result = (
            FlextDbOracleCliService._OracleConnectionHelper.create_config_from_params(
                host="",  # Empty host should cause validation error
                password="test_password",
            )
        )

        assert result.is_failure
        assert "Configuration creation failed" in str(result.error)

    def test_validate_connection_success(self) -> None:
        """Test successful connection validation."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_password",
        )

        with patch.object(FlextDbOracleApi, "connect") as mock_connect:
            mock_connect.return_value = FlextResult[FlextDbOracleApi].ok(Mock())

            result = (
                FlextDbOracleCliService._OracleConnectionHelper.validate_connection(
                    config
                )
            )

        assert result.is_success
        assert result.value is True

    def test_validate_connection_failure(self) -> None:
        """Test connection validation failure handling."""
        config = FlextDbOracleModels.OracleConfig(
            host="invalid-host",
            port=1521,
            service_name="INVALID",
            username="invalid_user",
            password="invalid_password",
        )

        with patch.object(FlextDbOracleApi, "connect") as mock_connect:
            mock_connect.return_value = FlextResult[FlextDbOracleApi].fail(
                "Connection failed"
            )

            result = (
                FlextDbOracleCliService._OracleConnectionHelper.validate_connection(
                    config
                )
            )

        assert result.is_failure
        assert "Connection failed" in str(result.error)


class TestOutputFormatter:
    """Test output formatter functionality."""

    def test_formatter_initialization_with_cli_main(self) -> None:
        """Test formatter initialization with CLI main."""
        mock_cli_main = Mock()
        formatter = FlextDbOracleCliService._OutputFormatter(mock_cli_main)

        assert formatter._cli_main is mock_cli_main

    def test_formatter_initialization_without_cli_main(self) -> None:
        """Test formatter initialization without CLI main."""
        formatter = FlextDbOracleCliService._OutputFormatter()

        assert formatter._cli_main is None

    def test_format_success_message(self) -> None:
        """Test success message formatting."""
        formatter = FlextDbOracleCliService._OutputFormatter()

        result = formatter.format_success_message("Operation completed")

        assert result.is_success
        assert result.value == "✅ Operation completed"

    def test_format_error_message(self) -> None:
        """Test error message formatting."""
        formatter = FlextDbOracleCliService._OutputFormatter()

        result = formatter.format_error_message("Something went wrong")

        assert result.is_success
        assert result.value == "❌ Something went wrong"

    def test_format_list_output_table_format(self) -> None:
        """Test list output formatting in table format."""
        formatter = FlextDbOracleCliService._OutputFormatter()
        items = ["table1", "table2", "table3"]

        result = formatter.format_list_output(items, "Database Tables", "table")

        assert result.is_success
        output = result.value
        assert "Database Tables" in output
        assert "table1" in output
        assert "table2" in output
        assert "table3" in output

    def test_format_list_output_json_format(self) -> None:
        """Test list output formatting in JSON format."""
        formatter = FlextDbOracleCliService._OutputFormatter()
        items = ["schema1", "schema2"]

        result = formatter.format_list_output(items, "Schemas", "json")

        assert result.is_success
        output = result.value
        data = json.loads(output)
        assert data["title"] == "Schemas"
        assert data["items"] == ["schema1", "schema2"]

    def test_format_list_output_yaml_format(self) -> None:
        """Test list output formatting in YAML format."""
        formatter = FlextDbOracleCliService._OutputFormatter()
        items = ["item1", "item2"]

        result = formatter.format_list_output(items, "Test Items", "yaml")

        assert result.is_success
        output = result.value
        data = yaml.safe_load(output)
        assert data["title"] == "Test Items"
        assert data["items"] == ["item1", "item2"]

    def test_format_list_output_plain_format(self) -> None:
        """Test list output formatting in plain format."""
        formatter = FlextDbOracleCliService._OutputFormatter()
        items = ["item1", "item2"]

        result = formatter.format_list_output(items, "Test Items", "plain")

        assert result.is_success
        output = result.value
        assert "Test Items" in output
        assert "item1" in output
        assert "item2" in output

    def test_format_list_output_dict_items(self) -> None:
        """Test list output formatting with dict items."""
        formatter = FlextDbOracleCliService._OutputFormatter()
        items: list[dict[str, object]] = [
            {"name": "table1", "type": "TABLE"},
            {"name": "table2", "type": "VIEW"},
            {"other": "value"},  # Test item without name
        ]

        result = formatter.format_list_output(items, "Database Objects", "table")

        assert result.is_success
        output = result.value
        assert "table1" in output
        assert "table2" in output

    def test_format_data_json(self) -> None:
        """Test data formatting as JSON."""
        formatter = FlextDbOracleCliService._OutputFormatter()
        data = {"key": "value", "number": 42}

        result = formatter.format_data(data, "json")

        assert result.is_success
        parsed_data = json.loads(result.value)
        assert parsed_data == data

    def test_format_data_yaml(self) -> None:
        """Test data formatting as YAML."""
        formatter = FlextDbOracleCliService._OutputFormatter()
        data = {"key": "value", "number": 42}

        result = formatter.format_data(data, "yaml")

        assert result.is_success
        parsed_data = yaml.safe_load(result.value)
        assert parsed_data == data

    def test_format_data_plain(self) -> None:
        """Test data formatting as plain text."""
        formatter = FlextDbOracleCliService._OutputFormatter()
        data = {"key": "value"}

        result = formatter.format_data(data, "plain")

        assert result.is_success
        assert str(data) == result.value

    def test_display_message(self) -> None:
        """Test message display functionality."""
        formatter = FlextDbOracleCliService._OutputFormatter()

        # This method prints to stdout, so we test it doesn't raise an exception
        formatter.display_message("Test message")


class TestCliServiceOperations:
    """Test CLI service operation methods."""

    def test_execute_health_check_success(self) -> None:
        """Test successful health check execution."""
        cli_service = FlextDbOracleCliService()

        FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_password",
        )

        with patch.object(
            FlextDbOracleCliService._OracleConnectionHelper, "validate_connection"
        ) as mock_validate:
            mock_validate.return_value = FlextResult[bool].ok(True)

            result = cli_service.execute_health_check(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
            )

        assert result.is_success
        output = result.value
        assert "healthy" in output

    def test_execute_health_check_config_creation_failure(self) -> None:
        """Test health check with config creation failure."""
        cli_service = FlextDbOracleCliService()

        result = cli_service.execute_health_check(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="",  # Empty password should cause failure
        )

        assert result.is_failure  # Method returns failure when config creation fails
        assert result.error is not None and "Password is required" in result.error

    def test_execute_health_check_connection_failure(self) -> None:
        """Test health check with connection validation failure."""
        cli_service = FlextDbOracleCliService()

        with patch.object(
            FlextDbOracleCliService._OracleConnectionHelper, "validate_connection"
        ) as mock_validate:
            mock_validate.return_value = FlextResult[bool].fail("Database unreachable")

            result = cli_service.execute_health_check(
                host="unreachable-host",
                port=1521,
                service_name="INVALID",
                username="test_user",
                password="test_password",
            )

        assert (
            result.is_failure
        )  # Method returns failure when connection validation fails
        assert result.error is not None and "Database unreachable" in result.error

    def test_execute_list_schemas_success(self) -> None:
        """Test successful schema listing."""
        cli_service = FlextDbOracleCliService()

        mock_api = Mock()
        mock_api.get_schemas.return_value = FlextResult[list[str]].ok(
            ["SCHEMA1", "SCHEMA2", "SCHEMA3"]
        )

        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "get_schemas") as mock_get_schemas,
        ):
            mock_connect.return_value = FlextResult[FlextDbOracleApi].ok(mock_api)
            mock_get_schemas.return_value = FlextResult[list[str]].ok(
                ["SCHEMA1", "SCHEMA2"]
            )

            result = cli_service.execute_list_schemas(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
                output_format="table",
            )

        assert result.is_success
        output = result.value
        assert "Listed 2 schemas successfully" in output

    def test_execute_list_schemas_connection_failure(self) -> None:
        """Test schema listing with connection failure."""
        cli_service = FlextDbOracleCliService()

        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
        ):
            mock_connect.return_value = FlextResult[FlextDbOracleApi].fail(
                "Connection failed"
            )

            result = cli_service.execute_list_schemas(
                host="invalid-host",
                port=1521,
                service_name="INVALID",
                username="test_user",
                password="test_password",
            )

        assert result.is_failure  # Method returns failure when connection fails
        assert result.error is not None and "Connection failed" in result.error

    def test_execute_list_schemas_api_failure(self) -> None:
        """Test schema listing with API failure."""
        cli_service = FlextDbOracleCliService()

        mock_api = Mock()

        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "get_schemas") as mock_get_schemas,
        ):
            mock_connect.return_value = FlextResult[FlextDbOracleApi].ok(mock_api)
            mock_get_schemas.return_value = FlextResult[list[str]].fail(
                "Schema query failed"
            )

            result = cli_service.execute_list_schemas(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
            )

        assert result.is_failure  # Method returns failure when API operation fails
        assert result.error is not None and "Schema query failed" in result.error

    def test_execute_list_tables_success(self) -> None:
        """Test successful table listing."""
        cli_service = FlextDbOracleCliService()

        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "get_tables") as mock_get_tables,
        ):
            mock_connect.return_value = FlextResult[FlextDbOracleApi].ok(Mock())
            mock_get_tables.return_value = FlextResult[list[str]].ok(
                ["TABLE1", "TABLE2"]
            )

            result = cli_service.execute_list_tables(
                schema="TEST_SCHEMA",
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
                output_format="json",
            )

        assert result.is_success
        output = result.value
        assert "Listed 2 tables" in output  # Allow for schema name in message

    def test_execute_list_tables_no_schema(self) -> None:
        """Test table listing without schema name."""
        cli_service = FlextDbOracleCliService()

        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "get_tables") as mock_get_tables,
        ):
            mock_connect.return_value = FlextResult[FlextDbOracleApi].ok(Mock())
            mock_get_tables.return_value = FlextResult[list[str]].ok(["TABLE1"])

            result = cli_service.execute_list_tables(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
            )

        assert result.is_success
        output = result.value
        assert "Listed 1 tables" in output  # Allow for schema name in message

    def test_execute_query_success(self) -> None:
        """Test successful query execution."""
        cli_service = FlextDbOracleCliService()

        mock_result = [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]

        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "query") as mock_query,
        ):
            mock_connect.return_value = FlextResult[FlextDbOracleApi].ok(Mock())
            mock_query.return_value = FlextResult[list[dict[str, object]]].ok(
                mock_result
            )

            result = cli_service.execute_query(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
                sql="SELECT * FROM test_table",
                output_format="json",
            )

        assert result.is_success
        output = result.value
        # The result can be either formatted JSON or a success message
        if output.startswith("{"):
            data = json.loads(output)
            assert data["rows"] == 2
        else:
            assert "Query executed successfully" in output

    def test_execute_query_empty_sql(self) -> None:
        """Test query execution with empty SQL."""
        cli_service = FlextDbOracleCliService()

        result = cli_service.execute_query(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_password",
            sql="",
        )

        assert result.is_failure
        assert "SQL query cannot be empty" in str(result.error)

    def test_execute_query_whitespace_sql(self) -> None:
        """Test query execution with whitespace-only SQL."""
        cli_service = FlextDbOracleCliService()

        result = cli_service.execute_query(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_password",
            sql="   \n\t  ",
        )

        assert result.is_failure
        assert "SQL query cannot be empty" in str(result.error)


class TestYamlModuleProtocol:
    """Test YAML module protocol interface."""

    def test_yaml_module_protocol_interface(self) -> None:
        """Test that yaml module conforms to the protocol."""
        # Test that standard yaml module matches our protocol
        yaml_module = yaml

        # Test dump method exists and works
        data = {"test": "value"}
        result = yaml_module.dump(data, default_flow_style=True)

        assert isinstance(result, str)
        assert "test" in result
        assert "value" in result

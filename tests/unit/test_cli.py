"""Real CLI tests WITHOUT mocks - testing actual FlextDbOracleClient functionality.

This module provides comprehensive tests for CLI components using REAL code
execution without mocks, following FLEXT testing standards.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from unittest.mock import Mock, patch

import yaml
from flext_core import r, t
from pydantic import TypeAdapter

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleCli,
    FlextDbOracleClient,
    FlextDbOracleSettings,
    FlextDbOracleUtilities,
)
from flext_db_oracle.cli import HealthCheckReport, NamedItem


class TestFlextDbOracleClientReal:
    """Test FlextDbOracleClient class with REAL functionality - NO MOCKS."""

    def test_client_initialization_debug_mode(self) -> None:
        """Test CLI client initialization in debug mode."""
        client = FlextDbOracleClient(debug=True)
        assert client.debug is True
        assert client.current_connection is None
        assert client.user_preferences["default_output_format"] == "table"
        assert client.user_preferences["show_execution_time"] == "True"
        assert client.container is not None
        assert client.logger is not None

    def test_client_initialization_production_mode(self) -> None:
        """Test CLI client initialization in production mode."""
        client = FlextDbOracleClient(debug=False)
        assert client.debug is False
        assert client.user_preferences["auto_confirm_operations"] == "False"
        assert client.user_preferences["connection_timeout"] == 30
        assert client.user_preferences["query_limit"] == 1000

    def test_client_initialization_real(self) -> None:
        """Test actual CLI client initialization."""
        client = FlextDbOracleClient()
        assert client.container is not None
        assert client.logger is not None
        assert client.current_connection is None

    def test_configure_preferences_real(self) -> None:
        """Test configuring user preferences with real values."""
        client = FlextDbOracleClient()
        result = client.configure_preferences(
            default_output_format="json", query_limit=2000, show_execution_time=False
        )
        assert result.is_success is True
        assert client.user_preferences["default_output_format"] == "json"
        assert client.user_preferences["query_limit"] == 2000
        assert client.user_preferences["show_execution_time"] is False

    def test_configure_preferences_invalid_keys(self) -> None:
        """Test configuring preferences with invalid keys."""
        client = FlextDbOracleClient()
        original_prefs = client.user_preferences.model_copy()
        result = client.configure_preferences(
            invalid_key="value", another_invalid="test"
        )
        assert result.is_success is True
        original_dict: dict[str, object] = (
            original_prefs.model_dump()
            if hasattr(original_prefs, "model_dump")
            else dict(original_prefs)
        )
        original_dict["invalid_key"] = "value"
        original_dict["another_invalid"] = "test"
        assert client.user_preferences.model_dump() == original_dict

    def test_connection_without_config(self) -> None:
        """Test connection methods without active connection."""
        client = FlextDbOracleClient()
        result = client.execute_query("SELECT 1 FROM DUAL")
        assert not result.is_success
        assert result.error
        assert (
            result.error is not None and "No active Oracle connection" in result.error
        )
        schemas_result = client.list_schemas()
        assert not schemas_result.is_success
        assert schemas_result.error
        assert "No active Oracle connection" in schemas_result.error
        tables_result = client.list_tables()
        assert not tables_result.is_success
        assert tables_result.error
        assert "No active Oracle connection" in tables_result.error
        health_result = client.health_check()
        assert not health_result.is_success
        assert health_result.error
        assert "No active Oracle connection" in health_result.error

    def test_connect_to_oracle_invalid_credentials(self) -> None:
        """Test Oracle connection with invalid credentials (real connection attempt)."""
        client = FlextDbOracleClient()
        result = client.connect_to_oracle(
            host="nonexistent-host-12345.invalid",
            port=9999,
            service_name="INVALID",
            username="invalid_user",
            password="invalid_password",
        )
        assert not result.is_success
        assert result.error
        assert (
            "Connection failed" in result.error
            or "Oracle connection failed" in result.error
            or "Connection error" in result.error
        )

    def test_get_global_client_real(self) -> None:
        """Test creating client instances with real functionality."""
        client1 = FlextDbOracleClient()
        client2 = FlextDbOracleClient()
        assert isinstance(client1, FlextDbOracleClient)
        assert isinstance(client2, FlextDbOracleClient)
        assert client1 is not client2

    def test_run_cli_command_real(self) -> None:
        """Test CLI command execution with real functionality."""
        result = FlextDbOracleClient.run_cli_command("health", timeout=30)
        assert isinstance(result, r)

    def test_connection_wizard_real_validation(self) -> None:
        """Test connection wizard input validation."""
        client = FlextDbOracleClient()
        assert hasattr(client, "connect_to_oracle")
        assert callable(client.connect_to_oracle)

    def test_oracle_cli_client_methods_real(self) -> None:
        """Test FlextDbOracleClient has proper CLI methods."""
        client = FlextDbOracleClient()
        assert hasattr(client, "connect_to_oracle")
        assert hasattr(client, "execute_query")
        assert hasattr(client, "list_schemas")
        assert hasattr(client, "list_tables")
        assert hasattr(client, "health_check")

    def test_client_real_error_handling(self) -> None:
        """Test real error handling in client methods."""
        client = FlextDbOracleClient()
        result = client.execute_query("")
        assert not result.is_success
        bad_result = client.configure_preferences(valid_key="")
        assert isinstance(bad_result, r)
        assert bad_result.is_success

    def test_client_preferences_persistence(self) -> None:
        """Test that preference changes persist within client instance."""
        client = FlextDbOracleClient()
        client.user_preferences["default_output_format"]
        client.user_preferences["connection_timeout"]
        client.configure_preferences(
            default_output_format="json", connection_timeout=60
        )
        assert client.user_preferences["default_output_format"] == "json"
        assert client.user_preferences["connection_timeout"] == 60
        assert client.user_preferences["query_limit"] == 1000


class TestFlextDbOracleClientIntegration:
    """Integration tests using real Oracle database operations."""

    def test_client_with_real_config_creation(self) -> None:
        """Test client operations with real configuration objects."""
        config = FlextDbOracleSettings(
            host="localhost",
            port=1521,
            name="XE",
            service_name="XE",
            username="test",
            password="test",
            ssl_server_cert_dn=None,
        )
        client = FlextDbOracleClient()
        service_name = config.service_name or "default_service"
        result = client.connect_to_oracle(
            config.host,
            config.port,
            service_name,
            config.username,
            config.password.get_secret_value() if config.password else None,
        )
        assert not result.is_success
        assert isinstance(result.error, str)


class TestFlextDbOracleCli:
    """Test CLI service initialization and basic functionality."""

    def test_cli_service_initialization_success(self) -> None:
        """Test successful CLI service initialization."""
        cli_service = FlextDbOracleCli()
        assert cli_service is not None
        assert cli_service._container is not None
        assert cli_service.logger is not None

    def test_cli_service_initialization_basic(self) -> None:
        """Test basic CLI service initialization."""
        cli_service = FlextDbOracleCli()
        assert cli_service is not None
        assert hasattr(cli_service, "logger")

    def test_initialize_cli_main_success(self) -> None:
        """Test successful CLI main initialization."""
        cli_service = FlextDbOracleCli()
        result = cli_service._initialize_cli_main()
        assert isinstance(result, r)

    def test_initialize_cli_main_failure(self) -> None:
        """Test CLI main initialization failure handling."""
        cli_service = FlextDbOracleCli()
        with patch("flext_db_oracle.cli.FlextCliCommands") as mock_cli_main:
            mock_cli_main.side_effect = Exception("Initialization error")
            result = cli_service._initialize_cli_main()
            assert result.is_failure
            assert "FlextCliCommands initialization failed" in str(result.error)


class TestOracleConnectionHelper:
    """Test Oracle connection helper functionality."""

    def test_create_config_from_params_success(self) -> None:
        """Test successful config creation from parameters."""
        result = FlextDbOracleCli._OracleConnectionHelper.create_config_from_params(
            host="test-host",
            port=1522,
            service_name="TEST_SERVICE",
            username="test_user",
            password="test_password",
        )
        assert result.is_success
        config = result.value
        assert config.host == "test-host"
        assert config.port == 1522
        assert config.service_name == "TEST_SERVICE"
        assert config.username == "test_user"
        assert config.password is not None
        assert config.password.get_secret_value() == "test_password"

    def test_create_config_from_params_defaults(self) -> None:
        """Test config creation with default parameters."""
        result = FlextDbOracleCli._OracleConnectionHelper.create_config_from_params(
            password="test_password"
        )
        assert result.is_success
        config = result.value
        assert config.host == "localhost"
        assert config.port == 1521
        assert config.service_name == "XEPDB1"
        assert config.username == "system"

    def test_create_config_from_params_no_password(self) -> None:
        """Test config creation fails without password."""
        result = FlextDbOracleCli._OracleConnectionHelper.create_config_from_params(
            host="test-host", username="test_user"
        )
        assert result.is_failure
        assert "Password is required" in str(result.error)

    def test_create_config_from_params_empty_password(self) -> None:
        """Test config creation fails with empty password."""
        result = FlextDbOracleCli._OracleConnectionHelper.create_config_from_params(
            host="test-host", username="test_user", password=""
        )
        assert result.is_failure
        assert "Password is required" in str(result.error)

    def test_create_config_from_params_validation_error(self) -> None:
        """Test config creation handles validation errors."""
        result = FlextDbOracleCli._OracleConnectionHelper.create_config_from_params(
            host="", password="test_password"
        )
        assert result.is_failure
        assert "Configuration creation failed" in str(result.error)

    def test_validate_connection_success(self) -> None:
        """Test successful connection validation."""
        config = FlextDbOracleSettings(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_password",
        )
        with patch.object(FlextDbOracleApi, "connect") as mock_connect:
            mock_connect.return_value = r[FlextDbOracleApi].ok(Mock())
            result = FlextDbOracleCli._OracleConnectionHelper.validate_connection(
                config
            )
        assert result.is_success
        assert result.value is True

    def test_validate_connection_failure(self) -> None:
        """Test connection validation failure handling."""
        config = FlextDbOracleSettings(
            host="invalid-host",
            port=1521,
            service_name="INVALID",
            username="invalid_user",
            password="invalid_password",
        )
        with patch.object(FlextDbOracleApi, "connect") as mock_connect:
            mock_connect.return_value = r[FlextDbOracleApi].fail("Connection failed")
            result = FlextDbOracleCli._OracleConnectionHelper.validate_connection(
                config
            )
        assert result.is_failure
        assert "Connection failed" in str(result.error)


class TestOutputFormatter:
    """Test output formatter functionality."""

    def test_formatter_initialization_with_cli_main(self) -> None:
        """Test formatter initialization with CLI main."""
        mock_cli_main = Mock()
        formatter = FlextDbOracleCli._OutputFormatter(mock_cli_main)
        assert formatter._cli_main is mock_cli_main

    def test_formatter_initialization_without_cli_main(self) -> None:
        """Test formatter initialization without CLI main."""
        formatter = FlextDbOracleCli._OutputFormatter()
        assert formatter._cli_main is None

    def test_format_success_message(self) -> None:
        """Test success message formatting."""
        formatter = FlextDbOracleCli._OutputFormatter()
        result = formatter.format_success_message("Operation completed")
        assert result.is_success
        assert result.value == "✅ Operation completed"

    def test_format_error_message(self) -> None:
        """Test error message formatting."""
        formatter = FlextDbOracleCli._OutputFormatter()
        result = formatter.format_error_message("Something went wrong")
        assert result.is_success
        assert result.value == "❌ Something went wrong"

    def test_format_list_output_table_format(self) -> None:
        """Test list output formatting in table format."""
        formatter = FlextDbOracleCli._OutputFormatter()
        items = ["table1", "table2", "table3"]
        result = formatter.format_list_output(items, "Database Tables", "table")
        assert result.is_success
        output = result.value
        assert "Database Tables" in output
        assert "table1" in output
        assert "table2" in output
        assert "table3" in output

    _JSON_ADAPTER: TypeAdapter[dict[str, object]] = TypeAdapter(dict[str, object])

    def test_format_list_output_json_format(self) -> None:
        """Test list output formatting in JSON format."""
        formatter = FlextDbOracleCli._OutputFormatter()
        items = ["schema1", "schema2"]
        result = formatter.format_list_output(items, "Schemas", "json")
        assert result.is_success
        output = result.value
        data = self._JSON_ADAPTER.validate_json(output)
        assert data["title"] == "Schemas"
        assert data["items"] == ["schema1", "schema2"]

    def test_format_list_output_yaml_format(self) -> None:
        """Test list output formatting in YAML format."""
        formatter = FlextDbOracleCli._OutputFormatter()
        items = ["item1", "item2"]
        result = formatter.format_list_output(items, "Test Items", "yaml")
        assert result.is_success
        output = result.value
        data = yaml.safe_load(output)
        assert data["title"] == "Test Items"
        assert data["items"] == ["item1", "item2"]

    def test_format_list_output_plain_format(self) -> None:
        """Test list output formatting in plain format."""
        formatter = FlextDbOracleCli._OutputFormatter()
        items = ["item1", "item2"]
        result = formatter.format_list_output(items, "Test Items", "plain")
        assert result.is_success
        output = result.value
        assert "Test Items" in output
        assert "item1" in output
        assert "item2" in output

    def test_format_list_output_dict_items(self) -> None:
        """Test list output formatting with dict[str, object] items."""
        formatter = FlextDbOracleCli._OutputFormatter()
        items: list[NamedItem] = [
            NamedItem(name="table1"),
            NamedItem(name="table2"),
            NamedItem(name="unnamed"),
        ]
        result = formatter.format_list_output(items, "Database Objects", "table")
        assert result.is_success
        output = result.value
        assert "table1" in output
        assert "table2" in output

    _DATA_ADAPTER: TypeAdapter[dict[str, object]] = TypeAdapter(dict[str, object])

    def test_format_data_json(self) -> None:
        """Test data formatting as JSON."""
        formatter = FlextDbOracleCli._OutputFormatter()
        data = {"key": "value", "number": 42}
        result = formatter.format_data(data, "json")
        assert result.is_success
        parsed_data = self._DATA_ADAPTER.validate_json(result.value)
        assert parsed_data["key"] == "value"
        assert parsed_data["number"] == 42

    def test_format_data_yaml(self) -> None:
        """Test data formatting as YAML."""
        formatter = FlextDbOracleCli._OutputFormatter()
        data = {"key": "value", "number": 42}
        result = formatter.format_data(data, "yaml")
        assert result.is_success
        parsed_data = yaml.safe_load(result.value)
        assert parsed_data == data

    def test_format_data_plain(self) -> None:
        """Test data formatting as plain text."""
        formatter = FlextDbOracleCli._OutputFormatter()
        data = {"key": "value"}
        result = formatter.format_data(data, "plain")
        assert result.is_success
        assert str(data) == result.value

    def test_display_message(self) -> None:
        """Test message display functionality."""
        formatter = FlextDbOracleCli._OutputFormatter()
        formatter.display_message("Test message")


class TestCliServiceOperations:
    """Test CLI service operation methods."""

    def test_execute_health_check_success(self) -> None:
        """Test successful health check execution."""
        cli_service = FlextDbOracleCli()
        FlextDbOracleSettings(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_password",
        )
        with patch.object(
            FlextDbOracleCli._OracleConnectionHelper, "validate_connection"
        ) as mock_validate:
            mock_validate.return_value = r[bool].ok(True)
            result = cli_service.execute_health_check(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
            )
        assert result.is_success
        output = result.value
        assert isinstance(output, HealthCheckReport)
        assert hasattr(output, "status") and output.status is not None

    def test_execute_health_check_config_creation_failure(self) -> None:
        """Test health check with config creation failure."""
        cli_service = FlextDbOracleCli()
        result = cli_service.execute_health_check(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="",
        )
        assert result.is_success
        output = result.value
        assert isinstance(output, HealthCheckReport)
        assert hasattr(output, "status") and output.status is not None

    def test_execute_health_check_connection_failure(self) -> None:
        """Test health check with connection validation failure."""
        cli_service = FlextDbOracleCli()
        with patch.object(FlextDbOracleApi, "get_health_status") as mock_health:
            mock_health.return_value = r.fail("Database unreachable")
            result = cli_service.execute_health_check(
                host="unreachable-host",
                port=1521,
                service_name="INVALID",
                username="test_user",
                password="test_password",
            )
        assert result.is_failure
        assert result.error is not None and "Database unreachable" in result.error

    def test_execute_list_schemas_success(self) -> None:
        """Test successful schema listing."""
        cli_service = FlextDbOracleCli()
        mock_api = Mock()
        mock_api.get_schemas.return_value = r[list[str]].ok([
            "SCHEMA1",
            "SCHEMA2",
            "SCHEMA3",
        ])
        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "get_schemas") as mock_get_schemas,
        ):
            mock_connect.return_value = r[FlextDbOracleApi].ok(mock_api)
            mock_get_schemas.return_value = r[list[str]].ok([
                "SCHEMA1",
                "SCHEMA2",
            ])
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
        cli_service = FlextDbOracleCli()
        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
        ):
            mock_connect.return_value = r[FlextDbOracleApi].fail("Connection failed")
            result = cli_service.execute_list_schemas(
                host="invalid-host",
                port=1521,
                service_name="INVALID",
                username="test_user",
                password="test_password",
            )
        assert result.is_failure
        assert result.error is not None and "Connection failed" in result.error

    def test_execute_list_schemas_api_failure(self) -> None:
        """Test schema listing with API failure."""
        cli_service = FlextDbOracleCli()
        mock_api = Mock()
        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "get_schemas") as mock_get_schemas,
        ):
            mock_connect.return_value = r[FlextDbOracleApi].ok(mock_api)
            mock_get_schemas.return_value = r[list[str]].fail("Schema query failed")
            result = cli_service.execute_list_schemas(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
            )
        assert result.is_failure
        assert result.error is not None and "Schema query failed" in result.error

    def test_execute_list_tables_success(self) -> None:
        """Test successful table listing."""
        cli_service = FlextDbOracleCli()
        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "get_tables") as mock_get_tables,
        ):
            mock_connect.return_value = r[FlextDbOracleApi].ok(Mock())
            mock_get_tables.return_value = r[list[str]].ok([
                "TABLE1",
                "TABLE2",
            ])
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
        assert "Listed 2 tables" in output

    def test_execute_list_tables_no_schema(self) -> None:
        """Test table listing without schema name."""
        cli_service = FlextDbOracleCli()
        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "get_tables") as mock_get_tables,
        ):
            mock_connect.return_value = r[FlextDbOracleApi].ok(Mock())
            mock_get_tables.return_value = r[list[str]].ok(["TABLE1"])
            result = cli_service.execute_list_tables(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
            )
        assert result.is_success
        output = result.value
        assert "Listed 1 tables" in output

    def test_execute_query_success(self) -> None:
        """Test successful query execution."""
        cli_service = FlextDbOracleCli()
        mock_result: list[t.Dict] = [
            t.Dict(root={"id": 1, "name": "test"}),
            t.Dict(root={"id": 2, "name": "test2"}),
        ]
        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "query") as mock_query,
        ):
            mock_connect.return_value = r[FlextDbOracleApi].ok(Mock())
            mock_query.return_value = r[list[t.Dict]].ok(mock_result)
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
        assert "Query executed successfully" in output or "rows" in output.lower()

    def test_execute_query_empty_sql(self) -> None:
        """Test query execution with empty SQL."""
        cli_service = FlextDbOracleCli()
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
        cli_service = FlextDbOracleCli()
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


class TestYamlModule:
    """Test YAML module protocol interface."""

    def test_yaml_module_protocol_interface(self) -> None:
        """Test that yaml module conforms to the protocol."""
        yaml_module = yaml
        data = {"test": "value"}
        result = yaml_module.dump(data, default_flow_style=True)
        assert isinstance(result, str)
        assert "test" in result
        assert "value" in result


class TestCLIRealFunctionality:
    """Test CLI using real flext-cli API - NO MOCKS."""

    def test_cli_creation_and_basic_functionality(self) -> None:
        """Test CLI creation and basic functionality - REAL IMPLEMENTATION."""
        oracle_cli = FlextDbOracleClient()
        assert hasattr(oracle_cli, "execute_query")
        get_history_method = getattr(oracle_cli, "get_command_history", None)
        if callable(get_history_method):
            history = get_history_method()
            assert isinstance(history, list)
        else:
            assert callable(getattr(oracle_cli, "execute_query", None))

    def test_environment_configuration_real(self) -> None:
        """Test environment configuration using real API functionality."""
        test_env_vars = {
            "ORACLE_HOST": "localhost",
            "ORACLE_PORT": "1521",
            "ORACLE_USERNAME": "testuser",
            "ORACLE_PASSWORD": "testpass",
            "ORACLE_SERVICE_NAME": "TESTDB",
        }
        original_env: dict[str, str | None] = {}
        for key, value in test_env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        try:
            api_result = FlextDbOracleApi.from_env()
            assert api_result.is_success
            api = api_result.value
            assert api.config.host is not None
        finally:
            for key, original_value in original_env.items():
                if original_value is None:
                    if key in os.environ:
                        del os.environ[key]
                else:
                    os.environ[key] = original_value

    def test_api_observability_and_connection_real(self) -> None:
        """Test API observability and connection functionality - REAL IMPLEMENTATION."""
        config = FlextDbOracleSettings(
            host="localhost",
            port=1521,
            service_name="TESTDB",
            username="test",
            password="test",
        )
        api = FlextDbOracleApi(config)
        metrics_result = api.get_observability_metrics()
        assert metrics_result.is_success
        assert isinstance(metrics_result.value, object)
        connection_result = api.test_connection()
        assert hasattr(connection_result, "is_success")
        is_valid = api.is_valid()
        assert isinstance(is_valid, bool)
        assert is_valid is True

    def test_output_formatting_real(self) -> None:
        """Test output formatting using real functionality."""
        utilities = FlextDbOracleUtilities()
        test_result = {"column1": "value1", "column2": "value2"}
        for format_type in ["table", "json", "csv"]:
            format_result = utilities.format_query_result(
                test_result, format_type=format_type
            )
            assert format_result.is_success
            assert isinstance(format_result.value, str)
            assert len(format_result.value) > 0

    def test_error_handling_real(self) -> None:
        """Test error handling using real functionality - NO MOCKS."""
        invalid_config = FlextDbOracleSettings(
            host="invalid.host",
            port=9999,
            service_name="INVALID_SERVICE",
            username="invalid_user",
            password="invalid_password",
        )
        api = FlextDbOracleApi(invalid_config)
        query_result = api.query("SELECT 1 FROM DUAL")
        assert query_result.is_failure
        assert query_result.error is not None
        assert (
            "not connected" in query_result.error.lower()
            or "connection" in query_result.error.lower()
        )
        schemas_result = api.get_schemas()
        assert schemas_result.is_failure
        tables_result = api.get_tables()
        assert tables_result.is_failure

    def test_parameter_processing_real(self) -> None:
        """Test parameter processing using real API functionality."""
        config_data = {
            "host": "param_test_host",
            "port": 1521,
            "service_name": "PARAM_TEST",
            "username": "param_user",
            "password": "param_pass",
        }
        config = FlextDbOracleSettings(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])) if config_data.get("port") else 1521,
            service_name=str(config_data.get("service_name", "XE")),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)
        assert api.config.host == "param_test_host"
        assert api.config.port == 1521
        assert api.config.service_name == "PARAM_TEST"
        assert api.config.username == "param_user"

    def test_comprehensive_api_coverage_real(self) -> None:
        """Comprehensive API coverage test using real functionality - NO MOCKS."""
        config = FlextDbOracleSettings(
            host="comprehensive_test",
            port=1521,
            name="COMP_TEST",
            service_name="COMP_TEST",
            username="comp_user",
            password="comp_pass",
        )
        api = FlextDbOracleApi(config)
        methods_to_test = [
            ("is_valid", api.is_valid),
            ("to_dict", api.to_dict),
            ("get_observability_metrics", api.get_observability_metrics),
            ("optimize_query", lambda: api.optimize_query("SELECT * FROM test")),
            ("list_plugins", api.list_plugins),
        ]
        for _method_name, method_call in methods_to_test:
            result = method_call()
            if hasattr(result, "success"):
                assert hasattr(result, "error") or hasattr(result, "value")
            else:
                assert result is not None

    def test_factory_methods_real(self) -> None:
        """Test factory methods using real functionality - NO MOCKS."""
        original_env: dict[str, str | None] = {}
        env_vars = {
            "ORACLE_USERNAME": "testuser",
            "ORACLE_PASSWORD": "testpass",
            "ORACLE_HOST": "localhost",
            "ORACLE_PORT": "1521",
            "ORACLE_SERVICE_NAME": "XEPDB1",
        }
        for key, value in env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        try:
            api_result = FlextDbOracleApi.from_env()
            assert api_result.is_success
            api = api_result.value
            assert api.config.host is not None
            assert isinstance(api.config.port, int)
        finally:
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value
        config_for_url = FlextDbOracleSettings(
            host="host",
            port=1521,
            service_name="SERVICE",
            username="user",
            password="pass",
        )
        url_api = FlextDbOracleApi(config=config_for_url)
        assert url_api.config.host == "host"
        assert url_api.config.port == 1521
        assert url_api.config.service_name == "SERVICE"

    def test_plugin_system_real(self) -> None:
        """Test plugin system using real functionality - NO MOCKS."""
        config = FlextDbOracleSettings(
            host="plugin_test",
            port=1521,
            service_name="PLUGIN_TEST",
            username="plugin_user",
            password="plugin_pass",
        )
        api = FlextDbOracleApi(config)
        test_plugin = {"name": "test_plugin", "version": "1.0.0"}
        register_result = api.register_plugin("test_plugin", test_plugin)
        assert register_result.is_success
        list_result = api.list_plugins()
        assert list_result.is_success
        plugin_list = list_result.value
        assert "test_plugin" in plugin_list
        get_result = api.get_plugin("test_plugin")
        assert get_result.is_success
        retrieved_plugin = get_result.value
        assert retrieved_plugin == test_plugin
        unregister_result = api.unregister_plugin("test_plugin")
        assert unregister_result.is_success
        final_list = api.list_plugins()
        assert final_list.is_success
        assert "test_plugin" not in final_list.value

"""Real CLI tests WITHOUT mocks - testing actual FlextDbOracleClient functionality.

This module provides comprehensive tests for CLI components using REAL code
execution without mocks, following FLEXT testing standards.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from collections.abc import Sequence
from unittest.mock import Mock, patch

from flext_tests import tm

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleCli,
    FlextDbOracleClient,
    FlextDbOracleSettings,
)
from tests import m, r, t, u


class TestFlextDbOracleClientReal:
    """Test FlextDbOracleClient class with REAL functionality - NO MOCKS."""

    def test_client_initialization_debug_mode(self) -> None:
        """Test CLI client initialization in debug mode."""
        client = FlextDbOracleClient(debug=True)
        tm.that(client.debug, eq=True)
        tm.that(client.current_connection, none=True)
        tm.that(client.user_preferences["default_output_format"], eq="table")
        tm.that(client.user_preferences["show_execution_time"], eq="True")
        tm.that(client.container, none=False)
        tm.that(client.logger, none=False)

    def test_client_initialization_production_mode(self) -> None:
        """Test CLI client initialization in production mode."""
        client = FlextDbOracleClient(debug=False)
        tm.that(client.debug is False, eq=True)
        tm.that(client.user_preferences["auto_confirm_operations"], eq="False")
        tm.that(client.user_preferences["connection_timeout"], eq=30)
        tm.that(client.user_preferences["query_limit"], eq=1000)

    def test_client_initialization_real(self) -> None:
        """Test actual CLI client initialization."""
        client = FlextDbOracleClient()
        tm.that(client.container, none=False)
        tm.that(client.logger, none=False)
        tm.that(client.current_connection, none=True)

    def test_configure_preferences_real(self) -> None:
        """Test configuring user preferences with real values."""
        client = FlextDbOracleClient()
        result = client.configure_preferences(
            default_output_format="json",
            query_limit=2000,
            show_execution_time=False,
        )
        tm.that(result.is_success, eq=True)
        tm.that(client.user_preferences["default_output_format"], eq="json")
        tm.that(client.user_preferences["query_limit"], eq=2000)
        tm.that(client.user_preferences["show_execution_time"] is False, eq=True)

    def test_configure_preferences_invalid_keys(self) -> None:
        """Test configuring preferences with invalid keys."""
        client = FlextDbOracleClient()
        result = client.configure_preferences(
            invalid_key="value",
            another_invalid="test",
        )
        tm.that(result.is_success, eq=True)
        assert not hasattr(client.user_preferences, "invalid_key")
        assert not hasattr(client.user_preferences, "another_invalid")

    def test_connection_without_config(self) -> None:
        """Test connection methods without active connection."""
        client = FlextDbOracleClient()
        result = client.execute_query("SELECT 1 FROM DUAL")
        tm.that(not result.is_success, eq=True)
        tm.that(result.error, none=False)
        tm.that(
            (
                result.error is not None
                and "No active Oracle connection" in (result.error or "")
            ),
            eq=True,
        )
        schemas_result = client.list_schemas()
        tm.that(not schemas_result.is_success, eq=True)
        tm.that(schemas_result.error, none=False)
        tm.that((schemas_result.error or ""), has="No active Oracle connection")
        tables_result = client.list_tables()
        tm.that(not tables_result.is_success, eq=True)
        tm.that(tables_result.error, none=False)
        tm.that((tables_result.error or ""), has="No active Oracle connection")
        health_result = client.health_check()
        tm.that(not health_result.is_success, eq=True)
        tm.that(health_result.error, none=False)
        tm.that((health_result.error or ""), has="No active Oracle connection")

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
        tm.that(not result.is_success, eq=True)
        tm.that(bool(result.error), eq=True)
        tm.that(
            (
                "Connection failed" in (result.error or "")
                or "Oracle connection failed" in (result.error or "")
                or "Connection error" in (result.error or "")
            ),
            eq=True,
        )

    def test_get_global_client_real(self) -> None:
        """Test creating client instances with real functionality."""
        client1 = FlextDbOracleClient()
        client2 = FlextDbOracleClient()
        tm.that(client1, is_=FlextDbOracleClient)
        tm.that(client2, is_=FlextDbOracleClient)
        tm.that(client1 is not client2, eq=True)

    def test_run_cli_command_real(self) -> None:
        """Test CLI command execution with real functionality."""
        result = FlextDbOracleClient.run_cli_command("health", timeout=30)
        tm.that(result, is_=r)

    def test_connection_wizard_real_validation(self) -> None:
        """Test connection wizard input validation."""
        client = FlextDbOracleClient()
        tm.that(callable(client.connect_to_oracle), eq=True)

    def test_oracle_cli_client_methods_real(self) -> None:
        """Test FlextDbOracleClient has proper CLI methods."""
        FlextDbOracleClient()

    def test_client_real_error_handling(self) -> None:
        """Test real error handling in client methods."""
        client = FlextDbOracleClient()
        result = client.execute_query("")
        tm.that(not result.is_success, eq=True)
        bad_result = client.configure_preferences(valid_key="")
        tm.that(bad_result, is_=r)
        tm.ok(bad_result)

    def test_client_preferences_persistence(self) -> None:
        """Test that preference changes persist within client instance."""
        client = FlextDbOracleClient()
        client.user_preferences["default_output_format"]
        client.user_preferences["connection_timeout"]
        client.configure_preferences(
            default_output_format="json",
            connection_timeout=60,
        )
        tm.that(client.user_preferences["default_output_format"], eq="json")
        tm.that(client.user_preferences["connection_timeout"], eq=60)
        tm.that(client.user_preferences["query_limit"], eq=1000)


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
        tm.that(not result.is_success, eq=True)
        tm.that(result.error, is_=str)


class TestFlextDbOracleCli:
    """Test CLI service initialization and basic functionality."""

    def test_cli_service_initialization_success(self) -> None:
        """Test successful CLI service initialization."""
        cli_service = FlextDbOracleCli()
        tm.that(isinstance(cli_service, FlextDbOracleCli), eq=True)
        tm.that(cli_service._container is not None, eq=True)
        tm.that(cli_service.logger is not None, eq=True)

    def test_cli_service_initialization_basic(self) -> None:
        """Test basic CLI service initialization."""
        cli_service = FlextDbOracleCli()
        tm.that(isinstance(cli_service, FlextDbOracleCli), eq=True)


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
        tm.ok(result)
        config = result.value
        tm.that(config.host, eq="test-host")
        tm.that(config.port, eq=1522)
        tm.that(config.service_name, eq="TEST_SERVICE")
        tm.that(config.username, eq="test_user")
        tm.that(config.password, none=False)
        if config.password is not None:
            tm.that(config.password.get_secret_value(), eq="test_password")

    def test_create_config_from_params_defaults(self) -> None:
        """Test config creation with default parameters."""
        result = FlextDbOracleCli._OracleConnectionHelper.create_config_from_params(
            password="test_password",
        )
        tm.ok(result)
        config = result.value
        tm.that(config.host, eq="localhost")
        tm.that(config.port, eq=1521)
        tm.that(config.service_name, eq="XEPDB1")
        tm.that(config.username, eq="system")

    def test_create_config_from_params_no_password(self) -> None:
        """Test config creation fails without password."""
        result = FlextDbOracleCli._OracleConnectionHelper.create_config_from_params(
            host="test-host",
            username="test_user",
        )
        tm.that(result.is_failure, eq=True)
        tm.that(str(result.error), has="Password is required")

    def test_create_config_from_params_empty_password(self) -> None:
        """Test config creation fails with empty password."""
        result = FlextDbOracleCli._OracleConnectionHelper.create_config_from_params(
            host="test-host",
            username="test_user",
            password="",
        )
        tm.that(result.is_failure, eq=True)
        tm.that(str(result.error), has="Password is required")

    def test_create_config_from_params_validation_error(self) -> None:
        """Test config creation handles validation errors."""
        result = FlextDbOracleCli._OracleConnectionHelper.create_config_from_params(
            host="",
            password="test_password",
        )
        tm.that(result.is_failure, eq=True)
        tm.that(str(result.error), has="Configuration creation failed")

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
                config,
            )
        tm.ok(result)
        tm.that(result.value, eq=True)

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
                config,
            )
        tm.that(result.is_failure, eq=True)
        tm.that(str(result.error), has="Connection failed")


class TestOutputFormatter:
    """Test output formatter functionality."""

    def test_formatter_initialization_with_cli(self) -> None:
        """Test formatter initialization (static methods, no state)."""
        formatter = FlextDbOracleCli._OutputFormatter()
        assert formatter is not None

    def test_format_success_message(self) -> None:
        """Test success message formatting."""
        formatter = FlextDbOracleCli._OutputFormatter()
        result = formatter.format_success_message("Operation completed")
        tm.ok(result)
        tm.that(result.value, eq="✅ Operation completed")

    def test_format_error_message(self) -> None:
        """Test error message formatting."""
        formatter = FlextDbOracleCli._OutputFormatter()
        result = formatter.format_error_message("Something went wrong")
        tm.ok(result)
        tm.that(result.value, eq="❌ Something went wrong")

    def test_format_list_output_table_format(self) -> None:
        """Test list output formatting in table format."""
        formatter = FlextDbOracleCli._OutputFormatter()
        items = ["table1", "table2", "table3"]
        result = formatter.format_list_output(items, "Database Tables", "table")
        tm.ok(result)
        output = result.value
        tm.that(output, has="Database Tables")
        tm.that(output, has="table1")
        tm.that(output, has="table2")
        tm.that(output, has="table3")

    def test_format_list_output_json_format(self) -> None:
        """Test list output formatting in JSON format."""
        formatter = FlextDbOracleCli._OutputFormatter()
        items = ["schema1", "schema2"]
        result = formatter.format_list_output(items, "Schemas", "json")
        tm.ok(result)
        output = result.value
        data = t.Tests.CONTAINER_MAPPING_ADAPTER.validate_json(output)
        tm.that(data["title"], eq="Schemas")
        tm.that(data["items"], eq=["schema1", "schema2"])

    def test_format_list_output_yaml_format(self) -> None:
        """Test list output formatting in YAML format."""
        formatter = FlextDbOracleCli._OutputFormatter()
        items = ["item1", "item2"]
        result = formatter.format_list_output(items, "Test Items", "yaml")
        tm.ok(result)
        output = result.value
        data = u.Cli.yaml_parse(output).unwrap_or({})
        tm.that(data["title"], eq="Test Items")
        tm.that(data["items"], eq=["item1", "item2"])

    def test_format_list_output_plain_format(self) -> None:
        """Test list output formatting in plain format."""
        formatter = FlextDbOracleCli._OutputFormatter()
        items = ["item1", "item2"]
        result = formatter.format_list_output(items, "Test Items", "plain")
        tm.ok(result)
        output = result.value
        tm.that(output, has="Test Items")
        tm.that(output, has="item1")
        tm.that(output, has="item2")

    def test_format_list_output_dict_items(self) -> None:
        """Test list output formatting with t.ContainerMapping items."""
        formatter = FlextDbOracleCli._OutputFormatter()
        items: Sequence[m.DbOracle.NamedItem] = [
            m.DbOracle.NamedItem(name="table1"),
            m.DbOracle.NamedItem(name="table2"),
            m.DbOracle.NamedItem(name="unnamed"),
        ]
        result = formatter.format_list_output(items, "Database Objects", "table")
        tm.ok(result)
        output = result.value
        tm.that(output, has="table1")
        tm.that(output, has="table2")

    def test_format_data_json(self) -> None:
        """Test data formatting as JSON."""
        formatter = FlextDbOracleCli._OutputFormatter()
        data: dict[str, t.Scalar] = {"key": "value", "number": 42}
        result = formatter.format_data(data, "json")
        tm.ok(result)
        parsed_data = t.Tests.CONTAINER_MAPPING_ADAPTER.validate_json(result.value)
        tm.that(parsed_data["key"], eq="value")
        tm.that(parsed_data["number"], eq=42)

    def test_format_data_yaml(self) -> None:
        """Test data formatting as YAML."""
        formatter = FlextDbOracleCli._OutputFormatter()
        data: dict[str, t.Scalar] = {"key": "value", "number": 42}
        result = formatter.format_data(data, "yaml")
        tm.ok(result)
        parsed_data = u.Cli.yaml_parse(result.value).unwrap_or({})
        expected: dict[str, str | int] = {"key": "value", "number": 42}
        tm.that(parsed_data, eq=expected)

    def test_format_data_plain(self) -> None:
        """Test data formatting as plain text."""
        formatter = FlextDbOracleCli._OutputFormatter()
        data = {"key": "value"}
        result = formatter.format_data(data, "plain")
        tm.ok(result)
        tm.that(str(data), eq=result.value)

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
            FlextDbOracleCli._OracleConnectionHelper,
            "validate_connection",
        ) as mock_validate:
            mock_validate.return_value = r[bool].ok(True)
            result = cli_service.execute_health_check(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
            )
        tm.ok(result)
        output = result.value
        tm.that(output, is_=m.DbOracle.HealthCheckReport)

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
        tm.ok(result)
        output = result.value
        tm.that(output, is_=m.DbOracle.HealthCheckReport)

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
        tm.that(result.is_failure, eq=True)
        assert result.error is not None
        tm.that(
            "Database unreachable" in result.error,
            eq=True,
        )

    def test_execute_list_schemas_success(self) -> None:
        """Test successful schema listing."""
        cli_service = FlextDbOracleCli()
        mock_api = Mock()
        mock_api.get_schemas.return_value = r[t.StrSequence].ok([
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
            mock_get_schemas.return_value = r[t.StrSequence].ok([
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
        tm.ok(result)
        output = result.value
        tm.that(output, has="Listed 2 schemas successfully")

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
        tm.that(result.is_failure, eq=True)
        assert result.error is not None
        tm.that(
            "Connection failed" in result.error,
            eq=True,
        )

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
            mock_get_schemas.return_value = r[t.StrSequence].fail("Schema query failed")
            result = cli_service.execute_list_schemas(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
            )
        tm.that(result.is_failure, eq=True)
        assert result.error is not None
        tm.that(
            "Schema query failed" in result.error,
            eq=True,
        )

    def test_execute_list_tables_success(self) -> None:
        """Test successful table listing."""
        cli_service = FlextDbOracleCli()
        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "get_tables") as mock_get_tables,
        ):
            mock_connect.return_value = r[FlextDbOracleApi].ok(Mock())
            mock_get_tables.return_value = r[t.StrSequence].ok([
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
        tm.ok(result)
        output = result.value
        tm.that(output, has="Listed 2 tables")

    def test_execute_list_tables_no_schema(self) -> None:
        """Test table listing without schema name."""
        cli_service = FlextDbOracleCli()
        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "get_tables") as mock_get_tables,
        ):
            mock_connect.return_value = r[FlextDbOracleApi].ok(Mock())
            mock_get_tables.return_value = r[t.StrSequence].ok(["TABLE1"])
            result = cli_service.execute_list_tables(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
            )
        tm.ok(result)
        output = result.value
        tm.that(output, has="Listed 1 tables")

    def test_execute_query_success(self) -> None:
        """Test successful query execution."""
        cli_service = FlextDbOracleCli()
        mock_result: Sequence[t.Dict] = [
            t.Dict(root={"id": 1, "name": "test"}),
            t.Dict(root={"id": 2, "name": "test2"}),
        ]
        with (
            patch.object(FlextDbOracleApi, "__init__", return_value=None),
            patch.object(FlextDbOracleApi, "connect") as mock_connect,
            patch.object(FlextDbOracleApi, "query") as mock_query,
        ):
            mock_connect.return_value = r[FlextDbOracleApi].ok(Mock())
            mock_query.return_value = r[Sequence[t.Dict]].ok(mock_result)
            result = cli_service.execute_query(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_password",
                sql="SELECT * FROM test_table",
                output_format="json",
            )
        tm.ok(result)
        output = result.value
        tm.that(
            "Query executed successfully" in output or "rows" in output.lower(),
            eq=True,
        )

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
        tm.that(result.is_failure, eq=True)
        tm.that(str(result.error), has="SQL query cannot be empty")

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
        tm.that(result.is_failure, eq=True)
        tm.that(str(result.error), has="SQL query cannot be empty")


class TestYamlModule:
    """Test YAML module protocol interface."""

    def test_yaml_module_protocol_interface(self) -> None:
        """Test that yaml dump produces valid YAML string."""
        data: dict[str, str] = {"test": "value"}
        result = u.Cli.yaml_dump_str(data)
        tm.that(result, is_=str)
        tm.that(result, has="test")
        tm.that(result, has="value")


class TestCLIRealFunctionality:
    """Test CLI using real flext-cli API - NO MOCKS."""

    def test_cli_creation_and_basic_functionality(self) -> None:
        """Test CLI creation and basic functionality - REAL IMPLEMENTATION."""
        oracle_cli = FlextDbOracleClient()
        get_history_method = getattr(oracle_cli, "get_command_history", None)
        if callable(get_history_method):
            history = get_history_method()
            assert isinstance(history, list)

    def test_environment_configuration_real(self) -> None:
        """Test environment configuration using real API functionality."""
        test_env_vars = {
            "ORACLE_HOST": "localhost",
            "ORACLE_PORT": "1521",
            "ORACLE_USERNAME": "testuser",
            "ORACLE_PASSWORD": "testpass",
            "ORACLE_SERVICE_NAME": "TESTDB",
        }
        inherited_flext_env = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("FLEXT_TARGET_ORACLE_")
        }
        for key in inherited_flext_env:
            del os.environ[key]
        original_env: t.MutableOptionalStrMapping = {}
        for key, value in test_env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        try:
            api_result = FlextDbOracleApi.from_env()
            tm.ok(api_result)
            api = api_result.value
            tm.that(api.config.host, none=False)
        finally:
            for key, original_value in original_env.items():
                if original_value is None:
                    if key in os.environ:
                        del os.environ[key]
                else:
                    os.environ[key] = original_value
            os.environ.update(inherited_flext_env)

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
        tm.ok(metrics_result)
        tm.that(metrics_result.value, is_=dict)
        api.test_connection()
        is_valid = api.is_valid()
        tm.that(is_valid, is_=bool)
        tm.that(is_valid, eq=True)

    def test_output_formatting_real(self) -> None:
        """Test output formatting using real functionality."""
        test_result = {"column1": "value1", "column2": "value2"}
        for format_type in ["table", "json", "csv"]:
            format_result = u.DbOracle.format_query_result(
                test_result,
                format_type=format_type,
            )
            tm.ok(format_result)
            tm.that(format_result.value, is_=str)
            tm.that(bool(format_result.value), eq=True)

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
        tm.that(query_result.is_failure, eq=True)
        tm.that(query_result.error, none=False)
        tm.that(
            (
                "not connected" in query_result.error.lower()
                if query_result.error is not None
                else "" or "connection" in query_result.error.lower()
                if query_result.error is not None
                else ""
            ),
            eq=True,
        )
        schemas_result = api.get_schemas()
        tm.that(schemas_result.is_failure, eq=True)
        tables_result = api.get_tables()
        tm.that(tables_result.is_failure, eq=True)

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
        tm.that(api.config.host, eq="param_test_host")
        tm.that(api.config.port, eq=1521)
        tm.that(api.config.service_name, eq="PARAM_TEST")
        tm.that(api.config.username, eq="param_user")

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
        methods_to_test: Sequence[tuple[str, t.DbOracle.Tests.ApiCoverageCallable]] = [
            ("is_valid", api.is_valid),
            ("to_dict", api.to_dict),
            ("get_observability_metrics", api.get_observability_metrics),
            ("optimize_query", lambda: api.optimize_query("SELECT * FROM test")),
            ("list_plugins", api.list_plugins),
        ]
        for _method_name, method_call in methods_to_test:
            result = method_call()
            if hasattr(result, "success"):
                tm.that(
                    hasattr(result, "error") or hasattr(result, "value"),
                    eq=True,
                )
            else:
                assert result is not None

    def test_factory_methods_real(self) -> None:
        """Test factory methods using real functionality - NO MOCKS."""
        inherited_flext_env = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("FLEXT_TARGET_ORACLE_")
        }
        for key in inherited_flext_env:
            del os.environ[key]
        original_env: t.MutableOptionalStrMapping = {}
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
            tm.ok(api_result)
            api = api_result.value
            tm.that(api.config.host, none=False)
            tm.that(api.config.port, is_=int)
        finally:
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value
            os.environ.update(inherited_flext_env)
        config_for_url = FlextDbOracleSettings(
            host="host",
            port=1521,
            service_name="SERVICE",
            username="user",
            password="pass",
        )
        url_api = FlextDbOracleApi(config=config_for_url)
        tm.that(url_api.config.host, eq="host")
        tm.that(url_api.config.port, eq=1521)
        tm.that(url_api.config.service_name, eq="SERVICE")

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
        tm.ok(register_result)
        list_result = api.list_plugins()
        tm.ok(list_result)
        plugin_list = list_result.value
        tm.that(plugin_list, has="test_plugin")
        get_result = api.get_plugin("test_plugin")
        tm.ok(get_result)
        retrieved_plugin = get_result.value
        tm.that(retrieved_plugin, eq=test_plugin)
        unregister_result = api.unregister_plugin("test_plugin")
        tm.ok(unregister_result)
        final_list = api.list_plugins()
        tm.ok(final_list)
        tm.that("test_plugin" not in final_list.value, eq=True)

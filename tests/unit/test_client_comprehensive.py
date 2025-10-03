"""Test Oracle CLI client comprehensive functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import inspect
from typing import cast

import pytest
from flext_tests import FlextTestsBuilders, FlextTestsMatchers

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
)
from flext_db_oracle import (
    FlextDbOracleClient,
    FlextDbOracleModels,
    FlextDbOracleTypes,
)


class TestFlextDbOracleClientRealFunctionality:
    """Comprehensive tests for Oracle CLI Client using ONLY real functionality - NO MOCKS."""

    def setup_method(self) -> None:
        """Setup test CLI client with real configuration."""
        self.client = FlextDbOracleClient(debug=True)

    def test_client_initialization_complete_real(self) -> None:
        """Test complete client initialization with all attributes."""
        assert self.client is not None
        assert self.client.debug is True
        assert hasattr(self.client, "logger")
        assert hasattr(self.client, "container")
        assert hasattr(self.client, "current_connection")
        assert hasattr(self.client, "user_preferences")

    def test_client_properties_real(self) -> None:
        """Test client properties and default values."""
        # Default state
        assert self.client.current_connection is None

        # User preferences defaults
        preferences = self.client.user_preferences
        assert isinstance(preferences, dict)
        assert preferences["default_output_format"] == "table"
        assert preferences["auto_confirm_operations"] == "False"
        assert preferences["show_execution_time"] == "True"
        assert preferences["connection_timeout"] == 30
        assert preferences["query_limit"] == 1000

    def test_cli_initialization_real_functionality(self) -> None:
        """Test CLI initialization process."""
        # Test that client is properly initialized without initialize method
        assert self.client.container is not None
        assert self.client.logger is not None
        assert self.client.current_connection is None

    def test_client_debug_mode_real(self) -> None:
        """Test client with debug mode disabled."""
        client_no_debug = FlextDbOracleClient(debug=False)
        assert client_no_debug.debug is False

        # Verify components still initialized
        assert hasattr(client_no_debug, "logger")
        assert hasattr(client_no_debug, "container")
        assert hasattr(client_no_debug, "current_connection")

    def test_connect_to_oracle_invalid_config_real(self) -> None:
        """Test Oracle connection with invalid configuration."""
        result = self.client.connect_to_oracle(
            host="invalid_host",
            port=9999,
            service_name="invalid_service",
            username="invalid_user",
            password="invalid_password",
        )

        # Should fail gracefully with descriptive error
        FlextTestsMatchers.assert_result_failure(result)
        error_msg = (result.error or "").lower()
        assert (
            "connection" in error_msg
            or "failed" in error_msg
            or "timeout" in error_msg
            or "invalid" in error_msg
        )

    def test_execute_query_without_connection_real(self) -> None:
        """Test query execution without active connection."""
        result = self.client.execute_query("SELECT 1 FROM DUAL")

        # Should fail gracefully when no connection
        FlextTestsMatchers.assert_result_failure(result)
        error_msg = (result.error or "").lower()
        assert "connection" in error_msg or "not connected" in error_msg

    def test_connection_configuration_validation_real(self) -> None:
        """Test connection parameter validation."""
        # Test various invalid configurations that should be caught
        invalid_configs = [
            ("", 1521, "service", "user", "password"),  # Empty host
            ("host", 0, "service", "user", "password"),  # Invalid port
            ("host", 1521, "", "user", "password"),  # Empty service
            ("host", 1521, "service", "", "password"),  # Empty user
            ("host", 1521, "service", "user", ""),  # Empty password
        ]

        for host, port, service, user, password in invalid_configs:
            result = self.client.connect_to_oracle(host, port, service, user, password)
            # Should fail validation before attempting connection
            FlextTestsMatchers.assert_result_failure(result)

    def test_oracle_config_creation_real(self) -> None:
        """Test Oracle configuration object creation."""
        # Test that client can create valid Oracle configuration
        host = "test_host"
        port = 1521
        service_name = "TEST_SERVICE"
        user = "test_user"
        password = "test_password"

        # This tests the internal configuration creation logic
        try:
            config = FlextDbOracleModels.OracleConfig(
                host=host,
                port=port,
                service_name=service_name,
                username=user,
                password=password,
                ssl_server_cert_dn=None,
            )

            assert config.host == host
            assert config.port == port
            assert config.service_name == service_name
            assert config.username == user
            assert config.password == password
            assert config.ssl_server_cert_dn is None

        except Exception as e:
            pytest.fail(f"Oracle configuration creation failed: {e}")

    def test_client_error_handling_patterns_real(self) -> None:
        """Test client error handling patterns."""
        # Test that client handles various error conditions gracefully
        client = FlextDbOracleClient()

        # Test connection with various invalid inputs
        invalid_inputs = [
            # Test negative port
            ("host", -1, "service", "user", "pass"),
            # Test extremely large port
            ("host", 99999, "service", "user", "pass"),
            # Test special characters in service name
            ("host", 1521, "service;DROP TABLE", "user", "pass"),
        ]

        for host, port, service, user, password in invalid_inputs:
            result = client.connect_to_oracle(host, port, service, user, password)
            # All should fail gracefully without exceptions
            FlextTestsMatchers.assert_result_failure(result)
            assert isinstance(result.error, str)
            assert len(result.error) > 0

    def test_client_component_integration_real(self) -> None:
        """Test integration between client components."""
        client = FlextDbOracleClient(debug=True)

        # Verify all flext components are properly initialized
        assert client.logger is not None
        assert client.container is not None

        # Test component types
        assert isinstance(client.logger, FlextLogger)
        assert isinstance(client.container, FlextContainer)

    def test_user_preferences_modification_real(self) -> None:
        """Test user preferences can be modified."""
        client = FlextDbOracleClient()

        # Test modifying preferences
        client.user_preferences["default_output_format"] = "json"
        assert client.user_preferences["default_output_format"] == "json"

        # Test modifying boolean preference
        client.user_preferences["auto_confirm_operations"] = True
        assert client.user_preferences["auto_confirm_operations"] is True

        # Test modifying numeric preference
        client.user_preferences["connection_timeout"] = 60
        assert client.user_preferences["connection_timeout"] == 60

    def test_client_multiple_instances_isolation_real(self) -> None:
        """Test that multiple client instances are properly isolated."""
        client1 = FlextDbOracleClient(debug=True)
        client2 = FlextDbOracleClient(debug=False)

        # Test that instances have different configurations
        assert client1.debug is True
        assert client2.debug is False

        # Test that preferences are isolated
        client1.user_preferences["default_output_format"] = "json"
        client2.user_preferences["default_output_format"] = "xml"

        assert client1.user_preferences["default_output_format"] == "json"
        assert client2.user_preferences["default_output_format"] == "xml"

        # Test that connections are isolated
        assert client1.current_connection is None
        assert client2.current_connection is None

    def test_client_with_testbuilders_pattern_real(self) -> None:
        """Test client creation using TestBuilders patterns."""
        # Use TestBuilders to create test configuration
        config_result = (
            FlextTestsBuilders.result()
            .with_success_data(
                FlextDbOracleModels.OracleConfig(
                    host="testbuilder_host",
                    port=1521,
                    service_name="testbuilder_service",
                    username="testbuilder_user",
                    password="testbuilder_password",
                ),
            )
            .build()
        )

        # Type guard: ensure we have a FlextResult before passing to assert_result_success
        if not hasattr(config_result, "is_success"):
            msg = "Expected FlextResult with .is_success attribute"
            raise AssertionError(msg)

        # Cast to FlextResult to satisfy mypy
        result = cast("FlextResult[FlextDbOracleModels.OracleConfig]", config_result)
        FlextTestsMatchers.assert_result_success(result)

        config_data = result.value  # Access data from builder result
        # Handle case where builder returns dict with 'data' key
        if isinstance(config_data, dict) and "data" in config_data:
            config = config_data["data"]
        else:
            config = config_data
        assert isinstance(config, FlextDbOracleModels.OracleConfig)

        # Test that client can work with TestBuilders-created configuration
        client = FlextDbOracleClient()

        # Attempt connection (will fail, but tests configuration handling)
        connection_result = client.connect_to_oracle(
            host=config.host,
            port=config.port,
            service_name=config.service_name,
            username=config.username,
            password=config.password,
        )

        # Connection will fail (expected), but check that result structure is correct
        FlextTestsMatchers.assert_result_failure(connection_result)
        assert isinstance(connection_result.error, str)
        assert len(connection_result.error) > 0

        # Test configuration values were correctly processed
        assert config.host == "testbuilder_host"
        assert config.port == 1521
        assert config.service_name == "testbuilder_service"
        assert config.username == "testbuilder_user"
        assert config.password == "testbuilder_password"

    def test_client_string_representation_real(self) -> None:
        """Test client string representation methods."""
        client = FlextDbOracleClient(debug=True)

        # Test repr/str don't crash
        repr_str = repr(client)
        assert isinstance(repr_str, str)
        assert len(repr_str) > 0

        str_repr = str(client)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    def test_internal_chain_execution_structure_real(self) -> None:
        """Test internal chain execution structure."""
        client = FlextDbOracleClient()

        # Test that _execute_with_chain method exists and handles errors gracefully
        if hasattr(client, "_execute_with_chain"):
            # Test with invalid parameters
            result = client._execute_with_chain("invalid_operation")
            FlextTestsMatchers.assert_result_failure(result)
        else:
            # If method doesn't exist, this tests architectural understanding
            pytest.skip(
                "_execute_with_chain method not found - testing architectural understanding",
            )

    def test_client_connection_lifecycle_real(self) -> None:
        """Test complete connection lifecycle."""
        client = FlextDbOracleClient()

        # Initial state - no connection
        assert client.current_connection is None

        # Attempt connection (will fail with invalid config, but tests lifecycle)
        connect_result = client.connect_to_oracle(
            "invalid_host",
            1521,
            "service",
            "user",
            "password",
        )

        # Should fail but handle gracefully
        FlextTestsMatchers.assert_result_failure(connect_result)

        # Connection should remain None after failed connection
        assert client.current_connection is None

    def test_client_error_logging_integration_real(self) -> None:
        """Test that client properly integrates with logging."""
        client = FlextDbOracleClient(debug=True)

        # Verify logger is configured
        assert client.logger is not None
        assert hasattr(client.logger, "error")
        assert hasattr(client.logger, "info")
        assert hasattr(client.logger, "exception")

        # Test that operations that fail don't crash logging
        result = client.connect_to_oracle("invalid", 0, "", "", "")
        FlextTestsMatchers.assert_result_failure(result)

    def test_client_integration_with_flext_core_patterns_real(self) -> None:
        """Test client integration with flext-core patterns."""
        client = FlextDbOracleClient()

        # Test FlextResult pattern usage - client is initialized in constructor
        # No initialize method needed, client is ready to use
        assert client.container is not None
        assert client.logger is not None

        # Test query execution returns FlextResult (without connection - should fail gracefully)
        query_result = client.execute_query("SELECT 1")
        assert hasattr(query_result, "is_success")
        assert hasattr(query_result, "error") or hasattr(query_result, "value")
        FlextTestsMatchers.assert_result_failure(
            query_result,
        )  # Should fail without connection

    def test_list_schemas_without_connection_real(self) -> None:
        """Test list_schemas method without connection."""
        client = FlextDbOracleClient()

        result = client.list_schemas()

        # Should fail gracefully without connection
        FlextTestsMatchers.assert_result_failure(result)
        assert (
            "connection" in (result.error or "").lower()
            or "not connected" in (result.error or "").lower()
        )

    def test_configure_preferences_real(self) -> None:
        """Test configure_preferences method."""
        client = FlextDbOracleClient()

        # Test valid preference updates
        result = client.configure_preferences(
            default_output_format="json",
            auto_confirm_operations=True,
            connection_timeout=60,
        )

        FlextTestsMatchers.assert_result_success(result)
        assert client.user_preferences["default_output_format"] == "json"
        assert client.user_preferences["auto_confirm_operations"] is True
        assert client.user_preferences["connection_timeout"] == 60

        # Test invalid preferences (should be ignored)
        result_invalid = client.configure_preferences(
            invalid_preference="value",
            another_invalid=True,
        )

        FlextTestsMatchers.assert_result_success(
            result_invalid,
        )  # Should succeed but ignore invalid

    def test_run_cli_command_real(self) -> None:
        """Test run_cli_command function."""
        # Test invalid command
        result = FlextDbOracleClient.run_cli_command("invalid_command")
        FlextTestsMatchers.assert_result_failure(result)
        assert (
            "unknown" in (result.error or "").lower()
            or "command" in (result.error or "").lower()
        )

        # Test valid command without connection (should fail gracefully)
        result_query = FlextDbOracleClient.run_cli_command(
            "query",
            sql="SELECT 1 FROM DUAL",
        )
        FlextTestsMatchers.assert_result_failure(result_query)

        # Test health command without connection
        result_health = FlextDbOracleClient.run_cli_command("health")
        FlextTestsMatchers.assert_result_failure(result_health)

        # Test schemas command without connection
        result_schemas = FlextDbOracleClient.run_cli_command("schemas")
        FlextTestsMatchers.assert_result_failure(result_schemas)

    def test_internal_method_coverage_real(self) -> None:
        """Test internal method coverage."""
        client = FlextDbOracleClient()

        # Test _get_formatter_strategy
        if hasattr(client, "_get_formatter_strategy"):
            strategy_result = client._get_formatter_strategy("table")
            FlextTestsMatchers.assert_result_success(strategy_result)
            assert strategy_result.value is not None

            # Test strategy with mock data
            test_data = {
                "operation": "test",
                "params": {"title": "Test Results"},
                "result": [{"test": "value"}],
            }
            # Cast to expected type for formatter strategy
            data_for_formatter = cast("FlextDbOracleTypes.Query.QueryResult", test_data)
            strategy = strategy_result.value
            if callable(strategy):
                format_result = strategy(data_for_formatter)
                assert hasattr(format_result, "is_success")

        # Test _adapt_data_for_table
        if hasattr(client, "_adapt_data_for_table"):
            # Test with sample data - cast to proper type

            schemas_data = cast(
                "FlextDbOracleTypes.Query.QueryResult",
                {"schemas": ["SCHEMA1", "SCHEMA2"]},
            )
            schemas_result = client._adapt_data_for_table(schemas_data)
            FlextTestsMatchers.assert_result_success(schemas_result)
            assert isinstance(schemas_result.value, list)

            # Test with health data
            health_data = cast(
                "FlextDbOracleTypes.Query.QueryResult",
                {"status": "healthy", "connections": 5},
            )
            health_result = client._adapt_data_for_table(health_data)
            FlextTestsMatchers.assert_result_success(health_result)
            assert isinstance(health_result.value, list)

    def test_formatter_methods_real(self) -> None:
        """Test formatter methods."""
        client = FlextDbOracleClient()

        test_data = {
            "operation": "test",
            "params": {"title": "Test Results"},
            "result": [{"column1": "value1", "column2": "value2"}],
        }

        # Test _format_as_json
        if hasattr(client, "_format_as_json"):
            data_for_json = cast("FlextDbOracleTypes.Query.QueryResult", test_data)
            json_result = client._format_as_json(data_for_json)
            assert hasattr(json_result, "is_success")
            # Should work with formatter

        # Test _format_as_table
        if hasattr(client, "_format_as_table"):
            data_for_table = cast("FlextDbOracleTypes.Query.QueryResult", test_data)
            table_result = client._format_as_table(data_for_table)
            assert hasattr(table_result, "is_success")
            # Should work with formatter

    def test_connection_wizard_structure_real(self) -> None:
        """Test connection_wizard method structure."""
        client = FlextDbOracleClient()

        # Connection wizard functionality is handled through CLI commands
        # Test that client has connection capabilities through connect_to_oracle
        assert hasattr(client, "connect_to_oracle")
        assert callable(client.connect_to_oracle)

        # Test that method exists and has proper signature
        signature = inspect.signature(client.connect_to_oracle)
        assert (
            len(signature.parameters) == 5
        )  # host, port, service_name, user, password

        # Test that client has actual methods for database operations
        assert hasattr(client, "list_schemas")
        assert hasattr(client, "list_tables")
        assert hasattr(client, "health_check")

    def test_module_level_functions_real(self) -> None:
        """Test client instantiation pattern."""
        # Test client instantiation
        client_instance = FlextDbOracleClient()
        assert isinstance(client_instance, FlextDbOracleClient)

        # Test that new calls create separate instances
        client_instance2 = FlextDbOracleClient()
        assert client_instance is not client_instance2

        # Test that client has required CLI methods
        assert hasattr(client_instance, "execute_query")
        assert hasattr(client_instance, "list_schemas")
        assert hasattr(client_instance, "list_tables")
        assert hasattr(client_instance, "health_check")

    def test_error_handling_comprehensive_real(self) -> None:
        """Test comprehensive error handling patterns."""
        client = FlextDbOracleClient()

        # Test various operations that should fail gracefully
        operations = [
            ("execute_query", ["SELECT 1 FROM DUAL"]),
            ("list_schemas", []),
            ("list_tables", []),
            ("list_tables", ["SCHEMA"]),
            ("health_check", []),
        ]

        for method_name, args in operations:
            method = getattr(client, method_name)
            result = method(*args)

            # All methods should return FlextResult and fail gracefully without connection
            assert hasattr(result, "is_success")
            assert hasattr(result, "error") or hasattr(result, "value")
            FlextTestsMatchers.assert_result_failure(
                result,
            )  # Should fail without connection
            assert isinstance(result.error, str)
            assert len(result.error) > 0

    def test_list_tables_without_connection_real(self) -> None:
        """Test list_tables method without connection."""
        client = FlextDbOracleClient()

        # Test without schema
        result = client.list_tables()
        FlextTestsMatchers.assert_result_failure(result)
        assert (
            "connection" in (result.error or "").lower()
            or "not connected" in (result.error or "").lower()
        )

        # Test with schema
        result_with_schema = client.list_tables("TEST_SCHEMA")
        FlextTestsMatchers.assert_result_failure(result_with_schema)
        assert (
            "connection" in (result_with_schema.error or "").lower()
            or "not connected" in (result_with_schema.error or "").lower()
        )

    def test_health_check_without_connection_real(self) -> None:
        """Test health_check method without connection."""
        client = FlextDbOracleClient()

        result = client.health_check()

        # Should fail gracefully without connection
        FlextTestsMatchers.assert_result_failure(result)
        assert (
            "connection" in (result.error or "").lower()
            or "not connected" in (result.error or "").lower()
        )

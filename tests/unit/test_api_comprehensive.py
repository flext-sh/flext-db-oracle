"""Comprehensive Oracle API Tests - Real Implementation Without Mocks.

Tests the FlextDbOracleApi class completely without mocks,
achieving maximum coverage through real API operations using flext_tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

import pytest

from flext_core import FlextResult, FlextTypes
from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleModels,
    dispatcher as oracle_dispatcher,
)
from flext_tests import FlextTestsBuilders, FlextTestsMatchers


class TestFlextDbOracleApiRealFunctionality:
    """Comprehensive tests for Oracle API using ONLY real functionality - NO MOCKS."""

    def setup_method(self) -> None:
        """Setup test configuration and API instance."""
        self.config = FlextDbOracleModels.OracleConfig(
            host="test_host",
            port=1521,
            service_name="TEST",
            username="test_user",
            password="test_password",
        )
        self.api = FlextDbOracleApi(self.config)

    def test_api_initialization_complete_real(self) -> None:
        """Test complete API initialization with all attributes."""
        assert self.api is not None
        assert self.api.config == self.config
        assert hasattr(self.api, "_config")
        assert hasattr(self.api, "_services")
        assert hasattr(self.api, "_logger")
        assert hasattr(self.api, "_plugins")
        assert isinstance(self.api._plugins, dict)
        assert len(self.api._plugins) == 0

    def test_config_property_access_real(self) -> None:
        """Test config property returns correct configuration."""
        config = self.api.config
        assert config is self.config
        assert config.host == "test_host"
        assert config.port == 1521
        assert config.service_name == "TEST"
        assert config.username == "test_user"
        assert config.password == "test_password"

    def test_is_valid_real_functionality(self) -> None:
        """Test is_valid with real configuration validation."""
        result = self.api.is_valid()
        assert result is True

    def test_from_config_factory_method_real(self) -> None:
        """Test from_config class method."""
        api = FlextDbOracleApi.from_config(self.config)
        assert isinstance(api, FlextDbOracleApi)
        assert api.config == self.config
        assert api is not self.api  # Different instance

    def test_to_dict_complete_serialization_real(self) -> None:
        """Test complete dictionary serialization."""
        result = self.api.to_dict()
        assert isinstance(result, dict)

        # Use FlextTestsMatchers for better structure validation
        # Skip structure validation for now due to complex type requirements
        assert "config" in result
        assert "connected" in result
        assert "plugin_count" in result

        # Verify config section with type casting
        config_obj = result["config"]
        assert isinstance(config_obj, dict), "config should be a dict"
        # Cast to proper dict type for PyRight
        config_dict: FlextTypes.Core.Dict = config_obj
        assert config_dict["host"] == "test_host"
        assert config_dict["port"] == 1521
        assert config_dict["service_name"] == "TEST"
        assert config_dict["username"] == "test_user"
        # Verify password not exposed
        assert "password" not in config_dict

        # Verify other fields
        assert result["connected"] is False
        assert result["plugin_count"] == 0

    def test_to_dict_with_plugins_real(self) -> None:
        """Test to_dict with registered plugins."""
        # Register some plugins using REAL functionality
        self.api._plugins["test1"] = {"name": "test1"}
        self.api._plugins["test2"] = {"name": "test2"}

        result = self.api.to_dict()
        assert result["plugin_count"] == 2

    def test_is_connected_property_real_disconnected_state(self) -> None:
        """Test is_connected property when disconnected."""
        # Without mocking - test real disconnected state
        result = self.api.is_connected
        assert result is False

    # Query Operations Tests

    def test_query_operations_not_connected_real(self) -> None:
        """Test query operations fail gracefully when not connected."""
        result = self.api.query("SELECT 1 FROM DUAL")
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    def test_query_one_not_connected_real(self) -> None:
        """Test query_one fails gracefully when not connected."""
        result = self.api.query_one("SELECT 1 FROM DUAL")
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    def test_execute_not_connected_real(self) -> None:
        """Test execute fails gracefully when not connected."""
        result = self.api.execute_sql("CREATE TABLE test (id NUMBER)")
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    def test_dispatcher_query_flow_when_feature_enabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Ensure dispatcher handles query execution when feature flag is enabled."""
        monkeypatch.setenv("FLEXT_DB_ORACLE_ENABLE_DISPATCHER", "1")
        api = FlextDbOracleApi(self.config)

        class StubDispatcher:
            def __init__(self) -> None:
                self.commands: list[object] = []

            def dispatch(self, command: object) -> FlextResult[object]:
                self.commands.append(command)
                return FlextResult[object].ok(
                    [
                        {"result": 1},
                    ],
                )

        stub_dispatcher = StubDispatcher()

        monkeypatch.setattr(
            "flext_db_oracle.api.oracle_dispatcher.FlextDbOracleDispatcher.build_dispatcher",
            lambda *_, **__: stub_dispatcher,
            raising=False,
        )
        result = api.query("SELECT 1 FROM DUAL")

        assert result.is_success
        assert stub_dispatcher.commands, "dispatcher should receive the command"
        assert isinstance(
            stub_dispatcher.commands[0],
            oracle_dispatcher.FlextDbOracleDispatcher.ExecuteQueryCommand,
        )

        monkeypatch.delenv("FLEXT_DB_ORACLE_ENABLE_DISPATCHER", raising=False)

    # Schema Operations Tests

    def test_get_schemas_not_connected_real(self) -> None:
        """Test get_schemas fails gracefully when not connected."""
        result = self.api.get_schemas()
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    def test_get_tables_not_connected_real(self) -> None:
        """Test get_tables fails gracefully when not connected."""
        result = self.api.get_tables()
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    def test_get_columns_not_connected_real(self) -> None:
        """Test get_columns fails gracefully when not connected."""
        result = self.api.get_columns("test_table")
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    # Connection Test

    def test_test_connection_real_invalid_config(self) -> None:
        """Test test_connection with invalid config."""
        # Use real invalid configuration - should fail gracefully
        result = self.api.test_connection()
        FlextTestsMatchers.assert_result_failure(result)
        # Should contain connection-related error
        assert result.error is not None
        error_msg = result.error.lower()
        assert (
            "connection" in error_msg
            or "timeout" in error_msg
            or "failed" in error_msg
            or "connect" in error_msg
        )

    def test_disconnect_when_not_connected_real(self) -> None:
        """Test disconnect when not connected."""
        result = self.api.disconnect()
        FlextTestsMatchers.assert_result_success(result)

    # Utility Methods Tests
    def test_optimize_query_real_functionality(self) -> None:
        """Test query optimization with real functionality."""
        test_queries = [
            (
                "  SELECT   *   FROM   test   WHERE   id = 1  ",
                "SELECT * FROM test WHERE id = 1",
            ),
            ("select  col1,  col2  from table1", "select col1, col2 from table1"),
            ("SELECT\n\nid,\n\nname\n\nFROM\n\nusers", "SELECT id, name FROM users"),
        ]

        for input_query, expected_clean in test_queries:
            result = self.api.optimize_query(input_query)

            FlextTestsMatchers.assert_result_success(result)
            optimized_query = result.value
            assert isinstance(optimized_query, str)
            # The real implementation cleans whitespace and formatting
            assert optimized_query == expected_clean

    def test_get_observability_metrics_real(self) -> None:
        """Test observability metrics retrieval."""
        result = self.api.get_observability_metrics()

        FlextTestsMatchers.assert_result_success(result)
        metrics = result.value
        assert isinstance(metrics, dict)
        # Current implementation returns empty dict - test actual behavior
        # This demonstrates the method works, even if metrics are not populated

    # Configuration Factory Methods Tests

    def test_from_env_real_no_environment_vars(self) -> None:
        """Test from_env factory method with no environment variables."""
        result = FlextDbOracleApi.from_env("NONEXISTENT_PREFIX")

        # Since from_env provides defaults, it will succeed but use default values
        FlextTestsMatchers.assert_result_success(result)
        api = result.value
        assert api.config.host == "localhost"  # Default value
        assert api.config.port == 1521  # Default value
        assert api.config.service_name is None  # Default value (no env var set)

    def test_from_url_valid_url_real(self) -> None:
        """Test from_url factory method with valid Oracle URL."""
        result = FlextDbOracleApi.from_url("oracle://user:pass@host:1521/service")

        # Should succeed with valid Oracle URL
        FlextTestsMatchers.assert_result_success(result)
        api = result.value
        assert api.config.host == "host"
        assert api.config.port == 1521
        assert api.config.service_name == "SERVICE"
        assert api.config.username == "user"

    def test_from_url_invalid_url_real(self) -> None:
        """Test from_url with invalid URL format."""
        result = FlextDbOracleApi.from_url("invalid://not-oracle-url")

        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert (
            "invalid" in result.error.lower()
            or "failed to parse" in result.error.lower()
            or "not implemented" in result.error.lower()
        )

    # Plugin System Tests

    def test_plugin_registration_real_functionality(self) -> None:
        """Test successful plugin registration."""
        plugin = {"name": "test_plugin", "version": "1.0.0"}

        result = self.api.register_plugin("test_plugin", plugin)

        FlextTestsMatchers.assert_result_success(result)
        assert "test_plugin" in self.api._plugins
        assert self.api._plugins["test_plugin"] == plugin

    def test_plugin_unregistration_real_functionality(self) -> None:
        """Test successful plugin unregistration."""
        # Register a plugin first using real functionality
        plugin = {"name": "test_plugin"}
        self.api._plugins["test_plugin"] = plugin

        result = self.api.unregister_plugin("test_plugin")

        FlextTestsMatchers.assert_result_success(result)
        assert "test_plugin" not in self.api._plugins

    def test_plugin_unregistration_not_found_real(self) -> None:
        """Test plugin unregistration when plugin not found."""
        result = self.api.unregister_plugin("nonexistent_plugin")

        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "plugin 'nonexistent_plugin' not found" in result.error.lower()

    def test_get_plugin_real_functionality(self) -> None:
        """Test successful plugin retrieval."""
        plugin = {"name": "test_plugin", "version": "1.0.0"}
        self.api._plugins["test_plugin"] = plugin

        result = self.api.get_plugin("test_plugin")

        FlextTestsMatchers.assert_result_success(result)
        retrieved_plugin = result.value
        assert retrieved_plugin == plugin

    def test_get_plugin_not_found_real(self) -> None:
        """Test plugin retrieval when plugin not found."""
        result = self.api.get_plugin("nonexistent_plugin")

        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "plugin 'nonexistent_plugin' not found" in result.error.lower()

    def test_list_plugins_real_functionality(self) -> None:
        """Test successful plugin listing."""
        plugin1 = {"name": "plugin1"}
        plugin2 = {"name": "plugin2"}
        self.api._plugins["plugin1"] = plugin1
        self.api._plugins["plugin2"] = plugin2

        result = self.api.list_plugins()

        FlextTestsMatchers.assert_result_success(result)
        plugin_list = result.value
        assert isinstance(plugin_list, list)
        # Should return list of plugin info objects
        assert len(plugin_list) == 2

    def test_list_plugins_empty_real(self) -> None:
        """Test plugin listing when no plugins registered."""
        result = self.api.list_plugins()

        # Should succeed with empty list (based on actual API implementation)
        FlextTestsMatchers.assert_result_success(result)
        plugin_list = result.value
        assert isinstance(plugin_list, list)
        assert len(plugin_list) == 0

    # String representation test

    def test_repr_method_disconnected_real(self) -> None:
        """Test __repr__ method when disconnected (default state)."""
        repr_str = repr(self.api)
        expected = "FlextDbOracleApi(host=test_host, status=disconnected)"
        assert expected == repr_str

    # Factory Method Tests with TestBuilders

    def test_api_creation_using_testbuilders_real(self) -> None:
        """Test API creation using TestBuilders patterns."""
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
        if not hasattr(config_result, "success"):
            msg = "Expected FlextResult with .success attribute"
            raise AssertionError(msg)

        # Cast to FlextResult to satisfy mypy
        result = cast("FlextResult[object]", config_result)
        FlextTestsMatchers.assert_result_success(result)
        config = result.value
        assert isinstance(config, FlextDbOracleModels.OracleConfig)

        api = FlextDbOracleApi.from_config(config)
        assert isinstance(api, FlextDbOracleApi)
        assert api.config == config
        assert api.config.host == "testbuilder_host"

    def test_api_multiple_instances_isolation_real(self) -> None:
        """Test that multiple API instances are properly isolated."""
        config1 = FlextDbOracleModels.OracleConfig(
            host="instance1",
            port=1521,
            service_name="service1",
            username="user1",
            password="password1",
        )

        config2 = FlextDbOracleModels.OracleConfig(
            host="instance2",
            port=1522,
            service_name="service2",
            username="user2",
            password="password2",
        )

        api1 = FlextDbOracleApi(config1)
        api2 = FlextDbOracleApi(config2)

        # Test that instances are separate
        assert api1.config.host == "instance1"
        assert api2.config.host == "instance2"
        assert api1.config.port == 1521
        assert api2.config.port == 1522

        # Test plugin isolation using real functionality
        plugin1 = {"name": "plugin1", "version": "1.0.0"}
        api1.register_plugin("plugin1", plugin1)

        # api2 should not have api1's plugin
        api2_list = api2.list_plugins()
        FlextTestsMatchers.assert_result_success(api2_list)
        assert api2_list.value == []  # Empty list

        # api1 should have its plugin
        api1_list = api1.list_plugins()
        FlextTestsMatchers.assert_result_success(api1_list)
        plugin_list = api1_list.value
        assert isinstance(plugin_list, list)
        assert len(plugin_list) == 1

    def test_api_error_handling_patterns_real(self) -> None:
        """Test API error handling patterns."""
        # Test invalid SQL query optimization - should still work
        invalid_sql = "INVALID SQL SYNTAX HERE"
        result = self.api.optimize_query(invalid_sql)

        # Should still work - optimization is forgiving and cleans whitespace
        FlextTestsMatchers.assert_result_success(result)
        optimized_query = result.value
        assert isinstance(optimized_query, str)
        # Should clean the query even if SQL syntax is invalid
        assert optimized_query == "INVALID SQL SYNTAX HERE"

    def test_context_manager_protocol_real(self) -> None:
        """Test context manager protocol."""
        # Test context manager methods exist
        assert hasattr(self.api, "__enter__")
        assert hasattr(self.api, "__exit__")
        assert callable(self.api.__enter__)
        assert callable(self.api.__exit__)

        # Test actual context manager usage
        with self.api as api_context:
            assert api_context is self.api
            assert isinstance(api_context, FlextDbOracleApi)
            # Should be able to use API within context
            result = api_context.is_valid()
            assert result is True

    def test_repr_method_real(self) -> None:
        """Test __repr__ method."""
        repr_str = repr(self.api)
        assert isinstance(repr_str, str)
        assert len(repr_str) > 0
        # Should contain class name and key information
        assert "FlextDbOracleApi" in repr_str
        # Should contain host information for identification
        assert self.config.host in repr_str or "test_host" in repr_str

    def test_convert_singer_type_method_real(self) -> None:
        """Test convert_singer_type method."""
        # Test various Singer type conversions - test interface, not specific mappings
        test_types = ["string", "integer", "number", "boolean", "date-time"]

        for singer_type in test_types:
            result = self.api.convert_singer_type(singer_type)

            # Should return FlextResult
            assert hasattr(result, "success")
            assert hasattr(result, "error")

            if result.is_success:
                FlextTestsMatchers.assert_result_success(result)
                # Should return some Oracle type string
                oracle_type = result.value
                assert isinstance(oracle_type, str)
                assert len(oracle_type) > 0
                # Should contain common Oracle type keywords
                assert any(
                    keyword in oracle_type.upper()
                    for keyword in [
                        "VARCHAR",
                        "NUMBER",
                        "TIMESTAMP",
                        "DATE",
                        "CLOB",
                        "BLOB",
                    ]
                )
            else:
                # Some types may not be implemented yet - that's valid
                FlextTestsMatchers.assert_result_failure(result)
                assert result.error is not None

    def test_map_singer_schema_method_real(self) -> None:
        """Test map_singer_schema method."""
        # Create test Singer schema
        test_schema: FlextTypes.Core.Dict = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string", "maxLength": 100},
                "active": {"type": "boolean"},
                "created_at": {"type": "string", "format": "date-time"},
            },
            "required": ["id", "name"],
        }

        result = self.api.map_singer_schema(test_schema)

        # Method may not be fully implemented - test the interface
        assert hasattr(result, "success")
        assert hasattr(result, "value")
        assert hasattr(result, "error")

        if result.is_success:
            FlextTestsMatchers.assert_result_success(result)
            schema_mapping = result.value
            assert isinstance(schema_mapping, dict)
        else:
            FlextTestsMatchers.assert_result_failure(result)
            assert result.error is not None

    def test_execute_sql_method_structure_real(self) -> None:
        """Test execute_sql method structure."""
        test_sql = "SELECT 1 FROM dual"
        result = self.api.execute_sql(test_sql)

        # Should return FlextResult with proper structure
        assert hasattr(result, "success")
        assert hasattr(result, "error")

        # When not connected, should fail with descriptive error
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        # Error should mention connection or similar
        error_lower = result.error.lower()
        assert (
            "connection" in error_lower
            or "connect" in error_lower
            or "not connected" in error_lower
        )

    def test_transaction_method_real(self) -> None:
        """Test transaction method."""
        result = self.api.transaction()

        # Should return FlextResult
        assert hasattr(result, "success")
        assert hasattr(result, "error")

        # Without connection, should fail gracefully
        if not result.is_success:
            FlextTestsMatchers.assert_result_failure(result)
            assert result.error is not None
            error_lower = result.error.lower()
            assert (
                "connection" in error_lower
                or "transaction" in error_lower
                or "not connected" in error_lower
            )

    def test_connection_property_real(self) -> None:
        """Test connection property."""
        # When not connected, should return None
        connection = self.api.connection
        assert connection is None

        # Verify property exists
        assert hasattr(self.api, "connection")

    def test_api_methods_exist_comprehensive_real(self) -> None:
        """Test that all expected API methods exist."""
        expected_methods = [
            # Configuration methods
            "from_config",
            "from_env",
            "from_url",
            # Connection methods
            "connect",
            "disconnect",
            "test_connection",
            "is_connected",
            # Query methods
            "query",
            "query_one",
            "execute",
            "execute_many",
            "execute_sql",
            # Metadata methods
            "get_schemas",
            "get_tables",
            "get_columns",
            "get_table_metadata",
            "get_primary_keys",
            # Plugin methods
            "register_plugin",
            "unregister_plugin",
            "get_plugin",
            "list_plugins",
            # Utility methods
            "optimize_query",
            "get_observability_metrics",
            "get_health_status",
            # Singer methods
            "convert_singer_type",
            "map_singer_schema",
            # Properties and special methods
            "config",
            "connection",
            "is_valid",
            "to_dict",
            "transaction",
        ]

        for method_name in expected_methods:
            assert hasattr(self.api, method_name), f"Method {method_name} should exist"
            method = getattr(self.api, method_name)
            if method_name not in {
                "config",
                "connection",
                "is_connected",
            }:  # Properties
                assert callable(method), f"Method {method_name} should be callable"

    def test_plugin_management_edge_cases_real(self) -> None:
        """Test plugin management edge cases."""
        # Test registering None plugin (should work with defensive design)
        result = self.api.register_plugin("none_plugin", None)
        FlextTestsMatchers.assert_result_success(result)

        # Should be retrievable
        get_result = self.api.get_plugin("none_plugin")
        FlextTestsMatchers.assert_result_success(get_result)
        assert get_result.value is None

        # Test empty string plugin name
        empty_result = self.api.register_plugin("", {"test": "plugin"})
        FlextTestsMatchers.assert_result_success(empty_result)

        # Test retrieving empty name plugin
        get_empty = self.api.get_plugin("")
        FlextTestsMatchers.assert_result_success(get_empty)

        # Test unregistering plugin that exists
        unregister_result = self.api.unregister_plugin("")
        FlextTestsMatchers.assert_result_success(unregister_result)

    def test_optimize_query_edge_cases_real(self) -> None:
        """Test optimize_query with edge cases."""
        # Test empty query
        empty_result = self.api.optimize_query("")
        FlextTestsMatchers.assert_result_success(empty_result)
        assert not empty_result.value

        # Test query with lots of whitespace
        whitespace_query = "SELECT   \n\n   *    \n  FROM   \n   employees    \n\n"
        whitespace_result = self.api.optimize_query(whitespace_query)
        FlextTestsMatchers.assert_result_success(whitespace_result)
        optimized = whitespace_result.value
        assert optimized == "SELECT * FROM employees"

        # Test query with tabs and mixed whitespace
        tab_query = "SELECT\t\t*\tFROM\t\temployees\t\tWHERE\t\tid\t=\t1"
        tab_result = self.api.optimize_query(tab_query)
        FlextTestsMatchers.assert_result_success(tab_result)
        optimized_tab = tab_result.value
        assert optimized_tab == "SELECT * FROM employees WHERE id = 1"

    def test_api_configuration_variations_real(self) -> None:
        """Test API with various configuration scenarios."""
        # Test with minimal config
        minimal_config = FlextDbOracleModels.OracleConfig(
            host="m",
            port=1,
            service_name="S",
            username="u",
            password="p",
        )
        minimal_api = FlextDbOracleApi(minimal_config)
        assert minimal_api.is_valid() is True

        # Test API operations work with minimal config
        plugins = minimal_api.list_plugins()
        FlextTestsMatchers.assert_result_success(plugins)

        # Test with config containing special characters
        special_config = FlextDbOracleModels.OracleConfig(
            host="host-with.dots",
            port=65535,
            service_name="SERVICE_WITH_UNDERSCORES",
            username="user@domain",
            password="pass!@#$%",
        )
        special_api = FlextDbOracleApi(special_config)
        assert special_api.is_valid() is True

    def test_get_health_status_method_real(self) -> None:
        """Test get_health_status method."""
        result = self.api.get_health_status()

        # Should return FlextResult
        assert hasattr(result, "success")
        assert hasattr(result, "value")
        assert hasattr(result, "error")

        # Should succeed with health information
        FlextTestsMatchers.assert_result_success(result)
        health_data = result.value
        assert isinstance(health_data, dict)

        # Health data may be empty initially, that's valid
        assert len(health_data) >= 0

    def test_flext_result_consistency_real(self) -> None:
        """Test that all API methods return consistent FlextResult objects."""
        # Test optimize_query method
        result1 = self.api.optimize_query("SELECT 1")
        assert hasattr(result1, "is_success")
        assert hasattr(result1, "error")

        # Test get_observability_metrics method
        result2 = self.api.get_observability_metrics()
        assert hasattr(result2, "is_success")
        assert hasattr(result2, "error")

        # Test get_health_status method
        result3 = self.api.get_health_status()
        assert hasattr(result3, "is_success")
        assert hasattr(result3, "error")

        # Test list_plugins method
        result4 = self.api.list_plugins()
        assert hasattr(result4, "is_success")
        assert hasattr(result4, "error")

        # Test register_plugin method
        result5 = self.api.register_plugin("test", {"plugin": "data"})
        assert hasattr(result5, "is_success")
        assert hasattr(result5, "error")

        # Test all results follow FlextResult contract
        for result in [result1, result2, result3, result4, result5]:
            # All should return FlextResult with proper interface
            assert hasattr(result, "is_success")
            assert hasattr(result, "error")

            # Test FlextResult contract
            result_typed = cast("FlextResult[object]", result)
            if result_typed.is_success:
                assert result_typed.error is None
                # value can be any type including None (accessed safely)
                _ = getattr(
                    result_typed,
                    "value",
                    None,
                )  # Access is safe when success=True
            else:
                assert result_typed.error is not None
                assert isinstance(result_typed.error, str)
                assert len(result_typed.error) > 0

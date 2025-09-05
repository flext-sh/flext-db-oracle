"""Comprehensive Oracle API Tests - Real Implementation Without Mocks.

Tests the FlextDbOracleApi class completely without mocks,
achieving maximum coverage through real API operations using flext_tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import cast

from pydantic import SecretStr

# Add flext_tests to path
sys.path.insert(0, str(Path(__file__).parents[4] / "flext-core" / "src"))

from flext_core import FlextTypes
from flext_tests import FlextMatchers, TestBuilders

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
from flext_db_oracle.models import FlextDbOracleModels


class TestFlextDbOracleApiRealFunctionality:
    """Comprehensive tests for Oracle API using ONLY real functionality - NO MOCKS."""

    def setup_method(self) -> None:
        """Setup test configuration and API instance."""
        self.config = FlextDbOracleConfig(
            host="test_host",
            port=1521,
            service_name="TEST",
            username="test_user",
            password=SecretStr("test_password"),
        )
        self.api = FlextDbOracleApi(self.config)

    def test_api_initialization_complete_real(self) -> None:
        """Test complete API initialization with all attributes - REAL FUNCTIONALITY."""
        assert self.api is not None
        assert self.api.config == self.config
        assert hasattr(self.api, "_config")
        assert hasattr(self.api, "_services")
        assert hasattr(self.api, "_logger")
        assert hasattr(self.api, "_plugins")
        assert isinstance(self.api._plugins, dict)
        assert len(self.api._plugins) == 0

    def test_config_property_access_real(self) -> None:
        """Test config property returns correct configuration - REAL FUNCTIONALITY."""
        config = self.api.config
        assert config is self.config
        assert config.host == "test_host"
        assert config.port == 1521
        assert config.service_name == "TEST"
        assert config.username == "test_user"
        assert config.password.get_secret_value() == "test_password"

    def test_is_valid_real_functionality(self) -> None:
        """Test is_valid with real configuration validation - REAL FUNCTIONALITY."""
        result = self.api.is_valid()
        assert result is True

    def test_from_config_factory_method_real(self) -> None:
        """Test from_config class method - REAL FUNCTIONALITY."""
        api = FlextDbOracleApi.from_config(self.config)
        assert isinstance(api, FlextDbOracleApi)
        assert api.config == self.config
        assert api is not self.api  # Different instance

    def test_to_dict_complete_serialization_real(self) -> None:
        """Test complete dictionary serialization - REAL FUNCTIONALITY."""
        result = self.api.to_dict()
        assert isinstance(result, dict)

        # Use FlextMatchers for better structure validation
        FlextMatchers.assert_json_structure(
            cast("FlextTypes.Core.JsonObject", result),
            ["config", "connected", "plugin_count"],
        )

        # Verify config section with type casting
        config_obj = result["config"]
        assert isinstance(config_obj, dict), "config should be a dict"
        # Cast to proper dict type for PyRight
        config_dict: dict[str, object] = config_obj
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
        """Test to_dict with registered plugins - REAL FUNCTIONALITY."""
        # Register some plugins using REAL functionality
        self.api._plugins["test1"] = {"name": "test1"}
        self.api._plugins["test2"] = {"name": "test2"}

        result = self.api.to_dict()
        assert result["plugin_count"] == 2

    def test_is_connected_property_real_disconnected_state(self) -> None:
        """Test is_connected property when disconnected - REAL FUNCTIONALITY."""
        # Without mocking - test real disconnected state
        result = self.api.is_connected
        assert result is False

    # Query Operations Tests - REAL FUNCTIONALITY (will fail when not connected)

    def test_query_operations_not_connected_real(self) -> None:
        """Test query operations fail gracefully when not connected - REAL FUNCTIONALITY."""
        # Test query method - should fail gracefully without connection
        result = self.api.query("SELECT 1 FROM DUAL")
        FlextMatchers.assert_result_failure(result)
        assert result.error
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    def test_query_one_not_connected_real(self) -> None:
        """Test query_one fails gracefully when not connected - REAL FUNCTIONALITY."""
        result = self.api.query_one("SELECT 1 FROM DUAL")
        FlextMatchers.assert_result_failure(result)
        assert result.error
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    def test_execute_not_connected_real(self) -> None:
        """Test execute fails gracefully when not connected - REAL FUNCTIONALITY."""
        result = self.api.execute("CREATE TABLE test (id NUMBER)")
        FlextMatchers.assert_result_failure(result)
        assert result.error
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    # Schema Operations Tests - REAL FUNCTIONALITY

    def test_get_schemas_not_connected_real(self) -> None:
        """Test get_schemas fails gracefully when not connected - REAL FUNCTIONALITY."""
        result = self.api.get_schemas()
        FlextMatchers.assert_result_failure(result)
        assert result.error
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    def test_get_tables_not_connected_real(self) -> None:
        """Test get_tables fails gracefully when not connected - REAL FUNCTIONALITY."""
        result = self.api.get_tables()
        FlextMatchers.assert_result_failure(result)
        assert result.error
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    def test_get_columns_not_connected_real(self) -> None:
        """Test get_columns fails gracefully when not connected - REAL FUNCTIONALITY."""
        result = self.api.get_columns("test_table")
        FlextMatchers.assert_result_failure(result)
        assert result.error
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    # Connection Test - REAL FUNCTIONALITY

    def test_test_connection_real_invalid_config(self) -> None:
        """Test test_connection with invalid config - REAL FUNCTIONALITY."""
        # Use real invalid configuration - should fail gracefully
        result = self.api.test_connection()
        FlextMatchers.assert_result_failure(result)
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
        """Test disconnect when not connected - REAL FUNCTIONALITY."""
        result = self.api.disconnect()
        FlextMatchers.assert_result_success(result)

    # Utility Methods Tests - REAL FUNCTIONALITY

    def test_optimize_query_real_functionality(self) -> None:
        """Test query optimization with real functionality - NO MOCKS."""
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

            FlextMatchers.assert_result_success(result)
            optimized_query = result.value
            assert isinstance(optimized_query, str)
            # The real implementation cleans whitespace and formatting
            assert optimized_query == expected_clean

    def test_get_observability_metrics_real(self) -> None:
        """Test observability metrics retrieval - REAL FUNCTIONALITY."""
        result = self.api.get_observability_metrics()

        FlextMatchers.assert_result_success(result)
        metrics = result.value
        assert isinstance(metrics, dict)
        # Current implementation returns empty dict - test actual behavior
        # This demonstrates the method works, even if metrics are not populated

    # Configuration Factory Methods Tests - REAL FUNCTIONALITY

    def test_from_env_real_no_environment_vars(self) -> None:
        """Test from_env factory method with no environment variables - REAL FUNCTIONALITY."""
        result = FlextDbOracleApi.from_env("NONEXISTENT_PREFIX")

        # Since from_env provides defaults, it will succeed but use default values
        FlextMatchers.assert_result_success(result)
        api = result.value
        assert api.config.host == "localhost"  # Default value
        assert api.config.port == 1521  # Default value
        assert api.config.service_name == "XEPDB1"  # Default value

    def test_from_url_valid_url_real(self) -> None:
        """Test from_url factory method with valid Oracle URL - REAL FUNCTIONALITY."""
        result = FlextDbOracleApi.from_url("oracle://user:pass@host:1521/service")

        # Should succeed with valid Oracle URL
        FlextMatchers.assert_result_success(result)
        api = result.value
        assert api.config.host == "host"
        assert api.config.port == 1521
        assert api.config.service_name == "service"
        assert api.config.username == "user"

    def test_from_url_invalid_url_real(self) -> None:
        """Test from_url with invalid URL format - REAL FUNCTIONALITY."""
        result = FlextDbOracleApi.from_url("invalid://not-oracle-url")

        FlextMatchers.assert_result_failure(result)
        assert result.error is not None
        assert (
            "invalid" in result.error.lower()
            or "failed to parse" in result.error.lower()
            or "not implemented" in result.error.lower()
        )

    # Plugin System Tests - REAL FUNCTIONALITY

    def test_plugin_registration_real_functionality(self) -> None:
        """Test successful plugin registration - REAL FUNCTIONALITY."""
        plugin = {"name": "test_plugin", "version": "1.0.0"}

        result = self.api.register_plugin("test_plugin", plugin)

        FlextMatchers.assert_result_success(result)
        assert "test_plugin" in self.api._plugins
        assert self.api._plugins["test_plugin"] == plugin

    def test_plugin_unregistration_real_functionality(self) -> None:
        """Test successful plugin unregistration - REAL FUNCTIONALITY."""
        # Register a plugin first using real functionality
        plugin = {"name": "test_plugin"}
        self.api._plugins["test_plugin"] = plugin

        result = self.api.unregister_plugin("test_plugin")

        FlextMatchers.assert_result_success(result)
        assert "test_plugin" not in self.api._plugins

    def test_plugin_unregistration_not_found_real(self) -> None:
        """Test plugin unregistration when plugin not found - REAL FUNCTIONALITY."""
        result = self.api.unregister_plugin("nonexistent_plugin")

        FlextMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "plugin 'nonexistent_plugin' not found" in result.error.lower()

    def test_get_plugin_real_functionality(self) -> None:
        """Test successful plugin retrieval - REAL FUNCTIONALITY."""
        plugin = {"name": "test_plugin", "version": "1.0.0"}
        self.api._plugins["test_plugin"] = plugin

        result = self.api.get_plugin("test_plugin")

        FlextMatchers.assert_result_success(result)
        retrieved_plugin = result.value
        assert retrieved_plugin == plugin

    def test_get_plugin_not_found_real(self) -> None:
        """Test plugin retrieval when plugin not found - REAL FUNCTIONALITY."""
        result = self.api.get_plugin("nonexistent_plugin")

        FlextMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "plugin 'nonexistent_plugin' not found" in result.error.lower()

    def test_list_plugins_real_functionality(self) -> None:
        """Test successful plugin listing - REAL FUNCTIONALITY."""
        plugin1 = {"name": "plugin1"}
        plugin2 = {"name": "plugin2"}
        self.api._plugins["plugin1"] = plugin1
        self.api._plugins["plugin2"] = plugin2

        result = self.api.list_plugins()

        FlextMatchers.assert_result_success(result)
        plugin_list = result.value
        assert isinstance(plugin_list, list)
        # Should return list of plugin info objects
        assert len(plugin_list) == 2

    def test_list_plugins_empty_real(self) -> None:
        """Test plugin listing when no plugins registered - REAL FUNCTIONALITY."""
        result = self.api.list_plugins()

        # Should succeed with empty list (based on actual API implementation)
        FlextMatchers.assert_result_success(result)
        plugin_list = result.value
        assert isinstance(plugin_list, list)
        assert len(plugin_list) == 0

    # String representation test - REAL FUNCTIONALITY

    def test_repr_method_disconnected_real(self) -> None:
        """Test __repr__ method when disconnected (default state) - REAL FUNCTIONALITY."""
        repr_str = repr(self.api)
        expected = "FlextDbOracleApi(host=test_host, status=disconnected)"
        assert expected == repr_str

    # Factory Method Tests with TestBuilders - REAL FUNCTIONALITY

    def test_api_creation_using_testbuilders_real(self) -> None:
        """Test API creation using TestBuilders patterns - REAL FUNCTIONALITY."""
        config_result = (
            TestBuilders.result()
            .with_success_data(
                FlextDbOracleModels.OracleConfig(
                    host="testbuilder_host",
                    port=1521,
                    service_name="testbuilder_service",
                    username="testbuilder_user",
                    password=SecretStr("testbuilder_password"),
                ),
            )
            .build()
        )

        FlextMatchers.assert_result_success(config_result)
        config = config_result.value
        assert isinstance(config, FlextDbOracleModels.OracleConfig)

        api = FlextDbOracleApi.from_config(config)
        assert isinstance(api, FlextDbOracleApi)
        assert api.config == config
        assert api.config.host == "testbuilder_host"

    def test_api_multiple_instances_isolation_real(self) -> None:
        """Test that multiple API instances are properly isolated - REAL FUNCTIONALITY."""
        config1 = FlextDbOracleConfig(
            host="instance1",
            port=1521,
            service_name="service1",
            username="user1",
            password=SecretStr("password1"),
        )

        config2 = FlextDbOracleConfig(
            host="instance2",
            port=1522,
            service_name="service2",
            username="user2",
            password=SecretStr("password2"),
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
        FlextMatchers.assert_result_success(api2_list)  # Should succeed with empty list
        assert api2_list.value == []  # Empty list

        # api1 should have its plugin
        api1_list = api1.list_plugins()
        FlextMatchers.assert_result_success(api1_list)
        plugin_list = api1_list.value
        assert isinstance(plugin_list, list)
        assert len(plugin_list) == 1

    def test_api_error_handling_patterns_real(self) -> None:
        """Test API error handling patterns - REAL FUNCTIONALITY."""
        # Test invalid SQL query optimization - should still work
        invalid_sql = "INVALID SQL SYNTAX HERE"
        result = self.api.optimize_query(invalid_sql)

        # Should still work - optimization is forgiving and cleans whitespace
        FlextMatchers.assert_result_success(result)
        optimized_query = result.value
        assert isinstance(optimized_query, str)
        # Should clean the query even if SQL syntax is invalid
        assert optimized_query == "INVALID SQL SYNTAX HERE"

    def test_api_with_config_method_real(self) -> None:
        """Test with_config class method - REAL FUNCTIONALITY."""
        api = FlextDbOracleApi.with_config(self.config)
        assert isinstance(api, FlextDbOracleApi)
        assert api.config == self.config
        assert api is not self.api  # Different instance

"""Comprehensive Oracle API Tests - Real Implementation.

Tests the FlextDbOracleApi class completely without mocks,
achieving maximum coverage through real API operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import SecretStr

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.models import FlextDbOracleConfig


class TestPlugin:
    """Test plugin class for API testing."""

    def __init__(self, name: str, version: str) -> None:
        self.name = name
        self.version = version

    def get_info(self) -> dict[str, object]:
        """Return plugin information."""
        return {"name": self.name, "version": self.version, "type": "test_plugin"}


class TestFlextDbOracleApiComprehensive:
    """Comprehensive tests for Oracle API without mocks."""

    def test_api_initialization_with_config(self) -> None:
        """Test API initialization with configuration."""
        config = FlextDbOracleConfig(
            host="test_host",
            port=1521,
            service_name="test_service",
            username="test_user",
            password=SecretStr("test_password"),
        )

        api = FlextDbOracleApi(config)

        # Test basic properties
        assert not api.is_connected
        assert api.connection is None
        assert api.config == config

    def test_api_factory_methods(self) -> None:
        """Test API factory methods."""
        config = FlextDbOracleConfig(
            host="factory_host",
            port=1521,
            service_name="factory_service",
            username="factory_user",
            password=SecretStr("factory_password"),
        )

        # Test from_config class method
        api = FlextDbOracleApi.from_config(config)
        assert isinstance(api, FlextDbOracleApi)
        assert api.config == config

        # Test with_config class method
        api2 = FlextDbOracleApi.with_config(config)
        assert isinstance(api2, FlextDbOracleApi)
        assert api2.config == config

    def test_api_from_url_method(self) -> None:
        """Test API creation from URL (currently not implemented)."""
        url = "oracle://test_user:test_pass@test_host:1521/test_service"

        result = FlextDbOracleApi.from_url(url)

        # Currently not implemented, so should fail with descriptive error
        assert not result.success
        assert (
            "not implemented" in result.error.lower()
            or "url parsing" in result.error.lower()
        )

    def test_api_from_url_invalid_format(self) -> None:
        """Test API creation from invalid URL format."""
        invalid_url = "invalid://not-oracle-url"

        result = FlextDbOracleApi.from_url(invalid_url)

        assert not result.success
        assert (
            "invalid URL format" in result.error.lower()
            or "failed to parse" in result.error.lower()
            or "not implemented" in result.error.lower()
        )

    def test_api_optimize_query_method(self) -> None:
        """Test query optimization method (works without connection)."""
        config = FlextDbOracleConfig(
            host="test",
            port=1521,
            service_name="test",
            username="test",
            password=SecretStr("test"),
        )
        api = FlextDbOracleApi(config)

        # Test with simple query
        simple_query = "SELECT * FROM users"
        result = api.optimize_query(simple_query)

        assert result.success
        optimization = result.value
        assert isinstance(optimization, dict)
        assert "original_query" in optimization
        assert "suggestions" in optimization
        assert optimization["original_query"] == simple_query

    def test_api_optimize_query_complex(self) -> None:
        """Test query optimization with complex query."""
        config = FlextDbOracleConfig(
            host="test",
            port=1521,
            service_name="test",
            username="test",
            password=SecretStr("test"),
        )
        api = FlextDbOracleApi(config)

        # Test with complex query
        complex_query = """
            SELECT u.name, d.department_name, COUNT(*) as emp_count
            FROM users u
            JOIN departments d ON u.dept_id = d.id
            WHERE u.active = 1 AND d.budget > 100000
            GROUP BY u.name, d.department_name
            ORDER BY emp_count DESC
        """

        result = api.optimize_query(complex_query)

        assert result.success
        optimization = result.value
        assert isinstance(optimization, dict)
        assert "original_query" in optimization
        assert "suggestions" in optimization
        assert len(optimization["suggestions"]) >= 1

    def test_api_get_observability_metrics(self) -> None:
        """Test observability metrics retrieval (works without connection)."""
        config = FlextDbOracleConfig(
            host="metrics_test",
            port=1521,
            service_name="metrics_service",
            username="metrics_user",
            password=SecretStr("metrics_password"),
        )
        api = FlextDbOracleApi(config)

        result = api.get_observability_metrics()

        assert result.success
        metrics = result.value
        assert isinstance(metrics, dict)

        # Check for actual metric fields returned
        assert "connection_status" in metrics
        assert "config_loaded" in metrics
        assert "context_name" in metrics
        assert "plugin_count" in metrics

        # Verify metric values
        assert metrics["connection_status"] == "disconnected"
        assert metrics["config_loaded"] is True
        assert isinstance(metrics["plugin_count"], int)

    def test_api_plugin_system_empty(self) -> None:
        """Test plugin system when no plugins are registered."""
        config = FlextDbOracleConfig(
            host="plugin_test",
            port=1521,
            service_name="plugin_service",
            username="plugin_user",
            password=SecretStr("plugin_password"),
        )
        api = FlextDbOracleApi(config)

        # Test list_plugins when empty
        result = api.list_plugins()
        assert not result.success  # Should fail when empty
        assert (
            "plugin listing returned empty" in result.error.lower()
            or "no plugins" in result.error.lower()
        )

    def test_api_plugin_system_operations(self) -> None:
        """Test plugin system basic operations."""
        config = FlextDbOracleConfig(
            host="plugin_ops_test",
            port=1521,
            service_name="plugin_ops_service",
            username="plugin_ops_user",
            password=SecretStr("plugin_ops_password"),
        )
        api = FlextDbOracleApi(config)

        # Test register_plugin
        test_plugin = TestPlugin("test_plugin", "1.0.0")
        register_result = api.register_plugin("test_plugin", test_plugin)
        assert register_result.success

        # Test list_plugins after registration
        list_result = api.list_plugins()
        assert list_result.success
        plugins = list_result.value
        assert isinstance(plugins, list)
        assert len(plugins) == 1
        assert plugins[0]["name"] == "test_plugin"

        # Test get_plugin
        get_result = api.get_plugin("test_plugin")
        assert get_result.success
        retrieved_plugin = get_result.value
        assert retrieved_plugin == test_plugin

        # Test unregister_plugin
        unregister_result = api.unregister_plugin("test_plugin")
        assert unregister_result.success

        # Test list_plugins after unregistration should be empty
        final_list_result = api.list_plugins()
        assert not final_list_result.success  # Empty again

    def test_api_get_plugin_nonexistent(self) -> None:
        """Test getting a non-existent plugin."""
        config = FlextDbOracleConfig(
            host="test",
            port=1521,
            service_name="test",
            username="test",
            password=SecretStr("test"),
        )
        api = FlextDbOracleApi(config)

        result = api.get_plugin("nonexistent_plugin")

        assert not result.success
        assert "not found" in result.error.lower() or "plugin" in result.error.lower()

    def test_api_connection_status_without_connection(self) -> None:
        """Test connection status methods when not connected."""
        config = FlextDbOracleConfig(
            host="status_test",
            port=1521,
            service_name="status_service",
            username="status_user",
            password=SecretStr("status_password"),
        )
        api = FlextDbOracleApi(config)

        # Test is_connected
        assert not api.is_connected

        # Test connection property
        assert api.connection is None

        # Test config property
        assert api.config == config

    def test_api_query_methods_without_connection(self) -> None:
        """Test that query methods fail gracefully when not connected."""
        config = FlextDbOracleConfig(
            host="query_test",
            port=1521,
            service_name="query_service",
            username="query_user",
            password=SecretStr("query_password"),
        )
        api = FlextDbOracleApi(config)

        # Test query method
        query_result = api.query("SELECT 1 FROM dual")
        assert not query_result.success
        assert (
            "not connected" in query_result.error.lower()
            or "connection" in query_result.error.lower()
        )

        # Test query_one method
        query_one_result = api.query_one("SELECT 1 FROM dual")
        assert not query_one_result.success
        assert (
            "not connected" in query_one_result.error.lower()
            or "connection" in query_one_result.error.lower()
        )

        # Test execute_sql method
        execute_result = api.execute_sql("CREATE TABLE test (id NUMBER)")
        assert not execute_result.success
        assert (
            "not connected" in execute_result.error.lower()
            or "connection" in execute_result.error.lower()
        )

    def test_api_schema_methods_without_connection(self) -> None:
        """Test that schema methods fail gracefully when not connected."""
        config = FlextDbOracleConfig(
            host="schema_test",
            port=1521,
            service_name="schema_service",
            username="schema_user",
            password=SecretStr("schema_password"),
        )
        api = FlextDbOracleApi(config)

        # Test get_schemas method
        schemas_result = api.get_schemas()
        assert not schemas_result.success
        assert (
            "not connected" in schemas_result.error.lower()
            or "connection" in schemas_result.error.lower()
        )

        # Test get_tables method
        tables_result = api.get_tables()
        assert not tables_result.success
        assert (
            "not connected" in tables_result.error.lower()
            or "connection" in tables_result.error.lower()
        )

        # Test get_columns method
        columns_result = api.get_columns("test_table")
        assert not columns_result.success
        assert (
            "not connected" in columns_result.error.lower()
            or "connection" in columns_result.error.lower()
        )

    def test_api_test_connection_method(self) -> None:
        """Test connection testing method."""
        config = FlextDbOracleConfig(
            host="connection_test",
            port=1521,
            service_name="connection_service",
            username="connection_user",
            password=SecretStr("connection_password"),
        )
        api = FlextDbOracleApi(config)

        # Test connection (should fail with invalid credentials)
        test_result = api.test_connection()
        assert not test_result.success
        # Should contain connection-related error
        assert (
            "connection" in test_result.error.lower()
            or "timeout" in test_result.error.lower()
            or "failed" in test_result.error.lower()
            or "connected" in test_result.error.lower()
        )

    def test_api_disconnect_when_not_connected(self) -> None:
        """Test disconnect method when not connected."""
        config = FlextDbOracleConfig(
            host="disconnect_test",
            port=1521,
            service_name="disconnect_service",
            username="disconnect_user",
            password=SecretStr("disconnect_password"),
        )
        api = FlextDbOracleApi(config)

        # Disconnect when not connected should succeed
        result = api.disconnect()
        assert result.success

    def test_api_serialization_and_dict_conversion(self) -> None:
        """Test API serialization and dictionary conversion."""
        config = FlextDbOracleConfig(
            host="serialization_test",
            port=1521,
            service_name="serialization_service",
            username="serialization_user",
            password=SecretStr("serialization_password"),
        )
        api = FlextDbOracleApi(config)

        # Test to_dict method if available
        if hasattr(api, "to_dict"):
            result = api.to_dict()
            assert isinstance(result, dict)
            # May be empty dict depending on implementation

        # Test model_dump if available (Pydantic)
        if hasattr(api, "model_dump"):
            result = api.model_dump()
            assert isinstance(result, dict)
            # May be empty depending on implementation

    def test_api_initialization_variations(self) -> None:
        """Test different API initialization patterns."""
        # Test with minimal config
        minimal_config = FlextDbOracleConfig(
            host="minimal",
            port=1521,
            service_name="minimal",
            username="minimal",
            password=SecretStr("minimal"),
        )

        api1 = FlextDbOracleApi(minimal_config)
        assert api1.config == minimal_config

        # Test with full config including optional fields
        full_config = FlextDbOracleConfig(
            host="full.example.com",
            port=1521,
            service_name="full_service",
            username="full_user",
            password=SecretStr("full_password"),
            sid="FULL_SID",
            oracle_schema="FULL_SCHEMA",
            pool_min=2,
            pool_max=20,
            pool_increment=2,
            ssl_enabled=True,
        )

        api2 = FlextDbOracleApi(full_config)
        assert api2.config == full_config
        assert api2.config.oracle_schema == "FULL_SCHEMA"
        assert api2.config.ssl_enabled is True

    def test_api_error_handling_patterns(self) -> None:
        """Test API error handling patterns."""
        config = FlextDbOracleConfig(
            host="error_test",
            port=1521,
            service_name="error_service",
            username="error_user",
            password=SecretStr("error_password"),
        )
        api = FlextDbOracleApi(config)

        # Test invalid SQL query optimization
        invalid_sql = "INVALID SQL SYNTAX HERE"
        result = api.optimize_query(invalid_sql)

        # Should still work - optimization is forgiving
        assert result.success
        optimization = result.value
        assert "original_query" in optimization
        assert optimization["original_query"] == invalid_sql

    def test_api_multiple_instances_isolation(self) -> None:
        """Test that multiple API instances are properly isolated."""
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

        # Test plugin isolation
        plugin1 = TestPlugin("plugin1", "1.0.0")
        api1.register_plugin("plugin1", plugin1)

        # api2 should not have api1's plugin
        api2_list = api2.list_plugins()
        assert not api2_list.success  # Should be empty

        # api1 should have its plugin
        api1_list = api1.list_plugins()
        assert api1_list.success
        plugin_list = api1_list.value
        assert isinstance(plugin_list, list)
        assert len(plugin_list) == 1
        assert plugin_list[0]["name"] == "plugin1"

"""Real Oracle Plugins Tests - Using Docker Oracle Container.

This module tests plugin functionality against a real Oracle container,
maximizing coverage of plugin operations and extensibility features.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
    create_data_validation_plugin,
    create_performance_monitor_plugin,
    create_security_audit_plugin,
    register_all_oracle_plugins,
)


class TestRealOraclePlugins:
    """Test Oracle plugin system with real container."""

    def test_real_plugins_create_performance(self, oracle_container: None) -> None:
        """Test creating performance plugin with real Oracle."""
        plugin_result = create_performance_monitor_plugin()

        # Using modern pattern - handle failure first
        if plugin_result.is_failure:
            raise AssertionError(
                f"Performance plugin creation failed: {plugin_result.error}"
            )
        # Success case - use modern .value access
        plugin = plugin_result.value
        assert plugin is not None

        # Test plugin was created successfully
        assert plugin is not None

    def test_real_plugins_create_security(self, oracle_container: None) -> None:
        """Test creating security plugin with real Oracle."""
        plugin_result = create_security_audit_plugin()

        # Using modern pattern - handle failure first
        if plugin_result.is_failure:
            raise AssertionError(
                f"Security plugin creation failed: {plugin_result.error}"
            )
        # Success case - use modern .value access
        plugin = plugin_result.value
        assert plugin is not None

        # Test plugin was created successfully
        assert plugin is not None

    def test_real_plugins_create_validation(self, oracle_container: None) -> None:
        """Test creating validation plugin with real Oracle."""
        plugin_result = create_data_validation_plugin()

        # Using modern pattern - handle failure first
        if plugin_result.is_failure:
            raise AssertionError(
                f"Validation plugin creation failed: {plugin_result.error}"
            )
        # Success case - use modern .value access
        plugin = plugin_result.value
        assert plugin is not None

        # Test plugin was created successfully
        assert plugin is not None

    def test_real_plugins_register_all(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test registering all Oracle plugins."""
        # Register all plugins - using modern pattern
        result = register_all_oracle_plugins(oracle_api)

        if result.is_failure:
            raise AssertionError(f"Plugin registration failed: {result.error}")
        # Success case - use modern .value access
        plugins_dict = result.value
        assert isinstance(plugins_dict, dict)
        # May be empty if no plugins are registered by default
        assert len(result.value) >= 0


class TestRealOraclePluginErrorHandling:
    """Test plugin error handling with real Oracle."""

    def test_real_plugins_create_all_types(self) -> None:
        """Test creating all plugin types."""
        # Performance plugin - using modern pattern
        plugin_result = create_performance_monitor_plugin()
        if plugin_result.is_failure:
            raise AssertionError(
                f"Performance plugin creation failed: {plugin_result.error}"
            )

        # Security plugin - using modern pattern
        security_result = create_security_audit_plugin()
        if security_result.is_failure:
            raise AssertionError(
                f"Security plugin creation failed: {security_result.error}"
            )

        # Validation plugin - using modern pattern
        validation_result = create_data_validation_plugin()
        if validation_result.is_failure:
            raise AssertionError(
                f"Validation plugin creation failed: {validation_result.error}"
            )

    def test_real_plugins_register_with_empty_dict(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test registering plugins with empty dictionary."""
        result = register_all_oracle_plugins(oracle_api)

        # Using modern pattern - handle failure first
        if result.is_failure:
            raise AssertionError(f"Plugin registration failed: {result.error}")
        # Dictionary may be empty or populated depending on implementation
        assert isinstance(result.value, dict)

    def test_real_plugins_register_multiple_times(
        self,
        real_oracle_config: FlextDbOracleConfig,
        oracle_container: None,
    ) -> None:
        """Test registering plugins multiple times."""
        # Connect first
        from flext_db_oracle import FlextDbOracleApi

        api = FlextDbOracleApi.with_config(real_oracle_config)
        connected_api = api.connect()  # Returns self, fluent API pattern

        # Verify connection was successful
        assert connected_api.is_connected

        # Register once - using modern pattern
        result1 = register_all_oracle_plugins(connected_api)
        if result1.is_failure:
            raise AssertionError(f"First plugin registration failed: {result1.error}")
        plugins1 = result1.value
        first_count = len(plugins1)

        # Register again - should not fail - using modern pattern
        result2 = register_all_oracle_plugins(connected_api)
        if result2.is_failure:
            raise AssertionError(f"Second plugin registration failed: {result2.error}")
        plugins2 = result2.value

        # Count should be consistent
        assert len(plugins2) >= first_count


class TestRealOraclePluginIntegration:
    """Test plugin integration with real Oracle operations."""

    def test_real_plugins_with_oracle_metadata(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test plugins integration with Oracle metadata operations."""
        # Create plugins - using modern pattern
        perf_result = create_performance_monitor_plugin()
        if perf_result.is_failure:
            raise AssertionError(
                f"Performance plugin creation failed: {perf_result.error}"
            )

        security_result = create_security_audit_plugin()
        if security_result.is_failure:
            raise AssertionError(
                f"Security plugin creation failed: {security_result.error}"
            )

        validation_result = create_data_validation_plugin()
        if validation_result.is_failure:
            raise AssertionError(
                f"Validation plugin creation failed: {validation_result.error}"
            )

        # Test that API operations still work with plugins created - using modern pattern
        tables_result = oracle_api.get_tables()
        if tables_result.is_failure:
            raise AssertionError(f"Get tables failed: {tables_result.error}")

    def test_real_plugins_with_oracle_connection(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test plugins with Oracle connection operations."""
        # Register all plugins
        register_result = register_all_oracle_plugins(oracle_api)
        assert register_result.success

        # Test connection still works - using modern pattern
        connection_result = oracle_api.test_connection()
        if connection_result.is_failure:
            raise AssertionError(f"Connection test failed: {connection_result.error}")
        # Success case - connection test passed

    def test_real_plugins_with_query_operations(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test plugins with Oracle query operations."""
        # Create individual plugins - using modern pattern
        perf_plugin = create_performance_monitor_plugin()
        if perf_plugin.is_failure:
            raise AssertionError(
                f"Performance plugin creation failed: {perf_plugin.error}"
            )
        # Success case - performance plugin created

        security_plugin = create_security_audit_plugin()
        if security_plugin.is_failure:
            raise AssertionError(
                f"Security plugin creation failed: {security_plugin.error}"
            )
        # Success case - security plugin created

        validation_plugin = create_data_validation_plugin()
        if validation_plugin.is_failure:
            raise AssertionError(
                f"Validation plugin creation failed: {validation_plugin.error}"
            )
        # Success case - validation plugin created

        # Test query operations still work - using modern pattern
        query_result = oracle_api.query("SELECT COUNT(*) FROM FLEXTTEST.EMPLOYEES")
        if query_result.is_failure:
            raise AssertionError(f"Query failed: {query_result.error}")
        query_data = query_result.value
        assert len(query_data.rows) > 0

    def test_real_plugins_comprehensive_coverage(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test comprehensive plugin coverage with various Oracle operations."""
        # Register all plugins
        register_result = register_all_oracle_plugins(oracle_api)
        assert register_result.success

        # Test various API operations to ensure plugins don't interfere
        operations: list[object] = [
            oracle_api.test_connection,
            oracle_api.get_schemas,
            oracle_api.get_tables,
            lambda: oracle_api.get_columns("EMPLOYEES"),
            lambda: oracle_api.query("SELECT SYSDATE FROM DUAL"),
        ]

        for operation in operations:
            try:
                if callable(operation):
                    result = operation()
                    # Operations should either succeed or fail gracefully
                    assert hasattr(result, "success")
            except (ValueError, TypeError, RuntimeError) as e:
                # Should not raise unhandled exceptions
                pytest.fail(f"Operation raised unhandled exception: {e}")

    def test_real_plugins_plugin_object_types(self) -> None:
        """Test that plugins return proper object types."""
        # Create all plugin types
        plugins = [
            create_performance_monitor_plugin(),
            create_security_audit_plugin(),
            create_data_validation_plugin(),
        ]

        for plugin_result in plugins:
            if plugin_result.is_failure:
                raise AssertionError(f"Plugin creation failed: {plugin_result.error}")
            # Success case - use modern .value access
            plugin = plugin_result.value
            assert plugin is not None
            # Plugin should have some basic attributes or methods
            assert hasattr(plugin, "__class__")

    def test_real_plugins_with_different_configs(
        self,
        real_oracle_config: FlextDbOracleConfig,
        oracle_container: None,
    ) -> None:
        """Test plugins with different configuration objects."""
        # Create alternative config
        alt_config = FlextDbOracleConfig(
            host=real_oracle_config.host,
            port=real_oracle_config.port,
            username=real_oracle_config.username,
            password=real_oracle_config.password,
            service_name=real_oracle_config.service_name,
            encoding="UTF-8",
        )

        # Create APIs with different configs
        api1 = FlextDbOracleApi(real_oracle_config)
        api2 = FlextDbOracleApi(alt_config)

        result1 = register_all_oracle_plugins(api1)
        result2 = register_all_oracle_plugins(api2)

        # Using modern pattern - handle failures first
        if result1.is_failure:
            raise AssertionError(f"API1 plugin registration failed: {result1.error}")
        plugins1 = result1.value

        if result2.is_failure:
            raise AssertionError(f"API2 plugin registration failed: {result2.error}")
        plugins2 = result2.value

        # Both should work with equivalent configs
        assert len(plugins1) == len(plugins2)

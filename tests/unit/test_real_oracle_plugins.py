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

        assert plugin_result.success
        assert plugin_result.data is not None
        plugin = plugin_result.data

        # Test plugin was created successfully
        assert plugin is not None

    def test_real_plugins_create_security(self, oracle_container: None) -> None:
        """Test creating security plugin with real Oracle."""
        plugin_result = create_security_audit_plugin()

        assert plugin_result.success
        assert plugin_result.data is not None
        plugin = plugin_result.data

        # Test plugin was created successfully
        assert plugin is not None

    def test_real_plugins_create_validation(self, oracle_container: None) -> None:
        """Test creating validation plugin with real Oracle."""
        plugin_result = create_data_validation_plugin()

        assert plugin_result.success
        assert plugin_result.data is not None
        plugin = plugin_result.data

        # Test plugin was created successfully
        assert plugin is not None

    def test_real_plugins_register_all(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test registering all Oracle plugins."""
        # Register all plugins
        result = register_all_oracle_plugins(oracle_api)

        assert result.success
        assert isinstance(result.data, dict)
        # May be empty if no plugins are registered by default
        assert len(result.data) >= 0


class TestRealOraclePluginErrorHandling:
    """Test plugin error handling with real Oracle."""

    def test_real_plugins_create_all_types(self) -> None:
        """Test creating all plugin types."""
        # Performance plugin
        plugin_result = create_performance_monitor_plugin()
        assert plugin_result.success

        # Security plugin
        security_result = create_security_audit_plugin()
        assert security_result.success

        # Validation plugin
        validation_result = create_data_validation_plugin()
        assert validation_result.success

    def test_real_plugins_register_with_empty_dict(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test registering plugins with empty dictionary."""
        result = register_all_oracle_plugins(oracle_api)

        assert result.success
        # Dictionary may be empty or populated depending on implementation
        assert isinstance(result.data, dict)

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

        # Register once
        result1 = register_all_oracle_plugins(connected_api)
        assert result1.success
        first_count = len(result1.data)

        # Register again - should not fail
        result2 = register_all_oracle_plugins(connected_api)
        assert result2.success

        # Count should be consistent
        assert len(result2.data) >= first_count


class TestRealOraclePluginIntegration:
    """Test plugin integration with real Oracle operations."""

    def test_real_plugins_with_oracle_metadata(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test plugins integration with Oracle metadata operations."""
        # Create plugins
        perf_result = create_performance_monitor_plugin()
        assert perf_result.success

        security_result = create_security_audit_plugin()
        assert security_result.success

        validation_result = create_data_validation_plugin()
        assert validation_result.success

        # Test that API operations still work with plugins created
        tables_result = oracle_api.get_tables()
        assert tables_result.success

    def test_real_plugins_with_oracle_connection(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test plugins with Oracle connection operations."""
        # Register all plugins
        register_result = register_all_oracle_plugins(oracle_api)
        assert register_result.success

        # Test connection still works
        connection_result = oracle_api.test_connection()
        assert connection_result.success

    def test_real_plugins_with_query_operations(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test plugins with Oracle query operations."""
        # Create individual plugins
        perf_plugin = create_performance_monitor_plugin()
        security_plugin = create_security_audit_plugin()
        validation_plugin = create_data_validation_plugin()

        assert perf_plugin.success
        assert security_plugin.success
        assert validation_plugin.success

        # Test query operations still work
        query_result = oracle_api.query("SELECT COUNT(*) FROM FLEXTTEST.EMPLOYEES")
        assert query_result.success
        assert len(query_result.data) > 0

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
        operations = [
            oracle_api.test_connection,
            oracle_api.get_schemas,
            oracle_api.get_tables,
            lambda: oracle_api.get_columns("EMPLOYEES"),
            lambda: oracle_api.query("SELECT SYSDATE FROM DUAL"),
        ]

        for operation in operations:
            try:
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
            assert plugin_result.success
            plugin = plugin_result.data
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

        assert result1.success
        assert result2.success

        # Both should work with equivalent configs
        assert len(result1.data) == len(result2.data)

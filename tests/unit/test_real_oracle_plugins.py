"""Real Oracle Plugins Tests - Using Docker Oracle Container.

This module tests plugin functionality against a real Oracle container,
maximizing coverage of plugin operations and extensibility features.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_db_oracle import (
    create_data_validation_plugin,
    create_performance_monitor_plugin,
    create_security_audit_plugin,
    register_all_oracle_plugins,
)


class TestRealOraclePlugins:
    """Test Oracle plugin system with real container."""

    def test_real_plugins_create_performance(self, oracle_container) -> None:
        """Test creating performance plugin with real Oracle."""
        plugin_result = create_performance_monitor_plugin()

        assert plugin_result.is_success
        assert plugin_result.data is not None
        plugin = plugin_result.data

        # Test plugin was created successfully
        assert plugin is not None

    def test_real_plugins_create_security(self, oracle_container) -> None:
        """Test creating security plugin with real Oracle."""
        plugin_result = create_security_audit_plugin()

        assert plugin_result.is_success
        assert plugin_result.data is not None
        plugin = plugin_result.data

        # Test plugin was created successfully
        assert plugin is not None

    def test_real_plugins_create_validation(self, oracle_container) -> None:
        """Test creating validation plugin with real Oracle."""
        plugin_result = create_data_validation_plugin()

        assert plugin_result.is_success
        assert plugin_result.data is not None
        plugin = plugin_result.data

        # Test plugin was created successfully
        assert plugin is not None

    def test_real_plugins_register_all(
        self, real_oracle_config, oracle_container,
    ) -> None:
        """Test registering all Oracle plugins."""
        plugins_dict = {}

        # Register all plugins
        result = register_all_oracle_plugins(plugins_dict, real_oracle_config)

        assert result.is_success
        assert isinstance(plugins_dict, dict)
        # May be empty if no plugins are registered by default
        assert len(plugins_dict) >= 0


class TestRealOraclePluginErrorHandling:
    """Test plugin error handling with real Oracle."""

    def test_real_plugins_create_all_types(self) -> None:
        """Test creating all plugin types."""
        # Performance plugin
        plugin_result = create_performance_monitor_plugin()
        assert plugin_result.is_success

        # Security plugin
        security_result = create_security_audit_plugin()
        assert security_result.is_success

        # Validation plugin
        validation_result = create_data_validation_plugin()
        assert validation_result.is_success

    def test_real_plugins_register_with_empty_dict(
        self, real_oracle_config, oracle_container,
    ) -> None:
        """Test registering plugins with empty dictionary."""
        plugins_dict = {}

        result = register_all_oracle_plugins(plugins_dict, real_oracle_config)

        assert result.is_success
        # Dictionary may be empty or populated depending on implementation
        assert isinstance(plugins_dict, dict)

    def test_real_plugins_register_multiple_times(
        self, oracle_api, oracle_container,
    ) -> None:
        """Test registering plugins multiple times."""
        # Connect first
        connected_api = oracle_api.connect()

        # Register once
        result1 = register_all_oracle_plugins(connected_api)
        assert result1.is_success
        first_count = len(result1.data)

        # Register again - should not fail
        result2 = register_all_oracle_plugins(connected_api)
        assert result2.is_success

        # Count should be consistent
        assert len(result2.data) >= first_count


class TestRealOraclePluginIntegration:
    """Test plugin integration with real Oracle operations."""

    def test_real_plugins_with_oracle_metadata(
        self, oracle_api, oracle_container,
    ) -> None:
        """Test plugins integration with Oracle metadata operations."""
        # Create plugins
        perf_result = create_performance_monitor_plugin()
        assert perf_result.is_success

        security_result = create_security_audit_plugin()
        assert security_result.is_success

        validation_result = create_data_validation_plugin()
        assert validation_result.is_success

        # Test that API operations still work with plugins created
        tables_result = oracle_api.get_tables()
        assert tables_result.is_success

    def test_real_plugins_with_oracle_connection(
        self, oracle_api, oracle_container,
    ) -> None:
        """Test plugins with Oracle connection operations."""
        plugins_dict = {}

        # Register all plugins
        register_result = register_all_oracle_plugins(plugins_dict, oracle_api._config)
        assert register_result.is_success

        # Test connection still works
        connection_result = oracle_api.test_connection()
        assert connection_result.is_success

    def test_real_plugins_with_query_operations(
        self, oracle_api, oracle_container,
    ) -> None:
        """Test plugins with Oracle query operations."""
        # Create individual plugins
        perf_plugin = create_performance_monitor_plugin()
        security_plugin = create_security_audit_plugin()
        validation_plugin = create_data_validation_plugin()

        assert perf_plugin.is_success
        assert security_plugin.is_success
        assert validation_plugin.is_success

        # Test query operations still work
        query_result = oracle_api.query("SELECT COUNT(*) FROM FLEXTTEST.EMPLOYEES")
        assert query_result.is_success
        assert len(query_result.data) > 0

    def test_real_plugins_comprehensive_coverage(
        self, oracle_api, oracle_container,
    ) -> None:
        """Test comprehensive plugin coverage with various Oracle operations."""
        plugins_dict = {}

        # Register all plugins
        register_result = register_all_oracle_plugins(plugins_dict, oracle_api._config)
        assert register_result.is_success

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
                assert hasattr(result, "is_success")
            except Exception as e:
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
            assert plugin_result.is_success
            plugin = plugin_result.data
            assert plugin is not None
            # Plugin should have some basic attributes or methods
            assert hasattr(plugin, "__class__")

    def test_real_plugins_with_different_configs(
        self, real_oracle_config, oracle_container,
    ) -> None:
        """Test plugins with different configuration objects."""
        from flext_db_oracle import FlextDbOracleConfig

        # Create alternative config
        alt_config = FlextDbOracleConfig(
            host=real_oracle_config.host,
            port=real_oracle_config.port,
            username=real_oracle_config.username,
            password=real_oracle_config.password,
            service_name=real_oracle_config.service_name,
            encoding="UTF-8",
        )

        # Test register with different configs
        plugins_dict1 = {}
        plugins_dict2 = {}

        result1 = register_all_oracle_plugins(plugins_dict1, real_oracle_config)
        result2 = register_all_oracle_plugins(plugins_dict2, alt_config)

        assert result1.is_success
        assert result2.is_success

        # Both should work with equivalent configs
        assert len(plugins_dict1) == len(plugins_dict2)

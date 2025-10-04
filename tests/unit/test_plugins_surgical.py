"""Surgical tests for FlextDbOraclePlugins - targeting specific uncovered lines.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import unittest.mock

from flext_core import FlextTypes

from flext_db_oracle import FlextDbOraclePlugins


class TestPluginsSurgical:
    """Surgical tests for specific uncovered plugin functions."""

    def test_register_plugin_basic(self) -> None:
        """Test register_plugin with valid data."""
        plugins = FlextDbOraclePlugins()
        plugin_data: FlextTypes.Dict = {
            "type": "monitor",
            "config": {"enabled": True},
        }

        result = plugins.register_plugin("test_plugin", plugin_data)

        assert result.is_success
        # Verify plugin was registered
        list_result = plugins.list_plugins()
        assert list_result.is_success
        plugin_list = list_result.unwrap()
        assert "test_plugin" in plugin_list

    def test_register_plugin_overwrites_existing(self) -> None:
        """Test register_plugin overwrites existing plugin."""
        plugins = FlextDbOraclePlugins()
        plugin_data1: FlextTypes.Dict = {"version": "1.0"}
        plugin_data2: FlextTypes.Dict = {"version": "2.0"}

        # Register first version
        result1 = plugins.register_plugin("test_plugin", plugin_data1)
        assert result1.is_success

        # Register second version (should overwrite)
        result2 = plugins.register_plugin("test_plugin", plugin_data2)
        assert result2.is_success

        # Verify it was overwritten
        get_result = plugins.get_plugin("test_plugin")
        assert get_result.is_success
        plugin = get_result.unwrap()
        plugin = get_result.unwrap()
        assert isinstance(plugin, dict) and plugin["version"] == "2.0"

    def test_unregister_plugin_existing(self) -> None:
        """Test unregister_plugin removes existing plugin."""
        plugins = FlextDbOraclePlugins()
        plugin_data: FlextTypes.Dict = {"type": "test"}

        # Register plugin first
        register_result = plugins.register_plugin("test_plugin", plugin_data)
        assert register_result.is_success

        # Unregister plugin
        unregister_result = plugins.unregister_plugin("test_plugin")
        assert unregister_result.is_success

        # Verify plugin was removed
        get_result = plugins.get_plugin("test_plugin")
        assert get_result.is_failure
        assert get_result.error is not None and "not found" in get_result.error

    def test_unregister_plugin_nonexistent(self) -> None:
        """Test unregister_plugin with non-existent plugin."""
        plugins = FlextDbOraclePlugins()

        # Try to unregister non-existent plugin (should not fail)
        result = plugins.unregister_plugin("nonexistent_plugin")
        assert result.is_success

    def test_list_plugins_empty(self) -> None:
        """Test list_plugins fails when no plugins registered."""
        plugins = FlextDbOraclePlugins()

        result = plugins.list_plugins()
        assert result.is_failure
        assert (
            result.error is not None and "plugin listing returned empty" in result.error
        )

    def test_list_plugins_with_registered(self) -> None:
        """Test list_plugins returns registered plugins."""
        plugins = FlextDbOraclePlugins()

        # Register a few plugins
        plugins.register_plugin("plugin1", {"type": "test1"})
        plugins.register_plugin("plugin2", {"type": "test2"})

        result = plugins.list_plugins()
        assert result.is_success
        plugin_dict = result.unwrap()
        assert len(plugin_dict) == 2
        assert "plugin1" in plugin_dict
        assert "plugin2" in plugin_dict

    def test_get_plugin_existing(self) -> None:
        """Test get_plugin returns existing plugin data."""
        plugins = FlextDbOraclePlugins()
        plugin_data: FlextTypes.Dict = {"type": "monitor", "config": {"timeout": 30}}

        # Register plugin
        plugins.register_plugin("test_plugin", plugin_data)

        # Get plugin
        result = plugins.get_plugin("test_plugin")
        assert result.is_success
        retrieved_data = result.unwrap()
        assert retrieved_data == plugin_data

    def test_get_plugin_nonexistent(self) -> None:
        """Test get_plugin fails for non-existent plugin."""
        plugins = FlextDbOraclePlugins()

        result = plugins.get_plugin("nonexistent_plugin")
        assert result.is_failure
        assert result.error is not None and "not found" in result.error

    def test_create_performance_monitor_plugin(self) -> None:
        """Test create_performance_monitor_plugin factory method."""
        plugins = FlextDbOraclePlugins()

        result = plugins.create_performance_monitor_plugin()
        assert result.is_success
        plugin_data = result.unwrap()
        assert plugin_data["name"] == "performance_monitor"
        assert "version" in plugin_data
        assert "type" in plugin_data

    def test_create_data_validation_plugin(self) -> None:
        """Test create_data_validation_plugin factory method."""
        plugins = FlextDbOraclePlugins()

        result = plugins.create_data_validation_plugin()
        assert result.is_success
        plugin_data = result.unwrap()
        assert plugin_data["name"] == "data_validation"
        assert plugin_data["type"] == "validation"
        assert "capabilities" in plugin_data

    def test_create_security_audit_plugin(self) -> None:
        """Test create_security_audit_plugin factory method."""
        plugins = FlextDbOraclePlugins()

        result = plugins.create_security_audit_plugin()
        assert result.is_success
        plugin_data = result.unwrap()
        assert plugin_data["name"] == "security_audit"
        assert "version" in plugin_data
        assert "type" in plugin_data

    def test_register_all_oracle_plugins(self) -> None:
        """Test register_all_oracle_plugins registers default plugins."""
        plugins = FlextDbOraclePlugins()

        result = plugins.register_all_oracle_plugins()
        assert result.is_success

        # Verify some default plugins were registered
        list_result = plugins.list_plugins()
        assert list_result.is_success
        plugin_dict = list_result.unwrap()
        assert len(plugin_dict) > 0

        # Check for expected plugin types
        expected_plugins = ["performance_monitor", "data_validation", "security_audit"]
        for plugin_name in expected_plugins:
            get_result = plugins.get_plugin(plugin_name)
            assert get_result.is_success


class TestPluginsExceptionHandling:
    """Surgical tests targeting exception handling paths in plugins."""

    def test_register_all_oracle_plugins_exception_handling(self) -> None:
        """Test register_all_oracle_plugins exception path."""
        plugins = FlextDbOraclePlugins()

        # Mock create_performance_monitor_plugin to trigger exception
        with unittest.mock.patch.object(
            plugins,
            "create_performance_monitor_plugin",
            side_effect=Exception("Mock error"),
        ):
            result = plugins.register_all_oracle_plugins()
            assert result.is_failure
            assert result.error is not None
            assert (
                result.error is not None
                and "Plugin registration failed: Mock error" in result.error
            )

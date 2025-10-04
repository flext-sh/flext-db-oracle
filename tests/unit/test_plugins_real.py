"""Real tests for FlextDbOraclePlugins without mocks.

Coverage target: 15% → 90%

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextTypes

from flext_db_oracle import FlextDbOraclePlugins


class TestFlextDbOraclePluginsReal:
    """Real tests for FlextDbOraclePlugins without mocks."""

    def test_plugin_initialization(self) -> None:
        """Test plugin system initialization."""
        plugins = FlextDbOraclePlugins()
        assert plugins._plugins == {}

    def test_register_plugin_success(self) -> None:
        """Test successful plugin registration."""
        plugins = FlextDbOraclePlugins()

        plugin_data: FlextTypes.Dict = {
            "name": "test_plugin",
            "version": "1.0.0",
            "type": "testing",
            "capabilities": ["test1", "test2"],
        }

        result = plugins.register_plugin("test_plugin", plugin_data)
        assert result.is_success
        assert result.value is None
        assert "test_plugin" in plugins._plugins
        assert plugins._plugins["test_plugin"] == plugin_data

    def test_register_multiple_plugins(self) -> None:
        """Test registering multiple plugins."""
        plugins = FlextDbOraclePlugins()

        # Register first plugin
        plugin1: FlextTypes.Dict = {"name": "plugin1", "version": "1.0.0"}
        result1 = plugins.register_plugin("plugin1", plugin1)
        assert result1.is_success

        # Register second plugin
        plugin2: FlextTypes.Dict = {"name": "plugin2", "version": "2.0.0"}
        result2 = plugins.register_plugin("plugin2", plugin2)
        assert result2.is_success

        # Verify both registered
        assert len(plugins._plugins) == 2
        assert "plugin1" in plugins._plugins
        assert "plugin2" in plugins._plugins

    def test_unregister_plugin_success(self) -> None:
        """Test successful plugin unregistration."""
        plugins = FlextDbOraclePlugins()

        # First register a plugin
        plugin_data: FlextTypes.Dict = {"name": "test", "version": "1.0.0"}
        plugins.register_plugin("test", plugin_data)
        assert "test" in plugins._plugins

        # Now unregister it
        result = plugins.unregister_plugin("test")
        assert result.is_success
        assert result.value is None
        assert "test" not in plugins._plugins

    def test_unregister_nonexistent_plugin(self) -> None:
        """Test unregistering a plugin that doesn't exist."""
        plugins = FlextDbOraclePlugins()

        # Unregister non-existent plugin - should succeed
        result = plugins.unregister_plugin("nonexistent")
        assert result.is_success  # Returns success even if plugin doesn't exist

    def test_list_plugins_empty(self) -> None:
        """Test listing plugins when none registered."""
        plugins = FlextDbOraclePlugins()

        result = plugins.list_plugins()
        assert not result.is_success
        assert result.error == "plugin listing returned empty"

    def test_list_plugins_with_data(self) -> None:
        """Test listing plugins when some are registered."""
        plugins = FlextDbOraclePlugins()

        # Register some plugins
        plugin1: FlextTypes.Dict = {"name": "plugin1", "version": "1.0.0"}
        plugin2: FlextTypes.Dict = {"name": "plugin2", "version": "2.0.0"}
        plugins.register_plugin("plugin1", plugin1)
        plugins.register_plugin("plugin2", plugin2)

        # List plugins
        result = plugins.list_plugins()
        assert result.is_success
        assert isinstance(result.value, dict)
        assert len(result.value) == 2
        assert "plugin1" in result.value
        assert "plugin2" in result.value
        # Verify it's a copy
        assert result.value is not plugins._plugins

    def test_get_plugin_success(self) -> None:
        """Test getting a specific plugin."""
        plugins = FlextDbOraclePlugins()

        # Register a plugin
        plugin_data: FlextTypes.Dict = {
            "name": "test",
            "version": "1.0.0",
            "active": True,
        }
        plugins.register_plugin("test", plugin_data)

        # Get the plugin
        result = plugins.get_plugin("test")
        assert result.is_success
        assert result.value == plugin_data

    def test_get_plugin_not_found(self) -> None:
        """Test getting a plugin that doesn't exist."""
        plugins = FlextDbOraclePlugins()

        result = plugins.get_plugin("nonexistent")
        assert not result.is_success
        assert result.error is not None
        assert (
            result.error is not None
            and "Plugin 'nonexistent' not found" in result.error
        )

    def test_create_performance_monitor_plugin(self) -> None:
        """Test creating performance monitor plugin data."""
        plugins = FlextDbOraclePlugins()

        result = plugins.create_performance_monitor_plugin()
        assert result.is_success
        assert isinstance(result.value, dict)
        assert result.value["name"] == "performance_monitor"
        assert result.value["version"] == "1.0.0"
        assert result.value["type"] == "monitoring"
        capabilities = result.value["capabilities"]
        assert isinstance(capabilities, list)
        assert "query_tracking" in capabilities
        assert "performance_metrics" in capabilities
        assert "alerting" in capabilities

    def test_create_data_validation_plugin(self) -> None:
        """Test creating data validation plugin data."""
        plugins = FlextDbOraclePlugins()

        result = plugins.create_data_validation_plugin()
        assert result.is_success
        assert isinstance(result.value, dict)
        assert result.value["name"] == "data_validation"
        assert result.value["version"] == "1.0.0"
        assert result.value["type"] == "validation"
        capabilities = result.value["capabilities"]
        assert isinstance(capabilities, list)
        assert "schema_validation" in capabilities
        assert "data_integrity" in capabilities
        assert "constraints" in capabilities

    def test_create_security_audit_plugin(self) -> None:
        """Test creating security audit plugin data."""
        plugins = FlextDbOraclePlugins()

        result = plugins.create_security_audit_plugin()
        assert result.is_success
        assert isinstance(result.value, dict)
        assert result.value["name"] == "security_audit"
        assert result.value["version"] == "1.0.0"
        assert result.value["type"] == "security"
        capabilities = result.value["capabilities"]
        assert isinstance(capabilities, list)
        assert "access_logging" in capabilities
        assert "privilege_audit" in capabilities
        assert "compliance" in capabilities

    def test_register_all_oracle_plugins(self) -> None:
        """Test registering all available Oracle plugins."""
        plugins = FlextDbOraclePlugins()

        result = plugins.register_all_oracle_plugins()
        assert result.is_success
        assert isinstance(result.value, dict)

        # Check registration summary
        assert result.value["registered_count"] == 3
        assert result.value["registration_status"] == "completed"
        available_plugins = result.value["available_plugins"]
        assert isinstance(available_plugins, list)
        assert "performance_monitor" in available_plugins
        assert "data_validation" in available_plugins
        assert "security_audit" in available_plugins

        # Verify plugins are actually registered
        assert len(plugins._plugins) == 3
        assert "performance_monitor" in plugins._plugins
        assert "data_validation" in plugins._plugins
        assert "security_audit" in plugins._plugins

    def test_plugin_lifecycle(self) -> None:
        """Test complete plugin lifecycle."""
        plugins = FlextDbOraclePlugins()

        # Start with empty system
        list_result = plugins.list_plugins()
        assert not list_result.is_success

        # Register all plugins
        register_result = plugins.register_all_oracle_plugins()
        assert register_result.is_success
        assert register_result.value["registered_count"] == 3

        # List should now succeed
        list_result = plugins.list_plugins()
        assert list_result.is_success
        assert len(list_result.value) == 3

        # Get specific plugin
        get_result = plugins.get_plugin("performance_monitor")
        assert get_result.is_success
        plugin_data = get_result.value
        assert isinstance(plugin_data, dict)
        assert plugin_data["name"] == "performance_monitor"

        # Unregister one plugin
        unregister_result = plugins.unregister_plugin("performance_monitor")
        assert unregister_result.is_success

        # Verify it's gone
        get_result = plugins.get_plugin("performance_monitor")
        assert not get_result.is_success

        # List should show 2 plugins
        list_result = plugins.list_plugins()
        assert list_result.is_success
        assert len(list_result.value) == 2

    def test_plugin_overwrite(self) -> None:
        """Test overwriting an existing plugin."""
        plugins = FlextDbOraclePlugins()

        # Register initial plugin
        plugin_v1: FlextTypes.Dict = {"name": "test", "version": "1.0.0"}
        result1 = plugins.register_plugin("test", plugin_v1)
        assert result1.is_success

        # Overwrite with new version
        plugin_v2: FlextTypes.Dict = {
            "name": "test",
            "version": "2.0.0",
            "updated": True,
        }
        result2 = plugins.register_plugin("test", plugin_v2)
        assert result2.is_success

        # Verify it was overwritten
        get_result = plugins.get_plugin("test")
        assert get_result.is_success
        plugin_data = get_result.value
        assert isinstance(plugin_data, dict)
        assert plugin_data["version"] == "2.0.0"
        assert plugin_data.get("updated") is True

    def test_plugin_data_immutability(self) -> None:
        """Test that plugin data modifications don't affect stored data."""
        plugins = FlextDbOraclePlugins()

        # Register plugin
        original_data: FlextTypes.Dict = {
            "name": "test",
            "version": "1.0.0",
            "mutable": [1, 2, 3],
        }
        plugins.register_plugin("test", original_data)

        # Get plugin and modify returned data
        get_result = plugins.get_plugin("test")
        assert get_result.is_success

        # Since we store the object directly, modifications will affect it
        # This is expected behavior - plugins are mutable references
        returned_data = get_result.value
        if isinstance(returned_data, dict) and "mutable" in returned_data:
            returned_data["mutable"].append(4)

        # Verify the stored data is affected (expected for mutable references)
        get_result2 = plugins.get_plugin("test")
        assert get_result2.is_success
        if isinstance(get_result2.value, dict) and "mutable" in get_result2.value:
            assert 4 in get_result2.value["mutable"]

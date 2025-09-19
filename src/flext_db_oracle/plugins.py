"""Oracle Database plugins using unified class pattern.

Eliminates facade pattern and provides direct unified interface.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult, FlextTypes, FlextUtilities


class FlextDbOraclePlugins(FlextUtilities):
    """Single consolidated Oracle plugins class.

    Following flext-core pattern: one class per module, all functionality consolidated.
    Provides unified plugin management interface.
    """

    def __init__(self) -> None:
        """Initialize Oracle plugins system."""
        self._plugins: FlextTypes.Core.Dict = {}

    # Factory methods ELIMINATED - create plugin data directly as dicts:
    # {"name": "performance_monitor", "version": "1.0.0", "type": "monitoring",
    #  "capabilities": ["query_tracking", "performance_metrics", "alerting"]}

    def register_plugin(
        self,
        name: str,
        plugin_data: FlextTypes.Core.Dict,
    ) -> FlextResult[None]:
        """Register a plugin."""
        try:
            self._plugins[name] = plugin_data
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to register plugin '{name}': {e}")

    def unregister_plugin(self, name: str) -> FlextResult[None]:
        """Unregister a plugin."""
        try:
            if name in self._plugins:
                del self._plugins[name]
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to unregister plugin '{name}': {e}")

    def list_plugins(self) -> FlextResult[FlextTypes.Core.Dict]:
        """List all registered plugins."""
        try:
            if not self._plugins:
                return FlextResult[FlextTypes.Core.Dict].fail(
                    "plugin listing returned empty",
                )
            return FlextResult[FlextTypes.Core.Dict].ok(self._plugins.copy())
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to list plugins: {e}",
            )

    def get_plugin(self, name: str) -> FlextResult[object]:
        """Get a specific plugin."""
        try:
            if name not in self._plugins:
                return FlextResult[object].fail(f"Plugin '{name}' not found")
            return FlextResult[object].ok(self._plugins[name])
        except Exception as e:
            return FlextResult[object].fail(f"Failed to get plugin '{name}': {e}")

    def create_performance_monitor_plugin(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Create performance monitor plugin data."""
        try:
            plugin_data: FlextTypes.Core.Dict = {
                "name": "performance_monitor",
                "version": "1.0.0",
                "type": "monitoring",
                "capabilities": ["query_tracking", "performance_metrics", "alerting"],
            }
            return FlextResult[FlextTypes.Core.Dict].ok(plugin_data)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to create performance monitor plugin: {e}",
            )

    def create_data_validation_plugin(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Create data validation plugin data."""
        try:
            plugin_data: FlextTypes.Core.Dict = {
                "name": "data_validation",
                "version": "1.0.0",
                "type": "validation",
                "capabilities": ["schema_validation", "data_integrity", "constraints"],
            }
            return FlextResult[FlextTypes.Core.Dict].ok(plugin_data)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to create data validation plugin: {e}",
            )

    def create_security_audit_plugin(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Create security audit plugin data."""
        try:
            plugin_data: FlextTypes.Core.Dict = {
                "name": "security_audit",
                "version": "1.0.0",
                "type": "security",
                "capabilities": ["access_logging", "privilege_audit", "compliance"],
            }
            return FlextResult[FlextTypes.Core.Dict].ok(plugin_data)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Failed to create security audit plugin: {e}",
            )

    def register_all_oracle_plugins(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Register all available Oracle plugins.

        Returns:
            FlextResult containing the registered plugins information.

        """
        try:
            plugins_info: FlextTypes.Core.Dict = {}
            plugin_count = 0

            # Create and register plugins using factory methods
            perf_result = self.create_performance_monitor_plugin()
            if perf_result.success:
                self.register_plugin("performance_monitor", perf_result.value)
                plugin_count += 1

            validation_result = self.create_data_validation_plugin()
            if validation_result.success:
                self.register_plugin("data_validation", validation_result.value)
                plugin_count += 1

            security_result = self.create_security_audit_plugin()
            if security_result.success:
                self.register_plugin("security_audit", security_result.value)
                plugin_count += 1

            # Store registration summary
            plugins_info["registered_count"] = plugin_count
            plugins_info["registration_status"] = "completed"
            plugins_info["available_plugins"] = list(self._plugins.keys())

            return FlextResult[FlextTypes.Core.Dict].ok(plugins_info)
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Plugin registration failed: {e}",
            )


# Export the single class following flext-core pattern
__all__ = ["FlextDbOraclePlugins"]

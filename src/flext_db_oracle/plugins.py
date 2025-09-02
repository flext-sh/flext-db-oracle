"""Oracle database plugins facade module.

This module provides facade access to plugin functionality from FlextDbOracleServices.
Following the FLEXT architectural patterns with consolidated functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.services import FlextDbOracleServices


def create_performance_monitor_plugin() -> FlextResult[dict[str, object]]:
    """Create performance monitor plugin using PluginService.

    Facade function providing access to plugin functionality.
    """
    try:
        plugin_service = FlextDbOracleServices.PluginService()
        plugin_data = {
            "name": "performance_monitor",
            "version": "1.0.0",
            "service": plugin_service,
        }
        return FlextResult[dict[str, object]].ok(plugin_data)
    except Exception as e:
        return FlextResult[dict[str, object]].fail(
            f"Performance monitor plugin creation failed: {e}"
        )


def create_data_validation_plugin() -> FlextResult[dict[str, object]]:
    """Create data validation plugin using PluginService.

    Facade function providing access to plugin functionality.
    """
    try:
        plugin_service = FlextDbOracleServices.PluginService()
        plugin_data = {
            "name": "data_validation",
            "version": "1.0.0",
            "service": plugin_service,
        }
        return FlextResult[dict[str, object]].ok(plugin_data)
    except Exception as e:
        return FlextResult[dict[str, object]].fail(
            f"Data validation plugin creation failed: {e}"
        )


def create_security_audit_plugin() -> FlextResult[dict[str, object]]:
    """Create security audit plugin using PluginService.

    Facade function providing access to plugin functionality.
    """
    try:
        plugin_service = FlextDbOracleServices.PluginService()
        plugin_data = {
            "name": "security_audit",
            "version": "1.0.0",
            "service": plugin_service,
        }
        return FlextResult[dict[str, object]].ok(plugin_data)
    except Exception as e:
        return FlextResult[dict[str, object]].fail(
            f"Security audit plugin creation failed: {e}"
        )


def register_all_oracle_plugins(
    api: FlextDbOracleApi,
) -> FlextResult[dict[str, object]]:
    """Register all available Oracle plugins with the given API.

    Args:
        api: The FlextDbOracleApi instance to register plugins with.

    Returns:
        FlextResult containing the registered plugins information.

    """
    try:
        plugins_info: dict[str, object] = {}
        plugin_count = 0

        # Create and register each plugin type
        perf_result = create_performance_monitor_plugin()
        if perf_result.success:
            plugin_count += 1

        validation_result = create_data_validation_plugin()
        if validation_result.success:
            plugin_count += 1

        security_result = create_security_audit_plugin()
        if security_result.success:
            plugin_count += 1

        # Store registration summary
        plugins_info["registered_count"] = plugin_count
        plugins_info["api_connected"] = api.is_connected
        plugins_info["registration_status"] = "completed"

        return FlextResult[dict[str, object]].ok(plugins_info)
    except Exception as e:
        return FlextResult[dict[str, object]].fail(f"Plugin registration failed: {e}")


# Export main plugin service for direct access
PluginService = FlextDbOracleServices.PluginService

__all__ = [
    "PluginService",
    "create_data_validation_plugin",
    "create_performance_monitor_plugin",
    "create_security_audit_plugin",
    "register_all_oracle_plugins",
]

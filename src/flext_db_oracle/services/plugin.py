"""Plugin, metrics, and operations service mixin for flext-db-oracle.

Provides plugin registration, observability metrics recording,
health status, and operation tracking.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy.exc import (
    OperationalError as SQLAlchemyOperationalError,
)

from flext_core import r
from flext_db_oracle import (
    FlextDbOracleModels as m,
    FlextDbOracleServiceBase,
    FlextDbOracleTypes as t,
    FlextDbOracleUtilities as u,
)


class FlextDbOracleServicePlugin(FlextDbOracleServiceBase):
    """Mixin providing plugin, metrics, and operations for FlextDbOracleServices.

    Handles: register_plugin, unregister_plugin, get_plugin, list_plugins,
    record_metric, get_metrics, track_operation, get_operations.
    """

    def get_metrics(self) -> r[m.DbOracle.HealthStatus]:
        """Get metrics status with observability integration."""
        status = "connected" if self.is_connected() else "disconnected"
        metrics_payload: t.StrMapping = {
            metric_name: str(metric_value)
            for metric_name, metric_value in self._metrics.items()
        }
        return r[m.DbOracle.HealthStatus].ok(
            m.DbOracle.HealthStatus.model_validate({
                "status": f"{status}_with_observability",
                "timestamp": self._get_current_timestamp(),
                "service": "oracle",
                "database": self.db_config.service_name,
                "metrics": metrics_payload,
            }),
        )

    def get_operations(
        self,
    ) -> r[Sequence[m.DbOracle.OperationRecord]]:
        """Get tracked operations."""
        return r[Sequence[m.DbOracle.OperationRecord]].ok(
            list(self._operations),
        )

    def get_plugin(self, _name: str) -> r[t.ContainerValue]:
        """Get plugin data from local service registry."""
        if not _name:
            return r[t.ContainerValue].fail("Plugin name is required")
        if _name not in self._plugins:
            return r[t.ContainerValue].fail(f"Plugin '{_name}' not found")
        return r[t.ContainerValue].ok(self._plugins[_name])

    def list_plugins(self) -> r[t.ConfigMap]:
        """List plugin names from local service registry."""
        plugin_names = list(self._plugins.keys())
        return r[t.ConfigMap].ok(t.ConfigMap(root=dict.fromkeys(plugin_names, True)))

    def record_metric(
        self,
        _name: str,
        _value: float,
        _tags: t.ConfigMap | t.ContainerValueMapping | None = None,
    ) -> r[bool]:
        """Record metric in the local service metrics registry."""
        if not _name:
            return r[bool].fail("Metric name is required")
        self._metrics[_name] = _value
        return r[bool].ok(True)

    def register_plugin(self, _name: str, _plugin: t.ContainerValue) -> r[bool]:
        """Register plugin in local service registry."""
        if not _name:
            return r[bool].fail("Plugin name is required")
        plugin_payload = FlextDbOracleServiceBase._validate_config_map(_plugin)
        if plugin_payload is None:
            return r[bool].fail("Plugin payload must be a mapping")
        self._plugins[_name] = _plugin
        return r[bool].ok(True)

    def track_operation(
        self,
        operation_type: str = "",
        duration: float = 0.0,
        *,
        success: bool = True,
        metadata: t.ConfigMap | t.ContainerValueMapping | None = None,
    ) -> r[bool]:
        """Track database operation for monitoring."""

        def _track() -> bool:
            metadata_value = (
                metadata
                if isinstance(metadata, t.ConfigMap)
                else t.ConfigMap.model_validate({
                    "root": dict(metadata) if metadata else {},
                })
            )
            operation = m.DbOracle.OperationRecord(
                operation_type=operation_type,
                duration=duration,
                success=success,
                metadata_info=str(metadata_value),
                timestamp=self._get_current_timestamp(),
            )
            self._operations.append(operation)
            return True

        return u.try_(
            _track,
            catch=(
                t.DbOracle.OracleDatabaseError,
                t.DbOracle.OracleInterfaceError,
                ConnectionError,
                SQLAlchemyOperationalError,
                OSError,
            ),
        ).map_error(lambda e: f"Failed to track operation: {e}")

    def unregister_plugin(self, _name: str) -> r[bool]:
        """Unregister plugin from local service registry."""
        if not _name:
            return r[bool].fail("Plugin name is required")
        if _name not in self._plugins:
            return r[bool].fail(f"Plugin '{_name}' not found")
        self._plugins.pop(_name)
        return r[bool].ok(True)


__all__ = ["FlextDbOracleServicePlugin"]

"""Plugin, metrics, and operations service mixin for flext-db-oracle.

Provides plugin registration, observability metrics recording,
health status, and operation tracking.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Sequence,
)

from sqlalchemy.exc import (
    OperationalError as SQLAlchemyOperationalError,
)

from flext_db_oracle import (
    FlextDbOracleServiceBase,
    m,
    p,
    r,
    t,
    u,
)


class FlextDbOracleServicePlugin(FlextDbOracleServiceBase):
    """Mixin providing plugin, metrics, and operations for FlextDbOracleServices.

    Handles: register_plugin, unregister_plugin, get_plugin, list_plugins,
    record_metric, get_metrics, track_operation, get_operations.
    """

    def fetch_metrics(self) -> p.Result[m.DbOracle.HealthStatus]:
        """Get metrics status with observability integration."""
        status = "connected" if self.connected() else "disconnected"
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

    def fetch_operations(
        self,
    ) -> p.Result[Sequence[m.DbOracle.OperationRecord]]:
        """Get tracked operations."""
        return r[Sequence[m.DbOracle.OperationRecord]].ok(
            list(self._operations),
        )

    def fetch_plugin(self, _name: str) -> p.Result[t.RuntimeData]:
        """Get plugin data from local service registry."""
        if not _name:
            return r[t.RuntimeData].fail("Plugin name is required")
        if _name not in self._plugins:
            return r[t.RuntimeData].fail(f"Plugin '{_name}' not found")
        return r[t.RuntimeData].ok(self._plugins[_name])

    def list_plugins(self) -> p.Result[m.ConfigMap]:
        """List plugin names from local service registry."""
        plugin_names = list(self._plugins.keys())
        return r[m.ConfigMap].ok(m.ConfigMap(root=dict.fromkeys(plugin_names, True)))

    def record_metric(
        self,
        _name: str,
        _value: float,
        _tags: m.ConfigMap | t.JsonMapping | None = None,
    ) -> p.Result[bool]:
        """Record metric in the local service metrics registry."""
        if not _name:
            return r[bool].fail("Metric name is required")
        self._metrics[_name] = _value
        return r[bool].ok(True)

    def register_plugin(self, _name: str, _plugin: t.RuntimeData) -> p.Result[bool]:
        """Register plugin in local service registry."""
        if not _name:
            return r[bool].fail("Plugin name is required")
        self._plugins[_name] = _plugin
        return r[bool].ok(True)

    def track_operation(
        self,
        operation_type: str = "",
        duration: float = 0.0,
        *,
        success: bool = True,
        metadata: m.ConfigMap | t.JsonMapping | None = None,
    ) -> p.Result[bool]:
        """Track database operation for monitoring."""

        def _track() -> bool:
            metadata_value = (
                metadata
                if isinstance(metadata, m.ConfigMap)
                else m.ConfigMap.model_validate({
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

    def unregister_plugin(self, _name: str) -> p.Result[bool]:
        """Unregister plugin from local service registry."""
        if not _name:
            return r[bool].fail("Plugin name is required")
        if _name not in self._plugins:
            return r[bool].fail(f"Plugin '{_name}' not found")
        self._plugins.pop(_name)
        return r[bool].ok(True)


__all__: list[str] = ["FlextDbOracleServicePlugin"]

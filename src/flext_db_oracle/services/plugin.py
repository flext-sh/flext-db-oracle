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
    e,
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

    def fetch_plugin(self, name: str) -> p.Result[t.JsonPayload]:
        """Get plugin data from local service registry."""
        if not name:
            return r[t.JsonPayload].fail("Plugin name is required")
        if name not in self._plugins:
            return e.fail_not_found("Plugin", name, result_type=r[t.JsonPayload])
        return r[t.JsonPayload].ok(self._plugins[name])

    def list_plugins(self) -> p.Result[m.ConfigMap]:
        """List plugin names from local service registry."""
        plugin_names = list(self._plugins.keys())
        return r[m.ConfigMap].ok(m.ConfigMap(root=dict.fromkeys(plugin_names, True)))

    def record_metric(
        self,
        name: str,
        value: float,
        tags: m.ConfigMap | t.JsonMapping | None = None,
    ) -> p.Result[bool]:
        """Record metric in the local service metrics registry."""
        if not name:
            return r[bool].fail("Metric name is required")
        metric_payload: t.JsonValue = value
        if tags is not None:
            normalized_tags: dict[str, t.JsonValue] = {
                tag_name: u.normalize_to_metadata(tag_value)
                for tag_name, tag_value in tags.items()
            }
            metric_payload = {
                "value": value,
                "tags": normalized_tags,
            }
        self._metrics[name] = metric_payload
        return r[bool].ok(True)

    def register_plugin(self, name: str, plugin: t.JsonPayload) -> p.Result[bool]:
        """Register plugin in local service registry."""
        if not name:
            return r[bool].fail("Plugin name is required")
        self._plugins[name] = plugin
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

    def unregister_plugin(self, name: str) -> p.Result[bool]:
        """Unregister plugin from local service registry."""
        if not name:
            return r[bool].fail("Plugin name is required")
        if name not in self._plugins:
            return e.fail_not_found("Plugin", name, result_type=r[bool])
        self._plugins.pop(name)
        return r[bool].ok(True)


__all__: list[str] = ["FlextDbOracleServicePlugin"]

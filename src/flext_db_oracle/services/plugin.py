"""Plugin, metrics, and operations service mixin for flext-db-oracle.

Provides plugin registration, observability metrics recording,
health status, and operation tracking.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from importlib import import_module

from flext_core import r
from sqlalchemy.exc import (
    OperationalError as SQLAlchemyOperationalError,
)

from flext_db_oracle import FlextDbOracleModels, FlextDbOracleServiceBase, t, u


class FlextDbOracleServicePlugin(FlextDbOracleServiceBase):
    """Mixin providing plugin, metrics, and operations for FlextDbOracleServices.

    Handles: register_plugin, unregister_plugin, get_plugin, list_plugins,
    record_metric, get_metrics, track_operation, get_operations.
    """

    def get_metrics(self) -> r[FlextDbOracleModels.DbOracle.HealthStatus]:
        """Get metrics status with explicit observability integration check."""
        try:
            observability_module = import_module("flext_observability")
        except ModuleNotFoundError:
            return r[FlextDbOracleModels.DbOracle.HealthStatus].fail(
                "flext-observability integration unavailable; install flext-observability",
            )
        metric_factory = getattr(observability_module, "flext_metric", None)
        if not callable(metric_factory):
            core_module = import_module("flext_observability._core")
            metric_factory = getattr(core_module, "flext_metric", None)
        if not callable(metric_factory):
            return r[FlextDbOracleModels.DbOracle.HealthStatus].fail(
                "flext-observability does not expose flext_metric",
            )
        status = "connected" if self.is_connected() else "disconnected"
        metrics_payload: t.StrMapping = {
            metric_name: str(metric_value)
            for metric_name, metric_value in self._metrics.items()
        }
        return r[FlextDbOracleModels.DbOracle.HealthStatus].ok(
            FlextDbOracleModels.DbOracle.HealthStatus.model_validate({
                "status": f"{status}_with_observability",
                "timestamp": self._get_current_timestamp(),
                "service": "oracle",
                "database": self.db_config.service_name,
                "metrics": metrics_payload,
            }),
        )

    def get_operations(
        self,
    ) -> r[Sequence[FlextDbOracleModels.DbOracle.OperationRecord]]:
        """Get tracked operations."""
        return r[Sequence[FlextDbOracleModels.DbOracle.OperationRecord]].ok(
            list(self._operations),
        )

    def get_plugin(self, _name: str) -> r[t.ContainerValue]:
        """Get plugin data from local service registry."""
        if not _name:
            return r[t.ContainerValue].fail("Plugin name is required")
        try:
            _ = import_module("flext_plugin.api")
        except ModuleNotFoundError:
            return r[t.ContainerValue].fail(
                "flext-plugin integration unavailable; install flext-plugin",
            )
        if _name not in self._plugins:
            return r[t.ContainerValue].fail(f"Plugin '{_name}' not found")
        return r[t.ContainerValue].ok(self._plugins[_name])

    def list_plugins(self) -> r[t.ConfigMap]:
        """List plugin names from local service registry."""
        try:
            _ = import_module("flext_plugin.api")
        except ModuleNotFoundError:
            return r[t.ConfigMap].fail(
                "flext-plugin integration unavailable; install flext-plugin",
            )
        plugin_names = list(self._plugins.keys())
        return r[t.ConfigMap].ok(t.ConfigMap(root=dict.fromkeys(plugin_names, True)))

    def record_metric(
        self,
        _name: str,
        _value: float,
        _tags: t.ConfigMap | t.ContainerValueMapping | None = None,
    ) -> r[bool]:
        """Record metric through flext-observability when available."""
        if not _name:
            return r[bool].fail("Metric name is required")
        try:
            observability_module = import_module("flext_observability")
        except ModuleNotFoundError:
            return r[bool].fail(
                "flext-observability integration unavailable; install flext-observability",
            )
        metric_factory = getattr(observability_module, "flext_metric", None)
        if not callable(metric_factory):
            core_module = import_module("flext_observability._core")
            metric_factory = getattr(core_module, "flext_metric", None)
        if not callable(metric_factory):
            return r[bool].fail("flext-observability does not expose flext_metric")
        typed_tags = (
            _tags
            if isinstance(_tags, t.ConfigMap) or _tags is None
            else t.ConfigMap.model_validate({"root": dict(_tags)})
        )
        tags_str: t.StrMapping = (
            {str(k): str(v) for k, v in typed_tags.root.items()}
            if typed_tags is not None
            else {}
        )
        metric_result = metric_factory(
            name=_name,
            value=_value,
            tags=t.Dict.model_validate({"root": tags_str}),
        )
        if getattr(metric_result, "is_failure", False):
            return r[bool].fail(
                getattr(
                    metric_result,
                    "error",
                    "Metric recording failed in observability",
                ),
            )
        self._metrics[_name] = self._get_current_timestamp()
        return r[bool].ok(True)

    def register_plugin(self, _name: str, _plugin: t.ContainerValue) -> r[bool]:
        """Register plugin via flext-plugin when available."""
        if not _name:
            return r[bool].fail("Plugin name is required")
        plugin_payload = FlextDbOracleServiceBase._validate_config_map(_plugin)
        if plugin_payload is None:
            return r[bool].fail("Plugin payload must be a mapping")
        try:
            _ = import_module("flext_plugin.api")
            _ = import_module("flext_plugin.models")
        except ModuleNotFoundError:
            return r[bool].fail(
                "flext-plugin integration unavailable; install flext-plugin",
            )
        self._plugins[_name] = _name
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
            operation = FlextDbOracleModels.DbOracle.OperationRecord(
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
                FlextDbOracleServiceBase.OracleDatabaseError,
                FlextDbOracleServiceBase.OracleInterfaceError,
                ConnectionError,
                SQLAlchemyOperationalError,
                OSError,
            ),
        ).map_error(lambda e: f"Failed to track operation: {e}")

    def unregister_plugin(self, _name: str) -> r[bool]:
        """Unregister plugin from local service registry."""
        if not _name:
            return r[bool].fail("Plugin name is required")
        try:
            _ = import_module("flext_plugin.api")
        except ModuleNotFoundError:
            return r[bool].fail(
                "flext-plugin integration unavailable; install flext-plugin",
            )
        if _name not in self._plugins:
            return r[bool].fail(f"Plugin '{_name}' not found")
        self._plugins.pop(_name)
        return r[bool].ok(True)


__all__ = ["FlextDbOracleServicePlugin"]

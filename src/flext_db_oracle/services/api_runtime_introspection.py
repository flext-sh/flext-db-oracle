"""Introspection behavior of the public DB Oracle API facade runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from flext_db_oracle import m, p, r, t
from flext_db_oracle.services import FlextDbOracleApiRuntimeState


class FlextDbOracleApiRuntimeIntrospection(FlextDbOracleApiRuntimeState):
    """Schema introspection, Singer mapping, and plugin behavior."""

    def convert_singer_type(
        self,
        singer_type: str | Sequence[str],
        _format_hint: str | None = None,
    ) -> p.Result[str]:
        """Convert Singer JSON Schema type to Oracle SQL type.

        Returns:
            The resulting ``p.Result[str]``.

        """
        return self._services.convert_singer_type(singer_type, _format_hint)

    def fetch_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> p.Result[Sequence[m.DbOracle.Column]]:
        """Get column information for specified table.

        Returns:
            The resulting ``p.Result[Sequence[m.DbOracle.Column]]``.

        """
        return self._services.fetch_columns(table_name, schema_name)

    def fetch_health_status(self) -> p.Result[m.DbOracle.ConnectionStatus]:
        """Get database connection health status.

        Returns:
            The resulting ``p.Result[m.DbOracle.ConnectionStatus]``.

        """
        return self._services.fetch_connection_status()

    def fetch_observability_metrics(self) -> p.Result[t.JsonMapping]:
        """Get observability metrics for the connection.

        Returns:
            The resulting ``p.Result[t.JsonMapping]``.

        """
        return self._services.fetch_metrics().map(lambda metrics: metrics.model_dump())

    def fetch_plugin(self, name: str) -> p.Result[t.JsonPayload | t.FlatContainer]:
        """Get a registered plugin by name.

        Returns:
            The resulting ``p.Result[t.JsonPayload | t.FlatContainer]``.

        """
        return self._services.fetch_plugin(name)

    def fetch_primary_keys(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> p.Result[Sequence[str]]:
        """Delegate primary key retrieval to the schema service.

        Returns:
            The resulting ``p.Result[Sequence[str]]``.

        """
        return self._services.fetch_primary_keys(table_name, schema)

    def fetch_schemas(self) -> p.Result[Sequence[str]]:
        """Get list of available schemas.

        Returns:
            The resulting ``p.Result[Sequence[str]]``.

        """
        return self._services.fetch_schemas()

    def fetch_table_metadata(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> p.Result[m.DbOracle.TableMetadata]:
        """Get complete table metadata including columns and constraints.

        Returns:
            The resulting ``p.Result[m.DbOracle.TableMetadata]``.

        """
        return self._services.fetch_table_metadata(table_name, schema)

    def fetch_tables(self, schema: str | None = None) -> p.Result[Sequence[str]]:
        """Get list of tables in specified schema.

        Returns:
            The resulting ``p.Result[Sequence[str]]``.

        """
        return self._services.fetch_tables(schema)

    def list_plugins(self) -> p.Result[Sequence[str]]:
        """List all registered plugin names.

        Returns:
            The resulting ``p.Result[Sequence[str]]``.

        """
        return self._services.list_plugins().map(
            lambda plugin_map: list(plugin_map.root.keys()),
        )

    def map_singer_schema(
        self,
        singer_schema: m.DbOracle.SingerSchema | t.JsonMapping,
    ) -> p.Result[Mapping[str, str]]:
        """Map Singer JSON Schema to Oracle table schema.

        Returns:
            The resulting ``p.Result[Mapping[str, str]]``.

        """
        if not singer_schema:
            return r[Mapping[str, str]].fail("Schema must be a mapping")
        return self._services.map_singer_schema(singer_schema).map(
            lambda value: value.mapping,
        )

    def register_plugin(
        self,
        name: str,
        plugin: t.JsonPayload | t.FlatContainer,
    ) -> p.Result[bool]:
        """Register a plugin in local API registry.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        return self._services.register_plugin(name, plugin)

    def unregister_plugin(self, name: str) -> p.Result[bool]:
        """Unregister a plugin from local API registry.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        return self._services.unregister_plugin(name)


__all__: list[str] = ["FlextDbOracleApiRuntimeIntrospection"]

"""Oracle Database API with complete FLEXT ecosystem integration.

This API provides a unified interface to Oracle database operations
following FLEXT patterns with complete flext-core integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import types
from collections.abc import (
    Sequence,
)
from datetime import UTC, datetime
from typing import Self, override

from flext_db_oracle import (
    FlextDbOracleDispatcher,
    FlextDbOracleServiceBase,
    FlextDbOracleServices,
    FlextDbOracleSettings,
    c,
    m,
    p,
    r,
    t,
    u,
)


class FlextDbOracleApi(FlextDbOracleServiceBase):
    """Unified DB Oracle service facade via MRO composition."""

    def __init__(
        self,
        settings: FlextDbOracleSettings,
        context_name: str | None = None,
    ) -> None:
        """Initialize API with Oracle configuration and complete flext-core integration."""
        super().__init__(settings)
        self._oracle_config = settings
        self._services = FlextDbOracleServices(settings=self._oracle_config)
        self._context_name = context_name or "oracle-api"
        self._context: None = None
        self._dispatcher = FlextDbOracleDispatcher.build_dispatcher(self._services)

    @override
    def __repr__(self) -> str:
        """Return string representation of the API instance."""
        status = "connected" if self.connected() else "disconnected"
        return f"FlextDbOracleApi(host={self._oracle_config.host}, status={status})"

    def __enter__(self) -> Self:
        """Context manager entry."""
        connect_result = self.connect()
        if connect_result.failure:
            msg = connect_result.error or "Failed to connect to Oracle database"
            raise RuntimeError(msg)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Context manager exit - cleanup resources."""
        try:
            self.logger.debug("Disconnecting on context exit")
            self._services.disconnect()
        except Exception as exc:
            self.logger.warning("Disconnect failed on context exit", error=str(exc))

    @property
    def _dispatch_enabled(self) -> bool:
        """Check if dispatcher is enabled."""
        return True

    @property
    @override
    def settings(self) -> FlextDbOracleSettings:
        """Get the configuration."""
        return self._oracle_config

    @property
    def connection(self) -> FlextDbOracleServices | None:
        """Get connection t.JsonValue - public interface."""
        return self._services if self._services.connected() else None

    @override
    def connected(self) -> bool:
        """Check if connected to the database."""
        return self._services.connected()

    @property
    def oracle_config(self) -> FlextDbOracleSettings:
        """Get the Oracle configuration."""
        return self._oracle_config

    @property
    def oracle_services(self) -> FlextDbOracleServices:
        """Get the Oracle services instance."""
        return self._services

    @classmethod
    def from_config(cls, settings: FlextDbOracleSettings) -> FlextDbOracleApi:
        """Create API instance from an existing settings t.JsonValue."""
        return cls(settings=settings)

    @classmethod
    def _build_api_result(
        cls,
        settings: FlextDbOracleSettings,
    ) -> p.Result[FlextDbOracleApi]:
        """Create API instance from validated settings."""
        if not settings.username:
            return r[FlextDbOracleApi].fail(
                "Oracle username is required but not configured",
            )
        password = settings.password
        if password is None or not str(password):
            return r[FlextDbOracleApi].fail(
                "Oracle password is required but not configured",
            )
        return r[FlextDbOracleApi].ok(cls(settings=settings))

    @staticmethod
    def _normalize_parameters(
        parameters: t.JsonMapping | None = None,
    ) -> p.Result[m.ConfigMap]:
        """Normalize query parameters into the canonical ConfigMap contract."""
        if parameters is None:
            return r[m.ConfigMap].ok(m.ConfigMap(root={}))
        return (
            u
            .try_(lambda: dict(parameters))
            .map(lambda normalized: m.ConfigMap.model_validate({"root": normalized}))
            .lash(
                lambda error: r[m.ConfigMap].fail(f"Invalid query parameters: {error}")
            )
        )

    @classmethod
    def _normalize_parameters_list(
        cls,
        parameters_list: Sequence[t.JsonMapping],
    ) -> p.Result[Sequence[m.ConfigMap]]:
        """Normalize bulk query parameters into canonical ConfigMap values."""
        normalized: list[m.ConfigMap] = []
        for parameters in parameters_list:
            result = cls._normalize_parameters(parameters)
            if result.failure:
                return r[Sequence[m.ConfigMap]].fail(
                    result.error or "Invalid bulk query parameters",
                )
            normalized.append(result.value)
        return r[Sequence[m.ConfigMap]].ok(normalized)

    @classmethod
    def from_env(cls, prefix: str = "ORACLE_") -> p.Result[FlextDbOracleApi]:
        """Create API instance from environment variables.

        Args:
            prefix: Environment variable prefix (default: "ORACLE_")

        Returns:
            r[FlextDbOracleApi]: API instance or error.

        """
        values = FlextDbOracleSettings.resolve_environment_values(prefix)
        username = values.get("username")
        password = values.get("password")
        if username is None or not str(username).strip():
            return r[FlextDbOracleApi].fail(
                "Oracle username is required but not configured",
            )
        if password is None or not str(password).strip():
            return r[FlextDbOracleApi].fail(
                "Oracle password is required but not configured",
            )
        return FlextDbOracleSettings.from_env(prefix).flat_map(cls._build_api_result)

    @classmethod
    def from_url(cls, url: str) -> p.Result[FlextDbOracleApi]:
        """Create API instance from Oracle URL string.

        Args:
        url: Oracle connection URL (oracle://user:pass@host:port/service)

        Returns:
        r[FlextDbOracleApi]: API instance or error.

        """
        return FlextDbOracleSettings.from_url(url).flat_map(cls._build_api_result)

    def connect(self) -> p.Result[FlextDbOracleApi]:
        """Connect to Oracle database."""
        self.logger.info(
            "Connecting to Oracle database",
            extra=self._oracle_config.host,
        )
        return self._services.connect().map(lambda _: self)

    def convert_singer_type(
        self,
        singer_type: str | t.StrSequence,
        _format_hint: str | None = None,
    ) -> p.Result[str]:
        """Convert Singer JSON Schema type to Oracle SQL type."""
        return self._services.convert_singer_type(singer_type, _format_hint)

    def disconnect(self) -> p.Result[bool]:
        """Disconnect from Oracle database."""
        self.logger.info("Disconnecting from Oracle database")
        return self._services.disconnect()

    @override
    def execute(self, **_kwargs: t.Scalar) -> p.Result[FlextDbOracleSettings]:
        """Execute default domain service operation - return settings."""
        return u.try_(lambda: self._oracle_config).map_error(
            lambda e: f"API execution failed: {e}",
        )

    def execute_many(
        self,
        sql: str,
        params_list: Sequence[t.JsonMapping],
    ) -> p.Result[int]:
        """Execute a statement multiple times with different parameters."""
        self.logger.debug("Executing bulk statement", batch_size=len(params_list))
        return self._normalize_parameters_list(params_list).flat_map(
            lambda normalized_parameters: self._services.execute_many(
                sql,
                normalized_parameters,
            ),
        )

    def execute_sql(
        self,
        sql: str,
        parameters: t.JsonMapping | None = None,
    ) -> p.Result[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected."""
        return self.execute_statement(sql, parameters)

    def execute_statement(
        self,
        sql: str | t.JsonValue,
        params: t.JsonMapping | None = None,
    ) -> p.Result[int]:
        """Execute SQL statement directly and return affected rows."""
        sql_text = str(sql)
        self.logger.debug("Executing SQL statement", statement_length=len(sql_text))
        return self._normalize_parameters(params).flat_map(
            lambda normalized_parameters: self._services.execute_statement(
                sql_text,
                normalized_parameters,
            ),
        )

    def fetch_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> p.Result[Sequence[m.DbOracle.Column]]:
        """Get column information for specified table."""
        return self._services.fetch_columns(table_name, schema_name)

    def fetch_health_status(self) -> p.Result[m.DbOracle.ConnectionStatus]:
        """Get database connection health status."""
        return self._services.fetch_connection_status()

    def fetch_observability_metrics(self) -> p.Result[t.JsonMapping]:
        """Get observability metrics for the connection."""
        return self._services.fetch_metrics().map(lambda metrics: metrics.model_dump())

    def fetch_plugin(self, _name: str) -> p.Result[t.RuntimeData]:
        """Get a registered plugin by name."""
        return self._services.fetch_plugin(_name)

    def fetch_primary_keys(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> p.Result[t.StrSequence]:
        """Get primary key column names for specified table."""
        return self._services.fetch_primary_keys(table_name, schema)

    def fetch_schemas(self) -> p.Result[t.StrSequence]:
        """Get list of available schemas."""
        return self._services.fetch_schemas()

    def fetch_table_metadata(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> p.Result[m.DbOracle.TableMetadata]:
        """Get complete table metadata including columns and constraints."""
        return self._services.fetch_table_metadata(table_name, schema)

    def fetch_tables(self, schema: str | None = None) -> p.Result[t.StrSequence]:
        """Get list of tables in specified schema."""
        return self._services.fetch_tables(schema)

    @override
    def valid(self) -> bool:
        """Check if API configuration is valid."""
        return self._oracle_config.port >= c.DbOracle.OracleNetwork.MIN_PORT and bool(
            self._oracle_config.service_name,
        )

    def list_plugins(self) -> p.Result[t.StrSequence]:
        """List all registered plugin names."""
        return self._services.list_plugins().map(
            lambda plugin_map: list(plugin_map.root.keys()),
        )

    def map_singer_schema(
        self,
        singer_schema: m.DbOracle.SingerSchema | t.JsonMapping,
    ) -> p.Result[t.StrMapping]:
        """Map Singer JSON Schema to Oracle table schema."""
        if not isinstance(singer_schema, (dict, m.DbOracle.SingerSchema)):
            return r[t.StrMapping].fail("Schema must be a mapping")
        return self._services.map_singer_schema(singer_schema).map(
            lambda value: value.mapping,
        )

    def optimize_query(self, sql: str) -> p.Result[str]:
        """Optimize a SQL query for Oracle."""
        return u.try_(
            lambda: " ".join(sql.split()),
            catch=(AttributeError, ValueError, TypeError),
        ).map_error(lambda e: f"Query optimization failed: {e}")

    def query(
        self,
        sql: str,
        parameters: t.JsonMapping | None = None,
    ) -> p.Result[Sequence[m.Dict]]:
        """Execute a SELECT query and return all results."""
        self.logger.debug("Executing query", query_length=len(sql))
        return self._normalize_parameters(parameters).flat_map(
            lambda normalized_parameters: self._services.execute_query(
                sql,
                normalized_parameters,
            ),
        )

    def query_one(
        self,
        sql: str,
        parameters: t.JsonMapping | None = None,
    ) -> p.Result[m.Dict | None]:
        """Execute a SELECT query and return first result or None."""
        return self._normalize_parameters(parameters).flat_map(
            lambda normalized_parameters: self._services.fetch_one(
                sql,
                normalized_parameters,
            ),
        )

    def register_plugin(
        self,
        _name: str,
        _plugin: t.RuntimeData,
    ) -> p.Result[bool]:
        """Register a plugin in local API registry."""
        return self._services.register_plugin(_name, _plugin)

    def test_connection(self) -> p.Result[bool]:
        """Test Oracle database connection."""
        return self._services.test_connection()

    def to_dict(
        self,
        obj: t.JsonMapping | None = None,
    ) -> m.ConfigMap:
        """Serialize API state or explicit mapping into the canonical ConfigMap."""
        if obj is not None:
            return m.ConfigMap(root=dict(obj))
        return m.ConfigMap(
            root={
                "settings": self.oracle_config.model_dump(
                    exclude={"password"},
                    mode="python",
                ),
                "connected": self.connected(),
                "plugin_count": len(
                    self._services.list_plugins().unwrap_or(m.ConfigMap(root={})).root,
                ),
            },
        )

    def transaction(self) -> p.Result[t.JsonMapping]:
        """Get transaction status information."""
        return r[t.JsonMapping].ok(
            {
                "connected": self._services.connected(),
                "transaction_available": True,
            },
        )

    def unregister_plugin(self, _name: str) -> p.Result[bool]:
        """Unregister a plugin from local API registry."""
        return self._services.unregister_plugin(_name)

    def _convert_to_query_result(
        self,
        sql: str,
        data: Sequence[m.Dict],
    ) -> m.DbOracle.QueryResult:
        """Convert raw query data to QueryResult model."""
        if not data:
            return m.DbOracle.QueryResult(
                query=sql,
                columns=[],
                rows=[],
                row_count=0,
                unique_id="",
                created_at=datetime.now(UTC),
                domain_events=[],
                result_data=[],
                query_hash="",
                explain_plan="",
            )
        first_row = data[0].root
        columns = list(first_row.keys())
        rows = [
            m.DbOracle.RowData(
                values=[str(value) for value in row.root.values()],
            )
            for row in data
        ]
        return m.DbOracle.QueryResult(
            query=sql,
            columns=columns,
            rows=rows,
            row_count=len(data),
            unique_id="",
            created_at=datetime.now(UTC),
            domain_events=[],
            result_data=[],
            query_hash="",
            explain_plan="",
        )

    def _execute_query_sql(
        self,
        sql: str,
    ) -> p.Result[m.DbOracle.QueryResult]:
        """Execute SQL query and return results as QueryResult."""
        return self._services.execute_query(sql).map(
            lambda data: self._convert_to_query_result(sql, data),
        )


db_oracle = FlextDbOracleApi

__all__: list[str] = ["FlextDbOracleApi", "db_oracle"]

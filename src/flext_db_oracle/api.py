"""Oracle Database API with complete FLEXT ecosystem integration.

This API provides a unified interface to Oracle database operations
following FLEXT patterns with complete flext-core integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import os
import types
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Self, override

import oracledb
from pydantic import ValidationError

from flext_core import FlextResult as r, FlextService as s
from flext_db_oracle import (
    FlextDbOracleConstants as c,
    FlextDbOracleDispatcher,
    FlextDbOracleModels as m,
    FlextDbOracleServices,
    FlextDbOracleSettings,
    FlextDbOracleTypes as t,
    FlextDbOracleUtilities as u,
)

OracleDatabaseError: type[Exception] = oracledb.DatabaseError
OracleInterfaceError: type[Exception] = oracledb.InterfaceError


class FlextDbOracleApi(s[FlextDbOracleSettings]):
    """Oracle Database API with complete flext-core integration.

    This API provides a unified interface to Oracle database operations,
    integrating with flext-core components for proper error handling,
    logging, service orchestration, and enterprise patterns.

    Architecture:
    - Extends s for domain service patterns
    - Uses r railway pattern for error handling
    - Integrates FlextContext, FlextBus for enterprise features
    - Delegates to s for Oracle operations
    - Optional FlextDispatcher integration for CQRS patterns
    """

    @override
    def __init__(
        self,
        config: FlextDbOracleSettings,
        context_name: str | None = None,
    ) -> None:
        """Initialize API with Oracle configuration and complete flext-core integration."""
        super().__init__()
        self._oracle_config = config
        self._services = FlextDbOracleServices(config=self._oracle_config)
        self._context_name = context_name or "oracle-api"
        self._context = None
        self._dispatcher = FlextDbOracleDispatcher.build_dispatcher(self._services)
        self._plugins: t.MutableContainerValueMapping = {}
        self._registry = self._plugins

    @override
    def __repr__(self) -> str:
        """Return string representation of the API instance."""
        status = "connected" if self.is_connected else "disconnected"
        return f"FlextDbOracleApi(host={self._oracle_config.host}, status={status})"

    def __enter__(self) -> Self:
        """Context manager entry."""
        connect_result = self.connect()
        if connect_result.is_failure:
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
        with contextlib.suppress(Exception):
            self.logger.debug("Disconnecting on context exit")
            self._services.disconnect()

    @property
    def _dispatch_enabled(self) -> bool:
        """Check if dispatcher is enabled."""
        return True

    @property
    @override
    def config(self) -> FlextDbOracleSettings:
        """Get the configuration."""
        return self._oracle_config

    @property
    def connection(self) -> FlextDbOracleServices | None:
        """Get connection t.NormalizedValue - public interface."""
        return self._services if self._services.is_connected() else None

    @property
    def is_connected(self) -> bool:
        """Check if connected to the database."""
        return self._services.is_connected()

    @property
    def oracle_config(self) -> FlextDbOracleSettings:
        """Get the Oracle configuration."""
        return self._oracle_config

    @property
    def oracle_services(self) -> FlextDbOracleServices:
        """Get the Oracle services instance."""
        return self._services

    @classmethod
    def from_config(cls, config: FlextDbOracleSettings) -> FlextDbOracleApi:
        """Create API instance from an existing settings t.NormalizedValue."""
        return cls(config=config)

    @classmethod
    def _build_api_result(
        cls,
        config: FlextDbOracleSettings,
    ) -> r[FlextDbOracleApi]:
        """Create API instance from validated settings."""
        if not config.username:
            return r[FlextDbOracleApi].fail(
                "Oracle username is required but not configured",
            )
        password = config.password
        if password is None or not str(password):
            return r[FlextDbOracleApi].fail(
                "Oracle password is required but not configured",
            )
        return r[FlextDbOracleApi].ok(cls(config=config))

    @staticmethod
    def _normalize_parameters(
        parameters: t.ContainerValueMapping | None = None,
    ) -> r[t.ConfigMap]:
        """Normalize query parameters into the canonical ConfigMap contract."""
        if parameters is None:
            return r[t.ConfigMap].ok(t.ConfigMap(root={}))
        try:
            return r[t.ConfigMap].ok(
                t.ConfigMap.model_validate({"root": dict(parameters)}),
            )
        except (TypeError, ValidationError) as error:
            return r[t.ConfigMap].fail(f"Invalid query parameters: {error}")

    @classmethod
    def _normalize_parameters_list(
        cls,
        parameters_list: Sequence[t.ContainerValueMapping],
    ) -> r[Sequence[t.ConfigMap]]:
        """Normalize bulk query parameters into canonical ConfigMap values."""
        normalized: list[t.ConfigMap] = []
        for parameters in parameters_list:
            result = cls._normalize_parameters(parameters)
            if result.is_failure:
                return r[Sequence[t.ConfigMap]].fail(
                    result.error or "Invalid bulk query parameters",
                )
            normalized.append(result.value)
        return r[Sequence[t.ConfigMap]].ok(normalized)

    @classmethod
    def from_env(cls, prefix: str = "ORACLE_") -> r[FlextDbOracleApi]:
        """Create API instance from environment variables.

        Args:
            prefix: Environment variable prefix (default: "ORACLE_")

        Returns:
            r[FlextDbOracleApi]: API instance or error.

        """
        username = os.getenv(f"{prefix}USERNAME")
        password = os.getenv(f"{prefix}PASSWORD")
        if prefix == c.DbOracle.OracleEnvironment.PREFIX_ORACLE:
            flext_username = os.getenv("FLEXT_TARGET_ORACLE_USERNAME")
            flext_password = os.getenv("FLEXT_TARGET_ORACLE_PASSWORD")
            if flext_username is not None:
                username = flext_username
            if flext_password is not None:
                password = flext_password
        if username is None or not username.strip():
            return r[FlextDbOracleApi].fail(
                "Oracle username is required but not configured",
            )
        if password is None or not password.strip():
            return r[FlextDbOracleApi].fail(
                "Oracle password is required but not configured",
            )
        return FlextDbOracleSettings.from_env(prefix).flat_map(cls._build_api_result)

    @classmethod
    def from_url(cls, url: str) -> r[FlextDbOracleApi]:
        """Create API instance from Oracle URL string.

        Args:
        url: Oracle connection URL (oracle://user:pass@host:port/service)

        Returns:
        r[FlextDbOracleApi]: API instance or error.

        """
        return FlextDbOracleSettings.from_url(url).flat_map(cls._build_api_result)

    def connect(self) -> r[FlextDbOracleApi]:
        """Connect to Oracle database."""
        self.logger.info(
            "Connecting to Oracle database",
            extra=self._oracle_config.host,
        )
        return self._services.connect().map(lambda _: self)

    def convert_singer_type(
        self,
        singer_type: str | t.StrSequence,
        format_hint: str | None = None,
    ) -> r[str]:
        """Convert Singer JSON Schema type to Oracle SQL type."""
        return self._services.convert_singer_type(singer_type, format_hint)

    def disconnect(self) -> r[bool]:
        """Disconnect from Oracle database."""
        self.logger.info("Disconnecting from Oracle database")
        return self._services.disconnect()

    @override
    def execute(self, **_kwargs: t.Scalar) -> r[FlextDbOracleSettings]:
        """Execute default domain service operation - return config."""
        return u.try_(lambda: self._oracle_config).map_error(
            lambda e: f"API execution failed: {e}",
        )

    def execute_many(
        self,
        sql: str,
        parameters_list: Sequence[t.ContainerValueMapping],
    ) -> r[int]:
        """Execute a statement multiple times with different parameters."""
        self.logger.debug("Executing bulk statement", batch_size=len(parameters_list))
        return self._normalize_parameters_list(parameters_list).flat_map(
            lambda normalized_parameters: self._services.execute_many(
                sql,
                normalized_parameters,
            ),
        )

    def execute_sql(
        self,
        sql: str,
        parameters: t.ContainerValueMapping | None = None,
    ) -> r[int]:
        """Execute an INSERT/UPDATE/DELETE statement and return rows affected."""
        return self.execute_statement(sql, parameters)

    def execute_statement(
        self,
        sql: str | t.ContainerValue,
        parameters: t.ContainerValueMapping | None = None,
    ) -> r[int]:
        """Execute SQL statement directly and return affected rows."""
        sql_text = str(sql)
        self.logger.debug("Executing SQL statement", statement_length=len(sql_text))
        return self._normalize_parameters(parameters).flat_map(
            lambda normalized_parameters: self._services.execute_statement(
                sql_text,
                normalized_parameters,
            ),
        )

    def get_columns(
        self,
        table: str,
        schema: str | None = None,
    ) -> r[Sequence[m.DbOracle.Column]]:
        """Get column information for specified table."""
        return self._services.get_columns(table, schema)

    def get_health_status(self) -> r[m.DbOracle.ConnectionStatus]:
        """Get database connection health status."""
        return self._services.get_connection_status()

    def get_observability_metrics(self) -> r[t.ContainerValueMapping]:
        """Get observability metrics for the connection."""
        return self._services.get_metrics().map(lambda metrics: metrics.model_dump())

    def get_plugin(self, name: str) -> r[t.ContainerValue | None]:
        """Get a registered plugin by name."""
        if name not in self._plugins:
            return r[t.ContainerValue | None].fail(f"Plugin '{name}' not found")
        plugin = self._plugins[name]
        return r[t.ContainerValue | None].ok(plugin)

    def get_primary_keys(
        self,
        table: str,
        schema: str | None = None,
    ) -> r[t.StrSequence]:
        """Get primary key column names for specified table."""
        return self._services.get_primary_keys(table, schema)

    def get_schemas(self) -> r[t.StrSequence]:
        """Get list of available schemas."""
        return self._services.get_schemas()

    def get_table_metadata(
        self,
        table: str,
        schema: str | None = None,
    ) -> r[m.DbOracle.TableMetadata]:
        """Get complete table metadata including columns and constraints."""
        return self._services.get_table_metadata(table, schema)

    def get_tables(self, schema: str | None = None) -> r[t.StrSequence]:
        """Get list of tables in specified schema."""
        return self._services.get_tables(schema)

    @override
    def is_valid(self) -> bool:
        """Check if API configuration is valid."""
        return self._oracle_config.port >= c.DbOracle.OracleNetwork.MIN_PORT and bool(
            self._oracle_config.service_name,
        )

    def list_plugins(self) -> r[t.StrSequence]:
        """List all registered plugin names."""
        return r[t.StrSequence].ok(list(self._plugins.keys()))

    def map_singer_schema(self, schema: t.ContainerValue) -> r[t.StrMapping]:
        """Map Singer JSON Schema to Oracle table schema."""
        if not isinstance(schema, dict):
            return r[t.StrMapping].fail("Schema must be a mapping")
        return self._services.map_singer_schema(schema).map(lambda value: value.mapping)

    def optimize_query(self, sql: str) -> r[str]:
        """Optimize a SQL query for Oracle."""
        return u.try_(
            lambda: " ".join(sql.split()),
            catch=(AttributeError, ValueError, TypeError),
        ).map_error(lambda e: f"Query optimization failed: {e}")

    def query(
        self,
        sql: str,
        parameters: t.ContainerValueMapping | None = None,
    ) -> r[Sequence[t.Dict]]:
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
        parameters: t.ContainerValueMapping | None = None,
    ) -> r[t.Dict | None]:
        """Execute a SELECT query and return first result or None."""
        return self._normalize_parameters(parameters).flat_map(
            lambda normalized_parameters: self._services.fetch_one(
                sql,
                normalized_parameters,
            ),
        )

    def register_plugin(self, name: str, plugin: t.ContainerValue) -> r[bool]:
        """Register a plugin in local API registry."""
        self._plugins[name] = plugin
        return r[bool].ok(True)

    def test_connection(self) -> r[bool]:
        """Test Oracle database connection."""
        return self._services.test_connection()

    def to_dict(
        self,
        obj: t.ContainerValueMapping | None = None,
    ) -> t.ConfigMap:
        """Serialize API state or explicit mapping into the canonical ConfigMap."""
        if obj is not None:
            return t.ConfigMap(root=dict(obj))
        return t.ConfigMap(
            root={
                "config": self.oracle_config.model_dump(
                    exclude={"password"},
                    mode="python",
                ),
                "connected": self.is_connected,
                "plugin_count": len(self._plugins),
            },
        )

    def transaction(self) -> r[t.ContainerValueMapping]:
        """Get transaction status information."""
        return r[t.ContainerValueMapping].ok(
            {
                "connected": self._services.is_connected(),
                "transaction_available": True,
            },
        )

    def unregister_plugin(self, name: str) -> r[bool]:
        """Unregister a plugin from local API registry."""
        if name not in self._plugins:
            return r[bool].fail(f"Plugin '{name}' not found")
        self._plugins.pop(name)
        return r[bool].ok(True)

    def _convert_to_query_result(
        self,
        sql: str,
        data: Sequence[t.Dict],
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
    ) -> r[m.DbOracle.QueryResult]:
        """Execute SQL query and return results as QueryResult."""
        return self._services.execute_query(sql).map(
            lambda data: self._convert_to_query_result(sql, data),
        )

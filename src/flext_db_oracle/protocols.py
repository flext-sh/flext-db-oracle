"""Oracle Database protocols for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, r

from flext_db_oracle import m, t


class FlextDbOracleProtocols(FlextProtocols):
    """Oracle database protocols extending FlextProtocols.

    Extends FlextProtocols to inherit all foundation protocols (Result, Service, etc.)
    and adds Oracle-specific protocols in the DbOracle namespace.

    Architecture:
    - EXTENDS: FlextProtocols (inherits Foundation, Domain, Application, etc.)
    - ADDS: Oracle-specific protocols in DbOracle namespace

    Usage:
    from flext_db_oracle.protocols import FlextDbOracleProtocols

    # Foundation protocols (inherited)
    result: FlextDbOracleProtocols.Result[str]
    service: FlextDbOracleProtocols.Service[str]

    # Oracle-specific protocols
    connection: FlextDbOracleProtocols.Database.Connection
    query: FlextDbOracleProtocols.Database.QueryExecutor
    """

    class DbOracle:
        """Oracle database domain-specific protocols."""

        @runtime_checkable
        class YamlModule(Protocol):
            """Protocol for YAML module interface."""

            def dump(
                self,
                data: Mapping[str, t.NormalizedValue] | Sequence[t.NormalizedValue],
                *,
                default_flow_style: bool = True,
            ) -> str:
                """Dump data as YAML string."""
                ...

        @runtime_checkable
        class Connection(Protocol):
            """Protocol for Oracle database connection operations."""

            def connect(self) -> r[bool]:
                """Establish Oracle database connection.

                Returns:
                r[bool]: Connection success status

                """
                ...

            def disconnect(self) -> r[bool]:
                """Close Oracle database connection.

                Returns:
                r[bool]: Disconnection success status

                """
                ...

            def is_connected(self) -> r[bool]:
                """Check if Oracle connection is active.

                Returns:
                r[bool]: Connection status

                """
                ...

        @runtime_checkable
        class OraclePlugin(Protocol):
            """Protocol for Oracle database plugins.

            All plugins registered with the FlextDbOracle plugin system
            must satisfy this protocol.
            """

            def get_connection(self) -> r[t.ContainerValue]:
                """Get current Oracle connection t.NormalizedValue.

                Returns:
                r: Connection t.NormalizedValue or error

                """
                ...

            def initialize(self) -> r[bool]:
                """Initialize the plugin."""
                ...

            def shutdown(self) -> r[bool]:
                """Shutdown the plugin."""
                ...

            def test_connection(self) -> r[bool]:
                """Test Oracle database connectivity.

                Returns:
                r[bool]: Connection test result

                """
                ...

        @runtime_checkable
        class QueryExecutor(Protocol):
            """Protocol for Oracle query execution operations."""

            def execute_many(
                self,
                sql: str,
                params_list: Sequence[Mapping[str, t.ContainerValue]],
            ) -> r[int]:
                """Execute Oracle SQL statement with multiple parameter sets.

                Args:
                sql: SQL statement string
                params_list: List of parameter dictionaries

                Returns:
                r[int]: Number of affected rows

                """
                ...

            def execute_query(
                self,
                sql: str,
                params: Mapping[str, t.ContainerValue] | None = None,
            ) -> r[Sequence[t.Dict]]:
                """Execute Oracle SQL query.

                Args:
                sql: SQL query string
                params: Query parameters

                Returns:
                r: Query result or error

                """
                ...

            def execute_statement(
                self,
                sql: str,
                params: Mapping[str, t.ContainerValue] | None = None,
            ) -> r[bool]:
                """Execute Oracle SQL statement.

                Args:
                sql: SQL statement string
                params: Statement parameters

                Returns:
                r[bool]: Execution success status

                """
                ...

            def fetch_one(
                self,
                sql: str,
                params: Mapping[str, t.ContainerValue] | None = None,
            ) -> r[t.Dict | None]:
                """Fetch single result from Oracle query.

                Args:
                sql: SQL query string
                params: Query parameters

                Returns:
                r[t.Dict | None]: Single result or None

                """
                ...

        @runtime_checkable
        class SchemaIntrospector(Protocol):
            """Protocol for Oracle schema introspection operations."""

            def get_columns(
                self,
                table: str,
                schema: str | None = None,
            ) -> r[Sequence[m.DbOracle.Column]]:
                """Get column information for Oracle table.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[Sequence[Mapping[str, t.ContainerValue]]]: Column metadata or error

                """
                ...

            def get_primary_keys(
                self,
                table: str,
                schema: str | None = None,
            ) -> r[Sequence[str]]:
                """Get primary key columns for Oracle table.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[Sequence[str]]: Primary key column names or error

                """
                ...

            def get_schemas(self) -> r[Sequence[str]]:
                """Get list of Oracle schemas.

                Returns:
                r[Sequence[str]]: Schema names or error

                """
                ...

            def get_table_metadata(
                self,
                table: str,
                schema: str | None = None,
            ) -> r[m.DbOracle.TableMetadata]:
                """Get Oracle table metadata.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[Mapping[str, t.ContainerValue]]: Table metadata or error

                """
                ...

            def get_tables(self, schema: str | None = None) -> r[Sequence[str]]:
                """Get list of tables in Oracle schema.

                Args:
                schema: Schema name (optional)

                Returns:
                r[Sequence[str]]: Table names or error

                """
                ...

        @runtime_checkable
        class SqlBuilder(Protocol):
            """Protocol for Oracle SQL statement building operations."""

            def build_delete_statement(self, table: str, where_clause: str) -> r[str]:
                """Build Oracle DELETE statement.

                Args:
                table: Table name
                where_clause: WHERE condition

                Returns:
                r[str]: SQL DELETE statement or error

                """
                ...

            def build_insert_statement(
                self,
                table: str,
                data: Mapping[str, t.ContainerValue],
            ) -> r[tuple[str, Mapping[str, t.ContainerValue]]]:
                """Build Oracle INSERT statement.

                Args:
                table: Table name
                data: Column data

                Returns:
                r[tuple[str, Mapping[str, t.ContainerValue]]]: SQL and parameters or error

                """
                ...

            def build_select(
                self,
                table: str,
                columns: Sequence[str] | None = None,
                where_clause: str | None = None,
                order_by: str | None = None,
                limit: int | None = None,
            ) -> r[str]:
                """Build Oracle SELECT statement.

                Args:
                table: Table name
                columns: Column names (optional)
                where_clause: WHERE condition (optional)
                order_by: ORDER BY clause (optional)
                limit: Row limit (optional)

                Returns:
                r[str]: SQL SELECT statement or error

                """
                ...

            def build_update_statement(
                self,
                table: str,
                data: Mapping[str, t.ContainerValue],
                where_clause: str,
            ) -> r[tuple[str, Mapping[str, t.ContainerValue]]]:
                """Build Oracle UPDATE statement.

                Args:
                table: Table name
                data: Column data
                where_clause: WHERE condition

                Returns:
                r[tuple[str, Mapping[str, t.ContainerValue]]]: SQL and parameters or error

                """
                ...

        @runtime_checkable
        class DdlGenerator(Protocol):
            """Protocol for Oracle DDL generation operations."""

            def build_create_index_statement(
                self,
                table: str,
                columns: Sequence[str],
                index_name: str | None = None,
                *,
                unique: bool = False,
            ) -> r[str]:
                """Build Oracle CREATE INDEX statement.

                Args:
                table: Table name
                columns: Index columns
                index_name: Index name (optional)
                unique: Create unique index

                Returns:
                r[str]: CREATE INDEX statement or error

                """
                ...

            def create_table_ddl(
                self,
                table: str,
                columns: Sequence[m.DbOracle.Column],
                schema: str | None = None,
            ) -> r[str]:
                """Generate Oracle CREATE TABLE DDL.

                Args:
                table: Table name
                columns: Column definitions
                schema: Schema name (optional)

                Returns:
                r[str]: CREATE TABLE DDL or error

                """
                ...

            def drop_table_ddl(self, table: str, schema: str | None = None) -> r[str]:
                """Generate Oracle DROP TABLE DDL.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[str]: DROP TABLE DDL or error

                """
                ...

        @runtime_checkable
        class MetricsCollector(Protocol):
            """Protocol for Oracle database metrics collection."""

            def get_metrics(self) -> r[m.DbOracle.HealthStatus]:
                """Get collected Oracle metrics.

                Returns:
                r[Mapping[str, t.ContainerValue]]: Metrics data or error

                """
                ...

            def record_metric(
                self,
                name: str,
                value: float,
                tags: Mapping[str, str] | None = None,
            ) -> r[bool]:
                """Record Oracle database metric.

                Args:
                name: Metric name
                value: Metric value
                tags: Metric tags (optional)

                Returns:
                r[bool]: Success status

                """
                ...

            def track_operation(
                self,
                operation: str,
                duration: float,
                *,
                success: bool,
            ) -> r[bool]:
                """Track Oracle operation performance.

                Args:
                operation: Operation name
                duration: Operation duration
                success: Operation success status

                Returns:
                r[bool]: Tracking success status

                """
                ...

        @runtime_checkable
        class PluginRegistry(Protocol):
            """Protocol for Oracle database plugin registry operations."""

            def get_plugin(self, name: str) -> r[t.ContainerValue]:
                """Get Oracle database plugin by name.

                Args:
                name: Plugin name

                Returns:
                r: Plugin instance or error

                """
                ...

            def list_plugins(self) -> r[Sequence[str]]:
                """List registered Oracle database plugins.

                Returns:
                r[Sequence[str]]: Plugin names or error

                """
                ...

            def register_plugin(self, name: str, _plugin: t.ContainerValue) -> r[bool]:
                """Register Oracle database plugin.

                Args:
                name: Plugin name
                plugin: Plugin instance

                Returns:
                r[bool]: Registration success status

                """
                ...

            def unregister_plugin(self, name: str) -> r[bool]:
                """Unregister Oracle database plugin.

                Args:
                name: Plugin name

                Returns:
                r[bool]: Unregistration success status

                """
                ...

        @runtime_checkable
        class HealthCheck(Protocol):
            """Protocol for Oracle database health check operations."""

            def get_connection_status(self) -> r[m.DbOracle.ConnectionStatus]:
                """Get Oracle connection status information.

                Returns:
                r[Mapping[str, t.ContainerValue]]: Connection status or error

                """
                ...

            def health_check(self) -> r[m.DbOracle.HealthStatus]:
                """Perform Oracle database health check.

                Returns:
                r[Mapping[str, t.ContainerValue]]: Health status or error

                """
                ...


__all__ = ["FlextDbOracleProtocols", "p"]

p = FlextDbOracleProtocols

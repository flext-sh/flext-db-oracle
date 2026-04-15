"""Oracle Database protocols for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from flext_core import p
from flext_db_oracle import m, t


class FlextDbOracleProtocols(p):
    """Oracle database protocols extending FlextProtocols.

    Extends FlextProtocols to inherit all foundation protocols (Result, Service, etc.)
    and adds Oracle-specific protocols in the DbOracle namespace.

    Architecture:
    - EXTENDS: FlextProtocols (inherits Foundation, Domain, Application, etc.)
    - ADDS: Oracle-specific protocols in DbOracle namespace

    Usage:
    from flext_db_oracle import FlextDbOracleProtocols

    # Foundation protocols (inherited)
    result: FlextDbOracleProtocols.Result[str]
    service: FlextDbOracleProtocols.Service[str]

    # Oracle-specific protocols
    connection: FlextDbOracleProtocols.Database.Connection
    query: FlextDbOracleProtocols.Database.QueryExecutor
    """

    @runtime_checkable
    class DbOracle(Protocol):
        """Oracle database domain-specific protocols."""

        @runtime_checkable
        class Connection(Protocol):
            """Protocol for Oracle database connection operations."""

            def connect(self) -> p.Result[bool]:
                """Establish Oracle database connection.

                Returns:
                r[bool]: Connection success status

                """
                ...

            def disconnect(self) -> p.Result[bool]:
                """Close Oracle database connection.

                Returns:
                r[bool]: Disconnection success status

                """
                ...

            def connected(self) -> p.Result[bool]:
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

            def get_connection(self) -> p.Result[t.ContainerValue]:
                """Get current Oracle connection t.RecursiveContainer.

                Returns:
                r: Connection t.RecursiveContainer or error

                """
                ...

            def initialize(self) -> p.Result[bool]:
                """Initialize the plugin."""
                ...

            def shutdown(self) -> p.Result[bool]:
                """Shutdown the plugin."""
                ...

            def test_connection(self) -> p.Result[bool]:
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
                params_list: Sequence[t.ContainerValueMapping],
            ) -> p.Result[int]:
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
                params: t.ContainerValueMapping | None = None,
            ) -> p.Result[Sequence[t.Dict]]:
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
                params: t.ContainerValueMapping | None = None,
            ) -> p.Result[bool]:
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
                params: t.ContainerValueMapping | None = None,
            ) -> p.Result[t.Dict | None]:
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
            ) -> p.Result[Sequence[m.DbOracle.Column]]:
                """Get column information for Oracle table.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[Sequence[t.ContainerValueMapping]]: Column metadata or error

                """
                ...

            def get_primary_keys(
                self,
                table: str,
                schema: str | None = None,
            ) -> p.Result[t.StrSequence]:
                """Get primary key columns for Oracle table.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[t.StrSequence]: Primary key column names or error

                """
                ...

            def get_schemas(self) -> p.Result[t.StrSequence]:
                """Get list of Oracle schemas.

                Returns:
                r[t.StrSequence]: Schema names or error

                """
                ...

            def get_table_metadata(
                self,
                table: str,
                schema: str | None = None,
            ) -> p.Result[m.DbOracle.TableMetadata]:
                """Get Oracle table metadata.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[t.ContainerValueMapping]: Table metadata or error

                """
                ...

            def get_tables(self, schema: str | None = None) -> p.Result[t.StrSequence]:
                """Get list of tables in Oracle schema.

                Args:
                schema: Schema name (optional)

                Returns:
                r[t.StrSequence]: Table names or error

                """
                ...

        @runtime_checkable
        class SqlBuilder(Protocol):
            """Protocol for Oracle SQL statement building operations."""

            def build_delete_statement(
                self, table: str, where_clause: str
            ) -> p.Result[str]:
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
                data: t.ContainerValueMapping,
            ) -> p.Result[tuple[str, t.ContainerValueMapping]]:
                """Build Oracle INSERT statement.

                Args:
                table: Table name
                data: Column data

                Returns:
                r[tuple[str, t.ContainerValueMapping]]: SQL and parameters or error

                """
                ...

            def build_select(
                self,
                table: str,
                columns: t.StrSequence | None = None,
                where_clause: str | None = None,
                order_by: str | None = None,
                limit: int | None = None,
            ) -> p.Result[str]:
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
                data: t.ContainerValueMapping,
                where_clause: str,
            ) -> p.Result[tuple[str, t.ContainerValueMapping]]:
                """Build Oracle UPDATE statement.

                Args:
                table: Table name
                data: Column data
                where_clause: WHERE condition

                Returns:
                r[tuple[str, t.ContainerValueMapping]]: SQL and parameters or error

                """
                ...

        @runtime_checkable
        class DdlGenerator(Protocol):
            """Protocol for Oracle DDL generation operations."""

            def build_create_index_statement(
                self,
                table: str,
                columns: t.StrSequence,
                index_name: str | None = None,
                *,
                unique: bool = False,
            ) -> p.Result[str]:
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
            ) -> p.Result[str]:
                """Generate Oracle CREATE TABLE DDL.

                Args:
                table: Table name
                columns: Column definitions
                schema: Schema name (optional)

                Returns:
                r[str]: CREATE TABLE DDL or error

                """
                ...

            def drop_table_ddl(
                self, table: str, schema: str | None = None
            ) -> p.Result[str]:
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

            def get_metrics(self) -> p.Result[m.DbOracle.HealthStatus]:
                """Get collected Oracle metrics.

                Returns:
                r[t.ContainerValueMapping]: Metrics data or error

                """
                ...

            def record_metric(
                self,
                name: str,
                value: float,
                tags: t.StrMapping | None = None,
            ) -> p.Result[bool]:
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
            ) -> p.Result[bool]:
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

            def get_plugin(self, name: str) -> p.Result[t.ContainerValue]:
                """Get Oracle database plugin by name.

                Args:
                name: Plugin name

                Returns:
                r: Plugin instance or error

                """
                ...

            def list_plugins(self) -> p.Result[t.StrSequence]:
                """List registered Oracle database plugins.

                Returns:
                r[t.StrSequence]: Plugin names or error

                """
                ...

            def register_plugin(
                self, name: str, _plugin: t.ContainerValue
            ) -> p.Result[bool]:
                """Register Oracle database plugin.

                Args:
                name: Plugin name
                plugin: Plugin instance

                Returns:
                r[bool]: Registration success status

                """
                ...

            def unregister_plugin(self, name: str) -> p.Result[bool]:
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

            def get_connection_status(self) -> p.Result[m.DbOracle.ConnectionStatus]:
                """Get Oracle connection status information.

                Returns:
                r[t.ContainerValueMapping]: Connection status or error

                """
                ...

            def health_check(self) -> p.Result[m.DbOracle.HealthStatus]:
                """Perform Oracle database health check.

                Returns:
                r[t.ContainerValueMapping]: Health status or error

                """
                ...


p = FlextDbOracleProtocols

__all__: list[str] = ["FlextDbOracleProtocols", "p"]

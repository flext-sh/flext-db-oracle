"""Oracle Database protocols for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core.protocols import p as core_protocols
from flext_db_oracle.models import m as m_db_oracle
from flext_db_oracle.typings import t


class FlextDbOracleProtocols(core_protocols):
    """Oracle database protocols extending core_protocols.

    Extends p to inherit all foundation protocols (Result, Service, etc.)
    and adds Oracle-specific protocols in the Database namespace.

    Architecture:
    - EXTENDS: p (inherits Foundation, Domain, Application, etc.)
    - ADDS: Oracle-specific protocols in Database namespace
    - PROVIDES: Root-level alias `p` for convenient access

    Usage:
    from flext_db_oracle.protocols import p

    # Foundation protocols (inherited)
    result: core_protocols.Result[str]
    service: core_protocols.Service[str]

    # Oracle-specific protocols
    connection: core_protocols.Database.ConnectionProtocol
    query: core_protocols.Database.QueryExecutorProtocol
    """

    # =========================================================================
    # INHERITED FOUNDATION PROTOCOLS - Available from p
    # =========================================================================
    # Foundation, Domain, Application, Infrastructure, Extensions, Commands
    # are all inherited from p parent class

    # =========================================================================
    # ORACLE DATABASE-SPECIFIC PROTOCOLS - Domain extension for database operations
    # =========================================================================

    class DbOracle:
        """Oracle database domain-specific protocols."""

        @runtime_checkable
        class ConnectionProtocol(core_protocols.Service, Protocol):
            """Protocol for Oracle database connection operations."""

            def connect(self) -> core_protocols.Result[bool]:
                """Establish Oracle database connection.

                Returns:
                r[bool]: Connection success status

                """
                ...  # INTERFACE  # INTERFACE

            def disconnect(self) -> core_protocols.Result[bool]:
                """Close Oracle database connection.

                Returns:
                r[bool]: Disconnection success status

                """
                ...  # INTERFACE  # INTERFACE

            def is_connected(self) -> core_protocols.Result[bool]:
                """Check if Oracle connection is active.

                Returns:
                r[bool]: Connection status

                """
                ...  # INTERFACE  # INTERFACE

            def test_connection(self) -> core_protocols.Result[bool]:
                """Test Oracle database connectivity.

                Returns:
                r[bool]: Connection test result

                """
                ...  # INTERFACE  # INTERFACE

            def get_connection(self) -> core_protocols.Result[t.JsonValue]:
                """Get current Oracle connection object.

                Returns:
                r[t.JsonValue]: Connection object or error

                """
                ...  # INTERFACE  # INTERFACE

        @runtime_checkable
        class QueryExecutorProtocol(core_protocols.Service, Protocol):
            """Protocol for Oracle query execution operations."""

            def execute_query(
                self,
                sql: str,
                params: dict[str, t.JsonValue] | None = None,
            ) -> core_protocols.Result[t.JsonValue]:
                """Execute Oracle SQL query.

                Args:
                sql: SQL query string
                params: Query parameters

                Returns:
                r[t.JsonValue]: Query result or error

                """
                ...  # INTERFACE  # INTERFACE

            def execute_statement(
                self,
                sql: str,
                params: dict[str, t.JsonValue] | None = None,
            ) -> core_protocols.Result[bool]:
                """Execute Oracle SQL statement.

                Args:
                sql: SQL statement string
                params: Statement parameters

                Returns:
                r[bool]: Execution success status

                """
                ...  # INTERFACE  # INTERFACE

            def execute_many(
                self,
                sql: str,
                params_list: list[dict[str, t.JsonValue]],
            ) -> core_protocols.Result[int]:
                """Execute Oracle SQL statement with multiple parameter sets.

                Args:
                sql: SQL statement string
                params_list: List of parameter dictionaries

                Returns:
                r[int]: Number of affected rows

                """
                ...  # INTERFACE  # INTERFACE

            def fetch_one(
                self,
                sql: str,
                params: dict[str, t.JsonValue] | None = None,
            ) -> core_protocols.Result[t.JsonValue | None]:
                """Fetch single result from Oracle query.

                Args:
                sql: SQL query string
                params: Query parameters

                Returns:
                r[t.JsonValue | None]: Single result or None

                """
                ...  # INTERFACE

        @runtime_checkable
        class SchemaIntrospectorProtocol(core_protocols.Service, Protocol):
            """Protocol for Oracle schema introspection operations."""

            def get_schemas(self) -> core_protocols.Result[list[str]]:
                """Get list of Oracle schemas.

                Returns:
                r[list[str]]: Schema names or error

                """
                ...  # INTERFACE

            def get_tables(
                self,
                schema: str | None = None,
            ) -> core_protocols.Result[list[str]]:
                """Get list of tables in Oracle schema.

                Args:
                schema: Schema name (optional)

                Returns:
                r[list[str]]: Table names or error

                """
                ...  # INTERFACE

            def get_columns(
                self,
                table: str,
                schema: str | None = None,
            ) -> core_protocols.Result[list[m_db_oracle.DbOracle.Column]]:
                """Get column information for Oracle table.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[list[dict[str, t.JsonValue]]]: Column metadata or error

                """
                ...  # INTERFACE

            def get_table_metadata(
                self,
                table: str,
                schema: str | None = None,
            ) -> core_protocols.Result[m_db_oracle.DbOracle.TableMetadata]:
                """Get Oracle table metadata.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[dict[str, t.JsonValue]]: Table metadata or error

                """
                ...  # INTERFACE

            def get_primary_keys(
                self,
                table: str,
                schema: str | None = None,
            ) -> core_protocols.Result[list[str]]:
                """Get primary key columns for Oracle table.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[list[str]]: Primary key column names or error

                """
                ...  # INTERFACE

        @runtime_checkable
        class SqlBuilderProtocol(core_protocols.Service, Protocol):
            """Protocol for Oracle SQL statement building operations."""

            def build_select(
                self,
                table: str,
                columns: list[str] | None = None,
                where_clause: str | None = None,
                order_by: str | None = None,
                limit: int | None = None,
            ) -> core_protocols.Result[str]:
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
                ...  # INTERFACE

            def build_insert_statement(
                self,
                table: str,
                data: dict[str, t.JsonValue],
            ) -> core_protocols.Result[tuple[str, dict[str, t.JsonValue]]]:
                """Build Oracle INSERT statement.

                Args:
                table: Table name
                data: Column data

                Returns:
                r[tuple[str, dict[str, t.JsonValue]]]: SQL and parameters or error

                """
                ...  # INTERFACE

            def build_update_statement(
                self,
                table: str,
                data: dict[str, t.JsonValue],
                where_clause: str,
            ) -> core_protocols.Result[tuple[str, dict[str, t.JsonValue]]]:
                """Build Oracle UPDATE statement.

                Args:
                table: Table name
                data: Column data
                where_clause: WHERE condition

                Returns:
                r[tuple[str, dict[str, t.JsonValue]]]: SQL and parameters or error

                """
                ...  # INTERFACE

            def build_delete_statement(
                self,
                table: str,
                where_clause: str,
            ) -> core_protocols.Result[str]:
                """Build Oracle DELETE statement.

                Args:
                table: Table name
                where_clause: WHERE condition

                Returns:
                r[str]: SQL DELETE statement or error

                """
                ...  # INTERFACE

        @runtime_checkable
        class DdlGeneratorProtocol(core_protocols.Service, Protocol):
            """Protocol for Oracle DDL generation operations."""

            def create_table_ddl(
                self,
                table: str,
                columns: list[m_db_oracle.DbOracle.Column],
                schema: str | None = None,
            ) -> core_protocols.Result[str]:
                """Generate Oracle CREATE TABLE DDL.

                Args:
                table: Table name
                columns: Column definitions
                schema: Schema name (optional)

                Returns:
                r[str]: CREATE TABLE DDL or error

                """
                ...  # INTERFACE

            def drop_table_ddl(
                self,
                table: str,
                schema: str | None = None,
            ) -> core_protocols.Result[str]:
                """Generate Oracle DROP TABLE DDL.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[str]: DROP TABLE DDL or error

                """
                ...  # INTERFACE

            def build_create_index_statement(
                self,
                table: str,
                columns: list[str],
                index_name: str | None = None,
                *,
                unique: bool = False,
            ) -> core_protocols.Result[str]:
                """Build Oracle CREATE INDEX statement.

                Args:
                table: Table name
                columns: Index columns
                index_name: Index name (optional)
                unique: Create unique index

                Returns:
                r[str]: CREATE INDEX statement or error

                """
                ...  # INTERFACE

        @runtime_checkable
        class MetricsCollectorProtocol(core_protocols.Service, Protocol):
            """Protocol for Oracle database metrics collection."""

            def record_metric(
                self,
                name: str,
                value: float,
                tags: dict[str, str] | None = None,
            ) -> core_protocols.Result[bool]:
                """Record Oracle database metric.

                Args:
                name: Metric name
                value: Metric value
                tags: Metric tags (optional)

                Returns:
                r[bool]: Success status

                """
                ...  # INTERFACE

            def get_metrics(
                self,
            ) -> core_protocols.Result[m_db_oracle.DbOracle.HealthStatus]:
                """Get collected Oracle metrics.

                Returns:
                r[dict[str, t.JsonValue]]: Metrics data or error

                """
                ...  # INTERFACE

            def track_operation(
                self,
                operation: str,
                duration: float,
                *,
                success: bool,
            ) -> core_protocols.Result[bool]:
                """Track Oracle operation performance.

                Args:
                operation: Operation name
                duration: Operation duration
                success: Operation success status

                Returns:
                r[bool]: Tracking success status

                """
                ...  # INTERFACE

        @runtime_checkable
        class PluginRegistryProtocol(core_protocols.Service, Protocol):
            """Protocol for Oracle database plugin registry operations."""

            def register_plugin(
                self,
                name: str,
                _plugin: t.JsonValue,
            ) -> core_protocols.Result[bool]:
                """Register Oracle database plugin.

                Args:
                name: Plugin name
                plugin: Plugin instance

                Returns:
                r[bool]: Registration success status

                """
                ...  # INTERFACE

            def unregister_plugin(self, name: str) -> core_protocols.Result[bool]:
                """Unregister Oracle database plugin.

                Args:
                name: Plugin name

                Returns:
                r[bool]: Unregistration success status

                """
                ...  # INTERFACE

            def get_plugin(self, name: str) -> core_protocols.Result[t.JsonValue]:
                """Get Oracle database plugin by name.

                Args:
                name: Plugin name

                Returns:
                r[t.JsonValue]: Plugin instance or error

                """
                ...  # INTERFACE

            def list_plugins(self) -> core_protocols.Result[list[str]]:
                """List registered Oracle database plugins.

                Returns:
                r[list[str]]: Plugin names or error

                """
                ...  # INTERFACE

        @runtime_checkable
        class HealthCheckProtocol(core_protocols.Service, Protocol):
            """Protocol for Oracle database health check operations."""

            def health_check(
                self,
            ) -> core_protocols.Result[m_db_oracle.DbOracle.HealthStatus]:
                """Perform Oracle database health check.

                Returns:
                r[dict[str, t.JsonValue]]: Health status or error

                """
                ...  # INTERFACE

            def get_connection_status(
                self,
            ) -> core_protocols.Result[m_db_oracle.DbOracle.ConnectionStatus]:
                """Get Oracle connection status information.

                Returns:
                r[dict[str, t.JsonValue]]: Connection status or error

                """
                ...  # INTERFACE


# Runtime alias for simplified usage
p = FlextDbOracleProtocols

__all__ = [
    "FlextDbOracleProtocols",
    "p",
]

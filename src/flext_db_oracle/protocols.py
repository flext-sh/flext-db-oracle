"""Oracle Database protocols for FLEXT ecosystem."""

from typing import Protocol, runtime_checkable

from flext_core import FlextResult, p, t


class FlextDbOracleProtocols(p):
    """Oracle database protocols extending p foundation.

    Extends p with Oracle-specific protocol definitions
    while inheriting all foundation protocols. Follows FLEXT namespace pattern.
    """

    # =========================================================================
    # INHERITED FOUNDATION PROTOCOLS - Available from p
    # =========================================================================
    # Foundation, Domain, Application, Infrastructure, Extensions, Commands
    # are all inherited from p parent class

    # =========================================================================
    # ORACLE DATABASE-SPECIFIC PROTOCOLS - Domain extension for database operations
    # =========================================================================

    class Database:
        """Oracle database domain-specific protocols."""

        @runtime_checkable
        class ConnectionProtocol(p.Service, Protocol):
            """Protocol for Oracle database connection operations."""

            def connect(self) -> FlextResult[bool]:
                """Establish Oracle database connection.

                Returns:
                FlextResult[bool]: Connection success status

                """
                ...
                ...

            def disconnect(self) -> FlextResult[bool]:
                """Close Oracle database connection.

                Returns:
                FlextResult[bool]: Disconnection success status

                """
                ...
                ...

            def is_connected(self) -> FlextResult[bool]:
                """Check if Oracle connection is active.

                Returns:
                FlextResult[bool]: Connection status

                """
                ...
                ...

            def test_connection(self) -> FlextResult[bool]:
                """Test Oracle database connectivity.

                Returns:
                FlextResult[bool]: Connection test result

                """
                ...
                ...

            def get_connection(self) -> FlextResult[object]:
                """Get current Oracle connection object.

                Returns:
                FlextResult[object]: Connection object or error

                """
                ...
                ...

        @runtime_checkable
        class QueryExecutorProtocol(p.Service, Protocol):
            """Protocol for Oracle query execution operations."""

            def execute_query(
                self, sql: str, params: dict[str, t.JsonValue] | None = None
            ) -> FlextResult[object]:
                """Execute Oracle SQL query.

                Args:
                sql: SQL query string
                params: Query parameters

                Returns:
                FlextResult[object]: Query result or error

                """
                ...
                ...

            def execute_statement(
                self, sql: str, params: dict[str, t.JsonValue] | None = None
            ) -> FlextResult[bool]:
                """Execute Oracle SQL statement.

                Args:
                sql: SQL statement string
                params: Statement parameters

                Returns:
                FlextResult[bool]: Execution success status

                """
                ...
                ...

            def execute_many(
                self, sql: str, params_list: list[dict[str, t.JsonValue]]
            ) -> FlextResult[int]:
                """Execute Oracle SQL statement with multiple parameter sets.

                Args:
                sql: SQL statement string
                params_list: List of parameter dictionaries

                Returns:
                FlextResult[int]: Number of affected rows

                """
                ...
                ...

            def fetch_one(
                self, sql: str, params: dict[str, t.JsonValue] | None = None
            ) -> FlextResult[t.JsonValue | None]:
                """Fetch single result from Oracle query.

                Args:
                sql: SQL query string
                params: Query parameters

                Returns:
                FlextResult[object | None]: Single result or None

                """
                ...

        @runtime_checkable
        class SchemaIntrospectorProtocol(p.Service, Protocol):
            """Protocol for Oracle schema introspection operations."""

            def get_schemas(self) -> FlextResult[list[str]]:
                """Get list of Oracle schemas.

                Returns:
                FlextResult[list[str]]: Schema names or error

                """
                ...

            def get_tables(self, schema: str | None = None) -> FlextResult[list[str]]:
                """Get list of tables in Oracle schema.

                Args:
                schema: Schema name (optional)

                Returns:
                FlextResult[list[str]]: Table names or error

                """
                ...

            def get_columns(
                self, table: str, schema: str | None = None
            ) -> FlextResult[list[dict[str, t.JsonValue]]]:
                """Get column information for Oracle table.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                FlextResult[list[dict[str, t.JsonValue]]]: Column metadata or error

                """
                ...

            def get_table_metadata(
                self, table: str, schema: str | None = None
            ) -> FlextResult[dict[str, t.JsonValue]]:
                """Get Oracle table metadata.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                FlextResult[dict[str, t.JsonValue]]: Table metadata or error

                """
                ...

            def get_primary_keys(
                self, table: str, schema: str | None = None
            ) -> FlextResult[list[str]]:
                """Get primary key columns for Oracle table.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                FlextResult[list[str]]: Primary key column names or error

                """
                ...

        @runtime_checkable
        class SqlBuilderProtocol(p.Service, Protocol):
            """Protocol for Oracle SQL statement building operations."""

            def build_select(
                self,
                table: str,
                columns: list[str] | None = None,
                where_clause: str | None = None,
                order_by: str | None = None,
                limit: int | None = None,
            ) -> FlextResult[str]:
                """Build Oracle SELECT statement.

                Args:
                table: Table name
                columns: Column names (optional)
                where_clause: WHERE condition (optional)
                order_by: ORDER BY clause (optional)
                limit: Row limit (optional)

                Returns:
                FlextResult[str]: SQL SELECT statement or error

                """
                ...

            def build_insert_statement(
                self, table: str, data: dict[str, t.JsonValue]
            ) -> FlextResult[tuple[str, dict[str, t.JsonValue]]]:
                """Build Oracle INSERT statement.

                Args:
                table: Table name
                data: Column data

                Returns:
                FlextResult[tuple[str, dict[str, t.JsonValue]]]: SQL and parameters or error

                """
                ...

            def build_update_statement(
                self,
                table: str,
                data: dict[str, t.JsonValue],
                where_clause: str,
            ) -> FlextResult[tuple[str, dict[str, t.JsonValue]]]:
                """Build Oracle UPDATE statement.

                Args:
                table: Table name
                data: Column data
                where_clause: WHERE condition

                Returns:
                FlextResult[tuple[str, dict[str, t.JsonValue]]]: SQL and parameters or error

                """
                ...

            def build_delete_statement(
                self, table: str, where_clause: str
            ) -> FlextResult[str]:
                """Build Oracle DELETE statement.

                Args:
                table: Table name
                where_clause: WHERE condition

                Returns:
                FlextResult[str]: SQL DELETE statement or error

                """
                ...

        @runtime_checkable
        class DdlGeneratorProtocol(p.Service, Protocol):
            """Protocol for Oracle DDL generation operations."""

            def create_table_ddl(
                self,
                table: str,
                columns: list[dict[str, t.JsonValue]],
                schema: str | None = None,
            ) -> FlextResult[str]:
                """Generate Oracle CREATE TABLE DDL.

                Args:
                table: Table name
                columns: Column definitions
                schema: Schema name (optional)

                Returns:
                FlextResult[str]: CREATE TABLE DDL or error

                """
                ...

            def drop_table_ddl(
                self, table: str, schema: str | None = None
            ) -> FlextResult[str]:
                """Generate Oracle DROP TABLE DDL.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                FlextResult[str]: DROP TABLE DDL or error

                """
                ...

            def build_create_index_statement(
                self,
                table: str,
                columns: list[str],
                index_name: str | None = None,
                *,
                unique: bool = False,
            ) -> FlextResult[str]:
                """Build Oracle CREATE INDEX statement.

                Args:
                table: Table name
                columns: Index columns
                index_name: Index name (optional)
                unique: Create unique index

                Returns:
                FlextResult[str]: CREATE INDEX statement or error

                """
                ...

        @runtime_checkable
        class MetricsCollectorProtocol(p.Service, Protocol):
            """Protocol for Oracle database metrics collection."""

            def record_metric(
                self,
                name: str,
                value: float,
                tags: dict[str, str] | None = None,
            ) -> FlextResult[bool]:
                """Record Oracle database metric.

                Args:
                name: Metric name
                value: Metric value
                tags: Metric tags (optional)

                Returns:
                FlextResult[bool]: Success status

                """
                ...

            def get_metrics(self) -> FlextResult[dict[str, t.JsonValue]]:
                """Get collected Oracle metrics.

                Returns:
                FlextResult[dict[str, t.JsonValue]]: Metrics data or error

                """
                ...

            def track_operation(
                self, operation: str, duration: float, *, success: bool
            ) -> FlextResult[bool]:
                """Track Oracle operation performance.

                Args:
                operation: Operation name
                duration: Operation duration
                success: Operation success status

                Returns:
                FlextResult[bool]: Tracking success status

                """
                ...

        @runtime_checkable
        class PluginRegistryProtocol(p.Service, Protocol):
            """Protocol for Oracle database plugin registry operations."""

            def register_plugin(self, name: str, _plugin: object) -> FlextResult[bool]:
                """Register Oracle database plugin.

                Args:
                name: Plugin name
                plugin: Plugin instance

                Returns:
                FlextResult[bool]: Registration success status

                """
                ...

            def unregister_plugin(self, name: str) -> FlextResult[bool]:
                """Unregister Oracle database plugin.

                Args:
                name: Plugin name

                Returns:
                FlextResult[bool]: Unregistration success status

                """
                ...

            def get_plugin(self, name: str) -> FlextResult[object]:
                """Get Oracle database plugin by name.

                Args:
                name: Plugin name

                Returns:
                FlextResult[object]: Plugin instance or error

                """
                ...

            def list_plugins(self) -> FlextResult[list[str]]:
                """List registered Oracle database plugins.

                Returns:
                FlextResult[list[str]]: Plugin names or error

                """
                ...

        @runtime_checkable
        class HealthCheckProtocol(p.Service, Protocol):
            """Protocol for Oracle database health check operations."""

            def health_check(self) -> FlextResult[dict[str, t.JsonValue]]:
                """Perform Oracle database health check.

                Returns:
                FlextResult[dict[str, t.JsonValue]]: Health status or error

                """
                ...

            def get_connection_status(
                self,
            ) -> FlextResult[dict[str, t.JsonValue]]:
                """Get Oracle connection status information.

                Returns:
                FlextResult[dict[str, t.JsonValue]]: Connection status or error

                """
                ...


# NO ALIASES - STRICT RULE: only use direct imports from protocols module
# All usage must be: FlextDbOracleProtocols.Database.ConnectionProtocol
# NOT: FlextDbOracleProtocols.OracleConnectionProtocol


__all__ = [
    "FlextDbOracleProtocols",
]

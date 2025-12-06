"""Oracle Database protocols for FLEXT ecosystem."""

from typing import Protocol, runtime_checkable

from flext_core import p as p_core, r, t


class FlextDbOracleProtocols(p_core):
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
        class ConnectionProtocol(p_core.Service, Protocol):
            """Protocol for Oracle database connection operations."""

            def connect(self) -> r[bool]:
                """Establish Oracle database connection.

                Returns:
                r[bool]: Connection success status

                """
                ...
                ...

            def disconnect(self) -> r[bool]:
                """Close Oracle database connection.

                Returns:
                r[bool]: Disconnection success status

                """
                ...
                ...

            def is_connected(self) -> r[bool]:
                """Check if Oracle connection is active.

                Returns:
                r[bool]: Connection status

                """
                ...
                ...

            def test_connection(self) -> r[bool]:
                """Test Oracle database connectivity.

                Returns:
                r[bool]: Connection test result

                """
                ...
                ...

            def get_connection(self) -> r[object]:
                """Get current Oracle connection object.

                Returns:
                r[object]: Connection object or error

                """
                ...
                ...

        @runtime_checkable
        class QueryExecutorProtocol(p_core.Service, Protocol):
            """Protocol for Oracle query execution operations."""

            def execute_query(
                self,
                sql: str,
                params: dict[str, t.JsonValue] | None = None,
            ) -> r[object]:
                """Execute Oracle SQL query.

                Args:
                sql: SQL query string
                params: Query parameters

                Returns:
                r[object]: Query result or error

                """
                ...
                ...

            def execute_statement(
                self,
                sql: str,
                params: dict[str, t.JsonValue] | None = None,
            ) -> r[bool]:
                """Execute Oracle SQL statement.

                Args:
                sql: SQL statement string
                params: Statement parameters

                Returns:
                r[bool]: Execution success status

                """
                ...
                ...

            def execute_many(
                self,
                sql: str,
                params_list: list[dict[str, t.JsonValue]],
            ) -> r[int]:
                """Execute Oracle SQL statement with multiple parameter sets.

                Args:
                sql: SQL statement string
                params_list: List of parameter dictionaries

                Returns:
                r[int]: Number of affected rows

                """
                ...
                ...

            def fetch_one(
                self,
                sql: str,
                params: dict[str, t.JsonValue] | None = None,
            ) -> r[t.JsonValue | None]:
                """Fetch single result from Oracle query.

                Args:
                sql: SQL query string
                params: Query parameters

                Returns:
                r[object | None]: Single result or None

                """
                ...

        @runtime_checkable
        class SchemaIntrospectorProtocol(p_core.Service, Protocol):
            """Protocol for Oracle schema introspection operations."""

            def get_schemas(self) -> r[list[str]]:
                """Get list of Oracle schemas.

                Returns:
                r[list[str]]: Schema names or error

                """
                ...

            def get_tables(self, schema: str | None = None) -> r[list[str]]:
                """Get list of tables in Oracle schema.

                Args:
                schema: Schema name (optional)

                Returns:
                r[list[str]]: Table names or error

                """
                ...

            def get_columns(
                self,
                table: str,
                schema: str | None = None,
            ) -> r[list[dict[str, t.JsonValue]]]:
                """Get column information for Oracle table.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[list[dict[str, t.JsonValue]]]: Column metadata or error

                """
                ...

            def get_table_metadata(
                self,
                table: str,
                schema: str | None = None,
            ) -> r[dict[str, t.JsonValue]]:
                """Get Oracle table metadata.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[dict[str, t.JsonValue]]: Table metadata or error

                """
                ...

            def get_primary_keys(
                self,
                table: str,
                schema: str | None = None,
            ) -> r[list[str]]:
                """Get primary key columns for Oracle table.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[list[str]]: Primary key column names or error

                """
                ...

        @runtime_checkable
        class SqlBuilderProtocol(p_core.Service, Protocol):
            """Protocol for Oracle SQL statement building operations."""

            def build_select(
                self,
                table: str,
                columns: list[str] | None = None,
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

            def build_insert_statement(
                self,
                table: str,
                data: dict[str, t.JsonValue],
            ) -> r[tuple[str, dict[str, t.JsonValue]]]:
                """Build Oracle INSERT statement.

                Args:
                table: Table name
                data: Column data

                Returns:
                r[tuple[str, dict[str, t.JsonValue]]]: SQL and parameters or error

                """
                ...

            def build_update_statement(
                self,
                table: str,
                data: dict[str, t.JsonValue],
                where_clause: str,
            ) -> r[tuple[str, dict[str, t.JsonValue]]]:
                """Build Oracle UPDATE statement.

                Args:
                table: Table name
                data: Column data
                where_clause: WHERE condition

                Returns:
                r[tuple[str, dict[str, t.JsonValue]]]: SQL and parameters or error

                """
                ...

            def build_delete_statement(
                self,
                table: str,
                where_clause: str,
            ) -> r[str]:
                """Build Oracle DELETE statement.

                Args:
                table: Table name
                where_clause: WHERE condition

                Returns:
                r[str]: SQL DELETE statement or error

                """
                ...

        @runtime_checkable
        class DdlGeneratorProtocol(p_core.Service, Protocol):
            """Protocol for Oracle DDL generation operations."""

            def create_table_ddl(
                self,
                table: str,
                columns: list[dict[str, t.JsonValue]],
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

            def drop_table_ddl(
                self,
                table: str,
                schema: str | None = None,
            ) -> r[str]:
                """Generate Oracle DROP TABLE DDL.

                Args:
                table: Table name
                schema: Schema name (optional)

                Returns:
                r[str]: DROP TABLE DDL or error

                """
                ...

            def build_create_index_statement(
                self,
                table: str,
                columns: list[str],
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

        @runtime_checkable
        class MetricsCollectorProtocol(p_core.Service, Protocol):
            """Protocol for Oracle database metrics collection."""

            def record_metric(
                self,
                name: str,
                value: float,
                tags: dict[str, str] | None = None,
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

            def get_metrics(self) -> r[dict[str, t.JsonValue]]:
                """Get collected Oracle metrics.

                Returns:
                r[dict[str, t.JsonValue]]: Metrics data or error

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
        class PluginRegistryProtocol(p_core.Service, Protocol):
            """Protocol for Oracle database plugin registry operations."""

            def register_plugin(self, name: str, _plugin: object) -> r[bool]:
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

            def get_plugin(self, name: str) -> r[object]:
                """Get Oracle database plugin by name.

                Args:
                name: Plugin name

                Returns:
                r[object]: Plugin instance or error

                """
                ...

            def list_plugins(self) -> r[list[str]]:
                """List registered Oracle database plugins.

                Returns:
                r[list[str]]: Plugin names or error

                """
                ...

        @runtime_checkable
        class HealthCheckProtocol(p_core.Service, Protocol):
            """Protocol for Oracle database health check operations."""

            def health_check(self) -> r[dict[str, t.JsonValue]]:
                """Perform Oracle database health check.

                Returns:
                r[dict[str, t.JsonValue]]: Health status or error

                """
                ...

            def get_connection_status(
                self,
            ) -> r[dict[str, t.JsonValue]]:
                """Get Oracle connection status information.

                Returns:
                r[dict[str, t.JsonValue]]: Connection status or error

                """
                ...


# NO ALIASES - STRICT RULE: only use direct imports from protocols module
# All usage must be: FlextDbOracleProtocols.Database.ConnectionProtocol
# NOT: FlextDbOracleProtocols.OracleConnectionProtocol


__all__ = [
    "FlextDbOracleProtocols",
]

"""Oracle Database protocols for FLEXT ecosystem."""

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult


class FlextDbOracleProtocols(FlextProtocols):
    """Oracle Database protocols extending FlextProtocols with Oracle-specific interfaces.

    This class provides protocol definitions for Oracle database operations,
    connection management, query execution, schema introspection, and DDL generation.
    """

    @runtime_checkable
    class ConnectionProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle database connection operations."""

        def connect(self) -> FlextResult[bool]:
            """Establish Oracle database connection.

            Returns:
                FlextResult[bool]: Connection success status

            """

        def disconnect(self) -> FlextResult[bool]:
            """Close Oracle database connection.

            Returns:
                FlextResult[bool]: Disconnection success status

            """

        def is_connected(self) -> FlextResult[bool]:
            """Check if Oracle connection is active.

            Returns:
                FlextResult[bool]: Connection status

            """

        def test_connection(self) -> FlextResult[bool]:
            """Test Oracle database connectivity.

            Returns:
                FlextResult[bool]: Connection test result

            """

        def get_connection(self) -> FlextResult[object]:
            """Get current Oracle connection object.

            Returns:
                FlextResult[object]: Connection object or error

            """

    @runtime_checkable
    class QueryExecutorProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle query execution operations."""

        def execute_query(
            self, sql: str, params: dict[str, object] | None = None
        ) -> FlextResult[object]:
            """Execute Oracle SQL query.

            Args:
                sql: SQL query string
                params: Query parameters

            Returns:
                FlextResult[object]: Query result or error

            """

        def execute_statement(
            self, sql: str, params: dict[str, object] | None = None
        ) -> FlextResult[bool]:
            """Execute Oracle SQL statement.

            Args:
                sql: SQL statement string
                params: Statement parameters

            Returns:
                FlextResult[bool]: Execution success status

            """

        def execute_many(
            self, sql: str, params_list: list[dict[str, object]]
        ) -> FlextResult[int]:
            """Execute Oracle SQL statement with multiple parameter sets.

            Args:
                sql: SQL statement string
                params_list: List of parameter dictionaries

            Returns:
                FlextResult[int]: Number of affected rows

            """

        def fetch_one(
            self, sql: str, params: dict[str, object] | None = None
        ) -> FlextResult[object | None]:
            """Fetch single result from Oracle query.

            Args:
                sql: SQL query string
                params: Query parameters

            Returns:
                FlextResult[object | None]: Single result or None

            """

    @runtime_checkable
    class SchemaIntrospectorProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle schema introspection operations."""

        def get_schemas(self) -> FlextResult[list[str]]:
            """Get list of Oracle schemas.

            Returns:
                FlextResult[list[str]]: Schema names or error

            """

        def get_tables(self, schema: str | None = None) -> FlextResult[list[str]]:
            """Get list of tables in Oracle schema.

            Args:
                schema: Schema name (optional)

            Returns:
                FlextResult[list[str]]: Table names or error

            """

        def get_columns(
            self, table: str, schema: str | None = None
        ) -> FlextResult[list[dict[str, object]]]:
            """Get column information for Oracle table.

            Args:
                table: Table name
                schema: Schema name (optional)

            Returns:
                FlextResult[list[dict[str, object]]]: Column metadata or error

            """

        def get_table_metadata(
            self, table: str, schema: str | None = None
        ) -> FlextResult[dict[str, object]]:
            """Get Oracle table metadata.

            Args:
                table: Table name
                schema: Schema name (optional)

            Returns:
                FlextResult[dict[str, object]]: Table metadata or error

            """

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

    @runtime_checkable
    class SqlBuilderProtocol(FlextProtocols.Domain.Service, Protocol):
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

        def build_insert_statement(
            self, table: str, data: dict[str, object]
        ) -> FlextResult[tuple[str, dict[str, object]]]:
            """Build Oracle INSERT statement.

            Args:
                table: Table name
                data: Column data

            Returns:
                FlextResult[tuple[str, dict[str, object]]]: SQL and parameters or error

            """

        def build_update_statement(
            self, table: str, data: dict[str, object], where_clause: str
        ) -> FlextResult[tuple[str, dict[str, object]]]:
            """Build Oracle UPDATE statement.

            Args:
                table: Table name
                data: Column data
                where_clause: WHERE condition

            Returns:
                FlextResult[tuple[str, dict[str, object]]]: SQL and parameters or error

            """

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

    @runtime_checkable
    class DdlGeneratorProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle DDL generation operations."""

        def create_table_ddl(
            self,
            table: str,
            columns: list[dict[str, object]],
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

    @runtime_checkable
    class MetricsCollectorProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle database metrics collection."""

        def record_metric(
            self, name: str, value: float, tags: dict[str, str] | None = None
        ) -> FlextResult[bool]:
            """Record Oracle database metric.

            Args:
                name: Metric name
                value: Metric value
                tags: Metric tags (optional)

            Returns:
                FlextResult[bool]: Success status

            """

        def get_metrics(self) -> FlextResult[dict[str, object]]:
            """Get collected Oracle metrics.

            Returns:
                FlextResult[dict[str, object]]: Metrics data or error

            """

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

    @runtime_checkable
    class PluginRegistryProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle database plugin registry operations."""

        def register_plugin(self, name: str, plugin: object) -> FlextResult[bool]:
            """Register Oracle database plugin.

            Args:
                name: Plugin name
                plugin: Plugin instance

            Returns:
                FlextResult[bool]: Registration success status

            """

        def unregister_plugin(self, name: str) -> FlextResult[bool]:
            """Unregister Oracle database plugin.

            Args:
                name: Plugin name

            Returns:
                FlextResult[bool]: Unregistration success status

            """

        def get_plugin(self, name: str) -> FlextResult[object]:
            """Get Oracle database plugin by name.

            Args:
                name: Plugin name

            Returns:
                FlextResult[object]: Plugin instance or error

            """

        def list_plugins(self) -> FlextResult[list[str]]:
            """List registered Oracle database plugins.

            Returns:
                FlextResult[list[str]]: Plugin names or error

            """

    @runtime_checkable
    class HealthCheckProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Oracle database health check operations."""

        def health_check(self) -> FlextResult[dict[str, object]]:
            """Perform Oracle database health check.

            Returns:
                FlextResult[dict[str, object]]: Health status or error

            """

        def get_connection_status(self) -> FlextResult[dict[str, object]]:
            """Get Oracle connection status information.

            Returns:
                FlextResult[dict[str, object]]: Connection status or error

            """

    # Convenience aliases for easier downstream usage
    OracleConnectionProtocol = ConnectionProtocol
    OracleQueryProtocol = QueryExecutorProtocol
    OracleSchemaProtocol = SchemaIntrospectorProtocol
    OracleSqlProtocol = SqlBuilderProtocol
    OracleDdlProtocol = DdlGeneratorProtocol
    OracleMetricsProtocol = MetricsCollectorProtocol
    OraclePluginProtocol = PluginRegistryProtocol
    OracleHealthProtocol = HealthCheckProtocol


__all__ = [
    "FlextDbOracleProtocols",
]

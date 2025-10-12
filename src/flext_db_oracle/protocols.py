"""Oracle Database protocols for FLEXT ecosystem."""

from typing import Protocol, runtime_checkable

from flext_core import FlextCore


class FlextDbOracleProtocols(FlextCore.Protocols):
    """Oracle database protocols extending FlextCore.Protocols foundation.

    Extends FlextCore.Protocols with Oracle-specific protocol definitions
    while inheriting all foundation protocols. Follows FLEXT namespace pattern.
    """

    # =========================================================================
    # INHERITED FOUNDATION PROTOCOLS - Available from FlextCore.Protocols
    # =========================================================================
    # Foundation, Domain, Application, Infrastructure, Extensions, Commands
    # are all inherited from FlextCore.Protocols parent class

    # =========================================================================
    # ORACLE DATABASE-SPECIFIC PROTOCOLS - Domain extension for database operations
    # =========================================================================

    class Database:
        """Oracle database domain-specific protocols."""

        @runtime_checkable
        class ConnectionProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Oracle database connection operations."""

            def connect(self) -> FlextCore.Result[bool]:
                """Establish Oracle database connection.

                Returns:
                    FlextCore.Result[bool]: Connection success status

                """
                ...
                ...

            def disconnect(self) -> FlextCore.Result[bool]:
                """Close Oracle database connection.

                Returns:
                    FlextCore.Result[bool]: Disconnection success status

                """
                ...
                ...

            def is_connected(self) -> FlextCore.Result[bool]:
                """Check if Oracle connection is active.

                Returns:
                    FlextCore.Result[bool]: Connection status

                """
                ...
                ...

            def test_connection(self) -> FlextCore.Result[bool]:
                """Test Oracle database connectivity.

                Returns:
                    FlextCore.Result[bool]: Connection test result

                """
                ...
                ...

            def get_connection(self) -> FlextCore.Result[object]:
                """Get current Oracle connection object.

                Returns:
                    FlextCore.Result[object]: Connection object or error

                """
                ...
                ...

        @runtime_checkable
        class QueryExecutorProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Oracle query execution operations."""

            def execute_query(
                self, sql: str, params: FlextCore.Types.Dict | None = None
            ) -> FlextCore.Result[object]:
                """Execute Oracle SQL query.

                Args:
                    sql: SQL query string
                    params: Query parameters

                Returns:
                    FlextCore.Result[object]: Query result or error

                """
                ...
                ...

            def execute_statement(
                self, sql: str, params: FlextCore.Types.Dict | None = None
            ) -> FlextCore.Result[bool]:
                """Execute Oracle SQL statement.

                Args:
                    sql: SQL statement string
                    params: Statement parameters

                Returns:
                    FlextCore.Result[bool]: Execution success status

                """
                ...
                ...

            def execute_many(
                self, sql: str, params_list: list[FlextCore.Types.Dict]
            ) -> FlextCore.Result[int]:
                """Execute Oracle SQL statement with multiple parameter sets.

                Args:
                    sql: SQL statement string
                    params_list: List of parameter dictionaries

                Returns:
                    FlextCore.Result[int]: Number of affected rows

                """
                ...
                ...

            def fetch_one(
                self, sql: str, params: FlextCore.Types.Dict | None = None
            ) -> FlextCore.Result[object | None]:
                """Fetch single result from Oracle query.

                Args:
                    sql: SQL query string
                    params: Query parameters

                Returns:
                    FlextCore.Result[object | None]: Single result or None

                """
                ...

        @runtime_checkable
        class SchemaIntrospectorProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Oracle schema introspection operations."""

            def get_schemas(self) -> FlextCore.Result[FlextCore.Types.StringList]:
                """Get list of Oracle schemas.

                Returns:
                    FlextCore.Result[FlextCore.Types.StringList]: Schema names or error

                """
                ...

            def get_tables(
                self, schema: str | None = None
            ) -> FlextCore.Result[FlextCore.Types.StringList]:
                """Get list of tables in Oracle schema.

                Args:
                    schema: Schema name (optional)

                Returns:
                    FlextCore.Result[FlextCore.Types.StringList]: Table names or error

                """
                ...

            def get_columns(
                self, table: str, schema: str | None = None
            ) -> FlextCore.Result[list[FlextCore.Types.Dict]]:
                """Get column information for Oracle table.

                Args:
                    table: Table name
                    schema: Schema name (optional)

                Returns:
                    FlextCore.Result[list[FlextCore.Types.Dict]]: Column metadata or error

                """
                ...

            def get_table_metadata(
                self, table: str, schema: str | None = None
            ) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Get Oracle table metadata.

                Args:
                    table: Table name
                    schema: Schema name (optional)

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Table metadata or error

                """
                ...

            def get_primary_keys(
                self, table: str, schema: str | None = None
            ) -> FlextCore.Result[FlextCore.Types.StringList]:
                """Get primary key columns for Oracle table.

                Args:
                    table: Table name
                    schema: Schema name (optional)

                Returns:
                    FlextCore.Result[FlextCore.Types.StringList]: Primary key column names or error

                """
                ...

        @runtime_checkable
        class SqlBuilderProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Oracle SQL statement building operations."""

            def build_select(
                self,
                table: str,
                columns: FlextCore.Types.StringList | None = None,
                where_clause: str | None = None,
                order_by: str | None = None,
                limit: int | None = None,
            ) -> FlextCore.Result[str]:
                """Build Oracle SELECT statement.

                Args:
                    table: Table name
                    columns: Column names (optional)
                    where_clause: WHERE condition (optional)
                    order_by: ORDER BY clause (optional)
                    limit: Row limit (optional)

                Returns:
                    FlextCore.Result[str]: SQL SELECT statement or error

                """
                ...

            def build_insert_statement(
                self, table: str, data: FlextCore.Types.Dict
            ) -> FlextCore.Result[tuple[str, FlextCore.Types.Dict]]:
                """Build Oracle INSERT statement.

                Args:
                    table: Table name
                    data: Column data

                Returns:
                    FlextCore.Result[tuple[str, FlextCore.Types.Dict]]: SQL and parameters or error

                """
                ...

            def build_update_statement(
                self, table: str, data: FlextCore.Types.Dict, where_clause: str
            ) -> FlextCore.Result[tuple[str, FlextCore.Types.Dict]]:
                """Build Oracle UPDATE statement.

                Args:
                    table: Table name
                    data: Column data
                    where_clause: WHERE condition

                Returns:
                    FlextCore.Result[tuple[str, FlextCore.Types.Dict]]: SQL and parameters or error

                """
                ...

            def build_delete_statement(
                self, table: str, where_clause: str
            ) -> FlextCore.Result[str]:
                """Build Oracle DELETE statement.

                Args:
                    table: Table name
                    where_clause: WHERE condition

                Returns:
                    FlextCore.Result[str]: SQL DELETE statement or error

                """
                ...

        @runtime_checkable
        class DdlGeneratorProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Oracle DDL generation operations."""

            def create_table_ddl(
                self,
                table: str,
                columns: list[FlextCore.Types.Dict],
                schema: str | None = None,
            ) -> FlextCore.Result[str]:
                """Generate Oracle CREATE TABLE DDL.

                Args:
                    table: Table name
                    columns: Column definitions
                    schema: Schema name (optional)

                Returns:
                    FlextCore.Result[str]: CREATE TABLE DDL or error

                """
                ...

            def drop_table_ddl(
                self, table: str, schema: str | None = None
            ) -> FlextCore.Result[str]:
                """Generate Oracle DROP TABLE DDL.

                Args:
                    table: Table name
                    schema: Schema name (optional)

                Returns:
                    FlextCore.Result[str]: DROP TABLE DDL or error

                """
                ...

            def build_create_index_statement(
                self,
                table: str,
                columns: FlextCore.Types.StringList,
                index_name: str | None = None,
                *,
                unique: bool = False,
            ) -> FlextCore.Result[str]:
                """Build Oracle CREATE INDEX statement.

                Args:
                    table: Table name
                    columns: Index columns
                    index_name: Index name (optional)
                    unique: Create unique index

                Returns:
                    FlextCore.Result[str]: CREATE INDEX statement or error

                """
                ...

        @runtime_checkable
        class MetricsCollectorProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Oracle database metrics collection."""

            def record_metric(
                self,
                name: str,
                value: float,
                tags: FlextCore.Types.StringDict | None = None,
            ) -> FlextCore.Result[bool]:
                """Record Oracle database metric.

                Args:
                    name: Metric name
                    value: Metric value
                    tags: Metric tags (optional)

                Returns:
                    FlextCore.Result[bool]: Success status

                """
                ...

            def get_metrics(self) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Get collected Oracle metrics.

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Metrics data or error

                """
                ...

            def track_operation(
                self, operation: str, duration: float, *, success: bool
            ) -> FlextCore.Result[bool]:
                """Track Oracle operation performance.

                Args:
                    operation: Operation name
                    duration: Operation duration
                    success: Operation success status

                Returns:
                    FlextCore.Result[bool]: Tracking success status

                """
                ...

        @runtime_checkable
        class PluginRegistryProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Oracle database plugin registry operations."""

            def register_plugin(
                self, name: str, plugin: object
            ) -> FlextCore.Result[bool]:
                """Register Oracle database plugin.

                Args:
                    name: Plugin name
                    plugin: Plugin instance

                Returns:
                    FlextCore.Result[bool]: Registration success status

                """
                ...

            def unregister_plugin(self, name: str) -> FlextCore.Result[bool]:
                """Unregister Oracle database plugin.

                Args:
                    name: Plugin name

                Returns:
                    FlextCore.Result[bool]: Unregistration success status

                """
                ...

            def get_plugin(self, name: str) -> FlextCore.Result[object]:
                """Get Oracle database plugin by name.

                Args:
                    name: Plugin name

                Returns:
                    FlextCore.Result[object]: Plugin instance or error

                """
                ...

            def list_plugins(self) -> FlextCore.Result[FlextCore.Types.StringList]:
                """List registered Oracle database plugins.

                Returns:
                    FlextCore.Result[FlextCore.Types.StringList]: Plugin names or error

                """
                ...

        @runtime_checkable
        class HealthCheckProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Oracle database health check operations."""

            def health_check(self) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Perform Oracle database health check.

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Health status or error

                """
                ...

            def get_connection_status(self) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Get Oracle connection status information.

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Connection status or error

                """
                ...


# NO ALIASES - STRICT RULE: only use direct imports from protocols module
# All usage must be: FlextDbOracleProtocols.Database.ConnectionProtocol
# NOT: FlextDbOracleProtocols.OracleConnectionProtocol


__all__ = [
    "FlextDbOracleProtocols",
]

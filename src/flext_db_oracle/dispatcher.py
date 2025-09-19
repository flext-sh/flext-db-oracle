"""Dispatcher integration helpers for flext-db-oracle services."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from flext_core import FlextBus, FlextDispatcher, FlextDispatcherRegistry
from flext_db_oracle.services import FlextDbOracleServices


class FlextDbOracleDispatcher:
    """Unified Oracle Database Dispatcher with integrated command classes."""

    @dataclass(slots=True)
    class ConnectCommand:
        """Command to establish an Oracle database connection."""

    @dataclass(slots=True)
    class DisconnectCommand:
        """Command to close the Oracle database connection."""

    @dataclass(slots=True)
    class TestConnectionCommand:
        """Command to validate the Oracle database connectivity."""

    @dataclass(slots=True)
    class ExecuteQueryCommand:
        """Command to execute a SQL query and return rows."""

        sql: str
        parameters: dict[str, object] | None = None

    @dataclass(slots=True)
    class FetchOneCommand:
        """Command to execute a SQL query and fetch a single row."""

        sql: str
        parameters: dict[str, object] | None = None

    @dataclass(slots=True)
    class ExecuteStatementCommand:
        """Command to execute a SQL statement (INSERT/UPDATE/DELETE)."""

        sql: str
        parameters: dict[str, object] | None = None

    @dataclass(slots=True)
    class ExecuteManyCommand:
        """Command to execute a SQL statement multiple times."""

        sql: str
        parameters_list: list[dict[str, object]]

    @dataclass(slots=True)
    class GetSchemasCommand:
        """Command to retrieve available database schemas."""

    @dataclass(slots=True)
    class GetTablesCommand:
        """Command to list tables for an optional schema."""

        schema: str | None = None

    @dataclass(slots=True)
    class GetColumnsCommand:
        """Command to list column metadata for a table."""

        table: str
        schema: str | None = None

    @classmethod
    def build_dispatcher(
        cls,
        services: FlextDbOracleServices,
        *,
        bus: FlextBus | None = None,
    ) -> FlextDispatcher:
        """Create a dispatcher instance wired to Oracle services."""
        dispatcher = FlextDispatcher(bus=bus)
        registry = FlextDispatcherRegistry(dispatcher)

        # Create properly typed handler functions using object type for flexibility
        def connect_handler(_cmd: object) -> object:
            return services.connect()

        def disconnect_handler(_cmd: object) -> object:
            return services.disconnect()

        def test_connection_handler(_cmd: object) -> object:
            """Test Oracle connection handler - cmd parameter required by dispatcher interface."""
            # Parameter _cmd is required by dispatcher interface but not used in this handler
            _ = _cmd  # Explicitly acknowledge unused parameter
            return services.test_connection()

        def execute_query_handler(cmd: object) -> object:
            # Safe attribute access with hasattr checks
            sql = getattr(cmd, "sql", "")
            parameters = getattr(cmd, "parameters", None) or {}
            return services.execute_query(sql, parameters)

        def fetch_one_handler(cmd: object) -> object:
            # Safe attribute access with hasattr checks
            sql = getattr(cmd, "sql", "")
            parameters = getattr(cmd, "parameters", None) or {}
            return services.fetch_one(sql, parameters)

        def execute_statement_handler(cmd: object) -> object:
            # Safe attribute access with hasattr checks
            sql = getattr(cmd, "sql", "")
            parameters = getattr(cmd, "parameters", None) or {}
            return services.execute_statement(sql, parameters)

        def execute_many_handler(cmd: object) -> object:
            # Safe attribute access with hasattr checks
            sql = getattr(cmd, "sql", "")
            parameters_list = getattr(cmd, "parameters_list", [])
            return services.execute_many(sql, parameters_list)

        def get_schemas_handler(_cmd: object) -> object:
            return services.get_schemas()

        def get_tables_handler(cmd: object) -> object:
            # Safe attribute access with hasattr checks
            schema = getattr(cmd, "schema", None)
            return services.get_tables(schema)

        def get_columns_handler(cmd: object) -> object:
            # Safe attribute access with hasattr checks
            table = getattr(cmd, "table", "")
            schema = getattr(cmd, "schema", None)
            return services.get_columns(table, schema)

        # Use register_function_map with proper typing

        function_map: dict[
            type, tuple[Callable[[object], object], dict[str, object] | None]
        ] = {
            cls.ConnectCommand: (connect_handler, None),
            cls.DisconnectCommand: (disconnect_handler, None),
            cls.TestConnectionCommand: (test_connection_handler, None),
            cls.ExecuteQueryCommand: (execute_query_handler, None),
            cls.FetchOneCommand: (fetch_one_handler, None),
            cls.ExecuteStatementCommand: (execute_statement_handler, None),
            cls.ExecuteManyCommand: (execute_many_handler, None),
            cls.GetSchemasCommand: (get_schemas_handler, None),
            cls.GetTablesCommand: (get_tables_handler, None),
            cls.GetColumnsCommand: (get_columns_handler, None),
        }

        registry.register_function_map(function_map)

        return dispatcher


# FLEXT ZERO TOLERANCE: No aliases or legacy access - use unified class directly

__all__ = [
    "FlextDbOracleDispatcher",
]

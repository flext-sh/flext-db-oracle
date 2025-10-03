"""Dispatcher integration helpers for flext-db-oracle services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from flext_core import FlextBus, FlextDispatcher, FlextRegistry, FlextTypes
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
        parameters: FlextTypes.Dict | None = None

    @dataclass(slots=True)
    class FetchOneCommand:
        """Command to execute a SQL query and fetch a single row."""

        sql: str
        parameters: FlextTypes.Dict | None = None

    @dataclass(slots=True)
    class ExecuteStatementCommand:
        """Command to execute a SQL statement (INSERT/UPDATE/DELETE)."""

        sql: str
        parameters: FlextTypes.Dict | None = None

    @dataclass(slots=True)
    class ExecuteManyCommand:
        """Command to execute a SQL statement multiple times."""

        sql: str
        parameters_list: list[FlextTypes.Dict]

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
        registry = FlextRegistry(dispatcher)

        # Create properly typed handler functions using object type for flexibility
        def connect_handler(_cmd: object) -> object:
            return services.connect()

        def disconnect_handler(_cmd: object) -> object:
            return services.disconnect()

        def connection_test_handler(_command_data: object) -> object:
            """Oracle connection test handler - command_data parameter required by dispatcher interface."""
            # Parameter _command_data is required by dispatcher interface but not used in this handler
            return services.test_connection()

        def execute_query_handler(command: object) -> object:
            # Safe attribute access with hasattr checks
            sql = getattr(command, "sql", "")
            parameters: FlextTypes.Dict = getattr(command, "parameters", None) or {}
            return services.execute_query(sql, parameters)

        def fetch_one_handler(command: object) -> object:
            # Safe attribute access with hasattr checks
            sql = getattr(command, "sql", "")
            parameters: FlextTypes.Dict = getattr(command, "parameters", None) or {}
            return services.fetch_one(sql, parameters)

        def execute_statement_handler(command: object) -> object:
            # Safe attribute access with hasattr checks
            sql = getattr(command, "sql", "")
            parameters: FlextTypes.Dict = getattr(command, "parameters", None) or {}
            return services.execute_statement(sql, parameters)

        def execute_many_handler(command: object) -> object:
            # Safe attribute access with hasattr checks
            sql = getattr(command, "sql", "")
            parameters_list: list[FlextTypes.Dict] = getattr(
                command, "parameters_list", []
            )
            return services.execute_many(sql, parameters_list)

        def get_schemas_handler(_cmd: object) -> object:
            return services.get_schemas()

        def get_tables_handler(command: object) -> object:
            # Safe attribute access with hasattr checks
            schema = getattr(command, "schema", None)
            return services.get_tables(schema)

        def get_columns_handler(command: object) -> object:
            # Safe attribute access with hasattr checks
            table = getattr(command, "table", "")
            schema = getattr(command, "schema", None)
            return services.get_columns(table, schema)

        # Use register_function_map with proper typing

        function_map: dict[
            type, tuple[Callable[[object], object], FlextTypes.Dict | None]
        ] = {
            cls.ConnectCommand: (connect_handler, None),
            cls.DisconnectCommand: (disconnect_handler, None),
            cls.TestConnectionCommand: (connection_test_handler, None),
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

"""Dispatcher integration helpers for flext-db-oracle services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from flext_core import FlextDispatcher, FlextRegistry, r, t
from flext_core.service import FlextService

from flext_db_oracle.services import FlextDbOracleServices


class FlextDbOracleDispatcher(FlextService[None]):
    """Unified Oracle Database Dispatcher with integrated command classes."""

    def execute(self, **_kwargs: t.JsonValue) -> r[None]:
        """Execute dispatcher operation - returns None as this is a factory class."""
        return r[None].ok(None)

    @dataclass(slots=True)
    class ConnectCommand:
        """Command to establish an Oracle database connection."""

    class DisconnectCommand:
        """Command to close the Oracle database connection."""

    class TestConnectionCommand:
        """Command to validate the Oracle database connectivity."""

    class ExecuteQueryCommand:
        """Command to execute a SQL query and return rows."""

        sql: str
        parameters: dict[str, t.JsonValue] | None = None

    class FetchOneCommand:
        """Command to execute a SQL query and fetch a single row."""

    class ExecuteStatementCommand:
        """Command to execute a SQL statement (INSERT/UPDATE/DELETE)."""

    class ExecuteManyCommand:
        """Command to execute a SQL statement multiple times."""

        parameters_list: list[dict[str, t.JsonValue]]

    class GetSchemasCommand:
        """Command to retrieve available database schemas."""

    class GetTablesCommand:
        """Command to list tables for an optional schema."""

        schema: str | None = None

    class GetColumnsCommand:
        """Command to list column metadata for a table."""

        table: str

    @classmethod
    def _create_connection_handlers(
        cls,
        services: FlextDbOracleServices,
    ) -> dict[type, tuple[Callable[..., t.GeneralValueType], dict[str, t.JsonValue] | None]]:
        """Create connection-related handler functions."""

        def connect_handler(_cmd: t.GeneralValueType) -> t.GeneralValueType:
            return services.connect()

        def disconnect_handler(_cmd: t.GeneralValueType) -> t.GeneralValueType:
            return services.disconnect()

        def connection_test_handler(
            _command_data: t.GeneralValueType,
        ) -> t.GeneralValueType:
            """Oracle connection test handler - command_data parameter required by dispatcher interface."""
            return services.test_connection()

        return {
            cls.ConnectCommand: (connect_handler, None),
            cls.DisconnectCommand: (disconnect_handler, None),
            cls.TestConnectionCommand: (connection_test_handler, None),
        }

    def _create_query_handlers(
        self,
        services: FlextDbOracleServices,
    ) -> dict[type, tuple[Callable[..., t.GeneralValueType], dict[str, t.JsonValue] | None]]:
        """Create query-related handler functions."""

        def execute_query_handler(command: t.GeneralValueType) -> t.GeneralValueType:
            sql = getattr(command, "sql", "")
            parameters: dict[str, t.JsonValue] = (
                getattr(command, "parameters", None) or {}
            )
            return services.execute_query(sql, parameters)

        def fetch_one_handler(command: t.GeneralValueType) -> t.GeneralValueType:
            sql = getattr(command, "sql", "")
            parameters: dict[str, t.JsonValue] = (
                getattr(command, "parameters", None) or {}
            )
            return services.fetch_one(sql, parameters)

        def execute_statement_handler(
            command: t.GeneralValueType,
        ) -> t.GeneralValueType:
            sql = getattr(command, "sql", "")
            parameters: dict[str, t.JsonValue] = (
                getattr(command, "parameters", None) or {}
            )
            return services.execute_statement(sql, parameters)

        def execute_many_handler(command: t.GeneralValueType) -> t.GeneralValueType:
            sql = getattr(command, "sql", "")
            parameters_list: list[dict[str, t.JsonValue]] = getattr(
                command,
                "parameters_list",
                [],
            )
            return services.execute_many(sql, parameters_list)

        return {
            self.ExecuteQueryCommand: (execute_query_handler, None),
            self.FetchOneCommand: (fetch_one_handler, None),
            self.ExecuteStatementCommand: (execute_statement_handler, None),
            self.ExecuteManyCommand: (execute_many_handler, None),
        }

    def _create_schema_handlers(
        self,
        services: FlextDbOracleServices,
    ) -> dict[type, tuple[Callable[..., t.GeneralValueType], dict[str, t.JsonValue] | None]]:
        """Create schema/metadata handler functions."""

        def get_schemas_handler(_cmd: t.GeneralValueType) -> t.GeneralValueType:
            return services.get_schemas()

        def get_tables_handler(command: t.GeneralValueType) -> t.GeneralValueType:
            schema = getattr(command, "schema", None)
            return services.get_tables(schema)

        def get_columns_handler(command: t.GeneralValueType) -> t.GeneralValueType:
            table = getattr(command, "table", "")
            schema = getattr(command, "schema", None)
            return services.get_columns(table, schema)

        return {
            self.GetSchemasCommand: (get_schemas_handler, None),
            self.GetTablesCommand: (get_tables_handler, None),
            self.GetColumnsCommand: (get_columns_handler, None),
        }

    @classmethod
    def build_dispatcher(
        cls,
        services: FlextDbOracleServices,
        *,
        _bus: object | None = None,
    ) -> FlextDispatcher:
        """Create a dispatcher instance wired to Oracle services."""
        dispatcher = FlextDispatcher()
        _registry = FlextRegistry(dispatcher)  # Registry initialized for future use
        # Create handler functions grouped by functionality
        function_map: dict[
            type, tuple[Callable[..., t.GeneralValueType], dict[str, t.GeneralValueType] | None]
        ] = {}
        # Add connection handlers
        function_map.update(cls._create_connection_handlers(services))
        # Add query handlers - need instance for these methods now
        instance = cls()
        function_map.update(instance._create_query_handlers(services))
        # Add schema handlers
        function_map.update(instance._create_schema_handlers(services))
        # Register each handler from the function map
        for command_type, (handler_fn, _metadata) in function_map.items():
            # Register handler with dispatcher
            dispatcher.register_handler(command_type, handler_fn)
        return dispatcher


# FLEXT Zero Tolerance: No aliases or legacy access - use unified class directly
__all__ = [
    "FlextDbOracleDispatcher",
]

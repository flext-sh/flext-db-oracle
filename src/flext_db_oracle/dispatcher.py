"""Dispatcher integration helpers for flext-db-oracle services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from flext_core import (
    FlextDispatcher,
    FlextRegistry,
    FlextService,
    t,
)

from flext_db_oracle.services import FlextDbOracleServices


class FlextDbOracleDispatcher(FlextService):
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
        parameters: dict[str, t.JsonValue] | None = None

    @dataclass(slots=True)
    class FetchOneCommand:
        """Command to execute a SQL query and fetch a single row."""

        sql: str
        parameters: dict[str, t.JsonValue] | None = None

    @dataclass(slots=True)
    class ExecuteStatementCommand:
        """Command to execute a SQL statement (INSERT/UPDATE/DELETE)."""

        sql: str
        parameters: dict[str, t.JsonValue] | None = None

    @dataclass(slots=True)
    class ExecuteManyCommand:
        """Command to execute a SQL statement multiple times."""

        sql: str
        parameters_list: list[dict[str, t.JsonValue]]

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
    def _create_connection_handlers(
        cls,
        services: FlextDbOracleServices,
    ) -> dict[type, tuple[t.MiddlewareType, dict[str, object] | None]]:
        """Create connection-related handler functions."""

        def connect_handler(_cmd: object) -> object:
            return services.connect()

        def disconnect_handler(_cmd: object) -> object:
            return services.disconnect()

        def connection_test_handler(_command_data: object) -> object:
            """Oracle connection test handler - command_data parameter required by dispatcher interface."""
            return services.test_connection()

        return cast(
            "dict[type, tuple[t.MiddlewareType, dict[str, object] | None]]",
            {
                cls.ConnectCommand: (connect_handler, None),
                cls.DisconnectCommand: (disconnect_handler, None),
                cls.TestConnectionCommand: (connection_test_handler, None),
            },
        )

    @classmethod
    def _create_query_handlers(
        cls,
        services: FlextDbOracleServices,
    ) -> dict[type, tuple[t.MiddlewareType, dict[str, object] | None]]:
        """Create query-related handler functions."""

        def execute_query_handler(command: object) -> object:
            sql = getattr(command, "sql", "")
            parameters: dict[str, t.JsonValue] = (
                getattr(command, "parameters", None) or {}
            )
            return services.execute_query(sql, parameters)

        def fetch_one_handler(command: object) -> object:
            sql = getattr(command, "sql", "")
            parameters: dict[str, t.JsonValue] = (
                getattr(command, "parameters", None) or {}
            )
            return services.fetch_one(sql, parameters)

        def execute_statement_handler(command: object) -> object:
            sql = getattr(command, "sql", "")
            parameters: dict[str, t.JsonValue] = (
                getattr(command, "parameters", None) or {}
            )
            return services.execute_statement(sql, parameters)

        def execute_many_handler(command: object) -> object:
            sql = getattr(command, "sql", "")
            parameters_list: list[dict[str, t.JsonValue]] = getattr(
                command,
                "parameters_list",
                [],
            )
            return services.execute_many(sql, parameters_list)

        return cast(
            "dict[type, tuple[t.MiddlewareType, dict[str, object] | None]]",
            {
                cls.ExecuteQueryCommand: (execute_query_handler, None),
                cls.FetchOneCommand: (fetch_one_handler, None),
                cls.ExecuteStatementCommand: (execute_statement_handler, None),
                cls.ExecuteManyCommand: (execute_many_handler, None),
            },
        )

    @classmethod
    def _create_schema_handlers(
        cls,
        services: FlextDbOracleServices,
    ) -> dict[type, tuple[t.MiddlewareType, dict[str, object] | None]]:
        """Create schema/metadata handler functions."""

        def get_schemas_handler(_cmd: object) -> object:
            return services.get_schemas()

        def get_tables_handler(command: object) -> object:
            schema = getattr(command, "schema", None)
            return services.get_tables(schema)

        def get_columns_handler(command: object) -> object:
            table = getattr(command, "table", "")
            schema = getattr(command, "schema", None)
            return services.get_columns(table, schema)

        return cast(
            "dict[type, tuple[t.MiddlewareType, dict[str, object] | None]]",
            {
                cls.GetSchemasCommand: (get_schemas_handler, None),
                cls.GetTablesCommand: (get_tables_handler, None),
                cls.GetColumnsCommand: (get_columns_handler, None),
            },
        )

    @classmethod
    def build_dispatcher(
        cls,
        services: FlextDbOracleServices,
        *,
        _bus: object | None = None,
    ) -> FlextDispatcher:
        """Create a dispatcher instance wired to Oracle services."""
        dispatcher = FlextDispatcher()
        registry = FlextRegistry(dispatcher)

        # Create handler functions grouped by functionality
        function_map: dict[type, tuple[t.MiddlewareType, dict[str, object] | None]] = {}

        # Add connection handlers
        function_map.update(cls._create_connection_handlers(services))

        # Add query handlers
        function_map.update(cls._create_query_handlers(services))

        # Add schema handlers
        function_map.update(cls._create_schema_handlers(services))

        registry.register_function_map(function_map)

        return dispatcher


# FLEXT Zero Tolerance: No aliases or legacy access - use unified class directly

__all__ = [
    "FlextDbOracleDispatcher",
]

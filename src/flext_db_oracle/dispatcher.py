"""Dispatcher integration helpers for flext-db-oracle services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import cast, override

from flext_core import FlextContainer, FlextRegistry, r, t
from flext_core.models import FlextModels as m
from flext_core.protocols import p
from flext_core.service import FlextService
from flext_db_oracle.services import FlextDbOracleServices
from pydantic import Field


class FlextDbOracleDispatcher(FlextService[None]):
    """Unified Oracle Database Dispatcher with integrated command classes."""

    @override
    def execute(self) -> r[None]:
        """Execute dispatcher operation - returns None as this is a factory class."""
        return r[None].ok(None)

    class ConnectCommand(m.Command):
        """Command to establish an Oracle database connection."""

    class DisconnectCommand(m.Command):
        """Command to close the Oracle database connection."""

    class TestConnectionCommand(m.Command):
        """Command to validate the Oracle database connectivity."""

    class ExecuteQueryCommand(m.Command):
        """Command to execute a SQL query and return rows."""

        sql: str = Field(description="SQL query to execute")
        parameters: t.ConfigMap | None = Field(
            default=None, description="Query parameters"
        )

    class FetchOneCommand(m.Command):
        """Command to execute a SQL query and fetch a single row."""

        sql: str = Field(description="SQL query to execute")
        parameters: t.ConfigMap | None = Field(
            default=None, description="Query parameters"
        )

    class ExecuteStatementCommand(m.Command):
        """Command to execute a SQL statement (INSERT/UPDATE/DELETE)."""

        sql: str = Field(description="SQL statement to execute")
        parameters: t.ConfigMap | None = Field(
            default=None, description="Statement parameters"
        )

    class ExecuteManyCommand(m.Command):
        """Command to execute a SQL statement multiple times."""

        sql: str = Field(description="SQL statement to execute")
        parameters_list: list[t.ConfigMap] = Field(description="List of parameter sets")

    class GetSchemasCommand(m.Command):
        """Command to retrieve available database schemas."""

    class GetTablesCommand(m.Command):
        """Command to list tables for an optional schema."""

        schema_name: str | None = Field(
            default=None, description="Optional schema name"
        )

    class GetColumnsCommand(m.Command):
        """Command to list column metadata for a table."""

        table: str = Field(description="Table name")
        schema_name: str | None = Field(
            default=None, description="Optional schema name"
        )

    @classmethod
    def _create_connection_handlers(
        cls,
        services: FlextDbOracleServices,
    ) -> dict[
        type,
        tuple[
            Callable[[object], t.GeneralValueType],
            Mapping[str, t.JsonValue] | None,
        ],
    ]:
        """Create connection-related handler functions."""

        def connect_handler(_cmd: object) -> t.GeneralValueType:
            return services.connect().is_success

        def disconnect_handler(_cmd: object) -> t.GeneralValueType:
            return services.disconnect().is_success

        def connection_test_handler(_command_data: object) -> t.GeneralValueType:
            """Oracle connection test handler - command_data parameter required by dispatcher interface."""
            return services.test_connection().map_or(False)

        return {
            cls.ConnectCommand: (connect_handler, None),
            cls.DisconnectCommand: (disconnect_handler, None),
            cls.TestConnectionCommand: (connection_test_handler, None),
        }

    def _create_query_handlers(
        self,
        services: FlextDbOracleServices,
    ) -> dict[
        type,
        tuple[
            Callable[[object], t.GeneralValueType],
            Mapping[str, t.JsonValue] | None,
        ],
    ]:
        """Create query-related handler functions."""

        def execute_query_handler(command: object) -> t.GeneralValueType:
            if isinstance(command, self.ExecuteQueryCommand):
                sql = command.sql
                parameters = command.parameters or t.ConfigMap(root={})
            else:
                sql = ""
                parameters = t.ConfigMap(root={})
            return services.execute_query(sql, parameters).map_or([])

        def fetch_one_handler(command: object) -> t.GeneralValueType:
            if isinstance(command, self.FetchOneCommand):
                sql = command.sql
                parameters = command.parameters or t.ConfigMap(root={})
            else:
                sql = ""
                parameters = t.ConfigMap(root={})
            return services.fetch_one(sql, parameters).map_or(None)

        def execute_statement_handler(command: object) -> t.GeneralValueType:
            if isinstance(command, self.ExecuteStatementCommand):
                sql = command.sql
                parameters = command.parameters or t.ConfigMap(root={})
            else:
                sql = ""
                parameters = t.ConfigMap(root={})
            return services.execute_statement(sql, parameters).map_or(0)

        def execute_many_handler(command: object) -> t.GeneralValueType:
            if isinstance(command, self.ExecuteManyCommand):
                sql = command.sql
                parameters_list = command.parameters_list
            else:
                sql = ""
                parameters_list = list[t.ConfigMap]()
            return services.execute_many(sql, parameters_list).map_or(0)

        return {
            self.ExecuteQueryCommand: (execute_query_handler, None),
            self.FetchOneCommand: (fetch_one_handler, None),
            self.ExecuteStatementCommand: (execute_statement_handler, None),
            self.ExecuteManyCommand: (execute_many_handler, None),
        }

    def _create_schema_handlers(
        self,
        services: FlextDbOracleServices,
    ) -> dict[
        type,
        tuple[
            Callable[[object], t.GeneralValueType],
            Mapping[str, t.JsonValue] | None,
        ],
    ]:
        """Create schema/metadata handler functions."""

        def get_schemas_handler(_cmd: object) -> t.GeneralValueType:
            return services.get_schemas().map_or([])

        def get_tables_handler(command: object) -> t.GeneralValueType:
            schema: str | None = None
            if isinstance(command, FlextDbOracleDispatcher.GetTablesCommand):
                schema = command.schema_name
            return services.get_tables(schema).map_or([])

        def get_columns_handler(command: object) -> t.GeneralValueType:
            if isinstance(command, FlextDbOracleDispatcher.GetColumnsCommand):
                table = command.table
                schema = command.schema_name
            else:
                table = ""
                schema = None
            return services.get_columns(table, schema).map_or([])

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
    ) -> p.CommandBus:
        """Create a dispatcher instance wired to Oracle services."""
        dispatcher = cast(
            "p.CommandBus", FlextContainer.get_global().get("command_bus").unwrap()
        )
        _registry = FlextRegistry(dispatcher)  # Registry initialized for future use
        # Create handler functions grouped by functionality
        function_map: dict[
            type,
            tuple[
                Callable[[object], t.GeneralValueType],
                Mapping[str, t.JsonValue] | None,
            ],
        ] = {}
        # Add connection handlers
        function_map.update(cls._create_connection_handlers(services))
        # Add query handlers - need instance for these methods now
        instance = cls()
        function_map.update(instance._create_query_handlers(services))
        # Add schema handlers
        function_map.update(instance._create_schema_handlers(services))
        # Register each handler with strict API (handler must expose message_type)
        for handler_fn, _metadata in function_map.values():
            # Set message_type on handler for strict route discovery
            dispatcher.register_handler(cast("t.HandlerType", handler_fn))
        return dispatcher


# FLEXT Zero Tolerance: No aliases or legacy access - use unified class directly
__all__ = [
    "FlextDbOracleDispatcher",
]

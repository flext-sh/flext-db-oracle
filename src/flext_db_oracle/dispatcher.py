"""Dispatcher integration helpers for flext-db-oracle services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import ClassVar, override

from flext_core import FlextContainer, FlextRegistry, FlextService, p, r, t

from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.services import FlextDbOracleServices


class FlextDbOracleDispatcher(FlextService[None]):
    """Unified Oracle Database Dispatcher with integrated command classes."""

    ConnectCommand: ClassVar[type] = FlextDbOracleModels.DbOracle.ConnectCommand
    DisconnectCommand: ClassVar[type] = FlextDbOracleModels.DbOracle.DisconnectCommand
    TestConnectionCommand: ClassVar[type] = (
        FlextDbOracleModels.DbOracle.TestConnectionCommand
    )
    ExecuteQueryCommand: ClassVar[type] = (
        FlextDbOracleModels.DbOracle.ExecuteQueryCommand
    )
    FetchOneCommand: ClassVar[type] = FlextDbOracleModels.DbOracle.FetchOneCommand
    ExecuteStatementCommand: ClassVar[type] = (
        FlextDbOracleModels.DbOracle.ExecuteStatementCommand
    )
    ExecuteManyCommand: ClassVar[type] = FlextDbOracleModels.DbOracle.ExecuteManyCommand
    GetSchemasCommand: ClassVar[type] = FlextDbOracleModels.DbOracle.GetSchemasCommand
    GetTablesCommand: ClassVar[type] = FlextDbOracleModels.DbOracle.GetTablesCommand
    GetColumnsCommand: ClassVar[type] = FlextDbOracleModels.DbOracle.GetColumnsCommand

    @override
    def execute(self) -> r[None]:
        """Execute dispatcher operation - returns None as this is a factory class."""
        return r[None].ok(None)

    @classmethod
    def _create_connection_handlers(
        cls, services: FlextDbOracleServices
    ) -> dict[
        type,
        tuple[
            Callable[[t.ContainerValue], t.ContainerValue],
            Mapping[str, t.ContainerValue] | None,
        ],
    ]:
        """Create connection-related handler functions."""

        def connect_handler(_cmd: t.ContainerValue) -> t.ContainerValue:
            return services.connect().is_success

        def disconnect_handler(_cmd: t.ContainerValue) -> t.ContainerValue:
            return services.disconnect().is_success

        def connection_test_handler(
            _command_data: t.ContainerValue,
        ) -> t.ContainerValue:
            """Oracle connection test handler - command_data parameter required by dispatcher interface."""
            return services.test_connection().map_or(False)

        return {
            FlextDbOracleModels.DbOracle.ConnectCommand: (connect_handler, None),
            FlextDbOracleModels.DbOracle.DisconnectCommand: (disconnect_handler, None),
            FlextDbOracleModels.DbOracle.TestConnectionCommand: (
                connection_test_handler,
                None,
            ),
        }

    @classmethod
    def build_dispatcher(
        cls, services: FlextDbOracleServices, *, _bus: t.ContainerValue | None = None
    ) -> p.CommandBus:
        """Create a dispatcher instance wired to Oracle services."""
        disp = FlextContainer.get_global().get("command_bus").unwrap()
        if not isinstance(disp, p.CommandBus):
            msg = "command_bus is not CommandBus"
            raise TypeError(msg)
        dispatcher = disp
        _registry = FlextRegistry(dispatcher=dispatcher)
        function_map: dict[
            type,
            tuple[
                Callable[[t.ContainerValue], t.ContainerValue],
                Mapping[str, t.ContainerValue] | None,
            ],
        ] = {}
        function_map.update(cls._create_connection_handlers(services))
        instance = cls()
        function_map.update(instance._create_query_handlers(services))
        function_map.update(instance._create_schema_handlers(services))
        for handler_fn, _metadata in function_map.values():
            dispatcher.register_handler(handler_fn)
        return dispatcher

    def _create_query_handlers(
        self, services: FlextDbOracleServices
    ) -> dict[
        type,
        tuple[
            Callable[[t.ContainerValue], t.ContainerValue],
            Mapping[str, t.ContainerValue] | None,
        ],
    ]:
        """Create query-related handler functions."""

        def execute_query_handler(command: t.ContainerValue) -> t.ContainerValue:
            if isinstance(command, FlextDbOracleModels.DbOracle.ExecuteQueryCommand):
                sql = command.sql
                parameters = t.ConfigMap(root=command.parameters or {})
            else:
                sql = ""
                parameters = t.ConfigMap(root={})
            return services.execute_query(sql, parameters).map_or([])

        def fetch_one_handler(command: t.ContainerValue) -> t.ContainerValue:
            if isinstance(command, FlextDbOracleModels.DbOracle.FetchOneCommand):
                sql = command.sql
                parameters = t.ConfigMap(root=command.parameters or {})
            else:
                sql = ""
                parameters = t.ConfigMap(root={})
            return services.fetch_one(sql, parameters).map_or(None)

        def execute_statement_handler(command: t.ContainerValue) -> t.ContainerValue:
            if isinstance(
                command, FlextDbOracleModels.DbOracle.ExecuteStatementCommand
            ):
                sql = command.sql
                parameters = t.ConfigMap(root=command.parameters or {})
            else:
                sql = ""
                parameters = t.ConfigMap(root={})
            return services.execute_statement(sql, parameters).map_or(0)

        def execute_many_handler(command: t.ContainerValue) -> t.ContainerValue:
            if isinstance(command, FlextDbOracleModels.DbOracle.ExecuteManyCommand):
                sql = command.sql
                parameters_list = command.parameters_list
            else:
                sql = ""
                parameters_list = list[Mapping[str, t.ContainerValue]]()
            return services.execute_many(sql, parameters_list).map_or(0)

        return {
            FlextDbOracleModels.DbOracle.ExecuteQueryCommand: (
                execute_query_handler,
                None,
            ),
            FlextDbOracleModels.DbOracle.FetchOneCommand: (fetch_one_handler, None),
            FlextDbOracleModels.DbOracle.ExecuteStatementCommand: (
                execute_statement_handler,
                None,
            ),
            FlextDbOracleModels.DbOracle.ExecuteManyCommand: (
                execute_many_handler,
                None,
            ),
        }

    def _create_schema_handlers(
        self, services: FlextDbOracleServices
    ) -> dict[
        type,
        tuple[
            Callable[[t.ContainerValue], t.ContainerValue],
            Mapping[str, t.ContainerValue] | None,
        ],
    ]:
        """Create schema/metadata handler functions."""

        def get_schemas_handler(_cmd: t.ContainerValue) -> t.ContainerValue:
            return services.get_schemas().map_or([])

        def get_tables_handler(command: t.ContainerValue) -> t.ContainerValue:
            schema: str | None = None
            if isinstance(command, FlextDbOracleModels.DbOracle.GetTablesCommand):
                schema = command.schema_name
            return services.get_tables(schema).map_or([])

        def get_columns_handler(command: t.ContainerValue) -> t.ContainerValue:
            if isinstance(command, FlextDbOracleModels.DbOracle.GetColumnsCommand):
                table = command.table
                schema = command.schema_name
            else:
                table = ""
                schema = None
            return services.get_columns(table, schema).map_or([])

        return {
            FlextDbOracleModels.DbOracle.GetSchemasCommand: (
                get_schemas_handler,
                None,
            ),
            FlextDbOracleModels.DbOracle.GetTablesCommand: (get_tables_handler, None),
            FlextDbOracleModels.DbOracle.GetColumnsCommand: (
                get_columns_handler,
                None,
            ),
        }


__all__ = ["FlextDbOracleDispatcher"]

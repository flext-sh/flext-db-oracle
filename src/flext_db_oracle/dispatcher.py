"""Dispatcher integration helpers for flext-db-oracle services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from flext_core import FlextContainer, FlextService
from flext_db_oracle import m, p, r, t

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        MutableMapping,
    )

    from flext_db_oracle.services.facade import FlextDbOracleServices


class FlextDbOracleDispatcher(FlextService):
    """Unified Oracle Database Dispatcher with integrated command classes."""

    _container_type: ClassVar[p.ContainerType] = FlextContainer

    @override
    def execute(self) -> p.Result[None]:
        """Execute dispatcher operation - returns None as this is a factory class."""
        return r[None].ok(None)

    @classmethod
    def _create_connection_handlers(
        cls,
        services: FlextDbOracleServices,
    ) -> t.MappingKV[
        type,
        tuple[
            Callable[[t.JsonValue], t.JsonValue],
            t.JsonMapping | None,
        ],
    ]:
        """Create connection-related handler functions."""

        def connect_handler(_cmd: t.JsonValue) -> t.JsonValue:
            return services.connect().success

        def disconnect_handler(_cmd: t.JsonValue) -> t.JsonValue:
            return services.disconnect().success

        def connection_test_handler(
            _command_data: t.JsonValue,
        ) -> t.JsonValue:
            """Oracle connection test handler - command_data parameter required by dispatcher interface."""
            return services.test_connection().map_or(False)

        return {
            m.DbOracle.ConnectCommand: (connect_handler, None),
            m.DbOracle.DisconnectCommand: (disconnect_handler, None),
            m.DbOracle.TestConnectionCommand: (
                connection_test_handler,
                None,
            ),
        }

    @classmethod
    def build_dispatcher(
        cls,
        services: FlextDbOracleServices,
        *,
        _bus: t.JsonValue | None = None,
    ) -> p.Dispatcher:
        """Create a dispatcher instance wired to Oracle services."""
        dispatcher = cls._container_type.shared().dispatcher().unwrap()
        function_map: MutableMapping[
            type,
            tuple[
                Callable[[t.JsonValue], t.JsonValue],
                t.JsonMapping | None,
            ],
        ] = {}
        function_map.update(cls._create_connection_handlers(services))
        instance = cls()
        function_map.update(instance._create_query_handlers(services))
        function_map.update(instance._create_schema_handlers(services))
        for handler_fn, _metadata in function_map.values():

            def _wrap(
                fn: Callable[[t.JsonValue], t.JsonValue],
            ) -> Callable[[t.JsonValue], p.Result[t.JsonValue]]:
                def wrapped(*args: t.JsonValue) -> p.Result[t.JsonValue]:
                    result = fn(*args)
                    return r[t.JsonValue].ok(result)

                return wrapped

            dispatcher.register_handler(_wrap(handler_fn))
        return dispatcher

    def _create_query_handlers(
        self,
        services: FlextDbOracleServices,
    ) -> t.MappingKV[
        type,
        tuple[
            Callable[[t.JsonValue], t.JsonValue],
            t.JsonMapping | None,
        ],
    ]:
        """Create query-related handler functions."""

        def execute_query_handler(command: t.JsonValue) -> t.JsonValue:
            if isinstance(command, m.DbOracle.ExecuteQueryCommand):
                sql = command.sql
                parameters = m.ConfigMap.model_validate({
                    "root": command.parameters or {},
                })
            else:
                sql = ""
                parameters = m.ConfigMap(root={})
            result = services.execute_query(sql, parameters)
            return len(result.value) if result.success else 0

        def fetch_one_handler(command: t.JsonValue) -> t.JsonValue:
            if isinstance(command, m.DbOracle.FetchOneCommand):
                sql = command.sql
                parameters = m.ConfigMap.model_validate({
                    "root": command.parameters or {},
                })
            else:
                sql = ""
                parameters = m.ConfigMap(root={})
            result = services.fetch_one(sql, parameters)
            return str(result.value) if result.success and result.value else ""

        def execute_statement_handler(command: t.JsonValue) -> t.JsonValue:
            if isinstance(
                command,
                m.DbOracle.ExecuteStatementCommand,
            ):
                sql = command.sql
                parameters = m.ConfigMap.model_validate({
                    "root": command.parameters or {},
                })
            else:
                sql = ""
                parameters = m.ConfigMap(root={})
            return services.execute_statement(sql, parameters).map_or(0)

        def execute_many_handler(command: t.JsonValue) -> t.JsonValue:
            if isinstance(command, m.DbOracle.ExecuteManyCommand):
                sql = command.sql
                parameters_list: t.SequenceOf[t.JsonMapping] = list(
                    command.parameters_list,
                )
            else:
                sql = ""
                parameters_list = []
            return services.execute_many(sql, parameters_list).map_or(0)

        return {
            m.DbOracle.ExecuteQueryCommand: (
                execute_query_handler,
                None,
            ),
            m.DbOracle.FetchOneCommand: (fetch_one_handler, None),
            m.DbOracle.ExecuteStatementCommand: (
                execute_statement_handler,
                None,
            ),
            m.DbOracle.ExecuteManyCommand: (
                execute_many_handler,
                None,
            ),
        }

    def _create_schema_handlers(
        self,
        services: FlextDbOracleServices,
    ) -> t.MappingKV[
        type,
        tuple[
            Callable[[t.JsonValue], t.JsonValue],
            t.JsonMapping | None,
        ],
    ]:
        """Create schema/metadata handler functions."""

        def get_schemas_handler(_cmd: t.JsonValue) -> t.JsonValue:
            result = services.fetch_schemas()
            return ",".join(result.value) if result.success else ""

        def get_tables_handler(command: t.JsonValue) -> t.JsonValue:
            schema: str | None = None
            if isinstance(command, m.DbOracle.GetTablesCommand):
                schema = command.schema_name
            result = services.fetch_tables(schema)
            return ",".join(result.value) if result.success else ""

        def get_columns_handler(command: t.JsonValue) -> t.JsonValue:
            if isinstance(command, m.DbOracle.GetColumnsCommand):
                table = command.table
                schema = command.schema_name
            else:
                table = ""
                schema = None
            result = services.fetch_columns(table, schema)
            return ",".join(col.name for col in result.value) if result.success else ""

        return {
            m.DbOracle.GetSchemasCommand: (
                get_schemas_handler,
                None,
            ),
            m.DbOracle.GetTablesCommand: (get_tables_handler, None),
            m.DbOracle.GetColumnsCommand: (
                get_columns_handler,
                None,
            ),
        }


__all__: list[str] = ["FlextDbOracleDispatcher"]

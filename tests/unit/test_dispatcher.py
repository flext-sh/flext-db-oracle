"""Behavioral tests for FlextDbOracleDispatcher.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleDispatcher, FlextDbOracleSettings, p
from flext_db_oracle.services.facade import FlextDbOracleServices
from tests import m


class TestsFlextDbOracleDispatcher:
    """Observable public contract of the Oracle dispatcher and its command surface."""

    @pytest.fixture
    def services(self) -> FlextDbOracleServices:
        """Oracle services wired to non-connecting placeholder settings."""
        settings = FlextDbOracleSettings(
            DbOracle={
                "host": "test-host",
                "username": "test-user",
                "password": "test-password",
            },
        )
        return FlextDbOracleServices(settings=settings)

    # --- dispatcher factory contract -------------------------------------

    def test_execute_reports_success(self) -> None:
        """execute() is a no-op factory hook that yields a successful result."""
        result = FlextDbOracleDispatcher().execute()

        tm.that(result.success, eq=True)

    def test_build_dispatcher_exposes_dispatch_capability(
        self,
        services: FlextDbOracleServices,
    ) -> None:
        """build_dispatcher returns a wired dispatcher exposing dispatch()."""
        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)

        tm.that(callable(dispatcher.dispatch), eq=True)

    def test_build_dispatcher_exposes_register_handler_capability(
        self,
        services: FlextDbOracleServices,
    ) -> None:
        """The wired dispatcher can accept handler registrations."""
        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)

        tm.that(callable(dispatcher.register_handler), eq=True)

    def test_build_dispatcher_reuses_shared_dispatcher(
        self,
        services: FlextDbOracleServices,
    ) -> None:
        """Repeated builds resolve the same shared container dispatcher."""
        first = FlextDbOracleDispatcher.build_dispatcher(services)
        second = FlextDbOracleDispatcher.build_dispatcher(services)

        tm.that(first is second, eq=True)

    # --- command surface contract ----------------------------------------

    def test_execute_query_command_carries_sql_and_parameters(self) -> None:
        """ExecuteQueryCommand preserves sql and explicit parameters."""
        cmd = m.DbOracle.ExecuteQueryCommand(
            sql="SELECT 1 FROM DUAL",
            parameters={"limit": 10},
        )

        tm.that(cmd.sql, eq="SELECT 1 FROM DUAL")
        tm.that(cmd.parameters, eq={"limit": 10})

    @pytest.mark.parametrize(
        "command_type",
        [
            m.DbOracle.ExecuteQueryCommand,
            m.DbOracle.FetchOneCommand,
            m.DbOracle.ExecuteStatementCommand,
        ],
    )
    def test_sql_command_parameters_default_to_none(
        self,
        command_type: type[p.DbOracle.ExecuteQueryCommand],
    ) -> None:
        """SQL commands omit parameters as None when none are supplied."""
        cmd = command_type(sql="SELECT 1 FROM DUAL")

        tm.that(cmd.sql, eq="SELECT 1 FROM DUAL")
        tm.that(cmd.parameters, none=True)

    @pytest.mark.parametrize(
        "command_type",
        [
            m.DbOracle.ExecuteQueryCommand,
            m.DbOracle.FetchOneCommand,
            m.DbOracle.ExecuteStatementCommand,
            m.DbOracle.ExecuteManyCommand,
        ],
    )
    def test_sql_command_requires_sql(
        self,
        command_type: type[p.DbOracle.ExecuteQueryCommand],
    ) -> None:
        """SQL is a mandatory field; construction without it fails validation."""
        with pytest.raises(m.ValidationError):
            command_type()

    def test_execute_many_command_preserves_parameter_batches(self) -> None:
        """ExecuteManyCommand keeps the ordered batch of parameter mappings."""
        cmd = m.DbOracle.ExecuteManyCommand(
            sql="INSERT INTO t VALUES (:v)",
            parameters_list=[{"v": 1}, {"v": 2}],
        )

        tm.that(cmd.sql, eq="INSERT INTO t VALUES (:v)")
        tm.that(list(cmd.parameters_list), eq=[{"v": 1}, {"v": 2}])

    def test_get_columns_command_carries_table_and_schema(self) -> None:
        """GetColumnsCommand exposes both the table and its schema."""
        cmd = m.DbOracle.GetColumnsCommand(table="EMPLOYEES", schema_name="HR")

        tm.that(cmd.table, eq="EMPLOYEES")
        tm.that(cmd.schema_name, eq="HR")

    @pytest.mark.parametrize(
        ("schema_name", "expected"),
        [
            ("HR", "HR"),
            (None, None),
        ],
    )
    def test_get_tables_command_schema_is_optional(
        self,
        schema_name: str | None,
        expected: str | None,
    ) -> None:
        """GetTablesCommand accepts an optional schema, defaulting to None."""
        cmd = m.DbOracle.GetTablesCommand(schema_name=schema_name)

        tm.that(cmd.schema_name, eq=expected)

    def test_get_tables_command_defaults_schema_to_none(self) -> None:
        """Omitting schema_name yields a None schema selector."""
        cmd = m.DbOracle.GetTablesCommand()

        tm.that(cmd.schema_name, none=True)

    def test_command_round_trips_through_model_dump(self) -> None:
        """Public model_dump surfaces the command's declared field values."""
        cmd = m.DbOracle.ExecuteQueryCommand(
            sql="SELECT * FROM DUAL",
            parameters={"a": 1},
        )

        dumped = cmd.model_dump()

        tm.that(dumped["sql"], eq="SELECT * FROM DUAL")
        tm.that(dumped["parameters"], eq={"a": 1})

"""Behavioral tests for the Oracle metadata service contract.

Exercises the OBSERVABLE public contract of ``FlextDbOracleServices`` metadata
introspection: the ``r[T]`` outcome of fallible operations when no live
connection exists, the settings/execute contract of the facade, and the public
state of the ``m.DbOracle.Column`` / ``m.DbOracle.Table`` domain models.

No live Oracle instance is required: without a connection every schema
introspection call must surface a failure result, never raise and never invent
data.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleSettings, p
from flext_db_oracle.services.facade import FlextDbOracleServices
from tests import m

if TYPE_CHECKING:
    from collections.abc import Callable


class TestsFlextDbOracleMetadata:
    """Public-contract tests for Oracle metadata introspection."""

    @pytest.fixture
    def settings(self) -> FlextDbOracleSettings:
        """Return in-memory Oracle settings pointing at no reachable host."""
        return FlextDbOracleSettings(
            DbOracle={
                "host": "test",
                "port": 1521,
                "service_name": "TEST",
                "username": "test",
                "password": "test",
            }
        )

    @pytest.fixture
    def services(self, settings: FlextDbOracleSettings) -> FlextDbOracleServices:
        """Return a freshly composed, unconnected services facade."""
        return FlextDbOracleServices(settings=settings)

    # -- facade contract ---------------------------------------------------

    def test_settings_property_exposes_supplied_connection_config(
        self, services: FlextDbOracleServices, settings: FlextDbOracleSettings
    ) -> None:
        """The settings property returns the exact configuration supplied."""
        bound = services.settings

        tm.that(bound, eq=settings)
        tm.that(bound.DbOracle.host, eq="test")
        tm.that(bound.DbOracle.port, eq=1521)
        tm.that(bound.DbOracle.service_name, eq="TEST")
        tm.that(bound.DbOracle.username, eq="test")

    def test_new_facade_reports_not_connected(
        self, services: FlextDbOracleServices
    ) -> None:
        """A freshly built facade is not connected until connect succeeds."""
        tm.that(services.connected(), eq=False)

    def test_execute_returns_active_settings_as_success(
        self, services: FlextDbOracleServices, settings: FlextDbOracleSettings
    ) -> None:
        """execute() succeeds and yields the active Oracle configuration."""
        value = tm.ok(services.execute())

        tm.that(value, eq=settings)

    # -- fallible introspection: not-connected failure contract ------------

    @pytest.mark.parametrize(
        ("label", "call"),
        [
            ("fetch_schemas", lambda s: s.fetch_schemas()),
            ("fetch_tables_default", lambda s: s.fetch_tables()),
            ("fetch_tables_schema", lambda s: s.fetch_tables("APP_SCHEMA")),
            ("fetch_tables_empty_schema", lambda s: s.fetch_tables("")),
            ("fetch_tables_none_schema", lambda s: s.fetch_tables(None)),
            ("fetch_columns_table", lambda s: s.fetch_columns("T")),
            ("fetch_columns_schema", lambda s: s.fetch_columns("T", "APP_SCHEMA")),
            ("fetch_table_metadata", lambda s: s.fetch_table_metadata("T")),
            ("fetch_primary_keys", lambda s: s.fetch_primary_keys("T")),
            ("test_connection", lambda s: s.test_connection()),
        ],
    )
    def test_metadata_op_fails_when_not_connected(
        self,
        services: FlextDbOracleServices,
        label: str,
        call: Callable[[FlextDbOracleServices], p.Result[object]],
    ) -> None:
        """Every introspection op returns a failure citing the missing link."""
        _ = label
        result = call(services)

        error = tm.fail(result, has="Not connected")
        tm.that(bool(error), eq=True)

    def test_failed_op_recovers_via_unwrap_or_default(
        self, services: FlextDbOracleServices
    ) -> None:
        """A failed result yields the caller default via unwrap_or."""
        fallback: list[str] = ["<none>"]

        recovered = services.fetch_schemas().unwrap_or(fallback)

        tm.that(recovered, eq=fallback)

    def test_map_does_not_run_transform_on_failure(
        self, services: FlextDbOracleServices
    ) -> None:
        """map() is skipped for a failure and the error is preserved intact."""
        mapped = services.fetch_tables("APP_SCHEMA").map(len)

        tm.fail(mapped, has="Not connected")

    def test_recover_swaps_a_failed_metadata_op_for_success(
        self, services: FlextDbOracleServices
    ) -> None:
        """Recover turns a failure into a success carrying the fallback."""
        recovered = services.fetch_schemas().recover(lambda _error: ["RECOVERED"])

        value = tm.ok(recovered)
        tm.that(value, eq=["RECOVERED"])

    # -- Column model public state -----------------------------------------

    @pytest.mark.parametrize(
        ("data_type", "nullable"),
        [("NUMBER", False), ("VARCHAR2", True), ("DATE", True)],
    )
    def test_column_exposes_public_field_state(
        self, data_type: str, nullable: bool
    ) -> None:
        """Column reflects the field values supplied through its public API."""
        column = m.DbOracle.Column(name="ID", data_type=data_type, nullable=nullable)

        tm.that(column.name, eq="ID")
        tm.that(column.data_type, eq=data_type)
        tm.that(column.nullable, eq=nullable)
        tm.that(column.primary_key, eq=False)
        tm.that(column.default_value, eq="")

    def test_column_supports_mapping_access_contract(self) -> None:
        """Column exposes a public key lookup and membership contract."""
        column = m.DbOracle.Column(name="CODE", data_type="VARCHAR2")

        tm.that(column["name"], eq="CODE")
        tm.that(column["column_name"], eq="CODE")
        tm.that(column["data_type"], eq="VARCHAR2")
        tm.that("data_type" in column, eq=True)
        tm.that("missing_key" in column, eq=False)
        tm.that(column["missing_key"], eq="")

    def test_column_model_dump_roundtrips_public_fields(self) -> None:
        """model_dump surfaces the public column fields for serialization."""
        column = m.DbOracle.Column(
            name="AMOUNT", data_type="NUMBER", nullable=True, primary_key=True
        )

        dumped = column.model_dump()

        tm.that(dumped["name"], eq="AMOUNT")
        tm.that(dumped["data_type"], eq="NUMBER")
        tm.that(dumped["nullable"], eq=True)
        tm.that(dumped["primary_key"], eq=True)

    # -- Table model public state ------------------------------------------

    def test_table_aggregates_its_columns(self) -> None:
        """Table exposes its name, owner, and ordered column collection."""
        columns = [
            m.DbOracle.Column(name="ID", data_type="NUMBER", nullable=False),
            m.DbOracle.Column(name="NAME", data_type="VARCHAR2", nullable=True),
        ]
        table = m.DbOracle.Table(
            name="COMPLEX_TABLE", owner="APP_SCHEMA", columns=columns
        )

        tm.that(table.name, eq="COMPLEX_TABLE")
        tm.that(table.owner, eq="APP_SCHEMA")
        tm.that(len(table.columns), eq=2)
        tm.that(table.columns[0].name, eq="ID")
        tm.that(table.columns[1].name, eq="NAME")

    def test_table_defaults_owner_and_columns_when_omitted(self) -> None:
        """A table declared with only a name defaults owner and columns."""
        table = m.DbOracle.Table(name="BARE")

        tm.that(table.name, eq="BARE")
        tm.that(table.owner, eq="")
        tm.that(len(table.columns), eq=0)

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
from typing import TYPE_CHECKING, TypeVar
import pytest
from flext_db_oracle import FlextDbOracleSettings
from flext_db_oracle.services.facade import FlextDbOracleServices
from flext_tests import tm
from tests import m, t

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from flext_db_oracle import p

_T = TypeVar("_T")


# flext-1wjg1.16: named functions (not lambdas) so pyrefly can type the
# `services` parameter from the explicit annotation -- an inline lambda
# inside the parametrize list literal has no expected-type context to infer
# its parameter from ([implicit-any-lambda]).
def _call_fetch_schemas(services: FlextDbOracleServices) -> p.Result[t.StrSequence]:
    return services.fetch_schemas()


def _call_fetch_tables_default(
    services: FlextDbOracleServices,
) -> p.Result[t.StrSequence]:
    return services.fetch_tables()


def _call_fetch_tables_schema(
    services: FlextDbOracleServices,
) -> p.Result[t.StrSequence]:
    return services.fetch_tables("APP_SCHEMA")


def _call_fetch_tables_empty_schema(
    services: FlextDbOracleServices,
) -> p.Result[t.StrSequence]:
    return services.fetch_tables("")


def _call_fetch_tables_none_schema(
    services: FlextDbOracleServices,
) -> p.Result[t.StrSequence]:
    return services.fetch_tables(None)


def _call_fetch_columns_table(
    services: FlextDbOracleServices,
) -> p.Result[Sequence[m.DbOracle.Column]]:
    return services.fetch_columns("T")


def _call_fetch_columns_schema(
    services: FlextDbOracleServices,
) -> p.Result[Sequence[m.DbOracle.Column]]:
    return services.fetch_columns("T", "APP_SCHEMA")


def _call_fetch_table_metadata(
    services: FlextDbOracleServices,
) -> p.Result[m.DbOracle.TableMetadata]:
    return services.fetch_table_metadata("T")


def _call_fetch_primary_keys(
    services: FlextDbOracleServices,
) -> p.Result[t.StrSequence]:
    return services.fetch_primary_keys("T")


def _call_test_connection(services: FlextDbOracleServices) -> p.Result[bool]:
    return services.test_connection()


class TestsFlextDbOracleMetadata:
    """Public-contract tests for Oracle metadata introspection."""

    @pytest.fixture
    def settings(self) -> FlextDbOracleSettings:
        """Return in-memory Oracle settings pointing at no reachable host."""
        return FlextDbOracleSettings.model_validate({
            "DbOracle": {
                "host": "test",
                "port": 1521,
                "service_name": "TEST",
                "username": "test",
                "password": "test",
            }
        })

    @pytest.fixture
    def services(self, settings: FlextDbOracleSettings) -> FlextDbOracleServices:
        """Return a freshly composed, unconnected services facade."""
        return FlextDbOracleServices(settings=settings)

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

    @pytest.mark.parametrize(
        ("label", "call"),
        [
            ("fetch_schemas", _call_fetch_schemas),
            ("fetch_tables_default", _call_fetch_tables_default),
            ("fetch_tables_schema", _call_fetch_tables_schema),
            ("fetch_tables_empty_schema", _call_fetch_tables_empty_schema),
            ("fetch_tables_none_schema", _call_fetch_tables_none_schema),
            ("fetch_columns_table", _call_fetch_columns_table),
            ("fetch_columns_schema", _call_fetch_columns_schema),
            ("fetch_table_metadata", _call_fetch_table_metadata),
            ("fetch_primary_keys", _call_fetch_primary_keys),
            ("test_connection", _call_test_connection),
        ],
    )
    def test_metadata_op_fails_when_not_connected(
        self,
        services: FlextDbOracleServices,
        label: str,
        call: Callable[[FlextDbOracleServices], p.Result[_T]],
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

    @pytest.mark.parametrize(
        ("data_type", "nullable"),
        [("NUMBER", False), ("VARCHAR2", True), ("DATE", True)],
    )
    def test_column_exposes_public_field_state(
        self, data_type: str, *, nullable: bool
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

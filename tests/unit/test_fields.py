"""Behavioral tests for Oracle settings and domain-model field contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleSettings
from tests import m

# NOTE (multi-agent): ADR-005 — settings fields live under settings.DbOracle.*;
# the flat from_url/from_env factories and uppercase/business-rule validators
# were removed by design (layer-0 scalar namespace), so those tests are gone.


class TestsFlextDbOracleFields:
    """Observable behavior of settings and DbOracle domain models."""

    # ---- FlextDbOracleSettings default contract -------------------------

    def test_default_settings_expose_expected_connection_values(self) -> None:
        """Defaults construct a valid, fully-populated Oracle settings object."""
        settings = FlextDbOracleSettings()

        tm.that(settings.DbOracle.host, eq="localhost")
        tm.that(settings.DbOracle.port, eq=1521)
        tm.that(settings.DbOracle.service_name, eq="XEPDB1")
        tm.that(settings.DbOracle.username, eq="system")

    def test_settings_model_dump_round_trips_overrides(self) -> None:
        """Public model_dump reflects caller-provided namespace values."""
        settings = FlextDbOracleSettings(
            DbOracle={
                "host": "db.example.com",
                "port": 1600,
                "username": "app_user",
            },
        )

        dumped = settings.model_dump()

        tm.that(dumped["DbOracle"]["host"], eq="db.example.com")
        tm.that(dumped["DbOracle"]["port"], eq=1600)
        tm.that(dumped["DbOracle"]["username"], eq="app_user")

    def test_service_name_round_trips_through_namespace(self) -> None:
        """service_name is stored verbatim inside the DbOracle namespace."""
        settings = FlextDbOracleSettings(DbOracle={"service_name": "MYPDB"})

        tm.that(settings.DbOracle.service_name, eq="MYPDB")

    def test_sid_only_configuration_is_accepted(self) -> None:
        """A legacy SID connection is valid inside the DbOracle namespace."""
        settings = FlextDbOracleSettings(DbOracle={"service_name": "", "sid": "legacy"})

        tm.that(settings.DbOracle.sid, eq="legacy")
        tm.that(settings.DbOracle.service_name, eq="")

    # NOTE: p.DbOracle.ConnectionStatus behavior is intentionally NOT covered
    # here. That model carries a `datetime` forward reference that is unresolved
    # at runtime (raises PydanticUserError demanding model_rebuild()), so it
    # cannot be instantiated through the public API in this environment. The
    # sibling tests/unit/test_models.py fails on the same defect. Exercising it
    # would require a src fix or a forbidden model_rebuild(); neither is in
    # scope for this file, so no test is kept rather than poking private
    # model_fields.

    # ---- QueryResult behavior -------------------------------------------

    def test_query_result_syncs_row_count_and_derives_columns(self) -> None:
        """row_count auto-syncs to row length and column_count reflects columns."""
        result = m.DbOracle.QueryResult(
            query="SELECT id, name FROM t",
            columns=("id", "name"),
            rows=[
                m.DbOracle.RowData(values=(1, "a")),
                m.DbOracle.RowData(values=(2, "b")),
            ],
        )

        tm.that(result.row_count, eq=2)
        tm.that(result.column_count, eq=2)
        tm.that(result.has_results, eq=True)

    def test_empty_query_result_has_no_results(self) -> None:
        """An empty result reports zero rows and no results."""
        result = m.DbOracle.QueryResult(query="SELECT 1 FROM dual")

        tm.that(result.row_count, eq=0)
        tm.that(result.has_results, eq=False)
        tm.that(result.column_count, eq=0)

    def test_query_result_rejects_row_column_mismatch(self) -> None:
        """A row whose width differs from the column count is rejected."""
        with pytest.raises(ValueError, match="match column count"):
            m.DbOracle.QueryResult(
                query="SELECT a FROM t",
                columns=("a",),
                rows=[p.DbOracle.RowData(values=(1, 2))],
            )

    # ---- RowData / ColumnMetadata contracts -----------------------------

    def test_row_data_defaults_to_empty_values(self) -> None:
        """RowData without values yields an empty tuple payload."""
        row = m.DbOracle.RowData()

        tm.that(tuple(row.values), eq=())

    def test_column_metadata_exposes_declared_fields(self) -> None:
        """ColumnMetadata surfaces name, data_type, and a default nullable flag."""
        column = m.DbOracle.ColumnMetadata(name="ID", data_type="NUMBER")

        tm.that(column.name, eq="ID")
        tm.that(column.data_type, eq="NUMBER")
        tm.that(column.nullable, eq=True)

    def test_column_metadata_respects_non_nullable_flag(self) -> None:
        """Explicit nullable=False is preserved on the public field."""
        column = m.DbOracle.ColumnMetadata(
            name="ID",
            data_type="NUMBER",
            nullable=False,
        )

        tm.that(column.nullable, eq=False)

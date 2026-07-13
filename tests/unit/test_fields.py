"""Behavioral tests for Oracle settings and domain-model field contracts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_db_oracle import FlextDbOracleSettings
from tests.models import m

# NOTE (multi-agent): ADR-005 — settings fields live under settings.DbOracle.*;
# the flat from_url/from_env factories and uppercase/business-rule validators
# were removed by design (layer-0 scalar namespace), so those tests are gone.


class TestsFlextDbOracleFields:
    """Observable behavior of settings and DbOracle domain models."""

    # ---- FlextDbOracleSettings default contract -------------------------

    def test_default_settings_expose_expected_connection_values(self) -> None:
        """Defaults construct a valid, fully-populated Oracle settings object."""
        settings = FlextDbOracleSettings()

        assert settings.DbOracle.host == "localhost"
        assert settings.DbOracle.port == 1521
        assert settings.DbOracle.service_name == "XEPDB1"
        assert settings.DbOracle.username == "system"

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

        assert dumped["DbOracle"]["host"] == "db.example.com"
        assert dumped["DbOracle"]["port"] == 1600
        assert dumped["DbOracle"]["username"] == "app_user"

    def test_service_name_round_trips_through_namespace(self) -> None:
        """service_name is stored verbatim inside the DbOracle namespace."""
        settings = FlextDbOracleSettings(DbOracle={"service_name": "MYPDB"})

        assert settings.DbOracle.service_name == "MYPDB"

    def test_sid_only_configuration_is_accepted(self) -> None:
        """A legacy SID connection is valid inside the DbOracle namespace."""
        settings = FlextDbOracleSettings(DbOracle={"service_name": "", "sid": "legacy"})

        assert settings.DbOracle.sid == "legacy"
        assert settings.DbOracle.service_name == ""

    # NOTE: m.DbOracle.ConnectionStatus behavior is intentionally NOT covered
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

        assert result.row_count == 2
        assert result.column_count == 2
        assert result.has_results is True

    def test_empty_query_result_has_no_results(self) -> None:
        """An empty result reports zero rows and no results."""
        result = m.DbOracle.QueryResult(query="SELECT 1 FROM dual")

        assert result.row_count == 0
        assert result.has_results is False
        assert result.column_count == 0

    def test_query_result_rejects_row_column_mismatch(self) -> None:
        """A row whose width differs from the column count is rejected."""
        with pytest.raises(ValueError, match="match column count"):
            m.DbOracle.QueryResult(
                query="SELECT a FROM t",
                columns=("a",),
                rows=[m.DbOracle.RowData(values=(1, 2))],
            )

    # ---- RowData / ColumnMetadata contracts -----------------------------

    def test_row_data_defaults_to_empty_values(self) -> None:
        """RowData without values yields an empty tuple payload."""
        row = m.DbOracle.RowData()

        assert tuple(row.values) == ()

    def test_column_metadata_exposes_declared_fields(self) -> None:
        """ColumnMetadata surfaces name, data_type, and a default nullable flag."""
        column = m.DbOracle.ColumnMetadata(name="ID", data_type="NUMBER")

        assert column.name == "ID"
        assert column.data_type == "NUMBER"
        assert column.nullable is True

    def test_column_metadata_respects_non_nullable_flag(self) -> None:
        """Explicit nullable=False is preserved on the public field."""
        column = m.DbOracle.ColumnMetadata(
            name="ID",
            data_type="NUMBER",
            nullable=False,
        )

        assert column.nullable is False

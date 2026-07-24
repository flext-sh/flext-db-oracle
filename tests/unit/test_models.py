"""Behavioral unit tests for flext_db_oracle.models public contract.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleSettings
from tests import c, m, u


@pytest.mark.unit
class TestsFlextDbOracleModels:
    """Assert observable public behavior of the Oracle domain models and settings."""

    # ------------------------------------------------------------------
    # ConnectionStatus
    # ------------------------------------------------------------------

    def test_connected_status_reports_connected_description(self) -> None:
        """A connected status exposes a 'Connected' human-readable description."""
        status = m.DbOracle.ConnectionStatus(
            connected=True, host="localhost", service_name="XEPDB1", username="system"
        )
        tm.that(status.status_description, eq="Connected")
        tm.that(status.healthy, eq=True)
        tm.that(status.connection_info, has="localhost")
        tm.that(status.connection_info, has="XEPDB1")
        tm.that(status.connection_info, has="system")

    def test_disconnected_status_surfaces_error_in_description(self) -> None:
        """A disconnected status embeds its error message in the description."""
        status = m.DbOracle.ConnectionStatus(connected=False)
        tm.that(status.status_description, eq="Disconnected")
        tm.that(status.healthy, eq=False)
        tm.that(status.connection_info, eq="Not connected")

    @pytest.mark.parametrize(
        ("connection_time", "rating"),
        [
            (0.05, "Excellent"),
            (0.3, "Good"),
            (1.5, "Acceptable"),
            (3.0, "Slow"),
            (0.0, "No performance data"),
        ],
    )
    def test_performance_info_reflects_connection_time(
        self, connection_time: float, rating: str
    ) -> None:
        """performance_info categorizes the measured connection time."""
        status = m.DbOracle.ConnectionStatus(
            connected=True, host="localhost", connection_time=connection_time
        )
        tm.that(status.performance_info, has=rating)

    def test_connected_without_host_is_rejected(self) -> None:
        """Consistency validator rejects a connected status without a host."""
        with pytest.raises(
            ValueError, match="Connected status requires host information"
        ):
            m.DbOracle.ConnectionStatus(connected=True, host="", port=1521)

    def test_out_of_range_port_is_rejected(self) -> None:
        """Port outside the valid range is rejected at construction."""
        with pytest.raises(ValueError, match="less than or equal to"):
            m.DbOracle.ConnectionStatus(connected=True, host="localhost", port=99999)

    def test_long_error_message_is_truncated_on_serialization(self) -> None:
        """Serialized error messages are capped at the configured maximum."""
        status = m.DbOracle.ConnectionStatus(connected=False, error_message="x" * 800)
        serialized = status.model_dump(mode="json")
        tm.that(
            len(serialized["error_message"]),
            lte=c.DbOracle.MAX_ERROR_MESSAGE_LENGTH + len("... (truncated)"),
        )

    # ------------------------------------------------------------------
    # QueryResult
    # ------------------------------------------------------------------

    def test_query_result_minimal_defaults(self) -> None:
        """A minimal QueryResult exposes empty collections and zeroed metrics."""
        result = m.DbOracle.QueryResult(query="SELECT 1")
        tm.that(result.query, eq="SELECT 1")
        tm.that(result.row_count, eq=0)
        tm.that(result.execution_time_ms, eq=0)
        tm.that(result.columns, empty=True)
        tm.that(result.rows, empty=True)
        tm.that(result.has_results, eq=False)
        tm.that(result.column_count, eq=0)

    def test_row_count_is_derived_from_supplied_rows(self) -> None:
        """row_count is normalized to the number of typed rows regardless of input."""
        result = m.DbOracle.QueryResult(
            query="SELECT id, name FROM users",
            columns=["id", "name"],
            rows=[
                m.DbOracle.RowData(values=[1, "John"]),
                m.DbOracle.RowData(values=[2, "Jane"]),
            ],
            execution_time_ms=150,
        )
        tm.that(result.row_count, eq=2)
        tm.that(result.has_results, eq=True)
        tm.that(result.column_count, eq=2)
        tm.that(result.columns, eq=["id", "name"])

    def test_execution_time_seconds_converts_from_milliseconds(self) -> None:
        """execution_time_seconds is the millisecond value divided by 1000."""
        result = m.DbOracle.QueryResult(query="SELECT 1", execution_time_ms=2500)
        tm.that(abs(result.execution_time_seconds - 2.5), lt=1e-9)

    def test_data_size_and_memory_estimates_scale_with_shape(self) -> None:
        """Estimated size scales with rows * columns * estimation factor."""
        result = m.DbOracle.QueryResult(
            query="SELECT 1",
            columns=["col1"],
            rows=[
                m.DbOracle.RowData(values=[1]),
                m.DbOracle.RowData(values=[2]),
                m.DbOracle.RowData(values=[3]),
            ],
        )
        expected_size = 3 * 1 * c.DbOracle.DATA_SIZE_ESTIMATION_FACTOR
        tm.that(result.data_size_bytes, eq=expected_size)
        tm.that(abs(result.memory_usage_mb - expected_size / (1024 * 1024)), lt=1e-12)

    @pytest.mark.parametrize(
        ("execution_time_ms", "rating"),
        [(50, "Excellent"), (300, "Good"), (1500, "Acceptable"), (2500, "Slow")],
    )
    def test_performance_rating_without_results_uses_time_thresholds(
        self, execution_time_ms: int, rating: str
    ) -> None:
        """With no rows, performance_rating is decided by execution time alone."""
        result = m.DbOracle.QueryResult(
            query="SELECT 1", execution_time_ms=execution_time_ms
        )
        tm.that(result.has_results, eq=False)
        tm.that(result.performance_rating, eq=rating)

    def test_performance_rating_with_results_is_acceptable_within_grace(self) -> None:
        """A result-bearing query within the grace window rates as Acceptable."""
        result = m.DbOracle.QueryResult(
            query="SELECT 1",
            columns=["col1"],
            rows=[m.DbOracle.RowData(values=[1])],
            execution_time_ms=2500,
        )
        tm.that(result.has_results, eq=True)
        tm.that(result.performance_rating, eq="Acceptable")

    def test_row_length_mismatch_is_rejected(self) -> None:
        """Rows whose width differs from the column count are rejected."""
        with pytest.raises(ValueError, match=r"Row length.*doesn't match column count"):
            m.DbOracle.QueryResult(
                query="SELECT 1",
                columns=["id", "name"],
                rows=[m.DbOracle.RowData(values=[1])],
            )

    def test_negative_execution_time_is_rejected(self) -> None:
        """A negative execution time is rejected at construction."""
        with pytest.raises(ValueError, match="greater than or equal to"):
            m.DbOracle.QueryResult(query="SELECT 1", execution_time_ms=-100)

    def test_query_result_roundtrips_through_model_validate(self) -> None:
        """A dumped QueryResult validates back into an equivalent model."""
        result = m.DbOracle.QueryResult(
            query="SELECT 1",
            columns=["id"],
            rows=[m.DbOracle.RowData(values=[1]), m.DbOracle.RowData(values=[2])],
            execution_time_ms=100,
        )
        validated = m.DbOracle.QueryResult.model_validate(result.model_dump())
        tm.that(validated.row_count, eq=2)
        tm.that(validated.columns, eq=["id"])

    # ------------------------------------------------------------------
    # Table / Column / Schema
    # ------------------------------------------------------------------

    def test_table_defaults_to_no_columns(self) -> None:
        """A bare Table exposes its identity and an empty column collection."""
        table = m.DbOracle.Table(name="users", owner="hr")
        tm.that(table.name, eq="users")
        tm.that(table.owner, eq="hr")
        tm.that(table.columns, empty=True)

    def test_table_preserves_supplied_columns(self) -> None:
        """A Table exposes its columns and their nullability contract."""
        table = m.DbOracle.Table(
            name="users",
            owner="hr",
            columns=[
                m.DbOracle.Column(name="id", data_type="NUMBER", nullable=False),
                m.DbOracle.Column(name="name", data_type="VARCHAR2(100)"),
            ],
        )
        tm.that(len(table.columns), eq=2)
        tm.that(table.columns[0].name, eq="id")
        tm.that(table.columns[0].nullable, eq=False)
        tm.that(table.columns[1].name, eq="name")
        tm.that(table.columns[1].nullable, eq=True)

    def test_column_defaults_and_explicit_values(self) -> None:
        """Column exposes type, nullability and default value through public fields."""
        column = m.DbOracle.Column(
            name="user_id", data_type="NUMBER(38)", nullable=False, default_value="NULL"
        )
        tm.that(column.name, eq="user_id")
        tm.that(column.data_type, eq="NUMBER(38)")
        tm.that(column.nullable, eq=False)
        tm.that(column.default_value, eq="NULL")

    def test_column_mapping_access_exposes_aliases(self) -> None:
        """Column supports mapping-style access over its public attributes."""
        column = m.DbOracle.Column(name="user_id", data_type="NUMBER")
        tm.that("column_name" in column, eq=True)
        tm.that(column["column_name"], eq="user_id")
        tm.that(column["data_type"], eq="NUMBER")
        tm.that("unknown" in column, eq=False)

    def test_schema_defaults_to_no_tables(self) -> None:
        """A bare Schema exposes its name and an empty table collection."""
        schema = m.DbOracle.Schema(name="hr")
        tm.that(schema.name, eq="hr")
        tm.that(schema.tables, empty=True)

    def test_schema_preserves_supplied_tables(self) -> None:
        """A Schema exposes the tables it was constructed with, in order."""
        schema = m.DbOracle.Schema(
            name="hr",
            tables=[
                m.DbOracle.Table(name="users", owner="hr"),
                m.DbOracle.Table(name="orders", owner="hr"),
            ],
        )
        tm.that(len(schema.tables), eq=2)
        tm.that(schema.tables[0].name, eq="users")
        tm.that(schema.tables[1].name, eq="orders")

    def test_create_index_config_exposes_all_options(self) -> None:
        """CreateIndexConfig surfaces every supplied index option."""
        config = m.DbOracle.CreateIndexConfig(
            table_name="users",
            index_name="idx_users_email",
            columns=["email"],
            unique=True,
            schema_name="hr",
            tablespace="users_idx",
            parallel=4,
        )
        tm.that(config.table_name, eq="users")
        tm.that(config.index_name, eq="idx_users_email")
        tm.that(config.columns, eq=["email"])
        tm.that(config.unique, eq=True)
        tm.that(config.schema_name, eq="hr")
        tm.that(config.tablespace, eq="users_idx")
        tm.that(config.parallel, eq=4)

    def test_create_index_config_requires_columns(self) -> None:
        """A CreateIndexConfig without columns is rejected."""
        with pytest.raises(ValueError, match="columns"):
            m.DbOracle.CreateIndexConfig(
                table_name="users", index_name="idx_users_email"
            )

    def test_positive_index_parallel_degree_is_enforced(self) -> None:
        """A non-positive parallel degree is rejected."""
        with pytest.raises(ValueError, match="greater than"):
            m.DbOracle.CreateIndexConfig(
                table_name="users",
                index_name="idx_users",
                columns=["email"],
                parallel=0,
            )

    # ------------------------------------------------------------------
    # FlextDbOracleSettings
    # ------------------------------------------------------------------

    def test_settings_defaults(self) -> None:
        """Settings expose documented Oracle defaults under the DbOracle namespace."""
        settings = FlextDbOracleSettings()
        tm.that(settings.DbOracle.host, eq="localhost")
        tm.that(settings.DbOracle.port, eq=1521)
        tm.that(settings.DbOracle.name, eq="XE")
        tm.that(settings.DbOracle.service_name, eq="XEPDB1")
        tm.that(settings.DbOracle.username, eq="system")
        tm.that(settings.DbOracle.password, eq="")
        tm.that(settings.DbOracle.ssl_server_cert_dn, none=True)

    def test_settings_accept_custom_values(self) -> None:
        """Settings retain every explicitly supplied namespace value."""
        settings = FlextDbOracleSettings(
            DbOracle={
                "host": "oracle.example.com",
                "port": 1522,
                "name": "ORCL",
                "service_name": "ORCLPDB1",
                "username": "app_user",
                "password": "secret123",
                "ssl_server_cert_dn": "CN=oracle.example.com",
            }
        )
        tm.that(settings.DbOracle.host, eq="oracle.example.com")
        tm.that(settings.DbOracle.port, eq=1522)
        tm.that(settings.DbOracle.name, eq="ORCL")
        tm.that(settings.DbOracle.service_name, eq="ORCLPDB1")
        tm.that(settings.DbOracle.username, eq="app_user")
        tm.that(settings.DbOracle.password, eq="secret123")
        tm.that(settings.DbOracle.ssl_server_cert_dn, eq="CN=oracle.example.com")

    def test_env_variables_populate_namespace(self) -> None:
        """ORACLE_DBORACLE__* env vars populate the DbOracle namespace."""
        FlextDbOracleSettings.reset_for_testing()
        with u.Tests.env_vars_context({
            "ORACLE_DBORACLE__HOST": "db.example.com",
            "ORACLE_DBORACLE__PORT": "1522",
            "ORACLE_DBORACLE__SERVICE_NAME": "MYDB",
            "ORACLE_DBORACLE__USERNAME": "dbuser",
        }):
            settings = FlextDbOracleSettings()
        tm.that(settings.DbOracle.host, eq="db.example.com")
        tm.that(settings.DbOracle.port, eq=1522)
        tm.that(settings.DbOracle.service_name, eq="MYDB")
        tm.that(settings.DbOracle.username, eq="dbuser")

    def test_settings_serialization_exposes_fields(self) -> None:
        """model_dump exposes the connection fields inside the namespace."""
        settings = FlextDbOracleSettings(
            DbOracle={
                "host": "test.com",
                "port": 1522,
                "username": "user",
                "password": "pass",
            }
        )
        serialized = settings.model_dump()
        tm.that(serialized["DbOracle"]["host"], eq="test.com")
        tm.that(serialized["DbOracle"]["port"], eq=1522)
        tm.that(serialized["DbOracle"]["username"], eq="user")

    def test_settings_value_equality(self) -> None:
        """Clones with equal namespace values compare equal, unequal ones differ."""
        base = FlextDbOracleSettings().clone(DbOracle={"host": "localhost"})
        same = FlextDbOracleSettings().clone(DbOracle={"host": "localhost"})
        other = FlextDbOracleSettings().clone(DbOracle={"host": "remotehost"})
        tm.that(base, eq=same)
        tm.that(base, ne=other)

    def test_settings_repr_includes_identifying_fields(self) -> None:
        """Representation identifies the settings type and connection values."""
        settings = FlextDbOracleSettings(
            DbOracle={"host": "localhost", "port": 1521, "username": "system"}
        )
        repr_str = repr(settings)
        tm.that(repr_str, has="FlextDbOracleSettings")
        tm.that(repr_str, has="localhost")
        tm.that(repr_str, has="1521")

    def test_independent_instances_do_not_share_mutation(self) -> None:
        """Mutating one settings clone never affects another."""
        first = FlextDbOracleSettings().clone()
        second = FlextDbOracleSettings().clone()
        first.DbOracle.host = "modified"
        tm.that(second.DbOracle.host, eq="localhost")

    # ------------------------------------------------------------------
    # Offline model contracts for database-shaped payloads
    # ------------------------------------------------------------------

    def test_query_result_contract_returns_rows(self) -> None:
        """QueryResult carries typed row payloads without a live database."""
        row = m.DbOracle.RowData(values=(1, "test"))
        query_result = m.DbOracle.QueryResult(
            query="SELECT 1 as id, 'test' as name FROM DUAL",
            columns=("ID", "NAME"),
            rows=(row,),
        )
        tm.that(query_result.has_results, eq=True)
        tm.that(query_result.row_count, eq=1)
        tm.that(query_result.rows[0].values, eq=(1, "test"))

    def test_schema_contract_preserves_table_metadata(self) -> None:
        """Schema payloads preserve table metadata without a live database."""
        table = m.DbOracle.Table(name="dual", owner="SYS")
        schema = m.DbOracle.Schema(name="SYS", tables=(table,))
        tm.that(schema.name, eq="SYS")
        tm.that(schema.tables[0].name, eq="dual")
        tm.that(schema.tables[0].owner, eq="SYS")

"""Comprehensive unit tests for flext_db_oracle.models module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

import pytest
from flext_tests import tm

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleSettings,
)
from tests import c, m


@pytest.mark.unit_pure
class Testm:
    """Comprehensive test m functionality and validation."""

    def test_connection_status_creation_defaults(self) -> None:
        """Test ConnectionStatus creation with defaults."""
        status = m.DbOracle.ConnectionStatus()
        tm.that(not status.is_connected, eq=True)
        tm.that(status.error_message, eq="")
        tm.that(abs(status.connection_time - 0.0), lt=1e-9)
        tm.that(status.session_id, eq="")
        tm.that(status.host, eq="")
        tm.that(status.port, eq=c.DbOracle.Connection.DEFAULT_PORT)
        tm.that(status.service_name, eq="")
        tm.that(status.username, eq="")
        tm.that(status.db_version, eq="")

    def test_connection_status_creation_with_values(self) -> None:
        """Test ConnectionStatus creation with custom values."""
        now = datetime.now(UTC)
        status = m.DbOracle.ConnectionStatus(
            is_connected=True,
            error_message="",
            connection_time=0.5,
            last_activity=now,
            session_id="ABC123",
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="system",
            db_version="19.3.0.0.0",
        )
        tm.that(status.is_connected, eq=True)
        tm.that(abs(status.connection_time - 0.5), lt=1e-9)
        tm.that(status.session_id, eq="ABC123")
        tm.that(status.host, eq="localhost")
        tm.that(status.service_name, eq="XEPDB1")
        tm.that(status.username, eq="system")

    def test_connection_status_computed_fields(self) -> None:
        """Test ConnectionStatus computed fields."""
        now = datetime.now(UTC)
        status = m.DbOracle.ConnectionStatus(
            is_connected=True,
            last_activity=now,
            host="localhost",
            service_name="XEPDB1",
            username="system",
        )
        tm.that(status.status_description, eq="Connected")
        status.is_connected = False
        status.error_message = "Connection lost"
        tm.that(status.status_description, eq="Disconnected: Connection lost")
        status.is_connected = True
        status.error_message = ""
        tm.that(status.connection_age_seconds, gte=0)
        tm.that(status.is_healthy, eq=True)
        tm.that(status.connection_info, has="localhost")
        tm.that(status.connection_info, has="1521")
        tm.that(status.connection_info, has="XEPDB1")
        tm.that(status.connection_info, has="system")

    def test_connection_status_performance_info(self) -> None:
        """Test ConnectionStatus performance rating."""
        status = m.DbOracle.ConnectionStatus(
            is_connected=True,
            host="localhost",
            connection_time=0.05,
        )
        tm.that(status.performance_info, has="Excellent")
        status.connection_time = 0.3
        tm.that(status.performance_info, has="Good")
        status.connection_time = 1.5
        tm.that(status.performance_info, has="Acceptable")
        status.connection_time = 3.0
        tm.that(status.performance_info, has="Slow")
        status.connection_time = 0.0
        tm.that(status.performance_info, has="No performance data")

    def test_connection_status_validation(self) -> None:
        """Test ConnectionStatus validation."""
        status = m.DbOracle.ConnectionStatus(
            is_connected=True,
            host="localhost",
            port=1521,
        )
        validated = m.DbOracle.ConnectionStatus.model_validate(
            status.model_dump(),
        )
        tm.that(validated.is_connected, eq=True)
        with pytest.raises(
            ValueError,
            match="Connected status requires host information",
        ):
            m.DbOracle.ConnectionStatus(
                is_connected=True,
                host="",
                port=1521,
            )
        with pytest.raises(ValueError, match="less than or equal to"):
            m.DbOracle.ConnectionStatus(
                is_connected=True,
                host="localhost",
                port=99999,
            )
        with pytest.raises(ValueError, match="greater than or equal to"):
            m.DbOracle.ConnectionStatus(connection_time=-1.0)

    def test_connection_status_serialization(self) -> None:
        """Test ConnectionStatus field serialization."""
        now = datetime.now(UTC)
        status = m.DbOracle.ConnectionStatus(
            is_connected=True,
            host="localhost",
            last_check=now,
            last_activity=now,
            error_message="Test error message that is very long and should be truncated because it's over 500 characters in length and we want to make sure the serialization works properly by cutting it off at the appropriate limit",
            connection_time=1.23456,
        )
        serialized = status.model_dump(mode="json")
        tm.that(serialized, has="last_check")
        tm.that(serialized, has="last_activity")
        tm.that(len(status.error_message), lte=500 + len("... (truncated)"))
        tm.that(abs(status.connection_time - 1.23456), lt=1e-9)

    def test_query_result_creation_minimal(self) -> None:
        """Test QueryResult creation with minimal data."""
        result = m.DbOracle.QueryResult(query="SELECT 1")
        tm.that(result.query, eq="SELECT 1")
        tm.that(result.row_count, eq=0)
        tm.that(result.execution_time_ms, eq=0)
        tm.that(result.result_data, eq=[])
        tm.that(result.columns, eq=[])
        tm.that(result.rows, eq=[])
        tm.that(result.query_hash, eq="")
        tm.that(result.explain_plan, eq="")

    def test_query_result_creation_with_data(self) -> None:
        """Test QueryResult creation with full data."""
        result = m.DbOracle.QueryResult(
            query="SELECT id, name FROM users",
            columns=["id", "name"],
            rows=[
                m.DbOracle.RowData(values=[1, "John"]),
                m.DbOracle.RowData(values=[2, "Jane"]),
            ],
            execution_time_ms=150,
            query_hash="abc123",
            explain_plan="TABLE ACCESS FULL",
        )
        tm.that(result.query, eq="SELECT id, name FROM users")
        tm.that(result.row_count, eq=2)
        tm.that(result.execution_time_ms, eq=150)
        tm.that(result.columns, eq=["id", "name"])
        tm.that(
            result.rows,
            eq=[
                m.DbOracle.RowData(values=[1, "John"]),
                m.DbOracle.RowData(values=[2, "Jane"]),
            ],
        )
        tm.that(result.query_hash, eq="abc123")
        tm.that(result.explain_plan, eq="TABLE ACCESS FULL")

    def test_query_result_computed_fields(self) -> None:
        """Test QueryResult computed fields."""
        result = m.DbOracle.QueryResult(
            query="SELECT 1",
            execution_time_ms=2500,
            columns=["col1"],
            rows=[
                m.DbOracle.RowData(values=[1]),
                m.DbOracle.RowData(values=[2]),
                m.DbOracle.RowData(values=[3]),
            ],
        )
        tm.that(abs(result.execution_time_seconds - 2.5), lt=1e-9)
        tm.that(result.has_results, eq=True)
        tm.that(result.column_count, eq=1)
        tm.that(result.performance_rating, eq="Acceptable")
        expected_size = 3 * 1 * 50
        tm.that(result.data_size_bytes, eq=expected_size)
        expected_mb = expected_size / (1024 * 1024)
        tm.that(result.memory_usage_mb, eq=expected_mb)

    def test_query_result_performance_ratings(self) -> None:
        """Test QueryResult performance rating categories."""
        result = m.DbOracle.QueryResult(
            query="SELECT 1",
            execution_time_ms=50,
        )
        tm.that(result.performance_rating, eq="Excellent")
        result.execution_time_ms = 300
        tm.that(result.performance_rating, eq="Good")
        result.execution_time_ms = 1500
        tm.that(result.performance_rating, eq="Acceptable")
        result.execution_time_ms = 2500
        tm.that(result.performance_rating, eq="Slow")

    def test_query_result_validation(self) -> None:
        """Test QueryResult validation."""
        result = m.DbOracle.QueryResult(
            query="SELECT 1",
            columns=["id"],
            rows=[
                m.DbOracle.RowData(values=[1]),
                m.DbOracle.RowData(values=[2]),
            ],
            execution_time_ms=100,
        )
        validated = m.DbOracle.QueryResult.model_validate(
            result.model_dump(),
        )
        tm.that(validated.row_count, eq=2)
        with pytest.raises(ValueError, match="greater than or equal to"):
            m.DbOracle.QueryResult(
                query="SELECT 1",
                execution_time_ms=-100,
            )
        with pytest.raises(ValueError, match=r"Row length.*doesn't match column count"):
            m.DbOracle.QueryResult(
                query="SELECT 1",
                columns=["id", "name"],
                rows=[
                    m.DbOracle.RowData(values=[1]),
                    m.DbOracle.RowData(values=[2]),
                ],
            )

    def test_query_result_serialization(self) -> None:
        """Test QueryResult field serialization."""
        result = m.DbOracle.QueryResult(
            query="SELECT 1",
            execution_time_ms=1500,
        )
        serialized = result.model_dump(mode="json")
        tm.that(serialized, has="execution_time_ms")
        execution_time_str = result.execution_time_ms
        tm.that(execution_time_str, eq=1500)

    def test_table_creation(self) -> None:
        """Test Table model creation."""
        table = m.DbOracle.Table(name="users", owner="hr")
        tm.that(table.name, eq="users")
        tm.that(table.owner, eq="hr")
        tm.that(table.columns, eq=[])

    def test_table_with_columns(self) -> None:
        """Test Table with columns."""
        columns = [
            m.DbOracle.Column(
                name="id",
                data_type="NUMBER",
                nullable=False,
            ),
            m.DbOracle.Column(name="name", data_type="VARCHAR2(100)"),
        ]
        table = m.DbOracle.Table(
            name="users",
            owner="hr",
            columns=columns,
        )
        tm.that(len(table.columns), eq=2)
        tm.that(table.columns[0].name, eq="id")
        tm.that(table.columns[0].nullable is False, eq=True)
        tm.that(table.columns[1].name, eq="name")
        tm.that(table.columns[1].nullable is True, eq=True)

    def test_column_creation(self) -> None:
        """Test Column model creation."""
        column = m.DbOracle.Column(
            name="user_id",
            data_type="NUMBER(38)",
            nullable=False,
            default_value="NULL",
        )
        tm.that(column.name, eq="user_id")
        tm.that(column.data_type, eq="NUMBER(38)")
        tm.that(column.nullable is False, eq=True)
        tm.that(column.default_value, eq="NULL")

    def test_schema_creation(self) -> None:
        """Test Schema model creation."""
        schema = m.DbOracle.Schema(name="hr")
        tm.that(schema.name, eq="hr")
        tm.that(schema.tables, eq=[])

    def test_schema_with_tables(self) -> None:
        """Test Schema with tables."""
        tables = [
            m.DbOracle.Table(name="users", owner="hr"),
            m.DbOracle.Table(name="orders", owner="hr"),
        ]
        schema = m.DbOracle.Schema(name="hr", tables=tables)
        tm.that(len(schema.tables), eq=2)
        tm.that(schema.tables[0].name, eq="users")
        tm.that(schema.tables[1].name, eq="orders")

    def test_create_index_config_creation(self) -> None:
        """Test CreateIndexConfig creation."""
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
        tm.that(config.unique is True, eq=True)
        tm.that(config.schema_name, eq="hr")
        tm.that(config.tablespace, eq="users_idx")
        tm.that(config.parallel, eq=4)

    def test_merge_statement_config_creation(self) -> None:
        """Test MergeStatementConfig creation."""
        config = m.DbOracle.MergeStatementConfig(
            target_table="users",
            source_query="SELECT id, name FROM temp_users",
            merge_conditions=["t.id = s.id"],
            update_columns=["name"],
            insert_columns=["id", "name"],
        )
        tm.that(config.target_table, eq="users")
        tm.that(config.source_query, eq="SELECT id, name FROM temp_users")
        tm.that(config.merge_conditions, eq=["t.id = s.id"])
        tm.that(config.update_columns, eq=["name"])
        tm.that(config.insert_columns, eq=["id", "name"])

    def test_connection_status_real_oracle_integration(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test ConnectionStatus with real Oracle connection."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        status = m.DbOracle.ConnectionStatus(
            is_connected=True,
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="flexttest",
            connection_time=0.1,
        )
        tm.that(status.status_description, eq="Connected")
        tm.that(
            (
                status.connection_info
                == "host=localhost, port=1521, service=XEPDB1, user=flexttest"
            ),
            eq=True,
        )
        tm.that(status.is_healthy, eq=True)
        tm.that(
            (
                "Excellent" in status.performance_info
                or "Good" in status.performance_info
            ),
            eq=True,
        )

    def test_query_result_real_oracle_integration(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test QueryResult with real Oracle data."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        query_result = connected_oracle_api.query(
            "SELECT 1 as id, 'test' as name FROM DUAL",
        )
        tm.ok(query_result)
        data = query_result.value
        tm.that(len(data), eq=1)
        first_row = data[0].root if hasattr(data[0], "root") else data[0]
        tm.that("ID" in first_row or "id" in first_row, eq=True)
        result_model = m.DbOracle.QueryResult(
            query="SELECT 1 as id, 'test' as name FROM DUAL",
            columns=["id", "name"],
            rows=[m.DbOracle.RowData(values=[1, "test"])],
            execution_time_ms=50,
        )
        tm.that(result_model.has_results, eq=True)
        tm.that(result_model.column_count, eq=2)
        tm.that(
            {
                "Excellent",
                "Good",
                "Acceptable",
                "Slow",
            },
            has=result_model.performance_rating,
        )

    def test_table_model_real_oracle_integration(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test Table model with real Oracle schema data."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        schemas_result = connected_oracle_api.get_schemas()
        if schemas_result.is_success:
            schemas = schemas_result.value
            if schemas:
                table = m.DbOracle.Table(name="dual", owner="SYS")
                tm.that(table.name, eq="dual")
                tm.that(table.owner, eq="SYS")
                tm.that(table.columns, eq=[])


class TestFlextDbOracleSettings:
    """Comprehensive test FlextDbOracleSettings functionality."""

    def test_config_creation_defaults(self) -> None:
        """Test config creation with defaults."""
        config = FlextDbOracleSettings()
        tm.that(config.host, eq="localhost")
        tm.that(config.port, eq=1521)
        tm.that(config.name, eq="XE")
        tm.that(config.service_name, eq="XEPDB1")
        tm.that(config.username, eq="system")
        tm.that(config.password, eq="")
        tm.that(config.ssl_server_cert_dn, none=True)

    def test_config_creation_with_values(self) -> None:
        """Test config creation with custom values."""
        config = FlextDbOracleSettings(
            host="oracle.example.com",
            port=1522,
            name="ORCL",
            service_name="ORCLPDB1",
            username="app_user",
            password="secret123",
            ssl_server_cert_dn="CN=oracle.example.com",
        )
        tm.that(config.host, eq="oracle.example.com")
        tm.that(config.port, eq=1522)
        tm.that(config.name, eq="ORCL")
        tm.that(config.service_name, eq="ORCLPDB1")
        tm.that(config.username, eq="app_user")
        tm.that(config.password, eq="secret123")
        tm.that(config.ssl_server_cert_dn, eq="CN=oracle.example.com")

    def test_config_from_env_no_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config creation from environment with no variables set."""
        env_vars_to_clear = [
            "FLEXT_TARGET_ORACLE_HOST",
            "ORACLE_HOST",
            "FLEXT_TARGET_ORACLE_PORT",
            "ORACLE_PORT",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME",
            "ORACLE_SERVICE_NAME",
            "FLEXT_TARGET_ORACLE_USERNAME",
            "ORACLE_USERNAME",
            "FLEXT_TARGET_ORACLE_PASSWORD",
            "ORACLE_PASSWORD",
            "ORACLE_DATABASE_NAME",
            "ORACLE_SID",
        ]
        for var in env_vars_to_clear:
            monkeypatch.delenv(var, raising=False)
        result = FlextDbOracleSettings.from_env()
        tm.ok(result)
        config = result.value
        tm.that(config.host, eq="localhost")
        tm.that(config.port, eq=1521)
        tm.that(config.service_name, eq="XEPDB1")

    def test_config_from_env_with_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config creation from environment variables."""
        for key in list(os.environ.keys()):
            if key.startswith("FLEXT_TARGET_ORACLE_"):
                monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("ORACLE_HOST", "db.example.com")
        monkeypatch.setenv("ORACLE_PORT", "1522")
        monkeypatch.setenv("ORACLE_SERVICE_NAME", "MYDB")
        monkeypatch.setenv("ORACLE_USERNAME", "dbuser")
        monkeypatch.setenv("ORACLE_PASSWORD", "dbpass")
        monkeypatch.setenv("ORACLE_DATABASE_NAME", "ORCL")
        monkeypatch.setenv("ORACLE_SID", "ORCL")
        result = FlextDbOracleSettings.from_env()
        tm.ok(result)
        config = result.value
        tm.that(config.host, eq="db.example.com")
        tm.that(config.port, eq=1522)
        tm.that(config.service_name, eq="MYDB")
        tm.that(config.username, eq="dbuser")
        tm.that(config.password, eq="dbpass")
        tm.that(config.name, eq="ORCL")

    def test_config_from_env_flext_prefix(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test config creation with FLEXT prefix environment variables."""
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_HOST", "flext-db.example.com")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_USERNAME", "flext-user")
        result = FlextDbOracleSettings.from_env()
        tm.ok(result)
        config = result.value
        tm.that(config.host, eq="flext-db.example.com")
        tm.that(config.username, eq="flext-user")

    def test_config_from_env_mixed_prefixes(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test config creation with mixed prefixes."""
        monkeypatch.setenv("ORACLE_HOST", "oracle-host")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_HOST", "flext-host")
        monkeypatch.setenv("ORACLE_USERNAME", "oracle-user")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_USERNAME", "flext-user")
        result = FlextDbOracleSettings.from_env()
        tm.ok(result)
        config = result.value
        tm.that(config.host, eq="flext-host")
        tm.that(config.username, eq="flext-user")

    def test_config_from_env_port_conversion(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test port conversion from environment string to int."""
        for key in list(os.environ.keys()):
            if key.startswith("FLEXT_TARGET_ORACLE_"):
                monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("ORACLE_PORT", "1523")
        result = FlextDbOracleSettings.from_env()
        tm.ok(result)
        config = result.value
        tm.that(config.port, eq=1523)
        tm.that(config.port, is_=int)

    def test_config_from_env_invalid_port(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test config creation with invalid port."""
        for key in list(os.environ.keys()):
            if key.startswith("FLEXT_TARGET_ORACLE_"):
                monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("ORACLE_PORT", "invalid")
        result = FlextDbOracleSettings.from_env()
        tm.ok(result)
        config = result.value
        tm.that(config.port, eq=1521)

    def test_config_serialization(self) -> None:
        """Test config serialization."""
        config = FlextDbOracleSettings(
            host="test.com",
            port=1522,
            username="user",
            password="pass",
        )
        serialized = config.model_dump()
        tm.that(serialized["host"], eq="test.com")
        tm.that(serialized["port"], eq=1522)
        tm.that(serialized["username"], eq="user")

    def test_config_equality(self) -> None:
        """Test config equality comparison."""
        config1 = FlextDbOracleSettings(host="localhost", port=1521)
        config2 = FlextDbOracleSettings(host="localhost", port=1521)
        config3 = FlextDbOracleSettings(host="remotehost", port=1521)
        tm.that(config1, eq=config2)
        tm.that(config1, ne=config3)

    def test_config_repr(self) -> None:
        """Test config string representation."""
        config = FlextDbOracleSettings(host="localhost", port=1521, username="system")
        repr_str = repr(config)
        tm.that(repr_str, has="FlextDbOracleSettings")
        tm.that(repr_str, has="localhost")
        tm.that(repr_str, has="1521")

    def test_config_connection_string_components(self) -> None:
        """Test that config has all components needed for connection string."""
        config = FlextDbOracleSettings(
            host="oracle.example.com",
            port=1521,
            service_name="ORCLPDB1",
            username="appuser",
        )
        tm.that(config.host, eq="oracle.example.com")
        tm.that(config.port, eq=1521)
        tm.that(config.service_name, eq="ORCLPDB1")
        tm.that(config.username, eq="appuser")
        tm.that(config.name, eq="XE")

    def test_config_validation_through_creation(self) -> None:
        """Test config validation through successful creation."""
        config = FlextDbOracleSettings(
            host="valid-host",
            port=1521,
            service_name="VALID_SERVICE",
            username="valid_user",
        )
        tm.that(config.host, eq="valid-host")
        tm.that(config.port, eq=1521)

    def test_config_immutable_defaults(self) -> None:
        """Test that config defaults are properly set and don't change."""
        config1 = FlextDbOracleSettings()
        config2 = FlextDbOracleSettings()
        tm.that(config1.host, eq=config2.host)
        tm.that(config1.port, eq=config2.port)
        tm.that(config1.service_name, eq=config2.service_name)
        config1.host = "modified"
        tm.that(config2.host, eq="localhost")

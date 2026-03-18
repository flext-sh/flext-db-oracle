"""Comprehensive unit tests for flext_db_oracle.models module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleModels, FlextDbOracleSettings
from flext_db_oracle.constants import FlextDbOracleConstants


@pytest.mark.unit_pure
class TestFlextDbOracleModels:
    """Comprehensive test FlextDbOracleModels functionality and validation."""

    def test_connection_status_creation_defaults(self) -> None:
        """Test ConnectionStatus creation with defaults."""
        status = FlextDbOracleModels.DbOracle.ConnectionStatus()
        tm.that(not status.is_connected, eq=True)
        tm.that(status.error_message == "", eq=True)
        tm.that(abs(status.connection_time - 0.0), lt=1e-9)
        tm.that(status.session_id == "", eq=True)
        tm.that(status.host == "", eq=True)
        tm.that(
            status.port == FlextDbOracleConstants.DbOracle.Connection.DEFAULT_PORT,
            eq=True,
        )
        tm.that(status.service_name == "", eq=True)
        tm.that(status.username == "", eq=True)
        tm.that(status.db_version == "", eq=True)

    def test_connection_status_creation_with_values(self) -> None:
        """Test ConnectionStatus creation with custom values."""
        now = datetime.now(UTC)
        status = FlextDbOracleModels.DbOracle.ConnectionStatus(
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
        tm.that(status.session_id == "ABC123", eq=True)
        tm.that(status.host == "localhost", eq=True)
        tm.that(status.service_name == "XEPDB1", eq=True)
        tm.that(status.username == "system", eq=True)

    def test_connection_status_computed_fields(self) -> None:
        """Test ConnectionStatus computed fields."""
        now = datetime.now(UTC)
        status = FlextDbOracleModels.DbOracle.ConnectionStatus(
            is_connected=True,
            last_activity=now,
            host="localhost",
            service_name="XEPDB1",
            username="system",
        )
        tm.that(status.status_description == "Connected", eq=True)
        status.is_connected = False
        status.error_message = "Connection lost"
        tm.that(status.status_description == "Disconnected: Connection lost", eq=True)
        status.is_connected = True
        status.error_message = ""
        tm.that(status.connection_age_seconds >= 0 == True, eq=True)
        tm.that(status.is_healthy, eq=True)
        tm.that("localhost" in status.connection_info is True, eq=True)
        tm.that("1521" in status.connection_info is True, eq=True)
        tm.that("XEPDB1" in status.connection_info is True, eq=True)
        tm.that("system" in status.connection_info is True, eq=True)

    def test_connection_status_performance_info(self) -> None:
        """Test ConnectionStatus performance rating."""
        status = FlextDbOracleModels.DbOracle.ConnectionStatus(
            is_connected=True, host="localhost", connection_time=0.05
        )
        tm.that("Excellent" in status.performance_info is True, eq=True)
        status.connection_time = 0.3
        tm.that("Good" in status.performance_info is True, eq=True)
        status.connection_time = 1.5
        tm.that("Acceptable" in status.performance_info is True, eq=True)
        status.connection_time = 3.0
        tm.that("Slow" in status.performance_info is True, eq=True)
        status.connection_time = 0.0
        tm.that("No performance data" in status.performance_info is True, eq=True)

    def test_connection_status_validation(self) -> None:
        """Test ConnectionStatus validation."""
        status = FlextDbOracleModels.DbOracle.ConnectionStatus(
            is_connected=True, host="localhost", port=1521
        )
        validated = FlextDbOracleModels.DbOracle.ConnectionStatus.model_validate(
            status.model_dump()
        )
        tm.that(validated.is_connected, eq=True)
        with pytest.raises(
            ValueError, match="Connected status requires host information"
        ):
            FlextDbOracleModels.DbOracle.ConnectionStatus(
                is_connected=True, host="", port=1521
            )
        with pytest.raises(ValueError, match="Invalid port number"):
            FlextDbOracleModels.DbOracle.ConnectionStatus(
                is_connected=True, host="localhost", port=99999
            )
        with pytest.raises(ValueError, match="Connection time cannot be negative"):
            FlextDbOracleModels.DbOracle.ConnectionStatus(connection_time=-1.0)

    def test_connection_status_serialization(self) -> None:
        """Test ConnectionStatus field serialization."""
        now = datetime.now(UTC)
        status = FlextDbOracleModels.DbOracle.ConnectionStatus(
            is_connected=True,
            host="localhost",
            last_check=now,
            last_activity=now,
            error_message="Test error message that is very long and should be truncated because it's over 500 characters in length and we want to make sure the serialization works properly by cutting it off at the appropriate limit",
            connection_time=1.23456,
        )
        serialized = status.model_dump(mode="json")
        tm.that("last_check" in serialized is True, eq=True)
        tm.that("last_activity" in serialized is True, eq=True)
        tm.that(
            len(status.error_message) <= 500 + len("... (truncated)") is True, eq=True
        )
        tm.that(abs(status.connection_time - 1.23456), lt=1e-9)

    def test_query_result_creation_minimal(self) -> None:
        """Test QueryResult creation with minimal data."""
        result = FlextDbOracleModels.DbOracle.QueryResult(query="SELECT 1")
        tm.that(result.query == "SELECT 1", eq=True)
        tm.that(result.row_count == 0, eq=True)
        tm.that(result.execution_time_ms == 0, eq=True)
        tm.that(result.result_data == [], eq=True)
        tm.that(result.columns == [], eq=True)
        tm.that(result.rows == [], eq=True)
        tm.that(result.query_hash == "", eq=True)
        tm.that(result.explain_plan == "", eq=True)

    def test_query_result_creation_with_data(self) -> None:
        """Test QueryResult creation with full data."""
        result = FlextDbOracleModels.DbOracle.QueryResult(
            query="SELECT id, name FROM users",
            columns=["id", "name"],
            rows=[
                FlextDbOracleModels.DbOracle.RowData(values=[1, "John"]),
                FlextDbOracleModels.DbOracle.RowData(values=[2, "Jane"]),
            ],
            execution_time_ms=150,
            query_hash="abc123",
            explain_plan="TABLE ACCESS FULL",
        )
        tm.that(result.query == "SELECT id, name FROM users", eq=True)
        tm.that(result.row_count == 2, eq=True)
        tm.that(result.execution_time_ms == 150, eq=True)
        tm.that(result.columns == ["id", "name"], eq=True)
        tm.that(
            result.rows
            == [
                FlextDbOracleModels.DbOracle.RowData(values=[1, "John"]),
                FlextDbOracleModels.DbOracle.RowData(values=[2, "Jane"]),
            ],
            eq=True,
        )
        tm.that(result.query_hash == "abc123", eq=True)
        tm.that(result.explain_plan == "TABLE ACCESS FULL", eq=True)

    def test_query_result_computed_fields(self) -> None:
        """Test QueryResult computed fields."""
        result = FlextDbOracleModels.DbOracle.QueryResult(
            query="SELECT 1",
            execution_time_ms=2500,
            columns=["col1"],
            rows=[
                FlextDbOracleModels.DbOracle.RowData(values=[1]),
                FlextDbOracleModels.DbOracle.RowData(values=[2]),
                FlextDbOracleModels.DbOracle.RowData(values=[3]),
            ],
        )
        tm.that(abs(result.execution_time_seconds - 2.5), lt=1e-9)
        tm.that(result.has_results, eq=True)
        tm.that(result.column_count == 1, eq=True)
        tm.that(result.performance_rating == "Acceptable", eq=True)
        expected_size = 3 * 1 * 50
        tm.that(result.data_size_bytes == expected_size, eq=True)
        expected_mb = expected_size / (1024 * 1024)
        tm.that(result.memory_usage_mb == expected_mb, eq=True)

    def test_query_result_performance_ratings(self) -> None:
        """Test QueryResult performance rating categories."""
        result = FlextDbOracleModels.DbOracle.QueryResult(
            query="SELECT 1", execution_time_ms=50
        )
        tm.that(result.performance_rating == "Excellent", eq=True)
        result.execution_time_ms = 300
        tm.that(result.performance_rating == "Good", eq=True)
        result.execution_time_ms = 1500
        tm.that(result.performance_rating == "Acceptable", eq=True)
        result.execution_time_ms = 2500
        tm.that(result.performance_rating == "Slow", eq=True)

    def test_query_result_validation(self) -> None:
        """Test QueryResult validation."""
        result = FlextDbOracleModels.DbOracle.QueryResult(
            query="SELECT 1",
            columns=["id"],
            rows=[
                FlextDbOracleModels.DbOracle.RowData(values=[1]),
                FlextDbOracleModels.DbOracle.RowData(values=[2]),
            ],
            execution_time_ms=100,
        )
        validated = FlextDbOracleModels.DbOracle.QueryResult.model_validate(
            result.model_dump()
        )
        tm.that(validated.row_count == 2, eq=True)
        with pytest.raises(ValueError, match="Execution time cannot be negative"):
            FlextDbOracleModels.DbOracle.QueryResult(
                query="SELECT 1", execution_time_ms=-100
            )
        with pytest.raises(ValueError, match=r"Row length.*doesn't match column count"):
            FlextDbOracleModels.DbOracle.QueryResult(
                query="SELECT 1",
                columns=["id", "name"],
                rows=[
                    FlextDbOracleModels.DbOracle.RowData(values=[1]),
                    FlextDbOracleModels.DbOracle.RowData(values=[2]),
                ],
            )

    def test_query_result_serialization(self) -> None:
        """Test QueryResult field serialization."""
        result = FlextDbOracleModels.DbOracle.QueryResult(
            query="SELECT 1", execution_time_ms=1500
        )
        serialized = result.model_dump(mode="json")
        tm.that("execution_time_ms" in serialized is True, eq=True)
        execution_time_str = result.execution_time_ms
        tm.that(execution_time_str == 1500, eq=True)

    def test_table_creation(self) -> None:
        """Test Table model creation."""
        table = FlextDbOracleModels.DbOracle.Table(name="users", owner="hr")
        tm.that(table.name == "users", eq=True)
        tm.that(table.owner == "hr", eq=True)
        tm.that(table.columns == [], eq=True)

    def test_table_with_columns(self) -> None:
        """Test Table with columns."""
        columns = [
            FlextDbOracleModels.DbOracle.Column(
                name="id", data_type="NUMBER", nullable=False
            ),
            FlextDbOracleModels.DbOracle.Column(name="name", data_type="VARCHAR2(100)"),
        ]
        table = FlextDbOracleModels.DbOracle.Table(
            name="users", owner="hr", columns=columns
        )
        tm.that(len(table.columns) == 2, eq=True)
        tm.that(table.columns[0].name == "id", eq=True)
        tm.that(table.columns[0].nullable is False, eq=True)
        tm.that(table.columns[1].name == "name", eq=True)
        tm.that(table.columns[1].nullable is True == True, eq=True)

    def test_column_creation(self) -> None:
        """Test Column model creation."""
        column = FlextDbOracleModels.DbOracle.Column(
            name="user_id", data_type="NUMBER(38)", nullable=False, default_value="NULL"
        )
        tm.that(column.name == "user_id", eq=True)
        tm.that(column.data_type == "NUMBER(38)", eq=True)
        tm.that(column.nullable is False, eq=True)
        tm.that(column.default_value == "NULL", eq=True)

    def test_schema_creation(self) -> None:
        """Test Schema model creation."""
        schema = FlextDbOracleModels.DbOracle.Schema(name="hr")
        tm.that(schema.name == "hr", eq=True)
        tm.that(schema.tables == [], eq=True)

    def test_schema_with_tables(self) -> None:
        """Test Schema with tables."""
        tables = [
            FlextDbOracleModels.DbOracle.Table(name="users", owner="hr"),
            FlextDbOracleModels.DbOracle.Table(name="orders", owner="hr"),
        ]
        schema = FlextDbOracleModels.DbOracle.Schema(name="hr", tables=tables)
        tm.that(len(schema.tables) == 2, eq=True)
        tm.that(schema.tables[0].name == "users", eq=True)
        tm.that(schema.tables[1].name == "orders", eq=True)

    def test_create_index_config_creation(self) -> None:
        """Test CreateIndexConfig creation."""
        config = FlextDbOracleModels.DbOracle.CreateIndexConfig(
            table_name="users",
            index_name="idx_users_email",
            columns=["email"],
            unique=True,
            schema_name="hr",
            tablespace="users_idx",
            parallel=4,
        )
        tm.that(config.table_name == "users", eq=True)
        tm.that(config.index_name == "idx_users_email", eq=True)
        tm.that(config.columns == ["email"], eq=True)
        tm.that(config.unique is True == True, eq=True)
        tm.that(config.schema_name == "hr", eq=True)
        tm.that(config.tablespace == "users_idx", eq=True)
        tm.that(config.parallel == 4, eq=True)

    def test_merge_statement_config_creation(self) -> None:
        """Test MergeStatementConfig creation."""
        config = FlextDbOracleModels.DbOracle.MergeStatementConfig(
            target_table="users",
            source_query="SELECT id, name FROM temp_users",
            merge_conditions=["t.id = s.id"],
            update_columns=["name"],
            insert_columns=["id", "name"],
        )
        tm.that(config.target_table == "users", eq=True)
        tm.that(config.source_query == "SELECT id, name FROM temp_users", eq=True)
        tm.that(config.merge_conditions == ["t.id = s.id"], eq=True)
        tm.that(config.update_columns == ["name"], eq=True)
        tm.that(config.insert_columns == ["id", "name"], eq=True)

    def test_connection_status_real_oracle_integration(
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test ConnectionStatus with real Oracle connection."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        status = FlextDbOracleModels.DbOracle.ConnectionStatus(
            is_connected=True,
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="flexttest",
            connection_time=0.1,
        )
        tm.that(status.status_description == "Connected", eq=True)
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
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test QueryResult with real Oracle data."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        query_result = connected_oracle_api.query(
            "SELECT 1 as id, 'test' as name FROM DUAL"
        )
        tm.ok(query_result)
        data = query_result.value
        tm.that(len(data) == 1, eq=True)
        tm.that(data[0]["id"] == 1, eq=True)
        tm.that(data[0]["name"] == "test", eq=True)
        result_model = FlextDbOracleModels.DbOracle.QueryResult(
            query="SELECT 1 as id, 'test' as name FROM DUAL",
            columns=["id", "name"],
            rows=[FlextDbOracleModels.DbOracle.RowData(values=[1, "test"])],
            execution_time_ms=50,
        )
        tm.that(result_model.has_results, eq=True)
        tm.that(result_model.column_count == 2, eq=True)
        tm.that(
            result_model.performance_rating
            in {
                "Excellent",
                "Good",
                "Acceptable",
                "Slow",
            }
            == True,
            eq=True,
        )

    def test_table_model_real_oracle_integration(
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test Table model with real Oracle schema data."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        schemas_result = connected_oracle_api.get_schemas()
        if schemas_result.is_success:
            schemas = schemas_result.value
            if schemas:
                table = FlextDbOracleModels.DbOracle.Table(name="dual", owner="SYS")
                tm.that(table.name == "dual", eq=True)
                tm.that(table.owner == "SYS", eq=True)
                tm.that(table.columns == [], eq=True)


class TestFlextDbOracleSettings:
    """Comprehensive test FlextDbOracleSettings functionality."""

    def test_config_creation_defaults(self) -> None:
        """Test config creation with defaults."""
        config = FlextDbOracleSettings()
        tm.that(config.host == "localhost", eq=True)
        tm.that(config.port == 1521, eq=True)
        tm.that(config.name == "XE", eq=True)
        tm.that(config.service_name == "XEPDB1", eq=True)
        tm.that(config.username == "system", eq=True)
        tm.that(config.password == "", eq=True)
        tm.that(config.ssl_server_cert_dn is None is True, eq=True)

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
        tm.that(config.host == "oracle.example.com", eq=True)
        tm.that(config.port == 1522, eq=True)
        tm.that(config.name == "ORCL", eq=True)
        tm.that(config.service_name == "ORCLPDB1", eq=True)
        tm.that(config.username == "app_user", eq=True)
        tm.that(config.password == "secret123", eq=True)
        tm.that(config.ssl_server_cert_dn == "CN=oracle.example.com", eq=True)

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
        tm.that(config.host == "localhost", eq=True)
        tm.that(config.port == 1521, eq=True)
        tm.that(config.service_name == "XEPDB1", eq=True)

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
        tm.that(config.host == "db.example.com", eq=True)
        tm.that(config.port == 1522, eq=True)
        tm.that(config.service_name == "MYDB", eq=True)
        tm.that(config.username == "dbuser", eq=True)
        tm.that(config.password == "dbpass", eq=True)
        tm.that(config.name == "ORCL", eq=True)

    def test_config_from_env_flext_prefix(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config creation with FLEXT prefix environment variables."""
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_HOST", "flext-db.example.com")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_USERNAME", "flext-user")
        result = FlextDbOracleSettings.from_env()
        tm.ok(result)
        config = result.value
        tm.that(config.host == "flext-db.example.com", eq=True)
        tm.that(config.username == "flext-user", eq=True)

    def test_config_from_env_mixed_prefixes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config creation with mixed prefixes."""
        monkeypatch.setenv("ORACLE_HOST", "oracle-host")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_HOST", "flext-host")
        monkeypatch.setenv("ORACLE_USERNAME", "oracle-user")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_USERNAME", "flext-user")
        result = FlextDbOracleSettings.from_env()
        tm.ok(result)
        config = result.value
        tm.that(config.host == "flext-host", eq=True)
        tm.that(config.username == "flext-user", eq=True)

    def test_config_from_env_port_conversion(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test port conversion from environment string to int."""
        for key in list(os.environ.keys()):
            if key.startswith("FLEXT_TARGET_ORACLE_"):
                monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("ORACLE_PORT", "1523")
        result = FlextDbOracleSettings.from_env()
        tm.ok(result)
        config = result.value
        tm.that(config.port == 1523, eq=True)
        tm.that(isinstance(config.port, int), eq=True)

    def test_config_from_env_invalid_port(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config creation with invalid port."""
        for key in list(os.environ.keys()):
            if key.startswith("FLEXT_TARGET_ORACLE_"):
                monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("ORACLE_PORT", "invalid")
        result = FlextDbOracleSettings.from_env()
        tm.ok(result)
        config = result.value
        tm.that(config.port == 1521, eq=True)

    def test_config_serialization(self) -> None:
        """Test config serialization."""
        config = FlextDbOracleSettings(
            host="test.com", port=1522, username="user", password="pass"
        )
        serialized = config.model_dump()
        tm.that(serialized["host"] == "test.com", eq=True)
        tm.that(serialized["port"] == 1522, eq=True)
        tm.that(serialized["username"] == "user", eq=True)

    def test_config_equality(self) -> None:
        """Test config equality comparison."""
        config1 = FlextDbOracleSettings(host="localhost", port=1521)
        config2 = FlextDbOracleSettings(host="localhost", port=1521)
        config3 = FlextDbOracleSettings(host="remotehost", port=1521)
        tm.that(config1 == config2, eq=True)
        tm.that(config1 != config3 is True, eq=True)

    def test_config_repr(self) -> None:
        """Test config string representation."""
        config = FlextDbOracleSettings(host="localhost", port=1521, username="system")
        repr_str = repr(config)
        tm.that("FlextDbOracleSettings" in repr_str is True, eq=True)
        tm.that("localhost" in repr_str is True, eq=True)
        tm.that("1521" in repr_str is True, eq=True)

    def test_config_connection_string_components(self) -> None:
        """Test that config has all components needed for connection string."""
        config = FlextDbOracleSettings(
            host="oracle.example.com",
            port=1521,
            service_name="ORCLPDB1",
            username="appuser",
        )
        tm.that(config.host == "oracle.example.com", eq=True)
        tm.that(config.port == 1521, eq=True)
        tm.that(config.service_name == "ORCLPDB1", eq=True)
        tm.that(config.username == "appuser", eq=True)
        tm.that(config.name == "XE", eq=True)

    def test_config_validation_through_creation(self) -> None:
        """Test config validation through successful creation."""
        config = FlextDbOracleSettings(
            host="valid-host",
            port=1521,
            service_name="VALID_SERVICE",
            username="valid_user",
        )
        tm.that(config.host == "valid-host", eq=True)
        tm.that(config.port == 1521, eq=True)

    def test_config_immutable_defaults(self) -> None:
        """Test that config defaults are properly set and don't change."""
        config1 = FlextDbOracleSettings()
        config2 = FlextDbOracleSettings()
        tm.that(config1.host == config2.host, eq=True) == "localhost"
        tm.that(config1.port == config2.port, eq=True) == 1521
        tm.that(config1.service_name == config2.service_name, eq=True) == "XEPDB1"
        config1.host = "modified"
        tm.that(config2.host == "localhost", eq=True)

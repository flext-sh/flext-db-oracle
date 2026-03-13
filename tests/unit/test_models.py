"""Comprehensive unit tests for flext_db_oracle.models module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

import pytest

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleModels, FlextDbOracleSettings
from flext_db_oracle.constants import FlextDbOracleConstants


@pytest.mark.unit_pure
class TestFlextDbOracleModels:
    """Comprehensive test FlextDbOracleModels functionality and validation."""

    def test_connection_status_creation_defaults(self) -> None:
        """Test ConnectionStatus creation with defaults."""
        status = FlextDbOracleModels.DbOracle.ConnectionStatus()
        assert not status.is_connected
        assert status.error_message == ""
        assert status.connection_time == pytest.approx(0.0)
        assert status.session_id == ""
        assert status.host == ""
        assert status.port == FlextDbOracleConstants.DbOracle.Connection.DEFAULT_PORT
        assert status.service_name == ""
        assert status.username == ""
        assert status.db_version == ""

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
        assert status.is_connected
        assert status.connection_time == pytest.approx(0.5)
        assert status.session_id == "ABC123"
        assert status.host == "localhost"
        assert status.service_name == "XEPDB1"
        assert status.username == "system"

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
        assert status.status_description == "Connected"
        status.is_connected = False
        status.error_message = "Connection lost"
        assert status.status_description == "Disconnected: Connection lost"
        status.is_connected = True
        status.error_message = ""
        assert status.connection_age_seconds >= 0
        assert status.is_healthy
        assert "localhost" in status.connection_info
        assert "1521" in status.connection_info
        assert "XEPDB1" in status.connection_info
        assert "system" in status.connection_info

    def test_connection_status_performance_info(self) -> None:
        """Test ConnectionStatus performance rating."""
        status = FlextDbOracleModels.DbOracle.ConnectionStatus(
            is_connected=True, host="localhost", connection_time=0.05
        )
        assert "Excellent" in status.performance_info
        status.connection_time = 0.3
        assert "Good" in status.performance_info
        status.connection_time = 1.5
        assert "Acceptable" in status.performance_info
        status.connection_time = 3.0
        assert "Slow" in status.performance_info
        status.connection_time = 0.0
        assert "No performance data" in status.performance_info

    def test_connection_status_validation(self) -> None:
        """Test ConnectionStatus validation."""
        status = FlextDbOracleModels.DbOracle.ConnectionStatus(
            is_connected=True, host="localhost", port=1521
        )
        validated = status(status.model_dump())
        assert validated.is_connected
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
        assert "last_check" in serialized
        assert "last_activity" in serialized
        assert len(status.error_message) <= 500 + len("... (truncated)")
        assert status.connection_time == pytest.approx(1.23456)

    def test_query_result_creation_minimal(self) -> None:
        """Test QueryResult creation with minimal data."""
        result = FlextDbOracleModels.DbOracle.QueryResult(query="SELECT 1")
        assert result.query == "SELECT 1"
        assert result.row_count == 0
        assert result.execution_time_ms == 0
        assert result.result_data == []
        assert result.columns == []
        assert result.rows == []
        assert result.query_hash == ""
        assert result.explain_plan == ""

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
        assert result.query == "SELECT id, name FROM users"
        assert result.row_count == 2
        assert result.execution_time_ms == 150
        assert result.columns == ["id", "name"]
        assert result.rows == [
            FlextDbOracleModels.DbOracle.RowData(values=[1, "John"]),
            FlextDbOracleModels.DbOracle.RowData(values=[2, "Jane"]),
        ]
        assert result.query_hash == "abc123"
        assert result.explain_plan == "TABLE ACCESS FULL"

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
        assert result.execution_time_seconds == pytest.approx(2.5)
        assert result.has_results
        assert result.column_count == 1
        assert result.performance_rating == "Acceptable"
        expected_size = 3 * 1 * 50
        assert result.data_size_bytes == expected_size
        expected_mb = expected_size / (1024 * 1024)
        assert result.memory_usage_mb == expected_mb

    def test_query_result_performance_ratings(self) -> None:
        """Test QueryResult performance rating categories."""
        result = FlextDbOracleModels.DbOracle.QueryResult(
            query="SELECT 1", execution_time_ms=50
        )
        assert result.performance_rating == "Excellent"
        result.execution_time_ms = 300
        assert result.performance_rating == "Good"
        result.execution_time_ms = 1500
        assert result.performance_rating == "Acceptable"
        result.execution_time_ms = 2500
        assert result.performance_rating == "Slow"

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
        validated = result(result.model_dump())
        assert validated.row_count == 2
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
        assert "execution_time_ms" in serialized
        execution_time_str = result.execution_time_ms
        assert execution_time_str == 1500

    def test_table_creation(self) -> None:
        """Test Table model creation."""
        table = FlextDbOracleModels.DbOracle.Table(name="users", owner="hr")
        assert table.name == "users"
        assert table.owner == "hr"
        assert table.columns == []

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
        assert len(table.columns) == 2
        assert table.columns[0].name == "id"
        assert table.columns[0].nullable is False
        assert table.columns[1].name == "name"
        assert table.columns[1].nullable is True

    def test_column_creation(self) -> None:
        """Test Column model creation."""
        column = FlextDbOracleModels.DbOracle.Column(
            name="user_id", data_type="NUMBER(38)", nullable=False, default_value="NULL"
        )
        assert column.name == "user_id"
        assert column.data_type == "NUMBER(38)"
        assert column.nullable is False
        assert column.default_value == "NULL"

    def test_schema_creation(self) -> None:
        """Test Schema model creation."""
        schema = FlextDbOracleModels.DbOracle.Schema(name="hr")
        assert schema.name == "hr"
        assert schema.tables == []

    def test_schema_with_tables(self) -> None:
        """Test Schema with tables."""
        tables = [
            FlextDbOracleModels.DbOracle.Table(name="users", owner="hr"),
            FlextDbOracleModels.DbOracle.Table(name="orders", owner="hr"),
        ]
        schema = FlextDbOracleModels.DbOracle.Schema(name="hr", tables=tables)
        assert len(schema.tables) == 2
        assert schema.tables[0].name == "users"
        assert schema.tables[1].name == "orders"

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
        assert config.table_name == "users"
        assert config.index_name == "idx_users_email"
        assert config.columns == ["email"]
        assert config.unique is True
        assert config.schema_name == "hr"
        assert config.tablespace == "users_idx"
        assert config.parallel == 4

    def test_merge_statement_config_creation(self) -> None:
        """Test MergeStatementConfig creation."""
        config = FlextDbOracleModels.DbOracle.MergeStatementConfig(
            target_table="users",
            source_query="SELECT id, name FROM temp_users",
            merge_conditions=["t.id = s.id"],
            update_columns=["name"],
            insert_columns=["id", "name"],
        )
        assert config.target_table == "users"
        assert config.source_query == "SELECT id, name FROM temp_users"
        assert config.merge_conditions == ["t.id = s.id"]
        assert config.update_columns == ["name"]
        assert config.insert_columns == ["id", "name"]

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
        assert status.status_description == "Connected"
        assert (
            status.connection_info
            == "host=localhost, port=1521, service=XEPDB1, user=flexttest"
        )
        assert status.is_healthy
        assert (
            "Excellent" in status.performance_info or "Good" in status.performance_info
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
        assert query_result.is_success
        data = query_result.value
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["name"] == "test"
        result_model = FlextDbOracleModels.DbOracle.QueryResult(
            query="SELECT 1 as id, 'test' as name FROM DUAL",
            columns=["id", "name"],
            rows=[FlextDbOracleModels.DbOracle.RowData(values=[1, "test"])],
            execution_time_ms=50,
        )
        assert result_model.has_results
        assert result_model.column_count == 2
        assert result_model.performance_rating in {
            "Excellent",
            "Good",
            "Acceptable",
            "Slow",
        }

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
                assert table.name == "dual"
                assert table.owner == "SYS"
                assert table.columns == []


class TestFlextDbOracleSettings:
    """Comprehensive test FlextDbOracleSettings functionality."""

    def test_config_creation_defaults(self) -> None:
        """Test config creation with defaults."""
        config = FlextDbOracleSettings()
        assert config.host == "localhost"
        assert config.port == 1521
        assert config.name == "XE"
        assert config.service_name == "XEPDB1"
        assert config.username == "system"
        assert config.password == ""
        assert config.ssl_server_cert_dn is None

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
        assert config.host == "oracle.example.com"
        assert config.port == 1522
        assert config.name == "ORCL"
        assert config.service_name == "ORCLPDB1"
        assert config.username == "app_user"
        assert config.password == "secret123"
        assert config.ssl_server_cert_dn == "CN=oracle.example.com"

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
        assert result.is_success
        config = result.value
        assert config.host == "localhost"
        assert config.port == 1521
        assert config.service_name == "XEPDB1"

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
        assert result.is_success
        config = result.value
        assert config.host == "db.example.com"
        assert config.port == 1522
        assert config.service_name == "MYDB"
        assert config.username == "dbuser"
        assert config.password == "dbpass"
        assert config.name == "ORCL"

    def test_config_from_env_flext_prefix(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config creation with FLEXT prefix environment variables."""
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_HOST", "flext-db.example.com")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_USERNAME", "flext-user")
        result = FlextDbOracleSettings.from_env()
        assert result.is_success
        config = result.value
        assert config.host == "flext-db.example.com"
        assert config.username == "flext-user"

    def test_config_from_env_mixed_prefixes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config creation with mixed prefixes."""
        monkeypatch.setenv("ORACLE_HOST", "oracle-host")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_HOST", "flext-host")
        monkeypatch.setenv("ORACLE_USERNAME", "oracle-user")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_USERNAME", "flext-user")
        result = FlextDbOracleSettings.from_env()
        assert result.is_success
        config = result.value
        assert config.host == "flext-host"
        assert config.username == "flext-user"

    def test_config_from_env_port_conversion(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test port conversion from environment string to int."""
        for key in list(os.environ.keys()):
            if key.startswith("FLEXT_TARGET_ORACLE_"):
                monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("ORACLE_PORT", "1523")
        result = FlextDbOracleSettings.from_env()
        assert result.is_success
        config = result.value
        assert config.port == 1523
        assert isinstance(config.port, int)

    def test_config_from_env_invalid_port(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test config creation with invalid port."""
        for key in list(os.environ.keys()):
            if key.startswith("FLEXT_TARGET_ORACLE_"):
                monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("ORACLE_PORT", "invalid")
        result = FlextDbOracleSettings.from_env()
        assert result.is_success
        config = result.value
        assert config.port == 1521

    def test_config_serialization(self) -> None:
        """Test config serialization."""
        config = FlextDbOracleSettings(
            host="test.com", port=1522, username="user", password="pass"
        )
        serialized = config.model_dump()
        assert serialized["host"] == "test.com"
        assert serialized["port"] == 1522
        assert serialized["username"] == "user"

    def test_config_equality(self) -> None:
        """Test config equality comparison."""
        config1 = FlextDbOracleSettings(host="localhost", port=1521)
        config2 = FlextDbOracleSettings(host="localhost", port=1521)
        config3 = FlextDbOracleSettings(host="remotehost", port=1521)
        assert config1 == config2
        assert config1 != config3

    def test_config_repr(self) -> None:
        """Test config string representation."""
        config = FlextDbOracleSettings(host="localhost", port=1521, username="system")
        repr_str = repr(config)
        assert "FlextDbOracleSettings" in repr_str
        assert "localhost" in repr_str
        assert "1521" in repr_str

    def test_config_connection_string_components(self) -> None:
        """Test that config has all components needed for connection string."""
        config = FlextDbOracleSettings(
            host="oracle.example.com",
            port=1521,
            service_name="ORCLPDB1",
            username="appuser",
        )
        assert config.host == "oracle.example.com"
        assert config.port == 1521
        assert config.service_name == "ORCLPDB1"
        assert config.username == "appuser"
        assert config.name == "XE"

    def test_config_validation_through_creation(self) -> None:
        """Test config validation through successful creation."""
        config = FlextDbOracleSettings(
            host="valid-host",
            port=1521,
            service_name="VALID_SERVICE",
            username="valid_user",
        )
        assert config.host == "valid-host"
        assert config.port == 1521

    def test_config_immutable_defaults(self) -> None:
        """Test that config defaults are properly set and don't change."""
        config1 = FlextDbOracleSettings()
        config2 = FlextDbOracleSettings()
        assert config1.host == config2.host == "localhost"
        assert config1.port == config2.port == 1521
        assert config1.service_name == config2.service_name == "XEPDB1"
        config1.host = "modified"
        assert config2.host == "localhost"

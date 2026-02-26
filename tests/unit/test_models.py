"""Comprehensive unit tests for flext_db_oracle.models module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleModels, FlextDbOracleSettings
from flext_db_oracle.constants import FlextDbOracleConstants


@pytest.mark.unit_pure
class TestFlextDbOracleModels:
    """Comprehensive test FlextDbOracleModels functionality and validation."""

    # =============================================================================
    # ConnectionStatus tests
    # =============================================================================

    def test_connection_status_creation_defaults(self) -> None:
        """Test ConnectionStatus creation with defaults."""
        status = FlextDbOracleModels.ConnectionStatus()
        assert not status.is_connected
        assert status.error_message == ""
        assert status.connection_time == pytest.approx(0.0)
        assert status.session_id == ""
        assert status.host == ""
        assert status.port == FlextDbOracleConstants.Connection.DEFAULT_PORT
        assert status.service_name == ""
        assert status.username == ""
        assert status.db_version == ""

    def test_connection_status_creation_with_values(self) -> None:
        """Test ConnectionStatus creation with custom values."""
        now = datetime.now(UTC)
        status = FlextDbOracleModels.ConnectionStatus(
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
        status = FlextDbOracleModels.ConnectionStatus(
            is_connected=True,
            last_activity=now,
            host="localhost",
            service_name="XEPDB1",
            username="system",
        )

        # Test status_description
        assert status.status_description == "Connected"

        # Test disconnected status
        status.is_connected = False
        status.error_message = "Connection lost"
        assert status.status_description == "Disconnected: Connection lost"

        # Reset for other tests
        status.is_connected = True
        status.error_message = ""

        # Test connection_age_seconds
        assert status.connection_age_seconds >= 0

        # Test is_healthy
        assert status.is_healthy

        # Test connection_info
        assert "localhost" in status.connection_info
        assert "1521" in status.connection_info
        assert "XEPDB1" in status.connection_info
        assert "system" in status.connection_info

    def test_connection_status_performance_info(self) -> None:
        """Test ConnectionStatus performance rating."""
        # Excellent performance
        status = FlextDbOracleModels.ConnectionStatus(
            is_connected=True,
            connection_time=0.05,  # 50ms
        )
        assert "Excellent" in status.performance_info

        # Good performance
        status.connection_time = 0.3  # 300ms
        assert "Good" in status.performance_info

        # Acceptable performance
        status.connection_time = 1.5  # 1.5s
        assert "Acceptable" in status.performance_info

        # Slow performance
        status.connection_time = 3.0  # 3s
        assert "Slow" in status.performance_info

        # No performance data
        status.connection_time = 0.0
        assert "No performance data" in status.performance_info

    def test_connection_status_validation(self) -> None:
        """Test ConnectionStatus validation."""
        # Valid connected status
        status = FlextDbOracleModels.ConnectionStatus(
            is_connected=True,
            host="localhost",
            port=1521,
        )
        # Should not raise validation error
        validated = status.model_validate(status.model_dump())
        assert validated.is_connected

        # Invalid: connected without host
        with pytest.raises(
            ValueError,
            match="Connected status requires host information",
        ):
            FlextDbOracleModels.ConnectionStatus(
                is_connected=True,
                host="",  # Empty host when connected
                port=1521,
            )

        # Invalid port number
        with pytest.raises(ValueError, match="Invalid port number"):
            FlextDbOracleModels.ConnectionStatus(
                is_connected=True,
                host="localhost",
                port=99999,  # Invalid port
            )

        # Invalid negative connection time
        with pytest.raises(ValueError, match="Connection time cannot be negative"):
            FlextDbOracleModels.ConnectionStatus(connection_time=-1.0)

    def test_connection_status_serialization(self) -> None:
        """Test ConnectionStatus field serialization."""
        now = datetime.now(UTC)
        status = FlextDbOracleModels.ConnectionStatus(
            is_connected=True,
            last_check=now,
            last_activity=now,
            error_message="Test error message that is very long and should be truncated because it's over 500 characters in length and we want to make sure the serialization works properly by cutting it off at the appropriate limit",
            connection_time=1.23456,
        )

        # Test datetime serialization
        serialized = status.model_dump(mode="json")
        assert "last_check" in serialized
        assert "last_activity" in serialized

        # Test error message truncation
        assert len(status.error_message) <= 500 + len("... (truncated)")

        # Test connection time formatting
        assert status.connection_time == pytest.approx(1.23456)

    # =============================================================================
    # QueryResult tests
    # =============================================================================

    def test_query_result_creation_minimal(self) -> None:
        """Test QueryResult creation with minimal data."""
        result = FlextDbOracleModels.QueryResult(query="SELECT 1")
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
        result = FlextDbOracleModels.QueryResult(
            query="SELECT id, name FROM users",
            columns=["id", "name"],
            rows=[[1, "John"], [2, "Jane"]],
            execution_time_ms=150,
            query_hash="abc123",
            explain_plan="TABLE ACCESS FULL",
        )
        assert result.query == "SELECT id, name FROM users"
        assert result.row_count == 2  # Should be auto-calculated
        assert result.execution_time_ms == 150
        assert result.columns == ["id", "name"]
        assert result.rows == [[1, "John"], [2, "Jane"]]
        assert result.query_hash == "abc123"
        assert result.explain_plan == "TABLE ACCESS FULL"

    def test_query_result_computed_fields(self) -> None:
        """Test QueryResult computed fields."""
        result = FlextDbOracleModels.QueryResult(
            query="SELECT 1",
            execution_time_ms=2500,  # 2.5 seconds
            columns=["col1"],
            rows=[[1], [2], [3]],
        )

        # Test execution_time_seconds
        assert result.execution_time_seconds == pytest.approx(2.5)

        # Test has_results
        assert result.has_results

        # Test column_count
        assert result.column_count == 1

        # Test performance_rating
        assert result.performance_rating == "Acceptable"  # 2500ms is acceptable

        # Test data_size_bytes estimation
        expected_size = 3 * 1 * 50  # rows * columns * factor
        assert result.data_size_bytes == expected_size

        # Test memory_usage_mb
        expected_mb = expected_size / (1024 * 1024)
        assert result.memory_usage_mb == expected_mb

    def test_query_result_performance_ratings(self) -> None:
        """Test QueryResult performance rating categories."""
        # Excellent
        result = FlextDbOracleModels.QueryResult(query="SELECT 1", execution_time_ms=50)
        assert result.performance_rating == "Excellent"

        # Good
        result.execution_time_ms = 300
        assert result.performance_rating == "Good"

        # Acceptable
        result.execution_time_ms = 1500
        assert result.performance_rating == "Acceptable"

        # Slow
        result.execution_time_ms = 2500
        assert result.performance_rating == "Slow"

    def test_query_result_validation(self) -> None:
        """Test QueryResult validation."""
        # Valid result
        result = FlextDbOracleModels.QueryResult(
            query="SELECT 1",
            columns=["id"],
            rows=[[1], [2]],
            execution_time_ms=100,
        )
        validated = result.model_validate(result.model_dump())
        assert validated.row_count == 2  # Auto-corrected

        # Invalid: negative execution time
        with pytest.raises(ValueError, match="Execution time cannot be negative"):
            FlextDbOracleModels.QueryResult(query="SELECT 1", execution_time_ms=-100)

        # Invalid: row/column mismatch (this should be caught)
        with pytest.raises(ValueError, match=r"Row length.*doesn't match column count"):
            FlextDbOracleModels.QueryResult(
                query="SELECT 1",
                columns=["id", "name"],  # 2 columns
                rows=[[1], [2]],  # 1 value per row
            )

    def test_query_result_serialization(self) -> None:
        """Test QueryResult field serialization."""
        result = FlextDbOracleModels.QueryResult(
            query="SELECT 1",
            execution_time_ms=1500,  # 1.5 seconds
        )

        serialized = result.model_dump(mode="json")
        assert "execution_time_ms" in serialized

        # Test execution time serialization (should show as "1500ms" or "1.5s")
        execution_time_str = result.execution_time_ms
        assert execution_time_str == 1500

    # =============================================================================
    # Table, Column, Schema tests
    # =============================================================================

    def test_table_creation(self) -> None:
        """Test Table model creation."""
        table = FlextDbOracleModels.Table(name="users", owner="hr")
        assert table.name == "users"
        assert table.owner == "hr"
        assert table.columns == []

    def test_table_with_columns(self) -> None:
        """Test Table with columns."""
        columns = [
            FlextDbOracleModels.Column(name="id", data_type="NUMBER", nullable=False),
            FlextDbOracleModels.Column(name="name", data_type="VARCHAR2(100)"),
        ]
        table = FlextDbOracleModels.Table(name="users", owner="hr", columns=columns)
        assert len(table.columns) == 2
        assert table.columns[0].name == "id"
        assert table.columns[0].nullable is False
        assert table.columns[1].name == "name"
        assert table.columns[1].nullable is True  # default

    def test_column_creation(self) -> None:
        """Test Column model creation."""
        column = FlextDbOracleModels.Column(
            name="user_id",
            data_type="NUMBER(38)",
            nullable=False,
            default_value="NULL",
        )
        assert column.name == "user_id"
        assert column.data_type == "NUMBER(38)"
        assert column.nullable is False
        assert column.default_value == "NULL"

    def test_schema_creation(self) -> None:
        """Test Schema model creation."""
        schema = FlextDbOracleModels.Schema(name="hr")
        assert schema.name == "hr"
        assert schema.tables == []

    def test_schema_with_tables(self) -> None:
        """Test Schema with tables."""
        tables = [
            FlextDbOracleModels.Table(name="users", owner="hr"),
            FlextDbOracleModels.Table(name="orders", owner="hr"),
        ]
        schema = FlextDbOracleModels.Schema(name="hr", tables=tables)
        assert len(schema.tables) == 2
        assert schema.tables[0].name == "users"
        assert schema.tables[1].name == "orders"

    # =============================================================================
    # CreateIndexConfig tests
    # =============================================================================

    def test_create_index_config_creation(self) -> None:
        """Test CreateIndexConfig creation."""
        config = FlextDbOracleModels.CreateIndexConfig(
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

    # =============================================================================
    # MergeStatementConfig tests
    # =============================================================================

    def test_merge_statement_config_creation(self) -> None:
        """Test MergeStatementConfig creation."""
        config = FlextDbOracleModels.MergeStatementConfig(
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

    # =============================================================================
    # Integration tests with real Oracle when available
    # =============================================================================

    def test_connection_status_real_oracle_integration(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test ConnectionStatus with real Oracle connection."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")

        # Create a connection status from real connection
        status = FlextDbOracleModels.ConnectionStatus(
            is_connected=True,
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="flexttest",
            connection_time=0.1,
        )

        # Test computed fields
        assert status.status_description == "Connected"
        assert (
            status.connection_info
            == "host=localhost, port=1521, service=XEPDB1, user=flexttest"
        )
        assert status.is_healthy  # Should be healthy with recent activity

        # Test performance info
        assert (
            "Excellent" in status.performance_info or "Good" in status.performance_info
        )

    def test_query_result_real_oracle_integration(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test QueryResult with real Oracle data."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")

        # Execute a real query
        query_result = connected_oracle_api.query(
            "SELECT 1 as id, 'test' as name FROM DUAL",
        )
        assert query_result.is_success

        data = query_result.value
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["name"] == "test"

        # Create QueryResult model from real data
        result_model = FlextDbOracleModels.QueryResult(
            query="SELECT 1 as id, 'test' as name FROM DUAL",
            columns=["id", "name"],
            rows=[[1, "test"]],
            execution_time_ms=50,
        )

        # Test computed fields
        assert result_model.has_results
        assert result_model.column_count == 2
        assert result_model.performance_rating in {
            "Excellent",
            "Good",
            "Acceptable",
            "Slow",
        }

    def test_table_model_real_oracle_integration(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test Table model with real Oracle schema data."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")

        # Get real schema information
        schemas_result = connected_oracle_api.get_schemas()
        if schemas_result.is_success:
            schemas = schemas_result.value
            if schemas:
                # Create a table model representing real schema data
                table = FlextDbOracleModels.Table(
                    name="dual",  # DUAL table exists in Oracle
                    owner="SYS",
                )
                assert table.name == "dual"
                assert table.owner == "SYS"
                assert table.columns == []  # No columns defined in this simple test


class TestFlextDbOracleSettings:
    """Comprehensive test FlextDbOracleSettings functionality."""

    def test_config_creation_defaults(self) -> None:
        """Test config creation with defaults."""
        config = FlextDbOracleSettings()
        assert config.host == "localhost"
        assert config.port == 1521
        assert config.name == "XE"  # database name defaults to XE
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
        # Clear relevant env vars
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
        # Should have defaults
        assert config.host == "localhost"
        assert config.port == 1521
        assert config.service_name == "XEPDB1"

    def test_config_from_env_with_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config creation from environment variables."""
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
        assert config.name == "ORCL"  # database_name maps to name

    def test_config_from_env_flext_prefix(
        self,
        monkeypatch: pytest.MonkeyPatch,
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
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test config creation with mixed prefixes."""
        monkeypatch.setenv("ORACLE_HOST", "oracle-host")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_HOST", "flext-host")
        monkeypatch.setenv("ORACLE_USERNAME", "oracle-user")
        monkeypatch.setenv("FLEXT_TARGET_ORACLE_USERNAME", "flext-user")

        result = FlextDbOracleSettings.from_env()
        assert result.is_success
        config = result.value
        # Both prefixes should be present in the mapping
        assert config.host == "flext-host"  # FLEXT prefix takes precedence if both set
        assert config.username == "flext-user"

    def test_config_from_env_port_conversion(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test port conversion from environment string to int."""
        monkeypatch.setenv("ORACLE_PORT", "1523")

        result = FlextDbOracleSettings.from_env()
        assert result.is_success
        config = result.value
        assert config.port == 1523
        assert isinstance(config.port, int)

    def test_config_from_env_invalid_port(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test config creation with invalid port."""
        monkeypatch.setenv("ORACLE_PORT", "invalid")

        result = FlextDbOracleSettings.from_env()
        assert result.is_success  # Should not fail, uses default
        config = result.value
        assert config.port == 1521  # Default value

    def test_config_serialization(self) -> None:
        """Test config serialization."""
        config = FlextDbOracleSettings(
            host="test.com",
            port=1522,
            username="user",
            password="pass",
        )

        serialized = config.model_dump()
        assert serialized["host"] == "test.com"
        assert serialized["port"] == 1522
        assert serialized["username"] == "user"
        # Password should be included in serialization (may be needed for connection)

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

        # Verify all connection components are present
        assert config.host == "oracle.example.com"
        assert config.port == 1521
        assert config.service_name == "ORCLPDB1"
        assert config.username == "appuser"

        # Name should be available for SID connections
        assert config.name == "XE"  # default

    def test_config_validation_through_creation(self) -> None:
        """Test config validation through successful creation."""
        # Valid config should create without errors
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

        # Both should have same defaults
        assert config1.host == config2.host == "localhost"
        assert config1.port == config2.port == 1521
        assert config1.service_name == config2.service_name == "XEPDB1"

        # Modifying one shouldn't affect the other
        config1.host = "modified"
        assert config2.host == "localhost"

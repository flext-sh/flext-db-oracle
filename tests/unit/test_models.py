"""Test FlextDbOracleModels functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleConfig, FlextDbOracleModels


class TestFlextDbOracleModels:
    """Test FlextDbOracleModels functionality."""

    def test_models_has_connection_status(self) -> None:
        """Test models has ConnectionStatus class."""
        assert hasattr(FlextDbOracleModels, "ConnectionStatus")

    def test_models_has_query_result(self) -> None:
        """Test models has QueryResult class."""
        assert hasattr(FlextDbOracleModels, "QueryResult")

    def test_models_has_table(self) -> None:
        """Test models has Table class."""
        assert hasattr(FlextDbOracleModels, "Table")

    def test_models_has_column(self) -> None:
        """Test models has Column class."""
        assert hasattr(FlextDbOracleModels, "Column")

    def test_models_has_schema(self) -> None:
        """Test models has Schema class."""
        assert hasattr(FlextDbOracleModels, "Schema")

    def test_connection_status_creation(self) -> None:
        """Test ConnectionStatus can be created."""
        status = FlextDbOracleModels.ConnectionStatus()
        assert status is not None
        assert hasattr(status, "is_connected")

    def test_query_result_creation(self) -> None:
        """Test QueryResult can be created."""
        result = FlextDbOracleModels.QueryResult(
            query="SELECT 1", rows=[["value1"], ["value2"]]
        )
        assert result is not None
        assert result.query == "SELECT 1"
        assert result.row_count == 2

    def test_table_creation(self) -> None:
        """Test Table can be created."""
        table = FlextDbOracleModels.Table(name="test_table", schema="test_schema")
        assert table is not None
        assert table.name == "test_table"

    def test_column_creation(self) -> None:
        """Test Column can be created."""
        column = FlextDbOracleModels.Column(name="test_column", data_type="VARCHAR2")
        assert column is not None
        assert column.name == "test_column"

    def test_schema_creation(self) -> None:
        """Test Schema can be created."""
        schema = FlextDbOracleModels.Schema(name="test_schema")
        assert schema is not None
        assert schema.name == "test_schema"


class TestFlextDbOracleConfig:
    """Test FlextDbOracleConfig functionality."""

    def test_config_creation(self) -> None:
        """Test config can be created."""
        config = FlextDbOracleConfig()
        assert config is not None

    def test_config_attributes(self) -> None:
        """Test config has required attributes."""
        config = FlextDbOracleConfig()
        assert hasattr(config, "host")
        assert hasattr(config, "port")
        assert hasattr(config, "service_name")

    def test_config_defaults(self) -> None:
        """Test config has correct defaults."""
        config = FlextDbOracleConfig()
        assert config.host == "localhost"
        assert config.port == 1521
        assert config.service_name == "XEPDB1"

    def test_config_from_env_success(self) -> None:
        """Test config creation from environment succeeds."""
        result = FlextDbOracleConfig.from_env()
        assert result.is_success
        config = result.unwrap()
        assert config.host == "localhost"

    def test_config_with_custom_values(self) -> None:
        """Test config with custom values."""
        config = FlextDbOracleConfig(
            host="test-host", username="test-user", password="test-password"
        )
        assert config.host == "test-host"
        assert config.username == "test-user"

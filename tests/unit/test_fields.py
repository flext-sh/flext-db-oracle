"""Test field definitions and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleSettings
from tests.models import m


class TestsFlextDbOracleFields:
    """Test m and FlextDbOracleSettings fields."""

    def test_host_field_exists(self) -> None:
        """Test host field exists on settings."""
        assert "host" in FlextDbOracleSettings.model_fields
        assert FlextDbOracleSettings.model_fields["host"] is not None

    def test_port_field_exists(self) -> None:
        """Test port field exists on settings."""
        assert "port" in FlextDbOracleSettings.model_fields
        assert FlextDbOracleSettings.model_fields["port"] is not None

    def test_username_field_exists(self) -> None:
        """Test username field exists on settings."""
        assert "username" in FlextDbOracleSettings.model_fields
        assert FlextDbOracleSettings.model_fields["username"] is not None

    def test_password_field_exists(self) -> None:
        """Test password field exists on settings."""
        assert "password" in FlextDbOracleSettings.model_fields
        assert FlextDbOracleSettings.model_fields["password"] is not None

    def test_service_name_field_exists(self) -> None:
        """Test service_name field exists on settings."""
        assert "service_name" in FlextDbOracleSettings.model_fields
        assert FlextDbOracleSettings.model_fields["service_name"] is not None

    def test_connection_status_model_fields(self) -> None:
        """Test ConnectionStatus model has expected fields."""
        fields = m.DbOracle.ConnectionStatus.model_fields
        assert "connected" in fields
        assert "error_message" in fields

    def test_query_result_model_fields(self) -> None:
        """Test QueryResult model has expected fields."""
        fields = m.DbOracle.QueryResult.model_fields
        assert "query" in fields
        assert "columns" in fields
        assert "rows" in fields

    def test_row_data_model_fields(self) -> None:
        """Test RowData model has expected fields."""
        fields = m.DbOracle.RowData.model_fields
        assert "values" in fields

    def test_column_metadata_model_fields(self) -> None:
        """Test ColumnMetadata model has expected fields."""
        fields = m.DbOracle.ColumnMetadata.model_fields
        assert "name" in fields
        assert "data_type" in fields
        assert "nullable" in fields

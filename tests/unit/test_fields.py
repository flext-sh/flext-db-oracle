"""Test field definitions and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import tm

from flext_db_oracle import FlextDbOracleModels, FlextDbOracleSettings


class TestFlextDbOracleFields:
    """Test FlextDbOracleModels and FlextDbOracleSettings fields."""

    def test_host_field_exists(self) -> None:
        """Test host field exists on settings."""
        tm.that(FlextDbOracleSettings.model_fields, has="host")
        tm.that(FlextDbOracleSettings.model_fields["host"], none=False)

    def test_port_field_exists(self) -> None:
        """Test port field exists on settings."""
        tm.that(FlextDbOracleSettings.model_fields, has="port")
        tm.that(FlextDbOracleSettings.model_fields["port"], none=False)

    def test_username_field_exists(self) -> None:
        """Test username field exists on settings."""
        tm.that(FlextDbOracleSettings.model_fields, has="username")
        tm.that(FlextDbOracleSettings.model_fields["username"], none=False)

    def test_password_field_exists(self) -> None:
        """Test password field exists on settings."""
        tm.that(FlextDbOracleSettings.model_fields, has="password")
        tm.that(FlextDbOracleSettings.model_fields["password"], none=False)

    def test_service_name_field_exists(self) -> None:
        """Test service_name field exists on settings."""
        tm.that(FlextDbOracleSettings.model_fields, has="service_name")
        tm.that(FlextDbOracleSettings.model_fields["service_name"], none=False)

    def test_connection_status_model_fields(self) -> None:
        """Test ConnectionStatus model has expected fields."""
        fields = FlextDbOracleModels.DbOracle.ConnectionStatus.model_fields
        tm.that(fields, has="is_connected")
        tm.that(fields, has="error_message")

    def test_query_result_model_fields(self) -> None:
        """Test QueryResult model has expected fields."""
        fields = FlextDbOracleModels.DbOracle.QueryResult.model_fields
        tm.that(fields, has="query")
        tm.that(fields, has="columns")
        tm.that(fields, has="rows")

    def test_row_data_model_fields(self) -> None:
        """Test RowData model has expected fields."""
        fields = FlextDbOracleModels.DbOracle.RowData.model_fields
        tm.that(fields, has="values")

    def test_column_metadata_model_fields(self) -> None:
        """Test ColumnMetadata model has expected fields."""
        fields = FlextDbOracleModels.DbOracle.ColumnMetadata.model_fields
        tm.that(fields, has="name")
        tm.that(fields, has="data_type")
        tm.that(fields, has="nullable")

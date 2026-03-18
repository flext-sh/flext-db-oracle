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
        tm.that("host" in FlextDbOracleSettings.model_fields, eq=True)
        tm.that(FlextDbOracleSettings.model_fields["host"] is not None, eq=True)

    def test_port_field_exists(self) -> None:
        """Test port field exists on settings."""
        tm.that("port" in FlextDbOracleSettings.model_fields, eq=True)
        tm.that(FlextDbOracleSettings.model_fields["port"] is not None, eq=True)

    def test_username_field_exists(self) -> None:
        """Test username field exists on settings."""
        tm.that("username" in FlextDbOracleSettings.model_fields, eq=True)
        tm.that(FlextDbOracleSettings.model_fields["username"] is not None, eq=True)

    def test_password_field_exists(self) -> None:
        """Test password field exists on settings."""
        tm.that("password" in FlextDbOracleSettings.model_fields, eq=True)
        tm.that(FlextDbOracleSettings.model_fields["password"] is not None, eq=True)

    def test_service_name_field_exists(self) -> None:
        """Test service_name field exists on settings."""
        tm.that("service_name" in FlextDbOracleSettings.model_fields, eq=True)
        tm.that(FlextDbOracleSettings.model_fields["service_name"] is not None, eq=True)

    def test_connection_status_model_fields(self) -> None:
        """Test ConnectionStatus model has expected fields."""
        fields = FlextDbOracleModels.DbOracle.ConnectionStatus.model_fields
        tm.that("is_connected" in fields, eq=True)
        tm.that("error_message" in fields, eq=True)

    def test_query_result_model_fields(self) -> None:
        """Test QueryResult model has expected fields."""
        fields = FlextDbOracleModels.DbOracle.QueryResult.model_fields
        tm.that("query" in fields, eq=True)
        tm.that("columns" in fields, eq=True)
        tm.that("rows" in fields, eq=True)

    def test_row_data_model_fields(self) -> None:
        """Test RowData model has expected fields."""
        fields = FlextDbOracleModels.DbOracle.RowData.model_fields
        tm.that("values" in fields, eq=True)

    def test_column_metadata_model_fields(self) -> None:
        """Test ColumnMetadata model has expected fields."""
        fields = FlextDbOracleModels.DbOracle.ColumnMetadata.model_fields
        tm.that("name" in fields, eq=True)
        tm.that("data_type" in fields, eq=True)
        tm.that("nullable" in fields, eq=True)

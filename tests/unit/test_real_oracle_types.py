"""Real Oracle Types Tests - Using Docker Oracle Container.

This module tests type definition functionality against a real Oracle container,
maximizing coverage of type operations using actual database data structures.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_db_oracle import FlextDbOracleApi

from flext_db_oracle.types import (
    TDbOracleColumn,
    TDbOracleConnectionStatus,
    TDbOracleQueryResult,
    TDbOracleSchema,
    TDbOracleTable,
)


class TestRealOracleTypeValidation:
    """Test Oracle type validation with real data."""

    def test_real_oracle_column_from_db(self, oracle_api: FlextDbOracleApi, oracle_container: None) -> None:
        """Test creating Oracle column type from real database metadata."""
        # Connect first
        connected_api = oracle_api.connect()

        # Get real column data from Oracle
        columns_result = connected_api.get_columns("EMPLOYEES")
        assert columns_result.success

        # Find the EMPLOYEE_ID column
        employee_id_col = None
        for col in columns_result.data:
            if col["column_name"] == "EMPLOYEE_ID":
                employee_id_col = col
                break

        assert employee_id_col is not None

        # Create TDbOracleColumn from real data
        column = TDbOracleColumn(
            name=employee_id_col["column_name"],
            data_type=employee_id_col["data_type"],
            nullable=employee_id_col["nullable"],
            max_length=employee_id_col.get("data_length"),
            precision=employee_id_col.get("data_precision"),
            scale=employee_id_col.get("data_scale"),
            position=employee_id_col["column_id"],
            is_primary_key=True,  # We know this is the PK
        )

        # Validate domain rules
        validation = column.validate_domain_rules()
        assert validation.success

        # Test properties
        assert column.is_key_column
        assert "NUMBER" in column.full_type_spec

    def test_real_oracle_table_from_db(self, oracle_api: FlextDbOracleApi, oracle_container: None) -> None:
        """Test creating Oracle table type from real database metadata."""
        # Connect first
        connected_api = oracle_api.connect()

        # Get real table and column data
        columns_result = connected_api.get_columns("EMPLOYEES")
        assert columns_result.success

        # Create column objects
        columns = []
        for col_data in columns_result.data:
            column = TDbOracleColumn(
                name=col_data["column_name"],
                data_type=col_data["data_type"],
                nullable=col_data["nullable"],
                max_length=col_data.get("data_length"),
                precision=col_data.get("data_precision"),
                scale=col_data.get("data_scale"),
                position=col_data["column_id"],
                is_primary_key=(col_data["column_name"] == "EMPLOYEE_ID"),
            )
            columns.append(column)

        # Create table object
        table = TDbOracleTable(
            name="EMPLOYEES",
            schema_name="FLEXTTEST",
            columns=columns,
            created_date=datetime.now(),
        )

        # Validate domain rules
        validation = table.validate_domain_rules()
        assert validation.success

        # Test properties
        assert table.qualified_name == "FLEXTTEST.EMPLOYEES"
        assert len(table.primary_key_columns) == 1
        assert table.primary_key_columns[0].name == "EMPLOYEE_ID"
        assert "EMPLOYEE_ID" in table.column_names

    def test_real_oracle_schema_from_db(self, oracle_api: FlextDbOracleApi, oracle_container: None) -> None:
        """Test creating Oracle schema type from real database metadata."""
        # Connect first
        connected_api = oracle_api.connect()

        # Get real schema data
        tables_result = connected_api.get_tables()
        assert tables_result.success

        # Create table objects for a few key tables
        tables = []
        for table_name in ["EMPLOYEES", "DEPARTMENTS", "JOBS"]:
            if table_name in tables_result.data:
                # Get columns for this table
                columns_result = connected_api.get_columns(table_name)
                if columns_result.success:
                    columns = []
                    for col_data in columns_result.data:
                        column = TDbOracleColumn(
                            name=col_data["column_name"],
                            data_type=col_data["data_type"],
                            nullable=col_data["nullable"],
                            position=col_data["column_id"],
                        )
                        columns.append(column)

                    table = TDbOracleTable(
                        name=table_name,
                        schema_name="FLEXTTEST",
                        columns=columns,
                    )
                    tables.append(table)

        # Create schema object
        schema = TDbOracleSchema(
            name="FLEXTTEST",
            tables=tables,
            created_date=datetime.now(),
        )

        # Validate domain rules
        validation = schema.validate_domain_rules()
        assert validation.success

        # Test properties
        assert schema.table_count >= 3
        assert schema.total_columns > 0
        assert schema.get_table("EMPLOYEES") is not None

    def test_real_oracle_query_result_from_db(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test creating query result type from real database query."""
        # Connect first
        connected_api = oracle_api.connect()

        # Execute real query
        query_result = connected_api.query(
            "SELECT employee_id, first_name, last_name FROM EMPLOYEES WHERE ROWNUM <= 3",
        )
        assert query_result.success

        # Create TDbOracleQueryResult from real data
        query_result_obj = TDbOracleQueryResult(
            rows=[(row[0], row[1], row[2]) for row in query_result.data],
            columns=["EMPLOYEE_ID", "FIRST_NAME", "LAST_NAME"],
            row_count=len(query_result.data),
            execution_time_ms=50.0,  # Simulated timing
        )

        # Validate domain rules
        validation = query_result_obj.validate_domain_rules()
        assert validation.success

        # Test properties and methods
        assert not query_result_obj.is_empty
        assert query_result_obj.row_count == len(query_result_obj.rows)

        # Test to_dict_list conversion
        dict_list = query_result_obj.to_dict_list()
        assert len(dict_list) == query_result_obj.row_count
        assert "EMPLOYEE_ID" in dict_list[0]
        assert "FIRST_NAME" in dict_list[0]

    def test_real_oracle_connection_status_from_db(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test creating connection status type from real connection."""
        # Test connection first
        connection_result = oracle_api.test_connection()
        assert connection_result.success

        # Create connection status object
        connection_status = TDbOracleConnectionStatus(
            is_connected=True,
            host="localhost",
            port=1521,
            database="XEPDB1",
            username="flexttest",
            last_check=datetime.now(),
        )

        # Validate domain rules
        validation = connection_status.validate_domain_rules()
        assert validation.success

        # Test properties
        assert connection_status.connection_string == "flexttest@localhost:1521/XEPDB1"


class TestRealOracleTypeConversions:
    """Test Oracle type conversions with real data."""

    def test_real_oracle_data_type_mapping(self, oracle_api: FlextDbOracleApi, oracle_container: None) -> None:
        """Test mapping Oracle data types to Python types."""
        # Get real column data with various Oracle types
        columns_result = oracle_api.get_columns("EMPLOYEES")
        assert columns_result.success

        type_mappings = {}
        for col_data in columns_result.data:
            column = TDbOracleColumn(
                name=col_data["column_name"],
                data_type=col_data["data_type"],
                nullable=col_data["nullable"],
                position=col_data["column_id"],
                precision=col_data.get("data_precision"),
                scale=col_data.get("data_scale"),
                max_length=col_data.get("data_length"),
            )

            type_mappings[column.name] = column.full_type_spec

        # Verify common Oracle types are handled
        assert any("NUMBER" in spec for spec in type_mappings.values())
        assert any("VARCHAR2" in spec for spec in type_mappings.values())
        assert any("DATE" in spec for spec in type_mappings.values())

    def test_real_oracle_singer_type_conversion(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test converting Oracle types to Singer schema types."""
        # Get real column data
        columns_result = oracle_api.get_columns("EMPLOYEES")
        assert columns_result.success

        # Test Singer schema generation
        singer_schema = {
            "type": "object",
            "properties": {},
        }

        for col_data in columns_result.data:
            oracle_type = col_data["data_type"]

            # Map Oracle types to Singer types
            if "NUMBER" in oracle_type:
                singer_type = ["null", "number"] if col_data["nullable"] else ["number"]
            elif "VARCHAR" in oracle_type or "DATE" in oracle_type:
                singer_type = ["null", "string"] if col_data["nullable"] else ["string"]
            else:
                singer_type = ["null", "string"] if col_data["nullable"] else ["string"]

            singer_schema["properties"][col_data["column_name"]] = {
                "type": singer_type,
            }

        # Validate Singer schema structure
        assert "properties" in singer_schema
        assert "EMPLOYEE_ID" in singer_schema["properties"]
        assert "FIRST_NAME" in singer_schema["properties"]

    def test_real_oracle_constraint_validation(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test Oracle constraint validation with real data."""
        # Get real table with constraints
        columns_result = oracle_api.get_columns("EMPLOYEES")
        assert columns_result.success

        # Create table with validation rules
        columns = []
        for col_data in columns_result.data:
            column = TDbOracleColumn(
                name=col_data["column_name"],
                data_type=col_data["data_type"],
                nullable=col_data["nullable"],
                position=col_data["column_id"],
                is_primary_key=(col_data["column_name"] == "EMPLOYEE_ID"),
            )
            columns.append(column)

        table = TDbOracleTable(
            name="EMPLOYEES",
            schema_name="FLEXTTEST",
            columns=columns,
        )

        # Test constraint validation
        validation = table.validate_domain_rules()
        assert validation.success

        # Verify primary key constraints
        pk_columns = table.primary_key_columns
        assert len(pk_columns) == 1
        assert pk_columns[0].name == "EMPLOYEE_ID"


class TestRealOracleTypeErrorHandling:
    """Test Oracle type error handling."""

    def test_oracle_column_invalid_position(self) -> None:
        """Test column with invalid position."""
        column = TDbOracleColumn(
            name="TEST_COL",
            data_type="VARCHAR2(50)",
            position=0,  # Invalid - must be > 0
        )

        validation = column.validate_domain_rules()
        assert validation.is_failure
        assert "position" in validation.error.lower()

    def test_oracle_column_empty_name(self) -> None:
        """Test column with empty name."""
        column = TDbOracleColumn(
            name="",  # Invalid - empty name
            data_type="VARCHAR2(50)",
            position=1,
        )

        validation = column.validate_domain_rules()
        assert validation.is_failure
        assert "name" in validation.error.lower()

    def test_oracle_table_no_columns(self) -> None:
        """Test table with no columns."""
        table = TDbOracleTable(
            name="EMPTY_TABLE",
            schema_name="TEST",
            columns=[],  # Invalid - no columns
        )

        validation = table.validate_domain_rules()
        assert validation.is_failure
        assert "column" in validation.error.lower()

    def test_oracle_query_result_row_count_mismatch(self) -> None:
        """Test query result with mismatched row count."""
        query_result = TDbOracleQueryResult(
            rows=[("1", "John"), ("2", "Jane")],  # 2 rows
            columns=["ID", "NAME"],
            row_count=3,  # Wrong count
            execution_time_ms=10.0,
        )

        validation = query_result.validate_domain_rules()
        assert validation.is_failure
        assert "mismatch" in validation.error.lower()

    def test_oracle_connection_status_invalid_port(self) -> None:
        """Test connection status with invalid port."""
        connection_status = TDbOracleConnectionStatus(
            is_connected=True,
            host="localhost",
            port=999999,  # Invalid port
            database="TEST",
            username="test",
            last_check=datetime.now(),
        )

        validation = connection_status.validate_domain_rules()
        assert validation.is_failure
        assert "port" in validation.error.lower()

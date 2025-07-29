"""Comprehensive tests for types module."""

from __future__ import annotations

from datetime import UTC, datetime

from flext_db_oracle.constants import (
    ERROR_MSG_COLUMN_NAME_EMPTY,
    ERROR_MSG_DATA_TYPE_EMPTY,
    ERROR_MSG_HOST_EMPTY,
    ERROR_MSG_PORT_INVALID,
    ERROR_MSG_POSITION_INVALID,
    ERROR_MSG_SCHEMA_NAME_EMPTY,
    ERROR_MSG_TABLE_NAME_EMPTY,
    ERROR_MSG_USERNAME_EMPTY,
    MAX_PORT,
)
from flext_db_oracle.types import (
    TDbOracleColumn,
    TDbOracleConnectionStatus,
    TDbOracleQueryResult,
    TDbOracleSchema,
    TDbOracleTable,
)


class TestTDbOracleColumn:
    """Test TDbOracleColumn type."""

    def test_column_creation_valid(self) -> None:
        """Test valid column creation."""
        column = TDbOracleColumn(
            name="EMPLOYEE_ID",
            data_type="NUMBER",
            nullable=False,
            default_value=None,
            max_length=None,
            precision=6,
            scale=0,
            position=1,
            comments="Employee unique identifier",
            is_primary_key=True,
            is_foreign_key=False,
        )

        assert column.name == "EMPLOYEE_ID"
        assert column.data_type == "NUMBER"
        assert not column.nullable
        assert column.precision == 6
        assert column.scale == 0
        assert column.position == 1
        assert column.comments == "Employee unique identifier"
        assert column.is_primary_key
        assert not column.is_foreign_key

    def test_column_validation_success(self) -> None:
        """Test successful column validation."""
        column = TDbOracleColumn(
            name="FIRST_NAME",
            data_type="VARCHAR2",
            position=2,
        )

        result = column.validate_domain_rules()
        assert result.is_success
        assert result.data is None

    def test_column_validation_empty_name(self) -> None:
        """Test column validation with empty name."""
        column = TDbOracleColumn(
            name="",
            data_type="VARCHAR2",
            position=1,
        )

        result = column.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_COLUMN_NAME_EMPTY in result.error

    def test_column_validation_whitespace_name(self) -> None:
        """Test column validation with whitespace name."""
        column = TDbOracleColumn(
            name="   ",
            data_type="VARCHAR2",
            position=1,
        )

        result = column.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_COLUMN_NAME_EMPTY in result.error

    def test_column_validation_empty_data_type(self) -> None:
        """Test column validation with empty data type."""
        column = TDbOracleColumn(
            name="TEST_COL",
            data_type="",
            position=1,
        )

        result = column.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_DATA_TYPE_EMPTY in result.error

    def test_column_validation_whitespace_data_type(self) -> None:
        """Test column validation with whitespace data type."""
        column = TDbOracleColumn(
            name="TEST_COL",
            data_type="   ",
            position=1,
        )

        result = column.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_DATA_TYPE_EMPTY in result.error

    def test_column_validation_invalid_position_zero(self) -> None:
        """Test column validation with zero position."""
        column = TDbOracleColumn(
            name="TEST_COL",
            data_type="VARCHAR2",
            position=0,
        )

        result = column.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_POSITION_INVALID in result.error

    def test_column_validation_invalid_position_negative(self) -> None:
        """Test column validation with negative position."""
        column = TDbOracleColumn(
            name="TEST_COL",
            data_type="VARCHAR2",
            position=-1,
        )

        result = column.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_POSITION_INVALID in result.error

    def test_full_type_spec_varchar(self) -> None:
        """Test full type specification for VARCHAR2."""
        column = TDbOracleColumn(
            name="NAME",
            data_type="VARCHAR2",
            max_length=100,
            position=1,
        )

        assert column.full_type_spec == "VARCHAR2(100)"

    def test_full_type_spec_number_with_scale(self) -> None:
        """Test full type specification for NUMBER with precision and scale."""
        column = TDbOracleColumn(
            name="SALARY",
            data_type="NUMBER",
            precision=10,
            scale=2,
            position=1,
        )

        assert column.full_type_spec == "NUMBER(10,2)"

    def test_full_type_spec_number_without_scale(self) -> None:
        """Test full type specification for NUMBER with precision only."""
        column = TDbOracleColumn(
            name="ID",
            data_type="NUMBER",
            precision=10,
            position=1,
        )

        assert column.full_type_spec == "NUMBER(10)"

    def test_full_type_spec_basic_type(self) -> None:
        """Test full type specification for basic type."""
        column = TDbOracleColumn(
            name="CREATED",
            data_type="DATE",
            position=1,
        )

        assert column.full_type_spec == "DATE"

    def test_is_key_column_primary_key(self) -> None:
        """Test is_key_column property for primary key."""
        column = TDbOracleColumn(
            name="ID",
            data_type="NUMBER",
            position=1,
            is_primary_key=True,
            is_foreign_key=False,
        )

        assert column.is_key_column

    def test_is_key_column_foreign_key(self) -> None:
        """Test is_key_column property for foreign key."""
        column = TDbOracleColumn(
            name="DEPT_ID",
            data_type="NUMBER",
            position=1,
            is_primary_key=False,
            is_foreign_key=True,
        )

        assert column.is_key_column

    def test_is_key_column_both_keys(self) -> None:
        """Test is_key_column property for both primary and foreign key."""
        column = TDbOracleColumn(
            name="ID",
            data_type="NUMBER",
            position=1,
            is_primary_key=True,
            is_foreign_key=True,
        )

        assert column.is_key_column

    def test_is_key_column_no_key(self) -> None:
        """Test is_key_column property for non-key column."""
        column = TDbOracleColumn(
            name="NAME",
            data_type="VARCHAR2",
            position=1,
            is_primary_key=False,
            is_foreign_key=False,
        )

        assert not column.is_key_column


class TestTDbOracleTable:
    """Test TDbOracleTable type."""

    def test_table_creation_valid(self) -> None:
        """Test valid table creation."""
        columns = [
            TDbOracleColumn(name="ID", data_type="NUMBER", position=1),
            TDbOracleColumn(name="NAME", data_type="VARCHAR2", position=2),
        ]

        now = datetime.now(UTC)
        table = TDbOracleTable(
            name="EMPLOYEES",
            schema_name="HR",
            columns=columns,
            row_count=1000,
            size_bytes=52428800,  # 50MB in bytes
            tablespace="USERS",
            created_date=now,
            comments="Employee table",
        )

        assert table.name == "EMPLOYEES"
        assert table.schema_name == "HR"
        assert len(table.columns) == 2
        assert table.row_count == 1000
        assert table.size_bytes == 52428800
        assert table.tablespace == "USERS"
        assert table.created_date == now
        assert table.comments == "Employee table"

    def test_table_validation_success(self) -> None:
        """Test successful table validation."""
        columns = [
            TDbOracleColumn(name="ID", data_type="NUMBER", position=1),
        ]

        table = TDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=columns,
        )

        result = table.validate_domain_rules()
        assert result.is_success

    def test_table_validation_empty_name(self) -> None:
        """Test table validation with empty name."""
        columns = [
            TDbOracleColumn(name="ID", data_type="NUMBER", position=1),
        ]

        table = TDbOracleTable(
            name="",
            schema_name="TEST_SCHEMA",
            columns=columns,
        )

        result = table.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_TABLE_NAME_EMPTY in result.error

    def test_table_validation_whitespace_name(self) -> None:
        """Test table validation with whitespace name."""
        columns = [
            TDbOracleColumn(name="ID", data_type="NUMBER", position=1),
        ]

        table = TDbOracleTable(
            name="   ",
            schema_name="TEST_SCHEMA",
            columns=columns,
        )

        result = table.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_TABLE_NAME_EMPTY in result.error

    def test_table_validation_empty_schema_name(self) -> None:
        """Test table validation with empty schema name."""
        columns = [
            TDbOracleColumn(name="ID", data_type="NUMBER", position=1),
        ]

        table = TDbOracleTable(
            name="TEST_TABLE",
            schema_name="",
            columns=columns,
        )

        result = table.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_SCHEMA_NAME_EMPTY in result.error

    def test_table_validation_whitespace_schema_name(self) -> None:
        """Test table validation with whitespace schema name."""
        columns = [
            TDbOracleColumn(name="ID", data_type="NUMBER", position=1),
        ]

        table = TDbOracleTable(
            name="TEST_TABLE",
            schema_name="   ",
            columns=columns,
        )

        result = table.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_SCHEMA_NAME_EMPTY in result.error

    def test_table_validation_no_columns(self) -> None:
        """Test table validation with no columns."""
        table = TDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[],
        )

        result = table.validate_domain_rules()
        assert result.is_failure
        assert "Table must have at least one column" in result.error

    def test_table_validation_invalid_column(self) -> None:
        """Test table validation with invalid column."""
        invalid_column = TDbOracleColumn(
            name="",  # Invalid empty name
            data_type="VARCHAR2",
            position=1,
        )

        table = TDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[invalid_column],
        )

        result = table.validate_domain_rules()
        assert result.is_failure
        assert "Column" in result.error

    def test_get_column_found(self) -> None:
        """Test getting column by name when found."""
        column1 = TDbOracleColumn(name="ID", data_type="NUMBER", position=1)
        column2 = TDbOracleColumn(name="NAME", data_type="VARCHAR2", position=2)

        table = TDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[column1, column2],
        )

        found_column = table.get_column("NAME")
        assert found_column is not None
        assert found_column.name == "NAME"
        assert found_column.data_type == "VARCHAR2"

    def test_get_column_case_insensitive(self) -> None:
        """Test getting column by name is case insensitive."""
        column = TDbOracleColumn(name="ID", data_type="NUMBER", position=1)

        table = TDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[column],
        )

        found_column = table.get_column("id")
        assert found_column is not None
        assert found_column.name == "ID"

    def test_get_column_not_found(self) -> None:
        """Test getting column by name when not found."""
        column = TDbOracleColumn(name="ID", data_type="NUMBER", position=1)

        table = TDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[column],
        )

        found_column = table.get_column("NONEXISTENT")
        assert found_column is None

    def test_column_names_property(self) -> None:
        """Test column names property."""
        columns = [
            TDbOracleColumn(name="ID", data_type="NUMBER", position=1),
            TDbOracleColumn(name="NAME", data_type="VARCHAR2", position=2),
            TDbOracleColumn(name="EMAIL", data_type="VARCHAR2", position=3),
        ]

        table = TDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=columns,
        )

        column_names = table.column_names
        assert column_names == ["ID", "NAME", "EMAIL"]

    def test_qualified_name_property(self) -> None:
        """Test qualified name property."""
        columns = [
            TDbOracleColumn(name="ID", data_type="NUMBER", position=1),
        ]

        table = TDbOracleTable(
            name="EMPLOYEES",
            schema_name="HR",
            columns=columns,
        )

        assert table.qualified_name == "HR.EMPLOYEES"

    def test_primary_key_columns_property(self) -> None:
        """Test primary key columns property."""
        columns = [
            TDbOracleColumn(
                name="ID", data_type="NUMBER", position=1, is_primary_key=True,
            ),
            TDbOracleColumn(
                name="NAME", data_type="VARCHAR2", position=2, is_primary_key=False,
            ),
            TDbOracleColumn(
                name="CODE", data_type="VARCHAR2", position=3, is_primary_key=True,
            ),
        ]

        table = TDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=columns,
        )

        pk_columns = table.primary_key_columns
        assert len(pk_columns) == 2
        assert pk_columns[0].name == "ID"
        assert pk_columns[1].name == "CODE"

    def test_foreign_key_columns_property(self) -> None:
        """Test foreign key columns property."""
        columns = [
            TDbOracleColumn(
                name="ID", data_type="NUMBER", position=1, is_foreign_key=False,
            ),
            TDbOracleColumn(
                name="DEPT_ID", data_type="NUMBER", position=2, is_foreign_key=True,
            ),
            TDbOracleColumn(
                name="MANAGER_ID", data_type="NUMBER", position=3, is_foreign_key=True,
            ),
        ]

        table = TDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=columns,
        )

        fk_columns = table.foreign_key_columns
        assert len(fk_columns) == 2
        assert fk_columns[0].name == "DEPT_ID"
        assert fk_columns[1].name == "MANAGER_ID"


class TestTDbOracleSchema:
    """Test TDbOracleSchema type."""

    def test_schema_creation_valid(self) -> None:
        """Test valid schema creation."""
        column = TDbOracleColumn(name="ID", data_type="NUMBER", position=1)
        table = TDbOracleTable(
            name="EMPLOYEES",
            schema_name="HR",
            columns=[column],
        )

        now = datetime.now(UTC)
        schema = TDbOracleSchema(
            name="HR",
            tables=[table],
            created_date=now,
            default_tablespace="USERS",
        )

        assert schema.name == "HR"
        assert len(schema.tables) == 1
        assert schema.created_date == now
        assert schema.default_tablespace == "USERS"

    def test_schema_validation_success(self) -> None:
        """Test successful schema validation."""
        column = TDbOracleColumn(name="ID", data_type="NUMBER", position=1)
        table = TDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[column],
        )

        schema = TDbOracleSchema(
            name="TEST_SCHEMA",
            tables=[table],
        )

        result = schema.validate_domain_rules()
        assert result.is_success

    def test_schema_validation_empty_name(self) -> None:
        """Test schema validation with empty name."""
        schema = TDbOracleSchema(
            name="",
            tables=[],
        )

        result = schema.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_SCHEMA_NAME_EMPTY in result.error

    def test_schema_validation_whitespace_name(self) -> None:
        """Test schema validation with whitespace name."""
        schema = TDbOracleSchema(
            name="   ",
            tables=[],
        )

        result = schema.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_SCHEMA_NAME_EMPTY in result.error

    def test_schema_validation_invalid_table(self) -> None:
        """Test schema validation with invalid table."""
        invalid_table = TDbOracleTable(
            name="",  # Invalid empty name
            schema_name="TEST_SCHEMA",
            columns=[],
        )

        schema = TDbOracleSchema(
            name="TEST_SCHEMA",
            tables=[invalid_table],
        )

        result = schema.validate_domain_rules()
        assert result.is_failure
        assert "Table" in result.error

    def test_get_table_found(self) -> None:
        """Test getting table by name when found."""
        column = TDbOracleColumn(name="ID", data_type="NUMBER", position=1)
        table1 = TDbOracleTable(name="EMPLOYEES", schema_name="HR", columns=[column])
        table2 = TDbOracleTable(name="DEPARTMENTS", schema_name="HR", columns=[column])

        schema = TDbOracleSchema(
            name="HR",
            tables=[table1, table2],
        )

        found_table = schema.get_table("DEPARTMENTS")
        assert found_table is not None
        assert found_table.name == "DEPARTMENTS"

    def test_get_table_case_insensitive(self) -> None:
        """Test getting table by name is case insensitive."""
        column = TDbOracleColumn(name="ID", data_type="NUMBER", position=1)
        table = TDbOracleTable(name="EMPLOYEES", schema_name="HR", columns=[column])

        schema = TDbOracleSchema(
            name="HR",
            tables=[table],
        )

        found_table = schema.get_table("employees")
        assert found_table is not None
        assert found_table.name == "EMPLOYEES"

    def test_get_table_not_found(self) -> None:
        """Test getting table by name when not found."""
        column = TDbOracleColumn(name="ID", data_type="NUMBER", position=1)
        table = TDbOracleTable(name="EMPLOYEES", schema_name="HR", columns=[column])

        schema = TDbOracleSchema(
            name="HR",
            tables=[table],
        )

        found_table = schema.get_table("NONEXISTENT")
        assert found_table is None

    def test_table_count_property(self) -> None:
        """Test table count property."""
        column = TDbOracleColumn(name="ID", data_type="NUMBER", position=1)
        tables = [
            TDbOracleTable(name="EMPLOYEES", schema_name="HR", columns=[column]),
            TDbOracleTable(name="DEPARTMENTS", schema_name="HR", columns=[column]),
            TDbOracleTable(name="LOCATIONS", schema_name="HR", columns=[column]),
        ]

        schema = TDbOracleSchema(
            name="HR",
            tables=tables,
        )

        assert schema.table_count == 3

    def test_total_columns_property(self) -> None:
        """Test total columns property."""
        table1_columns = [
            TDbOracleColumn(name="ID", data_type="NUMBER", position=1),
            TDbOracleColumn(name="NAME", data_type="VARCHAR2", position=2),
        ]
        table2_columns = [
            TDbOracleColumn(name="DEPT_ID", data_type="NUMBER", position=1),
            TDbOracleColumn(name="DEPT_NAME", data_type="VARCHAR2", position=2),
            TDbOracleColumn(name="LOCATION", data_type="VARCHAR2", position=3),
        ]

        tables = [
            TDbOracleTable(name="EMPLOYEES", schema_name="HR", columns=table1_columns),
            TDbOracleTable(
                name="DEPARTMENTS", schema_name="HR", columns=table2_columns,
            ),
        ]

        schema = TDbOracleSchema(
            name="HR",
            tables=tables,
        )

        assert schema.total_columns == 5  # 2 + 3


class TestTDbOracleQueryResult:
    """Test TDbOracleQueryResult type."""

    def test_query_result_creation_valid(self) -> None:
        """Test valid query result creation."""
        rows = [
            (1, "John", "Doe"),
            (2, "Jane", "Smith"),
        ]
        columns = ["ID", "FIRST_NAME", "LAST_NAME"]

        result = TDbOracleQueryResult(
            rows=rows,
            columns=columns,
            row_count=2,
            execution_time_ms=125.5,
        )

        assert result.rows == rows
        assert result.columns == columns
        assert result.row_count == 2
        assert result.execution_time_ms == 125.5

    def test_query_result_validation_success(self) -> None:
        """Test successful query result validation."""
        result = TDbOracleQueryResult(
            rows=[(1, "John"), (2, "Jane")],
            columns=["ID", "NAME"],
            row_count=2,
            execution_time_ms=100.0,
        )

        validation_result = result.validate_domain_rules()
        assert validation_result.is_success

    def test_query_result_validation_row_count_mismatch(self) -> None:
        """Test query result validation with row count mismatch."""
        result = TDbOracleQueryResult(
            rows=[(1, "John"), (2, "Jane")],
            columns=["ID", "NAME"],
            row_count=3,  # Mismatch: actual rows = 2, claimed = 3
            execution_time_ms=100.0,
        )

        validation_result = result.validate_domain_rules()
        assert validation_result.is_failure
        assert "Row count mismatch" in validation_result.error

    def test_query_result_validation_negative_execution_time(self) -> None:
        """Test query result validation with negative execution time."""
        result = TDbOracleQueryResult(
            rows=[(1, "John")],
            columns=["ID", "NAME"],
            row_count=1,
            execution_time_ms=-10.0,  # Invalid negative time
        )

        validation_result = result.validate_domain_rules()
        assert validation_result.is_failure
        assert "Execution time cannot be negative" in validation_result.error

    def test_to_dict_list_with_data(self) -> None:
        """Test converting rows to list of dictionaries with data."""
        rows = [
            (1, "John", "john@example.com"),
            (2, "Jane", "jane@example.com"),
        ]
        columns = ["ID", "NAME", "EMAIL"]

        result = TDbOracleQueryResult(
            rows=rows,
            columns=columns,
            row_count=2,
            execution_time_ms=100.0,
        )

        dict_list = result.to_dict_list()
        expected = [
            {"ID": 1, "NAME": "John", "EMAIL": "john@example.com"},
            {"ID": 2, "NAME": "Jane", "EMAIL": "jane@example.com"},
        ]

        assert dict_list == expected

    def test_to_dict_list_no_columns(self) -> None:
        """Test converting rows to list of dictionaries with no columns."""
        result = TDbOracleQueryResult(
            rows=[(1, "John"), (2, "Jane")],
            columns=[],  # No columns defined
            row_count=2,
            execution_time_ms=100.0,
        )

        dict_list = result.to_dict_list()
        assert dict_list == []

    def test_to_dict_list_empty_result(self) -> None:
        """Test converting empty result to list of dictionaries."""
        result = TDbOracleQueryResult(
            rows=[],
            columns=["ID", "NAME"],
            row_count=0,
            execution_time_ms=50.0,
        )

        dict_list = result.to_dict_list()
        assert dict_list == []

    def test_is_empty_property_true(self) -> None:
        """Test is_empty property when result is empty."""
        result = TDbOracleQueryResult(
            rows=[],
            columns=["ID", "NAME"],
            row_count=0,
            execution_time_ms=50.0,
        )

        assert result.is_empty

    def test_is_empty_property_false(self) -> None:
        """Test is_empty property when result has data."""
        result = TDbOracleQueryResult(
            rows=[(1, "John")],
            columns=["ID", "NAME"],
            row_count=1,
            execution_time_ms=50.0,
        )

        assert not result.is_empty


class TestTDbOracleConnectionStatus:
    """Test TDbOracleConnectionStatus type."""

    def test_connection_status_creation_valid(self) -> None:
        """Test valid connection status creation."""
        now = datetime.now(UTC)
        status = TDbOracleConnectionStatus(
            is_connected=True,
            host="localhost",
            port=1521,
            database="ORCLCDB",
            username="hr",
            last_check=now,
            error_message=None,
        )

        assert status.is_connected
        assert status.host == "localhost"
        assert status.port == 1521
        assert status.database == "ORCLCDB"
        assert status.username == "hr"
        assert status.last_check == now
        assert status.error_message is None

    def test_connection_status_validation_success(self) -> None:
        """Test successful connection status validation."""
        status = TDbOracleConnectionStatus(
            is_connected=True,
            host="oracle.example.com",
            port=1521,
            database="PROD",
            username="app_user",
            last_check=datetime.now(UTC),
        )

        result = status.validate_domain_rules()
        assert result.is_success

    def test_connection_status_validation_empty_host(self) -> None:
        """Test connection status validation with empty host."""
        status = TDbOracleConnectionStatus(
            is_connected=False,
            host="",
            port=1521,
            database="PROD",
            username="app_user",
            last_check=datetime.now(UTC),
        )

        result = status.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_HOST_EMPTY in result.error

    def test_connection_status_validation_whitespace_host(self) -> None:
        """Test connection status validation with whitespace host."""
        status = TDbOracleConnectionStatus(
            is_connected=False,
            host="   ",
            port=1521,
            database="PROD",
            username="app_user",
            last_check=datetime.now(UTC),
        )

        result = status.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_HOST_EMPTY in result.error

    def test_connection_status_validation_invalid_port_zero(self) -> None:
        """Test connection status validation with zero port."""
        status = TDbOracleConnectionStatus(
            is_connected=False,
            host="localhost",
            port=0,
            database="PROD",
            username="app_user",
            last_check=datetime.now(UTC),
        )

        result = status.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_PORT_INVALID in result.error

    def test_connection_status_validation_invalid_port_negative(self) -> None:
        """Test connection status validation with negative port."""
        status = TDbOracleConnectionStatus(
            is_connected=False,
            host="localhost",
            port=-1,
            database="PROD",
            username="app_user",
            last_check=datetime.now(UTC),
        )

        result = status.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_PORT_INVALID in result.error

    def test_connection_status_validation_invalid_port_too_high(self) -> None:
        """Test connection status validation with port too high."""
        status = TDbOracleConnectionStatus(
            is_connected=False,
            host="localhost",
            port=MAX_PORT + 1,  # 65536
            database="PROD",
            username="app_user",
            last_check=datetime.now(UTC),
        )

        result = status.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_PORT_INVALID in result.error

    def test_connection_status_validation_max_port(self) -> None:
        """Test connection status validation with maximum valid port."""
        status = TDbOracleConnectionStatus(
            is_connected=True,
            host="localhost",
            port=MAX_PORT,  # 65535
            database="PROD",
            username="app_user",
            last_check=datetime.now(UTC),
        )

        result = status.validate_domain_rules()
        assert result.is_success

    def test_connection_status_validation_empty_username(self) -> None:
        """Test connection status validation with empty username."""
        status = TDbOracleConnectionStatus(
            is_connected=False,
            host="localhost",
            port=1521,
            database="PROD",
            username="",
            last_check=datetime.now(UTC),
        )

        result = status.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_USERNAME_EMPTY in result.error

    def test_connection_status_validation_whitespace_username(self) -> None:
        """Test connection status validation with whitespace username."""
        status = TDbOracleConnectionStatus(
            is_connected=False,
            host="localhost",
            port=1521,
            database="PROD",
            username="   ",
            last_check=datetime.now(UTC),
        )

        result = status.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_USERNAME_EMPTY in result.error

    def test_connection_string_property(self) -> None:
        """Test connection string property."""
        status = TDbOracleConnectionStatus(
            is_connected=True,
            host="oracle.example.com",
            port=1521,
            database="ORCLCDB",
            username="hr",
            last_check=datetime.now(UTC),
        )

        expected = "hr@oracle.example.com:1521/ORCLCDB"
        assert status.connection_string == expected

    def test_connection_status_with_error(self) -> None:
        """Test connection status with error message."""
        status = TDbOracleConnectionStatus(
            is_connected=False,
            host="invalid.host",
            port=1521,
            database="PROD",
            username="app_user",
            last_check=datetime.now(UTC),
            error_message="Connection timeout",
        )

        assert not status.is_connected
        assert status.error_message == "Connection timeout"

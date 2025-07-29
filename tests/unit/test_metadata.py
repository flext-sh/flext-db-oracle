"""Comprehensive tests for metadata module."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock

from flext_db_oracle.constants import (
    ERROR_MSG_COLUMN_ID_INVALID,
    ERROR_MSG_COLUMN_NAME_EMPTY,
    ERROR_MSG_DATA_TYPE_EMPTY,
    ERROR_MSG_SCHEMA_NAME_EMPTY,
    ERROR_MSG_TABLE_NAME_EMPTY,
)
from flext_db_oracle.metadata import (
    FlextDbOracleColumn,
    FlextDbOracleMetadataManager,
    FlextDbOracleSchema,
    FlextDbOracleTable,
)


class TestFlextDbOracleColumn:
    """Test FlextDbOracleColumn class."""

    def test_column_creation_valid(self) -> None:
        """Test valid column creation."""
        column = FlextDbOracleColumn(
            name="EMPLOYEE_ID",
            data_type="NUMBER",
            nullable=False,
            default_value=None,
            data_length=None,
            data_precision=6,
            data_scale=0,
            column_id=1,
            comments="Employee unique identifier",
        )

        assert column.name == "EMPLOYEE_ID"
        assert column.data_type == "NUMBER"
        assert not column.nullable
        assert column.data_precision == 6
        assert column.data_scale == 0
        assert column.column_id == 1
        assert column.comments == "Employee unique identifier"

    def test_column_validation_success(self) -> None:
        """Test successful column validation."""
        column = FlextDbOracleColumn(
            name="FIRST_NAME",
            data_type="VARCHAR2",
            column_id=2,
        )

        result = column.validate_domain_rules()
        assert result.is_success
        assert result.data is None

    def test_column_validation_empty_name(self) -> None:
        """Test column validation with empty name."""
        column = FlextDbOracleColumn(
            name="",
            data_type="VARCHAR2",
            column_id=1,
        )

        result = column.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_COLUMN_NAME_EMPTY in result.error

    def test_column_validation_whitespace_name(self) -> None:
        """Test column validation with whitespace name."""
        column = FlextDbOracleColumn(
            name="   ",
            data_type="VARCHAR2",
            column_id=1,
        )

        result = column.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_COLUMN_NAME_EMPTY in result.error

    def test_column_validation_empty_data_type(self) -> None:
        """Test column validation with empty data type."""
        column = FlextDbOracleColumn(
            name="TEST_COL",
            data_type="",
            column_id=1,
        )

        result = column.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_DATA_TYPE_EMPTY in result.error

    def test_column_validation_whitespace_data_type(self) -> None:
        """Test column validation with whitespace data type."""
        column = FlextDbOracleColumn(
            name="TEST_COL",
            data_type="   ",
            column_id=1,
        )

        result = column.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_DATA_TYPE_EMPTY in result.error

    def test_column_validation_invalid_column_id_zero(self) -> None:
        """Test column validation with zero column_id."""
        column = FlextDbOracleColumn(
            name="TEST_COL",
            data_type="VARCHAR2",
            column_id=0,
        )

        result = column.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_COLUMN_ID_INVALID in result.error

    def test_column_validation_invalid_column_id_negative(self) -> None:
        """Test column validation with negative column_id."""
        column = FlextDbOracleColumn(
            name="TEST_COL",
            data_type="VARCHAR2",
            column_id=-1,
        )

        result = column.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_COLUMN_ID_INVALID in result.error

    def test_full_type_definition_varchar(self) -> None:
        """Test full type definition for VARCHAR2."""
        column = FlextDbOracleColumn(
            name="NAME",
            data_type="VARCHAR2",
            data_length=100,
            column_id=1,
        )

        assert column.full_type_definition == "VARCHAR2(100)"

    def test_full_type_definition_number_with_scale(self) -> None:
        """Test full type definition for NUMBER with precision and scale."""
        column = FlextDbOracleColumn(
            name="SALARY",
            data_type="NUMBER",
            data_precision=10,
            data_scale=2,
            column_id=1,
        )

        assert column.full_type_definition == "NUMBER(10,2)"

    def test_full_type_definition_number_without_scale(self) -> None:
        """Test full type definition for NUMBER with precision only."""
        column = FlextDbOracleColumn(
            name="ID",
            data_type="NUMBER",
            data_precision=10,
            column_id=1,
        )

        assert column.full_type_definition == "NUMBER(10)"

    def test_full_type_definition_basic_type(self) -> None:
        """Test full type definition for basic type."""
        column = FlextDbOracleColumn(
            name="CREATED",
            data_type="DATE",
            column_id=1,
        )

        assert column.full_type_definition == "DATE"


class TestFlextDbOracleTable:
    """Test FlextDbOracleTable class."""

    def test_table_creation_valid(self) -> None:
        """Test valid table creation."""
        columns = [
            FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1),
            FlextDbOracleColumn(name="NAME", data_type="VARCHAR2", column_id=2),
        ]

        now = datetime.now(UTC)
        table = FlextDbOracleTable(
            name="EMPLOYEES",
            schema_name="HR",
            columns=columns,
            row_count=1000,
            size_mb=50.5,
            comments="Employee table",
            created_date=now,
        )

        assert table.name == "EMPLOYEES"
        assert table.schema_name == "HR"
        assert len(table.columns) == 2
        assert table.row_count == 1000
        assert table.size_mb == 50.5
        assert table.comments == "Employee table"
        assert table.created_date == now

    def test_table_validation_success(self) -> None:
        """Test successful table validation."""
        columns = [
            FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1),
        ]

        table = FlextDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=columns,
        )

        result = table.validate_domain_rules()
        assert result.is_success

    def test_table_validation_empty_name(self) -> None:
        """Test table validation with empty name."""
        columns = [
            FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1),
        ]

        table = FlextDbOracleTable(
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
            FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1),
        ]

        table = FlextDbOracleTable(
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
            FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1),
        ]

        table = FlextDbOracleTable(
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
            FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1),
        ]

        table = FlextDbOracleTable(
            name="TEST_TABLE",
            schema_name="   ",
            columns=columns,
        )

        result = table.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_SCHEMA_NAME_EMPTY in result.error

    def test_table_validation_no_columns(self) -> None:
        """Test table validation with no columns."""
        table = FlextDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[],
        )

        result = table.validate_domain_rules()
        assert result.is_failure
        assert "Table must have at least one column" in result.error

    def test_table_validation_invalid_column(self) -> None:
        """Test table validation with invalid column."""
        invalid_column = FlextDbOracleColumn(
            name="",  # Invalid empty name
            data_type="VARCHAR2",
            column_id=1,
        )

        table = FlextDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[invalid_column],
        )

        result = table.validate_domain_rules()
        assert result.is_failure
        assert "Column" in result.error

    def test_get_column_by_name_found(self) -> None:
        """Test getting column by name when found."""
        column1 = FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1)
        column2 = FlextDbOracleColumn(name="NAME", data_type="VARCHAR2", column_id=2)

        table = FlextDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[column1, column2],
        )

        found_column = table.get_column_by_name("NAME")
        assert found_column is not None
        assert found_column.name == "NAME"
        assert found_column.data_type == "VARCHAR2"

    def test_get_column_by_name_case_insensitive(self) -> None:
        """Test getting column by name is case insensitive."""
        column = FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1)

        table = FlextDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[column],
        )

        found_column = table.get_column_by_name("id")
        assert found_column is not None
        assert found_column.name == "ID"

    def test_get_column_by_name_not_found(self) -> None:
        """Test getting column by name when not found."""
        column = FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1)

        table = FlextDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[column],
        )

        found_column = table.get_column_by_name("NONEXISTENT")
        assert found_column is None

    def test_column_names_property(self) -> None:
        """Test column names property."""
        columns = [
            FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1),
            FlextDbOracleColumn(name="NAME", data_type="VARCHAR2", column_id=2),
            FlextDbOracleColumn(name="EMAIL", data_type="VARCHAR2", column_id=3),
        ]

        table = FlextDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=columns,
        )

        column_names = table.column_names
        assert column_names == ["ID", "NAME", "EMAIL"]


class TestFlextDbOracleSchema:
    """Test FlextDbOracleSchema class."""

    def test_schema_creation_valid(self) -> None:
        """Test valid schema creation."""
        column = FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1)
        table = FlextDbOracleTable(
            name="EMPLOYEES",
            schema_name="HR",
            columns=[column],
        )

        now = datetime.now(UTC)
        schema = FlextDbOracleSchema(
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
        column = FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1)
        table = FlextDbOracleTable(
            name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            columns=[column],
        )

        schema = FlextDbOracleSchema(
            name="TEST_SCHEMA",
            tables=[table],
        )

        result = schema.validate_domain_rules()
        assert result.is_success

    def test_schema_validation_empty_name(self) -> None:
        """Test schema validation with empty name."""
        schema = FlextDbOracleSchema(
            name="",
            tables=[],
        )

        result = schema.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_SCHEMA_NAME_EMPTY in result.error

    def test_schema_validation_whitespace_name(self) -> None:
        """Test schema validation with whitespace name."""
        schema = FlextDbOracleSchema(
            name="   ",
            tables=[],
        )

        result = schema.validate_domain_rules()
        assert result.is_failure
        assert ERROR_MSG_SCHEMA_NAME_EMPTY in result.error

    def test_schema_validation_invalid_table(self) -> None:
        """Test schema validation with invalid table."""
        invalid_table = FlextDbOracleTable(
            name="",  # Invalid empty name
            schema_name="TEST_SCHEMA",
            columns=[],
        )

        schema = FlextDbOracleSchema(
            name="TEST_SCHEMA",
            tables=[invalid_table],
        )

        result = schema.validate_domain_rules()
        assert result.is_failure
        assert "Table" in result.error

    def test_get_table_by_name_found(self) -> None:
        """Test getting table by name when found."""
        column = FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1)
        table1 = FlextDbOracleTable(
            name="EMPLOYEES", schema_name="HR", columns=[column],
        )
        table2 = FlextDbOracleTable(
            name="DEPARTMENTS", schema_name="HR", columns=[column],
        )

        schema = FlextDbOracleSchema(
            name="HR",
            tables=[table1, table2],
        )

        found_table = schema.get_table_by_name("DEPARTMENTS")
        assert found_table is not None
        assert found_table.name == "DEPARTMENTS"

    def test_get_table_by_name_case_insensitive(self) -> None:
        """Test getting table by name is case insensitive."""
        column = FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1)
        table = FlextDbOracleTable(name="EMPLOYEES", schema_name="HR", columns=[column])

        schema = FlextDbOracleSchema(
            name="HR",
            tables=[table],
        )

        found_table = schema.get_table_by_name("employees")
        assert found_table is not None
        assert found_table.name == "EMPLOYEES"

    def test_get_table_by_name_not_found(self) -> None:
        """Test getting table by name when not found."""
        column = FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1)
        table = FlextDbOracleTable(name="EMPLOYEES", schema_name="HR", columns=[column])

        schema = FlextDbOracleSchema(
            name="HR",
            tables=[table],
        )

        found_table = schema.get_table_by_name("NONEXISTENT")
        assert found_table is None

    def test_table_count_property(self) -> None:
        """Test table count property."""
        column = FlextDbOracleColumn(name="ID", data_type="NUMBER", column_id=1)
        tables = [
            FlextDbOracleTable(name="EMPLOYEES", schema_name="HR", columns=[column]),
            FlextDbOracleTable(name="DEPARTMENTS", schema_name="HR", columns=[column]),
            FlextDbOracleTable(name="LOCATIONS", schema_name="HR", columns=[column]),
        ]

        schema = FlextDbOracleSchema(
            name="HR",
            tables=tables,
        )

        assert schema.table_count == 3


class TestFlextDbOracleMetadataManager:
    """Test FlextDbOracleMetadataManager class."""

    def test_manager_initialization(self) -> None:
        """Test metadata manager initialization."""
        mock_connection = MagicMock()
        manager = FlextDbOracleMetadataManager(mock_connection)

        assert manager._connection is mock_connection
        assert manager._logger is not None

    def test_get_table_metadata_success(self) -> None:
        """Test successful table metadata retrieval."""
        mock_connection = MagicMock()

        # Mock column info response
        column_data = [
            {
                "column_name": "ID",
                "data_type": "NUMBER",
                "nullable": False,
                "default_value": None,
                "data_length": None,
                "data_precision": 10,
                "data_scale": 0,
                "column_id": 1,
                "comments": None,
            },
            {
                "column_name": "NAME",
                "data_type": "VARCHAR2",
                "nullable": True,
                "default_value": None,
                "data_length": 100,
                "data_precision": None,
                "data_scale": None,
                "column_id": 2,
                "comments": "Employee name",
            },
        ]

        from flext_core import FlextResult

        mock_connection.get_column_info.return_value = FlextResult.ok(column_data)

        manager = FlextDbOracleMetadataManager(mock_connection)
        result = manager.get_table_metadata("EMPLOYEES", "HR")

        assert result.is_success
        assert result.data is not None
        table = result.data
        assert table.name == "EMPLOYEES"
        assert table.schema_name == "HR"
        assert len(table.columns) == 2
        assert table.columns[0].name == "ID"
        assert table.columns[1].name == "NAME"

    def test_get_table_metadata_connection_failure(self) -> None:
        """Test table metadata retrieval with connection failure."""
        mock_connection = MagicMock()

        from flext_core import FlextResult

        mock_connection.get_column_info.return_value = FlextResult.fail(
            "Connection failed",
        )

        manager = FlextDbOracleMetadataManager(mock_connection)
        result = manager.get_table_metadata("EMPLOYEES", "HR")

        assert result.is_failure
        assert "Failed to get columns: Connection failed" in result.error

    def test_get_table_metadata_no_schema(self) -> None:
        """Test table metadata retrieval without schema."""
        mock_connection = MagicMock()

        column_data = [
            {
                "column_name": "ID",
                "data_type": "NUMBER",
                "nullable": False,
                "default_value": None,
                "data_length": None,
                "data_precision": 10,
                "data_scale": 0,
                "column_id": 1,
                "comments": None,
            },
        ]

        from flext_core import FlextResult

        mock_connection.get_column_info.return_value = FlextResult.ok(column_data)

        manager = FlextDbOracleMetadataManager(mock_connection)
        result = manager.get_table_metadata("EMPLOYEES")

        assert result.is_success
        assert result.data is not None
        table = result.data
        assert table.schema_name == "USER"

    def test_get_table_metadata_exception_handling(self) -> None:
        """Test table metadata retrieval exception handling."""
        mock_connection = MagicMock()
        mock_connection.get_column_info.side_effect = ValueError("Test error")

        manager = FlextDbOracleMetadataManager(mock_connection)
        result = manager.get_table_metadata("EMPLOYEES", "HR")

        assert result.is_failure
        assert "Failed to get table metadata: Test error" in result.error

    def test_get_schema_metadata_success(self) -> None:
        """Test successful schema metadata retrieval."""
        mock_connection = MagicMock()

        # Mock table names response
        table_names = ["EMPLOYEES", "DEPARTMENTS"]

        # Mock column data for each table
        employee_columns = [
            {
                "column_name": "ID",
                "data_type": "NUMBER",
                "nullable": False,
                "default_value": None,
                "data_length": None,
                "data_precision": 10,
                "data_scale": 0,
                "column_id": 1,
                "comments": None,
            },
        ]

        dept_columns = [
            {
                "column_name": "DEPT_ID",
                "data_type": "NUMBER",
                "nullable": False,
                "default_value": None,
                "data_length": None,
                "data_precision": 10,
                "data_scale": 0,
                "column_id": 1,
                "comments": None,
            },
        ]

        from flext_core import FlextResult

        mock_connection.get_table_names.return_value = FlextResult.ok(table_names)
        mock_connection.get_column_info.side_effect = [
            FlextResult.ok(employee_columns),
            FlextResult.ok(dept_columns),
        ]

        manager = FlextDbOracleMetadataManager(mock_connection)
        result = manager.get_schema_metadata("HR")

        assert result.is_success
        assert result.data is not None
        schema = result.data
        assert schema.name == "HR"
        assert len(schema.tables) == 2

    def test_get_schema_metadata_table_names_failure(self) -> None:
        """Test schema metadata retrieval with table names failure."""
        mock_connection = MagicMock()

        from flext_core import FlextResult

        mock_connection.get_table_names.return_value = FlextResult.fail(
            "Connection failed",
        )

        manager = FlextDbOracleMetadataManager(mock_connection)
        result = manager.get_schema_metadata("HR")

        assert result.is_failure
        assert "Failed to get tables: Connection failed" in result.error

    def test_get_schema_metadata_some_table_failures(self) -> None:
        """Test schema metadata retrieval with some table failures."""
        mock_connection = MagicMock()

        # Mock table names response
        table_names = ["EMPLOYEES", "DEPARTMENTS"]

        # Mock successful column data for first table, failure for second
        employee_columns = [
            {
                "column_name": "ID",
                "data_type": "NUMBER",
                "nullable": False,
                "default_value": None,
                "data_length": None,
                "data_precision": 10,
                "data_scale": 0,
                "column_id": 1,
                "comments": None,
            },
        ]

        from flext_core import FlextResult

        mock_connection.get_table_names.return_value = FlextResult.ok(table_names)
        mock_connection.get_column_info.side_effect = [
            FlextResult.ok(employee_columns),
            FlextResult.fail("Table not found"),  # Second table fails
        ]

        manager = FlextDbOracleMetadataManager(mock_connection)
        result = manager.get_schema_metadata("HR")

        assert result.is_success
        assert result.data is not None
        schema = result.data
        assert schema.name == "HR"
        assert len(schema.tables) == 1  # Only successful table included

    def test_get_schema_metadata_exception_handling(self) -> None:
        """Test schema metadata retrieval exception handling."""
        mock_connection = MagicMock()
        mock_connection.get_table_names.side_effect = ValueError("Test error")

        manager = FlextDbOracleMetadataManager(mock_connection)
        result = manager.get_schema_metadata("HR")

        assert result.is_failure
        assert "Failed to get schema metadata: Test error" in result.error

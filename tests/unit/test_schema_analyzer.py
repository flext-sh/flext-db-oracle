"""Comprehensive unit tests for Oracle schema analyzer.

Tests the schema analysis functionality with proper pytest structure,
mocking, and comprehensive coverage of edge cases and error conditions.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from flext_core import FlextResult

from flext_db_oracle.schema.analyzer import SchemaAnalyzer


@pytest.fixture
def mock_connection_service() -> AsyncMock:
    """Create mock connection service for tests."""
    return AsyncMock()


@pytest.fixture
def schema_analyzer(mock_connection_service: AsyncMock) -> SchemaAnalyzer:
    """Create SchemaAnalyzer instance with mock connection."""
    return SchemaAnalyzer(mock_connection_service)


@pytest.fixture
def sample_table_data() -> list[list[Any]]:
    """Sample table data for testing."""
    return [
        ["EMPLOYEES", "USERS", "VALID", 100, 50, 2048],
        ["DEPARTMENTS", "USERS", "VALID", 10, 5, 1024],
    ]


@pytest.fixture
def sample_column_data() -> list[list[Any]]:
    """Sample column data for testing."""
    return [
        ["EMPLOYEE_ID", "NUMBER", 22, 10, 0, "N", 1, None],
        ["FIRST_NAME", "VARCHAR2", 50, None, None, "Y", 2, None],
        ["LAST_NAME", "VARCHAR2", 50, None, None, "N", 3, "UNKNOWN"],
        ["SALARY", "NUMBER", 22, 8, 2, "Y", 4, "0"],
    ]


class TestSchemaAnalyzer:
    """Test cases for SchemaAnalyzer class."""

    async def test_analyze_schema_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test successful schema analysis."""
        # Mock current schema
        mock_connection_service.execute_query.side_effect = [
            FlextResult.ok(MagicMock(rows=[["TEST_SCHEMA"]])),  # current schema
            FlextResult.ok(MagicMock(rows=[])),  # tables
            FlextResult.ok(MagicMock(rows=[])),  # views
            FlextResult.ok(MagicMock(rows=[])),  # sequences
            FlextResult.ok(MagicMock(rows=[])),  # procedures
        ]

        result = await schema_analyzer.analyze_schema()

        assert result.success
        assert result.data["schema_name"] == "TEST_SCHEMA"
        assert result.data["total_objects"] == 0

    async def test_analyze_schema_with_explicit_name(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test schema analysis with explicit schema name."""
        mock_connection_service.execute_query.side_effect = [
            FlextResult.ok(MagicMock(rows=[])),  # tables
            FlextResult.ok(MagicMock(rows=[])),  # views
            FlextResult.ok(MagicMock(rows=[])),  # sequences
            FlextResult.ok(MagicMock(rows=[])),  # procedures
        ]

        result = await schema_analyzer.analyze_schema("EXPLICIT_SCHEMA")

        assert result.success
        assert result.data["schema_name"] == "EXPLICIT_SCHEMA"

    async def test_analyze_schema_connection_failure(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test schema analysis with connection failure."""
        mock_connection_service.execute_query.return_value = FlextResult.fail(
            "Connection failed",
        )

        result = await schema_analyzer.analyze_schema()

        assert not result.success
        assert "Connection failed" in result.error

    async def test_get_tables_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
        sample_table_data: list[list[Any]],
    ) -> None:
        """Test successful table retrieval."""
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=sample_table_data),
        )

        result = await schema_analyzer.get_tables("TEST_SCHEMA")

        assert result.success
        tables = result.data
        assert len(tables) == 2
        assert tables[0]["name"] == "EMPLOYEES"
        assert tables[0]["num_rows"] == 100
        assert tables[1]["name"] == "DEPARTMENTS"

    async def test_get_tables_empty_result(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test table retrieval with empty result."""
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=[]),
        )

        result = await schema_analyzer.get_tables("TEST_SCHEMA")

        assert result.success
        assert result.data == []

    async def test_get_tables_query_failure(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test table retrieval with query failure."""
        mock_connection_service.execute_query.return_value = FlextResult.fail(
            "Query failed",
        )

        result = await schema_analyzer.get_tables("TEST_SCHEMA")

        assert not result.success
        assert "Query failed" in result.error

    async def test_get_table_columns_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
        sample_column_data: list[list[Any]],
    ) -> None:
        """Test successful column retrieval."""
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=sample_column_data),
        )

        result = await schema_analyzer.get_table_columns("TEST_SCHEMA", "EMPLOYEES")

        assert result.success
        columns = result.data
        assert len(columns) == 4
        assert columns[0]["name"] == "EMPLOYEE_ID"
        assert columns[0]["data_type"] == "NUMBER"
        assert columns[0]["nullable"] is False  # "N" converts to False
        assert columns[1]["nullable"] is True  # "Y" converts to True
        assert columns[2]["default_value"] == "UNKNOWN"
        assert columns[3]["default_value"] == "0"

    async def test_get_table_columns_no_results(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test column retrieval with no results."""
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=[]),
        )

        result = await schema_analyzer.get_table_columns("TEST_SCHEMA", "NONEXISTENT")

        assert result.success
        assert result.data == []

    async def test_get_views_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test successful view retrieval."""
        view_data = [
            ["EMP_VIEW", 1024, "SELECT * FROM employees"],
            ["DEPT_VIEW", 512, "SELECT * FROM departments"],
        ]
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=view_data),
        )

        result = await schema_analyzer.get_views("TEST_SCHEMA")

        assert result.success
        views = result.data
        assert len(views) == 2
        assert views[0]["name"] == "EMP_VIEW"
        assert views[0]["text_length"] == 1024

    async def test_get_sequences_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test successful sequence retrieval."""
        sequence_data = [
            ["EMP_SEQ", 1, 999999, 1, "N"],
            ["DEPT_SEQ", 1, 999999, 1, "N"],
        ]
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=sequence_data),
        )

        result = await schema_analyzer.get_sequences("TEST_SCHEMA")

        assert result.success
        sequences = result.data
        assert len(sequences) == 2
        assert sequences[0]["name"] == "EMP_SEQ"
        assert sequences[0]["increment_by"] == 1

    async def test_get_procedures_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test successful procedure retrieval."""
        procedure_data = [
            ["GET_EMPLOYEE", "PROCEDURE", "VALID", "2024-01-01", "2024-01-01"],
            ["CALC_SALARY", "FUNCTION", "VALID", "2024-01-01", "2024-01-01"],
        ]
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=procedure_data),
        )

        result = await schema_analyzer.get_procedures("TEST_SCHEMA")

        assert result.success
        procedures = result.data
        assert len(procedures) == 2
        assert procedures[0]["name"] == "GET_EMPLOYEE"
        assert procedures[0]["type"] == "PROCEDURE"
        assert procedures[1]["type"] == "FUNCTION"

    async def test_get_table_constraints_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test successful constraint retrieval."""
        constraint_data = [
            ["EMP_PK", "P", None, None, None, "ENABLED"],
            ["EMP_DEPT_FK", "R", None, "DEPT_PK", "CASCADE", "ENABLED"],
            ["EMP_SALARY_CHK", "C", "salary > 0", None, None, "ENABLED"],
        ]
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=constraint_data),
        )

        result = await schema_analyzer.get_table_constraints("TEST_SCHEMA", "EMPLOYEES")

        assert result.success
        constraints = result.data
        assert len(constraints) == 3
        assert constraints[0]["name"] == "EMP_PK"
        assert constraints[0]["type"] == "P"  # Primary key
        assert constraints[1]["type"] == "R"  # Foreign key
        assert constraints[2]["search_condition"] == "salary > 0"

    async def test_get_table_indexes_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test successful index retrieval."""
        index_data = [
            ["EMP_PK", "NORMAL", "UNIQUE", None, "VALID", 100, 10, 100],
            ["EMP_NAME_IDX", "NORMAL", "NONUNIQUE", None, "VALID", 100, 15, 95],
        ]
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=index_data),
        )

        result = await schema_analyzer.get_table_indexes("TEST_SCHEMA", "EMPLOYEES")

        assert result.success
        indexes = result.data
        assert len(indexes) == 2
        assert indexes[0]["name"] == "EMP_PK"
        assert indexes[0]["uniqueness"] == "UNIQUE"
        assert indexes[1]["uniqueness"] == "NONUNIQUE"

    async def test_get_detailed_table_info_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test successful detailed table info retrieval."""
        # Mock sequence of calls: tables, columns, constraints, indexes
        mock_connection_service.execute_query.side_effect = [
            FlextResult.ok(
                MagicMock(rows=[["EMPLOYEES", "USERS", "VALID", 100, 50, 2048]]),
            ),  # tables
            FlextResult.ok(
                MagicMock(rows=[["EMPLOYEE_ID", "NUMBER", 22, 10, 0, "N", 1, None]]),
            ),  # columns
            FlextResult.ok(
                MagicMock(rows=[["EMP_PK", "P", None, None, None, "ENABLED"]]),
            ),  # constraints
            FlextResult.ok(
                MagicMock(
                    rows=[["EMP_PK", "NORMAL", "UNIQUE", None, "VALID", 100, 10, 100]],
                ),
            ),  # indexes
        ]

        result = await schema_analyzer.get_detailed_table_info(
            "TEST_SCHEMA",
            "EMPLOYEES",
        )

        assert result.success
        table_info = result.data
        assert table_info["name"] == "EMPLOYEES"
        assert table_info["column_count"] == 1
        assert table_info["constraint_count"] == 1
        assert table_info["index_count"] == 1

    async def test_get_detailed_table_info_table_not_found(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test detailed table info when table doesn't exist."""
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=[]),
        )

        result = await schema_analyzer.get_detailed_table_info(
            "TEST_SCHEMA",
            "NONEXISTENT",
        )

        assert not result.success
        assert "Table list is empty" in result.error

    async def test_analyze_schema_size_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test successful schema size analysis."""
        size_data = [
            [1024.5, 10, "TABLE"],
            [512.25, 5, "INDEX"],
        ]
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=size_data),
        )

        result = await schema_analyzer.analyze_schema_size("TEST_SCHEMA")

        assert result.success
        size_analysis = result.data
        assert size_analysis["schema_name"] == "TEST_SCHEMA"
        assert size_analysis["total_size_mb"] == 1536.75  # 1024.5 + 512.25
        assert size_analysis["total_segments"] == 15  # 10 + 5
        assert len(size_analysis["segments"]) == 2

    async def test_analyze_schema_size_fallback_to_user_segments(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test schema size analysis fallback to user_segments."""
        # First call fails (dba_segments), second succeeds (user_segments)
        mock_connection_service.execute_query.side_effect = [
            FlextResult.fail("Access denied to dba_segments"),
            FlextResult.ok(MagicMock(rows=[[512.0, 5, "TABLE"]])),
        ]

        result = await schema_analyzer.analyze_schema_size("TEST_SCHEMA")

        assert result.success
        assert result.data["total_size_mb"] == 512.0

    async def test_get_complete_schema_metadata_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test complete schema metadata creation."""
        # Mock the complex sequence of calls
        mock_connection_service.execute_query.side_effect = [
            FlextResult.ok(MagicMock(rows=[["TEST_SCHEMA"]])),  # current schema
            FlextResult.ok(MagicMock(rows=[])),  # tables (for analyze_schema)
            FlextResult.ok(MagicMock(rows=[])),  # views (for analyze_schema)
            FlextResult.ok(MagicMock(rows=[])),  # sequences (for analyze_schema)
            FlextResult.ok(MagicMock(rows=[])),  # procedures (for analyze_schema)
            FlextResult.fail("No size data"),  # schema size (fails gracefully)
            FlextResult.fail("Fallback also fails"),  # fallback query also fails
        ]

        result = await schema_analyzer.get_complete_schema_metadata()

        assert result.success
        schema_metadata = result.data
        assert schema_metadata.name == "TEST_SCHEMA"
        assert (
            schema_metadata.total_size_mb == 0.0
        )  # Failed size analysis defaults to 0

    async def test_get_constraint_columns_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test constraint column retrieval."""
        column_data = [
            ["EMPLOYEE_ID"],
            ["DEPARTMENT_ID"],
        ]
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=column_data),
        )

        result = await schema_analyzer.get_constraint_columns(
            "TEST_SCHEMA",
            "EMP_DEPT_FK",
        )

        assert result.success
        columns = result.data
        assert columns == ["EMPLOYEE_ID", "DEPARTMENT_ID"]

    async def test_get_index_columns_success(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test index column retrieval."""
        column_data = [
            ["LAST_NAME"],
            ["FIRST_NAME"],
        ]
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=column_data),
        )

        result = await schema_analyzer.get_index_columns("TEST_SCHEMA", "EMP_NAME_IDX")

        assert result.success
        columns = result.data
        assert columns == ["LAST_NAME", "FIRST_NAME"]

    async def test_exception_handling(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test exception handling in analyzer methods."""
        # Mock connection service to raise exception
        mock_connection_service.execute_query.side_effect = Exception("Database error")

        result = await schema_analyzer.analyze_schema("TEST_SCHEMA")

        assert not result.success
        assert "Failed to analyze schema components" in result.error

    async def test_empty_current_schema(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test handling of empty current schema."""
        mock_connection_service.execute_query.return_value = FlextResult.ok(
            MagicMock(rows=[]),
        )

        result = await schema_analyzer.analyze_schema()

        assert not result.success
        assert "No current schema found" in result.error

    async def test_query_result_data_none(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test handling when query result data is None."""
        mock_connection_service.execute_query.return_value = FlextResult.ok(None)

        result = await schema_analyzer.get_tables("TEST_SCHEMA")

        assert not result.success
        assert "Query result is empty" in result.error


@pytest.mark.asyncio
class TestSchemaAnalyzerIntegration:
    """Integration-style tests for SchemaAnalyzer."""

    async def test_full_schema_analysis_workflow(
        self,
        schema_analyzer: SchemaAnalyzer,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Test complete schema analysis workflow."""
        # Mock complete workflow
        mock_connection_service.execute_query.side_effect = [
            FlextResult.ok(MagicMock(rows=[["TEST_SCHEMA"]])),  # current schema
            FlextResult.ok(
                MagicMock(rows=[["EMPLOYEES", "USERS", "VALID", 100, 50, 2048]]),
            ),  # tables
            FlextResult.ok(
                MagicMock(rows=[["EMP_VIEW", 1024, "SELECT * FROM employees"]]),
            ),  # views
            FlextResult.ok(
                MagicMock(rows=[["EMP_SEQ", 1, 999999, 1, "N"]]),
            ),  # sequences
            FlextResult.ok(
                MagicMock(
                    rows=[
                        [
                            "GET_EMPLOYEE",
                            "PROCEDURE",
                            "VALID",
                            "2024-01-01",
                            "2024-01-01",
                        ],
                    ],
                ),
            ),  # procedures
        ]

        result = await schema_analyzer.analyze_schema()

        assert result.success
        data = result.data
        assert data["schema_name"] == "TEST_SCHEMA"
        assert data["total_objects"] == 4  # 1 table + 1 view + 1 sequence + 1 procedure
        assert len(data["tables"]) == 1
        assert len(data["views"]) == 1
        assert len(data["sequences"]) == 1
        assert len(data["procedures"]) == 1

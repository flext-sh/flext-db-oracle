"""Tests for domain models module.

Tests for Oracle domain entities and value objects.
"""

from __future__ import annotations

from datetime import UTC, datetime

from flext_db_oracle.domain.models import (
    FlextDbOracleConnectionStatus,
    FlextDbOracleQueryResult,
    FlextDbOracleSchemaInfo,
    FlextDbOracleTableMetadata,
)


class TestFlextDbOracleConnectionStatus:
    """Test Oracle connection status model."""

    def test_connection_status_creation_success(self) -> None:
        """Test successful connection status creation."""
        status = FlextDbOracleConnectionStatus(
            is_connected=True,
            host="testhost",
            port=1521,
            database="testdb",
            username="testuser",
        )

        assert status.is_connected is True
        assert status.host == "testhost"
        assert status.port == 1521
        assert status.database == "testdb"
        assert status.username == "testuser"

    def test_connection_status_creation_disconnected(self) -> None:
        """Test disconnected connection status creation."""
        status = FlextDbOracleConnectionStatus(
            is_connected=False,
            host="testhost",
            port=1521,
            database="testdb",
            username="testuser",
            error_message="Connection failed",
        )

        assert status.is_connected is False
        assert status.host == "testhost"
        assert status.port == 1521
        assert status.database == "testdb"
        assert status.username == "testuser"
        assert status.error_message == "Connection failed"

    def test_connection_status_properties(self) -> None:
        """Test connection status properties."""
        status = FlextDbOracleConnectionStatus(
            is_connected=True,
            host="testhost",
            port=1521,
            database="testdb",
            username="testuser",
        )

        # Test connection_info property
        connection_info = status.connection_info
        assert "testuser" in connection_info
        assert "testhost" in connection_info
        assert "1521" in connection_info
        assert "testdb" in connection_info

    def test_connection_status_validation(self) -> None:
        """Test connection status validation."""
        # Should work with all required fields
        status = FlextDbOracleConnectionStatus(
            is_connected=True,
            host="host",
            port=1521,
            database="db",
            username="user",
        )
        assert status.is_connected is True

        # Test with error message
        status_with_error = FlextDbOracleConnectionStatus(
            is_connected=False,
            host="host",
            port=1521,
            database="db",
            username="user",
            error_message="Failed to connect",
        )
        assert status_with_error.is_connected is False
        assert status_with_error.error_message == "Failed to connect"


class TestFlextDbOracleQueryResult:
    """Test Oracle query result model."""

    def test_query_result_creation(self) -> None:
        """Test query result creation with data."""
        result = FlextDbOracleQueryResult(
            rows=[(1, "test"), (2, "data")],
            columns=["id", "name"],
            row_count=2,
            execution_time_ms=0.5,
        )

        assert len(result.rows) == 2
        assert result.rows[0] == (1, "test")
        assert result.rows[1] == (2, "data")
        assert result.columns == ["id", "name"]
        assert result.row_count == 2
        assert result.execution_time_ms == 0.5

    def test_query_result_empty(self) -> None:
        """Test empty query result."""
        result = FlextDbOracleQueryResult(
            rows=[],
            columns=[],
            row_count=0,
            execution_time_ms=0.1,
        )

        assert len(result.rows) == 0
        assert len(result.columns) == 0
        assert result.row_count == 0
        assert result.execution_time_ms == 0.1

    def test_query_result_defaults(self) -> None:
        """Test query result with default values."""
        result = FlextDbOracleQueryResult(
            rows=[(1,)],
            columns=["col1"],
        )

        assert len(result.rows) == 1
        assert result.columns == ["col1"]
        assert result.row_count == 0  # Default value
        assert result.execution_time_ms == 0.0  # Default value

    def test_query_result_properties(self) -> None:
        """Test query result computed properties."""
        result = FlextDbOracleQueryResult(
            rows=[(1, "a"), (2, "b"), (3, "c")],
            columns=["id", "value"],
            row_count=3,
            execution_time_ms=1.2,
        )

        # Test basic properties
        assert len(result.rows) == 3
        assert len(result.columns) == 2
        assert result.row_count == 3

        # Test additional properties if they exist
        if hasattr(result, "is_empty"):
            assert result.is_empty is False

        if hasattr(result, "column_count"):
            assert result.column_count == 2

    def test_query_result_large_dataset(self) -> None:
        """Test query result with larger dataset."""
        rows = [(i, f"value_{i}") for i in range(100)]
        result = FlextDbOracleQueryResult(
            rows=rows,
            columns=["id", "value"],
            row_count=100,
            execution_time_ms=2.5,
        )

        assert len(result.rows) == 100
        assert result.rows[0] == (0, "value_0")
        assert result.rows[99] == (99, "value_99")
        assert result.row_count == 100


class TestFlextDbOracleTableMetadata:
    """Test Oracle table metadata model."""

    def test_table_metadata_creation(self) -> None:
        """Test table metadata creation."""
        metadata = FlextDbOracleTableMetadata(
            table_name="TEST_TABLE",
            schema_name="TEST_SCHEMA",
            row_count=1000,
            created_date=datetime(2023, 1, 1, tzinfo=UTC),
        )

        assert metadata.table_name == "TEST_TABLE"
        assert metadata.schema_name == "TEST_SCHEMA"
        assert metadata.row_count == 1000
        assert metadata.created_date == datetime(2023, 1, 1, tzinfo=UTC)

    def test_table_metadata_minimal(self) -> None:
        """Test table metadata with minimal required fields."""
        metadata = FlextDbOracleTableMetadata(
            table_name="SIMPLE_TABLE",
            schema_name="SCHEMA",
        )

        assert metadata.table_name == "SIMPLE_TABLE"
        assert metadata.schema_name == "SCHEMA"
        assert metadata.row_count is None  # Default
        assert metadata.created_date is None

    def test_table_metadata_properties(self) -> None:
        """Test table metadata computed properties."""
        metadata = FlextDbOracleTableMetadata(
            table_name="LARGE_TABLE",
            schema_name="PROD_SCHEMA",
            row_count=5000000,
        )

        # Test full table name property
        assert "PROD_SCHEMA" in metadata.full_name
        assert "LARGE_TABLE" in metadata.full_name
        assert metadata.full_name == "PROD_SCHEMA.LARGE_TABLE"

    def test_table_metadata_validation(self) -> None:
        """Test table metadata validation."""
        # Should work with valid data
        metadata = FlextDbOracleTableMetadata(
            table_name="VALID_TABLE",
            schema_name="VALID_SCHEMA",
            row_count=500,
        )

        assert metadata.table_name == "VALID_TABLE"
        assert metadata.schema_name == "VALID_SCHEMA"
        assert metadata.row_count == 500


class TestFlextDbOracleSchemaInfo:
    """Test Oracle schema info model."""

    def test_schema_info_creation(self) -> None:
        """Test schema info creation."""
        schema_info = FlextDbOracleSchemaInfo(
            name="TEST_SCHEMA",
            table_count=15,
        )

        assert schema_info.name == "TEST_SCHEMA"
        assert schema_info.table_count == 15

    def test_schema_info_minimal(self) -> None:
        """Test schema info with minimal data."""
        schema_info = FlextDbOracleSchemaInfo(
            name="MINIMAL_SCHEMA",
        )

        assert schema_info.name == "MINIMAL_SCHEMA"
        assert schema_info.table_count == 0

    def test_schema_info_properties(self) -> None:
        """Test schema info computed properties."""
        # Create some test tables
        table1 = FlextDbOracleTableMetadata(
            table_name="TABLE1",
            schema_name="FULL_SCHEMA",
        )
        table2 = FlextDbOracleTableMetadata(
            table_name="TABLE2",
            schema_name="FULL_SCHEMA",
        )

        schema_info = FlextDbOracleSchemaInfo(
            name="FULL_SCHEMA",
            table_count=2,
            tables=[table1, table2],
        )

        # Test table_names property
        assert schema_info.table_names == ["TABLE1", "TABLE2"]
        assert len(schema_info.tables) == 2

    def test_schema_info_empty(self) -> None:
        """Test empty schema info."""
        schema_info = FlextDbOracleSchemaInfo(
            name="EMPTY_SCHEMA",
            table_count=0,
        )

        assert schema_info.name == "EMPTY_SCHEMA"
        assert schema_info.table_count == 0
        assert len(schema_info.tables) == 0
        assert schema_info.table_names == []


class TestModelIntegration:
    """Test integration between different models."""

    def test_models_work_together(self) -> None:
        """Test that models can be used together."""
        # Create connection status
        status = FlextDbOracleConnectionStatus(
            is_connected=True,
            host="localhost",
            port=1521,
            database="TESTDB",
            username="testuser",
        )

        # Create query result
        result = FlextDbOracleQueryResult(
            rows=[(1, "table1"), (2, "table2")],
            columns=["id", "name"],
            row_count=2,
        )

        # Create table metadata
        metadata = FlextDbOracleTableMetadata(
            table_name="table1",
            schema_name="TESTSCHEMA",
            row_count=100,
        )

        # Create schema info
        schema_info = FlextDbOracleSchemaInfo(
            name="TESTSCHEMA",
            table_count=2,
            tables=[metadata],
        )

        # Test that they all work together
        assert status.is_connected
        assert len(result.rows) == 2
        assert metadata.table_name == "table1"
        assert schema_info.name == "TESTSCHEMA"

        # Test that schema names match
        assert metadata.schema_name == schema_info.name
        assert "table1" in schema_info.table_names

    def test_model_serialization(self) -> None:
        """Test that models can be serialized."""
        status = FlextDbOracleConnectionStatus(
            is_connected=True,
            host="localhost",
            port=1521,
            database="testdb",
            username="testuser",
        )

        # Test dict conversion if available
        if hasattr(status, "model_dump"):
            status_dict = status.model_dump()
            assert isinstance(status_dict, dict)
            assert status_dict["is_connected"] is True
        elif hasattr(status, "dict"):
            status_dict = status.dict()
            assert isinstance(status_dict, dict)
            assert status_dict["is_connected"] is True

        # Test that we can create a new instance
        new_status = FlextDbOracleConnectionStatus(
            is_connected=False,
            host="localhost",
            port=1521,
            database="testdb",
            username="testuser",
        )
        assert new_status.is_connected is False

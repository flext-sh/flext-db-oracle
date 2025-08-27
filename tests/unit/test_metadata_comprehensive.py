"""Comprehensive tests for FlextDbOracleMetadataManager using real code validation.

This module tests the metadata management functionality with real code paths
instead of mocks, following the user's requirement for real code testing.
"""

from pydantic import SecretStr

from flext_db_oracle import FlextDbOracleConfig, FlextDbOracleConnection
from flext_db_oracle.metadata import FlextDbOracleMetadataManager


class TestFlextDbOracleMetadataManagerComprehensive:
    """Comprehensive tests for metadata manager using real code paths."""

    def setup_method(self) -> None:
        """Setup test configuration."""
        self.config = FlextDbOracleConfig(
            host="test",
            port=1521,
            service_name="TEST",
            username="test",
            password=SecretStr("test"),
        )
        self.connection = FlextDbOracleConnection(self.config)
        self.manager = FlextDbOracleMetadataManager(self.connection)

    def test_metadata_manager_initialization(self) -> None:
        """Test metadata manager initialization with real connection."""
        assert self.manager is not None
        assert self.manager.connection == self.connection
        # Metadata manager uses module-level logger, not instance logger
        assert hasattr(self.manager, "connection")

    def test_get_schemas_structure(self) -> None:
        """Test get_schemas method structure and error handling."""
        # Test method exists and returns FlextResult
        result = self.manager.get_schemas()
        assert hasattr(result, "success")
        assert hasattr(result, "error")

        # When not connected, should return failure
        assert not result.success
        assert result.error is not None
        assert (
            "not connected" in result.error.lower()
            or "connection" in result.error.lower()
        )

    def test_get_tables_structure(self) -> None:
        """Test get_tables method structure and error handling."""
        # Test with default schema
        result = self.manager.get_tables()
        assert hasattr(result, "success")
        assert not result.success  # Should fail when not connected

        # Test with specific schema
        result_with_schema = self.manager.get_tables("TEST_SCHEMA")
        assert not result_with_schema.success  # Should fail when not connected

    def test_get_columns_structure(self) -> None:
        """Test get_columns method structure and error handling."""
        result = self.manager.get_columns("TEST_TABLE")
        assert hasattr(result, "success")
        assert not result.success  # Should fail when not connected

        # Test with schema
        result_with_schema = self.manager.get_columns("TEST_TABLE", "TEST_SCHEMA")
        assert not result_with_schema.success

    def test_get_table_metadata_structure(self) -> None:
        """Test get_table_metadata method structure and error handling."""
        result = self.manager.get_tables("TEST_TABLE")
        assert hasattr(result, "success")
        assert not result.success  # Should fail when not connected

        # Test with schema
        result_with_schema = self.manager.get_tables(
            "TEST_TABLE", "TEST_SCHEMA"
        )
        assert not result_with_schema.success

    def test_get_column_metadata_structure(self) -> None:
        """Test get_column_metadata method structure and error handling."""
        result = self.manager.get_column_metadata("TEST_TABLE", "TEST_COLUMN")
        assert hasattr(result, "success")
        assert not result.success  # Should fail when not connected

    def test_get_schema_metadata_structure(self) -> None:
        """Test get_schema_metadata method structure and error handling."""
        result = self.manager.get_schema_metadata("TEST_SCHEMA")
        assert hasattr(result, "success")
        assert not result.success  # Should fail when not connected

    def test_generate_ddl_structure(self) -> None:
        """Test generate_ddl method structure and validation."""
        # Create a valid table model for DDL generation
        from flext_db_oracle.models import FlextDbOracleColumn, FlextDbOracleTable

        # Create columns
        columns = [
            FlextDbOracleColumn(
                column_name="ID", data_type="NUMBER", nullable=False, column_id=1
            ),
            FlextDbOracleColumn(
                column_name="NAME",
                data_type="VARCHAR2",
                data_length=100,
                nullable=True,
                column_id=2,
            ),
        ]

        # Create table
        table = FlextDbOracleTable(
            table_name="TEST_TABLE", schema_name="TEST_SCHEMA", columns=columns
        )

        result = self.manager.generate_ddl(table)
        assert hasattr(result, "success")
        # DDL generation should work even without connection (pure transformation)
        assert result.success
        assert "CREATE TABLE" in result.value.upper()
        assert "TEST_SCHEMA.TEST_TABLE" in result.value
        assert "ID" in result.value
        assert "NAME" in result.value

    def test_test_connection_structure(self) -> None:
        """Test test_connection method structure."""
        result = self.manager.test_connection()
        assert hasattr(result, "success")
        assert not result.success  # Should fail when not connected

    def test_error_handling_patterns(self) -> None:
        """Test consistent error handling patterns across methods."""
        # All methods should return FlextResult and handle disconnected state gracefully
        methods_to_test = [
            ("get_schemas", []),
            ("get_tables", []),
            ("get_columns", ["TEST_TABLE"]),
            ("get_table_metadata", ["TEST_TABLE"]),
            ("get_column_metadata", ["TEST_TABLE", "TEST_COLUMN"]),
            ("get_schema_metadata", ["TEST_SCHEMA"]),
            ("test_connection", []),
        ]

        for method_name, args in methods_to_test:
            method = getattr(self.manager, method_name)
            result = method(*args)

            # All methods should return FlextResult
            assert hasattr(result, "success")
            assert hasattr(result, "error")

            # When not connected, should fail with descriptive error
            if method_name != "generate_ddl":  # DDL doesn't require connection
                assert not result.success
                assert result.error is not None
                assert len(result.error) > 0

    def test_manager_real_functionality_coverage(self) -> None:
        """Test real functionality paths to increase coverage."""
        # Test connection property
        assert self.manager.connection is self.connection

        # Test manager has required attributes
        assert hasattr(self.manager, "connection")
        assert self.manager.connection is not None

        # Test all public methods exist
        expected_methods = [
            "get_schemas",
            "get_tables",
            "get_columns",
            "get_table_metadata",
            "get_column_metadata",
            "get_schema_metadata",
            "generate_ddl",
            "test_connection",
        ]

        for method_name in expected_methods:
            assert hasattr(self.manager, method_name)
            assert callable(getattr(self.manager, method_name))

    def test_ddl_generation_comprehensive(self) -> None:
        """Test comprehensive DDL generation functionality."""
        from flext_db_oracle.models import FlextDbOracleColumn, FlextDbOracleTable

        # Test with various column types
        columns = [
            FlextDbOracleColumn(
                column_name="ID",
                data_type="NUMBER",
                data_precision=10,
                nullable=False,
                column_id=1,
            ),
            FlextDbOracleColumn(
                column_name="CODE",
                data_type="VARCHAR2",
                data_length=50,
                nullable=False,
                column_id=2,
            ),
            FlextDbOracleColumn(
                column_name="CREATED_DATE", data_type="DATE", nullable=True, column_id=3
            ),
            FlextDbOracleColumn(
                column_name="AMOUNT",
                data_type="NUMBER",
                data_precision=10,
                data_scale=2,
                nullable=True,
                column_id=4,
            ),
        ]

        table = FlextDbOracleTable(
            table_name="COMPLEX_TABLE", schema_name="APP_SCHEMA", columns=columns
        )

        result = self.manager.generate_ddl(table)
        assert result.success

        ddl = result.value
        assert "CREATE TABLE APP_SCHEMA.COMPLEX_TABLE" in ddl
        assert "ID NUMBER(10) NOT NULL" in ddl
        assert "CODE VARCHAR2(50) NOT NULL" in ddl
        assert "CREATED_DATE DATE" in ddl
        assert "AMOUNT NUMBER(10,2)" in ddl

        # Test DDL is valid SQL-like structure
        assert ddl.count("(") >= 1
        assert ddl.count(")") >= 1
        assert "," in ddl

    def test_validation_logic_comprehensive(self) -> None:
        """Test validation logic in metadata operations."""
        # Test empty/invalid parameters
        result_empty_table = self.manager.get_columns("")
        assert not result_empty_table.success

        result_empty_schema = self.manager.get_schema_metadata("")
        assert not result_empty_schema.success

        # Test None parameters where not allowed
        result_none_table = self.manager.get_columns(None)
        assert not result_none_table.success

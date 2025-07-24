"""Comprehensive unit tests for Oracle database comparator.

Tests the database comparison functionality with proper pytest structure,
mocking, and comprehensive coverage of all comparison methods.
"""

import unittest
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from flext_core import FlextResult as ServiceResult
from src.flext_db_oracle.compare.comparator import (
    ComparisonConfig,
    DatabaseComparator,
)


@pytest.fixture
def mock_source_service() -> AsyncMock:
    """Create mock source connection service for tests."""
    return AsyncMock()


@pytest.fixture
def mock_target_service() -> AsyncMock:
    """Create mock target connection service for tests."""
    return AsyncMock()


@pytest.fixture
def mock_schema_differ() -> AsyncMock:
    """Create mock schema differ for tests."""
    return AsyncMock()


@pytest.fixture
def mock_data_differ() -> AsyncMock:
    """Create mock data differ for tests."""
    return AsyncMock()


@pytest.fixture
def sample_comparison_config() -> ComparisonConfig:
    """Create sample comparison configuration for tests."""
    return ComparisonConfig(
        include_schema=True,
        include_data=False,
        schema_objects=["tables", "views"],
        table_filters=["EMPLOYEES", "DEPARTMENTS"],
        exclude_tables=["TEMP_TABLE"],
        sample_size=1000,
    )


@pytest.fixture
def database_comparator(
    mock_source_service: AsyncMock,
    mock_target_service: AsyncMock,
    mock_schema_differ: AsyncMock,
    mock_data_differ: AsyncMock,
) -> DatabaseComparator:
    """Create DatabaseComparator instance with mock services."""
    return DatabaseComparator(
        source_service=mock_source_service,
        target_service=mock_target_service,
        schema_differ=mock_schema_differ,
        data_differ=mock_data_differ,
    )


class TestComparisonConfig:
    """Test cases for ComparisonConfig domain model."""

    def test_comparison_config_creation(self) -> None:
        """Test comparison configuration creation with valid parameters."""
        config = ComparisonConfig(
            include_schema=True,
            include_data=True,
            schema_objects=["tables", "views", "sequences"],
            table_filters=["EMP_%"],
            exclude_tables=["TEMP_%"],
            sample_size=500,
        )

        assert config.include_schema is True
        assert config.include_data is True
        assert config.schema_objects == ["tables", "views", "sequences"]
        assert config.table_filters == ["EMP_%"]
        assert config.exclude_tables == ["TEMP_%"]
        assert config.sample_size == 500

    def test_comparison_config_defaults(self) -> None:
        """Test comparison configuration with default values."""
        config = ComparisonConfig()

        assert config.include_schema is True
        assert config.include_data is False
        assert config.schema_objects == ["tables", "views", "sequences", "procedures"]
        assert config.table_filters == []
        assert config.exclude_tables == []
        assert config.sample_size is None

    def test_comparison_config_validation_success(self) -> None:
        """Test successful domain validation."""
        config = ComparisonConfig(
            schema_objects=["tables", "views", "indexes"],
            sample_size=100,
        )

        # Should not raise exception
        config.validate_domain_rules()

    def test_comparison_config_validation_empty_schema_objects(self) -> None:
        """Test validation failure with empty schema objects."""
        config = ComparisonConfig(schema_objects=[])

        with pytest.raises(ValueError, match="Schema objects list cannot be empty"):
            config.validate_domain_rules()

    def test_comparison_config_validation_invalid_schema_object(self) -> None:
        """Test validation failure with invalid schema object type."""
        config = ComparisonConfig(schema_objects=["tables", "invalid_object"])

        with pytest.raises(ValueError, match="Invalid schema object type: invalid_object"):
            config.validate_domain_rules()

    def test_comparison_config_validation_negative_sample_size(self) -> None:
        """Test validation failure with negative sample size."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="Input should be greater than or equal to 1"):
            ComparisonConfig(sample_size=-1)

    def test_comparison_config_validation_zero_sample_size(self) -> None:
        """Test validation failure with zero sample size."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="Input should be greater than or equal to 1"):
            ComparisonConfig(sample_size=0)


class TestDatabaseComparator:
    """Test cases for DatabaseComparator class."""

    def test_database_comparator_initialization(
        self,
        mock_source_service: AsyncMock,
        mock_target_service: AsyncMock,
        mock_schema_differ: AsyncMock,
        mock_data_differ: AsyncMock,
    ) -> None:
        """Test database comparator initialization."""
        comparator = DatabaseComparator(
            source_service=mock_source_service,
            target_service=mock_target_service,
            schema_differ=mock_schema_differ,
            data_differ=mock_data_differ,
        )

        assert comparator.source_service == mock_source_service
        assert comparator.target_service == mock_target_service
        assert comparator.schema_differ == mock_schema_differ
        assert comparator.data_differ == mock_data_differ

    def test_database_comparator_initialization_without_data_differ(
        self,
        mock_source_service: AsyncMock,
        mock_target_service: AsyncMock,
        mock_schema_differ: AsyncMock,
    ) -> None:
        """Test database comparator initialization without data differ."""
        comparator = DatabaseComparator(
            source_service=mock_source_service,
            target_service=mock_target_service,
            schema_differ=mock_schema_differ,
            data_differ=None,
        )

        assert comparator.data_differ is None

    async def test_compare_databases_schema_only_success(
        self,
        database_comparator: DatabaseComparator,
        sample_comparison_config: ComparisonConfig,
        mock_schema_differ: AsyncMock,
    ) -> None:
        """Test successful database comparison with schema only."""
        # Mock schema analysis results
        source_metadata = {"name": "SOURCE_SCHEMA", "tables": ["TABLE1", "TABLE2"]}
        target_metadata = {"name": "TARGET_SCHEMA", "tables": ["TABLE1", "TABLE3"]}

        with (
            unittest.mock.patch.object(
                database_comparator,
                "_get_schema_metadata",
                side_effect=[
                    ServiceResult.ok(source_metadata),
                    ServiceResult.ok(target_metadata),
                ],
            ),
        ):
            # Mock schema comparison result
            comparison_result = MagicMock()
            comparison_result.total_differences = 2
            mock_schema_differ.compare_schemas.return_value = ServiceResult.ok(
                comparison_result
            )

            result = await database_comparator.compare_databases(
                "SOURCE_SCHEMA", "TARGET_SCHEMA", sample_comparison_config
            )

            assert result.success
            assert result.data == comparison_result
            mock_schema_differ.compare_schemas.assert_called_once_with(
                source_metadata, target_metadata
            )

    async def test_compare_databases_schema_and_data_success(
        self, database_comparator: DatabaseComparator, mock_data_differ: AsyncMock
    ) -> None:
        """Test successful database comparison with schema and data."""
        config = ComparisonConfig(include_schema=True, include_data=True)

        # Mock schema analysis and comparison
        source_metadata = {"name": "SOURCE_SCHEMA", "tables": ["TABLE1"]}
        target_metadata = {"name": "TARGET_SCHEMA", "tables": ["TABLE1"]}
        schema_comparison_result = MagicMock()
        schema_comparison_result.total_differences = 0

        with (
            unittest.mock.patch.object(
                database_comparator,
                "_get_schema_metadata",
                side_effect=[
                    ServiceResult.ok(source_metadata),
                    ServiceResult.ok(target_metadata),
                ],
            ),
            unittest.mock.patch.object(
                database_comparator,
                "_compare_data",
                return_value=ServiceResult.ok({"data_differences": []}),
            ),
        ):
            database_comparator.schema_differ.compare_schemas.return_value = (
                ServiceResult.ok(schema_comparison_result)
            )

            result = await database_comparator.compare_databases(
                "SOURCE_SCHEMA", "TARGET_SCHEMA", config
            )

            assert result.success

    async def test_compare_databases_schema_metadata_failure(
        self,
        database_comparator: DatabaseComparator,
        sample_comparison_config: ComparisonConfig,
    ) -> None:
        """Test database comparison with schema metadata failure."""
        with unittest.mock.patch.object(
            database_comparator,
            "_get_schema_metadata",
            side_effect=[
                ServiceResult.fail("Source schema analysis failed"),
                ServiceResult.ok({"name": "TARGET"}),
            ],
        ):
            result = await database_comparator.compare_databases(
                "SOURCE_SCHEMA", "TARGET_SCHEMA", sample_comparison_config
            )

            assert not result.success
            assert "Failed to retrieve schema metadata" in result.error

    async def test_compare_databases_schema_comparison_failure(
        self,
        database_comparator: DatabaseComparator,
        sample_comparison_config: ComparisonConfig,
        mock_schema_differ: AsyncMock,
    ) -> None:
        """Test database comparison with schema comparison failure."""
        source_metadata = {"name": "SOURCE_SCHEMA"}
        target_metadata = {"name": "TARGET_SCHEMA"}

        with unittest.mock.patch.object(
            database_comparator,
            "_get_schema_metadata",
            side_effect=[
                ServiceResult.ok(source_metadata),
                ServiceResult.ok(target_metadata),
            ],
        ):
            mock_schema_differ.compare_schemas.return_value = ServiceResult.fail(
                "Schema comparison failed"
            )

            result = await database_comparator.compare_databases(
                "SOURCE_SCHEMA", "TARGET_SCHEMA", sample_comparison_config
            )

            assert not result.success
            assert "Schema comparison failed" in result.error

    async def test_compare_databases_data_comparison_failure(
        self, database_comparator: DatabaseComparator
    ) -> None:
        """Test database comparison with data comparison failure."""
        config = ComparisonConfig(include_schema=True, include_data=True)

        source_metadata = {"name": "SOURCE_SCHEMA"}
        target_metadata = {"name": "TARGET_SCHEMA"}
        schema_comparison_result = MagicMock()

        with (
            unittest.mock.patch.object(
                database_comparator,
                "_get_schema_metadata",
                side_effect=[
                    ServiceResult.ok(source_metadata),
                    ServiceResult.ok(target_metadata),
                ],
            ),
            unittest.mock.patch.object(
                database_comparator,
                "_compare_data",
                return_value=ServiceResult.fail("Data comparison failed"),
            ),
        ):
            database_comparator.schema_differ.compare_schemas.return_value = (
                ServiceResult.ok(schema_comparison_result)
            )

            result = await database_comparator.compare_databases(
                "SOURCE_SCHEMA", "TARGET_SCHEMA", config
            )

            assert not result.success
            assert "Data comparison failed" in result.error

    async def test_compare_databases_no_operations_performed(
        self, database_comparator: DatabaseComparator
    ) -> None:
        """Test database comparison with no operations configured."""
        config = ComparisonConfig(include_schema=False, include_data=False)

        result = await database_comparator.compare_databases(
            "SOURCE_SCHEMA", "TARGET_SCHEMA", config
        )

        assert not result.success
        assert "No comparison operations performed" in result.error

    async def test_compare_databases_exception_handling(
        self,
        database_comparator: DatabaseComparator,
        sample_comparison_config: ComparisonConfig,
    ) -> None:
        """Test database comparison exception handling."""
        with unittest.mock.patch.object(
            database_comparator,
            "_get_schema_metadata",
            side_effect=Exception("Unexpected error"),
        ):
            result = await database_comparator.compare_databases(
                "SOURCE_SCHEMA", "TARGET_SCHEMA", sample_comparison_config
            )

            assert not result.success
            assert "Schema comparison failed" in result.error

    async def test_get_schema_metadata_success(
        self, database_comparator: DatabaseComparator, mock_source_service: AsyncMock
    ) -> None:
        """Test successful schema metadata retrieval."""
        config = ComparisonConfig(schema_objects=["tables"])
        schema_data = {
            "name": "TEST_SCHEMA",
            "tables": ["TABLE1", "TABLE2"],
            "views": ["VIEW1"],
        }

        with unittest.mock.patch(
            "src.flext_db_oracle.compare.comparator.SchemaAnalyzer"
        ) as mock_analyzer_class:
            mock_analyzer = AsyncMock()
            mock_analyzer.analyze_schema.return_value = ServiceResult.ok(schema_data)
            mock_analyzer_class.return_value = mock_analyzer

            result = await database_comparator._get_schema_metadata(
                mock_source_service, "TEST_SCHEMA", config
            )

            assert result.success
            metadata = result.data
            assert metadata["name"] == "TEST_SCHEMA"
            assert "tables" in metadata
            mock_analyzer.analyze_schema.assert_called_once_with("TEST_SCHEMA")

    async def test_get_schema_metadata_analysis_failure(
        self, database_comparator: DatabaseComparator, mock_source_service: AsyncMock
    ) -> None:
        """Test schema metadata retrieval with analysis failure."""
        config = ComparisonConfig()

        with unittest.mock.patch(
            "src.flext_db_oracle.compare.comparator.SchemaAnalyzer"
        ) as mock_analyzer_class:
            mock_analyzer = AsyncMock()
            mock_analyzer.analyze_schema.return_value = ServiceResult.fail(
                "Schema analysis failed"
            )
            mock_analyzer_class.return_value = mock_analyzer

            result = await database_comparator._get_schema_metadata(
                mock_source_service, "TEST_SCHEMA", config
            )

            assert not result.success
            assert "Schema analysis failed" in result.error

    async def test_get_schema_metadata_empty_result(
        self, database_comparator: DatabaseComparator, mock_source_service: AsyncMock
    ) -> None:
        """Test schema metadata retrieval with empty result."""
        config = ComparisonConfig()

        with unittest.mock.patch(
            "src.flext_db_oracle.compare.comparator.SchemaAnalyzer"
        ) as mock_analyzer_class:
            mock_analyzer = AsyncMock()
            mock_analyzer.analyze_schema.return_value = ServiceResult.ok(None)
            mock_analyzer_class.return_value = mock_analyzer

            result = await database_comparator._get_schema_metadata(
                mock_source_service, "TEST_SCHEMA", config
            )

            assert not result.success
            assert "Schema analysis returned no metadata" in result.error

    async def test_compare_data_success(
        self, database_comparator: DatabaseComparator, mock_data_differ: AsyncMock
    ) -> None:
        """Test successful data comparison."""
        config = ComparisonConfig()
        schema_comparison = MagicMock()

        tables_to_compare = ["TABLE1", "TABLE2"]
        pk_columns = ["ID"]
        data_differences = [{"table": "TABLE1", "differences": 2}]

        with (
            unittest.mock.patch.object(
                database_comparator,
                "_get_comparable_tables",
                return_value=ServiceResult.ok(tables_to_compare),
            ),
            unittest.mock.patch.object(
                database_comparator,
                "_get_primary_key_columns",
                return_value=ServiceResult.ok(pk_columns),
            ),
        ):
            mock_data_differ.compare_table_data.return_value = ServiceResult.ok(
                data_differences
            )

            result = await database_comparator._compare_data(
                "SOURCE_SCHEMA", "TARGET_SCHEMA", config, schema_comparison
            )

            assert result.success
            result_data = result.data
            assert result_data["tables_compared"] == 2
            assert result_data["total_differences"] == 2

    async def test_compare_data_no_data_differ(
        self,
        mock_source_service: AsyncMock,
        mock_target_service: AsyncMock,
        mock_schema_differ: AsyncMock,
    ) -> None:
        """Test data comparison without data differ configured."""
        comparator = DatabaseComparator(
            source_service=mock_source_service,
            target_service=mock_target_service,
            schema_differ=mock_schema_differ,
            data_differ=None,
        )

        config = ComparisonConfig()
        result = await comparator._compare_data(
            "SOURCE_SCHEMA", "TARGET_SCHEMA", config, None
        )

        assert not result.success
        assert "Data differ not configured" in result.error

    async def test_compare_data_get_tables_failure(
        self, database_comparator: DatabaseComparator
    ) -> None:
        """Test data comparison with get tables failure."""
        config = ComparisonConfig()

        with unittest.mock.patch.object(
            database_comparator,
            "_get_comparable_tables",
            return_value=ServiceResult.fail("Failed to get tables"),
        ):
            result = await database_comparator._compare_data(
                "SOURCE_SCHEMA", "TARGET_SCHEMA", config, None
            )

            assert not result.success
            assert "Failed to get tables" in result.error

    async def test_compare_data_no_tables_to_compare(
        self, database_comparator: DatabaseComparator
    ) -> None:
        """Test data comparison with no tables to compare."""
        config = ComparisonConfig()

        with unittest.mock.patch.object(
            database_comparator,
            "_get_comparable_tables",
            return_value=ServiceResult.ok([]),
        ):
            result = await database_comparator._compare_data(
                "SOURCE_SCHEMA", "TARGET_SCHEMA", config, None
            )

            assert result.success
            assert result.data["data_differences"] == []

    async def test_compare_data_skip_table_without_primary_key(
        self, database_comparator: DatabaseComparator, mock_data_differ: AsyncMock
    ) -> None:
        """Test data comparison skipping tables without primary keys."""
        config = ComparisonConfig()
        tables_to_compare = ["TABLE1", "TABLE2"]

        with (
            unittest.mock.patch.object(
                database_comparator,
                "_get_comparable_tables",
                return_value=ServiceResult.ok(tables_to_compare),
            ),
            unittest.mock.patch.object(
                database_comparator,
                "_get_primary_key_columns",
                side_effect=[
                    ServiceResult.fail("No primary key"),  # TABLE1 - skip
                    ServiceResult.ok(["ID"]),  # TABLE2 - compare
                ],
            ),
        ):
            mock_data_differ.compare_table_data.return_value = ServiceResult.ok([])

            result = await database_comparator._compare_data(
                "SOURCE_SCHEMA", "TARGET_SCHEMA", config, None
            )

            assert result.success
            # Should only call compare_table_data once (for TABLE2)
            mock_data_differ.compare_table_data.assert_called_once()

    async def test_compare_data_exception_handling(
        self, database_comparator: DatabaseComparator
    ) -> None:
        """Test data comparison exception handling."""
        config = ComparisonConfig()

        with unittest.mock.patch.object(
            database_comparator,
            "_get_comparable_tables",
            side_effect=Exception("Unexpected error"),
        ):
            result = await database_comparator._compare_data(
                "SOURCE_SCHEMA", "TARGET_SCHEMA", config, None
            )

            assert not result.success
            assert "Data comparison failed" in result.error


@pytest.mark.asyncio
class TestDatabaseComparatorIntegration:
    """Integration-style tests for DatabaseComparator."""

    async def test_full_schema_comparison_workflow(
        self,
        mock_source_service: AsyncMock,
        mock_target_service: AsyncMock,
        mock_schema_differ: AsyncMock,
    ) -> None:
        """Test complete schema comparison workflow."""
        comparator = DatabaseComparator(
            source_service=mock_source_service,
            target_service=mock_target_service,
            schema_differ=mock_schema_differ,
            data_differ=None,
        )

        config = ComparisonConfig(
            include_schema=True,
            include_data=False,
            schema_objects=["tables", "views"],
        )

        # Mock comprehensive schema analysis
        source_schema = {
            "name": "SOURCE_SCHEMA",
            "tables": ["EMPLOYEES", "DEPARTMENTS"],
            "views": ["EMP_VIEW"],
            "total_objects": 3,
        }
        target_schema = {
            "name": "TARGET_SCHEMA",
            "tables": ["EMPLOYEES", "CONTRACTS"],
            "views": ["EMP_VIEW"],
            "total_objects": 3,
        }

        with unittest.mock.patch(
            "src.flext_db_oracle.compare.comparator.SchemaAnalyzer"
        ) as mock_analyzer_class:
            mock_analyzer = AsyncMock()
            mock_analyzer.analyze_schema.side_effect = [
                ServiceResult.ok(source_schema),
                ServiceResult.ok(target_schema),
            ]
            mock_analyzer_class.return_value = mock_analyzer

            # Mock schema comparison result
            comparison_result = MagicMock()
            comparison_result.total_differences = 2
            mock_schema_differ.compare_schemas.return_value = ServiceResult.ok(
                comparison_result
            )

            result = await comparator.compare_databases(
                "SOURCE_SCHEMA", "TARGET_SCHEMA", config
            )

            assert result.success
            assert result.data == comparison_result

            # Verify analyzer was called for both schemas
            assert mock_analyzer.analyze_schema.call_count == 2
            mock_analyzer.analyze_schema.assert_any_call("SOURCE_SCHEMA")
            mock_analyzer.analyze_schema.assert_any_call("TARGET_SCHEMA")

            # Verify schema comparison was called with correct metadata
            mock_schema_differ.compare_schemas.assert_called_once_with(
                source_schema, target_schema
            )

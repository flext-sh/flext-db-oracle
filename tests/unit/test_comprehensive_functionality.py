"""Comprehensive functionality tests for flext-infrastructure.databases.flext-db-oracle.

These tests exercise real code paths without requiring Oracle database connections.
They focus on testing business logic, configuration validation, and error handling.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from flext_db_oracle.application.services import (
    OracleConnectionService,
    OracleQueryService,
    OracleSchemaService,
)
from flext_db_oracle.config import OracleConfig
from flext_db_oracle.domain.models import OracleConnectionInfo, OracleQueryResult
from flext_db_oracle.maintenance.health import HealthChecker
from flext_db_oracle.schema.analyzer import SchemaAnalyzer
from flext_db_oracle.schema.ddl import DDLGenerator


class TestOracleConnectionService:
    """Test OracleConnectionService functionality."""

    def test_service_initialization(self) -> None:
        """Test service can be initialized with valid config."""
        config = OracleConfig(
            username="test_user",
            password="test_password",
            service_name="XE",
        )
        service = OracleConnectionService(config)

        assert service.config == config
        assert not service.is_pool_initialized
        assert not service.is_query_service_initialized

    @pytest.mark.asyncio
    async def test_initialize_pool_configuration(self) -> None:
        """Test pool initialization creates proper configuration."""
        config = OracleConfig(
            username="test_user",
            password="test_password",
            service_name="XE",
            pool_min_size=2,
            pool_max_size=10,
        )
        service = OracleConnectionService(config)

        with patch("oracledb.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_create_pool.return_value = mock_pool

            result = await service.initialize_pool()

            assert result.is_success
            pool_status = service.get_pool_status()
            assert pool_status["initialized"]
            assert pool_status["pool"] == mock_pool

            # Verify pool was created with correct parameters
            mock_create_pool.assert_called_once()
            call_kwargs = mock_create_pool.call_args[1]
            assert call_kwargs["min"] == 2
            assert call_kwargs["max"] == 10
            assert call_kwargs["user"] == "test_user"

    @pytest.mark.asyncio
    async def test_close_pool_success(self) -> None:
        """Test successful pool closure."""
        config = OracleConfig(
            username="test",
            password="test",
            service_name="XE",
        )
        service = OracleConnectionService(config)

        # Initialize pool first to test closure
        with patch("oracledb.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_create_pool.return_value = mock_pool
            await service.initialize_pool()

            result = await service.close_pool()

            assert result.is_success
            mock_pool.close.assert_called_once()
            assert not service.is_pool_initialized

    @pytest.mark.asyncio
    async def test_close_pool_error_handling(self) -> None:
        """Test pool closure error handling."""
        config = OracleConfig(
            username="test",
            password="test",
            service_name="XE",
        )
        service = OracleConnectionService(config)

        # Initialize pool first, then make close() raise exception
        with patch("oracledb.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_pool.close.side_effect = Exception("Pool close error")
            mock_create_pool.return_value = mock_pool

            await service.initialize_pool()
            result = await service.close_pool()

            assert not result.is_success
            assert "Connection pool closure failed" in result.error


class TestOracleQueryService:
    """Test OracleQueryService functionality."""

    def test_query_service_initialization(self) -> None:
        """Test query service initialization."""
        config = OracleConfig(
            username="test",
            password="test",
            service_name="XE",
        )
        conn_service = OracleConnectionService(config)
        query_service = OracleQueryService(conn_service)

        assert query_service.connection_service == conn_service


class TestSchemaAnalyzer:
    """Test SchemaAnalyzer functionality."""

    def test_analyzer_initialization(self) -> None:
        """Test analyzer can be initialized."""
        config = OracleConfig(
            username="test",
            password="test",
            service_name="XE",
        )
        conn_service = OracleConnectionService(config)
        analyzer = SchemaAnalyzer(conn_service)

        assert analyzer.connection_service == conn_service


class TestDDLGenerator:
    """Test DDL generator functionality."""

    def test_ddl_generator_initialization(self) -> None:
        """Test DDL generator initialization with different options."""
        generator = DDLGenerator(include_comments=True)
        assert hasattr(generator, "include_comments")

        generator_no_comments = DDLGenerator(include_comments=False)
        assert hasattr(generator_no_comments, "include_comments")


class TestHealthChecker:
    """Test health checker functionality."""

    def test_health_checker_initialization(self) -> None:
        """Test health checker initialization."""
        config = OracleConfig(
            username="test",
            password="test",
            service_name="XE",
        )
        conn_service = OracleConnectionService(config)
        health_checker = HealthChecker(conn_service)

        assert health_checker.connection_service == conn_service


class TestOracleSchemaService:
    """Test OracleSchemaService functionality."""

    def test_schema_service_initialization(self) -> None:
        """Test schema service initialization."""
        config = OracleConfig(
            username="test",
            password="test",
            service_name="XE",
        )
        conn_service = OracleConnectionService(config)
        query_service = OracleQueryService(conn_service)
        schema_service = OracleSchemaService(query_service)

        assert schema_service.query_service == query_service


class TestOracleConnectionInfo:
    """Test OracleConnectionInfo domain model."""

    def test_connection_info_creation(self) -> None:
        """Test connection info model creation."""
        connection_info = OracleConnectionInfo(
            host="localhost",
            port=1521,
            service_name="XE",
            username="test_user",
            password="test_password",
        )

        assert connection_info.host == "localhost"
        assert connection_info.port == 1521
        assert connection_info.service_name == "XE"
        assert connection_info.username == "test_user"
        assert connection_info.password == "test_password"


class TestServiceIntegration:
    """Test service integration patterns."""

    @pytest.mark.asyncio
    async def test_connection_service_with_query_service(self) -> None:
        """Test connection service integration with query service."""
        config = OracleConfig(
            username="test",
            password="test",
            service_name="XE",
        )
        conn_service = OracleConnectionService(config)

        # Initialize pool with mock
        with patch("oracledb.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_create_pool.return_value = mock_pool

            result = await conn_service.initialize_pool()
            assert result.is_success

            # Test that query service can be created after pool initialization
            query_service = OracleQueryService(conn_service)
            assert query_service.connection_service == conn_service

    def test_all_services_can_be_created_together(self) -> None:
        """Test that all services can be created together."""
        config = OracleConfig(
            username="test",
            password="test",
            service_name="XE",
        )
        conn_service = OracleConnectionService(config)

        # Create all services
        query_service = OracleQueryService(conn_service)
        schema_service = OracleSchemaService(query_service)
        analyzer = SchemaAnalyzer(conn_service)
        health_checker = HealthChecker(conn_service)

        # Verify they reference the correct services
        assert query_service.connection_service == conn_service
        assert schema_service.query_service == query_service
        assert analyzer.connection_service == conn_service
        assert health_checker.connection_service == conn_service


class TestConfigurationParsing:
    """Test configuration parsing and validation."""

    def test_oracle_config_valid_creation(self) -> None:
        """Test Oracle config creation with valid values."""
        config = OracleConfig(
            username="test_user",
            password="test_password",
            service_name="ORCL",
            host="localhost",
            port=1521,
        )

        assert config.username == "test_user"
        assert config.service_name == "ORCL"
        assert config.host == "localhost"
        assert config.port == 1521

    def test_oracle_config_connection_string_formatting(self) -> None:
        """Test connection string generation."""
        config = OracleConfig(
            username="user",
            password="pass",
            service_name="ORCL",
            host="dbserver",
            port=1521,
        )

        conn_string = config.connection_string
        assert "user" in conn_string
        assert "dbserver" in conn_string
        assert "1521" in conn_string
        assert "ORCL" in conn_string
        # Password should be masked
        assert "pass" not in conn_string

    def test_oracle_config_pool_settings(self) -> None:
        """Test connection pool configuration."""
        config = OracleConfig(
            username="user",
            password="pass",
            service_name="ORCL",
            pool_min_size=10,
            pool_max_size=50,
            pool_increment=5,
        )

        assert config.pool_min_size == 10
        assert config.pool_max_size == 50
        assert config.pool_increment == 5


class TestDomainModels:
    """Test domain model functionality."""

    def test_oracle_table_metadata_properties(self) -> None:
        """Test table metadata computed properties."""
        from flext_db_oracle.domain.models import OracleColumnInfo, OracleTableMetadata

        # Create columns with primary keys
        columns = [
            OracleColumnInfo(name="ID", data_type="NUMBER", is_primary_key=True),
            OracleColumnInfo(name="NAME", data_type="VARCHAR2", nullable=False),
            OracleColumnInfo(name="EMAIL", data_type="VARCHAR2", nullable=True),
        ]

        table = OracleTableMetadata(
            schema_name="HR",
            table_name="EMPLOYEES",
            columns=columns,
            row_count=1000,
        )

        assert table.full_name == "HR.EMPLOYEES"
        assert table.primary_key_columns == ["ID"]
        assert len(table.columns) == 3

    def test_oracle_query_result_methods(self) -> None:
        """Test query result utility methods."""
        result = OracleQueryResult(
            rows=[("John", 30), ("Jane", 25), ("Bob", 35)],
            row_count=3,
            columns=["name", "age"],
            execution_time_ms=150.5,
        )

        assert not result.is_empty
        assert result.get_column_values(0) == ["John", "Jane", "Bob"]
        assert result.get_column_values(1) == [30, 25, 35]

    def test_empty_oracle_query_result(self) -> None:
        """Test empty query result."""
        result = OracleQueryResult(
            rows=[],
            row_count=0,
            columns=["name", "age"],
            execution_time_ms=10.0,
        )

        assert result.is_empty
        assert result.get_column_values(0) == []

    def test_oracle_schema_info_properties(self) -> None:
        """Test schema info computed properties."""
        from flext_db_oracle.domain.models import OracleSchemaInfo, OracleTableMetadata

        tables = [
            OracleTableMetadata(schema_name="HR", table_name="EMPLOYEES"),
            OracleTableMetadata(schema_name="HR", table_name="DEPARTMENTS"),
        ]

        schema = OracleSchemaInfo(
            name="HR",
            tables=tables,
            table_count=2,
        )

        assert schema.table_names == ["EMPLOYEES", "DEPARTMENTS"]
        assert len(schema.tables) == 2

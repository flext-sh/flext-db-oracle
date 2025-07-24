"""Comprehensive unit tests for SQLAlchemy engine management.

Tests the SQLAlchemy engine functionality with proper pytest structure,
mocking, and comprehensive coverage of all engine management methods.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from flext_core import FlextResult
from sqlalchemy.exc import SQLAlchemyError
from src.flext_db_oracle.config import FlextDbOracleConfig
from src.flext_db_oracle.infrastructure.sqlalchemy_engine import (
    FlextDbOracleSQLAlchemyEngine,
)


@pytest.fixture
def sample_config() -> Any:
    """Create sample Oracle configuration for tests."""
    return FlextDbOracleConfig(
        username="test_user",
        password="test_password",
        host="localhost",
        port=1521,
        service_name="XE",
        pool_max_size=10,
        pool_min_size=2,
    )


@pytest.fixture
def engine_manager(sample_config: Any) -> FlextDbOracleSQLAlchemyEngine:
    """Create SQLAlchemy engine manager with sample config."""
    return FlextDbOracleSQLAlchemyEngine(sample_config)


class TestFlextDbOracleSQLAlchemyEngine:
    """Test cases for FlextDbOracleSQLAlchemyEngine class."""

    def test_initialization(self, sample_config: Any) -> None:
        """Test engine manager initialization."""
        engine_manager = FlextDbOracleSQLAlchemyEngine(sample_config)

        assert engine_manager.config == sample_config
        assert engine_manager.sync_engine is None
        assert engine_manager.async_engine is None

    def test_build_connection_url_service_name(self, engine_manager: Any) -> None:
        """Test connection URL building with service name."""
        url = engine_manager._build_connection_url()

        assert "oracle+oracledb://" in url
        assert "test_user:test_password" in url
        assert "localhost:1521" in url
        assert "service_name=XE" in url

    def test_build_connection_url_sid(self, sample_config: Any) -> None:
        """Test connection URL building with SID."""
        # Create config with SID instead of service_name
        config = FlextDbOracleConfig(
            username="test_user",
            password="test_password",
            host="localhost",
            port=1521,
            sid="ORCL",
        )
        engine_manager = FlextDbOracleSQLAlchemyEngine(config)

        url = engine_manager._build_connection_url()

        assert "oracle+oracledb://" in url
        assert "localhost:1521/ORCL" in url
        assert "service_name" not in url

    def test_build_connection_url_default(self, sample_config: Any) -> None:
        """Test connection URL building with default service name."""
        # Create config with default service_name
        config = FlextDbOracleConfig(
            username="test_user",
            password="test_password",
            host="localhost",
            port=1521,
            service_name="XE",  # Must provide default service name
        )
        engine_manager = FlextDbOracleSQLAlchemyEngine(config)

        url = engine_manager._build_connection_url()

        assert "service_name=XE" in url  # Default service name

    def test_create_engine_params(self, engine_manager: Any) -> None:
        """Test SQLAlchemy engine parameters creation."""
        params = engine_manager._create_engine_params()

        assert params["pool_size"] == 10
        assert params["max_overflow"] == 0
        assert params["pool_pre_ping"] is True
        assert "pool_recycle" in params
        assert params["echo"] is False
        assert "connect_args" in params

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.sessionmaker")
    async def test_initialize_sync_engine_success(
        self, mock_sessionmaker: Any, mock_create_engine: Any, engine_manager: Any
    ) -> None:
        """Test successful synchronous engine initialization."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session_factory = MagicMock()
        mock_sessionmaker.return_value = mock_session_factory

        result = await engine_manager.initialize_sync_engine()

        assert result.success
        assert result.data == mock_engine
        assert engine_manager.sync_engine == mock_engine
        mock_create_engine.assert_called_once()
        mock_sessionmaker.assert_called_once_with(
            bind=mock_engine,
            expire_on_commit=False,
        )

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_engine")
    async def test_initialize_sync_engine_already_initialized(
        self, mock_create_engine: Any, engine_manager: Any
    ) -> None:
        """Test sync engine initialization when already initialized."""
        # Set up already initialized engine
        existing_engine = MagicMock()
        engine_manager._sync_engine = existing_engine

        result = await engine_manager.initialize_sync_engine()

        assert result.success
        assert result.data == existing_engine
        mock_create_engine.assert_not_called()  # Should not create new engine

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_engine")
    async def test_initialize_sync_engine_sqlalchemy_error(
        self, mock_create_engine: Any, engine_manager: Any
    ) -> None:
        """Test sync engine initialization with SQLAlchemy error."""
        mock_create_engine.side_effect = SQLAlchemyError("Connection failed")

        result = await engine_manager.initialize_sync_engine()

        assert not result.success
        assert "Sync engine initialization failed" in result.error

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_engine")
    async def test_initialize_sync_engine_unexpected_error(
        self, mock_create_engine: Any, engine_manager: Any
    ) -> None:
        """Test sync engine initialization with unexpected error."""
        mock_create_engine.side_effect = Exception("Unexpected error")

        result = await engine_manager.initialize_sync_engine()

        assert not result.success
        assert "Sync engine initialization error" in result.error

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_async_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.async_sessionmaker")
    async def test_initialize_async_engine_success(
        self,
        mock_async_sessionmaker: Any,
        mock_create_async_engine: Any,
        engine_manager: Any,
    ) -> None:
        """Test successful asynchronous engine initialization."""
        mock_async_engine = MagicMock()
        mock_create_async_engine.return_value = mock_async_engine
        mock_async_session_factory = MagicMock()
        mock_async_sessionmaker.return_value = mock_async_session_factory

        result = await engine_manager.initialize_async_engine()

        assert result.success
        assert result.data == mock_async_engine
        assert engine_manager.async_engine == mock_async_engine
        mock_create_async_engine.assert_called_once()
        mock_async_sessionmaker.assert_called_once_with(
            bind=mock_async_engine,
            expire_on_commit=False,
        )

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_async_engine")
    async def test_initialize_async_engine_already_initialized(
        self, mock_create_async_engine: Any, engine_manager: Any
    ) -> None:
        """Test async engine initialization when already initialized."""
        # Set up already initialized engine
        existing_async_engine = MagicMock()
        engine_manager._async_engine = existing_async_engine

        result = await engine_manager.initialize_async_engine()

        assert result.success
        assert result.data == existing_async_engine
        mock_create_async_engine.assert_not_called()  # Should not create new engine

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_async_engine")
    async def test_initialize_async_engine_sqlalchemy_error(
        self, mock_create_async_engine: Any, engine_manager: Any
    ) -> None:
        """Test async engine initialization with SQLAlchemy error."""
        mock_create_async_engine.side_effect = SQLAlchemyError(
            "Async connection failed"
        )

        result = await engine_manager.initialize_async_engine()

        assert not result.success
        assert "Async engine initialization failed" in result.error

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.sessionmaker")
    async def test_get_session_context_manager(
        self, mock_sessionmaker: Any, mock_create_engine: Any, engine_manager: Any
    ) -> None:
        """Test synchronous session context manager."""
        # Mock engine and session setup
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session = MagicMock()
        mock_session_factory = MagicMock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory

        # Test successful session usage
        async with engine_manager.get_session() as session:
            assert session == mock_session

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.sessionmaker")
    async def test_get_session_with_exception(
        self, mock_sessionmaker: Any, mock_create_engine: Any, engine_manager: Any
    ) -> None:
        """Test synchronous session context manager with exception."""
        # Mock engine and session setup
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session = MagicMock()
        mock_session_factory = MagicMock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory

        # Test exception handling
        with pytest.raises(RuntimeError):
            async with engine_manager.get_session():
                raise RuntimeError("Test exception")

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.commit.assert_not_called()

    async def test_get_session_initialization_failure(
        self, engine_manager: Any
    ) -> None:
        """Test session context manager with initialization failure."""
        with (
            patch.object(
                engine_manager,
                "initialize_sync_engine",
                return_value=FlextResult.fail("Init failed"),
            ),
            pytest.raises(RuntimeError, match="Failed to initialize sync engine"),
        ):
            async with engine_manager.get_session():
                pass

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_async_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.async_sessionmaker")
    async def test_get_async_session_context_manager(
        self,
        mock_async_sessionmaker: Any,
        mock_create_async_engine: Any,
        engine_manager: Any,
    ) -> None:
        """Test asynchronous session context manager."""
        # Mock async engine and session setup
        mock_async_engine = MagicMock()
        mock_create_async_engine.return_value = mock_async_engine
        mock_async_session = AsyncMock()
        mock_async_session_factory = MagicMock(return_value=mock_async_session)
        mock_async_sessionmaker.return_value = mock_async_session_factory

        # Test successful async session usage
        async with engine_manager.get_async_session() as session:
            assert session == mock_async_session

        mock_async_session.commit.assert_called_once()
        mock_async_session.close.assert_called_once()

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_async_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.async_sessionmaker")
    async def test_get_async_session_with_exception(
        self,
        mock_async_sessionmaker: Any,
        mock_create_async_engine: Any,
        engine_manager: Any,
    ) -> None:
        """Test asynchronous session context manager with exception."""
        # Mock async engine and session setup
        mock_async_engine = MagicMock()
        mock_create_async_engine.return_value = mock_async_engine
        mock_async_session = AsyncMock()
        mock_async_session_factory = MagicMock(return_value=mock_async_session)
        mock_async_sessionmaker.return_value = mock_async_session_factory

        # Test exception handling
        with pytest.raises(RuntimeError):
            async with engine_manager.get_async_session():
                raise RuntimeError("Test async exception")

        mock_async_session.rollback.assert_called_once()
        mock_async_session.close.assert_called_once()
        mock_async_session.commit.assert_not_called()

    async def test_get_async_session_initialization_failure(
        self, engine_manager: Any
    ) -> None:
        """Test async session context manager with initialization failure."""
        with (
            patch.object(
                engine_manager,
                "initialize_async_engine",
                return_value=FlextResult.fail("Async init failed"),
            ),
            pytest.raises(RuntimeError, match="Failed to initialize async engine"),
        ):
            async with engine_manager.get_async_session():
                pass

    async def test_close_engines_both_engines(self, engine_manager: Any) -> None:
        """Test closing both sync and async engines."""
        # Set up both engines
        mock_sync_engine = MagicMock()
        mock_async_engine = AsyncMock()
        engine_manager._sync_engine = mock_sync_engine
        engine_manager._async_engine = mock_async_engine
        engine_manager._session_factory = MagicMock()
        engine_manager._async_session_factory = MagicMock()

        result = await engine_manager.close_engines()

        assert result.success
        mock_async_engine.dispose.assert_called_once()
        mock_sync_engine.dispose.assert_called_once()
        assert engine_manager._sync_engine is None
        assert engine_manager._async_engine is None
        assert engine_manager._session_factory is None
        assert engine_manager._async_session_factory is None

    async def test_close_engines_only_sync(self, engine_manager: Any) -> None:
        """Test closing only sync engine."""
        mock_sync_engine = MagicMock()
        engine_manager._sync_engine = mock_sync_engine
        engine_manager._session_factory = MagicMock()

        result = await engine_manager.close_engines()

        assert result.success
        mock_sync_engine.dispose.assert_called_once()
        assert engine_manager._sync_engine is None
        assert engine_manager._session_factory is None

    async def test_close_engines_only_async(self, engine_manager: Any) -> None:
        """Test closing only async engine."""
        mock_async_engine = AsyncMock()
        engine_manager._async_engine = mock_async_engine
        engine_manager._async_session_factory = MagicMock()

        result = await engine_manager.close_engines()

        assert result.success
        mock_async_engine.dispose.assert_called_once()
        assert engine_manager._async_engine is None
        assert engine_manager._async_session_factory is None

    async def test_close_engines_no_engines(self, engine_manager: Any) -> None:
        """Test closing engines when none are initialized."""
        result = await engine_manager.close_engines()

        assert result.success
        # Should complete successfully even with no engines

    async def test_close_engines_exception(self, engine_manager: Any) -> None:
        """Test closing engines with exception."""
        mock_sync_engine = MagicMock()
        mock_sync_engine.dispose.side_effect = Exception("Disposal error")
        engine_manager._sync_engine = mock_sync_engine

        result = await engine_manager.close_engines()

        assert not result.success
        assert "Engine disposal failed" in result.error

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.sessionmaker")
    async def test_get_connection_success(
        self, mock_sessionmaker: Any, mock_create_engine: Any, engine_manager: Any
    ) -> None:
        """Test successful database connection retrieval."""
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        result = await engine_manager.get_connection()

        assert result.success
        assert result.data == mock_connection
        mock_engine.connect.assert_called_once()

    async def test_get_connection_initialization_failure(
        self, engine_manager: Any
    ) -> None:
        """Test connection retrieval with initialization failure."""
        with patch.object(
            engine_manager,
            "initialize_sync_engine",
            return_value=FlextResult.fail("Init failed"),
        ):
            result = await engine_manager.get_connection()

            assert not result.success
            assert "Could not initialize engine" in result.error

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.sessionmaker")
    async def test_get_connection_connect_failure(
        self, mock_sessionmaker: Any, mock_create_engine: Any, engine_manager: Any
    ) -> None:
        """Test connection retrieval with connection failure."""
        mock_engine = MagicMock()
        mock_engine.connect.side_effect = Exception("Connection failed")
        mock_create_engine.return_value = mock_engine

        result = await engine_manager.get_connection()

        assert not result.success
        assert "Connection retrieval failed" in result.error

    def test_sync_engine_property(self, engine_manager: Any) -> None:
        """Test sync engine property."""
        assert engine_manager.sync_engine is None

        mock_engine = MagicMock()
        engine_manager._sync_engine = mock_engine
        assert engine_manager.sync_engine == mock_engine

    def test_async_engine_property(self, engine_manager: Any) -> None:
        """Test async engine property."""
        assert engine_manager.async_engine is None

        mock_async_engine = MagicMock()
        engine_manager._async_engine = mock_async_engine
        assert engine_manager.async_engine == mock_async_engine

    async def test_health_check_no_engines(self, engine_manager: Any) -> None:
        """Test health check with no engines initialized."""
        result = await engine_manager.health_check()

        assert result.success
        health_status = result.data
        assert health_status["sync_engine_active"] is False
        assert health_status["async_engine_active"] is False
        assert "connection_url" in health_status
        assert health_status["pool_size"] == 10

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.sessionmaker")
    async def test_health_check_sync_engine_healthy(
        self, mock_sessionmaker: Any, mock_create_engine: Any, engine_manager: Any
    ) -> None:
        """Test health check with healthy sync engine."""
        # Set up sync engine
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_connection.__enter__.return_value = mock_connection
        mock_connection.__exit__.return_value = None
        mock_connection.execute.return_value = mock_result
        mock_result.fetchone.return_value = [1]
        mock_engine.connect.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        # Initialize engine
        await engine_manager.initialize_sync_engine()

        result = await engine_manager.health_check()

        assert result.success
        health_status = result.data
        assert health_status["sync_engine_active"] is True
        assert health_status["sync_engine_healthy"] is True

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.sessionmaker")
    async def test_health_check_sync_engine_unhealthy(
        self, mock_sessionmaker: Any, mock_create_engine: Any, engine_manager: Any
    ) -> None:
        """Test health check with unhealthy sync engine."""
        # Set up sync engine that fails health check
        mock_engine = MagicMock()
        mock_engine.connect.side_effect = Exception("Connection failed")
        mock_create_engine.return_value = mock_engine

        # Initialize engine
        await engine_manager.initialize_sync_engine()

        result = await engine_manager.health_check()

        assert result.success
        health_status = result.data
        assert health_status["sync_engine_active"] is True
        assert health_status["sync_engine_healthy"] is False
        assert "sync_engine_error" in health_status

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_async_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.async_sessionmaker")
    async def test_health_check_async_engine_healthy(
        self,
        mock_async_sessionmaker: Any,
        mock_create_async_engine: Any,
        engine_manager: Any,
    ) -> None:
        """Test health check with healthy async engine."""
        # Set up async engine
        mock_async_engine = MagicMock()
        mock_async_connection = AsyncMock()
        mock_async_result = MagicMock()
        mock_async_connection.__aenter__.return_value = mock_async_connection
        mock_async_connection.__aexit__.return_value = None
        mock_async_connection.execute.return_value = mock_async_result
        mock_async_result.fetchone.return_value = [1]
        mock_async_engine.begin.return_value = mock_async_connection
        mock_create_async_engine.return_value = mock_async_engine

        # Initialize async engine
        await engine_manager.initialize_async_engine()

        result = await engine_manager.health_check()

        assert result.success
        health_status = result.data
        assert health_status["async_engine_active"] is True
        assert health_status["async_engine_healthy"] is True

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_async_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.async_sessionmaker")
    async def test_health_check_async_engine_unhealthy(
        self,
        mock_async_sessionmaker: Any,
        mock_create_async_engine: Any,
        engine_manager: Any,
    ) -> None:
        """Test health check with unhealthy async engine."""
        # Set up async engine that fails health check
        mock_async_engine = MagicMock()
        mock_async_engine.begin.side_effect = Exception("Async connection failed")
        mock_create_async_engine.return_value = mock_async_engine

        # Initialize async engine
        await engine_manager.initialize_async_engine()

        result = await engine_manager.health_check()

        assert result.success
        health_status = result.data
        assert health_status["async_engine_active"] is True
        assert health_status["async_engine_healthy"] is False
        assert "async_engine_error" in health_status

    async def test_health_check_exception(self, engine_manager: Any) -> None:
        """Test health check with unexpected exception."""
        # Mock config to raise exception during URL building
        with patch.object(
            engine_manager,
            "_build_connection_url",
            side_effect=Exception("URL build error"),
        ):
            result = await engine_manager.health_check()

            assert not result.success
            assert "Health check error" in result.error


@pytest.mark.asyncio
class TestSQLAlchemyEngineIntegration:
    """Integration-style tests for SQLAlchemy engine manager."""

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_async_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.sessionmaker")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.async_sessionmaker")
    async def test_full_engine_lifecycle(
        self,
        mock_async_sessionmaker: Any,
        mock_sessionmaker: Any,
        mock_create_async_engine: Any,
        mock_create_engine: Any,
        engine_manager: Any,
    ) -> None:
        """Test complete engine lifecycle: init -> use -> close."""
        # Mock engines and sessions
        mock_sync_engine = MagicMock()
        mock_async_engine = AsyncMock()
        mock_session = MagicMock()
        mock_async_session = AsyncMock()

        mock_create_engine.return_value = mock_sync_engine
        mock_create_async_engine.return_value = mock_async_engine
        mock_sessionmaker.return_value = MagicMock(return_value=mock_session)
        mock_async_sessionmaker.return_value = MagicMock(
            return_value=mock_async_session
        )

        # 1. Initialize both engines
        sync_result = await engine_manager.initialize_sync_engine()
        async_result = await engine_manager.initialize_async_engine()

        assert sync_result.success
        assert async_result.success
        assert engine_manager.sync_engine == mock_sync_engine
        assert engine_manager.async_engine == mock_async_engine

        # 2. Use session context managers
        async with engine_manager.get_session() as session:
            assert session == mock_session

        async with engine_manager.get_async_session() as async_session:
            assert async_session == mock_async_session

        # 3. Perform health check
        health_result = await engine_manager.health_check()
        assert health_result.success

        # 4. Close engines
        close_result = await engine_manager.close_engines()
        assert close_result.success
        assert engine_manager.sync_engine is None
        assert engine_manager.async_engine is None

    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.create_engine")
    @patch("src.flext_db_oracle.infrastructure.sqlalchemy_engine.sessionmaker")
    async def test_connection_retrieval_and_usage(
        self, mock_sessionmaker: Any, mock_create_engine: Any, engine_manager: Any
    ) -> None:
        """Test connection retrieval and usage workflow."""
        # Mock engine and connection
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        # Get connection
        result = await engine_manager.get_connection()

        assert result.success
        connection = result.data
        assert connection == mock_connection

        # Verify engine was created with correct parameters
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args

        # Check URL contains expected components
        connection_url = call_args[0][0]
        assert "oracle+oracledb://" in connection_url
        assert "test_user" in connection_url
        assert "localhost:1521" in connection_url

        # Check engine parameters
        engine_params = call_args[1]
        assert engine_params["pool_size"] == 10
        assert engine_params["pool_pre_ping"] is True


class TestConfigurationVariations:
    """Test engine manager with different configuration variations."""

    def test_minimal_config(self) -> None:
        """Test engine manager with minimal configuration."""
        config = FlextDbOracleConfig(
            username="user",
            password="pass",
            service_name="XE",
        )
        engine_manager = FlextDbOracleSQLAlchemyEngine(config)

        url = engine_manager._build_connection_url()
        # Should use default host and port
        assert "localhost:1521" in url
        assert "service_name=XE" in url

    def test_custom_pool_config(self) -> None:
        """Test engine manager with custom pool configuration."""
        config = FlextDbOracleConfig(
            username="user",
            password="pass",
            service_name="XE",
            pool_max_size=20,
            pool_min_size=5,
        )
        engine_manager = FlextDbOracleSQLAlchemyEngine(config)

        params = engine_manager._create_engine_params()
        assert params["pool_size"] == 20

    def test_different_database_identifiers(self) -> None:
        """Test URL building with different database identifier configurations."""
        # Test with service_name
        config_service = FlextDbOracleConfig(
            username="user",
            password="pass",
            service_name="PROD",
        )
        engine_service = FlextDbOracleSQLAlchemyEngine(config_service)
        url_service = engine_service._build_connection_url()
        assert "service_name=PROD" in url_service

        # Test with SID
        config_sid = FlextDbOracleConfig(
            username="user",
            password="pass",
            sid="ORCL",
        )
        engine_sid = FlextDbOracleSQLAlchemyEngine(config_sid)
        url_sid = engine_sid._build_connection_url()
        assert "/ORCL" in url_sid
        assert "service_name" not in url_sid

        # Test with neither explicitly set (should use default service name)
        config_default = FlextDbOracleConfig(
            username="user",
            password="pass",
            service_name="XE",  # Must provide at least one
        )
        engine_default = FlextDbOracleSQLAlchemyEngine(config_default)
        url_default = engine_default._build_connection_url()
        assert "service_name=XE" in url_default

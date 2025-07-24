"""FLEXT DB ORACLE - SQLAlchemy Engine Management.

SQLAlchemy-based Oracle database engine and session management following
Clean Architecture patterns with FlextDbOracle naming conventions.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

# Modern flext-core imports from root namespace
from flext_core import FlextResult
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from flext_db_oracle.constants import FlextDbOracleConstants

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.engine import Engine

    from flext_db_oracle.config import FlextDbOracleConfig

logger = logging.getLogger(__name__)


class FlextDbOracleSQLAlchemyEngine:
    """SQLAlchemy engine management for Oracle database connections.

    Provides both sync and async engine management with connection pooling
    and proper Oracle-specific configuration.
    """

    def __init__(self, config: FlextDbOracleConfig) -> None:
        """Initialize SQLAlchemy engine manager.

        Args:
            config: FlextDbOracle database configuration

        """
        self.config = config
        self._sync_engine: Engine | None = None
        self._async_engine: AsyncEngine | None = None
        self._session_factory: sessionmaker[Session] | None = None
        self._async_session_factory: async_sessionmaker[AsyncSession] | None = None

    def _build_connection_url(self, async_mode: bool = False) -> str:
        """Build SQLAlchemy connection URL for Oracle.

        Args:
            async_mode: Whether to build URL for async engine

        Returns:
            SQLAlchemy connection URL

        """
        # Use oracle+oracledb for sync, oracle+oracledb for async
        dialect = "oracle+oracledb"

        # Build base URL components
        username = self.config.username
        password = self.config.password
        host = self.config.host
        port = self.config.port

        # Determine service name or SID
        if self.config.service_name:
            database = self.config.service_name
            url = f"{dialect}://{username}:{password}@{host}:{port}/?service_name={database}"
        elif self.config.sid:
            database = self.config.sid
            url = f"{dialect}://{username}:{password}@{host}:{port}/{database}"
        else:
            # Default to XE service name
            url = f"{dialect}://{username}:{password}@{host}:{port}/?service_name=XE"

        return url

    def _create_engine_params(self) -> dict[str, Any]:
        """Create SQLAlchemy engine parameters with Oracle optimizations.

        Returns:
            Dictionary of engine parameters

        """
        return {
            "pool_size": self.config.pool_max_size,
            "max_overflow": 0,  # No overflow connections
            "pool_pre_ping": True,  # Validate connections
            "pool_recycle": FlextDbOracleConstants.DEFAULT_POOL_RECYCLE,
            "echo": False,  # Set to True for SQL debugging
            "connect_args": {
                # Remove incompatible parameters for oracledb
                # "encoding" and "nencoding" are not supported
                # "threaded" and "events" are not needed for modern oracledb
            },
        }

    async def initialize_sync_engine(self) -> FlextResult[Engine]:
        """Initialize synchronous SQLAlchemy engine.

        Returns:
            FlextResult containing the initialized engine

        """
        try:
            if self._sync_engine is not None:
                return FlextResult.ok(self._sync_engine)

            connection_url = self._build_connection_url(async_mode=False)
            engine_params = self._create_engine_params()

            self._sync_engine = create_engine(connection_url, **engine_params)

            # Create session factory
            self._session_factory = sessionmaker(
                bind=self._sync_engine,
                expire_on_commit=False,
            )

            # Engine created successfully - connection test moved to health_check
            # This allows engine to be created without active Oracle database

            logger.info("Synchronous SQLAlchemy engine initialized")
            return FlextResult.ok(self._sync_engine)

        except SQLAlchemyError as e:
            logger.exception("Failed to initialize sync SQLAlchemy engine")
            return FlextResult.fail(f"Sync engine initialization failed: {e}")
        except Exception as e:
            logger.exception("Unexpected error initializing sync engine")
            return FlextResult.fail(f"Sync engine initialization error: {e}")

    async def initialize_async_engine(self) -> FlextResult[AsyncEngine]:
        """Initialize asynchronous SQLAlchemy engine.

        Returns:
            FlextResult containing the initialized async engine

        """
        try:
            if self._async_engine is not None:
                return FlextResult.ok(self._async_engine)

            connection_url = self._build_connection_url(async_mode=True)
            engine_params = self._create_engine_params()

            self._async_engine = create_async_engine(connection_url, **engine_params)

            # Create async session factory
            self._async_session_factory = async_sessionmaker(
                bind=self._async_engine,
                expire_on_commit=False,
            )

            # Engine created successfully - connection test moved to health_check
            # This allows engine to be created without active Oracle database

            logger.info("Asynchronous SQLAlchemy engine initialized")
            return FlextResult.ok(self._async_engine)

        except SQLAlchemyError as e:
            logger.exception("Failed to initialize async SQLAlchemy engine")
            return FlextResult.fail(f"Async engine initialization failed: {e}")
        except Exception as e:
            logger.exception("Unexpected error initializing async engine")
            return FlextResult.fail(f"Async engine initialization error: {e}")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[Session]:
        """Get synchronous database session context manager.

        Yields:
            Database session

        """
        if self._session_factory is None:
            result = await self.initialize_sync_engine()
            if not result.success:
                msg = f"Failed to initialize sync engine: {result.error}"
                raise RuntimeError(msg)

        if self._session_factory is None:
            msg = "Session factory is None after initialization"
            raise RuntimeError(msg)

        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession]:
        """Get asynchronous database session context manager.

        Yields:
            Async database session

        """
        if self._async_session_factory is None:
            result = await self.initialize_async_engine()
            if not result.success:
                msg = f"Failed to initialize async engine: {result.error}"
                raise RuntimeError(msg)

        if self._async_session_factory is None:
            msg = "Async session factory is None after initialization"
            raise RuntimeError(msg)

        session = self._async_session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close_engines(self) -> FlextResult[None]:
        """Close all database engines and clean up resources.

        Returns:
            FlextResult indicating success or failure

        """
        try:
            if self._async_engine:
                await self._async_engine.dispose()
                self._async_engine = None
                self._async_session_factory = None
                logger.info("Async SQLAlchemy engine disposed")

            if self._sync_engine:
                self._sync_engine.dispose()
                self._sync_engine = None
                self._session_factory = None
                logger.info("Sync SQLAlchemy engine disposed")

            return FlextResult.ok(None)

        except Exception as e:
            logger.exception("Failed to dispose SQLAlchemy engines")
            return FlextResult.fail(f"Engine disposal failed: {e}")

    async def get_connection(self) -> FlextResult[Any]:
        """Get a raw database connection from the connection pool.

        Returns:
            FlextResult containing database connection

        """
        try:
            if self._sync_engine is None:
                # Try to initialize if not already done
                init_result = await self.initialize_sync_engine()
                if not init_result.success:
                    return FlextResult.fail(
                        f"Could not initialize engine: {init_result.error}",
                    )

            if self._sync_engine is None:
                return FlextResult.fail(
                    "Engine still not available after initialization",
                )

            # Get connection from the engine
            connection = self._sync_engine.connect()
            return FlextResult.ok(connection)

        except Exception as e:
            logger.exception("Failed to get database connection")
            return FlextResult.fail(f"Connection retrieval failed: {e}")

    @property
    def sync_engine(self) -> Engine | None:
        """Get the synchronous engine instance."""
        return self._sync_engine

    @property
    def async_engine(self) -> AsyncEngine | None:
        """Get the asynchronous engine instance."""
        return self._async_engine

    async def health_check(self) -> FlextResult[dict[str, Any]]:
        """Perform health check on database engines.

        Returns:
            FlextResult containing health check status

        """
        try:
            health_status = {
                "sync_engine_active": self._sync_engine is not None,
                "async_engine_active": self._async_engine is not None,
                "connection_url": self._build_connection_url(),
                "pool_size": self.config.pool_max_size,
            }

            # Test sync engine if available
            if self._sync_engine:
                try:
                    with self._sync_engine.connect() as conn:
                        result = conn.execute(text("SELECT 1 FROM dual"))
                        result.fetchone()
                    health_status["sync_engine_healthy"] = True
                except Exception as e:
                    health_status["sync_engine_healthy"] = False
                    health_status["sync_engine_error"] = str(e)

            # Test async engine if available
            if self._async_engine:
                try:
                    async with self._async_engine.begin() as conn:
                        result = await conn.execute(text("SELECT 1 FROM dual"))
                        result.fetchone()
                    health_status["async_engine_healthy"] = True
                except Exception as e:
                    health_status["async_engine_healthy"] = False
                    health_status["async_engine_error"] = str(e)

            return FlextResult.ok(health_status)

        except Exception as e:
            logger.exception("Health check failed")
            return FlextResult.fail(f"Health check error: {e}")

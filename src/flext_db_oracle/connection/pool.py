"""Oracle Database Connection Pool Implementation."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

import oracledb

from flext_db_oracle.connection.base import FlextDbOracleBaseOperations
from flext_db_oracle.logging_utils import get_logger

if TYPE_CHECKING:
    from collections.abc import Generator

    from flext_db_oracle.connection.config import ConnectionConfig
logger = get_logger(__name__)


class FlextDbOracleConnectionPool(FlextDbOracleBaseOperations):
    """Oracle database connection pool for high-performance applications.

    Manages a pool of database connections to improve performance and
    resource utilization in multi-threaded applications.
    """

    def __init__(self, config: ConnectionConfig) -> None:
        """Initialize the connection pool.

        Args:
            config: FlextDbOracle database connection configuration

        """
        self.config = config
        self._pool: Any = None
        self._is_initialized = False

    def initialize(self) -> None:
        try:
            params = self.config.to_connect_params()
            # Create connection pool
            self._pool = oracledb.create_pool(
                min=self.config.pool_min,
                max=self.config.pool_max,
                increment=self.config.pool_increment,
                **params,
            )
            self._is_initialized = True
            logger.info(
                "Initialized Oracle connection pool: min=%d, max=%d, increment=%d",
                self.config.pool_min,
                self.config.pool_max,
                self.config.pool_increment,
            )
        except Exception:
            logger.exception("Failed to initialize connection pool")
            raise

    def close(self) -> None:
        """Close the connection pool."""
        try:
            self._pool.close()
            self._is_initialized = False
            logger.info("Closed Oracle connection pool")
        except Exception:
            logger.exception("Error closing connection pool")
        self._pool = None

    @property
    def is_initialized(self) -> bool:
        """Check if pool is initialized."""
        return self._is_initialized and self._pool is not None

    @contextmanager
    def get_connection(self) -> Generator[Any]:
        """Get a connection from the pool.

        Yields:
            Database connection from the pool.

        Raises:
            RuntimeError: If pool is not initialized.

        """
        if not self.is_initialized:
            msg = "Connection pool is not initialized"
            raise RuntimeError(msg)
        try:
            connection = self._pool.acquire() if self._pool else None
            yield connection
        finally:
            if connection and self._pool:
                self._pool.release(connection)

    def execute(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[tuple[Any, ...]] | int:
        """Execute SQL statement using pooled connection."""
        with self.get_connection() as conn:
            return self._execute_with_connection(conn, sql, parameters)

    def execute_many(self, sql: str, parameters_list: list[dict[str, Any]]) -> int:
        """Execute SQL statement with multiple parameter sets using pooled connection.

        Args:
            sql: SQL statement to execute
            parameters_list: List of parameter dictionaries

        Returns:
            Number of rows affected

        """
        with self.get_connection() as conn:
            return self._execute_many_with_connection(conn, sql, parameters_list)

    def fetch_one(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> tuple[Any, ...] | None:
        """Fetch one row from SQL query using pooled connection."""
        with self.get_connection() as conn:
            return self._fetch_one_with_connection(conn, sql, parameters)

    def fetch_all(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[tuple[Any, ...]]:
        """Fetch all rows from SQL query using pooled connection."""
        with self.get_connection() as conn:
            return self._fetch_all_with_connection(conn, sql, parameters)

    @contextmanager
    def transaction(self) -> Generator[Any]:
        """Context manager for database transactions using pool.

        Automatically commits on success or rolls back on exception.

        Yields:
            Database connection for use within the transaction.

        """
        with self.get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def get_pool_stats(self) -> dict[str, Any]:
        """Get pool statistics."""
        if not self.is_initialized:
            return {"status": "not_initialized"}
        try:
            # Get pool statistics (if available in oracledb)
            stats = {
                "status": "initialized",
                "min_connections": self.config.pool_min,
                "max_connections": self.config.pool_max,
                "increment": self.config.pool_increment,
            }
            # Add actual pool stats if available
            if self._pool and hasattr(self._pool, "opened"):
                stats.update(
                    {
                        "opened": self._pool.opened,
                        "busy": self._pool.busy,
                    },
                )
            return stats
        except Exception as e:
            logger.exception("Error getting pool stats")
            return {"status": "error", "error": str(e)}


# Backward compatibility alias
ConnectionPool = FlextDbOracleConnectionPool

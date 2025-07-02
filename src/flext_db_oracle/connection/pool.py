"""Oracle Database Connection Pool Implementation."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

try:
    import oracledb

    ORACLEDB_AVAILABLE = True
except ImportError:
    ORACLEDB_AVAILABLE = False
    oracledb = None


if TYPE_CHECKING:
    from collections.abc import Generator

    from .config import ConnectionConfig

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Oracle database connection pool for high-performance applications.

    Manages a pool of database connections to improve performance and
    resource utilization in multi-threaded applications.
    """

    def __init__(self, config: ConnectionConfig) -> None:
        """Initialize connection pool.

        Args:
            config: Database connection configuration.
        """
        self.config = config
        self._pool = None
        self._is_initialized = False

    def initialize(self) -> None:
        """Initialize the connection pool.

        Raises:
            RuntimeError: If oracledb library is not available.
            Exception: If pool initialization fails.
        """
        if not ORACLEDB_AVAILABLE:
            raise RuntimeError(
                "oracledb library not available. Install with: pip install oracledb"
            )

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

        except Exception as e:
            logger.error("Failed to initialize connection pool: %s", e)
            raise

    def close(self) -> None:
        """Close the connection pool and all connections."""
        if self._pool and self._is_initialized:
            try:
                self._pool.close()
                self._is_initialized = False
                logger.info("Closed Oracle connection pool")
            except Exception as e:
                logger.error("Error closing connection pool: %s", e)

        self._pool = None

    @property
    def is_initialized(self) -> bool:
        """Check if pool is initialized.

        Returns:
            True if pool is initialized, False otherwise.
        """
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
            raise RuntimeError("Connection pool not initialized")

        connection = None
        try:
            connection = self._pool.acquire()
            yield connection
        finally:
            if connection:
                self._pool.release(connection)

    def execute(self, sql: str, parameters: dict[str, Any] | None = None) -> Any:
        """Execute SQL statement using a pool connection.

        Args:
            sql: SQL statement to execute.
            parameters: Optional parameters for the SQL statement.

        Returns:
            Query results or row count.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if parameters:
                    cursor.execute(sql, parameters)
                else:
                    cursor.execute(sql)

                # For SELECT statements, return fetchall()
                if sql.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                else:
                    # For DML statements, return row count
                    return cursor.rowcount
            finally:
                cursor.close()

    def execute_many(self, sql: str, parameters_list: list[dict[str, Any]]) -> int:
        """Execute SQL statement with multiple parameter sets using pool.

        Args:
            sql: SQL statement to execute.
            parameters_list: List of parameter dictionaries.

        Returns:
            Total number of affected rows.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(sql, parameters_list)
                return cursor.rowcount
            finally:
                cursor.close()

    def fetch_one(self, sql: str, parameters: dict[str, Any] | None = None) -> Any:
        """Fetch a single row using pool connection.

        Args:
            sql: SELECT statement to execute.
            parameters: Optional parameters for the SQL statement.

        Returns:
            Single row result or None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if parameters:
                    cursor.execute(sql, parameters)
                else:
                    cursor.execute(sql)
                return cursor.fetchone()
            finally:
                cursor.close()

    def fetch_all(
        self, sql: str, parameters: dict[str, Any] | None = None
    ) -> list[Any]:
        """Fetch all rows using pool connection.

        Args:
            sql: SELECT statement to execute.
            parameters: Optional parameters for the SQL statement.

        Returns:
            List of all rows.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if parameters:
                    cursor.execute(sql, parameters)
                else:
                    cursor.execute(sql)
                return cursor.fetchall()
            finally:
                cursor.close()

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
        """Get connection pool statistics.

        Returns:
            Dictionary containing pool statistics.
        """
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
            if hasattr(self._pool, "opened"):
                stats["opened_connections"] = self._pool.opened
            if hasattr(self._pool, "busy"):
                stats["busy_connections"] = self._pool.busy

            return stats

        except Exception as e:
            logger.error("Error getting pool stats: %s", e)
            return {"status": "error", "error": str(e)}

    def __enter__(self) -> ConnectionPool:
        """Context manager entry."""
        if not self.is_initialized:
            self.initialize()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

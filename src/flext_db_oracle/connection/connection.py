"""Oracle Database Connection Implementation."""

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


class OracleConnection:
    """Oracle database connection wrapper with enterprise features.

    Provides a high-level interface for Oracle database operations with
    proper connection management, error handling, and transaction support.
    """

    def __init__(self, config: ConnectionConfig) -> None:
        """Initialize Oracle connection.

        Args:
            config: Database connection configuration.
        """
        self.config = config
        self._connection = None
        self._is_connected = False

    def connect(self) -> None:
        """Establish database connection.

        Raises:
            RuntimeError: If oracledb library is not available.
            Exception: If connection fails.
        """
        if not ORACLEDB_AVAILABLE:
            raise RuntimeError(
                "oracledb library not available. Install with: pip install oracledb"
            )

        try:
            params = self.config.to_connect_params()
            self._connection = oracledb.connect(**params)
            self._is_connected = True
            logger.info("Connected to Oracle database: %s:%s",
                       self.config.host, self.config.port)
        except Exception as e:
            logger.error("Failed to connect to Oracle database: %s", e)
            raise

    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._is_connected:
            try:
                self._connection.close()
                self._is_connected = False
                logger.info("Disconnected from Oracle database")
            except Exception as e:
                logger.error("Error disconnecting from database: %s", e)

        self._connection = None

    @property
    def is_connected(self) -> bool:
        """Check if connection is active.

        Returns:
            True if connected, False otherwise.
        """
        return self._is_connected and self._connection is not None

    def execute(self, sql: str, parameters: dict[str, Any] | None = None) -> Any:
        """Execute SQL statement.

        Args:
            sql: SQL statement to execute.
            parameters: Optional parameters for the SQL statement.

        Returns:
            Cursor result for SELECT statements, row count for DML.

        Raises:
            RuntimeError: If not connected to database.
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to database")

        cursor = self._connection.cursor()
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
        """Execute SQL statement with multiple parameter sets.

        Args:
            sql: SQL statement to execute.
            parameters_list: List of parameter dictionaries.

        Returns:
            Total number of affected rows.

        Raises:
            RuntimeError: If not connected to database.
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to database")

        cursor = self._connection.cursor()
        try:
            cursor.executemany(sql, parameters_list)
            return cursor.rowcount
        finally:
            cursor.close()

    def fetch_one(self, sql: str, parameters: dict[str, Any] | None = None) -> Any:
        """Fetch a single row from query.

        Args:
            sql: SELECT statement to execute.
            parameters: Optional parameters for the SQL statement.

        Returns:
            Single row result or None.

        Raises:
            RuntimeError: If not connected to database.
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to database")

        cursor = self._connection.cursor()
        try:
            if parameters:
                cursor.execute(sql, parameters)
            else:
                cursor.execute(sql)
            return cursor.fetchone()
        finally:
            cursor.close()

    def fetch_all(self, sql: str, parameters: dict[str, Any] | None = None) -> list[Any]:
        """Fetch all rows from query.

        Args:
            sql: SELECT statement to execute.
            parameters: Optional parameters for the SQL statement.

        Returns:
            List of all rows.

        Raises:
            RuntimeError: If not connected to database.
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to database")

        cursor = self._connection.cursor()
        try:
            if parameters:
                cursor.execute(sql, parameters)
            else:
                cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()

    def commit(self) -> None:
        """Commit current transaction.

        Raises:
            RuntimeError: If not connected to database.
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to database")

        self._connection.commit()

    def rollback(self) -> None:
        """Rollback current transaction.

        Raises:
            RuntimeError: If not connected to database.
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to database")

        self._connection.rollback()

    @contextmanager
    def transaction(self) -> Generator[OracleConnection]:
        """Context manager for database transactions.

        Automatically commits on success or rolls back on exception.

        Yields:
            The connection instance for use within the transaction.
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to database")

        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise

    def get_table_names(self, schema: str | None = None) -> list[str]:
        """Get list of table names in the database.

        Args:
            schema: Optional schema name to filter tables.

        Returns:
            List of table names.
        """
        sql = "SELECT table_name FROM all_tables"
        if schema:
            sql += " WHERE owner = :schema"
            parameters = {"schema": schema.upper()}
        else:
            parameters = None

        results = self.fetch_all(sql, parameters)
        return [row[0] for row in results]

    def get_column_info(self, table_name: str, schema: str | None = None) -> list[dict[str, Any]]:
        """Get column information for a table.

        Args:
            table_name: Name of the table.
            schema: Optional schema name.

        Returns:
            List of dictionaries containing column information.
        """
        sql = """
        SELECT column_name, data_type, data_length, data_precision,
               data_scale, nullable, data_default
        FROM all_tab_columns
        WHERE table_name = :table_name
        """

        parameters = {"table_name": table_name.upper()}

        if schema:
            sql += " AND owner = :schema"
            parameters["schema"] = schema.upper()

        sql += " ORDER BY column_id"

        results = self.fetch_all(sql, parameters)

        columns = []
        for row in results:
            columns.append({
                "name": row[0],
                "type": row[1],
                "length": row[2],
                "precision": row[3],
                "scale": row[4],
                "nullable": row[5] == "Y",
                "default": row[6],
            })

        return columns

    def __enter__(self) -> OracleConnection:
        """Context manager entry."""
        if not self.is_connected:
            self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.disconnect()

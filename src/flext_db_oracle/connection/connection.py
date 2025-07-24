"""Oracle Database Connection Implementation."""

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


class FlextDbOracleConnection(FlextDbOracleBaseOperations):
    """Oracle database connection wrapper with enterprise features.

    Provides a high-level interface for Oracle database operations with
    proper connection management, error handling, and transaction support.
    """

    def __init__(self, config: ConnectionConfig) -> None:
        """Initialize the Oracle connection.

        Args:
            config: FlextDbOracle database connection configuration

        """
        self.config = config
        self._connection: Any = None
        self._is_connected = False

    def connect(self) -> None:
        try:
            params = self.config.to_connect_params()
            self._connection = oracledb.connect(**params)
            self._is_connected = True
            logger.info(
                "Connected to Oracle database: %s:%s",
                self.config.host,
                self.config.port,
            )
        except Exception:
            logger.exception("Failed to connect to Oracle database")
            raise

    def disconnect(self) -> None:
        """Disconnect from Oracle database."""
        try:
            self._connection.close()
            self._is_connected = False
            logger.info("Disconnected from Oracle database")
        except Exception:
            logger.exception("Error disconnecting from database")
        self._connection = None

    @property
    def is_connected(self) -> bool:
        """Check if connected to database."""
        return self._is_connected and self._connection is not None

    def execute(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[tuple[Any, ...]] | int:
        """Execute SQL statement."""
        if not self.is_connected:
            msg = "Not connected to database"
            raise RuntimeError(msg)
        return self._execute_with_connection(self._connection, sql, parameters)

    def execute_many(self, sql: str, parameters_list: list[dict[str, Any]]) -> int:
        """Execute SQL statement with multiple parameter sets."""
        if not self.is_connected:
            msg = "Not connected to database"
            raise RuntimeError(msg)
        return self._execute_many_with_connection(
            self._connection, sql, parameters_list
        )

    def fetch_one(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> tuple[Any, ...] | None:
        """Fetch one row from SQL query."""
        if not self.is_connected:
            msg = "Not connected to database"
            raise RuntimeError(msg)
        return self._fetch_one_with_connection(self._connection, sql, parameters)

    def fetch_all(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[tuple[Any, ...]]:
        """Fetch all rows from SQL query."""
        if not self.is_connected:
            msg = "Not connected to database"
            raise RuntimeError(msg)
        return self._fetch_all_with_connection(self._connection, sql, parameters)

    def commit(self) -> None:
        """Commit current transaction."""
        if not self.is_connected:
            msg = "Not connected to database"
            raise RuntimeError(msg)
        self._connection.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        if not self.is_connected:
            msg = "Not connected to database"
            raise RuntimeError(msg)
        self._connection.rollback()

    @contextmanager
    def transaction(self) -> Generator[Any]:
        """Context manager for database transactions."""
        if not self.is_connected:
            msg = "Not connected to database"
            raise RuntimeError(msg)
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise

    def get_table_names(self, schema: str | None = None) -> list[str]:
        """Get table names from database."""
        sql = "SELECT table_name FROM all_tables"
        if schema:
            sql += " WHERE owner = :schema"
            parameters = {"schema": schema.upper()}
        else:
            parameters = None
        results = self.fetch_all(sql, parameters)
        return [row[0] for row in results]

    def get_column_info(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get column information for a table."""
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
        return [
            {
                "name": row[0],
                "type": row[1],
                "length": row[2],
                "precision": row[3],
                "scale": row[4],
                "nullable": row[5] == "Y",
                "default": row[6],
            }
            for row in results
        ]

    def get_version(self) -> str:
        """Get Oracle database version."""
        result = self.fetch_one("SELECT * FROM v$version WHERE rownum = 1")
        return str(result[0]) if result else "Unknown"

    def test_connection(self) -> bool:
        """Test if connection is working."""
        if not self.is_connected:
            return False
        return self._test_connection_with_connection(self._connection)

"""Base database operations shared between Connection and Pool classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from flext_core import get_logger

if TYPE_CHECKING:
    import oracledb

logger = get_logger(__name__)


class FlextDbOracleBaseOperations:
    """Base class for shared database operations between Connection and Pool.

    Eliminates code duplication by providing common database operation methods
    that can be used by both single connection and pooled connection classes.
    """

    def _execute_with_connection(
        self,
        conn: oracledb.Connection,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[tuple[Any, ...]] | int:
        """Execute SQL statement with provided connection.

        Args:
            conn: Oracle database connection
            sql: SQL statement to execute
            parameters: Optional parameters for SQL statement

        Returns:
            For SELECT: List of result tuples
            For DML: Number of affected rows

        """
        cursor = conn.cursor()
        try:
            if parameters:
                cursor.execute(sql, parameters)
            else:
                cursor.execute(sql)

            # For SELECT statements, return fetchall()
            if sql.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                return result if result is not None else []

            # For DML statements, return row count
            rowcount = cursor.rowcount
            return rowcount if rowcount is not None else 0
        finally:
            cursor.close()

    def _execute_many_with_connection(
        self,
        conn: oracledb.Connection,
        sql: str,
        parameters_list: list[dict[str, Any]],
    ) -> int:
        """Execute SQL statement with multiple parameter sets.

        Args:
            conn: Oracle database connection
            sql: SQL statement to execute
            parameters_list: List of parameter dictionaries

        Returns:
            Number of affected rows

        """
        cursor = conn.cursor()
        try:
            cursor.executemany(sql, parameters_list)
            return int(cursor.rowcount) if cursor.rowcount is not None else 0
        finally:
            cursor.close()

    def _fetch_one_with_connection(
        self,
        conn: oracledb.Connection,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> tuple[Any, ...] | None:
        """Fetch one row from SQL query.

        Args:
            conn: Oracle database connection
            sql: SQL statement to execute
            parameters: Optional parameters for SQL statement

        Returns:
            First result tuple or None if no results

        """
        cursor = conn.cursor()
        try:
            if parameters:
                cursor.execute(sql, parameters)
            else:
                cursor.execute(sql)
            return cast("tuple[Any, ...] | None", cursor.fetchone())
        finally:
            cursor.close()

    def _fetch_all_with_connection(
        self,
        conn: oracledb.Connection,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[tuple[Any, ...]]:
        """Fetch all rows from SQL query.

        Args:
            conn: Oracle database connection
            sql: SQL statement to execute
            parameters: Optional parameters for SQL statement

        Returns:
            List of result tuples

        """
        cursor = conn.cursor()
        try:
            if parameters:
                cursor.execute(sql, parameters)
            else:
                cursor.execute(sql)
            result = cursor.fetchall()
            return result if result is not None else []
        finally:
            cursor.close()

    def _execute_with_metadata(
        self,
        conn: oracledb.Connection,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute SQL and return results with column metadata.

        Args:
            conn: Oracle database connection
            sql: SQL statement to execute
            parameters: Optional parameters for SQL statement

        Returns:
            Dictionary containing 'columns', 'rows', and 'affected_rows'

        """
        cursor = conn.cursor()
        try:
            if parameters:
                cursor.execute(sql, parameters)
            else:
                cursor.execute(sql)

            # Get column information from cursor description
            columns = []
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]

            # For SELECT statements, fetch results
            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                return {
                    "columns": columns,
                    "rows": rows if rows is not None else [],
                    "affected_rows": 0,
                }

            # For DML statements, return affected rows count
            affected_rows = cursor.rowcount if cursor.rowcount is not None else 0
            return {
                "columns": columns,
                "rows": [],
                "affected_rows": affected_rows,
            }
        finally:
            cursor.close()

    def _test_connection_with_connection(self, conn: oracledb.Connection) -> bool:
        """Test if connection is working.

        Args:
            conn: Oracle database connection

        Returns:
            True if connection is working, False otherwise

        """
        try:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT 1 FROM DUAL")
                result = cursor.fetchone()
                return result is not None and result[0] == 1
            finally:
                cursor.close()
        except Exception:
            logger.exception("Connection test failed")
            return False

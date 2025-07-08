"""SQL parsing utilities for Oracle databases."""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class SQLParser:
    """Parses and analyzes Oracle SQL statements."""

    def __init__(self) -> None:
        """Initialize SQL parser."""

    def parse_statement(self, sql: str) -> dict[str, Any]:
        """Parse a SQL statement and extract metadata.

        Args:
            sql: SQL statement to parse.

        Returns:
            Parsed SQL metadata.

        """
        sql = sql.strip()

        if not sql:
            return {"type": "empty", "valid": False}

        # Determine statement type
        statement_type = self._get_statement_type(sql)

        # Extract components based on type
        components = {}

        if statement_type == "SELECT":
            components = self._parse_select_statement(sql)
        elif statement_type == "INSERT":
            components = self._parse_insert_statement(sql)
        elif statement_type == "UPDATE":
            components = self._parse_update_statement(sql)
        elif statement_type == "DELETE":
            components = self._parse_delete_statement(sql)
        elif statement_type in {"CREATE", "ALTER", "DROP"}:
            components = self._parse_ddl_statement(sql, statement_type)

        return {
            "type": statement_type,
            "sql": sql,
            "valid": True,
            "components": components,
        }

    def extract_table_names(self, sql: str) -> list[str]:
        """Extract table names from a SQL statement.

        Args:
            sql: SQL statement.

        Returns:
            List of table names found in the statement.

        """
        # Simple regex-based extraction
        # (would need more sophisticated parsing for production)
        table_patterns = [
            r"FROM\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)",
            r"JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)",
            r"UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)",
            r"INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)",
            r"DELETE\s+FROM\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)",
        ]

        tables = set()
        sql_upper = sql.upper()

        for pattern in table_patterns:
            matches = re.finditer(pattern, sql_upper, re.IGNORECASE)
            for match in matches:
                table_name = match.group(1)
                # Remove schema prefix if present for consistency
                if "." in table_name:
                    table_name = table_name.split(".")[-1]
                tables.add(table_name.upper())

        return sorted(tables)

    def extract_column_names(self, sql: str) -> list[str]:
        """Extract column names from a SELECT statement.

        Args:
            sql: SQL SELECT statement.

        Returns:
            List of column names.

        """
        # Simplified extraction for demonstration
        if not sql.upper().strip().startswith("SELECT"):
            return []

        # Find the SELECT clause
        select_match = re.search(
            r"SELECT\s+(.*?)\s+FROM", sql, re.IGNORECASE | re.DOTALL
        )
        if not select_match:
            return []

        select_clause = select_match.group(1).strip()

        # Handle SELECT *
        if select_clause.strip() == "*":
            return ["*"]

        # Split by commas (simplified - doesn't handle functions properly)
        columns = []
        for col in select_clause.split(","):
            col = col.strip()
            # Extract column name (handle aliases)
            if " AS " in col.upper():
                col = col.split(" AS ")[1].strip()
            elif " " in col and not col.startswith("("):
                parts = col.split()
                col = parts[-1]  # Last part is usually the alias

            columns.append(col.strip())

        return columns

    def _get_statement_type(self, sql: str) -> str:
        """Determine the type of SQL statement."""
        sql_upper = sql.upper().strip()

        if sql_upper.startswith("SELECT"):
            return "SELECT"
        if sql_upper.startswith("INSERT"):
            return "INSERT"
        if sql_upper.startswith("UPDATE"):
            return "UPDATE"
        if sql_upper.startswith("DELETE"):
            return "DELETE"
        if sql_upper.startswith("CREATE"):
            return "CREATE"
        if sql_upper.startswith("ALTER"):
            return "ALTER"
        if sql_upper.startswith("DROP"):
            return "DROP"
        if sql_upper.startswith("TRUNCATE"):
            return "TRUNCATE"
        if sql_upper.startswith("MERGE"):
            return "MERGE"
        return "UNKNOWN"

    def _parse_select_statement(self, sql: str) -> dict[str, Any]:
        """Parse SELECT statement components."""
        return {
            "tables": self.extract_table_names(sql),
            "columns": self.extract_column_names(sql),
            "has_where": "WHERE" in sql.upper(),
            "has_group_by": "GROUP BY" in sql.upper(),
            "has_order_by": "ORDER BY" in sql.upper(),
            "has_join": any(
                join in sql.upper()
                for join in ["JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN"]
            ),
        }

    def _parse_insert_statement(self, sql: str) -> dict[str, Any]:
        """Parse INSERT statement components."""
        return {
            "tables": self.extract_table_names(sql),
            "has_values": "VALUES" in sql.upper(),
            "has_select": "SELECT" in sql.upper(),
        }

    def _parse_update_statement(self, sql: str) -> dict[str, Any]:
        """Parse UPDATE statement components."""
        return {
            "tables": self.extract_table_names(sql),
            "has_where": "WHERE" in sql.upper(),
            "has_join": "JOIN" in sql.upper(),
        }

    def _parse_delete_statement(self, sql: str) -> dict[str, Any]:
        """Parse DELETE statement components."""
        return {
            "tables": self.extract_table_names(sql),
            "has_where": "WHERE" in sql.upper(),
        }

    def _parse_ddl_statement(self, sql: str, statement_type: str) -> dict[str, Any]:
        """Parse DDL statement components."""
        return {
            "statement_type": statement_type,
            "tables": self.extract_table_names(sql),
        }

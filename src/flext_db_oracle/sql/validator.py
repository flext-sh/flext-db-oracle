"""SQL validation utilities for Oracle databases."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..connection.connection import OracleConnection

logger = logging.getLogger(__name__)


class SQLValidator:
    """Validates Oracle SQL statements for syntax and best practices."""

    def __init__(self, connection: OracleConnection | None = None) -> None:
        """Initialize SQL validator.

        Args:
            connection: Optional database connection for syntax validation.
        """
        self.connection = connection

    def validate_syntax(self, sql: str) -> dict[str, Any]:
        """Validate SQL syntax using database parser.

        Args:
            sql: SQL statement to validate.

        Returns:
            Syntax validation results.
        """
        if not self.connection:
            return {
                "status": "skipped",
                "message": "No database connection available for syntax validation",
            }

        try:
            # Use Oracle's EXPLAIN PLAN to validate syntax without execution
            validation_sql = f"EXPLAIN PLAN FOR {sql}"
            self.connection.execute(validation_sql)

            # Clean up plan table
            self.connection.execute("DELETE FROM plan_table WHERE statement_id IS NULL")

            return {
                "status": "valid",
                "message": "SQL syntax is valid",
            }

        except Exception as e:
            error_msg = str(e)
            return {
                "status": "invalid",
                "message": "SQL syntax error",
                "error": error_msg,
            }

    def validate_best_practices(self, sql: str) -> dict[str, Any]:
        """Validate SQL against best practices.

        Args:
            sql: SQL statement to validate.

        Returns:
            Best practices validation results.
        """
        violations = []
        warnings = []

        sql_upper = sql.upper().strip()

        # Check for dangerous operations
        if ("DROP " in sql_upper or "TRUNCATE " in sql_upper):
            violations.append({
                "severity": "critical",
                "rule": "dangerous_operation",
                "message": "DROP or TRUNCATE operations detected",
                "recommendation": "Use with extreme caution",
            })

        # Check for UPDATE/DELETE without WHERE
        if ("UPDATE " in sql_upper and "WHERE " not in sql_upper):
            violations.append({
                "severity": "high",
                "rule": "update_without_where",
                "message": "UPDATE statement without WHERE clause",
                "recommendation": "Add WHERE clause to limit affected rows",
            })

        if ("DELETE " in sql_upper and "WHERE " not in sql_upper):
            violations.append({
                "severity": "high",
                "rule": "delete_without_where",
                "message": "DELETE statement without WHERE clause",
                "recommendation": "Add WHERE clause to limit affected rows",
            })

        # Check for SELECT *
        if "SELECT *" in sql_upper:
            warnings.append({
                "severity": "medium",
                "rule": "select_star",
                "message": "SELECT * used instead of specific columns",
                "recommendation": "Specify only needed columns for better performance",
            })

        # Check for missing table aliases in joins
        if ("JOIN " in sql_upper and
            not re.search(r'\w+\s+[a-zA-Z]\w*\s+ON', sql, re.IGNORECASE)):
            warnings.append({
                "severity": "low",
                "rule": "missing_table_aliases",
                "message": "JOIN without table aliases",
                "recommendation": "Use table aliases for better readability",
            })

        # Check for hardcoded values
        if re.search(r"=\s*'[^']*'", sql):
            warnings.append({
                "severity": "low",
                "rule": "hardcoded_values",
                "message": "Hardcoded string values detected",
                "recommendation": "Consider using bind variables for better performance",
            })

        # Check for functions in WHERE clause
        function_patterns = [
            r"WHERE\s+\w*\([^)]*\)\s*[=<>]",
            r"WHERE\s+UPPER\(",
            r"WHERE\s+LOWER\(",
            r"WHERE\s+SUBSTR\(",
            r"WHERE\s+TO_CHAR\(",
        ]

        for pattern in function_patterns:
            if re.search(pattern, sql_upper):
                warnings.append({
                    "severity": "medium",
                    "rule": "function_in_where",
                    "message": "Function used in WHERE clause",
                    "recommendation": "Consider function-based indexes or query rewrite",
                })
                break

        # Check for OR conditions in WHERE
        if " OR " in sql_upper and "WHERE " in sql_upper:
            warnings.append({
                "severity": "medium",
                "rule": "or_conditions",
                "message": "OR conditions in WHERE clause",
                "recommendation": "Consider rewriting with UNION for better performance",
            })

        # Check for implicit data type conversions
        if re.search(r"=\s*\d+\s*", sql) and "VARCHAR" in sql_upper:
            warnings.append({
                "severity": "low",
                "rule": "implicit_conversion",
                "message": "Potential implicit data type conversion",
                "recommendation": "Ensure data types match to avoid performance issues",
            })

        return {
            "status": "completed",
            "sql": sql,
            "violations": violations,
            "warnings": warnings,
            "violation_count": len(violations),
            "warning_count": len(warnings),
            "overall_score": self._calculate_score(violations, warnings),
        }

    def validate_table_access(self, sql: str, allowed_schemas: list[str] | None = None) -> dict[str, Any]:
        """Validate table access permissions.

        Args:
            sql: SQL statement to validate.
            allowed_schemas: List of allowed schema names.

        Returns:
            Table access validation results.
        """
        if not allowed_schemas:
            return {
                "status": "skipped",
                "message": "No schema restrictions configured",
            }

        # Extract table references
        table_patterns = [
            r"FROM\s+([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)",
            r"JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)",
            r"UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)",
            r"INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)",
            r"DELETE\s+FROM\s+([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)",
        ]

        violations = []
        sql_upper = sql.upper()

        for pattern in table_patterns:
            matches = re.finditer(pattern, sql_upper, re.IGNORECASE)
            for match in matches:
                table_ref = match.group(1)
                schema_name = table_ref.split(".")[0]

                if schema_name.upper() not in [s.upper() for s in allowed_schemas]:
                    violations.append({
                        "table": table_ref,
                        "schema": schema_name,
                        "message": f"Access to schema '{schema_name}' not allowed",
                    })

        return {
            "status": "completed",
            "sql": sql,
            "allowed_schemas": allowed_schemas,
            "violations": violations,
            "access_allowed": len(violations) == 0,
        }

    def _calculate_score(self, violations: list[dict[str, Any]], warnings: list[dict[str, Any]]) -> int:
        """Calculate overall quality score (0-100)."""
        score = 100

        # Deduct points for violations
        for violation in violations:
            if violation["severity"] == "critical":
                score -= 30
            elif violation["severity"] == "high":
                score -= 20
            elif violation["severity"] == "medium":
                score -= 10
            elif violation["severity"] == "low":
                score -= 5

        # Deduct points for warnings
        for warning in warnings:
            if warning["severity"] == "high":
                score -= 10
            elif warning["severity"] == "medium":
                score -= 5
            elif warning["severity"] == "low":
                score -= 2

        return max(0, score)

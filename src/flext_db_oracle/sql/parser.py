"""SQL parsing utilities for Oracle databases.

Built on flext-core foundation for robust SQL parsing and analysis.
Uses ServiceResult pattern and modern Python 3.13 typing.
"""

from __future__ import annotations

import re
from typing import Any

from flext_core import DomainValueObject, Field, ServiceResult
from flext_observability.logging import get_logger

logger = get_logger(__name__)

# Constants
MAX_SQL_LENGTH_WARNING = 10000


class ParsedStatement(DomainValueObject):
    """Represents a parsed SQL statement."""

    statement_type: str = Field(..., description="Type of SQL statement")
    sql_text: str = Field(..., description="Original SQL text")
    is_valid: bool = Field(default=True, description="Whether the SQL is valid")
    tables: list[str] = Field(
        default_factory=list,
        description="Referenced table names",
    )
    columns: list[str] = Field(
        default_factory=list,
        description="Referenced column names",
    )
    where_conditions: list[str] = Field(
        default_factory=list,
        description="WHERE clause conditions",
    )
    joins: list[str] = Field(default_factory=list, description="JOIN clauses")
    complexity_score: int = Field(0, description="Statement complexity score", ge=0)

    @property
    def is_query(self) -> bool:
        """Check if this is a query statement."""
        return self.statement_type.upper() == "SELECT"

    @property
    def is_dml(self) -> bool:
        """Check if this is a data manipulation statement."""
        return self.statement_type.upper() in {"INSERT", "UPDATE", "DELETE"}

    @property
    def is_ddl(self) -> bool:
        """Check if this is a data definition statement."""
        return self.statement_type.upper() in {"CREATE", "ALTER", "DROP"}


class SQLParser:
    """Parses and analyzes Oracle SQL statements using flext-core patterns."""

    def __init__(self) -> None:
        """Initialize the SQL parser.

        Sets up regex patterns for parsing SQL statements and extracting components.
        """
        # SQL keyword patterns
        self.statement_patterns = {
            "SELECT": re.compile(r"^\s*SELECT\s+", re.IGNORECASE),
            "INSERT": re.compile(r"^\s*INSERT\s+", re.IGNORECASE),
            "UPDATE": re.compile(r"^\s*UPDATE\s+", re.IGNORECASE),
            "DELETE": re.compile(r"^\s*DELETE\s+", re.IGNORECASE),
            "CREATE": re.compile(r"^\s*CREATE\s+", re.IGNORECASE),
            "ALTER": re.compile(r"^\s*ALTER\s+", re.IGNORECASE),
            "DROP": re.compile(r"^\s*DROP\s+", re.IGNORECASE),
        }

        # Table name extraction patterns
        self.table_patterns = {
            "FROM": re.compile(
                r"\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)",
                re.IGNORECASE,
            ),
            "JOIN": re.compile(
                r"\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)",
                re.IGNORECASE,
            ),
            "UPDATE": re.compile(
                r"^\s*UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)",
                re.IGNORECASE,
            ),
            "INSERT": re.compile(
                r"^\s*INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)",
                re.IGNORECASE,
            ),
        }

    async def parse_statement(self, sql: str) -> ServiceResult[ParsedStatement]:
        """Parse a SQL statement and extract components."""
        try:
            sql = sql.strip()

            if not sql:
                return ServiceResult.fail("Empty SQL statement")

            logger.info("Parsing SQL statement")

            # Determine statement type
            statement_type = self._get_statement_type(sql)
            if not statement_type:
                return ServiceResult.fail("Could not determine statement type")

            # Extract components
            tables = self._extract_table_names(sql)
            columns = self._extract_column_names(sql)
            where_conditions = self._extract_where_conditions(sql)
            joins = self._extract_joins(sql)

            # Calculate complexity
            complexity = self._calculate_complexity(
                sql,
                tables,
                joins,
                where_conditions,
            )

            parsed = ParsedStatement(
                statement_type=statement_type,
                sql_text=sql,
                is_valid=True,
                tables=tables,
                columns=columns,
                where_conditions=where_conditions,
                joins=joins,
                complexity_score=complexity,
            )

            logger.info("SQL statement parsed successfully: %s", statement_type)
            return ServiceResult.ok(parsed)

        except Exception as e:
            logger.exception("SQL parsing failed")
            return ServiceResult.fail(f"SQL parsing failed: {e}")

    def _get_statement_type(self, sql: str) -> str | None:
        """Determine the type of SQL statement."""
        for stmt_type, pattern in self.statement_patterns.items():
            if pattern.match(sql):
                return stmt_type
        return None

    def _extract_table_names(self, sql: str) -> list[str]:
        """Extract table names from SQL statement."""
        tables = set()

        for pattern in self.table_patterns.values():
            matches = pattern.findall(sql)
            for match in matches:
                # Remove schema prefix if present
                table_name = match.split(".")[-1]
                tables.add(table_name.upper())

        return list(tables)

    def _extract_column_names(self, sql: str) -> list[str]:
        """Extract column names from SQL statement."""
        columns = []

        # Extract from SELECT clause
        select_match = re.search(
            r"SELECT\s+(.*?)\s+FROM",
            sql,
            re.IGNORECASE | re.DOTALL,
        )
        if select_match:
            select_clause = select_match.group(1)
            # Simple column extraction (would need more sophisticated parsing)
            column_parts = select_clause.split(",")
            for part in column_parts:
                clean_part = part.strip()
                if clean_part and clean_part != "*":
                    # Extract just the column name (remove aliases, functions)
                    column_name = re.sub(
                        r"\s+AS\s+.*",
                        "",
                        clean_part,
                        flags=re.IGNORECASE,
                    )
                    column_name = re.sub(
                        r".*\.",
                        "",
                        column_name,
                    )  # Remove table prefix
                    columns.append(column_name.strip())

        return columns

    def _extract_where_conditions(self, sql: str) -> list[str]:
        """Extract WHERE clause conditions."""
        conditions = []

        # Extract WHERE clause
        where_match = re.search(
            r"\bWHERE\s+(.*?)(?:\s+(?:GROUP\s+BY|ORDER\s+BY|HAVING|$))",
            sql,
            re.IGNORECASE | re.DOTALL,
        )
        if where_match:
            where_clause = where_match.group(1).strip()
            # Split on AND/OR (simple approach)
            condition_parts = re.split(
                r"\s+(?:AND|OR)\s+",
                where_clause,
                flags=re.IGNORECASE,
            )
            conditions = [cond.strip() for cond in condition_parts if cond.strip()]

        return conditions

    def _extract_joins(self, sql: str) -> list[str]:
        """Extract JOIN clauses."""
        joins = []

        # Extract different types of JOINs
        join_patterns = [
            r"(INNER\s+JOIN\s+[^\\s]+(?:\s+ON\s+[^\\s]+)?)",
            r"(LEFT\s+(?:OUTER\s+)?JOIN\s+[^\\s]+(?:\s+ON\s+[^\\s]+)?)",
            r"(RIGHT\s+(?:OUTER\s+)?JOIN\s+[^\\s]+(?:\s+ON\s+[^\\s]+)?)",
            r"(FULL\s+(?:OUTER\s+)?JOIN\s+[^\\s]+(?:\s+ON\s+[^\\s]+)?)",
            r"(JOIN\s+[^\\s]+(?:\s+ON\s+[^\\s]+)?)",
        ]

        for pattern in join_patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            joins.extend(matches)

        return joins

    def _calculate_complexity(
        self,
        sql: str,
        tables: list[str],
        joins: list[str],
        conditions: list[str],
    ) -> int:
        """Calculate statement complexity score."""
        score = 0

        # Base complexity
        score += len(sql) // 100  # 1 point per 100 characters

        # Table complexity
        score += len(tables) * 2  # 2 points per table

        # Join complexity
        score += len(joins) * 5  # 5 points per join

        # Condition complexity
        score += len(conditions) * 3  # 3 points per condition

        # Subquery complexity
        subquery_count = sql.upper().count("SELECT") - 1  # Subtract main SELECT
        score += subquery_count * 10  # 10 points per subquery

        # Function complexity
        function_patterns = [
            r"\bCOUNT\s*\(",
            r"\bSUM\s*\(",
            r"\bAVG\s*\(",
            r"\bMAX\s*\(",
            r"\bMIN\s*\(",
            r"\bCASE\s+",
            r"\bDECODE\s*\(",
        ]

        for pattern in function_patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            score += len(matches) * 2  # 2 points per function

        return score

    async def validate_syntax(self, sql: str) -> ServiceResult[dict[str, Any]]:
        """Perform basic SQL syntax validation."""
        try:
            validation_result: dict[str, Any] = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
            }

            # Basic syntax checks
            if not sql.strip():
                validation_result["is_valid"] = False
                validation_result["errors"].append("Empty SQL statement")
                return ServiceResult.ok(validation_result)

            # Check for balanced parentheses
            if sql.count("(") != sql.count(")"):
                validation_result["is_valid"] = False
                validation_result["errors"].append("Unbalanced parentheses")

            # Check for basic SQL structure
            statement_type = self._get_statement_type(sql)
            if not statement_type:
                validation_result["is_valid"] = False
                validation_result["errors"].append("Invalid SQL statement type")

            # Check for required clauses
            if statement_type == "SELECT" and not re.search(
                r"\bFROM\b",
                sql,
                re.IGNORECASE,
            ):
                validation_result["warnings"].append("SELECT without FROM clause")

            # Check for potential issues
            if re.search(r"SELECT\s+\*", sql, re.IGNORECASE):
                validation_result["warnings"].append("SELECT * may impact performance")

            if len(sql) > MAX_SQL_LENGTH_WARNING:
                validation_result["warnings"].append("Very long SQL statement")

            logger.info("SQL syntax validation completed")
            return ServiceResult.ok(validation_result)

        except Exception as e:
            logger.exception("SQL syntax validation failed")
            return ServiceResult.fail(f"Syntax validation failed: {e}")

    async def analyze_statement(self, sql: str) -> ServiceResult[dict[str, Any]]:
        """Perform comprehensive SQL statement analysis."""
        try:
            # Parse the statement
            parse_result = await self.parse_statement(sql)
            if not parse_result.is_success:
                return ServiceResult.fail(parse_result.error or "Parse failed")

            parsed = parse_result.data
            if parsed is None:
                return ServiceResult.fail("Failed to parse SQL statement")

            # Validate syntax
            validation_result = await self.validate_syntax(sql)
            validation = validation_result.data if validation_result.is_success else {}

            analysis = {
                "statement_type": parsed.statement_type,
                "complexity_score": parsed.complexity_score,
                "table_count": len(parsed.tables),
                "join_count": len(parsed.joins),
                "condition_count": len(parsed.where_conditions),
                "is_query": parsed.is_query,
                "is_dml": parsed.is_dml,
                "is_ddl": parsed.is_ddl,
                "tables": parsed.tables,
                "columns": parsed.columns,
                "validation": validation,
            }

            logger.info("SQL statement analysis completed")
            return ServiceResult.ok(analysis)

        except Exception as e:
            logger.exception("SQL statement analysis failed")
            return ServiceResult.fail(f"Statement analysis failed: {e}")

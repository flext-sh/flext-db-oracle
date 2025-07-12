"""Oracle SQL statement validation utilities.

Built on flext-core foundation for comprehensive SQL validation.
Uses ServiceResult pattern and modern Python 3.13 typing.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from pydantic import Field

from flext_core import DomainValueObject, ServiceResult
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_db_oracle.sql.parser import SQLParser

logger = get_logger(__name__)

# Constants
MAX_REASONABLE_ISSUES = 5


class ValidationRule(DomainValueObject):
    """Represents a SQL validation rule."""

    rule_id: str = Field(..., description="Unique rule identifier")
    rule_name: str = Field(..., description="Human-readable rule name")
    severity: str = Field(..., description="Rule severity (ERROR, WARNING, INFO)")
    description: str = Field(..., description="Rule description")
    pattern: str | None = Field(None, description="Regex pattern for the rule")

    @property
    def is_error(self) -> bool:
        """Check if this is an error-level rule."""
        return self.severity.upper() == "ERROR"

    @property
    def is_warning(self) -> bool:
        """Check if this is a warning-level rule."""
        return self.severity.upper() == "WARNING"


class ValidationResult(DomainValueObject):
    """Result of SQL validation."""

    is_valid: bool = Field(..., description="Whether SQL is valid")
    errors: list[str] = Field(default_factory=list, description="Error messages")
    warnings: list[str] = Field(default_factory=list, description="Warning messages")
    info: list[str] = Field(default_factory=list, description="Informational messages")
    rules_checked: int = Field(0, description="Number of rules checked", ge=0)

    @property
    def has_errors(self) -> bool:
        """Check if validation found errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if validation found warnings."""
        return len(self.warnings) > 0

    @property
    def total_issues(self) -> int:
        """Get total number of issues found."""
        return len(self.errors) + len(self.warnings) + len(self.info)


class SQLValidator:
    """Validates Oracle SQL statements for syntax and best practices using flext-core patterns."""

    def __init__(self, sql_parser: SQLParser | None = None) -> None:
        self.sql_parser = sql_parser
        self.validation_rules = self._initialize_rules()

    def _initialize_rules(self) -> list[ValidationRule]:
        """Initialize validation rules."""
        return [
            ValidationRule(
                rule_id="SELECT_STAR",
                rule_name="Avoid SELECT *",
                severity="WARNING",
                description="SELECT * can impact performance and maintainability",
                pattern=r"SELECT\s+\*",
            ),
            ValidationRule(
                rule_id="MISSING_WHERE",
                rule_name="Missing WHERE clause",
                severity="WARNING",
                description="UPDATE/DELETE without WHERE clause affects all rows",
                pattern=r"^(UPDATE|DELETE)(?!.*WHERE)",
            ),
            ValidationRule(
                rule_id="UNQUALIFIED_COLUMNS",
                rule_name="Unqualified column names",
                severity="INFO",
                description="Use table aliases for better readability",
                pattern=None,  # Complex logic required
            ),
            ValidationRule(
                rule_id="MISSING_INDEXES",
                rule_name="Potential missing indexes",
                severity="INFO",
                description="Consider adding indexes for WHERE clause columns",
                pattern=None,  # Complex logic required
            ),
            ValidationRule(
                rule_id="LONG_IN_LIST",
                rule_name="Long IN list",
                severity="WARNING",
                description="Very long IN lists can impact performance",
                pattern=r"IN\s*\([^)]{200,}\)",
            ),
            ValidationRule(
                rule_id="NESTED_SUBQUERIES",
                rule_name="Deeply nested subqueries",
                severity="WARNING",
                description="Consider using JOINs instead of nested subqueries",
                pattern=None,  # Complex logic required
            ),
            ValidationRule(
                rule_id="FUNCTION_IN_WHERE",
                rule_name="Function in WHERE clause",
                severity="INFO",
                description="Functions in WHERE clause may prevent index usage",
                pattern=r"WHERE.*\w+\s*\(",
            ),
        ]

    async def validate_sql(self, sql: str) -> ServiceResult[ValidationResult]:
        """Validate SQL statement against all rules."""
        try:
            logger.info("Starting SQL validation")

            errors = []
            warnings = []
            info = []
            rules_checked = 0

            # Basic syntax validation
            if not sql.strip():
                errors.append("Empty SQL statement")
                return ServiceResult.success(ValidationResult(
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    info=info,
                    rules_checked=1,
                ))

            # Check each validation rule
            for rule in self.validation_rules:
                rules_checked += 1
                issue = await self._check_rule(sql, rule)

                if issue:
                    if rule.is_error:
                        errors.append(issue)
                    elif rule.is_warning:
                        warnings.append(issue)
                    else:
                        info.append(issue)

            # Additional syntax checks
            syntax_issues = await self._check_basic_syntax(sql)
            errors.extend(syntax_issues)

            is_valid = len(errors) == 0

            result = ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                info=info,
                rules_checked=rules_checked,
            )

            logger.info("SQL validation completed: %d issues found", result.total_issues)
            return ServiceResult.success(result)

        except Exception as e:
            logger.exception("SQL validation failed: %s", e)
            return ServiceResult.failure(f"SQL validation failed: {e}")

    async def _check_rule(self, sql: str, rule: ValidationRule) -> str | None:
        """Check a specific validation rule."""
        try:
            if rule.pattern:
                # Pattern-based rule
                if re.search(rule.pattern, sql, re.IGNORECASE | re.MULTILINE):
                    return f"{rule.rule_name}: {rule.description}"

            # Special logic for complex rules
            if rule.rule_id == "UNQUALIFIED_COLUMNS":
                return await self._check_unqualified_columns(sql)
            if rule.rule_id == "MISSING_INDEXES":
                return await self._check_missing_indexes(sql)
            if rule.rule_id == "NESTED_SUBQUERIES":
                return await self._check_nested_subqueries(sql)

            return None

        except Exception as e:
            logger.warning("Rule check failed for %s: %s", rule.rule_id, e)
            return None

    async def _check_basic_syntax(self, sql: str) -> list[str]:
        """Check basic SQL syntax issues."""
        errors = []

        # Check balanced parentheses
        if sql.count("(") != sql.count(")"):
            errors.append("Unbalanced parentheses in SQL statement")

        # Check balanced quotes
        single_quotes = sql.count("'")
        if single_quotes % 2 != 0:
            errors.append("Unmatched single quotes in SQL statement")

        # Check for common typos
        if re.search(r"\bFORM\b", sql, re.IGNORECASE):
            errors.append("Possible typo: 'FORM' instead of 'FROM'")

        if re.search(r"\bSELECT\s*\*\s*FORM\b", sql, re.IGNORECASE):
            errors.append("Syntax error: 'FORM' should be 'FROM'")

        return errors

    async def _check_unqualified_columns(self, sql: str) -> str | None:
        """Check for unqualified column names in multi-table queries."""
        try:
            # Look for JOINs or multiple tables in FROM
            has_joins = bool(re.search(r"\bJOIN\b", sql, re.IGNORECASE))
            from_tables = re.findall(r"\bFROM\s+([^,\s]+(?:\s*,\s*[^,\s]+)*)", sql, re.IGNORECASE)
            has_multiple_tables = any("," in table_list for table_list in from_tables)

            if has_joins or has_multiple_tables:
                # Look for unqualified columns (simple heuristic)
                select_clause = re.search(r"SELECT\s+(.*?)\s+FROM", sql, re.IGNORECASE | re.DOTALL)
                if select_clause:
                    columns = select_clause.group(1)
                    # Check for columns without table qualifiers
                    unqualified = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b(?!\s*\()", columns)
                    if unqualified and not any("." in col for col in unqualified):
                        return "Consider qualifying column names with table aliases in multi-table queries"

            return None

        except Exception:
            return None

    async def _check_missing_indexes(self, sql: str) -> str | None:
        """Check for potential missing indexes."""
        try:
            # Look for WHERE clauses that might benefit from indexes
            where_match = re.search(r"\bWHERE\s+(.*?)(?:\s+(?:GROUP|ORDER|HAVING|$))", sql, re.IGNORECASE | re.DOTALL)
            if where_match:
                where_clause = where_match.group(1)
                # Look for equality conditions
                equality_conditions = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=", where_clause, re.IGNORECASE)
                if len(equality_conditions) > 2:
                    return "Consider creating composite indexes for multiple WHERE conditions"

            return None

        except Exception:
            return None

    async def _check_nested_subqueries(self, sql: str) -> str | None:
        """Check for deeply nested subqueries."""
        try:
            # Count SELECT statements to detect nesting
            select_count = len(re.findall(r"\bSELECT\b", sql, re.IGNORECASE))
            if select_count > 3:
                return "Consider using JOINs instead of deeply nested subqueries for better performance"

            return None

        except Exception:
            return None

    async def validate_with_recommendations(self, sql: str) -> ServiceResult[dict[str, Any]]:
        """Validate SQL and provide improvement recommendations."""
        try:
            # Perform validation
            validation_result = await self.validate_sql(sql)
            if validation_result.is_failure:
                return validation_result

            validation = validation_result.value

            # Generate recommendations
            recommendations = []

            if validation.has_errors:
                recommendations.append("Fix syntax errors before proceeding")

            if validation.has_warnings:
                recommendations.append("Address performance and maintainability warnings")

            # Additional recommendations based on SQL analysis
            if self.sql_parser:
                parse_result = await self.sql_parser.parse_statement(sql)
                if parse_result.is_success:
                    parsed = parse_result.value

                    if parsed.complexity_score > 50:
                        recommendations.append("Consider breaking down complex query into simpler parts")

                    if len(parsed.tables) > 5:
                        recommendations.append("Review if all tables are necessary for this query")

                    if len(parsed.joins) > 3:
                        recommendations.append("Verify that all JOINs are using appropriate indexes")

            result = {
                "validation": validation.model_dump(),
                "recommendations": recommendations,
                "summary": {
                    "is_valid": validation.is_valid,
                    "total_issues": validation.total_issues,
                    "severity_breakdown": {
                        "errors": len(validation.errors),
                        "warnings": len(validation.warnings),
                        "info": len(validation.info),
                    },
                },
            }

            logger.info("SQL validation with recommendations completed")
            return ServiceResult.success(result)

        except Exception as e:
            logger.exception("SQL validation with recommendations failed: %s", e)
            return ServiceResult.failure(f"Validation with recommendations failed: {e}")

    async def get_best_practices_report(self, sql: str) -> ServiceResult[dict[str, Any]]:
        """Generate a comprehensive best practices report."""
        try:
            validation_result = await self.validate_with_recommendations(sql)
            if validation_result.is_failure:
                return validation_result

            validation_data = validation_result.value

            # Best practices checklist
            checklist = {
                "uses_specific_columns": not bool(re.search(r"SELECT\s+\*", sql, re.IGNORECASE)),
                "has_where_clause": bool(re.search(r"\bWHERE\b", sql, re.IGNORECASE)),
                "uses_table_aliases": bool(re.search(r"\b[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s+ON\b", sql, re.IGNORECASE)),
                "avoids_functions_in_where": not bool(re.search(r"WHERE.*\w+\s*\(", sql, re.IGNORECASE)),
                "has_reasonable_complexity": validation_data.get("summary", {}).get("total_issues", 0) < MAX_REASONABLE_ISSUES,
            }

            score = sum(checklist.values()) / len(checklist) * 100

            report = {
                "validation_results": validation_data,
                "best_practices_checklist": checklist,
                "best_practices_score": round(score, 1),
                "grade": self._get_grade(score),
                "improvement_suggestions": self._get_improvement_suggestions(checklist),
            }

            logger.info("Best practices report generated with score: %.1f", score)
            return ServiceResult.success(report)

        except Exception as e:
            logger.exception("Best practices report generation failed: %s", e)
            return ServiceResult.failure(f"Best practices report failed: {e}")

    def _get_grade(self, score: float) -> str:
        """Get letter grade based on score."""
        # Grade thresholds
        GRADE_A_THRESHOLD = 90
        GRADE_B_THRESHOLD = 80
        GRADE_C_THRESHOLD = 70
        GRADE_D_THRESHOLD = 60

        if score >= GRADE_A_THRESHOLD:
            return "A"
        if score >= GRADE_B_THRESHOLD:
            return "B"
        if score >= GRADE_C_THRESHOLD:
            return "C"
        if score >= GRADE_D_THRESHOLD:
            return "D"
        return "F"

    def _get_improvement_suggestions(self, checklist: dict[str, bool]) -> list[str]:
        """Get improvement suggestions based on checklist."""
        suggestions = []

        if not checklist["uses_specific_columns"]:
            suggestions.append("Replace SELECT * with specific column names")

        if not checklist["has_where_clause"]:
            suggestions.append("Add WHERE clause to limit result set")

        if not checklist["uses_table_aliases"]:
            suggestions.append("Use table aliases for better readability")

        if not checklist["avoids_functions_in_where"]:
            suggestions.append("Move functions out of WHERE clause when possible")

        if not checklist["has_reasonable_complexity"]:
            suggestions.append("Simplify query to reduce complexity")

        return suggestions

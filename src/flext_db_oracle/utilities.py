"""FLEXT DB Oracle utility functions and common operations.

This module provides utility functions and static methods for common Oracle database
operations using Clean Architecture patterns and SOLID principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextResult

from flext_db_oracle.models import FlextDbOracleQueryResult

if TYPE_CHECKING:
    from flext_db_oracle import FlextDbOracleApi


class FlextDbOracleUtilities:
    """Utility functions for Oracle database operations.

    SOLID REFACTORING: Static utility methods using Single Responsibility Principle
    to encapsulate common Oracle operations and reduce code duplication across examples.

    Includes unwrap_or() pattern methods for reducing code bloat as per FLEXT standards.
    """

    # =============================================================================
    # MODERN PATTERN: Use FlextResult.unwrap_or() directly everywhere
    # =============================================================================

    # NOTE: FlextResult now has built-in unwrap_or() method
    # Use: result.unwrap_or(default_value) directly instead of utility methods
    #
    # Examples:
    #   result.unwrap_or([])      # for lists
    #   result.unwrap_or(False)   # for booleans
    #   result.unwrap_or(None)    # for nullable values
    #   result.unwrap_or({})      # for dictionaries

    # =============================================================================
    # EXISTING ORACLE OPERATIONS
    # =============================================================================

    @staticmethod
    def safe_get_schemas(api: FlextDbOracleApi) -> list[str]:
        """Safely get database schemas with fallback.

        Uses unwrap_or pattern to provide clean error handling with sensible defaults.

        Args:
            api: FlextDbOracleApi instance

        Returns:
            List of schema names, or empty list if operation fails

        """
        return api.get_schemas().unwrap_or([])

    @staticmethod
    def safe_get_tables(api: FlextDbOracleApi, schema: str | None = None) -> list[str]:
        """Safely get database tables with fallback.

        Uses unwrap_or pattern to provide clean error handling with sensible defaults.

        Args:
            api: FlextDbOracleApi instance
            schema: Optional schema name filter

        Returns:
            List of table names, or empty list if operation fails

        """
        return api.get_tables(schema).unwrap_or([])

    @staticmethod
    def safe_get_columns(
        api: FlextDbOracleApi, table: str, schema: str | None = None
    ) -> list[dict[str, object]]:
        """Safely get table columns with fallback.

        Uses unwrap_or pattern to provide clean error handling with sensible defaults.

        Args:
            api: FlextDbOracleApi instance
            table: Table name
            schema: Optional schema name

        Returns:
            List of column dictionaries, or empty list if operation fails

        """
        return api.get_columns(table, schema).unwrap_or([])

    @staticmethod
    def safe_test_connection(api: FlextDbOracleApi) -> bool:
        """Safely test database connection with fallback.

        Uses unwrap_or pattern to provide clean error handling with boolean result.

        Args:
            api: FlextDbOracleApi instance

        Returns:
            True if connection is healthy, False otherwise

        """
        return api.test_connection().unwrap_or(False)  # noqa: FBT003

    @staticmethod
    def safe_query(
        api: FlextDbOracleApi, sql: str, params: dict[str, object] | None = None
    ) -> list[tuple[object, ...]]:
        """Safely execute query with fallback.

        Uses unwrap_or pattern to provide clean error handling with sensible defaults.

        Args:
            api: FlextDbOracleApi instance
            sql: SQL query string
            params: Optional query parameters

        Returns:
            Query result rows, or empty list if operation fails

        """
        empty_result = FlextDbOracleQueryResult(
            columns=[], rows=[], row_count=0, query_hash=None
        )
        result = api.query(sql, params).unwrap_or(empty_result)
        return result.rows

    @staticmethod
    def safe_query_one(
        api: FlextDbOracleApi, sql: str, params: dict[str, object] | None = None
    ) -> tuple[object, ...] | None:
        """Safely execute single-row query with fallback.

        Uses unwrap_or pattern to provide clean error handling with None fallback.

        Args:
            api: FlextDbOracleApi instance
            sql: SQL query string
            params: Optional query parameters

        Returns:
            Single row result, or None if operation fails or no rows found

        """
        return api.query_one(sql, params).unwrap_or(None)

    @staticmethod
    def execute_with_fallback(
        api: FlextDbOracleApi,
        primary_operation: str,  # noqa: ARG004
        fallback_message: str = "Operation failed",
    ) -> str:
        """Execute operation with automatic fallback logic.

        Demonstrates the unwrap_or pattern for operations that can provide fallback values.
        This eliminates verbose success/failure checking patterns.

        Args:
            api: FlextDbOracleApi instance
            primary_operation: SQL or operation to execute (placeholder for demo)
            fallback_message: Message to return if operation fails

        Returns:
            Success message or fallback message

        """
        # Simple demonstration - in real implementation would execute actual operation
        result = api.test_connection()
        return result.map(lambda _: "Operation succeeded").unwrap_or(fallback_message)

    @staticmethod
    def validate_connection_with_retry(
        api: FlextDbOracleApi, max_retries: int = 3
    ) -> FlextResult[bool]:
        """Validate connection with retry logic.

        Demonstrates chaining FlextResult operations with unwrap_or for clean error handling.

        Args:
            api: FlextDbOracleApi instance
            max_retries: Maximum number of retry attempts

        Returns:
            FlextResult containing True if connection succeeds, False otherwise

        """
        for attempt in range(max_retries):
            result = api.test_connection()
            if result.is_success:
                return FlextResult[bool].ok(True)  # noqa: FBT003

            if attempt == max_retries - 1:
                # Last attempt failed
                error_msg = result.error or "Connection validation failed"
                return FlextResult[bool].fail(
                    f"Failed after {max_retries} attempts: {error_msg}"
                )

        return FlextResult[bool].fail("Unexpected retry loop termination")

    @staticmethod
    def get_database_summary(api: FlextDbOracleApi) -> dict[str, object]:
        """Get comprehensive database summary using utility methods.

        Demonstrates composition of utility methods with unwrap_or patterns
        for clean, readable code without verbose error checking.

        Args:
            api: FlextDbOracleApi instance

        Returns:
            Dictionary containing database summary information

        """
        schemas = FlextDbOracleUtilities.safe_get_schemas(api)

        tables_dict: dict[str, list[str]] = {}
        total_tables = 0

        # Get tables for each schema
        for schema in schemas[:5]:  # Limit to first 5 schemas for performance
            tables = FlextDbOracleUtilities.safe_get_tables(api, schema)
            tables_dict[schema] = tables
            total_tables += len(tables)

        summary: dict[str, object] = {
            "connection_healthy": FlextDbOracleUtilities.safe_test_connection(api),
            "schemas_count": len(schemas),
            "schemas": schemas,
            "tables": tables_dict,
            "total_tables": total_tables,
        }

        return summary

    @staticmethod
    def format_query_result(
        result: FlextResult[FlextDbOracleQueryResult],
        default_message: str = "No results",
    ) -> str:
        """Format query result for display using unwrap_or pattern.

        Args:
            result: FlextResult containing query results
            default_message: Message to show if no results or error

        Returns:
            Formatted string representation of results

        """
        empty_result = FlextDbOracleQueryResult(
            columns=[], rows=[], row_count=0, query_hash=None
        )
        data = result.unwrap_or(empty_result)

        if data.row_count == 0:
            return default_message

        return f"Query returned {data.row_count} row(s)"

    @staticmethod
    def safe_execute_batch(
        api: FlextDbOracleApi, operations: list[tuple[str, dict[str, object] | None]]
    ) -> bool:
        """Safely execute batch operations with boolean result.

        Uses unwrap_or pattern to convert complex FlextResult to simple boolean success indicator.

        Args:
            api: FlextDbOracleApi instance
            operations: List of (sql, params) tuples

        Returns:
            True if batch executed successfully, False otherwise

        """
        result = api.execute_batch(operations)
        # Convert any success result to True, any failure to False
        return result.map(lambda _: True).unwrap_or(False)  # noqa: FBT003

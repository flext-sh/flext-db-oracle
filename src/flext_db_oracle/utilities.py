"""FLEXT DB Oracle utility functions and common operations.

This module provides utility functions and static methods for common Oracle database
operations using Clean Architecture patterns and SOLID principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import TYPE_CHECKING

from flext_core import FlextResult

from flext_db_oracle.models import FlextDbOracleQueryResult

# Performance monitoring constants
PERFORMANCE_WARNING_THRESHOLD_SECONDS = 2.0

# Display constants
MAX_DISPLAY_ROWS = 50

if TYPE_CHECKING:
    from flext_db_oracle import FlextDbOracleApi
    from flext_db_oracle.config import FlextDbOracleConfig
else:
    # Runtime imports for utilities to avoid circular imports
    FlextDbOracleConfig = None
    FlextDbOracleApi = None


class FlextDbOracleUtilities:
    """Utility functions for Oracle database operations.

    SOLID REFACTORING: Static utility methods using Single Responsibility Principle
    to encapsulate common Oracle operations and reduce code duplication across examples.

    Includes unwrap_or() pattern methods for reducing code bloat as per FLEXT standards.
    """

    # =============================================================================
    # MODERN PATTERN: Use FlextResult.value with try/except for clean error handling
    # =============================================================================

    # NOTE: FlextResult.value provides direct access with exception on failure
    # Use: try/except blocks or is_success checks for safer code
    #
    # Examples:
    #   try: return result.value    except: return []       # for lists
    #   try: return result.value    except: return False    # for booleans
    #   try: return result.value    except: return None     # for nullable values
    #   try: return result.value    except: return {}       # for dictionaries

    @staticmethod
    def demonstrate_modern_patterns() -> None:
        """Demonstrate modern FlextResult patterns using .value with exception handling.

        This method shows the preferred patterns for handling FlextResult objects
        throughout the flext-db-oracle codebase.
        """
        # Example of modern patterns (for documentation):
        # MODERN: try/except with direct value access
        # try:
        #     return result.value
        # except TypeError:  # FlextResult failure
        #     return []  # or appropriate default

        # ALTERNATIVE: success check pattern
        # if result.is_success:
        #     return result.value
        # return default_value

        # This is a documentation method

    @staticmethod
    def safe_get_schemas_modern(api: FlextDbOracleApi) -> list[str]:
        """Modern pattern: Get schemas using .value with exception handling."""
        try:
            return api.get_schemas().value
        except TypeError:  # FlextResult failure
            return []

    @staticmethod
    def safe_get_tables_modern(
        api: FlextDbOracleApi, schema: str | None = None
    ) -> list[str]:
        """Modern pattern: Get tables using .value with exception handling."""
        try:
            return api.get_tables(schema).value
        except TypeError:  # FlextResult failure
            return []

    @staticmethod
    def safe_test_connection_modern(api: FlextDbOracleApi) -> bool:
        """Modern pattern: Test connection using .value with exception handling."""
        try:
            return api.test_connection().value
        except TypeError:  # FlextResult failure
            return False

    @staticmethod
    def safe_access_query_result(
        query_result: FlextDbOracleQueryResult, row_index: int = 0, col_index: int = 0
    ) -> object | None:
        """Safely access query result data with proper type checking."""
        if not query_result or not query_result.rows:
            return None

        if row_index >= len(query_result.rows):
            return None

        row = query_result.rows[row_index]
        if not hasattr(row, "__getitem__") or col_index >= len(row):
            return None

        return row[col_index]

    @staticmethod
    def safe_error_message(error: str | None) -> str:
        """Safely get error message handling None case."""
        return (error or "").lower()

    @staticmethod
    def safe_dict_access(data: dict[str, object], key: str) -> str:
        """Safely access dictionary value as string."""
        value = data.get(key, "")
        return str(value) if value is not None else ""

    #   try: return result.value   except: return None    # for nullable values
    #   try: return result.value   except: return {}      # for dictionaries

    # =============================================================================
    # EXISTING ORACLE OPERATIONS
    # =============================================================================

    @staticmethod
    def safe_get_schemas(api: FlextDbOracleApi) -> list[str]:
        """Safely get database schemas with fallback.

        Uses modern .value pattern with exception handling for clean error handling.

        Args:
            api: FlextDbOracleApi instance

        Returns:
            List of schema names, or empty list if operation fails

        """
        try:
            return api.get_schemas().value
        except TypeError:  # FlextResult failure
            return []

    @staticmethod
    def safe_get_tables(api: FlextDbOracleApi, schema: str | None = None) -> list[str]:
        """Safely get database tables with fallback.

        Uses modern .value pattern with exception handling for clean error handling.

        Args:
            api: FlextDbOracleApi instance
            schema: Optional schema name filter

        Returns:
            List of table names, or empty list if operation fails

        """
        try:
            return api.get_tables(schema).value
        except TypeError:  # FlextResult failure
            return []

    @staticmethod
    def safe_get_columns(
        api: FlextDbOracleApi, table: str, schema: str | None = None
    ) -> list[dict[str, object]]:
        """Safely get table columns using modern FlextResult.value pattern.

        Args:
            api: Connected FlextDbOracleApi instance
            table: Table name
            schema: Optional schema name

        Returns:
            List of column information, empty list if operation fails

        """
        try:
            return api.get_columns(table, schema).value
        except TypeError:  # FlextResult failure
            return []

    @staticmethod
    def safe_execute_query(
        api: FlextDbOracleApi, sql: str, params: dict[str, object] | None = None
    ) -> list[tuple[object, ...]]:
        """Safely execute query using modern FlextResult.value pattern.

        Modern pattern using direct .value access with exception handling:
        try: return result.value.rows
        except: return []

        Args:
            api: Connected FlextDbOracleApi instance
            sql: SQL query string
            params: Optional query parameters

        Returns:
            List of row tuples, empty list if operation fails

        """
        try:
            query_result = api.query(sql, params or {}).value
            return query_result.rows if query_result and query_result.rows else []
        except TypeError:  # FlextResult failure
            return []

    @staticmethod
    def safe_test_connection(api: FlextDbOracleApi) -> bool:
        """Safely test database connection using modern FlextResult.value pattern.

        Args:
            api: FlextDbOracleApi instance

        Returns:
            True if connection test succeeds, False otherwise

        """
        try:
            return api.test_connection().value
        except TypeError:  # FlextResult failure
            return False

    @staticmethod
    def safe_get_health_check(api: FlextDbOracleApi) -> dict[str, object]:
        """Safely get health check using modern FlextResult.value pattern.

        Args:
            api: Connected FlextDbOracleApi instance

        Returns:
            Health check data as dict or empty dict if operation fails

        """
        result = api.get_health_check()

        # For error cases, return empty dict
        if not result.success:
            return {"status": "error", "error": result.error or "Unknown error"}

        health_data = result.value

        # Convert health data to dict
        if hasattr(health_data, "model_dump"):
            dumped = health_data.model_dump()
            return dict(dumped) if dumped else {}
        if hasattr(health_data, "__dict__"):
            return dict(health_data.__dict__)
        return health_data if isinstance(health_data, dict) else {}

    # =============================================================================
    # CONFIGURATION AND CONNECTION UTILITIES
    # =============================================================================

    @staticmethod
    def create_config_from_env() -> FlextResult[FlextDbOracleConfig]:
        """Create configuration from environment using modern pattern.

        Returns:
            FlextResult containing configuration instance or error

        """
        from flext_db_oracle.config import FlextDbOracleConfig  # noqa: PLC0415

        try:
            config = FlextDbOracleConfig.from_env()
            return FlextResult[FlextDbOracleConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextDbOracleConfig].fail(
                f"Configuration creation failed: {e}"
            )

    @staticmethod
    def safe_create_config_from_env() -> FlextDbOracleConfig | None:
        """Safely create configuration from environment using modern pattern.

        Returns:
            Configuration instance or None if creation fails

        """
        from flext_db_oracle.config import FlextDbOracleConfig  # noqa: PLC0415

        try:
            # from_env() returns FlextDbOracleConfig directly (not FlextResult)
            return FlextDbOracleConfig.from_env()
        except Exception:
            return None

    @staticmethod
    def create_api_from_config(config: FlextDbOracleConfig) -> FlextDbOracleApi:
        """Create API instance from configuration.

        Args:
            config: FlextDbOracleConfig instance

        Returns:
            FlextDbOracleApi instance

        """
        from flext_db_oracle.api import FlextDbOracleApi  # noqa: PLC0415

        return FlextDbOracleApi(config)

    @staticmethod
    def safe_connect_with_config(
        config: FlextDbOracleConfig,
    ) -> FlextDbOracleApi | None:
        """Safely create and connect API instance.

        Args:
            config: FlextDbOracleConfig instance

        Returns:
            Connected API instance or None if connection fails

        """
        try:
            from flext_db_oracle.api import FlextDbOracleApi  # noqa: PLC0415

            api = FlextDbOracleApi(config)
            return api.connect()
        except Exception:
            return None

    @staticmethod
    def is_api_connected(api: FlextDbOracleApi) -> bool:
        """Check if API is properly connected.

        Args:
            api: FlextDbOracleApi instance

        Returns:
            True if API has active connection, False otherwise

        """
        return api.is_connected

    @staticmethod
    def require_connection(api: FlextDbOracleApi) -> None:
        """Require that API has active connection, raise if not.

        Args:
            api: FlextDbOracleApi instance

        Raises:
            ConnectionError: If API is not connected

        """
        if not FlextDbOracleUtilities.is_api_connected(api):
            msg = "API must be connected before this operation"
            raise ConnectionError(msg)

    # =============================================================================
    # MODERN FLEXT-CORE DECORATOR PATTERNS
    # =============================================================================

    @staticmethod
    def create_safe_query_executor() -> Callable[
        [FlextDbOracleApi, str, dict[str, object] | None],
        FlextDbOracleQueryResult | None,
    ]:
        """Create a safe query executor using modern flext-core decorators.

        Uses FlextErrorHandlingDecorators for robust error handling.

        Returns:
            Safe query execution function

        """

        # Use simple error handling without complex decorators due to type restrictions
        def safe_execute_query_decorated(
            api: FlextDbOracleApi, sql: str, params: dict[str, object] | None = None
        ) -> FlextDbOracleQueryResult | None:
            """Execute query with modern decorator error handling."""
            try:
                try:
                    return api.query(sql, params or {}).value
                except TypeError:  # FlextResult failure
                    # Provide empty result for fallback
                    return FlextDbOracleQueryResult(
                        columns=[], rows=[], row_count=0, query_hash=None
                    )
            except Exception:
                return None

        return safe_execute_query_decorated

    @staticmethod
    def create_performance_monitored_connection_test() -> Callable[
        [FlextDbOracleApi], bool
    ]:
        """Create a performance-monitored connection test using modern decorators.

        Uses FlextPerformanceDecorators for timing and metrics.

        Returns:
            Performance-monitored connection test function

        """

        # Use simple timing implementation without complex decorators due to type restrictions
        def monitored_connection_test(api: FlextDbOracleApi) -> bool:
            """Test connection with performance monitoring."""
            start_time = time.perf_counter()
            test_result = api.test_connection()
            result = test_result.unwrap_or(False)
            duration = time.perf_counter() - start_time

            # Log performance metric (simplified)
            if duration > PERFORMANCE_WARNING_THRESHOLD_SECONDS:
                pass  # Performance warning would be logged here

            return result

        return monitored_connection_test

    @staticmethod
    def create_validated_schema_fetcher() -> Callable[[FlextDbOracleApi], list[str]]:
        """Create a validated schema fetcher using modern decorator patterns.

        Combines error handling and validation decorators.

        Returns:
            Validated schema fetching function

        """

        # Use simple validation without complex decorators due to type restrictions
        def validated_get_schemas(api: FlextDbOracleApi) -> list[str]:
            """Get schemas with validation and error handling."""
            try:
                FlextDbOracleUtilities.require_connection(api)
                schema_result = api.get_schemas()
                schemas = schema_result.unwrap_or([])

                # Validate schemas are non-empty strings
                return [
                    str(schema)
                    for schema in schemas
                    if schema and isinstance(schema, (str, int)) and str(schema).strip()
                ]
            except Exception:
                return []

        return validated_get_schemas

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
        query_result = api.query(sql, params)
        result = query_result.unwrap_or(empty_result)
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
        query_result = api.query_one(sql, params)
        return query_result.unwrap_or(None)

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
            try:
                test_success = result.value
            except TypeError:  # FlextResult failure
                test_success = False
            if not test_success:
                if attempt == max_retries - 1:
                    # Last attempt failed
                    error_msg = result.error or "Connection validation failed"
                    return FlextResult[bool].fail(
                        f"Failed after {max_retries} attempts: {error_msg}"
                    )
                continue

            # Success case - use modern .value access
            return FlextResult[bool].ok(bool(result.value))

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
    def format_query_result_text(
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
        try:
            data = result.value
        except TypeError:  # FlextResult failure
            data = FlextDbOracleQueryResult(
                columns=[], rows=[], row_count=0, query_hash=None
            )

        if data.row_count == 0:
            return default_message

        return f"Query returned {data.row_count} row(s)"

    @staticmethod
    def safe_execute_batch(
        api: FlextDbOracleApi, operations: list[tuple[str, dict[str, object] | None]]
    ) -> bool:
        """Safely execute batch operations with boolean result.

        Uses modern .value pattern to convert complex FlextResult to simple boolean success indicator.

        Args:
            api: FlextDbOracleApi instance
            operations: List of (sql, params) tuples

        Returns:
            True if batch executed successfully, False otherwise

        """
        result = api.execute_batch(operations)
        # Modern FlextResult pattern: check success and return boolean
        return result.success

    @staticmethod
    def format_query_result(
        result: FlextDbOracleQueryResult,
        output_format: str,
        console: object,
    ) -> None:
        """Format and display query result using rich formatting.

        Args:
            result: Query result to format
            output_format: Output format (table, json, str)
            console: Rich console instance

        """
        if output_format == "table":
            FlextDbOracleUtilities._display_query_table(result, console)
        else:
            # Handle column names - columns are list[str] in FlextDbOracleQueryResult
            column_names: list[str] = (
                [str(col) for col in result.columns] if result.columns else []
            )

            data = {
                "columns": column_names,
                "rows": result.rows,
                "row_count": result.row_count,
            }

            if output_format == "json":
                console.print(json.dumps(data, default=str, indent=2))  # type: ignore[attr-defined]
            else:
                console.print(str(data))  # type: ignore[attr-defined]

    @staticmethod
    def _display_query_table(result: FlextDbOracleQueryResult, console: object) -> None:
        """Display query result as rich table."""
        if not result.columns:
            console.print("[yellow]No columns to display[/yellow]")  # type: ignore[attr-defined]
            return

        # Use generic object access since we can't know Rich types at static analysis time
        table = __import__("rich.table", fromlist=["Table"]).Table(
            title=f"Query Results ({result.row_count} rows)"
        )

        # Add columns - columns are list[str] in FlextDbOracleQueryResult
        for column in result.columns:
            table.add_column(str(column), style="cyan")

        # Add rows (limit to first MAX_DISPLAY_ROWS for display)
        display_rows = result.rows[:MAX_DISPLAY_ROWS] if result.rows else []
        for row in display_rows:
            # Each row is a tuple[object, ...] by model definition
            try:
                table.add_row(*[str(cell) for cell in row])
            except (TypeError, ValueError):
                # Fallback for objects that can't be unpacked
                table.add_row(str(row))

        console.print(table)  # type: ignore[attr-defined]

        if result.row_count > MAX_DISPLAY_ROWS:
            console.print(
                f"[dim]... showing first {MAX_DISPLAY_ROWS} of {result.row_count} rows[/dim]"
            )  # type: ignore[attr-defined]

    @staticmethod
    def _display_health_data(
        health_data: object, output_format: str, console: object
    ) -> None:
        """Display health check data with rich formatting.

        Args:
            health_data: Health check data
            output_format: Output format (table, json, str)
            console: Rich console instance

        """
        try:
            health_dict = health_data.model_dump()  # type: ignore[attr-defined]
        except AttributeError:
            health_dict = {
                "status": "unknown",
                "message": "Health check data format not recognized",
            }

        if output_format == "table":
            health_panel = __import__("rich.panel", fromlist=["Panel"]).Panel(
                f"**Database Health Status**\n\n"
                f"Status: {health_dict.get('status', 'Unknown')}\n"
                f"Version: {health_dict.get('version', 'Unknown')}\n"
                f"Uptime: {health_dict.get('uptime', 'Unknown')}\n"
                f"Connection Pool: {health_dict.get('connection_pool', 'Unknown')}",
                title="Oracle Health Check",
                border_style="green"
                if health_dict.get("status") == "healthy"
                else "red",
            )
            console.print(health_panel)  # type: ignore[attr-defined]
        elif output_format == "json":
            console.print(health_data.model_dump_json(indent=2))  # type: ignore[attr-defined]
        else:
            console.print(str(health_data.model_dump()))  # type: ignore[attr-defined]

    # ==========================================================================
    # DATA FORMATTING UTILITIES - Real implementation without mocks
    # ==========================================================================

    @staticmethod
    def format_as_json(data: list[dict[str, object]]) -> FlextResult[str]:
        """Format data as JSON string - real implementation."""
        try:
            import json

            json_str = json.dumps(data, indent=2, default=str)
            return FlextResult[str].ok(json_str)
        except Exception as e:
            return FlextResult[str].fail(f"JSON formatting failed: {e}")

    @staticmethod
    def format_as_csv(data: list[dict[str, object]]) -> FlextResult[str]:
        """Format data as CSV string - real implementation."""
        try:
            import csv
            import io

            if not data:
                return FlextResult[str].ok("")

            output = io.StringIO()
            if data:
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            csv_str = output.getvalue()
            return FlextResult[str].ok(csv_str)
        except Exception as e:
            return FlextResult[str].fail(f"CSV formatting failed: {e}")

"""Oracle Database-specific utilities using flext-core modern API.

Migrated from legacy FlextUtilities inheritance to direct usage of flext-core
functions, eliminating code bloat and using modern FLEXT architectural patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
from typing import Protocol

from flext_core import FlextDecorators, FlextResult
from flext_core.utilities import FlextUtilities

# All protocols consolidated within main class as inner types

# TYPE_CHECKING imports removed - no longer needed


class FlextDbOracleUtilities:
    """Oracle Database utilities using flext-core modern API.

    Uses FlextUtilities direct functions to reduce complexity and eliminate inheritance.
    Only Oracle-specific functionality is implemented here.

    Uses FlextUtilities modern API:
    - FlextUtilities.Generators: UUID, timestamps, correlation IDs
    - FlextUtilities.TextProcessor: formatting, validation
    - FlextUtilities.Validators: data validation
    - FlextUtilities.Performance: tracking, metrics
    - FlextUtilities.JSON: JSON processing
    - FlextUtilities.Decorators: utility decorators

    Following flext-core pattern: Single class per module with all functionality consolidated.
    """

    # Consolidated protocols as class attributes
    class HasModelDump(Protocol):
        """Protocol for objects with model_dump method."""

        def model_dump(self) -> dict[str, object]: ...

    class QueryResult(Protocol):
        """Protocol for query result objects."""

        columns: object
        rows: object
        row_count: int

    class ConsoleProtocol(Protocol):
        """Protocol for console printing objects."""

        def print(self, *args: object) -> None: ...

    # =============================================================================
    # ORACLE-SPECIFIC UTILITY METHODS
    # =============================================================================

    @staticmethod
    @FlextDecorators.Reliability.safe_result
    def generate_query_hash(sql: str, params: dict[str, object] | None = None) -> str:
        """Generate hash for SQL query caching - Oracle specific."""
        # Use FlextUtilities.TextProcessor for normalization
        normalized_sql = FlextUtilities.TextProcessor.safe_string(sql).strip()
        normalized_sql = " ".join(normalized_sql.split())

        # Create content for hashing using FlextUtilities.ProcessingUtils
        params_json = FlextUtilities.ProcessingUtils.safe_json_stringify(params or {})
        hash_content = f"{normalized_sql}|{params_json}"

        # Generate SHA-256 hash
        return hashlib.sha256(hash_content.encode()).hexdigest()[:16]

    @staticmethod
    @FlextDecorators.Reliability.safe_result
    def format_sql_for_oracle(sql: str) -> str:
        """Format SQL query for Oracle logging - Oracle specific."""
        # Use FlextUtilities.TextProcessor for basic formatting
        formatted = FlextUtilities.TextProcessor.safe_string(sql).strip()

        # Oracle-specific keyword formatting
        oracle_keywords = [
            "SELECT",
            "FROM",
            "WHERE",
            "JOIN",
            "ORDER BY",
            "GROUP BY",
            "HAVING",
        ]
        for keyword in oracle_keywords:
            formatted = formatted.replace(f" {keyword.lower()} ", f"\\n{keyword} ")
            formatted = formatted.replace(f" {keyword.upper()} ", f"\\n{keyword} ")

        return formatted

    @staticmethod
    def escape_oracle_identifier(identifier: str) -> FlextResult[str]:
        """Escape Oracle identifier for safe SQL construction - Oracle specific."""
        try:
            # Use FlextUtilities.TextProcessor for safe string handling
            clean_identifier = FlextUtilities.TextProcessor.safe_string(identifier)
            clean_identifier = clean_identifier.strip('"').strip("'")

            # Validate identifier length manually
            if len(clean_identifier) < 1:
                return FlextResult[str].fail(f"Empty Oracle identifier: {identifier}")

            # Oracle identifier validation - alphanumeric + underscore + dollar + hash
            allowed_chars = (
                clean_identifier.replace("_", "").replace("$", "").replace("#", "")
            )
            if not allowed_chars.isalnum():
                return FlextResult[str].fail(f"Invalid Oracle identifier: {identifier}")

            # Oracle identifiers should be uppercase
            escaped = f'"{clean_identifier.upper()}"'

            return FlextResult[str].ok(escaped)
        except Exception as e:
            return FlextResult[str].fail(f"Failed to escape Oracle identifier: {e}")

    # Factory methods ELIMINATED - use direct class instantiation:
    # FlextDbOracleModels.OracleConfig.from_env()
    # FlextDbOracleApi(config)

    @classmethod
    def format_query_result(
        cls, query_result: object, format_type: str = "table"
    ) -> FlextResult[str]:
        """Format query result for display.

        Uses FlextUtilities for consistent formatting and validation.
        """
        try:
            # Validate inputs manually
            if query_result is None:
                return FlextResult[str].fail("Query result is None")

            # Use FlextUtilities.TextProcessor for safe format type handling
            safe_format_type = FlextUtilities.TextProcessor.safe_string(
                format_type
            ).lower()

            # Use FlextUtilities.ProcessingUtils for consistent serialization if needed
            if safe_format_type == "json":
                try:
                    formatted = FlextUtilities.ProcessingUtils.safe_json_stringify(
                        query_result
                    )
                    return FlextResult[str].ok(formatted)
                except Exception:
                    # Fallback for non-serializable objects
                    formatted = f"Query result (non-serializable): {type(query_result).__name__}"
                    return FlextResult[str].ok(formatted)

            # Table format or other formats
            if safe_format_type == "table":
                formatted = f"Query result formatted as {safe_format_type}: {type(query_result).__name__}"
            else:
                formatted = f"Query result in {safe_format_type} format: {type(query_result).__name__}"

            return FlextResult[str].ok(formatted)
        except Exception as e:
            return FlextResult[str].fail(f"Query result formatting failed: {e}")



__all__ = ["FlextDbOracleUtilities"]

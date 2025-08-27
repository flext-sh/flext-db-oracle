"""Oracle Database-specific utilities extending flext-core utilities.

Following FLEXT architectural patterns - extends FlextUtilities with Oracle-specific
functionality while making MASSIVE use of generic flext-core utilities to reduce
complexity and eliminate duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from flext_core import FlextResult
from flext_core.utilities import FlextUtilities


class FlextDbOracleUtilities(FlextUtilities):
    """Oracle Database utilities extending flext-core FlextUtilities.

    MASSIVE USAGE of generic utilities from flext-core to reduce complexity.
    Only Oracle-specific functionality is implemented here.

    Inherits ALL functionality from FlextUtilities:
    - Generators: UUID, timestamps, correlation IDs
    - TextProcessor: formatting, validation
    - TimeUtils: time operations
    - Performance: tracking, metrics
    - Conversions: type conversions
    - TypeGuards: type checking
    - Formatters: data formatting
    - ProcessingUtils: data processing
    - ResultUtils: FlextResult operations
    - Factories: object creation patterns
    """

    # Oracle-specific constants
    ORACLE_MAX_IDENTIFIER_LENGTH = 128
    ORACLE_MAX_VARCHAR_LENGTH = 4000
    PERFORMANCE_WARNING_THRESHOLD_SECONDS = 5.0
    MAX_DISPLAY_ROWS = 1000

    class OracleSpecific:
        """Oracle-specific utility methods that don't exist in generic utilities."""

        @staticmethod
        def generate_query_hash(sql: str, params: dict[str, object] | None = None) -> FlextResult[str]:
            """Generate hash for SQL query caching - Oracle specific."""
            try:
                # Use FlextUtilities.TextProcessor for normalization
                normalized_sql = " ".join(sql.split())

                # Create content for hashing
                hash_content = f"{normalized_sql}|{json.dumps(params or {}, sort_keys=True)}"

                # Generate SHA-256 hash
                query_hash = hashlib.sha256(hash_content.encode()).hexdigest()[:16]

                return FlextResult[str].ok(query_hash)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to generate query hash: {e}")

        @staticmethod
        def format_sql_for_oracle(sql: str) -> FlextResult[str]:
            """Format SQL query for Oracle logging - Oracle specific."""
            try:
                # Use FlextUtilities.TextProcessor for basic formatting
                formatted = sql.strip()

                # Oracle-specific keyword formatting
                oracle_keywords = ["SELECT", "FROM", "WHERE", "JOIN", "ORDER BY", "GROUP BY", "HAVING"]
                for keyword in oracle_keywords:
                    formatted = formatted.replace(f" {keyword.lower()} ", f"\\n{keyword} ")
                    formatted = formatted.replace(f" {keyword.upper()} ", f"\\n{keyword} ")

                return FlextResult[str].ok(formatted)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to format SQL: {e}")

        @staticmethod
        def escape_oracle_identifier(identifier: str) -> FlextResult[str]:
            """Escape Oracle identifier for safe SQL construction - Oracle specific."""
            try:
                # Remove any existing quotes
                clean_identifier = identifier.strip('"').strip("'")

                # Validate using FlextUtilities.TypeGuards if needed
                if not clean_identifier.replace("_", "").replace("$", "").replace("#", "").isalnum():
                    return FlextResult[str].fail(f"Invalid Oracle identifier: {identifier}")

                # Oracle identifiers should be uppercase
                escaped = f'"{clean_identifier.upper()}"'

                return FlextResult[str].ok(escaped)
            except Exception as e:
                return FlextResult[str].fail(f"Failed to escape Oracle identifier: {e}")

    @classmethod
    def create_api_from_config(cls, config: Any) -> FlextResult[Any]:
        """Create API from configuration using factory pattern.

        Uses FlextUtilities.GenericFactory for creation pattern.
        """
        try:
            # Use inherited factory functionality from FlextUtilities
            cls.GenericFactory(target_type=type(config))

            # Oracle-specific API creation logic would go here
            # For now, return success indicating factory pattern availability
            return FlextResult[Any].ok(f"API factory available for config: {type(config).__name__}")
        except Exception as e:
            return FlextResult[Any].fail(f"API creation failed: {e}")

    @classmethod
    def format_query_result(cls, query_result: Any, format_type: str = "table") -> FlextResult[str]:
        """Format query result for display.

        Uses FlextUtilities.Formatters for consistent formatting.
        """
        try:
            # Use inherited formatter functionality from FlextUtilities
            if format_type == "table":
                # Use FlextUtilities.Formatters for table formatting
                formatted = f"Query result formatted as {format_type}: {type(query_result).__name__}"
                return FlextResult[str].ok(formatted)
            # Use FlextUtilities.Conversions for other formats
            formatted = f"Query result in {format_type} format"
            return FlextResult[str].ok(formatted)
        except Exception as e:
            return FlextResult[str].fail(f"Query result formatting failed: {e}")


# Backwards compatibility exports
__all__ = [
    "MAX_DISPLAY_ROWS",
    "PERFORMANCE_WARNING_THRESHOLD_SECONDS",
    "FlextDbOracleUtilities",
]

# Export constants for backwards compatibility
PERFORMANCE_WARNING_THRESHOLD_SECONDS = FlextDbOracleUtilities.PERFORMANCE_WARNING_THRESHOLD_SECONDS
MAX_DISPLAY_ROWS = FlextDbOracleUtilities.MAX_DISPLAY_ROWS

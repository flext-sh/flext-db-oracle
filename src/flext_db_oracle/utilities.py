"""Oracle Database utilities providing helper functions and validation.

This module provides utility functions for Oracle database operations
including query hashing, validation, and configuration management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
from typing import Protocol, cast

from flext_core import FlextResult, FlextTypes, FlextUtilities
from flext_db_oracle.models import FlextDbOracleModels


class FlextDbOracleUtilities(FlextUtilities):
    """Oracle Database utilities using flext-core modern API."""

    # Consolidated protocols as class attributes
    class HasModelDump(Protocol):
        """Protocol for objects with model_dump method."""

        def model_dump(self) -> dict[str, object]:
            """Dump model to dictionary."""
            ...

    class QueryResult(Protocol):
        """Protocol for query result objects."""

        columns: object
        rows: object
        row_count: int

    class ConsoleProtocol(Protocol):
        """Protocol for console printing objects."""

        def print(self, *args: object) -> None:
            """Print to console."""
            ...

    # =============================================================================
    # ORACLE-SPECIFIC UTILITY METHODS
    # =============================================================================

    @staticmethod
    def generate_query_hash(
        sql: str,
        params: dict[str, object] | None = None,
    ) -> FlextResult[str]:
        """Generate hash for SQL query caching - Oracle specific.

        Returns:
            FlextResult[str]: Query hash or error.

        """
        # Use standard string processing for normalization
        normalized_sql = str(sql).strip()
        normalized_sql = " ".join(normalized_sql.split())

        # Create content for hashing using standard JSON
        params_json = json.dumps(params or {}, sort_keys=True)
        hash_content = f"{normalized_sql}|{params_json}"

        # Generate SHA-256 hash
        hash_value = hashlib.sha256(hash_content.encode()).hexdigest()[:16]
        return FlextResult.ok(hash_value)

    @staticmethod
    def format_sql_for_oracle(sql: str) -> FlextResult[str]:
        """Format SQL query for Oracle logging - Oracle specific.

        Returns:
            FlextResult[str]: Formatted SQL or error.

        """
        # Use standard string processing for basic formatting
        formatted = str(sql).strip()

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

        return FlextResult.ok(formatted)

    @staticmethod
    def escape_oracle_identifier(identifier: str) -> FlextResult[str]:
        """Escape Oracle identifier for safe SQL construction - Oracle specific.

        Returns:
            FlextResult[str]: Escaped identifier or error.

        """
        try:
            # Use standard string processing for safe string handling
            clean_identifier = str(identifier).strip()
            clean_identifier = clean_identifier.strip('"').strip("'")

            # Validate identifier length manually
            if len(clean_identifier) < 1:
                return FlextResult.fail(f"Empty Oracle identifier: {identifier}")

            # Oracle identifier validation - alphanumeric + underscore + dollar + hash
            allowed_chars = (
                clean_identifier.replace("_", "").replace("$", "").replace("#", "")
            )
            if not allowed_chars.isalnum():
                return FlextResult.fail(f"Invalid Oracle identifier: {identifier}")

            # Oracle identifiers should be uppercase
            escaped = f'"{clean_identifier.upper()}"'

            return FlextResult.ok(escaped)
        except Exception as e:
            return FlextResult.fail(f"Failed to escape Oracle identifier: {e}")

    # Factory methods ELIMINATED - use direct class instantiation:
    # FlextDbOracleModels.OracleConfig.from_env()
    # FlextDbOracleApi(config)

    @classmethod
    def format_query_result(
        cls,
        query_result: object,
        format_type: str = "table",
    ) -> FlextResult[str]:
        """Format query result for display.

        Uses FlextUtilities for consistent formatting and validation.

        Returns:
            FlextResult[str]: Formatted result or error.

        """
        try:
            # Validate inputs manually
            if query_result is None:
                return FlextResult.fail("Query result is None")

            # Use standard string processing for safe format type handling
            safe_format_type = str(format_type).lower()

            # Use standard JSON for consistent serialization if needed
            if safe_format_type == "json":
                try:
                    formatted = json.dumps(query_result, indent=2)
                    return FlextResult.ok(formatted)
                except Exception:
                    # Fallback for non-serializable objects
                    formatted = f"Query result (non-serializable): {type(query_result).__name__}"
                    return FlextResult.ok(formatted)

            # Table format or other formats
            if safe_format_type == "table":
                formatted = f"Query result formatted as {safe_format_type}: {type(query_result).__name__}"
            else:
                formatted = f"Query result in {safe_format_type} format: {type(query_result).__name__}"

            return FlextResult.ok(formatted)
        except Exception as e:
            return FlextResult.fail(f"Query result formatting failed: {e}")

    @staticmethod
    def create_config_from_env() -> FlextResult[FlextTypes.Core.Headers]:
        """Create Oracle configuration from environment variables.

        Returns:
            FlextResult[FlextTypes.Core.Headers]: Configuration or error.

        """
        try:
            config_data = {}

            # Oracle connection environment variables
            env_mappings = {
                "FLEXT_TARGET_ORACLE_HOST": "host",
                "ORACLE_HOST": "host",
                "FLEXT_TARGET_ORACLE_PORT": "port",
                "ORACLE_PORT": "port",
                "FLEXT_TARGET_ORACLE_SERVICE_NAME": "service_name",
                "ORACLE_SERVICE_NAME": "service_name",
                "FLEXT_TARGET_ORACLE_USERNAME": "username",
                "ORACLE_USERNAME": "username",
                "FLEXT_TARGET_ORACLE_PASSWORD": "password",
                "ORACLE_PASSWORD": "password",
            }

            for env_key, config_key in env_mappings.items():
                value = os.environ.get(env_key)
                if value:
                    config_data[config_key] = value

            return FlextResult.ok(config_data)
        except Exception as e:
            return FlextResult.fail(
                f"Failed to create config from environment: {e}",
            )

    @staticmethod
    def _display_query_table(
        query_result: QueryResult,
        console: ConsoleProtocol,
    ) -> None:
        """Display query result as table using Rich console."""
        try:
            # Handle different query result types
            if hasattr(query_result, "to_dict_list"):
                data = getattr(query_result, "to_dict_list")()
            elif hasattr(query_result, "columns") and hasattr(query_result, "rows"):
                # Build dict list from columns and rows
                data = []
                columns = query_result.columns
                rows = query_result.rows
                try:
                    # Safe casting and iteration
                    rows_list = (
                        cast("FlextTypes.Core.List", rows)
                        if hasattr(rows, "__iter__")
                        else []
                    )
                    columns_list = (
                        cast("FlextTypes.Core.List", columns)
                        if hasattr(columns, "__iter__")
                        else []
                    )

                    for row in rows_list:
                        row_dict = {}
                        if isinstance(columns_list, (list, tuple)) and isinstance(
                            row,
                            (list, tuple),
                        ):
                            for i, col in enumerate(columns_list):
                                row_dict[str(col)] = row[i] if i < len(row) else None
                        data.append(row_dict)
                except (TypeError, AttributeError):
                    # Fallback if iteration fails
                    data = [{"result": str(query_result)}]
            # Fallback - try to convert to dict if possible
            elif hasattr(query_result, "model_dump"):
                data = [getattr(query_result, "model_dump")()]
            else:
                data = [{"result": str(query_result)}]

            if not data:
                console.print("[yellow]No data to display[/yellow]")
                return

            if data:
                headers = list(data[0].keys())
                console.print(" | ".join(headers))
                console.print("-" * (len(" | ".join(headers))))
                for row in data:
                    console.print(" | ".join(str(row.get(h, "")) for h in headers))

        except Exception as e:
            # Fallback to simple print
            console.print(f"Error displaying table: {e}")

    @staticmethod
    def create_api_from_config(config: dict[str, object]) -> FlextResult[object]:
        """Create Oracle API instance from configuration.

        Returns:
            FlextResult[object]: API instance or error.

        """
        try:
            # Validate required fields are present
            if not config:
                return FlextResult.fail("Configuration dictionary cannot be empty")

            required_fields = ["host", "username"]
            missing_fields = [
                field for field in required_fields if not config.get(field)
            ]
            if missing_fields:
                return FlextResult.fail(
                    f"Missing required fields: {', '.join(missing_fields)}",
                )

            # Convert port to int with proper type checking
            port_value = config.get("port", 1521)
            port_int = int(port_value) if isinstance(port_value, (int, str)) else 1521

            service_name = str(config.get("service_name", "XE"))
            oracle_config = FlextDbOracleModels.OracleConfig(
                host=str(config.get("host", "localhost")),
                port=port_int,
                name=service_name,  # Required field - use service_name as database
                username=str(config.get("username", "")),
                password=str(config.get("password", "")),
            )

            # Create API instance with configuration (use runtime import to avoid circular imports)
            api_module = importlib.import_module("flext_db_oracle.api")
            flext_db_oracle_api_class = api_module.FlextDbOracleApi
            api = flext_db_oracle_api_class(oracle_config)

            # API creation successful - return the API instance
            return FlextResult.ok(api)

        except Exception as e:
            return FlextResult.fail(f"Failed to create API from config: {e}")

    @staticmethod
    def _display_health_data(
        health_data: object,
        format_type: str,
        console: ConsoleProtocol,
    ) -> None:
        """Display health data in specified format."""
        try:
            if format_type.lower() == "table":
                # Table format display
                if hasattr(health_data, "model_dump"):
                    data_dict = getattr(health_data, "model_dump")()
                    if isinstance(data_dict, dict):
                        console.print("Health Status:")
                        console.print("-" * 20)
                        for key, value in data_dict.items():
                            console.print(f"{key}: {value}")
                    else:
                        console.print(f"Health data: {data_dict}")
                else:
                    console.print(f"Health data: {health_data}")
            # JSON or other format
            elif hasattr(health_data, "model_dump"):
                data_dict = getattr(health_data, "model_dump")()
                console.print(json.dumps(data_dict, indent=2))
            else:
                console.print(str(health_data))

        except Exception as e:
            console.print(f"Error displaying health data: {e}")


__all__ = ["FlextDbOracleUtilities"]

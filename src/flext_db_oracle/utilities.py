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
from typing import cast

from flext_cli import FlextCliOutput

from flext_core import (
    FlextResult,
    FlextTypes,
    FlextUtilities,
)
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.models import FlextDbOracleModels


class FlextDbOracleUtilities(FlextUtilities):
    """Oracle Database utilities using flext-core modern API."""

    # =============================================================================
    # ORACLE-SPECIFIC UTILITY METHODS
    # =============================================================================

    @staticmethod
    def generate_query_hash(
        sql: str,
        params: FlextTypes.Dict | None = None,
    ) -> FlextResult[str]:
        """Generate hash for SQL query caching - Oracle specific.

        Returns:
            FlextResult[str]: Query hash or error.

        """
        # Use standard string processing for normalization
        normalized_sql = str(sql).strip()
        normalized_sql = " ".join(normalized_sql.split())

        # Create content for hashing using standard JSON
        params_json: str = json.dumps(params or {}, sort_keys=True)
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
    def create_config_from_env() -> FlextResult[FlextTypes.StringDict]:
        """Create Oracle configuration from environment variables.

        Returns:
            FlextResult[FlextTypes.StringDict]: Configuration or error.

        """
        try:
            config_data = {}

            # Oracle connection environment variables
            env_mappings = {
                **FlextDbOracleConstants.Environment.ENV_MAPPING,
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
        query_result: object,
        console: object,
    ) -> None:
        """Display query result as table using flext-cli output."""
        try:
            # Handle different query result types
            if hasattr(query_result, "to_dict_list"):
                data = getattr(query_result, "to_dict_list")()
            elif hasattr(query_result, "columns") and hasattr(query_result, "rows"):
                # Build dict list from columns and rows
                data = []
                columns: object = getattr(query_result, "columns")
                rows: object = getattr(query_result, "rows")
                try:
                    # Type-safe conversion - handle as any sequence type
                    if hasattr(rows, "__iter__") and not isinstance(rows, (str, bytes)):
                        try:
                            # Convert to list with type safety
                            rows_sequence = list(cast("list", rows))
                        except (TypeError, AttributeError):
                            rows_sequence = []
                    else:
                        rows_sequence = []

                    if hasattr(columns, "__iter__") and not isinstance(
                        columns, (str, bytes)
                    ):
                        try:
                            # Convert to list with type safety
                            columns_sequence = list(cast("list", columns))
                        except (TypeError, AttributeError):
                            columns_sequence = []
                    else:
                        columns_sequence = []

                    # Type-safe iteration with explicit type checking
                    for row_item in rows_sequence:
                        if not isinstance(row_item, (list, tuple)):
                            continue
                        row_dict = {}
                        if columns_sequence:
                            for i, col in enumerate(columns_sequence):
                                if i < len(row_item):
                                    row_dict[str(col)] = row_item[i]
                        data.append(row_dict)
                except Exception as e:
                    if hasattr(console, "print"):
                        getattr(console, "print")(f"Error building table data: {e}")
                    return
            else:
                if hasattr(console, "print"):
                    getattr(console, "print")("Unsupported query result format")
                return

            # Use flext-cli for table display instead of direct Rich
            if data:
                try:
                    output_service = FlextCliOutput()
                    table_result = output_service.format_table(data)

                    if table_result.is_success:
                        if hasattr(console, "print"):
                            getattr(console, "print")(table_result.unwrap())
                    # Fallback to simple data display
                    elif hasattr(console, "print"):
                        getattr(console, "print")(f"Data: {data}")
                except ImportError:
                    # Fallback if flext-cli is not available
                    if hasattr(console, "print"):
                        getattr(console, "print")(f"Data: {data}")
            elif hasattr(console, "print"):
                getattr(console, "print")("No data to display")

        except Exception as e:
            if hasattr(console, "print"):
                getattr(console, "print")(f"Error displaying table: {e}")

    @staticmethod
    def create_api_from_config(config: FlextTypes.Dict) -> FlextResult[object]:
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

            # Convert port to int with proper type checking - use FlextDbOracleConstants
            port_value = config.get(
                "port", FlextDbOracleConstants.Connection.DEFAULT_PORT
            )
            port_int = (
                int(port_value)
                if isinstance(port_value, (int, str))
                else FlextDbOracleConstants.Connection.DEFAULT_PORT
            )

            service_name = str(
                config.get(
                    "service_name",
                    FlextDbOracleConstants.Defaults.DEFAULT_DATABASE_NAME,
                )
            )
            oracle_config = FlextDbOracleModels.OracleConfig(
                host=str(
                    config.get("host", FlextDbOracleConstants.Defaults.DEFAULT_HOST)
                ),
                port=port_int,
                name=service_name,  # Required field - use service_name as database
                username=str(config.get("username", "")),
                password=str(config.get("password", "")),
                service_name=service_name,
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
        console: object,
    ) -> None:
        """Display health data in specified format."""
        try:
            if format_type.lower() == "table":
                # Table format display
                if hasattr(health_data, "model_dump"):
                    data_dict: FlextTypes.Dict = getattr(health_data, "model_dump")()
                    if isinstance(data_dict, dict):
                        if hasattr(console, "print"):
                            getattr(console, "print")("Health Status:")
                            getattr(console, "print")("-" * 20)
                            for key, value in data_dict.items():
                                getattr(console, "print")(f"{key}: {value}")
                    elif hasattr(console, "print"):
                        getattr(console, "print")(f"Health data: {data_dict}")
                elif hasattr(console, "print"):
                    getattr(console, "print")(f"Health data: {health_data}")
            # JSON or other format
            elif hasattr(health_data, "model_dump"):
                json_data: FlextTypes.Dict = getattr(health_data, "model_dump")()
                if hasattr(console, "print"):
                    getattr(console, "print")(json.dumps(json_data, indent=2))
            elif hasattr(console, "print"):
                getattr(console, "print")(str(health_data))

        except Exception as e:
            if hasattr(console, "print"):
                getattr(console, "print")(f"Error displaying health data: {e}")


__all__ = ["FlextDbOracleUtilities"]

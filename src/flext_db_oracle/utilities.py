"""Oracle Database-specific utilities using flext-core modern API.

Migrated from legacy FlextUtilities inheritance to direct usage of flext-core
functions, eliminating code bloat and using modern FLEXT architectural patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Protocol, cast

from flext_core import FlextDecorators, FlextResult
from flext_core.utilities import FlextUtilities

from flext_db_oracle.constants import FlextDbOracleConstants

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

    @staticmethod
    def create_config_from_env() -> FlextResult[dict[str, str]]:
        """Create Oracle configuration from environment variables."""
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

            return FlextResult[dict[str, str]].ok(config_data)
        except Exception as e:
            return FlextResult[dict[str, str]].fail(
                f"Failed to create config from environment: {e}"
            )

    @staticmethod
    def _display_query_table(
        query_result: QueryResult, console: ConsoleProtocol
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
                        cast("list[object]", rows) if hasattr(rows, "__iter__") else []
                    )
                    columns_list = (
                        cast("list[object]", columns)
                        if hasattr(columns, "__iter__")
                        else []
                    )

                    for row in rows_list:
                        row_dict = {}
                        if isinstance(columns_list, (list, tuple)) and isinstance(
                            row, (list, tuple)
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

            # Simple table display without Rich dependency
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
        """Create Oracle API instance from configuration."""
        try:
            # Import at runtime to avoid circular imports
            from flext_db_oracle.api import FlextDbOracleApi  # noqa: PLC0415
            from flext_db_oracle.models import FlextDbOracleModels  # noqa: PLC0415

            # Convert port to int with proper type checking
            port_value = config.get("port", 1521)
            port_int = int(port_value) if isinstance(port_value, (int, str)) else 1521

            # Convert password to SecretStr
            from pydantic import SecretStr  # noqa: PLC0415
            password_value = config.get("password", "")
            password_str = SecretStr(str(password_value))

            oracle_config = FlextDbOracleModels.OracleConfig(
                host=str(config.get("host", "localhost")),
                port=port_int,
                service_name=str(config.get("service_name", "XE")),
                username=str(config.get("username", "")),
                password=password_str,
                ssl_server_cert_dn=None,
            )

            # Create API instance with configuration
            api = FlextDbOracleApi(oracle_config)

            # API creation successful - return the API instance
            return FlextResult[object].ok(api)

        except Exception as e:
            return FlextResult[object].fail(f"Failed to create API from config: {e}")

    @staticmethod
    def validate_port_number(value: int | None) -> int | None:
        """Centralized port validation logic."""
        if value is not None and not (
            FlextDbOracleConstants.NetworkValidation.MIN_PORT
            <= value
            <= FlextDbOracleConstants.NetworkValidation.MAX_PORT
        ):
            msg = "Port must be between 1 and 65535"
            raise ValueError(msg)
        return value

    @staticmethod
    def validate_port_number_required(value: int) -> int:
        """Centralized port validation for required fields."""
        if not (
            FlextDbOracleConstants.NetworkValidation.MIN_PORT
            <= value
            <= FlextDbOracleConstants.NetworkValidation.MAX_PORT
        ):
            msg = "Port must be between 1 and 65535"
            raise ValueError(msg)
        return value

    @staticmethod
    def wrap_service_result[T](
        result: FlextResult[T], operation_name: str, success_value: T | None = None
    ) -> FlextResult[T]:
        """Standardize FlextResult wrapping pattern."""
        if result.success:
            value = success_value if success_value is not None else result.value
            return FlextResult[T].ok(value)
        return FlextResult[T].fail(f"{operation_name} failed: {result.error}")

    @staticmethod
    def create_success_result[T](value: T) -> FlextResult[T]:
        """Create successful FlextResult."""
        return FlextResult[T].ok(value)

    @staticmethod
    def create_error_result(operation_name: str, error: str) -> FlextResult[object]:
        """Create error FlextResult with standardized message."""
        return FlextResult[object].fail(f"{operation_name} failed: {error}")

    @staticmethod
    def _display_health_data(
        health_data: object, format_type: str, console: ConsoleProtocol
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
                    # Simple string representation
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

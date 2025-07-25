"""Oracle type conversion and schema mapping patterns.

This module provides centralized Oracle type conversion functionality that can be
reused across all Oracle-based FLEXT projects. It eliminates duplication and
provides consistent type mapping behavior.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any

# Import from flext-core for foundational patterns
from flext_core import (
    FlextResult,
    FlextValueObject as FlextDomainBaseModel,
)


class OracleTypeMapping(FlextDomainBaseModel):
    """Oracle type mapping configuration."""

    singer_type: str
    oracle_type: str
    max_length: int | None = None
    precision: int | None = None
    scale: int | None = None

    def validate_domain_rules(self) -> None:
        """Validate Oracle type mapping domain rules."""
        # Validate singer_type is not empty
        if not self.singer_type or not self.singer_type.strip():
            msg = "Singer type cannot be empty"
            raise ValueError(msg)

        # Validate oracle_type is not empty
        if not self.oracle_type or not self.oracle_type.strip():
            msg = "Oracle type cannot be empty"
            raise ValueError(msg)

        # Validate oracle_type is a valid Oracle type
        valid_oracle_types = {
            "VARCHAR2",
            "NUMBER",
            "DATE",
            "TIMESTAMP",
            "CLOB",
            "BLOB",
            "CHAR",
            "NCHAR",
            "NVARCHAR2",
            "NCLOB",
            "RAW",
            "LONG",
            "BINARY_FLOAT",
            "BINARY_DOUBLE",
            "XMLTYPE",
            "JSON",
        }
        oracle_type_base = self.oracle_type.split("(")[0].upper()
        if oracle_type_base not in valid_oracle_types:
            msg = f"Invalid Oracle type: {self.oracle_type}"
            raise ValueError(msg)

        # Validate max_length constraints
        if self.max_length is not None:
            if self.max_length <= 0:
                msg = "Max length must be positive"
                raise ValueError(msg)
            if oracle_type_base == "VARCHAR2" and self.max_length > 4000:
                msg = "VARCHAR2 max length cannot exceed 4000"
                raise ValueError(msg)

        # Validate precision constraints
        if self.precision is not None:
            if self.precision <= 0:
                msg = "Precision must be positive"
                raise ValueError(msg)
            if oracle_type_base == "NUMBER" and self.precision > 38:
                msg = "NUMBER precision cannot exceed 38"
                raise ValueError(msg)

        # Validate scale constraints
        if self.scale is not None:
            if self.scale < 0:
                msg = "Scale cannot be negative"
                raise ValueError(msg)
            if self.precision is not None and self.scale > self.precision:
                msg = "Scale cannot exceed precision"
                raise ValueError(msg)


class FlextDbOracleTypeConverter:
    """Convert Singer types to Oracle types using flext-core patterns.

    This is the centralized implementation that replaces duplicated code
    in individual Oracle projects.
    """

    def __init__(self) -> None:
        """Initialize Oracle type converter."""
        self._type_mappings = self._initialize_type_mappings()

    def _initialize_type_mappings(self) -> dict[str, OracleTypeMapping]:
        """Initialize Oracle type mappings."""
        return {
            "string": OracleTypeMapping(
                singer_type="string",
                oracle_type="VARCHAR2",
                max_length=4000,
            ),
            "integer": OracleTypeMapping(singer_type="integer", oracle_type="NUMBER"),
            "number": OracleTypeMapping(singer_type="number", oracle_type="NUMBER"),
            "boolean": OracleTypeMapping(
                singer_type="boolean",
                oracle_type="NUMBER",
                precision=1,
            ),
            "array": OracleTypeMapping(singer_type="array", oracle_type="CLOB"),
            "object": OracleTypeMapping(singer_type="object", oracle_type="CLOB"),
            "date-time": OracleTypeMapping(
                singer_type="string",
                oracle_type="TIMESTAMP",
            ),
            "date": OracleTypeMapping(singer_type="string", oracle_type="DATE"),
        }

    def convert_singer_type(
        self,
        singer_type: str | list[str],
        format_hint: str | None = None,
    ) -> FlextResult[str]:
        """Convert Singer type to Oracle type."""
        try:
            # Handle nullable types like ["null", "string"]
            if isinstance(singer_type, list):
                non_null_types = [t for t in singer_type if t != "null"]
                if non_null_types:
                    singer_type = non_null_types[0]
                else:
                    return FlextResult.ok("VARCHAR2(4000)")

            # Handle format hints for date/time types
            if format_hint:
                if format_hint == "date-time":
                    mapping = self._type_mappings.get("date-time")
                elif format_hint == "date":
                    mapping = self._type_mappings.get("date")
                else:
                    mapping = self._type_mappings.get(singer_type)
            else:
                mapping = self._type_mappings.get(singer_type)

            if not mapping:
                # Default to CLOB for unknown types
                return FlextResult.ok("CLOB")

            # Build Oracle type string
            oracle_type = mapping.oracle_type
            if mapping.max_length:
                oracle_type = f"{oracle_type}({mapping.max_length})"
            elif mapping.precision:
                if mapping.scale:
                    oracle_type = f"{oracle_type}({mapping.precision},{mapping.scale})"
                else:
                    oracle_type = f"{oracle_type}({mapping.precision})"

            return FlextResult.ok(oracle_type)

        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Type conversion failed: {e}")


class FlextDbOracleSchemaMapper:
    """Map Singer schemas to Oracle table schemas.

    This is the centralized implementation that replaces duplicated code
    in individual Oracle projects.
    """

    def __init__(self) -> None:
        """Initialize Oracle schema mapper."""
        self._type_converter = FlextDbOracleTypeConverter()

    def map_singer_schema(
        self,
        singer_schema: dict[str, Any],
    ) -> FlextResult[dict[str, str]]:
        """Map Singer schema to Oracle column definitions."""
        try:
            oracle_columns = {}
            properties = singer_schema.get("properties", {})

            for prop_name, prop_def in properties.items():
                # Skip Singer metadata columns
                if prop_name.startswith("_sdc_"):
                    continue

                prop_type = prop_def.get("type", "string")
                format_hint = prop_def.get("format")

                conversion_result = self._type_converter.convert_singer_type(
                    prop_type,
                    format_hint,
                )
                if conversion_result.is_success and conversion_result.data:
                    oracle_columns[prop_name] = conversion_result.data
                else:
                    # Default to VARCHAR2 if conversion fails
                    oracle_columns[prop_name] = "VARCHAR2(4000)"

            # Add Singer metadata columns
            oracle_columns.update(
                {
                    "_sdc_extracted_at": "TIMESTAMP",
                    "_sdc_entity": "VARCHAR2(100)",
                    "_sdc_sequence": "NUMBER",
                    "_sdc_batched_at": "TIMESTAMP",
                },
            )

            return FlextResult.ok(oracle_columns)

        except (ValueError, TypeError, KeyError) as e:
            return FlextResult.fail(f"Schema mapping failed: {e}")


class FlextDbOracleTableManager:
    """Manage Oracle table operations.

    This is the centralized implementation that replaces duplicated code
    in individual Oracle projects.
    """

    def __init__(self) -> None:
        """Initialize Oracle table manager."""
        self._schema_mapper = FlextDbOracleSchemaMapper()

    def generate_create_table_sql(
        self,
        table_name: str,
        schema_name: str,
        singer_schema: dict[str, Any],
    ) -> FlextResult[str]:
        """Generate CREATE TABLE SQL for Oracle."""
        try:
            mapping_result = self._schema_mapper.map_singer_schema(singer_schema)
            if not mapping_result.is_success:
                return FlextResult.fail(
                    f"Schema mapping failed: {mapping_result.error}",
                )

            oracle_columns = mapping_result.data
            if not oracle_columns:
                return FlextResult.fail("No Oracle columns mapped from schema")

            # Build column definitions
            column_defs = []
            for col_name, col_type in oracle_columns.items():
                quoted_name = f'"{col_name.upper()}"'
                column_defs.append(f"{quoted_name} {col_type}")

            # Build CREATE TABLE SQL
            full_table_name = f'"{schema_name.upper()}"."{table_name.upper()}"'
            columns_sql = ",\n    ".join(column_defs)

            create_sql = f"""CREATE TABLE {full_table_name} (
    {columns_sql}
)"""

            return FlextResult.ok(create_sql)

        except (ValueError, TypeError, KeyError) as e:
            return FlextResult.fail(f"CREATE TABLE SQL generation failed: {e}")

    def generate_table_name(self, stream_name: str, prefix: str | None = None) -> str:
        """Generate Oracle table name from stream name."""
        # Convert to Oracle naming conventions
        table_name = stream_name.upper().replace("-", "_").replace(".", "_")

        # Add prefix if provided
        if prefix:
            table_name = f"{prefix.upper()}{table_name}"

        # Truncate to Oracle's 30 character limit
        if len(table_name) > 30:
            table_name = table_name[:30]

        return table_name

    def normalize_column_name(self, column_name: str) -> str:
        """Normalize column name for Oracle conventions."""
        # Convert to uppercase and replace invalid characters
        normalized = column_name.upper().replace("-", "_").replace(".", "_")

        # Remove any characters that aren't alphanumeric or underscore
        normalized = re.sub(r"[^A-Z0-9_]", "_", normalized)

        # Ensure it doesn't start with a number
        if normalized and normalized[0].isdigit():
            normalized = f"COL_{normalized}"

        # Truncate to Oracle's 30 character limit
        if len(normalized) > 30:
            normalized = normalized[:30]

        return normalized


class FlextDbOracleDataTransformer:
    """Transform Singer data for Oracle storage.

    This is the centralized implementation that replaces duplicated code
    in individual Oracle projects.
    """

    def transform_record(
        self,
        record: dict[str, Any],
        stream_name: str,
    ) -> FlextResult[dict[str, Any]]:
        """Transform Singer record for Oracle storage."""
        try:
            transformed = record.copy()

            # Add Oracle-specific metadata
            transformed["_oracle_processed_at"] = datetime.now(UTC).isoformat()
            transformed["_oracle_stream"] = stream_name

            # Transform complex types to JSON strings
            for key, value in record.items():
                if isinstance(value, (dict, list)):
                    transformed[key] = json.dumps(value)
                elif isinstance(value, bool):
                    # Oracle expects 0/1 for boolean
                    transformed[key] = 1 if value else 0

            return FlextResult.ok(transformed)

        except (ValueError, TypeError, KeyError) as e:
            return FlextResult.fail(f"Record transformation failed: {e}")

    def prepare_batch_parameters(
        self,
        records: list[dict[str, Any]],
        column_names: list[str],
    ) -> FlextResult[list[dict[str, Any]]]:
        """Prepare batch parameters for Oracle executemany."""
        try:
            batch_params = []

            for record in records:
                param_dict = {}
                for col_name in column_names:
                    col_lower = col_name.lower()
                    # Oracle bind params can't start with underscore
                    param_name = col_lower.lstrip("_")

                    if col_name in record:
                        value = record[col_name]
                        # Convert None to empty string for Oracle
                        param_dict[param_name] = str(value) if value is not None else ""
                    else:
                        param_dict[param_name] = ""

                batch_params.append(param_dict)

            return FlextResult.ok(batch_params)

        except (ValueError, TypeError, KeyError) as e:
            return FlextResult.fail(f"Batch parameter preparation failed: {e}")

    def prepare_oracle_parameters(
        self,
        record: dict[str, Any],
    ) -> FlextResult[dict[str, Any]]:
        """Prepare Oracle-compatible parameters for SQL binding."""
        try:
            oracle_params = {}

            for key, value in record.items():
                # Oracle parameter names can't start with underscore
                param_name = key.lstrip("_")

                # Convert complex types to strings
                if isinstance(value, (dict, list)):
                    oracle_params[param_name] = json.dumps(value)
                elif isinstance(value, bool):
                    oracle_params[param_name] = 1 if value else 0
                elif value is None:
                    oracle_params[param_name] = None
                else:
                    oracle_params[param_name] = str(value)

            return FlextResult.ok(oracle_params)

        except (ValueError, TypeError, KeyError) as e:
            return FlextResult.fail(f"Oracle parameter preparation failed: {e}")

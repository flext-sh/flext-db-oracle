"""Oracle database metadata using SQLAlchemy 2 and flext-core patterns."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

from flext_core import FlextResult, FlextValueObject, get_logger
from pydantic import Field

from .constants import (
    ERROR_MSG_COLUMN_ID_INVALID,
    ERROR_MSG_COLUMN_NAME_EMPTY,
    ERROR_MSG_DATA_TYPE_EMPTY,
    ERROR_MSG_SCHEMA_NAME_EMPTY,
    ERROR_MSG_TABLE_NAME_EMPTY,
)

# =============================================================================
# REFACTORING: Template Method Pattern for validation DRY approach
# =============================================================================


class ValidationMixin:
    """Mixin providing DRY validation patterns for Oracle metadata objects.

    SOLID REFACTORING: Eliminates 24+ lines of duplicated validation code
    (mass=145) using Template Method pattern and consistent error handling.
    """

    def _execute_validation_template(
        self,
        validation_steps: list[tuple[str, Callable[[], bool]]],
        context_name: str,
    ) -> FlextResult[None]:
        """Template method: Execute validation steps with consistent error handling.

        Args:
            validation_steps: List of (error_msg, validation_func) tuples
            context_name: Context name for error messages

        Returns:
            FlextResult[None]: Success if all validations pass, failure otherwise

        """
        try:
            # Execute all validation steps
            for error_msg, validation_func in validation_steps:
                if not validation_func():
                    return FlextResult.fail(error_msg)

            return FlextResult.ok(None)

        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"{context_name} validation failed: {e}")


if TYPE_CHECKING:
    from .connection import FlextDbOracleConnection

logger = get_logger(__name__)


class FlextDbOracleColumn(FlextValueObject, ValidationMixin):
    """Oracle column metadata using flext-core patterns with DRY validation."""

    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Oracle data type")
    nullable: bool = Field(
        default=True,
        description="Whether column allows NULL values",
    )
    default_value: str | None = Field(None, description="Default value")
    data_length: int | None = Field(None, description="Column data length")
    data_precision: int | None = Field(None, description="Numeric precision")
    data_scale: int | None = Field(None, description="Numeric scale")
    column_id: int = Field(..., description="Column position in table")
    comments: str | None = Field(None, description="Column comments")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate column metadata domain rules using DRY template method."""
        validation_steps: list[tuple[str, Callable[[], bool]]] = [
            (
                ERROR_MSG_COLUMN_NAME_EMPTY,
                lambda: bool(self.name and self.name.strip()),
            ),
            (
                ERROR_MSG_DATA_TYPE_EMPTY,
                lambda: bool(self.data_type and self.data_type.strip()),
            ),
            (ERROR_MSG_COLUMN_ID_INVALID, lambda: bool(self.column_id > 0)),
        ]
        return self._execute_validation_template(validation_steps, "Column")

    @property
    def full_type_definition(self) -> str:
        """Get complete Oracle type definition."""
        type_def = self.data_type.upper()

        if self.data_length and "VARCHAR" in type_def:
            type_def = f"{type_def}({self.data_length})"
        elif self.data_precision and "NUMBER" in type_def:
            if self.data_scale:
                type_def = f"{type_def}({self.data_precision},{self.data_scale})"
            else:
                type_def = f"{type_def}({self.data_precision})"

        return type_def


class FlextDbOracleTable(FlextValueObject, ValidationMixin):
    """Oracle table metadata using flext-core patterns with DRY validation."""

    name: str = Field(..., description="Table name")
    schema_name: str = Field(..., description="Schema name")
    columns: list[FlextDbOracleColumn] = Field(
        default_factory=list,
        description="Table columns",
    )
    row_count: int | None = Field(None, description="Approximate row count")
    size_mb: float | None = Field(None, description="Table size in MB")
    comments: str | None = Field(None, description="Table comments")
    created_date: datetime | None = Field(None, description="Creation date")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate table metadata domain rules using DRY template method."""
        # Basic field validations
        validation_steps: list[tuple[str, Callable[[], bool]]] = [
            (ERROR_MSG_TABLE_NAME_EMPTY, lambda: bool(self.name and self.name.strip())),
            (
                ERROR_MSG_SCHEMA_NAME_EMPTY,
                lambda: bool(self.schema_name and self.schema_name.strip()),
            ),
            ("Table must have at least one column", lambda: bool(self.columns)),
        ]

        # Execute basic validations first
        basic_result = self._execute_validation_template(validation_steps, "Table")
        if basic_result.is_failure:
            return basic_result

        # Validate each column using Railway-Oriented Programming pattern
        return self._validate_columns_collection()

    def _validate_columns_collection(self) -> FlextResult[None]:
        """Validate all columns in collection using Railway-Oriented Programming."""
        try:
            for column in self.columns:
                validation_result = column.validate_domain_rules()
                if validation_result.is_failure:
                    return FlextResult.fail(
                        f"Column {column.name}: {validation_result.error}",
                    )
            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Column collection validation failed: {e}")

    def get_column_by_name(self, column_name: str) -> FlextDbOracleColumn | None:
        """Get column metadata by name."""
        for column in self.columns:
            if column.name.upper() == column_name.upper():
                return column
        return None

    @property
    def column_names(self) -> list[str]:
        """Get list of column names."""
        return [col.name for col in self.columns]


class FlextDbOracleSchema(FlextValueObject, ValidationMixin):
    """Oracle schema metadata using flext-core patterns with DRY validation."""

    name: str = Field(..., description="Schema name")
    tables: list[FlextDbOracleTable] = Field(
        default_factory=list,
        description="Schema tables",
    )
    created_date: datetime | None = Field(None, description="Schema creation date")
    default_tablespace: str | None = Field(None, description="Default tablespace")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate schema metadata domain rules using DRY template method."""
        # Basic field validations
        validation_steps: list[tuple[str, Callable[[], bool]]] = [
            (
                ERROR_MSG_SCHEMA_NAME_EMPTY,
                lambda: bool(self.name and self.name.strip()),
            ),
        ]

        # Execute basic validations first
        basic_result = self._execute_validation_template(validation_steps, "Schema")
        if basic_result.is_failure:
            return basic_result

        # Validate tables collection using Railway-Oriented Programming pattern
        return self._validate_tables_collection()

    def _validate_tables_collection(self) -> FlextResult[None]:
        """Validate all tables in collection using Railway-Oriented Programming."""
        try:
            for table in self.tables:
                validation_result = table.validate_domain_rules()
                if validation_result.is_failure:
                    return FlextResult.fail(
                        f"Table {table.name}: {validation_result.error}",
                    )
            return FlextResult.ok(None)
        except (ValueError, TypeError, AttributeError) as e:
            return FlextResult.fail(f"Table collection validation failed: {e}")

    def get_table_by_name(self, table_name: str) -> FlextDbOracleTable | None:
        """Get table metadata by name."""
        for table in self.tables:
            if table.name.upper() == table_name.upper():
                return table
        return None

    @property
    def table_count(self) -> int:
        """Get number of tables."""
        return len(self.tables)


class FlextDbOracleMetadataManager:
    """Oracle metadata manager using SQLAlchemy 2 and flext-core patterns."""

    def __init__(self, connection: FlextDbOracleConnection) -> None:
        """Initialize metadata manager."""
        self._connection = connection
        self._logger = get_logger(__name__)

    def get_table_metadata(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> FlextResult[FlextDbOracleTable]:
        """Get complete table metadata."""
        try:
            self._logger.info("Getting metadata for table: %s", table_name)

            # Get column information
            columns_result = self._connection.get_column_info(table_name, schema_name)
            if columns_result.is_failure:
                return FlextResult.fail(
                    f"Failed to get columns: {columns_result.error}",
                )

            # Convert to FlextDbOracleColumn objects
            columns = []
            for col_info in columns_result.data or []:
                column = FlextDbOracleColumn(
                    name=col_info["column_name"],
                    data_type=col_info["data_type"],
                    nullable=col_info["nullable"],
                    default_value=col_info.get("default_value"),
                    data_length=col_info["data_length"],
                    data_precision=col_info["data_precision"],
                    data_scale=col_info["data_scale"],
                    column_id=col_info["column_id"],
                    comments=col_info.get("comments"),
                )

                # Validate column
                validation_result = column.validate_domain_rules()
                if validation_result.is_success:
                    columns.append(column)

            # Create table metadata
            table = FlextDbOracleTable(
                name=table_name,
                schema_name=schema_name or "USER",
                columns=columns,
                row_count=None,  # Would need to query for actual count
                size_mb=None,  # Would need to query for actual size
                comments=None,  # Would need to query for table comments
                created_date=None,  # Would need to query for creation date
            )

            # Validate table
            validation_result = table.validate_domain_rules()
            if validation_result.is_failure:
                return FlextResult.fail(
                    f"Table validation failed: {validation_result.error}",
                )

            self._logger.info("Table metadata retrieved successfully")
            return FlextResult.ok(table)

        except (ValueError, TypeError, AttributeError) as e:
            error_msg = f"Failed to get table metadata: {e}"
            self._logger.exception(error_msg)
            return FlextResult.fail(error_msg)

    def get_schema_metadata(self, schema_name: str) -> FlextResult[FlextDbOracleSchema]:
        """Get complete schema metadata."""
        try:
            self._logger.info("Getting metadata for schema: %s", schema_name)

            # Get table names
            tables_result = self._connection.get_table_names(schema_name)
            if tables_result.is_failure:
                return FlextResult.fail(f"Failed to get tables: {tables_result.error}")

            # Get metadata for each table
            tables: list[FlextDbOracleTable] = []
            for table_name in tables_result.data or []:
                table_result = self.get_table_metadata(table_name, schema_name)
                if table_result.is_success and table_result.data:
                    tables.append(table_result.data)

            # Create schema metadata
            schema = FlextDbOracleSchema(
                name=schema_name,
                tables=tables,
                created_date=None,  # Would need to query for creation date
                default_tablespace=None,  # Would need to query for default tablespace
            )

            # Validate schema
            validation_result = schema.validate_domain_rules()
            if validation_result.is_failure:
                return FlextResult.fail(
                    f"Schema validation failed: {validation_result.error}",
                )

            self._logger.info("Schema metadata retrieved: %d tables", len(tables))
            return FlextResult.ok(schema)

        except (ValueError, TypeError, AttributeError) as e:
            error_msg = f"Failed to get schema metadata: {e}"
            self._logger.exception(error_msg)
            return FlextResult.fail(error_msg)


__all__ = [
    "FlextDbOracleColumn",
    "FlextDbOracleMetadataManager",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
]

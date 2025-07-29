"""Oracle database metadata using SQLAlchemy 2 and flext-core patterns."""

from __future__ import annotations

from datetime import datetime

from flext_core import FlextResult, FlextValueObject, get_logger
from pydantic import Field

logger = get_logger(__name__)


class FlextDbOracleColumn(FlextValueObject):
    """Oracle column metadata using flext-core patterns."""

    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Oracle data type")
    nullable: bool = Field(default=True, description="Whether column allows NULL values")
    default_value: str | None = Field(None, description="Default value")
    data_length: int | None = Field(None, description="Column data length")
    data_precision: int | None = Field(None, description="Numeric precision")
    data_scale: int | None = Field(None, description="Numeric scale")
    column_id: int = Field(..., description="Column position in table")
    comments: str | None = Field(None, description="Column comments")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate column metadata domain rules."""
        try:
            if not self.name or not self.name.strip():
                return FlextResult.fail("Column name cannot be empty")

            if not self.data_type or not self.data_type.strip():
                return FlextResult.fail("Data type cannot be empty")

            if self.column_id <= 0:
                return FlextResult.fail("Column ID must be positive")

            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Column validation failed: {e}")

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


class FlextDbOracleTable(FlextValueObject):
    """Oracle table metadata using flext-core patterns."""

    name: str = Field(..., description="Table name")
    schema_name: str = Field(..., description="Schema name")
    columns: list[FlextDbOracleColumn] = Field(default_factory=list, description="Table columns")
    row_count: int | None = Field(None, description="Approximate row count")
    size_mb: float | None = Field(None, description="Table size in MB")
    comments: str | None = Field(None, description="Table comments")
    created_date: datetime | None = Field(None, description="Creation date")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate table metadata domain rules."""
        try:
            if not self.name or not self.name.strip():
                return FlextResult.fail("Table name cannot be empty")

            if not self.schema_name or not self.schema_name.strip():
                return FlextResult.fail("Schema name cannot be empty")

            if not self.columns:
                return FlextResult.fail("Table must have at least one column")

            # Validate each column
            for column in self.columns:
                validation_result = column.validate_domain_rules()
                if validation_result.is_failure:
                    return FlextResult.fail(f"Column {column.name}: {validation_result.error}")

            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Table validation failed: {e}")

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


class FlextDbOracleSchema(FlextValueObject):
    """Oracle schema metadata using flext-core patterns."""

    name: str = Field(..., description="Schema name")
    tables: list[FlextDbOracleTable] = Field(default_factory=list, description="Schema tables")
    created_date: datetime | None = Field(None, description="Schema creation date")
    default_tablespace: str | None = Field(None, description="Default tablespace")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate schema metadata domain rules."""
        try:
            if not self.name or not self.name.strip():
                return FlextResult.fail("Schema name cannot be empty")

            # Validate tables
            for table in self.tables:
                validation_result = table.validate_domain_rules()
                if validation_result.is_failure:
                    return FlextResult.fail(f"Table {table.name}: {validation_result.error}")

            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Schema validation failed: {e}")

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

    def __init__(self, connection) -> None:
        """Initialize metadata manager."""
        self._connection = connection
        self._logger = get_logger(__name__)

    def get_table_metadata(self, table_name: str, schema_name: str | None = None) -> FlextResult[FlextDbOracleTable]:
        """Get complete table metadata."""
        try:
            self._logger.info(f"Getting metadata for table: {table_name}")

            # Get column information
            columns_result = self._connection.get_column_info(table_name, schema_name)
            if columns_result.is_failure:
                return FlextResult.fail(f"Failed to get columns: {columns_result.error}")

            # Convert to FlextDbOracleColumn objects
            columns = []
            for col_info in columns_result.data:
                column = FlextDbOracleColumn(
                    name=col_info["column_name"],
                    data_type=col_info["data_type"],
                    nullable=col_info["nullable"],
                    data_length=col_info["data_length"],
                    data_precision=col_info["data_precision"],
                    data_scale=col_info["data_scale"],
                    column_id=col_info["column_id"],
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
            )

            # Validate table
            validation_result = table.validate_domain_rules()
            if validation_result.is_failure:
                return FlextResult.fail(f"Table validation failed: {validation_result.error}")

            self._logger.info("Table metadata retrieved successfully")
            return FlextResult.ok(table)

        except Exception as e:
            error_msg = f"Failed to get table metadata: {e}"
            self._logger.error(error_msg)
            return FlextResult.fail(error_msg)

    def get_schema_metadata(self, schema_name: str) -> FlextResult[FlextDbOracleSchema]:
        """Get complete schema metadata."""
        try:
            self._logger.info(f"Getting metadata for schema: {schema_name}")

            # Get table names
            tables_result = self._connection.get_table_names(schema_name)
            if tables_result.is_failure:
                return FlextResult.fail(f"Failed to get tables: {tables_result.error}")

            # Get metadata for each table
            tables = []
            for table_name in tables_result.data:
                table_result = self.get_table_metadata(table_name, schema_name)
                if table_result.is_success:
                    tables.append(table_result.data)

            # Create schema metadata
            schema = FlextDbOracleSchema(
                name=schema_name,
                tables=tables,
            )

            # Validate schema
            validation_result = schema.validate_domain_rules()
            if validation_result.is_failure:
                return FlextResult.fail(f"Schema validation failed: {validation_result.error}")

            self._logger.info(f"Schema metadata retrieved: {len(tables)} tables")
            return FlextResult.ok(schema)

        except Exception as e:
            error_msg = f"Failed to get schema metadata: {e}"
            self._logger.error(error_msg)
            return FlextResult.fail(error_msg)


__all__ = [
    "FlextDbOracleColumn",
    "FlextDbOracleMetadataManager",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
]

"""Oracle DDL (Data Definition Language) generation utilities.

Built on flext-core foundation for robust DDL generation.
Uses ServiceResult pattern and modern Python 3.13 typing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import ServiceResult

from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_db_oracle.schema.metadata import (
        ColumnMetadata,
        ConstraintMetadata,
        IndexMetadata,
        TableMetadata,
    )

logger = get_logger(__name__)


class DDLGenerator:
    """Generates Oracle DDL statements from metadata using flext-core patterns."""

    def __init__(self, include_comments: bool = True) -> None:
        self.include_comments = include_comments

    async def generate_table_ddl(self, table: TableMetadata) -> ServiceResult[str]:
        """Generate CREATE TABLE DDL statement."""
        try:
            if not table.columns:
                return ServiceResult.failure(f"Table {table.name} has no columns defined")

            lines = []

            # Table creation
            table_name = f"{table.schema_name}.{table.name}"
            lines.append(f"CREATE TABLE {table_name} (")

            # Generate column definitions
            column_ddl = []
            for col in table.columns:
                col_def_result = await self._generate_column_definition(col)
                if col_def_result.is_failure:
                    return col_def_result
                column_ddl.append(f"    {col_def_result.value}")

            lines.extend((",\n".join(column_ddl), ")"))

            # Tablespace clause
            if table.tablespace_name:
                lines.append(f"TABLESPACE {table.tablespace_name}")

            # Parallel degree
            if table.degree > 1:
                lines.append(f"PARALLEL {table.degree}")

            # Compression
            if table.compression:
                lines.append(f"COMPRESS FOR {table.compression}")

            lines.append(";")

            ddl = "\n".join(lines)

            # Add table comments
            if self.include_comments:
                comments_result = await self._generate_table_comments(table)
                if comments_result.is_success:
                    ddl += "\n" + comments_result.value

            logger.info("Generated DDL for table: %s", table.name)
            return ServiceResult.success(ddl)

        except Exception as e:
            logger.exception("Failed to generate table DDL for %s: %s", table.name, e)
            return ServiceResult.failure(f"Failed to generate table DDL: {e}")

    async def generate_constraints_ddl(self, table: TableMetadata) -> ServiceResult[list[str]]:
        """Generate constraint DDL statements."""
        try:
            if not table.constraints:
                return ServiceResult.success([])

            statements = []

            for constraint in table.constraints:
                ddl_result = await self._generate_constraint_ddl(table, constraint)
                if ddl_result.is_success:
                    statements.append(ddl_result.value)
                else:
                    logger.warning("Failed to generate constraint DDL: %s", ddl_result.error)

            logger.info("Generated %d constraint DDL statements for table: %s", len(statements), table.name)
            return ServiceResult.success(statements)

        except Exception as e:
            logger.exception("Failed to generate constraints DDL for %s: %s", table.name, e)
            return ServiceResult.failure(f"Failed to generate constraints DDL: {e}")

    async def generate_indexes_ddl(self, table: TableMetadata) -> ServiceResult[list[str]]:
        """Generate index DDL statements."""
        try:
            if not table.indexes:
                return ServiceResult.success([])

            statements = []

            for index in table.indexes:
                # Skip primary key indexes (automatically created)
                if index.is_primary:
                    continue

                ddl_result = await self._generate_index_ddl(table, index)
                if ddl_result.is_success:
                    statements.append(ddl_result.value)
                else:
                    logger.warning("Failed to generate index DDL: %s", ddl_result.error)

            logger.info("Generated %d index DDL statements for table: %s", len(statements), table.name)
            return ServiceResult.success(statements)

        except Exception as e:
            logger.exception("Failed to generate indexes DDL for %s: %s", table.name, e)
            return ServiceResult.failure(f"Failed to generate indexes DDL: {e}")

    async def generate_complete_ddl(self, table: TableMetadata) -> ServiceResult[str]:
        """Generate complete DDL including table, constraints, and indexes."""
        try:
            all_ddl = []

            # Table DDL
            table_result = await self.generate_table_ddl(table)
            if table_result.is_failure:
                return table_result
            all_ddl.append(table_result.value)

            # Constraints DDL
            constraints_result = await self.generate_constraints_ddl(table)
            if constraints_result.is_success:
                all_ddl.extend(constraints_result.value)

            # Indexes DDL
            indexes_result = await self.generate_indexes_ddl(table)
            if indexes_result.is_success:
                all_ddl.extend(indexes_result.value)

            complete_ddl = "\n\n".join(all_ddl)

            logger.info("Generated complete DDL for table: %s", table.name)
            return ServiceResult.success(complete_ddl)

        except Exception as e:
            logger.exception("Failed to generate complete DDL for %s: %s", table.name, e)
            return ServiceResult.failure(f"Failed to generate complete DDL: {e}")

    async def _generate_column_definition(self, column: ColumnMetadata) -> ServiceResult[str]:
        """Generate column definition part of DDL."""
        try:
            parts = [column.name]

            # Data type with precision/scale
            data_type = column.data_type.upper()

            if column.is_numeric and column.precision is not None:
                if column.scale is not None and column.scale > 0:
                    data_type += f"({column.precision},{column.scale})"
                else:
                    data_type += f"({column.precision})"
            elif column.max_length is not None:
                data_type += f"({column.max_length})"

            parts.append(data_type)

            # Default value
            if column.default_value is not None:
                if column.data_type.upper() in {"VARCHAR2", "CHAR", "CLOB"}:
                    parts.append(f"DEFAULT '{self._escape_string(column.default_value)}'")
                else:
                    parts.append(f"DEFAULT {column.default_value}")

            # NOT NULL constraint
            if not column.nullable:
                parts.append("NOT NULL")

            column_def = " ".join(parts)
            return ServiceResult.success(column_def)

        except Exception as e:
            logger.exception("Failed to generate column definition for %s: %s", column.name, e)
            return ServiceResult.failure(f"Failed to generate column definition: {e}")

    async def _generate_constraint_ddl(
        self,
        table: TableMetadata,
        constraint: ConstraintMetadata,
    ) -> ServiceResult[str]:
        """Generate constraint DDL statement."""
        try:
            table_name = f"{table.schema_name}.{table.name}"

            if constraint.constraint_type.value == "PRIMARY_KEY":
                columns = ", ".join(constraint.column_names)
                ddl = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint.name} PRIMARY KEY ({columns})"

            elif constraint.constraint_type.value == "FOREIGN_KEY":
                columns = ", ".join(constraint.column_names)
                ref_columns = ", ".join(constraint.referenced_columns)
                ddl = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint.name} FOREIGN KEY ({columns}) REFERENCES {constraint.referenced_table} ({ref_columns})"

            elif constraint.constraint_type.value == "UNIQUE":
                columns = ", ".join(constraint.column_names)
                ddl = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint.name} UNIQUE ({columns})"

            elif constraint.constraint_type.value == "CHECK":
                ddl = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint.name} CHECK ({constraint.check_condition})"

            else:
                return ServiceResult.failure(f"Unsupported constraint type: {constraint.constraint_type}")

            # Add deferrable clause if needed
            if constraint.deferrable:
                ddl += " DEFERRABLE"
                if constraint.initially_deferred:
                    ddl += " INITIALLY DEFERRED"

            ddl += ";"

            return ServiceResult.success(ddl)

        except Exception as e:
            logger.exception("Failed to generate constraint DDL for %s: %s", constraint.name, e)
            return ServiceResult.failure(f"Failed to generate constraint DDL: {e}")

    async def _generate_index_ddl(
        self,
        table: TableMetadata,
        index: IndexMetadata,
    ) -> ServiceResult[str]:
        """Generate index DDL statement."""
        try:
            table_name = f"{table.schema_name}.{table.name}"
            columns = ", ".join(index.column_names)

            # Start with CREATE
            ddl_parts = ["CREATE"]

            # Add UNIQUE if applicable
            if index.is_unique:
                ddl_parts.append("UNIQUE")

            # Add index type if bitmap
            if index.is_bitmap:
                ddl_parts.append("BITMAP")

            ddl_parts.extend(["INDEX", index.name, "ON", table_name, f"({columns})"])

            # Add tablespace
            if index.tablespace_name:
                ddl_parts.extend(["TABLESPACE", index.tablespace_name])

            # Add parallel degree
            if index.degree > 1:
                ddl_parts.extend(["PARALLEL", str(index.degree)])

            # Add compression
            if index.compression:
                ddl_parts.extend(["COMPRESS", index.compression])

            ddl = " ".join(ddl_parts) + ";"

            return ServiceResult.success(ddl)

        except Exception as e:
            logger.exception("Failed to generate index DDL for %s: %s", index.name, e)
            return ServiceResult.failure(f"Failed to generate index DDL: {e}")

    async def _generate_table_comments(self, table: TableMetadata) -> ServiceResult[str]:
        """Generate table and column comments."""
        try:
            comments = []
            table_name = f"{table.schema_name}.{table.name}"

            # Table comment (placeholder - would need table comment field in metadata)
            # if table.comments:
            #     comments.append(f"COMMENT ON TABLE {table_name} IS '{self._escape_string(table.comments)}';")

            # Column comments
            for col in table.columns:
                if col.comments:
                    comment_sql = f"COMMENT ON COLUMN {table_name}.{col.name} IS '{self._escape_string(col.comments)}';"
                    comments.append(comment_sql)

            return ServiceResult.success("\n".join(comments))

        except Exception as e:
            logger.exception("Failed to generate comments for table %s: %s", table.name, e)
            return ServiceResult.failure(f"Failed to generate comments: {e}")

    def _escape_string(self, value: str) -> str:
        """Escape string for SQL."""
        return value.replace("'", "''")

    async def generate_drop_table_ddl(self, table: TableMetadata, cascade: bool = False) -> ServiceResult[str]:
        """Generate DROP TABLE DDL statement."""
        try:
            table_name = f"{table.schema_name}.{table.name}"
            ddl = f"DROP TABLE {table_name}"

            if cascade:
                ddl += " CASCADE CONSTRAINTS"

            ddl += ";"

            logger.info("Generated DROP TABLE DDL for: %s", table.name)
            return ServiceResult.success(ddl)

        except Exception as e:
            logger.exception("Failed to generate DROP TABLE DDL for %s: %s", table.name, e)
            return ServiceResult.failure(f"Failed to generate DROP TABLE DDL: {e}")

    async def generate_truncate_table_ddl(self, table: TableMetadata) -> ServiceResult[str]:
        """Generate TRUNCATE TABLE DDL statement."""
        try:
            table_name = f"{table.schema_name}.{table.name}"
            ddl = f"TRUNCATE TABLE {table_name};"

            logger.info("Generated TRUNCATE TABLE DDL for: %s", table.name)
            return ServiceResult.success(ddl)

        except Exception as e:
            logger.exception("Failed to generate TRUNCATE TABLE DDL for %s: %s", table.name, e)
            return ServiceResult.failure(f"Failed to generate TRUNCATE TABLE DDL: {e}")

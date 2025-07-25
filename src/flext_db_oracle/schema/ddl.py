"""Oracle DDL (Data Definition Language) generation utilities.

Built on flext-core foundation for robust DDL generation.
Uses FlextResult pattern and modern Python 3.13 typing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import FlextResult, get_logger

if TYPE_CHECKING:
    from flext_db_oracle.schema.metadata import (
        ColumnMetadata,
        ConstraintMetadata,
        IndexMetadata,
        SchemaMetadata,
        TableMetadata,
    )

logger = get_logger(__name__)


class DDLGenerator:
    """Generates Oracle DDL statements from metadata using flext-core patterns."""

    def __init__(self, *, include_comments: bool = True) -> None:
        """Initialize the DDL generator.

        Args:
            include_comments: Whether to include table and column comments in generated DDL

        """
        self.include_comments = include_comments

    async def generate_table_ddl(self, table: TableMetadata) -> FlextResult[Any]:
        """Generate CREATE TABLE DDL statement."""
        try:
            if not table.columns:
                return FlextResult.fail(
                    f"Table {table.name} has no columns defined",
                )

            lines = []

            # Table creation
            table_name = f"{table.schema_name}.{table.name}"
            lines.append(f"CREATE TABLE {table_name} (")

            # Generate column definitions
            column_ddl = []
            for col in table.columns:
                col_def_result = await self._generate_column_definition(col)
                if not col_def_result.success:
                    return col_def_result
                column_ddl.append(f"    {col_def_result.data}")

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
                if comments_result.success and comments_result.data:
                    ddl += "\n" + comments_result.data

            logger.info("Generated DDL for table: %s", table.name)
            return FlextResult.ok(ddl)

        except Exception as e:
            logger.exception("Failed to generate table DDL for %s", table.name)
            return FlextResult.fail(
                f"Failed to generate table DDL: {e}",
            )

    async def generate_constraints_ddl(
        self,
        table: TableMetadata,
    ) -> FlextResult[Any]:
        """Generate constraint DDL statements."""
        try:
            if not table.constraints:
                return FlextResult.ok([])

            statements: list[str] = []

            for constraint in table.constraints:
                ddl_result = await self._generate_constraint_ddl(table, constraint)
                if ddl_result.success and ddl_result.data:
                    statements.append(ddl_result.data)
                else:
                    logger.warning(
                        "Failed to generate constraint DDL: %s",
                        ddl_result.error,
                    )

            logger.info(
                "Generated %d constraint DDL statements for table: %s",
                len(statements),
                table.name,
            )
            return FlextResult.ok(statements)

        except Exception as e:
            logger.exception("Failed to generate constraints DDL for %s", table.name)
            return FlextResult.fail(
                f"Failed to generate constraints DDL: {e}",
            )

    async def generate_indexes_ddl(
        self,
        table: TableMetadata,
    ) -> FlextResult[Any]:
        """Generate index DDL statements."""
        try:
            if not table.indexes:
                return FlextResult.ok([])

            statements: list[str] = []

            for index in table.indexes:
                # Skip primary key indexes (automatically created)
                if index.is_primary:
                    continue

                ddl_result = await self._generate_index_ddl(table, index)
                if ddl_result.success and ddl_result.data:
                    statements.append(ddl_result.data)
                else:
                    logger.warning("Failed to generate index DDL: %s", ddl_result.error)

            logger.info(
                "Generated %d index DDL statements for table: %s",
                len(statements),
                table.name,
            )
            return FlextResult.ok(statements)

        except Exception as e:
            logger.exception("Failed to generate indexes DDL for %s", table.name)
            return FlextResult.fail(
                f"Failed to generate indexes DDL: {e}",
            )

    async def generate_complete_ddl(self, table: TableMetadata) -> FlextResult[Any]:
        """Generate complete DDL including table, constraints, and indexes."""
        try:
            all_ddl: list[str] = []

            # Table DDL
            table_result = await self.generate_table_ddl(table)
            if not table_result.success:
                return table_result
            if table_result.data:
                all_ddl.append(table_result.data)

            # Constraints DDL
            constraints_result = await self.generate_constraints_ddl(table)
            if constraints_result.success and constraints_result.data:
                all_ddl.extend(constraints_result.data)

            # Indexes DDL
            indexes_result = await self.generate_indexes_ddl(table)
            if indexes_result.success and indexes_result.data:
                all_ddl.extend(indexes_result.data)

            complete_ddl = "\n\n".join(all_ddl)

            logger.info("Generated complete DDL for table: %s", table.name)
            return FlextResult.ok(complete_ddl)

        except Exception as e:
            logger.exception("Failed to generate complete DDL for %s", table.name)
            return FlextResult.fail(
                f"Failed to generate complete DDL: {e}",
            )

    async def _generate_column_definition(
        self,
        column: ColumnMetadata,
    ) -> FlextResult[Any]:
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
                    parts.append(
                        f"DEFAULT '{self._escape_string(column.default_value)}'",
                    )
                else:
                    parts.append(f"DEFAULT {column.default_value}")

            # NOT NULL constraint
            if not column.nullable:
                parts.append("NOT NULL")

            column_def = " ".join(parts)
            return FlextResult.ok(column_def)

        except Exception as e:
            logger.exception("Failed to generate column definition for %s", column.name)
            return FlextResult.fail(
                f"Failed to generate column definition: {e}",
            )

    async def _generate_constraint_ddl(
        self,
        table: TableMetadata,
        constraint: ConstraintMetadata,
    ) -> FlextResult[Any]:
        """Generate constraint DDL statement."""
        try:
            table_name = f"{table.schema_name}.{table.name}"

            if constraint.constraint_type == "PRIMARY_KEY":
                columns = ", ".join(constraint.column_names)
                ddl = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint.name} PRIMARY KEY ({columns})"

            elif constraint.constraint_type == "FOREIGN_KEY":
                columns = ", ".join(constraint.column_names)
                ref_columns = ", ".join(constraint.referenced_columns)
                ddl = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint.name} FOREIGN KEY ({columns}) REFERENCES {constraint.referenced_table} ({ref_columns})"

            elif constraint.constraint_type == "UNIQUE":
                columns = ", ".join(constraint.column_names)
                ddl = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint.name} UNIQUE ({columns})"

            elif constraint.constraint_type == "CHECK":
                ddl = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint.name} CHECK ({constraint.check_condition})"

            else:
                return FlextResult.fail(
                    f"Unsupported constraint type: {constraint.constraint_type}",
                )

            # Add deferrable clause if needed
            if constraint.deferrable:
                ddl += " DEFERRABLE"
                if constraint.initially_deferred:
                    ddl += " INITIALLY DEFERRED"

            ddl += ";"

            return FlextResult.ok(ddl)

        except Exception as e:
            logger.exception(
                "Failed to generate constraint DDL for %s",
                constraint.name,
            )
            return FlextResult.fail(
                f"Failed to generate constraint DDL: {e}",
            )

    async def _generate_index_ddl(
        self,
        table: TableMetadata,
        index: IndexMetadata,
    ) -> FlextResult[Any]:
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

            return FlextResult.ok(ddl)

        except Exception as e:
            logger.exception("Failed to generate index DDL for %s", index.name)
            return FlextResult.fail(
                f"Failed to generate index DDL: {e}",
            )

    async def _generate_table_comments(
        self,
        table: TableMetadata,
    ) -> FlextResult[Any]:
        """Generate table and column comments."""
        try:
            comments = []
            table_name = f"{table.schema_name}.{table.name}"

            # Table comment would be added here if table metadata included comments field

            # Column comments
            for col in table.columns:
                if col.comments:
                    comment_sql = f"COMMENT ON COLUMN {table_name}.{col.name} IS '{self._escape_string(col.comments)}';"
                    comments.append(comment_sql)

            return FlextResult.ok("\n".join(comments))

        except Exception as e:
            logger.exception("Failed to generate comments for table %s", table.name)
            return FlextResult.fail(
                f"Failed to generate comments: {e}",
            )

    def _escape_string(self, value: str) -> str:
        """Escape string for SQL."""
        return value.replace("'", "''")

    async def generate_drop_table_ddl(
        self,
        table: TableMetadata,
        *,
        cascade: bool = False,
    ) -> FlextResult[Any]:
        """Generate DROP TABLE DDL statement."""
        try:
            table_name = f"{table.schema_name}.{table.name}"
            ddl = f"DROP TABLE {table_name}"

            if cascade:
                ddl += " CASCADE CONSTRAINTS"

            ddl += ";"

            logger.info("Generated DROP TABLE DDL for: %s", table.name)
            return FlextResult.ok(ddl)

        except Exception as e:
            logger.exception("Failed to generate DROP TABLE DDL for %s", table.name)
            return FlextResult.fail(
                f"Failed to generate DROP TABLE DDL: {e}",
            )

    async def generate_truncate_table_ddl(
        self,
        table: TableMetadata,
    ) -> FlextResult[Any]:
        """Generate TRUNCATE TABLE DDL statement."""
        try:
            table_name = f"{table.schema_name}.{table.name}"
            ddl = f"TRUNCATE TABLE {table_name};"

            logger.info("Generated TRUNCATE TABLE DDL for: %s", table.name)
            return FlextResult.ok(ddl)

        except Exception as e:
            logger.exception("Failed to generate TRUNCATE TABLE DDL for %s", table.name)
            return FlextResult.fail(
                f"Failed to generate TRUNCATE TABLE DDL: {e}",
            )

    async def generate_sequence_ddl(
        self,
        sequence_data: dict[str, Any],
        schema_name: str,
    ) -> FlextResult[Any]:
        """Generate CREATE SEQUENCE DDL statement."""
        try:
            sequence_name = f"{schema_name}.{sequence_data['name']}"

            ddl_parts = [f"CREATE SEQUENCE {sequence_name}"]

            if sequence_data.get("min_value") is not None:
                ddl_parts.append(f"MINVALUE {sequence_data['min_value']}")

            if sequence_data.get("max_value") is not None:
                ddl_parts.append(f"MAXVALUE {sequence_data['max_value']}")

            if sequence_data.get("increment_by"):
                ddl_parts.append(f"INCREMENT BY {sequence_data['increment_by']}")

            if sequence_data.get("cycle_flag") == "Y":
                ddl_parts.append("CYCLE")
            else:
                ddl_parts.append("NOCYCLE")

            ddl_parts.append("CACHE 20")  # Default cache size

            ddl = " ".join(ddl_parts) + ";"

            logger.info("Generated CREATE SEQUENCE DDL for: %s", sequence_data["name"])
            return FlextResult.ok(ddl)

        except Exception as e:
            logger.exception(
                "Failed to generate SEQUENCE DDL for %s",
                sequence_data.get("name", "unknown"),
            )
            return FlextResult.fail(
                f"Failed to generate SEQUENCE DDL: {e}",
            )

    async def generate_view_ddl(
        self,
        view_data: dict[str, Any],
        schema_name: str,
    ) -> FlextResult[Any]:
        """Generate CREATE VIEW DDL statement."""
        try:
            view_name = f"{schema_name}.{view_data['name']}"

            if not view_data.get("text"):
                return FlextResult.fail(
                    f"View {view_data['name']} has no definition text",
                )

            ddl = f"CREATE OR REPLACE VIEW {view_name} AS\n{view_data['text']}"

            # Add semicolon if not present
            if not ddl.rstrip().endswith(";"):
                ddl += ";"

            logger.info("Generated CREATE VIEW DDL for: %s", view_data["name"])
            return FlextResult.ok(ddl)

        except Exception as e:
            logger.exception(
                "Failed to generate VIEW DDL for %s",
                view_data.get("name", "unknown"),
            )
            return FlextResult.fail(
                f"Failed to generate VIEW DDL: {e}",
            )

    async def generate_schema_ddl(
        self,
        schema_metadata: SchemaMetadata,
    ) -> FlextResult[Any]:
        """Generate complete schema DDL including all objects."""
        try:
            all_ddl: list[str] = []

            # Header comment
            all_ddl.append(f"-- DDL Script for Schema: {schema_metadata.name}")
            all_ddl.append(f"-- Generated at: {schema_metadata.analyzed_at}")
            all_ddl.append(f"-- Total Objects: {schema_metadata.total_objects}")
            all_ddl.append("")

            # Generate sequences first (tables may depend on them)
            all_ddl.append("-- ===== SEQUENCES =====")
            for sequence in schema_metadata.sequences:
                seq_result = await self.generate_sequence_ddl(
                    sequence,
                    schema_metadata.name,
                )
                if seq_result.success and seq_result.data:
                    all_ddl.extend((seq_result.data, ""))

            # Generate tables
            all_ddl.append("-- ===== TABLES =====")
            for table in schema_metadata.tables:
                table_result = await self.generate_complete_ddl(table)
                if table_result.success and table_result.data:
                    all_ddl.extend((table_result.data, ""))

            # Generate views (depend on tables)
            all_ddl.append("-- ===== VIEWS =====")
            for view_data in schema_metadata.views:
                # Convert ViewMetadata to dict for compatibility
                view_dict = {
                    "name": view_data.name,
                    "text": view_data.text,
                }
                view_result = await self.generate_view_ddl(
                    view_dict,
                    schema_metadata.name,
                )
                if view_result.success and view_result.data:
                    all_ddl.extend((view_result.data, ""))

            complete_ddl = "\n".join(all_ddl)

            logger.info(
                "Generated complete schema DDL for: %s (%d objects)",
                schema_metadata.name,
                schema_metadata.total_objects,
            )
            return FlextResult.ok(complete_ddl)

        except Exception as e:
            logger.exception(
                "Failed to generate schema DDL for %s",
                schema_metadata.name,
            )
            return FlextResult.fail(
                f"Failed to generate schema DDL: {e}",
            )

    async def generate_partitioned_table_ddl(
        self,
        table: TableMetadata,
        partition_info: dict[str, Any],
    ) -> FlextResult[Any]:
        """Generate DDL for partitioned table (advanced Oracle feature)."""
        try:
            # Start with basic table DDL
            basic_result = await self.generate_table_ddl(table)
            if not basic_result.success:
                return basic_result

            ddl = basic_result.data
            if not ddl:
                return FlextResult.fail(
                    "No DDL generated for partitioned table",
                )

            # Remove the final semicolon to add partitioning
            ddl = ddl.removesuffix(";")

            # Add partition clause
            partition_type = partition_info.get("type", "RANGE")
            partition_columns = partition_info.get("columns", [])

            if partition_columns:
                ddl += (
                    f"\nPARTITION BY {partition_type} ({', '.join(partition_columns)})"
                )

                # Add partition definitions if provided
                partitions = partition_info.get("partitions", [])
                if partitions:
                    ddl += " ("
                    partition_ddl = []
                    for partition in partitions:
                        part_name = partition.get("name")
                        part_values = partition.get("values")
                        if part_name and part_values:
                            partition_ddl.append(
                                f"  PARTITION {part_name} VALUES LESS THAN ({part_values})",
                            )

                    ddl += ",\n".join(partition_ddl)
                    ddl += "\n)"

            ddl += ";"

            logger.info("Generated partitioned table DDL for: %s", table.name)
            return FlextResult.ok(ddl)

        except Exception as e:
            logger.exception(
                "Failed to generate partitioned table DDL for %s",
                table.name,
            )
            return FlextResult.fail(
                f"Failed to generate partitioned table DDL: {e}",
            )

    async def generate_tablespace_ddl(
        self,
        tablespace_info: dict[str, Any],
    ) -> FlextResult[Any]:
        """Generate CREATE TABLESPACE DDL statement."""
        try:
            tablespace_name = tablespace_info["name"]
            datafile = tablespace_info.get(
                "datafile",
                f"/oracle/oradata/{tablespace_name}.dbf",
            )
            size = tablespace_info.get("size", "100M")
            autoextend = tablespace_info.get("autoextend", True)

            ddl_parts = [
                f"CREATE TABLESPACE {tablespace_name}",
                f"DATAFILE '{datafile}'",
                f"SIZE {size}",
            ]

            if autoextend:
                ddl_parts.append("AUTOEXTEND ON")
                next_size = tablespace_info.get("next", "10M")
                max_size = tablespace_info.get("maxsize", "UNLIMITED")
                ddl_parts.extend((f"NEXT {next_size}", f"MAXSIZE {max_size}"))

            # Add extent management
            ddl_parts.append("EXTENT MANAGEMENT LOCAL")
            ddl_parts.append("AUTOALLOCATE")

            # Add segment space management
            ddl_parts.append("SEGMENT SPACE MANAGEMENT AUTO")

            ddl = " ".join(ddl_parts) + ";"

            logger.info("Generated CREATE TABLESPACE DDL for: %s", tablespace_name)
            return FlextResult.ok(ddl)

        except Exception as e:
            logger.exception(
                "Failed to generate TABLESPACE DDL for %s",
                tablespace_info.get("name", "unknown"),
            )
            return FlextResult.fail(
                f"Failed to generate TABLESPACE DDL: {e}",
            )

"""Oracle DDL (Data Definition Language) generation utilities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_db_oracle.schema.metadata import (
        ColumnMetadata,
        ConstraintMetadata,
        IndexMetadata,
        TableMetadata,
    )

logger = logging.getLogger(__name__)


class DDLGenerator:
    """Generates Oracle DDL statements from metadata."""

    def __init__(self, include_comments: bool = True) -> None:
        """Initialize DDL generator.

        Args:
            include_comments: Whether to include comments in generated DDL.

        """
        self.include_comments = include_comments

    def generate_table_ddl(self, table: TableMetadata) -> str:
        """Generate CREATE TABLE DDL statement.

        Args:
            table: Table metadata.

        Returns:
            Complete CREATE TABLE DDL statement.

        """
        if not table.columns:
            msg = f"Table {table.name} has no columns defined"
            raise ValueError(msg)

        lines = []

        # Table creation
        lines.append(f"CREATE TABLE {table.schema_name}.{table.name} (")

        # Columns
        column_ddl = []
        for col in table.columns:
            col_def = self._generate_column_definition(col)
            column_ddl.append(f"    {col_def}")

        lines.extend((",\n".join(column_ddl), ")"))

        # Tablespace
        if table.tablespace:
            lines.append(f"TABLESPACE {table.tablespace}")

        lines.append(";")

        ddl = "\n".join(lines)

        # Add table comments
        if self.include_comments and table.comments:
            ddl += f"\n\nCOMMENT ON TABLE {table.schema_name}.{table.name} IS '{self._escape_comment(table.comments)}';"

        # Add column comments
        if self.include_comments and table.columns:
            for col in table.columns:
                if col.comments:
                    ddl += f"\nCOMMENT ON COLUMN {table.schema_name}.{table.name}.{col.name} IS '{self._escape_comment(col.comments)}';"

        return ddl

    def generate_constraints_ddl(self, table: TableMetadata) -> list[str]:
        """Generate DDL for table constraints.

        Args:
            table: Table metadata.

        Returns:
            List of ALTER TABLE statements for constraints.

        """
        if not table.constraints:
            return []

        statements = []

        for constraint in table.constraints:
            ddl = self._generate_constraint_ddl(
                table.schema_name, table.name, constraint
            )
            if ddl:
                statements.append(ddl)

        return statements

    def generate_indexes_ddl(self, table: TableMetadata) -> list[str]:
        """Generate DDL for table indexes.

        Args:
            table: Table metadata.

        Returns:
            List of CREATE INDEX statements.

        """
        if not table.indexes:
            return []

        statements = []

        for index in table.indexes:
            # Skip primary key indexes (created automatically)
            if index.is_primary:
                continue

            ddl = self._generate_index_ddl(table.schema_name, index)
            if ddl:
                statements.append(ddl)

        return statements

    def generate_complete_table_ddl(self, table: TableMetadata) -> str:
        """Generate complete DDL for a table including constraints and indexes.

        Args:
            table: Table metadata.

        Returns:
            Complete DDL script for the table.

        """
        ddl_parts = []

        # Main table DDL
        ddl_parts.append(self.generate_table_ddl(table))

        # Constraints
        constraint_ddls = self.generate_constraints_ddl(table)
        if constraint_ddls:
            ddl_parts.append("")  # Empty line
            ddl_parts.extend(constraint_ddls)

        # Indexes
        index_ddls = self.generate_indexes_ddl(table)
        if index_ddls:
            ddl_parts.append("")  # Empty line
            ddl_parts.extend(index_ddls)

        return "\n".join(ddl_parts)

    def generate_drop_table_ddl(
        self, schema_name: str, table_name: str, cascade: bool = False
    ) -> str:
        """Generate DROP TABLE DDL statement.

        Args:
            schema_name: Schema name.
            table_name: Table name.
            cascade: Whether to include CASCADE CONSTRAINTS.

        Returns:
            DROP TABLE DDL statement.

        """
        ddl = f"DROP TABLE {schema_name}.{table_name}"
        if cascade:
            ddl += " CASCADE CONSTRAINTS"
        ddl += ";"
        return ddl

    def generate_schema_ddl(
        self, tables: list[TableMetadata], include_drops: bool = False
    ) -> str:
        """Generate DDL for multiple tables in proper dependency order.

        Args:
            tables: List of table metadata.
            include_drops: Whether to include DROP statements.

        Returns:
            Complete schema DDL script.

        """
        ddl_parts = []

        if include_drops:
            # Drop tables in reverse dependency order
            sorted_tables = self._sort_tables_by_dependencies(tables, reverse=True)
            ddl_parts.append("-- Drop existing tables")
            ddl_parts.extend(self.generate_drop_table_ddl(
                        table.schema_name, table.name, cascade=True
                    ) for table in sorted_tables)
            ddl_parts.append("")

        # Create tables in dependency order
        sorted_tables = self._sort_tables_by_dependencies(tables)

        ddl_parts.append("-- Create tables")
        for table in sorted_tables:
            ddl_parts.extend((self.generate_complete_table_ddl(table), ""))

        return "\n".join(ddl_parts)

    def _generate_column_definition(self, col: ColumnMetadata) -> str:
        """Generate column definition for CREATE TABLE."""
        parts = [col.name]

        # Data type
        data_type = col.data_type.upper()

        # Add length/precision for applicable types
        if col.max_length and data_type in {"VARCHAR2", "CHAR", "NVARCHAR2", "NCHAR"}:
            data_type += f"({col.max_length})"
        elif col.precision is not None and data_type in {
            "NUMBER",
            "DECIMAL",
            "NUMERIC",
        }:
            if col.scale is not None:
                data_type += f"({col.precision},{col.scale})"
            else:
                data_type += f"({col.precision})"

        parts.append(data_type)

        # Default value
        if col.default_value:
            parts.append(f"DEFAULT {col.default_value}")

        # Nullable
        if not col.nullable:
            parts.append("NOT NULL")

        return " ".join(parts)

    def _generate_constraint_ddl(
        self, schema_name: str, table_name: str, constraint: ConstraintMetadata
    ) -> str | None:
        """Generate DDL for a single constraint."""
        if constraint.constraint_type == "PRIMARY_KEY":
            columns = ", ".join(constraint.column_names)
            return f"ALTER TABLE {schema_name}.{table_name} ADD CONSTRAINT {constraint.name} PRIMARY KEY ({columns});"

        if constraint.constraint_type == "FOREIGN_KEY":
            if not constraint.referenced_table or not constraint.referenced_columns:
                logger.warning(
                    "Foreign key constraint %s missing reference information",
                    constraint.name,
                )
                return None

            columns = ", ".join(constraint.column_names)
            ref_columns = ", ".join(constraint.referenced_columns)
            return f"ALTER TABLE {schema_name}.{table_name} ADD CONSTRAINT {constraint.name} FOREIGN KEY ({columns}) REFERENCES {constraint.referenced_table} ({ref_columns});"

        if constraint.constraint_type == "UNIQUE":
            columns = ", ".join(constraint.column_names)
            return f"ALTER TABLE {schema_name}.{table_name} ADD CONSTRAINT {constraint.name} UNIQUE ({columns});"

        if constraint.constraint_type == "CHECK":
            if not constraint.condition:
                logger.warning("Check constraint %s missing condition", constraint.name)
                return None
            return f"ALTER TABLE {schema_name}.{table_name} ADD CONSTRAINT {constraint.name} CHECK ({constraint.condition});"

        logger.warning(
            "Unsupported constraint type: %s", constraint.constraint_type
        )
        return None

    def _generate_index_ddl(self, schema_name: str, index: IndexMetadata) -> str:
        """Generate DDL for a single index."""
        index_type = "UNIQUE " if index.is_unique else ""
        columns = ", ".join(index.column_names)

        ddl = f"CREATE {index_type}INDEX {index.name} ON {schema_name}.{index.table_name} ({columns})"

        if index.tablespace:
            ddl += f" TABLESPACE {index.tablespace}"

        ddl += ";"
        return ddl

    def _sort_tables_by_dependencies(
        self, tables: list[TableMetadata], reverse: bool = False
    ) -> list[TableMetadata]:
        """Sort tables by foreign key dependencies.

        Tables with no foreign keys come first, then tables that depend on them, etc.
        If reverse=True, returns tables in reverse dependency order (for drops).
        """
        # Simple topological sort based on foreign key dependencies
        table_map = {table.name: table for table in tables}
        dependencies = {}

        # Build dependency graph
        for table in tables:
            deps = set()
            if table.constraints:
                for constraint in table.constraints:
                    if (
                        constraint.constraint_type == "FOREIGN_KEY"
                        and constraint.referenced_table
                        and constraint.referenced_table in table_map
                    ):
                        deps.add(constraint.referenced_table)
            dependencies[table.name] = deps

        # Topological sort
        sorted_names = []
        remaining = set(table_map.keys())

        while remaining:
            # Find tables with no unresolved dependencies
            ready = [name for name in remaining if not (dependencies[name] & remaining)]

            if not ready:
                # Circular dependency - just add remaining tables
                ready = list(remaining)
                logger.warning("Circular dependencies detected in tables: %s", ready)

            # Sort ready tables alphabetically for consistent output
            ready.sort()
            sorted_names.extend(ready)
            remaining -= set(ready)

        # Get sorted table objects
        sorted_tables = [table_map[name] for name in sorted_names]

        if reverse:
            sorted_tables.reverse()

        return sorted_tables

    def _escape_comment(self, comment: str) -> str:
        """Escape single quotes in comments."""
        return comment.replace("'", "''") if comment else ""

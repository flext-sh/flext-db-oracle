"""Oracle database schema analysis functionality."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .metadata import (
    ColumnMetadata,
    ConstraintMetadata,
    IndexMetadata,
    SchemaMetadata,
    TableMetadata,
)

if TYPE_CHECKING:
    from ..connection.connection import OracleConnection

logger = logging.getLogger(__name__)


class SchemaAnalyzer:
    """Analyzes Oracle database schemas and extracts metadata."""

    def __init__(self, connection: OracleConnection) -> None:
        """Initialize schema analyzer.

        Args:
            connection: Active Oracle database connection.
        """
        self.connection = connection

    def analyze_schema(self, schema_name: str | None = None) -> SchemaMetadata:
        """Analyze a complete schema and return metadata.

        Args:
            schema_name: Schema name to analyze. If None, uses current user schema.

        Returns:
            Complete schema metadata.
        """
        if schema_name is None:
            schema_name = self._get_current_schema()

        logger.info("Analyzing schema: %s", schema_name)

        # Get all tables
        tables = self.get_tables(schema_name)

        # Get all views
        views = self.get_views(schema_name)

        # Get other objects
        sequences = self.get_sequences(schema_name)
        procedures = self.get_procedures(schema_name)
        functions = self.get_functions(schema_name)
        packages = self.get_packages(schema_name)
        triggers = self.get_triggers(schema_name)

        return SchemaMetadata(
            name=schema_name,
            tables=tables,
            views=views,
            sequences=sequences,
            procedures=procedures,
            functions=functions,
            packages=packages,
            triggers=triggers,
        )

    def get_tables(self, schema_name: str) -> list[TableMetadata]:
        """Get all tables in a schema with complete metadata.

        Args:
            schema_name: Schema name.

        Returns:
            List of table metadata.
        """
        sql = """
        SELECT
            table_name,
            tablespace_name,
            created
        FROM all_tables
        WHERE owner = UPPER(:schema_name)
        ORDER BY table_name
        """

        tables = []
        rows = self.connection.fetch_all(sql, {"schema_name": schema_name})

        for row in rows:
            table_name = row[0]
            tablespace = row[1]
            created_date = str(row[2]) if row[2] else None

            # Get detailed table information
            columns = self.get_table_columns(schema_name, table_name)
            constraints = self.get_table_constraints(schema_name, table_name)
            indexes = self.get_table_indexes(schema_name, table_name)
            row_count = self.get_table_row_count(schema_name, table_name)
            comments = self.get_table_comments(schema_name, table_name)

            table_metadata = TableMetadata(
                name=table_name,
                schema_name=schema_name,
                table_type="TABLE",
                columns=columns,
                constraints=constraints,
                indexes=indexes,
                row_count=row_count,
                tablespace=tablespace,
                comments=comments,
                created_date=created_date,
            )

            tables.append(table_metadata)

        return tables

    def get_table_columns(
        self, schema_name: str, table_name: str
    ) -> list[ColumnMetadata]:
        """Get column metadata for a table.

        Args:
            schema_name: Schema name.
            table_name: Table name.

        Returns:
            List of column metadata.
        """
        sql = """
        SELECT
            c.column_name,
            c.data_type,
            c.nullable,
            c.data_default,
            c.data_length,
            c.data_precision,
            c.data_scale,
            cc.comments
        FROM all_tab_columns c
        LEFT JOIN all_col_comments cc ON c.owner = cc.owner
            AND c.table_name = cc.table_name
            AND c.column_name = cc.column_name
        WHERE c.owner = UPPER(:schema_name)
            AND c.table_name = UPPER(:table_name)
        ORDER BY c.column_id
        """

        columns = []
        rows = self.connection.fetch_all(
            sql, {"schema_name": schema_name, "table_name": table_name}
        )

        # Get primary key columns
        pk_columns = set(self._get_primary_key_columns(schema_name, table_name))

        # Get foreign key information
        fk_info = self._get_foreign_key_info(schema_name, table_name)

        for row in rows:
            column_name = row[0]

            column = ColumnMetadata(
                name=column_name,
                data_type=row[1],
                nullable=(row[2] == "Y"),
                default_value=row[3],
                max_length=row[4],
                precision=row[5],
                scale=row[6],
                is_primary_key=(column_name in pk_columns),
                is_foreign_key=(column_name in fk_info),
                foreign_key_table=fk_info.get(column_name, {}).get("table"),
                foreign_key_column=fk_info.get(column_name, {}).get("column"),
                comments=row[7],
            )

            columns.append(column)

        return columns

    def get_table_constraints(
        self, schema_name: str, table_name: str
    ) -> list[ConstraintMetadata]:
        """Get constraint metadata for a table.

        Args:
            schema_name: Schema name.
            table_name: Table name.

        Returns:
            List of constraint metadata.
        """
        sql = """
        SELECT
            c.constraint_name,
            c.constraint_type,
            c.status,
            c.validated,
            c.r_owner,
            c.r_constraint_name,
            c.search_condition
        FROM all_constraints c
        WHERE c.owner = UPPER(:schema_name)
            AND c.table_name = UPPER(:table_name)
        ORDER BY c.constraint_name
        """

        constraints = []
        rows = self.connection.fetch_all(
            sql, {"schema_name": schema_name, "table_name": table_name}
        )

        for row in rows:
            constraint_name = row[0]
            constraint_type = row[1]
            status = row[2]
            validated = row[3]

            # Get constraint columns
            columns = self._get_constraint_columns(schema_name, constraint_name)

            # Get referenced table/columns for foreign keys
            referenced_table = None
            referenced_columns = None
            if constraint_type == "R" and row[4] and row[5]:  # Foreign key
                referenced_table, referenced_columns = self._get_referenced_info(
                    row[4], row[5]
                )

            constraint = ConstraintMetadata(
                name=constraint_name,
                constraint_type=self._constraint_type_display(constraint_type),
                table_name=table_name,
                column_names=columns,
                referenced_table=referenced_table,
                referenced_columns=referenced_columns,
                condition=row[6],  # search_condition for CHECK constraints
                is_enabled=(status == "ENABLED"),
                is_validated=(validated == "VALIDATED"),
            )

            constraints.append(constraint)

        return constraints

    def get_table_indexes(
        self, schema_name: str, table_name: str
    ) -> list[IndexMetadata]:
        """Get index metadata for a table.

        Args:
            schema_name: Schema name.
            table_name: Table name.

        Returns:
            List of index metadata.
        """
        sql = """
        SELECT
            i.index_name,
            i.uniqueness,
            i.index_type,
            i.tablespace_name,
            i.status
        FROM all_indexes i
        WHERE i.table_owner = UPPER(:schema_name)
            AND i.table_name = UPPER(:table_name)
        ORDER BY i.index_name
        """

        indexes = []
        rows = self.connection.fetch_all(
            sql, {"schema_name": schema_name, "table_name": table_name}
        )

        for row in rows:
            index_name = row[0]

            # Get index columns
            columns = self._get_index_columns(schema_name, index_name)

            # Check if this is a primary key index
            is_primary = self._is_primary_key_index(schema_name, table_name, index_name)

            index = IndexMetadata(
                name=index_name,
                table_name=table_name,
                column_names=columns,
                is_unique=(row[1] == "UNIQUE"),
                is_primary=is_primary,
                index_type=row[2],
                tablespace=row[3],
                is_valid=(row[4] == "VALID"),
            )

            indexes.append(index)

        return indexes

    def get_views(self, schema_name: str) -> list[TableMetadata]:
        """Get all views in a schema.

        Args:
            schema_name: Schema name.

        Returns:
            List of view metadata.
        """
        sql = """
        SELECT view_name
        FROM all_views
        WHERE owner = UPPER(:schema_name)
        ORDER BY view_name
        """

        views = []
        rows = self.connection.fetch_all(sql, {"schema_name": schema_name})

        for row in rows:
            view_name = row[0]

            # Get view columns (similar to table columns)
            columns = self.get_table_columns(schema_name, view_name)
            comments = self.get_table_comments(schema_name, view_name)

            view_metadata = TableMetadata(
                name=view_name,
                schema_name=schema_name,
                table_type="VIEW",
                columns=columns,
                comments=comments,
            )

            views.append(view_metadata)

        return views

    def get_sequences(self, schema_name: str) -> list[str]:
        """Get all sequences in a schema."""
        sql = """
        SELECT sequence_name
        FROM all_sequences
        WHERE sequence_owner = UPPER(:schema_name)
        ORDER BY sequence_name
        """

        rows = self.connection.fetch_all(sql, {"schema_name": schema_name})
        return [row[0] for row in rows]

    def get_procedures(self, schema_name: str) -> list[str]:
        """Get all procedures in a schema."""
        sql = """
        SELECT object_name
        FROM all_objects
        WHERE owner = UPPER(:schema_name)
            AND object_type = 'PROCEDURE'
        ORDER BY object_name
        """

        rows = self.connection.fetch_all(sql, {"schema_name": schema_name})
        return [row[0] for row in rows]

    def get_functions(self, schema_name: str) -> list[str]:
        """Get all functions in a schema."""
        sql = """
        SELECT object_name
        FROM all_objects
        WHERE owner = UPPER(:schema_name)
            AND object_type = 'FUNCTION'
        ORDER BY object_name
        """

        rows = self.connection.fetch_all(sql, {"schema_name": schema_name})
        return [row[0] for row in rows]

    def get_packages(self, schema_name: str) -> list[str]:
        """Get all packages in a schema."""
        sql = """
        SELECT object_name
        FROM all_objects
        WHERE owner = UPPER(:schema_name)
            AND object_type = 'PACKAGE'
        ORDER BY object_name
        """

        rows = self.connection.fetch_all(sql, {"schema_name": schema_name})
        return [row[0] for row in rows]

    def get_triggers(self, schema_name: str) -> list[str]:
        """Get all triggers in a schema."""
        sql = """
        SELECT trigger_name
        FROM all_triggers
        WHERE owner = UPPER(:schema_name)
        ORDER BY trigger_name
        """

        rows = self.connection.fetch_all(sql, {"schema_name": schema_name})
        return [row[0] for row in rows]

    def get_table_row_count(self, schema_name: str, table_name: str) -> int | None:
        """Get approximate row count for a table."""
        try:
            sql = """
            SELECT num_rows
            FROM all_tables
            WHERE owner = UPPER(:schema_name)
                AND table_name = UPPER(:table_name)
            """

            result = self.connection.fetch_one(
                sql, {"schema_name": schema_name, "table_name": table_name}
            )

            return result[0] if result and result[0] is not None else None

        except Exception as e:
            logger.warning(
                "Could not get row count for %s.%s: %s", schema_name, table_name, e
            )
            return None

    def get_table_comments(self, schema_name: str, table_name: str) -> str | None:
        """Get table comments."""
        sql = """
        SELECT comments
        FROM all_tab_comments
        WHERE owner = UPPER(:schema_name)
            AND table_name = UPPER(:table_name)
        """

        result = self.connection.fetch_one(
            sql, {"schema_name": schema_name, "table_name": table_name}
        )

        return result[0] if result and result[0] else None

    def _get_current_schema(self) -> str:
        """Get the current schema name."""
        result = self.connection.fetch_one("SELECT USER FROM DUAL")
        return result[0] if result else "UNKNOWN"

    def _get_primary_key_columns(self, schema_name: str, table_name: str) -> list[str]:
        """Get primary key column names for a table."""
        sql = """
        SELECT cc.column_name
        FROM all_constraints c
        JOIN all_cons_columns cc ON c.constraint_name = cc.constraint_name
            AND c.owner = cc.owner
        WHERE c.owner = UPPER(:schema_name)
            AND c.table_name = UPPER(:table_name)
            AND c.constraint_type = 'P'
        ORDER BY cc.position
        """

        rows = self.connection.fetch_all(
            sql, {"schema_name": schema_name, "table_name": table_name}
        )

        return [row[0] for row in rows]

    def _get_foreign_key_info(
        self, schema_name: str, table_name: str
    ) -> dict[str, dict[str, str]]:
        """Get foreign key information for a table."""
        sql = """
        SELECT
            cc.column_name,
            rc.table_name AS referenced_table,
            rcc.column_name AS referenced_column
        FROM all_constraints c
        JOIN all_cons_columns cc ON c.constraint_name = cc.constraint_name
            AND c.owner = cc.owner
        JOIN all_constraints rc ON c.r_constraint_name = rc.constraint_name
            AND c.r_owner = rc.owner
        JOIN all_cons_columns rcc ON rc.constraint_name = rcc.constraint_name
            AND rc.owner = rcc.owner
            AND cc.position = rcc.position
        WHERE c.owner = UPPER(:schema_name)
            AND c.table_name = UPPER(:table_name)
            AND c.constraint_type = 'R'
        """

        fk_info = {}
        rows = self.connection.fetch_all(
            sql, {"schema_name": schema_name, "table_name": table_name}
        )

        for row in rows:
            fk_info[row[0]] = {"table": row[1], "column": row[2]}

        return fk_info

    def _get_constraint_columns(
        self, schema_name: str, constraint_name: str
    ) -> list[str]:
        """Get column names for a constraint."""
        sql = """
        SELECT column_name
        FROM all_cons_columns
        WHERE owner = UPPER(:schema_name)
            AND constraint_name = UPPER(:constraint_name)
        ORDER BY position
        """

        rows = self.connection.fetch_all(
            sql, {"schema_name": schema_name, "constraint_name": constraint_name}
        )

        return [row[0] for row in rows]

    def _get_referenced_info(
        self, ref_owner: str, ref_constraint_name: str
    ) -> tuple[str | None, list[str] | None]:
        """Get referenced table and columns for a foreign key constraint."""
        sql = """
        SELECT c.table_name
        FROM all_constraints c
        WHERE c.owner = UPPER(:ref_owner)
            AND c.constraint_name = UPPER(:ref_constraint_name)
        """

        result = self.connection.fetch_one(
            sql, {"ref_owner": ref_owner, "ref_constraint_name": ref_constraint_name}
        )

        if not result:
            return None, None

        ref_table = result[0]

        # Get referenced columns
        ref_columns = self._get_constraint_columns(ref_owner, ref_constraint_name)

        return ref_table, ref_columns

    def _get_index_columns(self, schema_name: str, index_name: str) -> list[str]:
        """Get column names for an index."""
        sql = """
        SELECT column_name
        FROM all_ind_columns
        WHERE index_owner = UPPER(:schema_name)
            AND index_name = UPPER(:index_name)
        ORDER BY column_position
        """

        rows = self.connection.fetch_all(
            sql, {"schema_name": schema_name, "index_name": index_name}
        )

        return [row[0] for row in rows]

    def _is_primary_key_index(
        self, schema_name: str, table_name: str, index_name: str
    ) -> bool:
        """Check if an index is created for a primary key constraint."""
        sql = """
        SELECT COUNT(*)
        FROM all_constraints c
        WHERE c.owner = UPPER(:schema_name)
            AND c.table_name = UPPER(:table_name)
            AND c.constraint_type = 'P'
            AND c.index_name = UPPER(:index_name)
        """

        result = self.connection.fetch_one(
            sql,
            {
                "schema_name": schema_name,
                "table_name": table_name,
                "index_name": index_name,
            },
        )

        return bool(result and result[0] > 0)

    def _constraint_type_display(self, constraint_type: str) -> str:
        """Convert Oracle constraint type code to display name."""
        type_map = {
            "P": "PRIMARY_KEY",
            "R": "FOREIGN_KEY",
            "U": "UNIQUE",
            "C": "CHECK",
            "V": "VIEW_CHECK",
            "O": "VIEW_READONLY",
        }
        return type_map.get(constraint_type, constraint_type)

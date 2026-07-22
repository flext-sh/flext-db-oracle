"""Schema and metadata service mixin for flext-db-oracle.

Provides Oracle schema introspection: tables, columns,
primary keys, table metadata, row counts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, select, table
from sqlalchemy.dialects.oracle import dialect as oracle_dialect
from sqlalchemy.exc import (
    DatabaseError as SQLAlchemyDatabaseError,
    OperationalError as SQLAlchemyOperationalError,
    SQLAlchemyError,
)
from sqlalchemy.sql import quoted_name

from flext_db_oracle import FlextDbOracleServiceBase, c, m, p, t, u

if TYPE_CHECKING:
    from collections.abc import Sequence


class FlextDbOracleServiceSchema(FlextDbOracleServiceBase):
    """Mixin providing schema introspection for FlextDbOracleServices.

    Handles: get_columns, get_primary_keys, get_primary_key_columns,
    get_schemas, get_tables, get_table_metadata, get_table_row_count.
    """

    def fetch_columns(
        self, table_name: str, schema_name: str | None = None
    ) -> p.Result[Sequence[m.DbOracle.Column]]:
        """Get column information for Oracle table."""
        if schema_name:
            sql = "\nSELECT column_name, data_type, data_length, data_precision, data_scale, nullable\nFROM all_tab_columns\nWHERE table_name = UPPER(:table_name) AND owner = UPPER(:schema_name)\nORDER BY column_id\n"
            params = m.ConfigMap(
                root={"table_name": table_name, "schema_name": schema_name}
            )
        else:
            sql = "\nSELECT column_name, data_type, data_length, data_precision, data_scale, nullable\nFROM user_tab_columns\nWHERE table_name = UPPER(:table_name)\nORDER BY column_id\n"
            params = m.ConfigMap(root={"table_name": table_name})
        return self.execute_query(sql, params).map(
            lambda rows: [
                m.DbOracle.Column(
                    name=str(
                        row.root.get("COLUMN_NAME") or row.root.get("column_name", "")
                    ),
                    data_type=str(
                        row.root.get("DATA_TYPE") or row.root.get("data_type", "")
                    ),
                    nullable=str(
                        row.root.get("NULLABLE") or row.root.get("nullable", "Y")
                    )
                    == "Y",
                    primary_key=False,
                    default_value=str(
                        row.root.get("DATA_DEFAULT") or row.root.get("data_default", "")
                    ),
                )
                for row in rows
            ]
        )

    def fetch_primary_key_columns(
        self, table_name: str, schema_name: str | None = None
    ) -> p.Result[t.StrSequence]:
        """Alias for get_primary_keys."""
        return self.fetch_primary_keys(table_name, schema_name)

    def fetch_primary_keys(
        self, table_name: str, schema: str | None = None
    ) -> p.Result[t.StrSequence]:
        """Get primary key column names for specified table."""

        def _fetch_keys() -> t.StrSequence:
            if schema:
                sql = "\n                SELECT column_name\n                FROM all_constraints c, all_cons_columns cc\n                WHERE c.constraint_type = 'P'\n                AND c.constraint_name = cc.constraint_name\n                AND c.table_name = UPPER(:table_name)\n                AND c.owner = UPPER(:schema)\n                ORDER BY cc.position\n                "
                params = m.ConfigMap(root={"table_name": table_name, "schema": schema})
            else:
                sql = "\n                SELECT column_name\n                FROM user_constraints c, user_cons_columns cc\n                WHERE c.constraint_type = 'P'\n                AND c.constraint_name = cc.constraint_name\n                AND c.table_name = UPPER(:table_name)\n                ORDER BY cc.position\n                "
                params = m.ConfigMap(root={"table_name": table_name})
            query_result = self.execute_query(sql, params)
            if query_result.failure:
                raise RuntimeError(query_result.error or "Query execution failed")
            return [str(row.root["column_name"]) for row in query_result.value]

        return u.try_(
            _fetch_keys,
            catch=(
                t.DbOracle.OracleDatabaseError,
                t.DbOracle.OracleInterfaceError,
                ConnectionError,
                SQLAlchemyDatabaseError,
                SQLAlchemyOperationalError,
                SQLAlchemyError,
                OSError,
                RuntimeError,
            ),
        ).map_error(lambda e: f"Failed to get primary keys: {e}")

    def fetch_schemas(self) -> p.Result[t.StrSequence]:
        """Get list of Oracle schemas."""
        sql = "SELECT username as schema_name FROM all_users WHERE username NOT IN ('SYS', 'SYSTEM', 'ANONYMOUS', 'XDB', 'CTXSYS', 'MDSYS', 'WMSYS') ORDER BY username"
        return self.execute_query(sql).map(
            lambda rows: [
                str(row.root.get("SCHEMA_NAME") or row.root.get("schema_name", ""))
                for row in rows
            ]
        )

    def fetch_table_metadata(
        self, table_name: str, schema: str | None = None
    ) -> p.Result[m.DbOracle.TableMetadata]:
        """Get complete table metadata."""

        def _fetch_metadata() -> m.DbOracle.TableMetadata:
            columns_result = self.fetch_columns(table_name, schema)
            if columns_result.failure:
                raise RuntimeError(columns_result.error or "Failed to get columns")

            pk_result = self.fetch_primary_keys(table_name, schema)
            if pk_result.failure:
                raise RuntimeError(pk_result.error or "Failed to get primary keys")

            return m.DbOracle.TableMetadata(
                table_name=table_name,
                schema_name=schema or "",
                columns=[
                    m.DbOracle.ColumnMetadata(
                        name=column.name,
                        data_type=column.data_type,
                        nullable=column.nullable,
                    )
                    for column in columns_result.value
                ],
                primary_keys=pk_result.value,
            )

        return u.try_(
            _fetch_metadata,
            catch=(
                t.DbOracle.OracleDatabaseError,
                t.DbOracle.OracleInterfaceError,
                ConnectionError,
                SQLAlchemyOperationalError,
                OSError,
                RuntimeError,
            ),
        ).map_error(lambda e: f"Failed to get table metadata: {e}")

    def fetch_table_row_count(
        self, table_name: str, schema_name: str | None = None
    ) -> p.Result[int]:
        """Get row count through SQLAlchemy Core Oracle compilation."""

        def _fetch_count() -> int:
            statement = select(func.count().label("count")).select_from(
                table(
                    table_name.upper()
                    if c.DbOracle.IDENTIFIER_RE.fullmatch(table_name)
                    else quoted_name(table_name, True),
                    schema=(
                        schema_name.upper()
                        if schema_name
                        and c.DbOracle.IDENTIFIER_RE.fullmatch(schema_name)
                        else quoted_name(schema_name, True)
                        if schema_name
                        else None
                    ),
                )
            )
            sql = c.DbOracle.collapse_whitespace(
                str(statement.compile(dialect=oracle_dialect()))
            ).strip()
            query_result = self.execute_query(sql)
            if query_result.failure:
                raise RuntimeError(query_result.error or "Query execution failed")
            return self._parse_count_from_rows(query_result.value)

        return u.try_(
            _fetch_count,
            catch=(
                t.DbOracle.OracleDatabaseError,
                t.DbOracle.OracleInterfaceError,
                ConnectionError,
                SQLAlchemyOperationalError,
                OSError,
                RuntimeError,
            ),
        ).map_error(lambda e: f"Failed to get row count: {e}")

    def fetch_tables(self, schema: str | None = None) -> p.Result[t.StrSequence]:
        """Get list of tables in Oracle schema."""
        if schema:
            sql = "SELECT table_name FROM all_tables WHERE owner = UPPER(:schema_name) ORDER BY table_name"
            params: m.ConfigMap | None = m.ConfigMap(root={"schema_name": schema})
        else:
            sql = "SELECT table_name FROM user_tables ORDER BY table_name"
            params = None
        return self.execute_query(sql, params).map(
            lambda rows: [
                str(row.root.get("TABLE_NAME") or row.root.get("table_name", ""))
                for row in rows
            ]
        )


__all__: list[str] = ["FlextDbOracleServiceSchema"]

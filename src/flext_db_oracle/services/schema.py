"""Schema and metadata service mixin for flext-db-oracle.

Provides Oracle schema introspection: tables, columns,
primary keys, table metadata, row counts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence

from flext_core import r
from sqlalchemy.exc import (
    DatabaseError as SQLAlchemyDatabaseError,
    OperationalError as SQLAlchemyOperationalError,
    SQLAlchemyError,
)

from flext_db_oracle import FlextDbOracleModels, FlextDbOracleServiceBase, t, u


class FlextDbOracleServiceSchema(FlextDbOracleServiceBase):
    """Mixin providing schema introspection for FlextDbOracleServices.

    Handles: get_columns, get_primary_keys, get_primary_key_columns,
    get_schemas, get_tables, get_table_metadata, get_table_row_count.
    """

    def get_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> r[Sequence[FlextDbOracleModels.DbOracle.Column]]:
        """Get column information for Oracle table."""
        if schema_name:
            sql = "\nSELECT column_name, data_type, data_length, data_precision, data_scale, nullable\nFROM all_tab_columns\nWHERE table_name = UPPER(:table_name) AND owner = UPPER(:schema_name)\nORDER BY column_id\n"
            params = t.ConfigMap(
                root={"table_name": table_name, "schema_name": schema_name},
            )
        else:
            sql = "\nSELECT column_name, data_type, data_length, data_precision, data_scale, nullable\nFROM user_tab_columns\nWHERE table_name = UPPER(:table_name)\nORDER BY column_id\n"
            params = t.ConfigMap(root={"table_name": table_name})
        return self.execute_query(sql, params).map(
            lambda rows: [
                FlextDbOracleModels.DbOracle.Column(
                    name=str(row.root.get("column_name", "")),
                    data_type=str(row.root.get("data_type", "")),
                    nullable=str(row.root.get("nullable", "Y")) == "Y",
                    primary_key=False,
                    default_value=str(row.root.get("data_default", "")),
                )
                for row in rows
            ],
        )

    def get_primary_key_columns(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> r[t.StrSequence]:
        """Alias for get_primary_keys."""
        return self.get_primary_keys(table_name, schema_name)

    def get_primary_keys(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> r[t.StrSequence]:
        """Get primary key column names for specified table."""

        def _fetch_keys() -> t.StrSequence:
            if schema:
                sql = "\n                SELECT column_name\n                FROM all_constraints c, all_cons_columns cc\n                WHERE c.constraint_type = 'P'\n                AND c.constraint_name = cc.constraint_name\n                AND c.table_name = UPPER(:table_name)\n                AND c.owner = UPPER(:schema)\n                ORDER BY cc.position\n                "
                params = t.ConfigMap(root={"table_name": table_name, "schema": schema})
            else:
                sql = "\n                SELECT column_name\n                FROM user_constraints c, user_cons_columns cc\n                WHERE c.constraint_type = 'P'\n                AND c.constraint_name = cc.constraint_name\n                AND c.table_name = UPPER(:table_name)\n                ORDER BY cc.position\n                "
                params = t.ConfigMap(root={"table_name": table_name})
            query_result = self.execute_query(sql, params)
            if query_result.is_failure:
                raise RuntimeError(query_result.error or "Query execution failed")
            return [str(row.root["column_name"]) for row in query_result.value]

        return u.try_(
            _fetch_keys,
            catch=(
                FlextDbOracleServiceBase.OracleDatabaseError,
                FlextDbOracleServiceBase.OracleInterfaceError,
                ConnectionError,
                SQLAlchemyDatabaseError,
                SQLAlchemyOperationalError,
                SQLAlchemyError,
                OSError,
                RuntimeError,
            ),
        ).map_error(lambda e: f"Failed to get primary keys: {e}")

    def get_schemas(self) -> r[t.StrSequence]:
        """Get list of Oracle schemas."""
        sql = "SELECT username as schema_name FROM all_users WHERE username NOT IN ('SYS', 'SYSTEM', 'ANONYMOUS', 'XDB', 'CTXSYS', 'MDSYS', 'WMSYS') ORDER BY username"
        return self.execute_query(sql).map(
            lambda rows: [str(row.root["schema_name"]) for row in rows],
        )

    def get_table_metadata(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> r[FlextDbOracleModels.DbOracle.TableMetadata]:
        """Get complete table metadata."""

        def _fetch_metadata() -> FlextDbOracleModels.DbOracle.TableMetadata:
            columns_result = self.get_columns(table_name, schema)
            if columns_result.is_failure:
                raise RuntimeError(columns_result.error or "Failed to get columns")

            pk_result = self.get_primary_keys(table_name, schema)
            if pk_result.is_failure:
                raise RuntimeError(pk_result.error or "Failed to get primary keys")

            return FlextDbOracleModels.DbOracle.TableMetadata(
                table_name=table_name,
                schema_name=schema or "",
                columns=[
                    FlextDbOracleModels.DbOracle.ColumnMetadata(
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
                FlextDbOracleServiceBase.OracleDatabaseError,
                FlextDbOracleServiceBase.OracleInterfaceError,
                ConnectionError,
                SQLAlchemyOperationalError,
                OSError,
                RuntimeError,
            ),
        ).map_error(lambda e: f"Failed to get table metadata: {e}")

    def get_table_row_count(
        self,
        table_name: str,
        schema_name: str | None = None,
    ) -> r[int]:
        """Get row count - simplified."""

        def _fetch_count() -> int:
            schema = f"{schema_name}." if schema_name else ""
            sql = f"SELECT COUNT(*) as count FROM {schema}{table_name}"  # nosec B608
            query_result = self.execute_query(sql)
            if query_result.is_failure:
                raise RuntimeError(query_result.error or "Query execution failed")
            return self._parse_count_from_rows(query_result.value)

        return u.try_(
            _fetch_count,
            catch=(
                FlextDbOracleServiceBase.OracleDatabaseError,
                FlextDbOracleServiceBase.OracleInterfaceError,
                ConnectionError,
                SQLAlchemyOperationalError,
                OSError,
                RuntimeError,
            ),
        ).map_error(lambda e: f"Failed to get row count: {e}")

    def get_tables(self, schema: str | None = None) -> r[t.StrSequence]:
        """Get list of tables in Oracle schema."""
        if schema:
            sql = "SELECT table_name FROM all_tables WHERE owner = UPPER(:schema_name) ORDER BY table_name"
            params: t.ConfigMap | None = t.ConfigMap(root={"schema_name": schema})
        else:
            sql = "SELECT table_name FROM user_tables ORDER BY table_name"
            params = None
        return self.execute_query(sql, params).map(
            lambda rows: [str(row.root["table_name"]) for row in rows],
        )


__all__ = ["FlextDbOracleServiceSchema"]

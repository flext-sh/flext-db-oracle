"""SQL builder service mixin for flext-db-oracle.

Provides DDL/DML statement generation: INSERT, UPDATE, DELETE,
SELECT, CREATE TABLE, DROP TABLE, CREATE INDEX.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableSequence,
    Sequence,
)

from flext_db_oracle import (
    FlextDbOracleServiceBase,
    c,
    m,
    p,
    r,
    t,
    u,
)


class FlextDbOracleServiceSqlBuilder(FlextDbOracleServiceBase):
    """Mixin providing SQL statement builders for FlextDbOracleServices.

    Handles: build_create_index_statement, build_delete_statement,
    build_insert_statement, build_select, build_update_statement,
    create_table_ddl, drop_table_ddl.
    """

    def build_create_index_statement(self, _config: t.JsonMapping) -> p.Result[str]:
        """Build Oracle CREATE INDEX statement from configuration."""
        try:
            if not isinstance(_config, Mapping):
                return r[str].fail("Invalid CREATE INDEX settings payload")
            raw_columns = _config.get("columns", [])
            columns_list: t.StrSequence = (
                [str(col) for col in raw_columns]
                if isinstance(raw_columns, list)
                else []
            )
            raw_parallel = _config.get("parallel", 1)
            parallel_value = u.to_int(
                raw_parallel if raw_parallel is not None else 1,
                default=1,
            )
            payload = {
                "table_name": str(_config.get("table_name", "")),
                "index_name": str(_config.get("index_name", "")),
                "columns": columns_list,
                "unique": bool(_config.get("unique", False)),
                "schema_name": str(_config.get("schema_name", "")),
                "tablespace": str(_config.get("tablespace", "")),
                "parallel": parallel_value,
            }
            settings = m.DbOracle.CreateIndexConfig.model_validate(
                payload,
            )
            if not settings.columns:
                return r[str].fail("Index definition requires at least one column")
            schema_prefix = f"{settings.schema_name}." if settings.schema_name else ""
            unique_prefix = "UNIQUE " if settings.unique else ""
            columns = ", ".join(settings.columns)
            sql = f"CREATE {unique_prefix}INDEX {settings.index_name} ON {schema_prefix}{settings.table_name} ({columns})"
            if settings.tablespace:
                sql = f"{sql} TABLESPACE {settings.tablespace}"
            if settings.parallel > 1:
                sql = f"{sql} PARALLEL {settings.parallel}"
            return r[str].ok(sql)
        except c.ValidationError as e:
            return r[str].fail(f"Invalid CREATE INDEX settings: {e}")

    def build_delete_statement(
        self,
        table_name: str,
        where_columns: t.StrSequence,
        schema: str | None = None,
    ) -> p.Result[str]:
        """Build DELETE statement - simplified."""
        wheres = " AND ".join(f"{col} = :{col}" for col in where_columns)
        schema_prefix = f"{schema}." if schema else ""
        sql = f"DELETE FROM {schema_prefix}{table_name} WHERE {wheres}"  # nosec B608
        return r[str].ok(sql)

    def build_insert_statement(
        self,
        table_name: str,
        columns: t.StrSequence,
        schema: str | None = None,
        returning_columns: t.StrSequence | None = None,
    ) -> p.Result[str]:
        """Build INSERT statement - simplified."""
        cols = ", ".join(columns)
        vals = ", ".join(f":{col}" for col in columns)
        schema_prefix = f"{schema}." if schema else ""
        sql = f"INSERT INTO {schema_prefix}{table_name} ({cols}) VALUES ({vals})"  # nosec B608
        if returning_columns:
            ret = ", ".join(returning_columns)
            sql += f" RETURNING {ret}"
        return r[str].ok(sql)

    def build_select(
        self,
        table_name: str,
        columns: t.StrSequence | None = None,
        conditions: m.ConfigMap | t.JsonMapping | None = None,
        schema_name: str | None = None,
    ) -> p.Result[str]:
        """Build SELECT query - simplified implementation."""
        typed_conditions = (
            conditions
            if isinstance(conditions, m.ConfigMap) or conditions is None
            else m.ConfigMap(root=dict(conditions))
        )
        cols = ", ".join(columns) if columns else "*"
        if typed_conditions and typed_conditions.root:
            where_pairs = [f"{k} = :{k}" for k in typed_conditions.root]
            where = f" WHERE {' AND '.join(where_pairs)}"
        else:
            where = ""
        schema_prefix = f"{schema_name.upper()}." if schema_name else ""
        sql = f"SELECT {cols} FROM {schema_prefix}{table_name.upper()}{where}"  # nosec B608
        return r[str].ok(sql)

    def build_update_statement(
        self,
        table_name: str,
        set_columns: t.StrSequence,
        where_columns: t.StrSequence,
        schema: str | None = None,
    ) -> p.Result[str]:
        """Build UPDATE statement - simplified."""
        sets = ", ".join(f"{col}=:{col}" for col in set_columns)
        wheres = " AND ".join(f"{col} = :{col}" for col in where_columns)
        schema_prefix = f"{schema}." if schema else ""
        sql = f"UPDATE {schema_prefix}{table_name} SET {sets} WHERE {wheres}"  # nosec B608
        return r[str].ok(sql)

    def create_table_ddl(
        self,
        table_name: str,
        columns: Sequence[m.DbOracle.Column | t.JsonMapping],
        schema: str | None = None,
    ) -> p.Result[str]:
        """Generate CREATE TABLE DDL - simplified."""
        col_defs: MutableSequence[str] = []
        primary_keys: MutableSequence[str] = []
        for col in columns:
            if isinstance(col, m.DbOracle.Column):
                name = col.name or c.IDENTIFIER_UNKNOWN
                data_type = col.data_type or "VARCHAR2(255)"
                nullable = "" if col.nullable else " NOT NULL"
                if col.primary_key:
                    primary_keys.append(name)
            else:
                name_value = col.get("name") or col.get("column_name")
                data_type_value = col.get("data_type")
                nullable_value = col.get("nullable", True)
                name = (
                    str(name_value) if name_value is not None else c.IDENTIFIER_UNKNOWN
                )
                data_type = (
                    str(data_type_value)
                    if data_type_value is not None
                    else "VARCHAR2(255)"
                )
                nullable = "" if bool(nullable_value) else " NOT NULL"
                if bool(col.get("primary_key", False)):
                    primary_keys.append(name)
            col_defs.append(f"{name} {data_type}{nullable}")
        if primary_keys:
            col_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
        schema_prefix = f"{schema}." if schema else ""
        ddl = f"CREATE TABLE {schema_prefix}{table_name} (\n  {', '.join(col_defs)}\n)"
        return r[str].ok(ddl)

    def drop_table_ddl(
        self, table_name: str, schema: str | None = None
    ) -> p.Result[str]:
        """Generate DROP TABLE DDL."""
        schema_prefix = f"{schema}." if schema else ""
        ddl = f"DROP TABLE {schema_prefix}{table_name}"
        return r[str].ok(ddl)


__all__: list[str] = ["FlextDbOracleServiceSqlBuilder"]

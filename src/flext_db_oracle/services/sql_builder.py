"""SQL builder service mixin for flext-db-oracle.

Provides DDL/DML statement generation: INSERT, UPDATE, DELETE,
SELECT, CREATE TABLE, DROP TABLE, CREATE INDEX.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from collections.abc import (
    Mapping,
    MutableSequence,
    Sequence,
)

from sqlalchemy import (
    bindparam,
    column,
    delete,
    insert,
    literal_column,
    select,
    table,
    update,
)
from sqlalchemy.dialects.oracle import dialect as oracle_dialect
from sqlalchemy.sql import quoted_name

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

    def build_create_index_statement(self, config: t.JsonMapping) -> p.Result[str]:
        """Build Oracle CREATE INDEX statement from configuration."""
        try:
            if not isinstance(config, Mapping):
                return r[str].fail("Invalid CREATE INDEX settings payload")
            raw_columns = config.get("columns", [])
            columns_list: t.StrSequence = (
                [str(col) for col in raw_columns]
                if isinstance(raw_columns, list)
                else []
            )
            raw_parallel = config.get("parallel", 1)
            parallel_value = u.to_int(
                raw_parallel if raw_parallel is not None else 1,
                default=1,
            )
            payload = {
                "table_name": str(config.get("table_name", "")),
                "index_name": str(config.get("index_name", "")),
                "columns": columns_list,
                "unique": bool(config.get("unique", False)),
                "schema_name": str(config.get("schema_name", "")),
                "tablespace": str(config.get("tablespace", "")),
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
        """Build DELETE statement through SQLAlchemy Core Oracle compilation."""
        bind_names = {
            column_name: f"bind_{index:04d}"
            for index, column_name in enumerate(where_columns)
        }
        table_clause = table(
            table_name.upper()
            if re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, table_name)
            else quoted_name(table_name, True),
            *(
                column(
                    column_name
                    if re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, column_name)
                    else quoted_name(column_name, True),
                )
                for column_name in where_columns
            ),
            schema=(
                schema.upper()
                if schema and re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, schema)
                else quoted_name(schema, True)
                if schema
                else None
            ),
        )
        statement = delete(table_clause)
        for column_name in where_columns:
            statement = statement.where(
                table_clause.c[column_name] == bindparam(bind_names[column_name]),
            )
        sql = re.sub(
            r"\s+",
            " ",
            str(statement.compile(dialect=oracle_dialect())),
        ).strip()
        for column_name, bind_name in bind_names.items():
            sql = sql.replace(f":{bind_name}", f":{column_name}")
        return r[str].ok(sql)

    def build_insert_statement(
        self,
        table_name: str,
        columns: t.StrSequence,
        schema: str | None = None,
        returning_columns: t.StrSequence | None = None,
    ) -> p.Result[str]:
        """Build INSERT statement through SQLAlchemy Core Oracle compilation."""
        statement_columns = tuple(dict.fromkeys([*columns, *(returning_columns or ())]))
        bind_names = {
            column_name: f"bind_{index:04d}"
            for index, column_name in enumerate(columns)
        }
        table_clause = table(
            table_name.upper()
            if re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, table_name)
            else quoted_name(table_name, True),
            *(
                column(
                    column_name
                    if re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, column_name)
                    else quoted_name(column_name, True),
                )
                for column_name in statement_columns
            ),
            schema=(
                schema.upper()
                if schema and re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, schema)
                else quoted_name(schema, True)
                if schema
                else None
            ),
        )
        statement = insert(table_clause).values({
            table_clause.c[column_name]: bindparam(bind_names[column_name])
            for column_name in columns
        })
        if returning_columns:
            statement = statement.returning(
                *(table_clause.c[column_name] for column_name in returning_columns),
            )
        sql = re.sub(
            r"\s+",
            " ",
            str(statement.compile(dialect=oracle_dialect())),
        ).strip()
        for column_name, bind_name in bind_names.items():
            sql = sql.replace(f":{bind_name}", f":{column_name}")
        return r[str].ok(sql)

    def build_select(
        self,
        table_name: str,
        columns: t.StrSequence | None = None,
        conditions: m.ConfigMap | t.JsonMapping | None = None,
        schema_name: str | None = None,
    ) -> p.Result[str]:
        """Build SELECT query through SQLAlchemy Core Oracle compilation."""
        typed_conditions = (
            conditions
            if isinstance(conditions, m.ConfigMap) or conditions is None
            else m.ConfigMap(root=dict(conditions))
        )
        selected_columns = list(columns) if columns else []
        condition_columns = tuple(typed_conditions.root) if typed_conditions else ()
        statement_columns = tuple(
            dict.fromkeys([*selected_columns, *condition_columns]),
        )
        bind_names = {
            column_name: f"bind_{index:04d}"
            for index, column_name in enumerate(condition_columns)
        }
        table_clause = table(
            table_name.upper()
            if re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, table_name)
            else quoted_name(table_name, True),
            *(
                column(
                    column_name
                    if re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, column_name)
                    else quoted_name(column_name, True),
                )
                for column_name in statement_columns
            ),
            schema=(
                schema_name.upper()
                if schema_name
                and re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, schema_name)
                else quoted_name(schema_name, True)
                if schema_name
                else None
            ),
        )
        selected_column_clauses = [
            table_clause.c[column_name] for column_name in selected_columns
        ]
        statement = (
            select(*selected_column_clauses)
            if selected_column_clauses
            else select(literal_column("*"))
        ).select_from(table_clause)
        for column_name in condition_columns:
            statement = statement.where(
                table_clause.c[column_name] == bindparam(bind_names[column_name]),
            )
        sql = re.sub(
            r"\s+",
            " ",
            str(statement.compile(dialect=oracle_dialect())),
        ).strip()
        for column_name, bind_name in bind_names.items():
            sql = sql.replace(f":{bind_name}", f":{column_name}")
        return r[str].ok(sql)

    def build_update_statement(
        self,
        table_name: str,
        set_columns: t.StrSequence,
        where_columns: t.StrSequence,
        schema: str | None = None,
    ) -> p.Result[str]:
        """Build UPDATE statement through SQLAlchemy Core Oracle compilation."""
        statement_columns = tuple(dict.fromkeys([*set_columns, *where_columns]))
        bind_names = {
            column_name: f"bind_{index:04d}"
            for index, column_name in enumerate(statement_columns)
        }
        table_clause = table(
            table_name.upper()
            if re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, table_name)
            else quoted_name(table_name, True),
            *(
                column(
                    column_name
                    if re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, column_name)
                    else quoted_name(column_name, True),
                )
                for column_name in statement_columns
            ),
            schema=(
                schema.upper()
                if schema and re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, schema)
                else quoted_name(schema, True)
                if schema
                else None
            ),
        )
        statement = update(table_clause).values({
            table_clause.c[column_name]: bindparam(bind_names[column_name])
            for column_name in set_columns
        })
        for column_name in where_columns:
            statement = statement.where(
                table_clause.c[column_name] == bindparam(bind_names[column_name]),
            )
        sql = re.sub(
            r"\s+",
            " ",
            str(statement.compile(dialect=oracle_dialect())),
        ).strip()
        for column_name, bind_name in bind_names.items():
            sql = sql.replace(f":{bind_name}", f":{column_name}")
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
            column_model = (
                col.model_copy(
                    update={
                        "name": col.name or c.IDENTIFIER_UNKNOWN,
                        "data_type": col.data_type or "VARCHAR2(255)",
                    }
                )
                if isinstance(col, m.DbOracle.Column)
                else m.DbOracle.Column.model_validate({
                    "name": str(
                        col.get("name")
                        or col.get("column_name")
                        or c.IDENTIFIER_UNKNOWN
                    ),
                    "data_type": str(col.get("data_type") or "VARCHAR2(255)"),
                    "nullable": bool(col.get("nullable", True)),
                    "primary_key": bool(col.get("primary_key", False)),
                    "default_value": str(col.get("default_value") or ""),
                })
            )
            column_name = (
                column_model.name
                if re.fullmatch(c.DbOracle.IDENTIFIER_PATTERN, column_model.name)
                else f'"{column_model.name}"'
            )
            if column_model.primary_key:
                primary_keys.append(column_name)
            nullable = "" if column_model.nullable else " NOT NULL"
            col_defs.append(f"{column_name} {column_model.data_type}{nullable}")
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

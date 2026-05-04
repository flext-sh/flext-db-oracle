"""SQL builder service mixin for flext-db-oracle.

Provides DDL/DML statement generation: INSERT, UPDATE, DELETE,
SELECT, CREATE TABLE, DROP TABLE, CREATE INDEX.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Mapping,
)
from typing import override

from sqlalchemy import (
    ClauseElement,
    Column as sa_Column,
    Index,
    MetaData,
    Table,
    bindparam,
    column,
    delete,
    insert,
    literal_column,
    select,
    table,
    text,
    update,
)
from sqlalchemy.dialects.oracle import dialect as oracle_dialect
from sqlalchemy.sql import quoted_name
from sqlalchemy.sql.ddl import CreateIndex, CreateTable, DropTable
from sqlalchemy.types import UserDefinedType

from flext_db_oracle import (
    FlextDbOracleServiceBase,
    c,
    m,
    p,
    r,
    t,
    u,
)


class OracleRawType(UserDefinedType[str]):
    """Preserve exact Oracle type strings in SQLAlchemy DDL."""

    def __init__(self, spec: str) -> None:
        self.spec = spec

    @override
    def get_col_spec(self, **_kw: p.AttributeProbe) -> str:
        return self.spec


class FlextDbOracleServiceSqlBuilder(FlextDbOracleServiceBase):
    """Mixin providing SQL statement builders for FlextDbOracleServices.

    Handles: build_create_index_statement, build_delete_statement,
    build_insert_statement, build_select, build_update_statement,
    create_table_ddl, drop_table_ddl.
    """

    @staticmethod
    def _normalize_identifier(name: str) -> str | quoted_name:
        if c.DbOracle.IDENTIFIER_RE.fullmatch(name):
            return quoted_name(name.upper(), quote=False)
        return quoted_name(name, quote=True)

    @staticmethod
    def _compile_statement(statement: ClauseElement) -> str:
        return c.DbOracle.collapse_whitespace(
            str(statement.compile(dialect=oracle_dialect())),
        ).strip()

    @classmethod
    def _compile_statement_with_binds(
        cls,
        statement: ClauseElement,
        bind_names: dict[str, str],
    ) -> str:
        sql = cls._compile_statement(statement)
        for column_name, bind_name in bind_names.items():
            sql = sql.replace(f":{bind_name}", f":{column_name}")
        return sql

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
            table_name = self._normalize_identifier(settings.table_name)
            schema_name = (
                self._normalize_identifier(settings.schema_name)
                if settings.schema_name
                else None
            )
            metadata = MetaData()
            table_object = Table(
                table_name,
                metadata,
                *(
                    sa_Column(
                        self._normalize_identifier(column_name),
                        OracleRawType("VARCHAR2(1)"),
                    )
                    for column_name in settings.columns
                ),
                schema=schema_name,
            )
            index = Index(
                self._normalize_identifier(settings.index_name),
                *(
                    table_object.c[self._normalize_identifier(column_name)]
                    for column_name in settings.columns
                ),
                unique=settings.unique,
            )
            sql = self._compile_statement(CreateIndex(index))
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
            if c.DbOracle.IDENTIFIER_RE.fullmatch(table_name)
            else quoted_name(table_name, True),
            *(
                column(
                    column_name
                    if c.DbOracle.IDENTIFIER_RE.fullmatch(column_name)
                    else quoted_name(column_name, True),
                )
                for column_name in where_columns
            ),
            schema=(
                schema.upper()
                if schema and c.DbOracle.IDENTIFIER_RE.fullmatch(schema)
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
        sql = c.DbOracle.collapse_whitespace(
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
            if c.DbOracle.IDENTIFIER_RE.fullmatch(table_name)
            else quoted_name(table_name, True),
            *(
                column(
                    column_name
                    if c.DbOracle.IDENTIFIER_RE.fullmatch(column_name)
                    else quoted_name(column_name, True),
                )
                for column_name in statement_columns
            ),
            schema=(
                schema.upper()
                if schema and c.DbOracle.IDENTIFIER_RE.fullmatch(schema)
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
        sql = c.DbOracle.collapse_whitespace(
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
            if c.DbOracle.IDENTIFIER_RE.fullmatch(table_name)
            else quoted_name(table_name, True),
            *(
                column(
                    column_name
                    if c.DbOracle.IDENTIFIER_RE.fullmatch(column_name)
                    else quoted_name(column_name, True),
                )
                for column_name in statement_columns
            ),
            schema=(
                schema_name.upper()
                if schema_name
                and c.DbOracle.IDENTIFIER_RE.fullmatch(schema_name)
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
        sql = c.DbOracle.collapse_whitespace(
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
            if c.DbOracle.IDENTIFIER_RE.fullmatch(table_name)
            else quoted_name(table_name, True),
            *(
                column(
                    column_name
                    if c.DbOracle.IDENTIFIER_RE.fullmatch(column_name)
                    else quoted_name(column_name, True),
                )
                for column_name in statement_columns
            ),
            schema=(
                schema.upper()
                if schema and c.DbOracle.IDENTIFIER_RE.fullmatch(schema)
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
        sql = c.DbOracle.collapse_whitespace(
            str(statement.compile(dialect=oracle_dialect())),
        ).strip()
        for column_name, bind_name in bind_names.items():
            sql = sql.replace(f":{bind_name}", f":{column_name}")
        return r[str].ok(sql)

    def create_table_ddl(
        self,
        table_name: str,
        columns: t.SequenceOf[m.DbOracle.Column | t.JsonMapping],
        schema: str | None = None,
    ) -> p.Result[str]:
        """Generate CREATE TABLE DDL through SQLAlchemy Oracle DDL compilation."""
        try:
            column_models: list[m.DbOracle.Column] = []
            for col in columns:
                if isinstance(col, m.DbOracle.Column):
                    column_model = col.model_copy(
                        update={
                            "name": col.name or c.IDENTIFIER_UNKNOWN,
                            "data_type": col.data_type or "VARCHAR2(255)",
                        }
                    )
                else:
                    column_model = m.DbOracle.Column.model_validate({
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
                column_models.append(column_model)
            normalized_table_name = self._normalize_identifier(table_name)
            normalized_schema_name = (
                self._normalize_identifier(schema) if schema else None
            )
            metadata = MetaData()
            table_object = Table(
                normalized_table_name,
                metadata,
                *(
                    sa_Column(
                        self._normalize_identifier(column_model.name),
                        OracleRawType(column_model.data_type),
                        nullable=column_model.nullable,
                        primary_key=column_model.primary_key,
                        server_default=(
                            text(column_model.default_value)
                            if column_model.default_value
                            else None
                        ),
                    )
                    for column_model in column_models
                ),
                schema=normalized_schema_name,
            )
            ddl = self._compile_statement(CreateTable(table_object))
            return r[str].ok(ddl)
        except c.ValidationError as e:
            return r[str].fail(f"Invalid CREATE TABLE settings: {e}")

    def drop_table_ddl(
        self, table_name: str, schema: str | None = None
    ) -> p.Result[str]:
        """Generate DROP TABLE DDL through SQLAlchemy Oracle DDL compilation."""
        normalized_table_name = self._normalize_identifier(table_name)
        normalized_schema_name = self._normalize_identifier(schema) if schema else None
        metadata = MetaData()
        table_object = Table(
            normalized_table_name,
            metadata,
            schema=normalized_schema_name,
        )
        ddl = self._compile_statement(DropTable(table_object))
        return r[str].ok(ddl)


__all__: list[str] = ["FlextDbOracleServiceSqlBuilder"]

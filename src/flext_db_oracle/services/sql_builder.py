"""SQL builder service mixin for flext-db-oracle.

Provides DDL/DML statement generation: INSERT, UPDATE, DELETE,
SELECT, CREATE TABLE, DROP TABLE, CREATE INDEX.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

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
)


class FlextDbOracleServiceSqlBuilder(FlextDbOracleServiceBase):
    """Mixin providing SQL statement builders for FlextDbOracleServices.

    Handles: build_create_index_statement, build_delete_statement,
    build_insert_statement, build_select, build_update_statement,
    create_table_ddl, drop_table_ddl.
    """

    class OracleRawType(UserDefinedType[str]):
        """Preserve exact Oracle type strings in SQLAlchemy DDL."""

        def __init__(self, spec: str) -> None:
            """Store the raw Oracle type specification."""
            self.spec = spec

        @override
        def get_col_spec(self, **_kw: p.AttributeProbe) -> str:
            return self.spec

    @staticmethod
    def _normalize_identifier(name: str) -> str | quoted_name:
        if c.DbOracle.IDENTIFIER_RE.fullmatch(name):
            return quoted_name(name.upper(), quote=False)
        return quoted_name(name, quote=True)

    @staticmethod
    def _compile_statement(statement: ClauseElement) -> str:
        compiled: str = c.DbOracle.collapse_whitespace(
            str(statement.compile(dialect=oracle_dialect())),
        ).strip()
        return compiled

    @classmethod
    def _compile_statement_with_binds(
        cls,
        statement: ClauseElement,
        bind_names: t.MappingKV[str, str],
    ) -> str:
        sql = cls._compile_statement(statement)
        for column_name, bind_name in bind_names.items():
            sql = sql.replace(f":{bind_name}", f":{column_name}")
        return sql

    def build_create_index_statement(self, config: t.JsonMapping) -> p.Result[str]:
        """Build Oracle CREATE INDEX statement from configuration."""
        try:
            if not config:
                return r[str].fail("Invalid CREATE INDEX settings payload")
            settings = m.DbOracle.CreateIndexConfig.model_validate(config)
            return self._create_index_sql(settings)
        except c.ValidationError as e:
            return r[str].fail(f"Invalid CREATE INDEX settings: {e}")

    def _create_index_sql(
        self,
        settings: m.DbOracle.CreateIndexConfig,
    ) -> p.Result[str]:
        """Compile CREATE INDEX SQL from validated settings."""
        if not settings.columns:
            return r[str].fail("Index definition requires at least one column")
        table_object = self._create_index_table(settings)
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

    def _create_index_table(
        self,
        settings: m.DbOracle.CreateIndexConfig,
    ) -> Table:
        """Build a SQLAlchemy table object for CREATE INDEX compilation."""
        table_name = self._normalize_identifier(settings.table_name)
        schema_name = (
            self._normalize_identifier(settings.schema_name)
            if settings.schema_name
            else None
        )
        metadata = MetaData()
        return Table(
            table_name,
            metadata,
            *(
                sa_Column(
                    self._normalize_identifier(column_name),
                    self.OracleRawType("VARCHAR2(1)"),
                )
                for column_name in settings.columns
            ),
            schema=schema_name,
        )

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
            else m.ConfigMap.model_validate(conditions)
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
                if schema_name and c.DbOracle.IDENTIFIER_RE.fullmatch(schema_name)
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
            column_models = self._normalize_table_columns(columns)
            table_object = self._create_table_object(table_name, column_models, schema)
            ddl = self._compile_statement(CreateTable(table_object))
            return r[str].ok(ddl)
        except c.ValidationError as e:
            return r[str].fail(f"Invalid CREATE TABLE settings: {e}")

    def _normalize_table_columns(
        self,
        columns: t.SequenceOf[m.DbOracle.Column | t.JsonMapping],
    ) -> t.SequenceOf[m.DbOracle.Column]:
        """Normalize raw column payloads into Column models."""
        return tuple(self._normalize_table_column(column) for column in columns)

    def _normalize_table_column(
        self,
        column: m.DbOracle.Column | t.JsonMapping,
    ) -> m.DbOracle.Column:
        """Normalize one raw column payload into a Column model."""
        if isinstance(column, m.DbOracle.Column):
            copied: m.DbOracle.Column = column.model_copy(
                update={
                    "name": column.name or c.IDENTIFIER_UNKNOWN,
                    "data_type": column.data_type or "VARCHAR2(255)",
                },
            )
            return copied
        normalized: m.DbOracle.Column = m.DbOracle.Column.model_validate({
            "name": str(
                column.get("name") or column.get("column_name") or c.IDENTIFIER_UNKNOWN,
            ),
            "data_type": str(column.get("data_type") or "VARCHAR2(255)"),
            "nullable": bool(column.get("nullable", True)),
            "primary_key": bool(column.get("primary_key", False)),
            "default_value": str(column.get("default_value") or ""),
        })
        return normalized

    def _create_table_object(
        self,
        table_name: str,
        column_models: t.SequenceOf[m.DbOracle.Column],
        schema: str | None,
    ) -> Table:
        """Build a SQLAlchemy table object for CREATE TABLE compilation."""
        normalized_table_name = self._normalize_identifier(table_name)
        normalized_schema_name = self._normalize_identifier(schema) if schema else None
        metadata = MetaData()
        return Table(
            normalized_table_name,
            metadata,
            *(
                sa_Column(
                    self._normalize_identifier(column_model.name),
                    self.OracleRawType(column_model.data_type),
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

    def drop_table_ddl(
        self,
        table_name: str,
        schema: str | None = None,
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

"""Oracle Database query, schema and metrics protocol contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Sequence

    from flext_db_oracle import m, p, t


class FlextDbOracleProtocolsQuery:
    """Oracle Database query protocol contracts composed into ``p.DbOracle``."""

    @runtime_checkable
    class QueryExecutor(Protocol):
        """Protocol for Oracle query execution operations."""

        def execute_many(
            self,
            sql: str,
            params_list: t.SequenceOf[t.JsonMapping],
        ) -> p.Result[int]:
            """Execute Oracle SQL statement with multiple parameter sets.

            Args:
            sql: SQL statement string
            params_list: List of parameter dictionaries

            Returns:
            r[int]: Number of affected rows

            """
            ...

        def execute_query(
            self,
            sql: str,
            params: t.JsonMapping | None = None,
        ) -> p.Result[Sequence[m.Dict]]:
            """Execute Oracle SQL query.

            Args:
            sql: SQL query string
            params: Query parameters

            Returns:
            r: Query result or error

            """
            ...

        def execute_statement(
            self,
            sql: str,
            params: t.JsonMapping | None = None,
        ) -> p.Result[bool]:
            """Execute Oracle SQL statement.

            Args:
            sql: SQL statement string
            params: Statement parameters

            Returns:
            r[bool]: Execution success status

            """
            ...

        def fetch_one(
            self,
            sql: str,
            params: t.JsonMapping | None = None,
        ) -> p.Result[m.Dict | None]:
            """Fetch single result from Oracle query.

            Args:
            sql: SQL query string
            params: Query parameters

            Returns:
            r[m.Dict | None]: Single result or None

            """
            ...

    @runtime_checkable
    class SchemaIntrospector(Protocol):
        """Protocol for Oracle schema introspection operations."""

        def fetch_columns(
            self,
            table: str,
            schema: str | None = None,
        ) -> p.Result[Sequence[m.DbOracle.Column]]:
            """Get column information for Oracle table.

            Args:
            table: Table name
            schema: Schema name (optional)

            Returns:
            r[Sequence[t.JsonMapping]]: Column metadata or error

            """
            ...

        def fetch_primary_keys(
            self,
            table: str,
            schema: str | None = None,
        ) -> p.Result[t.StrSequence]:
            """Get primary key columns for Oracle table.

            Args:
            table: Table name
            schema: Schema name (optional)

            Returns:
            r[t.StrSequence]: Primary key column names or error

            """
            ...

        def fetch_schemas(self) -> p.Result[t.StrSequence]:
            """Get list of Oracle schemas.

            Returns:
            r[t.StrSequence]: Schema names or error

            """
            ...

        def fetch_table_metadata(
            self,
            table: str,
            schema: str | None = None,
        ) -> p.Result[m.DbOracle.TableMetadata]:
            """Get Oracle table metadata.

            Args:
            table: Table name
            schema: Schema name (optional)

            Returns:
            r[t.JsonMapping]: Table metadata or error

            """
            ...

        def fetch_tables(
            self,
            schema: str | None = None,
        ) -> p.Result[t.StrSequence]:
            """Get list of tables in Oracle schema.

            Args:
            schema: Schema name (optional)

            Returns:
            r[t.StrSequence]: Table names or error

            """
            ...

    @runtime_checkable
    class SqlBuilder(Protocol):
        """Protocol for Oracle SQL statement building operations."""

        def build_delete_statement(
            self,
            table_name: str,
            where_columns: t.StrSequence,
            schema: str | None = None,
        ) -> p.Result[str]:
            """Build Oracle DELETE statement.

            Args:
                table_name: Table name.
                where_columns: Binding columns for the WHERE clause.
                schema: Optional schema name.

            Returns:
                The compiled DELETE statement or a typed failure.

            """
            ...

        def build_insert_statement(
            self,
            table_name: str,
            columns: t.StrSequence,
            schema: str | None = None,
            returning_columns: t.StrSequence | None = None,
        ) -> p.Result[str]:
            """Build Oracle INSERT statement.

            Args:
                table_name: Table name.
                columns: Columns to insert.
                schema: Optional schema name.
                returning_columns: Optional RETURNING columns.

            Returns:
                The compiled INSERT statement or a typed failure.

            """
            ...

        def build_select(
            self,
            table_name: str,
            columns: t.StrSequence | None = None,
            conditions: m.ConfigMap | t.JsonMapping | None = None,
            schema_name: str | None = None,
        ) -> p.Result[str]:
            """Build Oracle SELECT statement.

            Args:
                table_name: Table name.
                columns: Columns to project.
                conditions: Optional equality conditions.
                schema_name: Optional schema name.

            Returns:
                The compiled SELECT statement or a typed failure.

            """
            ...

        def build_update_statement(
            self,
            table_name: str,
            set_columns: t.StrSequence,
            where_columns: t.StrSequence,
            schema: str | None = None,
        ) -> p.Result[str]:
            """Build Oracle UPDATE statement.

            Args:
                table_name: Table name.
                set_columns: Columns to assign.
                where_columns: Binding columns for the WHERE clause.
                schema: Optional schema name.

            Returns:
                The compiled UPDATE statement or a typed failure.

            """
            ...

    @runtime_checkable
    class DdlGenerator(Protocol):
        """Protocol for Oracle DDL generation operations."""

        def build_create_index_statement(
            self,
            table: str,
            columns: t.StrSequence,
            index_name: str | None = None,
            *,
            unique: bool = False,
        ) -> p.Result[str]:
            """Build Oracle CREATE INDEX statement.

            Args:
            table: Table name
            columns: Index columns
            index_name: Index name (optional)
            unique: Create unique index

            Returns:
            r[str]: CREATE INDEX statement or error

            """
            ...

        def create_table_ddl(
            self,
            table: str,
            columns: t.SequenceOf[m.DbOracle.Column],
            schema: str | None = None,
        ) -> p.Result[str]:
            """Generate Oracle CREATE TABLE DDL.

            Args:
            table: Table name
            columns: Column definitions
            schema: Schema name (optional)

            Returns:
            r[str]: CREATE TABLE DDL or error

            """
            ...

        def drop_table_ddl(
            self,
            table: str,
            schema: str | None = None,
        ) -> p.Result[str]:
            """Generate Oracle DROP TABLE DDL.

            Args:
            table: Table name
            schema: Schema name (optional)

            Returns:
            r[str]: DROP TABLE DDL or error

            """
            ...

    @runtime_checkable
    class MetricsCollector(Protocol):
        """Protocol for Oracle database metrics collection."""

        def fetch_metrics(self) -> p.Result[m.DbOracle.HealthStatus]:
            """Get collected Oracle metrics.

            Returns:
            r[t.JsonMapping]: Metrics data or error

            """
            ...

        def record_metric(
            self,
            name: str,
            value: float,
            tags: t.StrMapping | None = None,
        ) -> p.Result[bool]:
            """Record Oracle database metric.

            Args:
            name: Metric name
            value: Metric value
            tags: Metric tags (optional)

            Returns:
            r[bool]: Success status

            """
            ...

        def track_operation(
            self,
            operation: str,
            duration: float,
            *,
            success: bool,
        ) -> p.Result[bool]:
            """Track Oracle operation performance.

            Args:
            operation: Operation name
            duration: Operation duration
            success: Operation success status

            Returns:
            r[bool]: Tracking success status

            """
            ...


__all__: list[str] = ["FlextDbOracleProtocolsQuery"]

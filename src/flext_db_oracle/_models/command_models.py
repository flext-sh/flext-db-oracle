"""Oracle Database dispatcher command models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import m

from flext_db_oracle import t


class FlextDbOracleModelsCommand:
    """Oracle Database command models composed into ``m.DbOracle``."""

    class ConnectCommand(m.Entity):
        """Command to establish Oracle connection."""

    class DisconnectCommand(m.Entity):
        """Command to close Oracle connection."""

    class TestConnectionCommand(m.Entity):
        """Command to test Oracle connection."""

    class ExecuteQueryCommand(m.Entity):
        """Command to execute SELECT query."""

        sql: str = m.Field(description="SQL SELECT query to execute")
        parameters: t.JsonMapping | None = m.Field(
            default=None,
            description="Query bind parameters",
            validate_default=True,
        )

    class FetchOneCommand(m.Entity):
        """Command to fetch single row."""

        sql: str = m.Field(description="SQL query to fetch a single row")
        parameters: t.JsonMapping | None = m.Field(
            default=None,
            description="Query bind parameters",
            validate_default=True,
        )

    class ExecuteStatementCommand(m.Entity):
        """Command to execute INSERT/UPDATE/DELETE."""

        sql: str = m.Field(description="SQL DML statement to execute")
        parameters: t.JsonMapping | None = m.Field(
            default=None,
            description="Statement bind parameters",
            validate_default=True,
        )

    class ExecuteManyCommand(m.Entity):
        """Command to execute batch statements."""

        sql: str = m.Field(description="SQL statement for batch execution")
        parameters_list: t.SequenceOf[t.JsonMapping] = m.Field(
            default_factory=tuple[t.JsonMapping, ...],
            description="List of parameter sets for batch execution",
        )

    class GetSchemasCommand(m.Entity):
        """Command to retrieve all schemas."""

    class GetTablesCommand(m.Entity):
        """Command to retrieve tables in schema."""

        schema_name: str | None = m.Field(
            default=None,
            description="Schema to list tables from",
            validate_default=True,
        )

    class GetColumnsCommand(m.Entity):
        """Command to retrieve columns in table."""

        table: str = m.Field(description="Table to retrieve columns from")
        schema_name: str | None = m.Field(
            default=None,
            description="Schema containing the table",
            validate_default=True,
        )


__all__: list[str] = ["FlextDbOracleModelsCommand"]

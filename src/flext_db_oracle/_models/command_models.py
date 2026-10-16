"""Oracle Database dispatcher command models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCliModels
from flext_core import u as core_u

from flext_db_oracle import t


class ConnectCommand(FlextCliModels.Entity):
    """Command to establish Oracle connection."""


class DisconnectCommand(FlextCliModels.Entity):
    """Command to close Oracle connection."""


class TestConnectionCommand(FlextCliModels.Entity):
    """Command to test Oracle connection."""


class ExecuteQueryCommand(FlextCliModels.Entity):
    """Command to execute SELECT query."""

    sql: str = core_u.Field(description="SQL SELECT query to execute")
    parameters: t.JsonMapping | None = core_u.Field(
        None,
        description="Query bind parameters",
        validate_default=True,
    )


class FetchOneCommand(FlextCliModels.Entity):
    """Command to fetch single row."""

    sql: str = core_u.Field(description="SQL query to fetch a single row")
    parameters: t.JsonMapping | None = core_u.Field(
        None,
        description="Query bind parameters",
        validate_default=True,
    )


class ExecuteStatementCommand(FlextCliModels.Entity):
    """Command to execute INSERT/UPDATE/DELETE."""

    sql: str = core_u.Field(description="SQL DML statement to execute")
    parameters: t.JsonMapping | None = core_u.Field(
        None,
        description="Statement bind parameters",
        validate_default=True,
    )


class ExecuteManyCommand(FlextCliModels.Entity):
    """Command to execute batch statements."""

    sql: str = core_u.Field(description="SQL statement for batch execution")
    parameters_list: t.SequenceOf[t.JsonMapping] = core_u.Field(
        default_factory=tuple[t.JsonMapping, ...],
        description="List of parameter sets for batch execution",
    )


class GetSchemasCommand(FlextCliModels.Entity):
    """Command to retrieve all schemas."""


class GetTablesCommand(FlextCliModels.Entity):
    """Command to retrieve tables in schema."""

    schema_name: str | None = core_u.Field(
        None,
        description="Schema to list tables from",
        validate_default=True,
    )


class GetColumnsCommand(FlextCliModels.Entity):
    """Command to retrieve columns in table."""

    table: str = core_u.Field(description="Table to retrieve columns from")
    schema_name: str | None = core_u.Field(
        None,
        description="Schema containing the table",
        validate_default=True,
    )


__all__: list[str] = [
    "ConnectCommand",
    "DisconnectCommand",
    "ExecuteManyCommand",
    "ExecuteQueryCommand",
    "ExecuteStatementCommand",
    "FetchOneCommand",
    "GetColumnsCommand",
    "GetSchemasCommand",
    "GetTablesCommand",
    "TestConnectionCommand",
]

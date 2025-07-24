"""Database utility functions for FLEXT DB Oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Shared database utility functions to eliminate code duplication.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import FlextResult as ServiceResult

from flext_db_oracle.logging_utils import get_logger

if TYPE_CHECKING:
    from flext_db_oracle.application.services import FlextDbOracleQueryService

logger = get_logger(__name__)


async def flext_db_oracle_get_primary_key_columns(
    query_service: FlextDbOracleQueryService,
    table_name: str,
    schema_name: str | None = None,
) -> ServiceResult[Any]:
    """Get primary key columns for a table.

    Args:
        query_service: FlextDbOracle query service for executing queries
        table_name: Name of the table
        schema_name: Name of the schema (optional)

    Returns:
        ServiceResult containing list of primary key column names

    """
    try:
        if schema_name:
            # Query with schema name (for comparator)
            query = """
                SELECT column_name
                FROM all_cons_columns
                WHERE owner = :schema_name
                AND table_name = :table_name
                AND constraint_name = (
                    SELECT constraint_name
                    FROM all_constraints
                    WHERE owner = :schema_name
                    AND table_name = :table_name
                    AND constraint_type = 'P'
                )
                ORDER BY position
            """
            params = {
                "schema_name": schema_name.upper(),
                "table_name": table_name.upper(),
            }
        else:
            # Query without schema name (for synchronizer)
            query = """
                SELECT column_name
                FROM all_cons_columns
                WHERE constraint_name = (
                    SELECT constraint_name
                    FROM all_constraints
                    WHERE table_name = :table_name
                    AND constraint_type = 'P'
                )
                ORDER BY position
            """
            params = {"table_name": table_name.upper()}

        result = await query_service.execute_query(query, params)

        if not result.success:
            return ServiceResult.fail(
                result.error or "Failed to get primary key columns",
            )

        if not result.data or not result.data.rows:
            if schema_name:
                # Comparator expects error when no PK found
                return ServiceResult.fail(
                    f"No primary key found for table {schema_name}.{table_name}",
                )
            # Synchronizer expects empty list when no PK found
            return ServiceResult.ok([])

        pk_columns = [row[0] for row in result.data.rows]

        if not pk_columns and schema_name:
            return ServiceResult.fail(
                f"No primary key columns found for table {schema_name}.{table_name}",
            )

        return ServiceResult.ok(pk_columns)

    except Exception as e:
        logger.exception("Failed to get primary key columns")
        return ServiceResult(
            success=True,
            error=f"Failed to get primary key columns: {e}",
        )

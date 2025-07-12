"""Oracle database schema analysis functionality.

Built on flext-core foundation for comprehensive schema analysis.
Uses flext-db-oracle domain models for consistency.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import ServiceResult

from flext_observability.logging import get_logger


if TYPE_CHECKING:
    from flext_db_oracle.application.services import OracleConnectionService

logger = get_logger(__name__)


class SchemaAnalyzer:
    """Analyzes Oracle database schemas using flext-core patterns."""

    def __init__(self, connection_service: OracleConnectionService) -> None:
        self.connection_service = connection_service

    async def analyze_schema(self, schema_name: str | None = None) -> ServiceResult[dict[str, Any]]:
        """Analyze Oracle schema and return comprehensive metadata."""
        try:
            if schema_name is None:
                schema_result = await self._get_current_schema()
                if schema_result.is_failure:
                    return schema_result
                schema_name = schema_result.value

            logger.info("Analyzing Oracle schema: %s", schema_name)

            # Analyze schema components
            tables_result = await self.get_tables(schema_name)
            views_result = await self.get_views(schema_name)
            sequences_result = await self.get_sequences(schema_name)
            procedures_result = await self.get_procedures(schema_name)

            if any(result.is_failure for result in [tables_result, views_result, sequences_result, procedures_result]):
                return ServiceResult.failure("Failed to analyze schema components")

            schema_analysis = {
                "schema_name": schema_name,
                "tables": tables_result.value,
                "views": views_result.value,
                "sequences": sequences_result.value,
                "procedures": procedures_result.value,
                "total_objects": (
                    len(tables_result.value) +
                    len(views_result.value) +
                    len(sequences_result.value) +
                    len(procedures_result.value)
                ),
            }

            logger.info("Schema analysis complete: %d total objects", schema_analysis["total_objects"])
            return ServiceResult.success(schema_analysis)

        except Exception as e:
            logger.exception("Schema analysis failed: %s", e)
            return ServiceResult.failure(f"Schema analysis failed: {e}")

    async def get_tables(self, schema_name: str) -> ServiceResult[list[dict[str, Any]]]:
        """Get all tables in the specified schema."""
        try:
            query = """
                SELECT table_name, tablespace_name, status, num_rows, blocks, avg_row_len
                FROM all_tables
                WHERE owner = :schema_name
                ORDER BY table_name
            """

            result = await self.connection_service.execute_query(
                query,
                {"schema_name": schema_name.upper()},
            )

            if result.is_failure:
                return result

            tables = [{
                    "name": row[0],
                    "tablespace": row[1],
                    "status": row[2],
                    "num_rows": row[3],
                    "blocks": row[4],
                    "avg_row_len": row[5],
                } for row in result.value.rows]

            logger.info("Found %d tables in schema %s", len(tables), schema_name)
            return ServiceResult.success(tables)

        except Exception as e:
            logger.exception("Failed to get tables: %s", e)
            return ServiceResult.failure(f"Failed to get tables: {e}")

    async def get_views(self, schema_name: str) -> ServiceResult[list[dict[str, Any]]]:
        """Get all views in the specified schema."""
        try:
            query = """
                SELECT view_name, text_length, type_text
                FROM all_views
                WHERE owner = :schema_name
                ORDER BY view_name
            """

            result = await self.connection_service.execute_query(
                query,
                {"schema_name": schema_name.upper()},
            )

            if result.is_failure:
                return result

            views = [{
                    "name": row[0],
                    "text_length": row[1],
                    "type_text": row[2],
                } for row in result.value.rows]

            logger.info("Found %d views in schema %s", len(views), schema_name)
            return ServiceResult.success(views)

        except Exception as e:
            logger.exception("Failed to get views: %s", e)
            return ServiceResult.failure(f"Failed to get views: {e}")

    async def get_sequences(self, schema_name: str) -> ServiceResult[list[dict[str, Any]]]:
        """Get all sequences in the specified schema."""
        try:
            query = """
                SELECT sequence_name, min_value, max_value, increment_by, cycle_flag
                FROM all_sequences
                WHERE sequence_owner = :schema_name
                ORDER BY sequence_name
            """

            result = await self.connection_service.execute_query(
                query,
                {"schema_name": schema_name.upper()},
            )

            if result.is_failure:
                return result

            sequences = [{
                    "name": row[0],
                    "min_value": row[1],
                    "max_value": row[2],
                    "increment_by": row[3],
                    "cycle_flag": row[4],
                } for row in result.value.rows]

            logger.info("Found %d sequences in schema %s", len(sequences), schema_name)
            return ServiceResult.success(sequences)

        except Exception as e:
            logger.exception("Failed to get sequences: %s", e)
            return ServiceResult.failure(f"Failed to get sequences: {e}")

    async def get_procedures(self, schema_name: str) -> ServiceResult[list[dict[str, Any]]]:
        """Get all procedures and functions in the specified schema."""
        try:
            query = """
                SELECT object_name, object_type, status, created, last_ddl_time
                FROM all_objects
                WHERE owner = :schema_name
                AND object_type IN ('PROCEDURE', 'FUNCTION', 'PACKAGE')
                ORDER BY object_type, object_name
            """

            result = await self.connection_service.execute_query(
                query,
                {"schema_name": schema_name.upper()},
            )

            if result.is_failure:
                return result

            procedures = [{
                    "name": row[0],
                    "type": row[1],
                    "status": row[2],
                    "created": row[3],
                    "last_ddl_time": row[4],
                } for row in result.value.rows]

            logger.info("Found %d procedures/functions in schema %s", len(procedures), schema_name)
            return ServiceResult.success(procedures)

        except Exception as e:
            logger.exception("Failed to get procedures: %s", e)
            return ServiceResult.failure(f"Failed to get procedures: {e}")

    async def get_table_columns(self, schema_name: str, table_name: str) -> ServiceResult[list[dict[str, Any]]]:
        """Get column information for a specific table."""
        try:
            query = """
                SELECT column_name, data_type, data_length, data_precision, data_scale,
                       nullable, column_id, default_value
                FROM all_tab_columns
                WHERE owner = :schema_name
                AND table_name = :table_name
                ORDER BY column_id
            """

            result = await self.connection_service.execute_query(
                query,
                {
                    "schema_name": schema_name.upper(),
                    "table_name": table_name.upper(),
                },
            )

            if result.is_failure:
                return result

            columns = [{
                    "name": row[0],
                    "data_type": row[1],
                    "data_length": row[2],
                    "data_precision": row[3],
                    "data_scale": row[4],
                    "nullable": row[5] == "Y",
                    "column_id": row[6],
                    "default_value": row[7],
                } for row in result.value.rows]

            logger.info("Found %d columns for table %s.%s", len(columns), schema_name, table_name)
            return ServiceResult.success(columns)

        except Exception as e:
            logger.exception("Failed to get table columns: %s", e)
            return ServiceResult.failure(f"Failed to get table columns: {e}")

    async def _get_current_schema(self) -> ServiceResult[str]:
        """Get the current schema name."""
        try:
            result = await self.connection_service.execute_query("SELECT USER FROM DUAL")

            if result.is_failure:
                return result

            if not result.value.rows:
                return ServiceResult.failure("No current schema found")

            schema_name = result.value.rows[0][0]
            return ServiceResult.success(schema_name)

        except Exception as e:
            logger.exception("Failed to get current schema: %s", e)
            return ServiceResult.failure(f"Failed to get current schema: {e}")

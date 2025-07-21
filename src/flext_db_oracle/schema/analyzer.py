"""Oracle database schema analysis functionality.

Built on flext-core foundation for comprehensive schema analysis.
Uses flext-infrastructure.databases.flext-db-oracle domain models for consistency.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import ServiceResult
from flext_observability.logging import get_logger

from flext_db_oracle.schema.metadata import (
    ColumnMetadata,
    ConstraintMetadata,
    ConstraintType,
    IndexMetadata,
    ObjectStatus,
    SchemaMetadata,
    TableMetadata,
    ViewMetadata,
)

if TYPE_CHECKING:
    from flext_db_oracle.application.services import OracleConnectionService

logger = get_logger(__name__)


class SchemaAnalyzer:
    """Analyzes Oracle database schemas using flext-core patterns."""

    def __init__(self, connection_service: OracleConnectionService) -> None:
        """Initialize the schema analyzer.

        Args:
            connection_service: Oracle connection service for database operations

        """
        self.connection_service = connection_service

    async def analyze_schema(
        self,
        schema_name: str | None = None,
    ) -> ServiceResult[dict[str, Any]]:
        """Analyze Oracle schema and return comprehensive metadata."""
        try:
            if schema_name is None:
                schema_result = await self._get_current_schema()
                if not schema_result.is_success:
                    return ServiceResult.fail(
                        schema_result.error or "Failed to get current schema",
                    )
                schema_name = schema_result.data
                if not schema_name:
                    return ServiceResult.fail("Empty schema name returned")

            logger.info("Analyzing Oracle schema: %s", schema_name)

            # Analyze schema components
            tables_result = await self.get_tables(schema_name)
            views_result = await self.get_views(schema_name)
            sequences_result = await self.get_sequences(schema_name)
            procedures_result = await self.get_procedures(schema_name)

            if any(
                not result.is_success
                for result in [
                    tables_result,
                    views_result,
                    sequences_result,
                    procedures_result,
                ]
            ):
                return ServiceResult.fail("Failed to analyze schema components")

            schema_analysis = {
                "schema_name": schema_name,
                "tables": tables_result.data,
                "views": views_result.data,
                "sequences": sequences_result.data,
                "procedures": procedures_result.data,
                "total_objects": (
                    len(tables_result.data or [])
                    + len(views_result.data or [])
                    + len(sequences_result.data or [])
                    + len(procedures_result.data or [])
                ),
            }

            logger.info(
                "Schema analysis complete: %d total objects",
                schema_analysis["total_objects"],
            )
            return ServiceResult.ok(schema_analysis)

        except Exception as e:
            logger.exception("Schema analysis failed")
            return ServiceResult.fail(f"Schema analysis failed: {e}")

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

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to execute query")

            if not result.data:
                return ServiceResult.fail("Query result is empty")

            tables = [
                {
                    "name": row[0],
                    "tablespace": row[1],
                    "status": row[2],
                    "num_rows": row[3],
                    "blocks": row[4],
                    "avg_row_len": row[5],
                }
                for row in result.data.rows
            ]

            logger.info("Found %d tables in schema %s", len(tables), schema_name)
            return ServiceResult.ok(tables)

        except Exception as e:
            logger.exception("Failed to get tables")
            return ServiceResult.fail(f"Failed to get tables: {e}")

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

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to execute query")

            if not result.data:
                return ServiceResult.fail("Query result is empty")

            views = [
                {
                    "name": row[0],
                    "text_length": row[1],
                    "type_text": row[2],
                }
                for row in result.data.rows
            ]

            logger.info("Found %d views in schema %s", len(views), schema_name)
            return ServiceResult.ok(views)

        except Exception as e:
            logger.exception("Failed to get views")
            return ServiceResult.fail(f"Failed to get views: {e}")

    async def get_sequences(
        self,
        schema_name: str,
    ) -> ServiceResult[list[dict[str, Any]]]:
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

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to execute query")

            if not result.data:
                return ServiceResult.fail("Query result is empty")

            sequences = [
                {
                    "name": row[0],
                    "min_value": row[1],
                    "max_value": row[2],
                    "increment_by": row[3],
                    "cycle_flag": row[4],
                }
                for row in result.data.rows
            ]

            logger.info("Found %d sequences in schema %s", len(sequences), schema_name)
            return ServiceResult.ok(sequences)

        except Exception as e:
            logger.exception("Failed to get sequences")
            return ServiceResult.fail(f"Failed to get sequences: {e}")

    async def get_procedures(
        self,
        schema_name: str,
    ) -> ServiceResult[list[dict[str, Any]]]:
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

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to execute query")

            if not result.data:
                return ServiceResult.fail("Query result is empty")

            procedures = [
                {
                    "name": row[0],
                    "type": row[1],
                    "status": row[2],
                    "created": row[3],
                    "last_ddl_time": row[4],
                }
                for row in result.data.rows
            ]

            logger.info(
                "Found %d procedures/functions in schema %s",
                len(procedures),
                schema_name,
            )
            return ServiceResult.ok(procedures)

        except Exception as e:
            logger.exception("Failed to get procedures")
            return ServiceResult.fail(f"Failed to get procedures: {e}")

    async def get_table_columns(
        self,
        schema_name: str,
        table_name: str,
    ) -> ServiceResult[list[dict[str, Any]]]:
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

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to execute query")

            if not result.data:
                return ServiceResult.fail("Query result is empty")

            columns = [
                {
                    "name": row[0],
                    "data_type": row[1],
                    "data_length": row[2],
                    "data_precision": row[3],
                    "data_scale": row[4],
                    "nullable": row[5] == "Y",
                    "column_id": row[6],
                    "default_value": row[7],
                }
                for row in result.data.rows
            ]

            logger.info(
                "Found %d columns for table %s.%s",
                len(columns),
                schema_name,
                table_name,
            )
            return ServiceResult.ok(columns)

        except Exception as e:
            logger.exception("Failed to get table columns")
            return ServiceResult.fail(f"Failed to get table columns: {e}")

    async def _get_current_schema(self) -> ServiceResult[str]:
        """Get the current schema name."""
        try:
            result = await self.connection_service.execute_query(
                "SELECT USER FROM DUAL",
            )

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to execute query")

            if not result.data or not result.data.rows:
                return ServiceResult.fail("No current schema found")

            schema_name = result.data.rows[0][0]
            return ServiceResult.ok(schema_name)

        except Exception as e:
            logger.exception("Failed to get current schema")
            return ServiceResult.fail(f"Failed to get current schema: {e}")

    async def get_table_constraints(
        self,
        schema_name: str,
        table_name: str,
    ) -> ServiceResult[list[dict[str, Any]]]:
        """Get all constraints for a specific table."""
        try:
            query = """
                SELECT constraint_name, constraint_type, search_condition,
                       r_constraint_name, delete_rule, status
                FROM all_constraints
                WHERE owner = :schema_name
                AND table_name = :table_name
                ORDER BY constraint_type, constraint_name
            """

            result = await self.connection_service.execute_query(
                query,
                {
                    "schema_name": schema_name.upper(),
                    "table_name": table_name.upper(),
                },
            )

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to execute query")

            if not result.data:
                return ServiceResult.fail("Query result is empty")

            constraints = [
                {
                    "name": row[0],
                    "type": row[1],
                    "search_condition": row[2],
                    "r_constraint_name": row[3],
                    "delete_rule": row[4],
                    "status": row[5],
                }
                for row in result.data.rows
            ]

            logger.info(
                "Found %d constraints for table %s.%s",
                len(constraints),
                schema_name,
                table_name,
            )
            return ServiceResult.ok(constraints)

        except Exception as e:
            logger.exception("Failed to get table constraints")
            return ServiceResult.fail(f"Failed to get table constraints: {e}")

    async def get_table_indexes(
        self,
        schema_name: str,
        table_name: str,
    ) -> ServiceResult[list[dict[str, Any]]]:
        """Get all indexes for a specific table."""
        try:
            query = """
                SELECT index_name, index_type, uniqueness, compression,
                       status, num_rows, leaf_blocks, distinct_keys
                FROM all_indexes
                WHERE table_owner = :schema_name
                AND table_name = :table_name
                ORDER BY index_name
            """

            result = await self.connection_service.execute_query(
                query,
                {
                    "schema_name": schema_name.upper(),
                    "table_name": table_name.upper(),
                },
            )

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to execute query")

            if not result.data:
                return ServiceResult.fail("Query result is empty")

            indexes = [
                {
                    "name": row[0],
                    "type": row[1],
                    "uniqueness": row[2],
                    "compression": row[3],
                    "status": row[4],
                    "num_rows": row[5],
                    "leaf_blocks": row[6],
                    "distinct_keys": row[7],
                }
                for row in result.data.rows
            ]

            logger.info(
                "Found %d indexes for table %s.%s",
                len(indexes),
                schema_name,
                table_name,
            )
            return ServiceResult.ok(indexes)

        except Exception as e:
            logger.exception("Failed to get table indexes")
            return ServiceResult.fail(f"Failed to get table indexes: {e}")

    async def get_detailed_table_info(
        self,
        schema_name: str,
        table_name: str,
    ) -> ServiceResult[dict[str, Any]]:
        """Get comprehensive information about a specific table."""
        try:
            # Get basic table info
            tables_result = await self.get_tables(schema_name)
            if not tables_result.is_success:
                return ServiceResult.fail(
                    tables_result.error or "Failed to get table list",
                )

            if not tables_result.data:
                return ServiceResult.fail("Table list is empty")

            table_info = next(
                (
                    t
                    for t in tables_result.data
                    if t["name"].upper() == table_name.upper()
                ),
                None,
            )

            if not table_info:
                return ServiceResult.fail(
                    f"Table {schema_name}.{table_name} not found",
                )

            # Get detailed information
            columns_result = await self.get_table_columns(schema_name, table_name)
            constraints_result = await self.get_table_constraints(
                schema_name,
                table_name,
            )
            indexes_result = await self.get_table_indexes(schema_name, table_name)

            if any(
                not result.is_success
                for result in [columns_result, constraints_result, indexes_result]
            ):
                return ServiceResult.fail("Failed to get detailed table information")

            detailed_info = {
                **table_info,
                "columns": columns_result.data,
                "constraints": constraints_result.data,
                "indexes": indexes_result.data,
                "column_count": len(columns_result.data or []),
                "constraint_count": len(constraints_result.data or []),
                "index_count": len(indexes_result.data or []),
            }

            logger.info(
                "Retrieved detailed info for table %s.%s",
                schema_name,
                table_name,
            )
            return ServiceResult.ok(detailed_info)

        except Exception as e:
            logger.exception("Failed to get detailed table info")
            return ServiceResult.fail(f"Failed to get detailed table info: {e}")

    async def analyze_schema_size(
        self,
        schema_name: str,
    ) -> ServiceResult[dict[str, Any]]:
        """Analyze total size and space usage of schema."""
        try:
            query = """
                SELECT
                    SUM(bytes) / 1024 / 1024 as total_mb,
                    COUNT(*) as segment_count,
                    segment_type
                FROM dba_segments
                WHERE owner = :schema_name
                GROUP BY segment_type
                ORDER BY total_mb DESC
            """

            result = await self.connection_service.execute_query(
                query,
                {"schema_name": schema_name.upper()},
            )

            if not result.is_success:
                # Fallback to user_segments if dba_segments not accessible
                fallback_query = """
                    SELECT
                        SUM(bytes) / 1024 / 1024 as total_mb,
                        COUNT(*) as segment_count,
                        segment_type
                    FROM user_segments
                    GROUP BY segment_type
                    ORDER BY total_mb DESC
                """

                fallback_result = await self.connection_service.execute_query(
                    fallback_query,
                )
                if not fallback_result.is_success:
                    return ServiceResult.fail(
                        fallback_result.error
                        or "Failed to analyze schema size (fallback)",
                    )
                result = fallback_result

            if not result.data:
                return ServiceResult.fail("Schema size analysis result is empty")

            size_analysis = {
                "schema_name": schema_name,
                "segments": [
                    {
                        "type": row[2],
                        "total_mb": float(row[0]) if row[0] else 0.0,
                        "count": row[1],
                    }
                    for row in result.data.rows
                ],
                "total_size_mb": sum(
                    float(row[0]) if row[0] else 0.0 for row in result.data.rows
                ),
                "total_segments": sum(row[1] for row in result.data.rows),
            }

            logger.info(
                "Schema %s total size: %.2f MB",
                schema_name,
                size_analysis["total_size_mb"],
            )
            return ServiceResult.ok(size_analysis)

        except Exception as e:
            logger.exception("Failed to analyze schema size")
            return ServiceResult.fail(f"Failed to analyze schema size: {e}")

    async def get_complete_schema_metadata(
        self,
        schema_name: str | None = None,
    ) -> ServiceResult[SchemaMetadata]:
        """Get complete schema metadata using domain models."""
        try:
            if schema_name is None:
                schema_result = await self._get_current_schema()
                if not schema_result.is_success:
                    return ServiceResult.fail(
                        schema_result.error or "Failed to get current schema",
                    )
                schema_name = schema_result.data
                if not schema_name:
                    return ServiceResult.fail("Empty schema name returned")

            logger.info("Getting complete schema metadata for: %s", schema_name)

            # Get basic schema analysis
            analysis_result = await self.analyze_schema(schema_name)
            if not analysis_result.is_success:
                return ServiceResult.fail(
                    analysis_result.error or "Failed to analyze schema",
                )

            analysis = analysis_result.data
            if not analysis:
                return ServiceResult.fail("Schema analysis returned no data")

            # Convert to domain models
            table_metadata_list = []
            tables = analysis.get("tables", [])
            for table_data in tables:
                # Get detailed table information
                table_detail_result = await self.get_detailed_table_info(
                    schema_name,
                    table_data["name"],
                )
                if not table_detail_result.is_success:
                    continue

                table_detail = table_detail_result.data
                if not table_detail:
                    continue

                # Create column metadata
                columns = [
                    ColumnMetadata(
                        name=col["name"],
                        data_type=col["data_type"],
                        nullable=col["nullable"],
                        default_value=col["default_value"],
                        max_length=col["data_length"],
                        precision=col["data_precision"],
                        scale=col["data_scale"],
                        column_id=col["column_id"],
                        foreign_key_table=None,
                        foreign_key_column=None,
                        comments=None,
                    )
                    for col in table_detail.get("columns", [])
                ]

                # Create constraint metadata
                constraints = []
                for const in table_detail.get("constraints", []):
                    constraint_type_map = {
                        "P": ConstraintType.PRIMARY_KEY,
                        "R": ConstraintType.FOREIGN_KEY,
                        "U": ConstraintType.UNIQUE,
                        "C": ConstraintType.CHECK,
                    }

                    constraint = ConstraintMetadata(
                        name=const["name"],
                        constraint_type=constraint_type_map.get(
                            const["type"],
                            ConstraintType.CHECK,
                        ),
                        table_name=table_data["name"],
                        column_names=[],  # Would need additional query to get columns
                        referenced_table=None,
                        check_condition=const["search_condition"],
                        status=(
                            ObjectStatus.ENABLED
                            if const["status"] == "ENABLED"
                            else ObjectStatus.DISABLED
                        ),
                    )
                    constraints.append(constraint)

                # Create index metadata
                indexes = [
                    IndexMetadata(
                        name=idx["name"],
                        table_name=table_data["name"],
                        column_names=[],  # Would need additional query to get columns
                        is_unique=idx["uniqueness"] == "UNIQUE",
                        index_type=idx["type"],
                        tablespace_name=None,
                        degree=1,
                        status=(
                            ObjectStatus.VALID
                            if idx["status"] == "VALID"
                            else ObjectStatus.INVALID
                        ),
                        compression=idx["compression"],
                    )
                    for idx in table_detail.get("indexes", [])
                ]

                # Create table metadata
                table_metadata = TableMetadata(
                    name=table_data["name"],
                    schema_name=schema_name,
                    tablespace_name=table_data["tablespace"],
                    status=(
                        ObjectStatus.VALID
                        if table_data["status"] == "VALID"
                        else ObjectStatus.INVALID
                    ),
                    num_rows=table_data["num_rows"],
                    blocks=table_data["blocks"],
                    avg_row_len=table_data["avg_row_len"],
                    compression=None,
                    degree=1,
                    columns=columns,
                    constraints=constraints,
                    indexes=indexes,
                    created=None,
                    last_ddl_time=None,
                    last_analyzed=None,
                )

                table_metadata_list.append(table_metadata)

            # Create view metadata
            view_metadata_list = [
                ViewMetadata(
                    name=view["name"],
                    schema_name=schema_name,
                    text_length=view["text_length"] or 0,
                    text=view.get("type_text"),
                    status=ObjectStatus.VALID,
                    created=None,
                    last_ddl_time=None,
                )
                for view in analysis.get("views", [])
            ]

            # Get schema size analysis
            size_result = await self.analyze_schema_size(schema_name)
            total_size_mb = 0.0
            if size_result.is_success and size_result.data:
                total_size_mb = size_result.data.get("total_size_mb", 0.0)

            # Create complete schema metadata
            schema_metadata = SchemaMetadata(
                name=schema_name,
                default_tablespace=None,
                temporary_tablespace=None,
                status=ObjectStatus.VALID,
                tables=table_metadata_list,
                views=view_metadata_list,
                sequences=analysis["sequences"],
                procedures=analysis["procedures"],
                total_objects=analysis["total_objects"],
                total_size_mb=total_size_mb,
            )

            logger.info(
                "Complete schema metadata created for %s: %d tables, %d views",
                schema_name,
                len(table_metadata_list),
                len(view_metadata_list),
            )

            return ServiceResult.ok(schema_metadata)

        except Exception as e:
            logger.exception("Failed to get complete schema metadata")
            return ServiceResult.fail(f"Failed to get complete schema metadata: {e}")

    async def get_constraint_columns(
        self,
        schema_name: str,
        constraint_name: str,
    ) -> ServiceResult[list[str]]:
        """Get column names for a specific constraint."""
        try:
            query = """
                SELECT column_name
                FROM all_cons_columns
                WHERE owner = :schema_name
                AND constraint_name = :constraint_name
                ORDER BY position
            """

            result = await self.connection_service.execute_query(
                query,
                {
                    "schema_name": schema_name.upper(),
                    "constraint_name": constraint_name.upper(),
                },
            )

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to execute query")

            if not result.data:
                return ServiceResult.fail("Query result is empty")

            columns = [row[0] for row in result.data.rows]
            return ServiceResult.ok(columns)

        except Exception as e:
            logger.exception("Failed to get constraint columns")
            return ServiceResult.fail(f"Failed to get constraint columns: {e}")

    async def get_index_columns(
        self,
        schema_name: str,
        index_name: str,
    ) -> ServiceResult[list[str]]:
        """Get column names for a specific index."""
        try:
            query = """
                SELECT column_name
                FROM all_ind_columns
                WHERE index_owner = :schema_name
                AND index_name = :index_name
                ORDER BY column_position
            """

            result = await self.connection_service.execute_query(
                query,
                {
                    "schema_name": schema_name.upper(),
                    "index_name": index_name.upper(),
                },
            )

            if not result.is_success:
                return ServiceResult.fail(result.error or "Failed to execute query")

            if not result.data:
                return ServiceResult.fail("Query result is empty")

            columns = [row[0] for row in result.data.rows]
            return ServiceResult.ok(columns)

        except Exception as e:
            logger.exception("Failed to get index columns")
            return ServiceResult.fail(f"Failed to get index columns: {e}")

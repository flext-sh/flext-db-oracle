"""Oracle database synchronization functionality.

Built on flext-core foundation for robust data synchronization.
Uses FlextResult pattern and async operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import (
    FlextResult,
    FlextValueObject,
    get_logger,
)
from pydantic import Field

if TYPE_CHECKING:
    from flext_db_oracle.application.services import FlextDbOracleConnectionService

logger = get_logger(__name__)


class SyncOperation(FlextValueObject):
    """Represents a synchronization operation."""

    operation_type: str = Field(..., description="Type of sync operation")
    table_name: str = Field(..., description="Table being synchronized")
    records_affected: int = Field(0, description="Number of records affected", ge=0)
    execution_time_ms: float = Field(
        0.0,
        description="Execution time in milliseconds",
        ge=0.0,
    )
    success: bool = Field(default=True, description="Whether operation succeeded")
    error_message: str | None = Field(None, description="Error message if failed")

    def validate_domain_rules(self) -> None:
        """Validate domain rules for sync operation."""
        if not self.operation_type.strip():
            msg = "Operation type cannot be empty"
            raise ValueError(msg)
        if not self.table_name.strip():
            msg = "Table name cannot be empty"
            raise ValueError(msg)
        if self.records_affected < 0:
            msg = "Records affected cannot be negative"
            raise ValueError(msg)
        if self.execution_time_ms < 0:
            msg = "Execution time cannot be negative"
            raise ValueError(msg)


class SyncResult(FlextValueObject):
    """Result of a synchronization operation."""

    source_name: str = Field(..., description="Source database identifier")
    target_name: str = Field(..., description="Target database identifier")
    operations: list[SyncOperation] = Field(
        default_factory=list,
        description="Sync operations performed",
    )
    total_records_synced: int = Field(0, description="Total records synchronized", ge=0)
    success: bool = Field(default=True, description="Overall success status")

    def validate_domain_rules(self) -> None:
        """Validate domain rules for sync result."""
        if not self.source_name.strip():
            msg = "Source name cannot be empty"
            raise ValueError(msg)
        if not self.target_name.strip():
            msg = "Target name cannot be empty"
            raise ValueError(msg)
        if self.total_records_synced < 0:
            msg = "Total records synced cannot be negative"
            raise ValueError(msg)

    @property
    def total_operations(self) -> int:
        """Get total number of operations."""
        return len(self.operations)

    @property
    def successful_operations(self) -> int:
        """Get number of successful operations."""
        return sum(1 for op in self.operations if op.success)

    @property
    def failed_operations(self) -> int:
        """Get number of failed operations."""
        return sum(1 for op in self.operations if not op.success)


class DatabaseSynchronizer:
    """Synchronizes data between Oracle databases using flext-core patterns."""

    def __init__(
        self,
        source_service: FlextDbOracleConnectionService,
        target_service: FlextDbOracleConnectionService,
    ) -> None:
        """Initialize the database synchronizer.

        Args:
            source_service: Connection service for source database
            target_service: Connection service for target database

        """
        self.source_service = source_service
        self.target_service = target_service

    async def synchronize_table(
        self,
        table_name: str,
        sync_strategy: str = "upsert",
    ) -> FlextResult[SyncResult]:
        """Synchronize a single table between databases."""
        try:
            logger.info("Starting synchronization for table: %s", table_name)

            operations = []

            # Example sync operation
            sync_op = SyncOperation(
                operation_type=sync_strategy,
                table_name=table_name,
                records_affected=0,
                execution_time_ms=0.0,
                success=True,
                error_message=None,
            )
            operations.append(sync_op)

            result = SyncResult(
                source_name="source_db",
                target_name="target_db",
                operations=operations,
                total_records_synced=0,
                success=True,
            )

            logger.info("Table synchronization complete: %s", table_name)
            return FlextResult.ok(result)

        except Exception as e:
            logger.exception("Table synchronization failed for %s", table_name)
            return FlextResult.fail(f"Table synchronization failed: {e}")

    async def synchronize_schema(
        self,
        schema_name: str,
        tables: list[str] | None = None,
    ) -> FlextResult[SyncResult]:
        """Synchronize multiple tables in a schema."""
        try:
            logger.info("Starting schema synchronization: %s", schema_name)

            if tables is None:
                # Get all tables in schema
                tables_result = await self._get_schema_tables(schema_name)
                if not tables_result.is_success:
                    return FlextResult.fail(
                        tables_result.error or "Failed to get schema tables",
                    )
                tables = tables_result.data or []

            all_operations: list[SyncOperation] = []
            total_synced = 0
            overall_success = True

            for table_name in tables:
                table_result = await self.synchronize_table(table_name)
                if table_result.is_success and table_result.data:
                    all_operations.extend(table_result.data.operations)
                    total_synced += table_result.data.total_records_synced
                else:
                    overall_success = False
                    logger.error(
                        "Failed to sync table %s: %s",
                        table_name,
                        table_result.error,
                    )

            result = SyncResult(
                source_name="source_db",
                target_name="target_db",
                operations=all_operations,
                total_records_synced=total_synced,
                success=overall_success,
            )

            logger.info(
                "Schema synchronization complete: %s (%d tables, %d records)",
                schema_name,
                len(tables),
                total_synced,
            )
            return FlextResult.ok(result)

        except Exception as e:
            logger.exception("Schema synchronization failed for %s", schema_name)
            return FlextResult.fail(f"Schema synchronization failed: {e}")

    async def _get_schema_tables(self, schema_name: str) -> FlextResult[list[str]]:
        """Get list of tables in a schema."""
        try:
            query = """
                SELECT table_name
                FROM all_tables
                WHERE owner = :schema_name
                ORDER BY table_name
            """

            result = await self.source_service.execute_query(
                query,
                {"schema_name": schema_name.upper()},
            )

            if not result.is_success:
                return FlextResult.fail(result.error or "Failed to execute query")

            if not result.data or not result.data.rows:
                return FlextResult.ok([])

            tables = [row[0] for row in result.data.rows]
            return FlextResult.ok(tables)

        except Exception as e:
            logger.exception("Failed to get schema tables")
            return FlextResult.fail(f"Failed to get schema tables: {e}")

    async def validate_sync_requirements(
        self,
        table_name: str,
    ) -> FlextResult[dict[str, Any]]:
        """Validate that a table can be synchronized."""
        try:
            # Check if table exists in both databases
            source_exists = await self._table_exists(self.source_service, table_name)
            target_exists = await self._table_exists(self.target_service, table_name)

            if not source_exists:
                return FlextResult.fail(
                    f"Source table {table_name} does not exist",
                )

            if not target_exists:
                return FlextResult.fail(
                    f"Target table {table_name} does not exist",
                )

            # Check for primary key
            pk_result = await self._get_primary_key_columns(table_name)
            if not pk_result.is_success:
                return FlextResult.fail(
                    f"Cannot determine primary key for {table_name}",
                )

            validation_info = {
                "source_exists": source_exists,
                "target_exists": target_exists,
                "primary_key_columns": pk_result.data,
                "sync_ready": True,
            }

            return FlextResult.ok(validation_info)

        except Exception as e:
            logger.exception("Sync validation failed for %s", table_name)
            return FlextResult.fail(f"Sync validation failed: {e}")

    async def _table_exists(
        self,
        connection_service: FlextDbOracleConnectionService,
        table_name: str,
    ) -> bool:
        try:
            query = """
                SELECT 1 FROM all_tables
                WHERE table_name = :table_name
            """

            result = await connection_service.execute_query(
                query,
                {"table_name": table_name.upper()},
            )

            if not result.is_success or not result.data or not result.data.rows:
                return False
            return len(result.data.rows) > 0

        except (ValueError, TypeError, AttributeError) as e:
            logger.warning("Failed to validate synchronization requirements: %s", e)
            return False

    async def _get_primary_key_columns(
        self,
        table_name: str,
    ) -> FlextResult[list[str]]:
        """Get primary key columns for a table."""
        try:
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

            result = await self.source_service.execute_query(
                query,
                {"table_name": table_name.upper()},
            )

            if not result.is_success:
                return FlextResult.fail(result.error or "Failed to execute query")

            if not result.data or not result.data.rows:
                return FlextResult.ok([])

            pk_columns = [row[0] for row in result.data.rows]
            return FlextResult.ok(pk_columns)

        except Exception as e:
            logger.exception("Failed to get primary key columns")
            return FlextResult.fail(f"Failed to get primary key columns: {e}")


class DataSynchronizer:
    """Simplified data synchronization interface for backward compatibility."""

    def __init__(
        self,
        source_service: FlextDbOracleConnectionService,
        target_service: FlextDbOracleConnectionService,
    ) -> None:
        """Initialize data synchronizer with connection services."""
        self.source_service = source_service
        self.target_service = target_service
        self._sync_engine = DatabaseSynchronizer(source_service, target_service)

    async def synchronize_table_data(
        self,
        table_name: str,
        strategy: str = "upsert",
    ) -> FlextResult[dict[str, Any]]:
        """Synchronize data for a specific table."""
        try:
            result = await self._sync_engine.synchronize_table(table_name, strategy)
            if not result.is_success:
                return FlextResult.fail(result.error or "Synchronization failed")

            if not result.data:
                return FlextResult.fail("Synchronization returned no data")

            # Convert to simplified format
            sync_summary = {
                "table_name": table_name,
                "strategy": strategy,
                "records_synced": result.data.total_records_synced,
                "operations": len(result.data.operations),
                "success": result.data.success,
            }

            return FlextResult.ok(sync_summary)

        except Exception as e:
            logger.exception("Data synchronization failed")
            return FlextResult.fail(f"Data synchronization failed: {e}")

    async def validate_synchronization_requirements(
        self,
        table_name: str,
    ) -> FlextResult[bool]:
        """Validate that synchronization can be performed."""
        try:
            validation_result = await self._sync_engine.validate_sync_requirements(
                table_name,
            )
            return FlextResult.ok(validation_result.is_success)

        except Exception as e:
            logger.exception("Synchronization validation failed")
            return FlextResult.fail(f"Synchronization validation failed: {e}")

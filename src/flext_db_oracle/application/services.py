"""Oracle Database Application Services.

Following flext-core application layer patterns with ServiceResult for error handling.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import TYPE_CHECKING, Any

import oracledb

from flext_core import ServiceResult

from flext_observability.logging import get_logger

from flext_db_oracle.domain.models import (
    OracleColumnInfo,
    OracleConnectionStatus,
    OracleQueryResult,
    OracleSchemaInfo,
    OracleTableMetadata,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from flext_db_oracle.config import OracleConfig

logger = get_logger(__name__)


class OracleConnectionService:
    """Service for managing Oracle database connections."""

    def __init__(self, config: OracleConfig) -> None:
        self.config = config
        self._pool: oracledb.ConnectionPool | None = None

    async def initialize_pool(self) -> ServiceResult[None]:
        """Initialize the connection pool."""
        try:
            # Build DSN with protocol support
            protocol = getattr(self.config, "protocol", "tcp")

            if protocol == "tcps":
                # For TCPS, build custom DSN string with SSL options
                service_or_sid = f"SERVICE_NAME={self.config.service_name}" if self.config.service_name else f"SID={self.config.sid}"
                dsn = f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)(HOST={self.config.host})(PORT={self.config.port}))(CONNECT_DATA=({service_or_sid})))"
            else:
                # For TCP, use standard makedsn
                dsn_params = {
                    "host": self.config.host,
                    "port": self.config.port,
                }
                if self.config.service_name:
                    dsn_params["service_name"] = self.config.service_name
                elif self.config.sid:
                    dsn_params["sid"] = self.config.sid

                dsn = oracledb.makedsn(**dsn_params)

            # Create connection parameters
            conn_params = {
                "user": self.config.username,
                "password": self.config.password,
                "dsn": dsn,
                "min": self.config.pool_min_size,
                "max": self.config.pool_max_size,
                "increment": self.config.pool_increment,
            }

            # For TCPS/Autonomous DB, disable SSL verification
            if protocol == "tcps":
                # Disable SSL server DN check
                conn_params["ssl_server_dn_match"] = False
                conn_params["ssl_server_cert_dn"] = None

            self._pool = oracledb.create_pool(**conn_params)
            logger.info(f"Oracle connection pool initialized: {self.config.connection_string}")
            return ServiceResult.success(None)

        except Exception as e:
            logger.exception(f"Failed to initialize Oracle connection pool: {e}")
            return ServiceResult.failure(f"Connection pool initialization failed: {e}")

    async def close_pool(self) -> ServiceResult[None]:
        """Close the connection pool."""
        try:
            if self._pool:
                self._pool.close()
                self._pool = None
                logger.info("Oracle connection pool closed")
            return ServiceResult.success(None)

        except Exception as e:
            logger.exception(f"Failed to close Oracle connection pool: {e}")
            return ServiceResult.failure(f"Connection pool closure failed: {e}")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[oracledb.AsyncConnection]:
        """Get a connection from the pool."""
        if not self._pool:
            init_result = await self.initialize_pool()
            if not init_result.is_success:
                msg = f"Failed to initialize connection pool: {init_result.error}"
                raise RuntimeError(msg)

        connection = None
        try:
            connection = self._pool.acquire()
            yield connection
        finally:
            if connection:
                self._pool.release(connection)

    async def test_connection(self) -> ServiceResult[OracleConnectionStatus]:
        """Test the database connection."""
        try:
            async with self.get_connection() as conn:
                # Simple test query
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM DUAL")
                    result = cursor.fetchone()

                    if result and result[0] == 1:
                        status = OracleConnectionStatus(
                            is_connected=True,
                            host=self.config.host,
                            port=self.config.port,
                            database=self.config.database_identifier,
                            username=self.config.username,
                            last_check=datetime.now(),
                        )
                        return ServiceResult.success(status)
                    status = OracleConnectionStatus(
                        is_connected=False,
                        host=self.config.host,
                        port=self.config.port,
                        database=self.config.database_identifier,
                        username=self.config.username,
                        last_check=datetime.now(),
                        error_message="Test query returned unexpected result",
                    )
                    return ServiceResult.failure("Connection test failed", status)

        except Exception as e:
            logger.exception(f"Oracle connection test failed: {e}")
            status = OracleConnectionStatus(
                is_connected=False,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database_identifier,
                username=self.config.username,
                last_check=datetime.now(),
                error_message=str(e),
            )
            return ServiceResult.failure(f"Connection test failed: {e}", status)


class OracleQueryService:
    """Service for executing Oracle database queries."""

    def __init__(self, connection_service: OracleConnectionService) -> None:
        self.connection_service = connection_service

    async def execute_query(self, sql: str, parameters: dict[str, Any] | None = None) -> ServiceResult[OracleQueryResult]:
        """Execute a SELECT query and return results."""
        start_time = datetime.now()

        try:
            async with self.connection_service.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, parameters or {})
                    rows = cursor.fetchall()

                    # Get column names
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []

                    # Convert rows to list of dictionaries
                    result_rows = [dict(zip(columns, row, strict=False)) for row in rows]

                    execution_time = (datetime.now() - start_time).total_seconds() * 1000

                    result = OracleQueryResult(
                        rows=result_rows,
                        row_count=len(result_rows),
                        columns=columns,
                        execution_time_ms=execution_time,
                    )

                    logger.info(f"Query executed successfully: {len(result_rows)} rows, {execution_time:.2f}ms")
                    return ServiceResult.success(result)

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.exception(f"Query execution failed after {execution_time:.2f}ms: {e}")
            return ServiceResult.failure(f"Query execution failed: {e}")

    async def execute_scalar(self, sql: str, parameters: dict[str, Any] | None = None) -> ServiceResult[Any]:
        """Execute a query and return a single scalar value."""
        try:
            result = await self.execute_query(sql, parameters)
            if result.is_success and result.value.row_count > 0:
                first_row = result.value.rows[0]
                first_value = next(iter(first_row.values())) if first_row else None
                return ServiceResult.success(first_value)
            return ServiceResult.success(None)

        except Exception as e:
            logger.exception(f"Scalar query execution failed: {e}")
            return ServiceResult.failure(f"Scalar query failed: {e}")


class OracleSchemaService:
    """Service for Oracle schema operations."""

    def __init__(self, query_service: OracleQueryService) -> None:
        self.query_service = query_service

    async def get_schema_info(self, schema_name: str) -> ServiceResult[OracleSchemaInfo]:
        """Get comprehensive schema information."""
        try:
            # Get schema tables
            tables_result = await self.get_schema_tables(schema_name)
            if not tables_result.is_success:
                return ServiceResult.failure(f"Failed to get schema tables: {tables_result.error}")

            schema_info = OracleSchemaInfo(
                name=schema_name,
                tables=tables_result.value,
                table_count=len(tables_result.value),
                created_date=datetime.now(),  # Would need actual query for real creation date
            )

            return ServiceResult.success(schema_info)

        except Exception as e:
            logger.exception(f"Failed to get schema info for {schema_name}: {e}")
            return ServiceResult.failure(f"Schema info retrieval failed: {e}")

    async def get_schema_tables(self, schema_name: str) -> ServiceResult[list[OracleTableMetadata]]:
        """Get all tables in a schema."""
        sql = """
        SELECT table_name, tablespace_name, num_rows
        FROM all_tables
        WHERE owner = UPPER(:schema_name)
        ORDER BY table_name
        """

        try:
            result = await self.query_service.execute_query(sql, {"schema_name": schema_name})
            if not result.is_success:
                return ServiceResult.failure(f"Failed to query schema tables: {result.error}")

            tables = []
            for row in result.value.rows:
                table_meta = OracleTableMetadata(
                    schema_name=schema_name,
                    table_name=row["TABLE_NAME"],
                    row_count=row.get("NUM_ROWS"),
                    tablespace=row.get("TABLESPACE_NAME"),
                )

                # Get column information for each table
                columns_result = await self.get_table_columns(schema_name, row["TABLE_NAME"])
                if columns_result.is_success:
                    table_meta.columns = columns_result.value

                tables.append(table_meta)

            return ServiceResult.success(tables)

        except Exception as e:
            logger.exception(f"Failed to get tables for schema {schema_name}: {e}")
            return ServiceResult.failure(f"Schema tables retrieval failed: {e}")

    async def get_table_columns(self, schema_name: str, table_name: str) -> ServiceResult[list[OracleColumnInfo]]:
        """Get column information for a specific table."""
        sql = """
        SELECT
            column_name,
            data_type,
            nullable,
            data_default,
            data_length,
            data_precision,
            data_scale
        FROM all_tab_columns
        WHERE owner = UPPER(:schema_name)
        AND table_name = UPPER(:table_name)
        ORDER BY column_id
        """

        try:
            result = await self.query_service.execute_query(sql, {
                "schema_name": schema_name,
                "table_name": table_name,
            })

            if not result.is_success:
                return ServiceResult.failure(f"Failed to query table columns: {result.error}")

            columns = []
            for row in result.value.rows:
                column_info = OracleColumnInfo(
                    name=row["COLUMN_NAME"],
                    data_type=row["DATA_TYPE"],
                    nullable=row["NULLABLE"] == "Y",
                    default_value=row.get("DATA_DEFAULT"),
                    max_length=row.get("DATA_LENGTH"),
                    precision=row.get("DATA_PRECISION"),
                    scale=row.get("DATA_SCALE"),
                )
                columns.append(column_info)

            return ServiceResult.success(columns)

        except Exception as e:
            logger.exception(f"Failed to get columns for {schema_name}.{table_name}: {e}")
            return ServiceResult.failure(f"Table columns retrieval failed: {e}")

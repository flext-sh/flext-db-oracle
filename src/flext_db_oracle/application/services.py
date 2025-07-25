"""Oracle Database Application Services.

Following flext-core application layer patterns with FlextResult for error handling.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import oracledb
from flext_core import FlextResult, get_logger

from flext_db_oracle.domain.models import (
    FlextDbOracleColumnInfo,
    FlextDbOracleConnectionStatus,
    FlextDbOracleQueryResult,
    FlextDbOracleSchemaInfo,
    FlextDbOracleTableMetadata,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from flext_db_oracle.config import FlextDbOracleConfig

logger = get_logger(__name__)


class FlextDbOracleConnectionService:
    """Service for managing Oracle database connections."""

    def __init__(self, config: FlextDbOracleConfig) -> None:
        """Initialize the Oracle connection service.

        Args:
            config: FlextDbOracle database configuration

        """
        self.config = config
        self._pool: oracledb.ConnectionPool | None = None
        self._query_service: FlextDbOracleQueryService | None = None

    async def initialize_pool(self) -> FlextResult[Any]:
        """Initialize the connection pool."""
        try:
            # Build DSN with protocol support
            protocol = getattr(self.config, "protocol", "tcp")

            if protocol == "tcps":
                # For TCPS, build custom DSN string with SSL options
                service_or_sid = (
                    f"SERVICE_NAME={self.config.service_name}"
                    if self.config.service_name
                    else f"SID={self.config.sid}"
                )
                dsn = (
                    f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)"
                    f"(HOST={self.config.host})(PORT={self.config.port}))"
                    f"(CONNECT_DATA=({service_or_sid})))"
                )
            # For TCP, use standard makedsn
            elif self.config.service_name:
                dsn = oracledb.makedsn(
                    host=self.config.host,
                    port=self.config.port,
                    service_name=self.config.service_name,
                )
            elif self.config.sid:
                dsn = oracledb.makedsn(
                    host=self.config.host,
                    port=self.config.port,
                    sid=self.config.sid,
                )
            else:
                dsn = oracledb.makedsn(
                    host=self.config.host,
                    port=self.config.port,
                )

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
            # Initialize query service after pool is ready
            self._query_service = FlextDbOracleQueryService(self)
            logger.info(
                "Oracle connection pool initialized: %s",
                self.config.connection_string,
            )
            return FlextResult.ok(None)

        except Exception as e:
            logger.exception("Failed to initialize Oracle connection pool")
            return FlextResult.fail(f"Connection pool initialization failed: {e}")

    async def close_pool(self) -> FlextResult[Any]:
        """Close the connection pool."""
        try:
            if self._pool:
                self._pool.close()
                self._pool = None
                logger.info("Oracle connection pool closed")
            return FlextResult.ok(None)

        except Exception as e:
            logger.exception("Failed to close Oracle connection pool")
            return FlextResult.fail(f"Connection pool closure failed: {e}")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[oracledb.Connection]:
        """Get a connection from the pool."""
        if not self._pool:
            init_result = await self.initialize_pool()
            if not init_result.success:
                msg = f"Failed to initialize connection pool: {init_result.error}"
                raise ValueError(msg)

        if not self._pool:
            msg = "Connection pool not initialized"
            raise ValueError(msg)

        connection = None
        try:
            connection = self._pool.acquire()
            yield connection
        finally:
            if connection and self._pool:
                self._pool.release(connection)

    async def test_connection(self) -> FlextResult[Any]:
        """Test the database connection."""
        try:
            async with self.get_connection() as conn:
                # Simple test query
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM DUAL")
                    result = cursor.fetchone()

                    if result and result[0] == 1:
                        status = FlextDbOracleConnectionStatus(
                            is_connected=True,
                            host=self.config.host,
                            port=self.config.port,
                            database=self.config.database_identifier,
                            username=self.config.username,
                            last_check=datetime.now(UTC),
                            error_message=None,
                        )
                        return FlextResult.ok(status)
                    status = FlextDbOracleConnectionStatus(
                        is_connected=False,
                        host=self.config.host,
                        port=self.config.port,
                        database=self.config.database_identifier,
                        username=self.config.username,
                        last_check=datetime.now(UTC),
                        error_message="Test query returned unexpected result",
                    )
                    return FlextResult.fail("Connection test failed")

        except Exception as e:
            logger.exception("Oracle connection test failed")
            status = FlextDbOracleConnectionStatus(
                is_connected=False,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database_identifier,
                username=self.config.username,
                last_check=datetime.now(UTC),
                error_message=str(e),
            )
            return FlextResult.fail(f"Connection test failed: {e}")

    @property
    def is_pool_initialized(self) -> bool:
        """Check if connection pool is initialized."""
        return self._pool is not None

    @property
    def is_query_service_initialized(self) -> bool:
        """Check if query service is initialized."""
        return self._query_service is not None

    def get_pool_status(self) -> dict[str, Any]:
        """Get connection pool status information."""
        if not self._pool:
            return {"initialized": False, "pool": None}
        return {"initialized": True, "pool": self._pool}

    async def get_database_info(self) -> FlextResult[Any]:
        """Get Oracle database information."""
        try:
            async with self.get_connection() as conn:
                # Get database version using safe cursor management
                version_sql = "SELECT banner FROM v$version WHERE rownum = 1"
                with conn.cursor() as cursor:
                    cursor.execute(version_sql)
                    version_result = cursor.fetchone()
                    version = version_result[0] if version_result else "Unknown"

                # Get database name and instance using safe cursor management
                info_sql = """
                SELECT
                    sys_context('USERENV', 'DB_NAME') as db_name,
                    sys_context('USERENV', 'INSTANCE_NAME') as instance_name,
                    sys_context('USERENV', 'SERVER_HOST') as host
                FROM dual
                """
                with conn.cursor() as cursor:
                    cursor.execute(info_sql)
                    info_result = cursor.fetchone()

                db_info = {
                    "version": version,
                    "database_name": info_result[0] if info_result else "Unknown",
                    "instance_name": info_result[1] if info_result else "Unknown",
                    "host": info_result[2] if info_result else "Unknown",
                    "connection_config": {
                        "host": self.config.host,
                        "port": self.config.port,
                        "service_name": self.config.service_name,
                        "sid": self.config.sid,
                    },
                }

                return FlextResult.ok(db_info)

        except Exception as e:
            logger.exception("Failed to get database info")
            return FlextResult.fail(f"Database info retrieval failed: {e}")

    async def execute_query(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> FlextResult[Any]:
        """Execute a query using the internal query service."""
        if not self._query_service:
            # Initialize pool and query service if not already done
            init_result = await self.initialize_pool()
            if not init_result.success:
                return FlextResult.fail(
                    f"Failed to initialize pool: {init_result.error}",
                )

        if not self._query_service:
            return FlextResult.fail("Query service not initialized")

        return await self._query_service.execute_query(sql, parameters)


class FlextDbOracleQueryService:
    """Service for executing Oracle database queries."""

    def __init__(self, connection_service: FlextDbOracleConnectionService) -> None:
        """Initialize the Oracle query service.

        Args:
            connection_service: FlextDbOracle connection service for database operations

        """
        self.connection_service = connection_service

    async def execute_query(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> FlextResult[Any]:
        """Execute a SELECT query and return results."""
        start_time = datetime.now(UTC)

        try:
            async with self.connection_service.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, parameters or {})
                    rows = cursor.fetchall()

                    # Get column names
                    columns = (
                        [desc[0] for desc in cursor.description]
                        if cursor.description
                        else []
                    )

                    # Keep rows as tuples for compatibility with existing code
                    result_rows = list(rows)

                    execution_time = (
                        datetime.now(UTC) - start_time
                    ).total_seconds() * 1000

                    result = FlextDbOracleQueryResult(
                        rows=result_rows,
                        row_count=len(result_rows),
                        columns=columns,
                        execution_time_ms=execution_time,
                    )

                    logger.info(
                        "Query executed successfully: %d rows, %.2fms",
                        len(result_rows),
                        execution_time,
                    )
                    return FlextResult.ok(result)

        except Exception as e:
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            logger.exception("Query execution failed after %.2fms", execution_time)
            return FlextResult.fail(f"Query execution failed: {e}")

    async def execute_scalar(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> FlextResult[Any]:
        """Execute a query and return a single scalar value."""
        try:
            result = await self.execute_query(sql, parameters)
            if result.success and result.data and result.data.row_count > 0:
                first_row = result.data.rows[0]
                first_value = first_row[0] if first_row else None
                return FlextResult.ok(first_value)
            return FlextResult.ok(None)

        except Exception as e:
            logger.exception("Scalar query execution failed")
            return FlextResult.fail(f"Scalar query failed: {e}")


class FlextDbOracleSchemaService:
    """Service for Oracle schema operations."""

    def __init__(self, query_service: FlextDbOracleQueryService) -> None:
        """Initialize the Oracle schema service.

        Args:
            query_service: FlextDbOracle query service for executing database queries

        """
        self.query_service = query_service

    async def get_schema_info(
        self,
        schema_name: str,
    ) -> FlextResult[Any]:
        """Get comprehensive schema information."""
        try:
            # Get schema tables
            tables_result = await self.get_schema_tables(schema_name)
            if not tables_result.success:
                return FlextResult.fail(
                    f"Failed to get schema tables: {tables_result.error}",
                )

            tables = tables_result.data or []
            schema_info = FlextDbOracleSchemaInfo(
                name=schema_name,
                tables=tables,
                table_count=len(tables),
                created_date=datetime.now(
                    UTC,
                ),  # Would need actual query for real creation date
            )

            return FlextResult.ok(schema_info)

        except Exception as e:
            logger.exception("Failed to get schema info for %s", schema_name)
            return FlextResult.fail(f"Schema info retrieval failed: {e}")

    async def get_schema_tables(
        self,
        schema_name: str,
    ) -> FlextResult[Any]:
        """Get all tables in a schema with optimized single-query approach.

        Eliminates N+1 query problem by fetching all table and column data together.
        """
        # Single optimized query to get all table and column information
        sql = """
        SELECT
            t.table_name,
            t.tablespace_name,
            t.num_rows,
            c.column_name,
            c.data_type,
            c.nullable,
            c.data_default,
            c.data_length,
            c.data_precision,
            c.data_scale,
            c.column_id
        FROM all_tables t
        LEFT JOIN all_tab_columns c ON t.owner = c.owner AND t.table_name = c.table_name
        WHERE t.owner = UPPER(:schema_name)
        ORDER BY t.table_name, c.column_id
        """

        try:
            result = await self.query_service.execute_query(
                sql,
                {"schema_name": schema_name},
            )
            if not result.success:
                return FlextResult.fail(
                    f"Failed to query schema tables: {result.error}",
                )

            if not result.data:
                return FlextResult.fail(
                    "No result data returned from schema query",
                )

            # Process results efficiently by grouping columns by table
            tables_dict: dict[str, dict[str, Any]] = {}
            for row in result.data.rows:
                table_name = row[0]
                tablespace_name = row[1]
                num_rows = row[2]

                # Initialize table metadata if not exists
                if table_name not in tables_dict:
                    tables_dict[table_name] = {
                        "metadata": {
                            "schema_name": schema_name,
                            "table_name": table_name,
                            "tablespace": tablespace_name,
                            "row_count": num_rows,
                            "comments": None,
                            "created_date": None,
                        },
                        "columns": [],
                    }

                # Add column information if present (LEFT JOIN may have NULL columns)
                if row[3] is not None:  # column_name exists
                    column_info = FlextDbOracleColumnInfo(
                        name=row[3],  # column_name
                        data_type=row[4],  # data_type
                        nullable=row[5] == "Y",  # nullable
                        default_value=row[6],  # data_default
                        max_length=row[7],  # data_length
                        precision=row[8],  # data_precision
                        scale=row[9],  # data_scale
                    )
                    tables_dict[table_name]["columns"].append(column_info)

            # Convert to FlextDbOracleTableMetadata objects
            tables = []
            for table_data in tables_dict.values():
                table_meta = FlextDbOracleTableMetadata(
                    columns=table_data["columns"],
                    **table_data["metadata"],
                )
                tables.append(table_meta)

            logger.info(
                "Retrieved %d tables with %d total columns for schema %s",
                len(tables),
                sum(len(t.columns) for t in tables),
                schema_name,
            )
            return FlextResult.ok(tables)

        except Exception as e:
            logger.exception("Failed to get tables for schema %s", schema_name)
            return FlextResult.fail(f"Schema tables retrieval failed: {e}")

    async def get_table_columns(
        self,
        schema_name: str,
        table_name: str,
    ) -> FlextResult[Any]:
        """Get column information for a specific table.

        Note: For bulk schema operations, use get_schema_tables() which is optimized
        to avoid N+1 query problems by fetching all tables and columns together.
        """
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
            result = await self.query_service.execute_query(
                sql,
                {
                    "schema_name": schema_name,
                    "table_name": table_name,
                },
            )

            if not result.success:
                return FlextResult.fail(
                    f"Failed to query table columns: {result.error}",
                )

            if not result.data:
                return FlextResult.fail(
                    "No result data returned from columns query",
                )

            columns = []
            for row in result.data.rows:
                column_info = FlextDbOracleColumnInfo(
                    name=row[0],  # column_name
                    data_type=row[1],  # data_type
                    nullable=row[2] == "Y",  # nullable
                    default_value=row[3],  # data_default
                    max_length=row[4],  # data_length
                    precision=row[5],  # data_precision
                    scale=row[6],  # data_scale
                    comments=None,
                )
                columns.append(column_info)

            return FlextResult.ok(columns)

        except Exception as e:
            logger.exception("Failed to get columns for %s.%s", schema_name, table_name)
            return FlextResult.fail(f"Table columns retrieval failed: {e}")

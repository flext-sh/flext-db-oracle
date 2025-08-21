"""Oracle database metadata management service following SOLID principles.

This module provides the metadata management service for Oracle database introspection
and schema analysis, following Clean Architecture and SOLID principles.

The MetadataManager is an application service that orchestrates database metadata
operations using the domain models from models.py.

SOLID Principles Applied:
- Single Responsibility: MetadataManager only handles metadata operations
- Open/Closed: Extensible through plugins and inheritance
- Liskov Substitution: Compatible with abstract database metadata interfaces
- Interface Segregation: Focused interface for metadata operations
- Dependency Inversion: Depends on abstractions (connection interface)

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextResult, get_logger

from flext_db_oracle.constants import FlextOracleDbConstants
from flext_db_oracle.models import (
    FlextDbOracleColumn,
    FlextDbOracleSchema,
    FlextDbOracleTable,
)

if TYPE_CHECKING:
    from flext_db_oracle.connection import FlextDbOracleConnection

logger = get_logger(__name__)

__all__ = [
    "FlextDbOracleColumn",
    "FlextDbOracleMetadataManager",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
]

# =============================================================================
# METADATA MANAGEMENT SERVICE - Application Layer
# =============================================================================


class FlextDbOracleMetadataManager:
    """Oracle database metadata management service.

    Application service responsible for coordinating Oracle database metadata
    operations including schema introspection, table analysis, and DDL generation.

    This class follows the Application Service pattern from Clean Architecture,
    orchestrating domain objects and database operations without containing
    business logic itself.

    Attributes:
        connection: Oracle database connection for metadata queries

    Example:
        >>> from flext_db_oracle import (
        ...     FlextDbOracleConnection,
        ...     FlextDbOracleMetadataManager,
        ... )
        >>> connection = FlextDbOracleConnection(config)
        >>> connection.connect()
        >>> metadata_manager = FlextDbOracleMetadataManager(connection)
        >>>
        >>> # Get schema metadata
        >>> schema_result = metadata_manager.get_schema_metadata("HR")
        >>> if schema_result.is_success:
        ...     schema = schema_result.value
        ...     print(f"Schema has {len(schema.tables)} tables")
        >>>
        >>> # Get table metadata
        >>> table_result = metadata_manager.get_table_metadata("EMPLOYEES", "HR")
        >>> if table_result.is_success:
        ...     table = table_result.value
        ...     print(f"Table has {len(table.columns)} columns")

    """

    def __init__(self, connection: FlextDbOracleConnection) -> None:
        """Initialize metadata manager with database connection.

        Args:
            connection: Active Oracle database connection

        """
        self.connection = connection
        logger.debug("Initialized FlextDbOracleMetadataManager")

    def get_schemas(self) -> FlextResult[list[str]]:
        """Get list of available database schemas.

        Returns:
            FlextResult containing list of schema names, or error if operation fails

        """
        query = """
        SELECT username
        FROM all_users
        WHERE username NOT IN ('SYS', 'SYSTEM', 'DBSNMP', 'SYSMAN', 'OUTLN', 'MGMT_VIEW')
        ORDER BY username
        """

        result = self.connection.execute_query(query)
        if result.is_failure:
            return FlextResult[list[str]].fail(
                f"Failed to retrieve schemas: {result.error}"
            )

        schemas = [str(row[0]) for row in result.value]
        logger.debug(f"Retrieved {len(schemas)} schemas")
        return FlextResult[list[str]].ok(schemas)

    def get_tables(self, schema_name: str | None = None) -> FlextResult[list[str]]:
        """Get list of tables in a schema.

        Args:
            schema_name: Schema name to query, or None for current user's schema

        Returns:
            FlextResult containing list of table names, or error if operation fails

        """
        if schema_name:
            query = """
            SELECT table_name
            FROM all_tables
            WHERE owner = :schema_name
            ORDER BY table_name
            """
            params: dict[str, object] = {"schema_name": schema_name.upper()}
        else:
            query = """
            SELECT table_name
            FROM user_tables
            ORDER BY table_name
            """
            params = {}

        result = self.connection.execute_query(query, params)
        if result.is_failure:
            return FlextResult[list[str]].fail(
                f"Failed to retrieve tables: {result.error}"
            )

        tables = [str(row[0]) for row in result.value]
        logger.debug(
            f"Retrieved {len(tables)} tables from schema {schema_name or 'current'}"
        )
        return FlextResult[list[str]].ok(tables)

    def get_columns(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[list[str]]:
        """Get list of columns in a table.

        Args:
            table_name: Table name to query
            schema_name: Schema name, or None for current user's schema

        Returns:
            FlextResult containing list of column names, or error if operation fails

        """
        if schema_name:
            query = """
            SELECT column_name
            FROM all_tab_columns
            WHERE table_name = :table_name
            AND owner = :schema_name
            ORDER BY column_id
            """
            params: dict[str, object] = {
                "table_name": table_name.upper(),
                "schema_name": schema_name.upper(),
            }
        else:
            query = """
            SELECT column_name
            FROM user_tab_columns
            WHERE table_name = :table_name
            ORDER BY column_id
            """
            params = {"table_name": table_name.upper()}

        result = self.connection.execute_query(query, params)
        if result.is_failure:
            return FlextResult[list[str]].fail(
                f"Failed to retrieve columns: {result.error}"
            )

        columns = [str(row[0]) for row in result.value]
        logger.debug(
            f"Retrieved {len(columns)} columns from table {schema_name or 'current'}.{table_name}"
        )
        return FlextResult[list[str]].ok(columns)

    def get_table_metadata(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[FlextDbOracleTable]:
        """Get complete table metadata including columns.

        Args:
            table_name: Table name to analyze
            schema_name: Schema name, or None for current user's schema

        Returns:
            FlextResult containing FlextDbOracleTable model, or error if operation fails

        """
        # First get table basic info
        if schema_name:
            table_query = """
            SELECT table_name, tablespace_name, null as table_comment
            FROM all_tables
            WHERE table_name = :table_name AND owner = :schema_name
            """
            table_params: dict[str, object] = {
                "table_name": table_name.upper(),
                "schema_name": schema_name.upper(),
            }
        else:
            table_query = """
            SELECT table_name, tablespace_name, null as table_comment
            FROM user_tables
            WHERE table_name = :table_name
            """
            table_params = {"table_name": table_name.upper()}
            schema_name = "USER"  # Default for current user

        table_result = self.connection.execute_query(table_query, table_params)
        if table_result.is_failure:
            return FlextResult[FlextDbOracleTable].fail(
                f"Failed to retrieve table info: {table_result.error}"
            )

        if not table_result.value:
            return FlextResult[FlextDbOracleTable].fail(
                f"Table {table_name} not found in schema {schema_name}"
            )

        table_row = table_result.value[0]

        # Get column metadata
        column_result = self.get_column_metadata(table_name, schema_name)
        if column_result.is_failure:
            return FlextResult[FlextDbOracleTable].fail(
                f"Failed to retrieve column metadata: {column_result.error}"
            )

        try:
            table = FlextDbOracleTable(
                table_name=str(table_row[0]),
                schema_name=schema_name,
                columns=column_result.value,
                tablespace_name=str(table_row[1]) if table_row[1] is not None else None,
                table_comment=str(table_row[2]) if table_row[2] is not None else None,
            )

            # Validate business rules
            validation_result = table.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[FlextDbOracleTable].fail(
                    f"Table validation failed: {validation_result.error}"
                )

            logger.debug(
                f"Retrieved metadata for table {schema_name}.{table_name} with {len(table.columns)} columns"
            )
            return FlextResult[FlextDbOracleTable].ok(table)

        except Exception as e:
            return FlextResult[FlextDbOracleTable].fail(
                f"Failed to create table model: {e}"
            )

    def get_column_metadata(
        self, table_name: str, schema_name: str | None = None
    ) -> FlextResult[list[FlextDbOracleColumn]]:
        """Get detailed column metadata for a table.

        Args:
            table_name: Table name to analyze
            schema_name: Schema name, or None for current user's schema

        Returns:
            FlextResult containing list of FlextDbOracleColumn models, or error if operation fails

        """
        if schema_name:
            query = """
            SELECT
                column_name,
                data_type,
                nullable,
                data_length,
                data_precision,
                data_scale,
                column_id,
                data_default,
                null as comments
            FROM all_tab_columns
            WHERE table_name = :table_name AND owner = :schema_name
            ORDER BY column_id
            """
            params: dict[str, object] = {
                "table_name": table_name.upper(),
                "schema_name": schema_name.upper(),
            }
        else:
            query = """
            SELECT
                column_name,
                data_type,
                nullable,
                data_length,
                data_precision,
                data_scale,
                column_id,
                data_default,
                null as comments
            FROM user_tab_columns
            WHERE table_name = :table_name
            ORDER BY column_id
            """
            params = {"table_name": table_name.upper()}

        result = self.connection.execute_query(query, params)
        if result.is_failure:
            return FlextResult[list[FlextDbOracleColumn]].fail(
                f"Failed to retrieve column metadata: {result.error}"
            )

        columns = []
        for row in result.value:
            try:
                column = FlextDbOracleColumn(
                    column_name=str(row[0]),
                    data_type=str(row[1]),
                    nullable=str(row[2]) == "Y",
                    data_length=int(row[3]) if row[3] is not None else None,
                    data_precision=int(row[4]) if row[4] is not None else None,
                    data_scale=int(row[5]) if row[5] is not None else None,
                    column_id=int(row[6]),
                    default_value=str(row[7]) if row[7] is not None else None,
                    comments=str(row[8]) if row[8] is not None else None,
                )

                # Validate business rules
                validation_result = column.validate_business_rules()
                if validation_result.is_failure:
                    logger.warning(
                        f"Column {row[0]} validation warning: {validation_result.error}"
                    )

                columns.append(column)

            except Exception as e:
                return FlextResult[list[FlextDbOracleColumn]].fail(
                    f"Failed to create column model for {row[0]}: {e}"
                )

        logger.debug(f"Retrieved metadata for {len(columns)} columns")
        return FlextResult[list[FlextDbOracleColumn]].ok(columns)

    def get_schema_metadata(self, schema_name: str) -> FlextResult[FlextDbOracleSchema]:
        """Get complete schema metadata including all tables.

        Args:
            schema_name: Schema name to analyze

        Returns:
            FlextResult containing FlextDbOracleSchema model, or error if operation fails

        """
        # Get table list
        tables_result = self.get_tables(schema_name)
        if tables_result.is_failure:
            return FlextResult[FlextDbOracleSchema].fail(
                f"Failed to retrieve tables: {tables_result.error}"
            )

        # Get metadata for each table
        tables = []
        for table_name in tables_result.value:
            table_result = self.get_table_metadata(table_name, schema_name)
            if table_result.is_failure:
                logger.warning(
                    f"Failed to get metadata for table {table_name}: {table_result.error}"
                )
                continue
            tables.append(table_result.value)

        try:
            schema = FlextDbOracleSchema(
                schema_name=schema_name,
                tables=tables,
                default_tablespace="USERS",
                temporary_tablespace="TEMP",
            )

            # Validate business rules
            validation_result = schema.validate_business_rules()
            if validation_result.is_failure:
                return FlextResult[FlextDbOracleSchema].fail(
                    f"Schema validation failed: {validation_result.error}"
                )

            logger.info(
                f"Retrieved metadata for schema {schema_name} with {len(tables)} tables"
            )
            return FlextResult[FlextDbOracleSchema].ok(schema)

        except Exception as e:
            return FlextResult[FlextDbOracleSchema].fail(
                f"Failed to create schema model: {e}"
            )

    def generate_ddl(self, table: FlextDbOracleTable) -> FlextResult[str]:
        """Generate CREATE TABLE DDL statement for a table.

        Args:
            table: Table model to generate DDL for

        Returns:
            FlextResult containing DDL string, or error if generation fails

        """
        try:
            ddl_lines = [f"CREATE TABLE {table.fully_qualified_name} ("]

            column_definitions = [
                f"    {column.sql_definition}" for column in table.columns
            ]

            ddl_lines.extend((",\n".join(column_definitions), ")"))

            if table.tablespace_name:
                ddl_lines.append(f"TABLESPACE {table.tablespace_name}")

            ddl = "\n".join(ddl_lines) + ";"

            logger.debug(f"Generated DDL for table {table.fully_qualified_name}")
            return FlextResult[str].ok(ddl)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to generate DDL: {e}")

    def test_connection(self) -> FlextResult[None]:
        """Test the database connection.

        Returns:
            FlextResult indicating success or failure of connection test

        """
        result = self.connection.execute_query(FlextOracleDbConstants.Query.TEST_QUERY)
        if result.is_failure:
            return FlextResult[None].fail(f"Connection test failed: {result.error}")

        logger.debug("Connection test successful")
        return FlextResult[None].ok(None)

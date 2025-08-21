"""Oracle database field definitions following flext-core field patterns.

This module provides reusable Pydantic field definitions for Oracle database
models, following the flext-core fields pattern for consistency and reusability.

Field definitions are organized by type:
- Connection fields (host, port, service_name, etc.)
- Database metadata fields (table_name, column_name, etc.)
- Query fields (fetch_size, timeout, etc.)
- Validation fields (constraints, patterns, etc.)

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from flext_db_oracle.constants import FlextOracleDbConstants

__all__ = [
    "ConnectionFields",
    "DatabaseMetadataFields",
    "QueryFields",
    "ValidationFields",
]

# =============================================================================
# CONNECTION FIELD DEFINITIONS
# =============================================================================


class ConnectionFields:
    """Oracle connection field definitions."""

    # Host and networking
    host = Field(
        ...,
        description="Oracle database host",
        min_length=1,
        max_length=255,
        examples=["localhost", "192.168.1.100", "oracle-db.company.com"],
    )

    port = Field(
        default=FlextOracleDbConstants.Connection.DEFAULT_PORT,
        description="Oracle database port number",
        ge=1,
        le=FlextOracleDbConstants.Connection.MAX_PORT,
        examples=[1521, 1522],
    )

    service_name = Field(
        default=FlextOracleDbConstants.Connection.DEFAULT_SERVICE_NAME,
        description="Oracle service name or SID",
        min_length=1,
        max_length=128,
        examples=["XEPDB1", "ORCL", "PDB1"],
    )

    # Authentication
    username = Field(
        ...,
        description="Database username",
        min_length=1,
        max_length=128,
        examples=["oracle", "app_user", "system"],
    )

    password = Field(
        ...,
        description="Database password",
        min_length=1,
        max_length=256,
        examples=["password123", "SecurePass!"],
        repr=False,  # Don't show password in repr
    )

    # Connection pool settings
    pool_min = Field(
        default=FlextOracleDbConstants.Connection.DEFAULT_POOL_MIN,
        description="Minimum pool size",
        ge=0,
        le=100,
        examples=[1, 5, 10],
    )

    pool_max = Field(
        default=FlextOracleDbConstants.Connection.DEFAULT_POOL_MAX,
        description="Maximum pool size",
        ge=1,
        le=1000,
        examples=[10, 50, 100],
    )

    pool_increment = Field(
        default=FlextOracleDbConstants.Connection.DEFAULT_POOL_INCREMENT,
        description="Pool increment size",
        ge=1,
        le=10,
        examples=[1, 2, 5],
    )

    # Timeouts
    connect_timeout = Field(
        default=FlextOracleDbConstants.Connection.DEFAULT_TIMEOUT,
        description="Connection timeout in seconds",
        ge=1,
        le=300,
        examples=[30, 60, 120],
    )

    pool_timeout = Field(
        default=FlextOracleDbConstants.Connection.DEFAULT_POOL_TIMEOUT,
        description="Pool timeout in seconds",
        ge=1,
        le=300,
        examples=[30, 60, 120],
    )


# =============================================================================
# DATABASE METADATA FIELD DEFINITIONS
# =============================================================================


class DatabaseMetadataFields:
    """Oracle database metadata field definitions."""

    # Schema and object names
    schema_name = Field(
        ...,
        description="Database schema name",
        min_length=1,
        max_length=FlextOracleDbConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH,
        pattern=FlextOracleDbConstants.OracleValidation.SCHEMA_PATTERN,
        examples=["HR", "SALES", "APP_SCHEMA"],
    )

    table_name = Field(
        ...,
        description="Database table name",
        min_length=1,
        max_length=FlextOracleDbConstants.OracleValidation.MAX_TABLE_NAME_LENGTH,
        pattern=FlextOracleDbConstants.OracleValidation.IDENTIFIER_PATTERN,
        examples=["EMPLOYEES", "CUSTOMERS", "ORDER_ITEMS"],
    )

    column_name = Field(
        ...,
        description="Database column name",
        min_length=1,
        max_length=FlextOracleDbConstants.OracleValidation.MAX_COLUMN_NAME_LENGTH,
        pattern=FlextOracleDbConstants.OracleValidation.IDENTIFIER_PATTERN,
        examples=["ID", "FIRST_NAME", "CREATED_DATE"],
    )

    # Data type information
    data_type = Field(
        ...,
        description="Oracle data type",
        min_length=1,
        max_length=128,
        examples=["VARCHAR2", "NUMBER", "DATE", "CLOB", "TIMESTAMP"],
    )

    data_length: int | None = Field(
        None,
        description="Data length for character types",
        ge=1,
        le=32767,
        examples=[50, 255, 4000],
    )

    data_precision: int | None = Field(
        None, description="Numeric precision", ge=1, le=38, examples=[10, 15, 38]
    )

    data_scale: int | None = Field(
        None, description="Numeric scale", ge=0, le=127, examples=[0, 2, 4]
    )

    # Column metadata
    column_id = Field(
        ..., description="Column position/ID", ge=1, le=1000, examples=[1, 2, 10]
    )

    nullable = Field(
        default=True, description="Column allows NULL values", examples=[True, False]
    )

    default_value: str | None = Field(
        None,
        description="Default value for column",
        max_length=4000,
        examples=["NULL", "SYSDATE", "'DEFAULT_VALUE'"],
    )

    comments: str | None = Field(
        None,
        description="Column comments",
        max_length=4000,
        examples=["Primary key", "Employee full name", "Created timestamp"],
    )


# =============================================================================
# QUERY FIELD DEFINITIONS
# =============================================================================


class QueryFields:
    """Oracle query field definitions."""

    # Fetch and pagination
    fetch_size = Field(
        default=FlextOracleDbConstants.Query.DEFAULT_FETCH_SIZE,
        description="Number of rows to fetch at once",
        ge=1,
        le=FlextOracleDbConstants.Query.MAX_FETCH_SIZE,
        examples=[100, 1000, 5000],
    )

    array_size = Field(
        default=FlextOracleDbConstants.Query.DEFAULT_ARRAY_SIZE,
        description="Array size for bulk operations",
        ge=1,
        le=10000,
        examples=[100, 500, 1000],
    )

    # Query execution
    execution_time_ms = Field(
        default=0.0,
        description="Query execution time in milliseconds",
        ge=0.0,
        examples=[100.5, 1500.2, 30000.0],
    )

    row_count = Field(
        default=0,
        description="Number of rows affected/returned",
        ge=0,
        examples=[0, 10, 1000, 50000],
    )

    # Query metadata
    query_hash: str | None = Field(
        None,
        description="Query hash for caching and identification",
        min_length=8,
        max_length=64,
        pattern=r"^[a-fA-F0-9]+$",
        examples=["a1b2c3d4e5f6", "1234567890abcdef"],
    )

    query_id: str | None = Field(
        None,
        description="Unique query identifier",
        min_length=1,
        max_length=128,
        examples=["query_001", "user_lookup", "monthly_report"],
    )


# =============================================================================
# VALIDATION FIELD DEFINITIONS
# =============================================================================


class ValidationFields:
    """Oracle validation field definitions."""

    # Connection validation
    is_connected = Field(
        ..., description="Connection status flag", examples=[True, False]
    )

    last_error: str | None = Field(
        None,
        description="Last error message",
        max_length=4000,
        examples=[None, "ORA-00942: table or view does not exist"],
    )

    connection_time_ms: float | None = Field(
        None,
        description="Connection establishment time in milliseconds",
        ge=0.0,
        examples=[50.0, 150.3, 500.7],
    )

    # Session metrics
    active_sessions = Field(
        default=0,
        description="Number of active database sessions",
        ge=0,
        le=10000,
        examples=[5, 25, 100],
    )

    max_sessions = Field(
        default=100,
        description="Maximum allowed sessions",
        ge=1,
        le=10000,
        examples=[50, 100, 500],
    )

    # Health check fields
    last_check: str | None = Field(
        None,
        description="Last health check timestamp",
        examples=["2025-01-15T10:30:00Z"],
    )

    is_healthy = Field(
        default=True, description="Overall health status", examples=[True, False]
    )


# =============================================================================
# TYPED FIELD ALIASES - For convenience and type safety
# =============================================================================

# Connection field types
HostField = Annotated[str, ConnectionFields.host]
PortField = Annotated[int, ConnectionFields.port]
ServiceNameField = Annotated[str, ConnectionFields.service_name]
UsernameField = Annotated[str, ConnectionFields.username]
PasswordField = Annotated[str, ConnectionFields.password]

# Metadata field types
SchemaNameField = Annotated[str, DatabaseMetadataFields.schema_name]
TableNameField = Annotated[str, DatabaseMetadataFields.table_name]
ColumnNameField = Annotated[str, DatabaseMetadataFields.column_name]
DataTypeField = Annotated[str, DatabaseMetadataFields.data_type]

# Query field types
FetchSizeField = Annotated[int, QueryFields.fetch_size]
ArraySizeField = Annotated[int, QueryFields.array_size]
ExecutionTimeField = Annotated[float, QueryFields.execution_time_ms]
RowCountField = Annotated[int, QueryFields.row_count]

# Validation field types
IsConnectedField = Annotated[bool, ValidationFields.is_connected]
LastErrorField = Annotated[str | None, ValidationFields.last_error]
ActiveSessionsField = Annotated[int, ValidationFields.active_sessions]
MaxSessionsField = Annotated[int, ValidationFields.max_sessions]

"""FLEXT DB Oracle Fields following Flext[Area][Module] pattern.

This module provides the FlextDbOracleFields class with consolidated
field definitions following FLEXT architectural patterns with DRY principles.

Single consolidated class containing ALL Oracle field definitions organized
internally, following SOLID principles and eliminating duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

from flext_core import FlextFactory
from pydantic import Field
from pydantic.fields import FieldInfo

from flext_db_oracle.constants import FlextDbOracleConstants


class FlextDbOracleFields(FlextFactory):
    """Oracle Database Fields following Flext[Area][Module] pattern.

    Single consolidated class containing ALL Oracle field definitions
    organized internally, following SOLID principles and DRY methodology.

    This class consolidates ALL Oracle field functionality into a single
    entry point eliminating duplication and multiple small classes.
    """

    # =============================================================================
    # CONNECTION FIELDS - HOST, NETWORK, AUTHENTICATION, POOLS
    # =============================================================================

    host = Field(
        ...,
        description="Oracle database host",
        min_length=1,
        max_length=255,
        examples=["localhost", "192.168.1.100", "oracle-db.company.com"],
    )

    port = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_PORT,
        description="Oracle database port number",
        ge=1,
        le=FlextDbOracleConstants.Connection.MAX_PORT,
        examples=[1521, 1522],
    )

    service_name = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_SERVICE_NAME,
        description="Oracle service name or SID",
        min_length=1,
        max_length=128,
        examples=["XEPDB1", "ORCL", "PDB1"],
    )

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
        default=FlextDbOracleConstants.Connection.DEFAULT_POOL_MIN,
        description="Minimum pool size",
        ge=0,
        le=100,
        examples=[1, 5, 10],
    )

    pool_max = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_POOL_MAX,
        description="Maximum pool size",
        ge=1,
        le=1000,
        examples=[10, 50, 100],
    )

    pool_increment = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_POOL_INCREMENT,
        description="Pool increment size",
        ge=1,
        le=10,
        examples=[1, 2, 5],
    )

    # Timeouts
    connect_timeout = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_TIMEOUT,
        description="Connection timeout in seconds",
        ge=1,
        le=300,
        examples=[30, 60, 120],
    )

    pool_timeout = Field(
        default=FlextDbOracleConstants.Connection.DEFAULT_POOL_TIMEOUT,
        description="Pool timeout in seconds",
        ge=1,
        le=300,
        examples=[30, 60, 120],
    )

    # =============================================================================
    # DATABASE METADATA FIELDS - SCHEMAS, TABLES, COLUMNS, DATA TYPES
    # =============================================================================

    schema_name = Field(
        ...,
        description="Database schema name",
        min_length=1,
        max_length=FlextDbOracleConstants.OracleValidation.MAX_SCHEMA_NAME_LENGTH,
        pattern=FlextDbOracleConstants.OracleValidation.SCHEMA_PATTERN,
        examples=["HR", "SALES", "APP_SCHEMA"],
    )

    table_name = Field(
        ...,
        description="Database table name",
        min_length=1,
        max_length=FlextDbOracleConstants.OracleValidation.MAX_TABLE_NAME_LENGTH,
        pattern=FlextDbOracleConstants.OracleValidation.IDENTIFIER_PATTERN,
        examples=["EMPLOYEES", "CUSTOMERS", "ORDER_ITEMS"],
    )

    column_name = Field(
        ...,
        description="Database column name",
        min_length=1,
        max_length=FlextDbOracleConstants.OracleValidation.MAX_COLUMN_NAME_LENGTH,
        pattern=FlextDbOracleConstants.OracleValidation.IDENTIFIER_PATTERN,
        examples=["ID", "FIRST_NAME", "CREATED_DATE"],
    )

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
    # QUERY FIELDS - EXECUTION, PAGINATION, PERFORMANCE
    # =============================================================================

    fetch_size = Field(
        default=FlextDbOracleConstants.Query.DEFAULT_FETCH_SIZE,
        description="Number of rows to fetch at once",
        ge=1,
        le=FlextDbOracleConstants.Query.MAX_FETCH_SIZE,
        examples=[100, 1000, 5000],
    )

    array_size = Field(
        default=FlextDbOracleConstants.Query.DEFAULT_ARRAY_SIZE,
        description="Array size for bulk operations",
        ge=1,
        le=10000,
        examples=[100, 500, 1000],
    )

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
    # VALIDATION FIELDS - CONNECTION STATUS, HEALTH, CONSTRAINTS
    # =============================================================================

    is_connected = Field(
        default=False,
        description="Connection status flag",
        examples=[True, False],
    )

    is_valid = Field(
        default=False,
        description="Validation status flag",
        examples=[True, False],
    )

    health_status = Field(
        default="unknown",
        description="Health check status",
        pattern=r"^(healthy|unhealthy|unknown|degraded)$",
        examples=["healthy", "unhealthy", "unknown", "degraded"],
    )

    last_check_time: str | None = Field(
        None,
        description="Last health check timestamp",
        examples=["2024-01-15T10:30:00Z"],
    )

    error_count = Field(
        default=0,
        description="Number of errors encountered",
        ge=0,
        examples=[0, 1, 5, 20],
    )

    # =============================================================================
    # FACTORY METHODS - CONSOLIDATED FIELD CREATION
    # =============================================================================

    @classmethod
    def get_connection_field(cls, field_name: str) -> FieldInfo:
        """Get connection field by name."""
        field_mapping = {
            "host": cls.host,
            "port": cls.port,
            "service_name": cls.service_name,
            "username": cls.username,
            "password": cls.password,
            "pool_min": cls.pool_min,
            "pool_max": cls.pool_max,
            "pool_increment": cls.pool_increment,
            "connect_timeout": cls.connect_timeout,
            "pool_timeout": cls.pool_timeout,
        }
        if field_name in field_mapping:
            return cast("FieldInfo", field_mapping[field_name])
        msg = f"Unknown connection field: {field_name}"
        raise ValueError(msg)

    @classmethod
    def get_metadata_field(cls, field_name: str) -> FieldInfo:
        """Get metadata field by name."""
        field_mapping = {
            "schema_name": cls.schema_name,
            "table_name": cls.table_name,
            "column_name": cls.column_name,
            "data_type": cls.data_type,
            "data_length": cls.data_length,
            "data_precision": cls.data_precision,
            "data_scale": cls.data_scale,
            "column_id": cls.column_id,
            "nullable": cls.nullable,
            "default_value": cls.default_value,
            "comments": cls.comments,
        }
        if field_name in field_mapping:
            return cast("FieldInfo", field_mapping[field_name])
        msg = f"Unknown metadata field: {field_name}"
        raise ValueError(msg)

    @classmethod
    def get_query_field(cls, field_name: str) -> FieldInfo:
        """Get query field by name."""
        field_mapping = {
            "fetch_size": cls.fetch_size,
            "array_size": cls.array_size,
            "execution_time_ms": cls.execution_time_ms,
            "row_count": cls.row_count,
            "query_hash": cls.query_hash,
            "query_id": cls.query_id,
        }
        if field_name in field_mapping:
            return cast("FieldInfo", field_mapping[field_name])
        msg = f"Unknown query field: {field_name}"
        raise ValueError(msg)

    # =============================================================================
    # BACKWARD COMPATIBILITY ALIASES - CONSOLIDATED
    # =============================================================================

    # Create compatibility classes as internal references
    class ConnectionFields:
        """Backward compatibility - use FlextDbOracleFields directly."""

        def __getattr__(self, name: str) -> object:
            """Delegate attribute access to FlextDbOracleFields."""
            return getattr(FlextDbOracleFields, name)

    class DatabaseMetadataFields:
        """Backward compatibility - use FlextDbOracleFields directly."""

        def __getattr__(self, name: str) -> object:
            """Delegate attribute access to FlextDbOracleFields."""
            return getattr(FlextDbOracleFields, name)

    class QueryFields:
        """Backward compatibility - use FlextDbOracleFields directly."""

        def __getattr__(self, name: str) -> object:
            """Delegate attribute access to FlextDbOracleFields."""
            return getattr(FlextDbOracleFields, name)

    class ValidationFields:
        """Backward compatibility - use FlextDbOracleFields directly."""

        def __getattr__(self, name: str) -> object:
            """Delegate attribute access to FlextDbOracleFields."""
            return getattr(FlextDbOracleFields, name)


# Module-level backward compatibility aliases
ConnectionFields = FlextDbOracleFields.ConnectionFields
DatabaseMetadataFields = FlextDbOracleFields.DatabaseMetadataFields
QueryFields = FlextDbOracleFields.QueryFields
ValidationFields = FlextDbOracleFields.ValidationFields

__all__ = [
    # Backward compatibility
    "ConnectionFields",
    "DatabaseMetadataFields",
    "FlextDbOracleFields",
    "QueryFields",
    "ValidationFields",
]

"""FLEXT DB ORACLE Constants - Oracle-specific Constants.

All Oracle database related constants organized following flext-core patterns.
Extends FlextConstants with Oracle-specific configuration.
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Final

# Import base constants from flext-core

# ==================================================================
# ENUMS - Oracle-specific enums
# ==================================================================


class FlextDbOracleConnectionProtocol(StrEnum):
    """Oracle connection protocols."""

    TCP = "tcp"
    TCPS = "tcps"
    IPC = "ipc"


class FlextDbOracleAuthMode(StrEnum):
    """Oracle authentication modes."""

    NORMAL = "normal"
    SYSDBA = "sysdba"
    SYSOPER = "sysoper"
    SYSASM = "sysasm"


class FlextDbOracleIsolationLevel(StrEnum):
    """Oracle transaction isolation levels."""

    READ_COMMITTED = "READ_COMMITTED"
    SERIALIZABLE = "SERIALIZABLE"


class FlextDbOracleDataType(StrEnum):
    """Oracle data types mapping."""

    VARCHAR2 = "VARCHAR2"
    NUMBER = "NUMBER"
    DATE = "DATE"
    TIMESTAMP = "TIMESTAMP"
    CLOB = "CLOB"
    BLOB = "BLOB"
    RAW = "RAW"
    ROWID = "ROWID"
    CHAR = "CHAR"
    NCHAR = "NCHAR"
    NVARCHAR2 = "NVARCHAR2"
    NCLOB = "NCLOB"


class FlextDbOraclePoolStrategy(StrEnum):
    """Connection pool strategies."""

    STATIC = "static"
    DYNAMIC = "dynamic"
    ADAPTIVE = "adaptive"


# ==================================================================
# UNIFIED ORACLE CONSTANTS CLASS
# ==================================================================


class FlextDbOracleConstants:
    """Unified Oracle constants extending FlextConstants patterns.

    All Oracle-specific constants organized as class attributes.
    This class should NEVER be instantiated - use class attributes.

    Usage:
        from flext_db_oracle.constants import FlextDbOracleConstants

        # Access constants directly
        port = FlextDbOracleConstants.DEFAULT_PORT
        timeout = FlextDbOracleConstants.DEFAULT_QUERY_TIMEOUT
        pool_size = FlextDbOracleConstants.DEFAULT_POOL_SIZE
    """

    # ================================================================
    # LIBRARY METADATA
    # ================================================================

    VERSION: Final[str] = "0.7.0"
    NAME: Final[str] = "flext-db-oracle"
    DESCRIPTION: Final[str] = "Enterprise Oracle Database Integration"

    # ================================================================
    # CONNECTION CONSTANTS
    # ================================================================

    # Default connection parameters
    DEFAULT_HOST: Final[str] = "localhost"
    DEFAULT_PORT: Final[int] = 1521
    DEFAULT_PROTOCOL: Final[FlextDbOracleConnectionProtocol] = (
        FlextDbOracleConnectionProtocol.TCP
    )
    DEFAULT_AUTH_MODE: Final[FlextDbOracleAuthMode] = FlextDbOracleAuthMode.NORMAL

    # Connection timeouts (in seconds)
    DEFAULT_CONNECT_TIMEOUT: Final[int] = 10
    DEFAULT_QUERY_TIMEOUT: Final[int] = 300
    DEFAULT_DDL_TIMEOUT: Final[int] = 600
    MAX_CONNECT_TIMEOUT: Final[int] = 60
    MAX_QUERY_TIMEOUT: Final[int] = 3600

    # Connection retry settings
    DEFAULT_RETRY_ATTEMPTS: Final[int] = 3
    DEFAULT_RETRY_DELAY: Final[float] = 1.0
    MAX_RETRY_ATTEMPTS: Final[int] = 10
    MAX_RETRY_DELAY: Final[float] = 30.0

    # ================================================================
    # CONNECTION POOL CONSTANTS
    # ================================================================

    # Pool size settings
    DEFAULT_POOL_MIN_SIZE: Final[int] = 1
    DEFAULT_POOL_MAX_SIZE: Final[int] = 10
    DEFAULT_POOL_INCREMENT: Final[int] = 1
    MAX_POOL_SIZE: Final[int] = 100
    MIN_POOL_SIZE: Final[int] = 1

    # Pool strategy
    DEFAULT_POOL_STRATEGY: Final[FlextDbOraclePoolStrategy] = (
        FlextDbOraclePoolStrategy.DYNAMIC
    )

    # Pool timeouts
    DEFAULT_POOL_TIMEOUT: Final[int] = 30
    DEFAULT_POOL_RECYCLE: Final[int] = 3600

    # ================================================================
    # QUERY EXECUTION CONSTANTS
    # ================================================================

    # Fetch sizes
    DEFAULT_FETCH_SIZE: Final[int] = 1000
    MAX_FETCH_SIZE: Final[int] = 10000
    MIN_FETCH_SIZE: Final[int] = 1

    # Batch sizes
    DEFAULT_BATCH_SIZE: Final[int] = 1000
    MAX_BATCH_SIZE: Final[int] = 50000
    MIN_BATCH_SIZE: Final[int] = 1

    # Array sizes for bulk operations
    DEFAULT_ARRAY_SIZE: Final[int] = 1000
    MAX_ARRAY_SIZE: Final[int] = 10000

    # ================================================================
    # ORACLE-SPECIFIC LIMITS
    # ================================================================

    # Oracle database limits
    MAX_IDENTIFIER_LENGTH: Final[int] = 128  # Oracle 12.2+
    MAX_VARCHAR2_LENGTH: Final[int] = 4000
    MAX_NVARCHAR2_LENGTH: Final[int] = 2000
    MAX_RAW_LENGTH: Final[int] = 2000
    MAX_CHAR_LENGTH: Final[int] = 2000

    # Schema object limits
    MAX_TABLE_NAME_LENGTH: Final[int] = 128
    MAX_COLUMN_NAME_LENGTH: Final[int] = 128
    MAX_INDEX_NAME_LENGTH: Final[int] = 128
    MAX_CONSTRAINT_NAME_LENGTH: Final[int] = 128

    # ================================================================
    # DDL CONSTANTS
    # ================================================================

    # DDL operation timeouts
    DDL_CREATE_TABLE_TIMEOUT: Final[int] = 300
    DDL_ALTER_TABLE_TIMEOUT: Final[int] = 600
    DDL_CREATE_INDEX_TIMEOUT: Final[int] = 1800
    DDL_DROP_TABLE_TIMEOUT: Final[int] = 60

    # DDL statement templates
    CREATE_TABLE_TEMPLATE: Final[str] = 'CREATE TABLE "{schema}"."{table}" ({columns})'
    ALTER_TABLE_TEMPLATE: Final[str] = 'ALTER TABLE "{schema}"."{table}" {action}'
    DROP_TABLE_TEMPLATE: Final[str] = 'DROP TABLE "{schema}"."{table}"'
    CREATE_INDEX_TEMPLATE: Final[str] = (
        'CREATE INDEX "{schema}"."{index}" ON "{schema}"."{table}" ({columns})'
    )

    # ================================================================
    # MONITORING CONSTANTS
    # ================================================================

    # Performance monitoring intervals (in seconds)
    DEFAULT_METRICS_INTERVAL: Final[int] = 60
    DEFAULT_HEALTH_CHECK_INTERVAL: Final[int] = 30
    DEFAULT_STATS_COLLECTION_INTERVAL: Final[int] = 300

    # Thresholds for alerts
    HIGH_CPU_THRESHOLD: Final[float] = 80.0
    HIGH_MEMORY_THRESHOLD: Final[float] = 85.0
    LOW_TABLESPACE_THRESHOLD: Final[float] = 90.0
    HIGH_WAIT_TIME_THRESHOLD: Final[float] = 1000.0  # milliseconds

    # ================================================================
    # VALIDATION PATTERNS
    # ================================================================

    # Oracle identifier patterns
    VALID_ORACLE_IDENTIFIER_PATTERN: Final[str] = r"^[A-Za-z][A-Za-z0-9_$#]*$"
    VALID_SCHEMA_NAME_PATTERN: Final[str] = r"^[A-Za-z][A-Za-z0-9_]*$"
    VALID_TABLE_NAME_PATTERN: Final[str] = r"^[A-Za-z][A-Za-z0-9_]*$"

    # Compiled regex patterns for performance
    ORACLE_IDENTIFIER_REGEX: Final[re.Pattern[str]] = re.compile(
        VALID_ORACLE_IDENTIFIER_PATTERN,
    )
    SCHEMA_NAME_REGEX: Final[re.Pattern[str]] = re.compile(VALID_SCHEMA_NAME_PATTERN)
    TABLE_NAME_REGEX: Final[re.Pattern[str]] = re.compile(VALID_TABLE_NAME_PATTERN)

    # ================================================================
    # ERROR CODES AND MESSAGES
    # ================================================================

    # Oracle error codes we handle specifically
    ORACLE_CONNECTION_ERROR_CODES: Final[frozenset[int]] = frozenset(
        {1, 12154, 12514, 12541, 12543, 12545, 12547, 12170, 17002},
    )

    ORACLE_TIMEOUT_ERROR_CODES: Final[frozenset[int]] = frozenset(
        {1013, 3113, 3114, 12170, 12171, 12547, 12549},
    )

    ORACLE_RESOURCE_ERROR_CODES: Final[frozenset[int]] = frozenset(
        {20, 28, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 61},
    )

    # ================================================================
    # METADATA QUERIES
    # ================================================================

    # Standard metadata queries
    QUERY_ALL_TABLES: Final[str] = """
        SELECT table_name, tablespace_name, num_rows, blocks, avg_row_len
        FROM all_tables
        WHERE owner = UPPER(:schema_name)
        ORDER BY table_name
    """

    QUERY_TABLE_COLUMNS: Final[str] = """
        SELECT column_name, data_type, nullable, data_default,
               data_length, data_precision, data_scale, column_id
        FROM all_tab_columns
        WHERE owner = UPPER(:schema_name)
        AND table_name = UPPER(:table_name)
        ORDER BY column_id
    """

    QUERY_TABLE_CONSTRAINTS: Final[str] = """
        SELECT constraint_name, constraint_type, status, validated
        FROM all_constraints
        WHERE owner = UPPER(:schema_name)
        AND table_name = UPPER(:table_name)
        ORDER BY constraint_name
    """

    QUERY_TABLE_INDEXES: Final[str] = """
        SELECT index_name, index_type, uniqueness, status, tablespace_name
        FROM all_indexes
        WHERE owner = UPPER(:schema_name)
        AND table_name = UPPER(:table_name)
        ORDER BY index_name
    """

    # ================================================================
    # VALIDATION METHODS
    # ================================================================

    @classmethod
    def is_valid_oracle_identifier(cls, identifier: str) -> bool:
        """Check if an identifier is valid for Oracle.

        Args:
            identifier: Identifier to validate

        Returns:
            True if valid, False otherwise

        """
        if not identifier or len(identifier) > cls.MAX_IDENTIFIER_LENGTH:
            return False
        return cls.ORACLE_IDENTIFIER_REGEX.match(identifier) is not None

    @classmethod
    def is_valid_schema_name(cls, schema_name: str) -> bool:
        """Check if a schema name is valid.

        Args:
            schema_name: Schema name to validate

        Returns:
            True if valid, False otherwise

        """
        if not schema_name or len(schema_name) > cls.MAX_IDENTIFIER_LENGTH:
            return False
        return cls.SCHEMA_NAME_REGEX.match(schema_name) is not None

    @classmethod
    def is_valid_table_name(cls, table_name: str) -> bool:
        """Check if a table name is valid.

        Args:
            table_name: Table name to validate

        Returns:
            True if valid, False otherwise

        """
        if not table_name or len(table_name) > cls.MAX_TABLE_NAME_LENGTH:
            return False
        return cls.TABLE_NAME_REGEX.match(table_name) is not None

    @classmethod
    def is_connection_error(cls, error_code: int) -> bool:
        """Check if error code indicates connection problem.

        Args:
            error_code: FlextDbOracle error code

        Returns:
            True if connection error, False otherwise

        """
        return error_code in cls.ORACLE_CONNECTION_ERROR_CODES

    @classmethod
    def is_timeout_error(cls, error_code: int) -> bool:
        """Check if error code indicates timeout.

        Args:
            error_code: FlextDbOracle error code

        Returns:
            True if timeout error, False otherwise

        """
        return error_code in cls.ORACLE_TIMEOUT_ERROR_CODES

    @classmethod
    def is_resource_error(cls, error_code: int) -> bool:
        """Check if error code indicates resource limit.

        Args:
            error_code: FlextDbOracle error code

        Returns:
            True if resource error, False otherwise

        """
        return error_code in cls.ORACLE_RESOURCE_ERROR_CODES

    # ================================================================
    # UTILITY METHODS
    # ================================================================

    @classmethod
    def get_all_connection_protocols(cls) -> list[FlextDbOracleConnectionProtocol]:
        """Get all available connection protocols."""
        return [
            FlextDbOracleConnectionProtocol.TCP,
            FlextDbOracleConnectionProtocol.TCPS,
            FlextDbOracleConnectionProtocol.IPC,
        ]

    @classmethod
    def get_all_auth_modes(cls) -> list[FlextDbOracleAuthMode]:
        """Get all available authentication modes."""
        return [
            FlextDbOracleAuthMode.NORMAL,
            FlextDbOracleAuthMode.SYSDBA,
            FlextDbOracleAuthMode.SYSOPER,
            FlextDbOracleAuthMode.SYSASM,
        ]

    @classmethod
    def get_all_isolation_levels(cls) -> list[FlextDbOracleIsolationLevel]:
        """Get all available isolation levels."""
        return [
            FlextDbOracleIsolationLevel.READ_COMMITTED,
            FlextDbOracleIsolationLevel.SERIALIZABLE,
        ]

    @classmethod
    def get_recommended_pool_size(cls, expected_concurrent_users: int) -> int:
        """Get recommended pool size based on expected users.

        Args:
            expected_concurrent_users: Expected concurrent users

        Returns:
            Recommended pool size

        """
        # Rule of thumb: pool size should be 2-3x concurrent users
        recommended = min(expected_concurrent_users * 2, cls.MAX_POOL_SIZE)
        return max(recommended, cls.MIN_POOL_SIZE)

    # ================================================================
    # PREVENT INSTANTIATION - Use class attributes directly
    # ================================================================

    def __init__(self) -> None:
        """Prevent instantiation of FlextDbOracleConstants.

        This class should not be instantiated. Use class attributes directly.

        Raises:
            TypeError: Always raised to prevent instantiation

        """
        msg = (
            "FlextDbOracleConstants should not be instantiated - "
            "use class attributes directly"
        )
        raise TypeError(msg)


# ==================================================================
# EXPORTS - Clean public API
# ==================================================================

__all__ = [
    # Enums
    "FlextDbOracleAuthMode",
    "FlextDbOracleConnectionProtocol",
    # Main constants class - PRIMARY INTERFACE
    "FlextDbOracleConstants",
    "FlextDbOracleDataType",
    "FlextDbOracleIsolationLevel",
    "FlextDbOraclePoolStrategy",
]

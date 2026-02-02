"""Oracle database constants following unified class pattern.

This module provides Oracle-specific constants organized into nested classes
for connection configuration, query operations, data types, validation rules,
error messages, and performance tuning.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar, Final

from flext_core.constants import FlextConstants, c as c_core


class FlextDbOracleConstants(FlextConstants):
    """Oracle database constants extending FlextConstants foundation.

    Usage:
    ```python
    from flext_db_oracle.constants import FlextDbOracleConstants

    port = FlextDbOracleConstants.DbOracle.Connection.DEFAULT_PORT
    query = FlextDbOracleConstants.DbOracle.Query.TEST_QUERY
    ```
    """

    class DbOracle:
        """Oracle database domain constants namespace.

        All Oracle-specific constants are organized here for better namespace
        organization and to enable composition with other domain constants.
        """

        class Connection:
            """Oracle connection configuration constants."""

            DEFAULT_CHARSET: Final[str] = "UTF8"
            DEFAULT_SERVICE_NAME: Final[str] = "XEPDB1"
            DEFAULT_PORT: Final[int] = 1521
            DEFAULT_DATABASE_NAME: Final[str] = "XE"
            DEFAULT_SID: Final[str] = "XE"
            DEFAULT_USERNAME: Final[str] = "system"
            DEFAULT_TIMEOUT: Final[int] = 30

            DEFAULT_POOL_INCREMENT: Final[int] = 1
            DEFAULT_POOL_MIN: Final[int] = 2
            DEFAULT_POOL_MAX: Final[int] = 20
            DEFAULT_POOL_TIMEOUT: Final[int] = 60
            DEFAULT_CONNECTION_TIMEOUT: Final[int] = 30

        class Error:
            """Oracle error handling constants."""

            MAX_ERROR_MESSAGE_LENGTH: Final[int] = 500
            MAX_STACK_TRACE_LENGTH: Final[int] = 2000
            DEFAULT_ERROR_CODE: Final[str] = "ORA-99999"

        class OracleNetwork:
            """Oracle-specific network configuration constants."""

            MIN_PORT: Final[int] = 1
            MAX_PORT: Final[int] = 65535
            DEFAULT_PORT: Final[int] = 1521
            DEFAULT_LISTENER_PORT: Final[int] = 1521
            DEFAULT_SSL_PORT: Final[int] = 2484

        class Query:
            """Oracle query and operation constants."""

            TEST_QUERY: Final[str] = "SELECT 1 FROM DUAL"
            DUAL_TABLE: Final[str] = "DUAL"
            DEFAULT_ARRAY_SIZE: Final[int] = 100
            DEFAULT_QUERY_LIMIT: Final[int] = 1000
            DEFAULT_QUERY_TIMEOUT: Final[int] = 60
            MAX_QUERY_TIMEOUT: Final[int] = 3600  # Maximum query timeout (1 hour)
            MAX_QUERY_ROWS: Final[int] = 100000  # Maximum rows per query

        class DataTypes:
            """Oracle data type constants and mappings."""

            # Oracle native types
            DATE_TYPE: Final[str] = "DATE"
            TIMESTAMP_TYPE: Final[str] = "TIMESTAMP"
            DEFAULT_VARCHAR_TYPE: Final[str] = "VARCHAR2(4000)"
            CLOB_TYPE: Final[str] = "CLOB"
            BLOB_TYPE: Final[str] = "BLOB"
            NUMBER_TYPE: Final[str] = "NUMBER"
            INTEGER_TYPE: Final[str] = "NUMBER(38)"
            BOOLEAN_TYPE: Final[str] = "NUMBER(1)"

            # Singer to Oracle type mapping
            SINGER_TYPE_MAP: ClassVar[dict[str, str]] = {
                "string": "VARCHAR2(4000)",
                "integer": "NUMBER(38)",
                "number": "NUMBER",
                "boolean": "NUMBER(1)",
                "array": "CLOB",
                "object": "CLOB",
                "date-time": "TIMESTAMP",
                "date": "DATE",
                "time": "TIMESTAMP",
            }

        class OracleValidation:
            """Oracle-specific validation limits and patterns."""

            # Oracle identifier limits
            MAX_ORACLE_IDENTIFIER_LENGTH: Final[int] = 30
            MAX_IDENTIFIER_LENGTH: Final[int] = 128
            MAX_TABLE_NAME_LENGTH: Final[int] = 128
            MAX_COLUMN_NAME_LENGTH: Final[int] = 128
            MAX_SCHEMA_NAME_LENGTH: Final[int] = 128
            MAX_USERNAME_LENGTH: Final[int] = 128
            MAX_SERVICE_NAME_LENGTH: Final[int] = 128
            MAX_HOSTNAME_LENGTH: Final[int] = 253
            MAX_VARCHAR_LENGTH: Final[int] = 4000

            # Field validation
            MIN_COLUMN_FIELDS: Final[int] = (
                4  # Required fields: "name", type, length, nullable
            )
            COLUMN_METADATA_FIELD_COUNT: Final[int] = (
                7  # Complete metadata fields count
            )

            # Oracle naming patterns
            ORACLE_IDENTIFIER_PATTERN: Final[str] = r"^[A-Z][A-Z0-9_$#]*$"
            IDENTIFIER_PATTERN: Final[str] = r"^[A-Za-z][A-Za-z0-9_$#]*$"
            SCHEMA_PATTERN: Final[str] = r"^[A-Za-z][A-Za-z0-9_$#]*$"

            # Oracle reserved words
            ORACLE_RESERVED: Final[frozenset[str]] = frozenset({
                "SELECT",
                "FROM",
                "WHERE",
                "INSERT",
                "UPDATE",
                "DELETE",
                "CREATE",
                "DROP",
                "ALTER",
                "TABLE",
                "INDEX",
                "VIEW",
                "PROCEDURE",
                "FUNCTION",
                "TRIGGER",
                "SEQUENCE",
                "PACKAGE",
                "CONSTRAINT",
                "PRIMARY",
                "FOREIGN",
                "KEY",
                "UNIQUE",
                "NOT",
                "NULL",
                "CHECK",
                "DEFAULT",
                "REFERENCES",
                "ON",
                "CASCADE",
                "RESTRICT",
                "SET",
                "COMMIT",
                "ROLLBACK",
                "SAVEPOINT",
            })

            # SQL keywords for validation
            SQL_KEYWORDS: Final[frozenset[str]] = frozenset({
                "SELECT",
                "FROM",
                "WHERE",
                "JOIN",
                "INNER",
                "LEFT",
                "RIGHT",
                "OUTER",
                "ON",
                "GROUP",
                "BY",
                "HAVING",
                "ORDER",
                "ASC",
                "DESC",
                "LIMIT",
                "OFFSET",
                "UNION",
                "ALL",
                "DISTINCT",
            })

        class ErrorMessages:
            """Oracle-specific error messages."""

            HOST_EMPTY: Final[str] = "Host cannot be empty"
            USERNAME_EMPTY: Final[str] = "Username cannot be empty"
            COLUMN_NAME_EMPTY: Final[str] = "Column name cannot be empty"
            DATA_TYPE_EMPTY: Final[str] = "Data type cannot be empty"
            TABLE_NAME_EMPTY: Final[str] = "Table name cannot be empty"
            SCHEMA_NAME_EMPTY: Final[str] = "Schema name cannot be empty"
            POSITION_INVALID: Final[str] = "Position must be positive"
            COLUMN_ID_INVALID: Final[str] = "Column ID must be positive"
            PORT_INVALID: Final[str] = "Invalid port number"
            CONNECTION_FAILED: Final[str] = "Failed to connect to Oracle database"
            QUERY_EXECUTION_FAILED: Final[str] = "Query execution failed"
            IDENTIFIER_TOO_LONG: Final[str] = (
                "Oracle identifier too long (max {max_length} chars)"
            )
            IDENTIFIER_INVALID_PATTERN: Final[str] = (
                "Oracle identifier does not match required pattern"
            )
            IDENTIFIER_RESERVED_WORD: Final[str] = (
                "Oracle identifier is a reserved word"
            )
            HOST_TOO_LONG: Final[str] = "Host too long (max {max_length} chars)"
            PORT_OUT_OF_RANGE: Final[str] = (
                "Port must be between {min_port}-{max_port}, got {port}"
            )
            QUERY_TIMEOUT_TOO_HIGH: Final[str] = (
                "Query timeout too high (max {max_timeout} seconds)"
            )

        class OraclePerformance:
            """Oracle-specific performance tuning constants."""

            DEFAULT_COMMIT_SIZE: Final[int] = 1000
            PERFORMANCE_WARNING_THRESHOLD_SECONDS: Final[float] = 5.0
            MAX_DISPLAY_ROWS: Final[int] = 1000
            MILLISECONDS_TO_SECONDS_THRESHOLD: Final[int] = 1000
            DEFAULT_BATCH_SIZE: Final[int] = (
                c_core.Performance.BatchProcessing.DEFAULT_SIZE
            )  # Reference FlextConstants
            MAX_BATCH_SIZE: Final[int] = (
                c_core.Performance.BatchProcessing.MAX_ITEMS
            )  # Reference FlextConstants
            DEFAULT_POOL_RECYCLE: Final[int] = 3600  # 1 hour

            # Performance thresholds for connection health
            CONNECTION_IDLE_TIMEOUT_SECONDS: Final[int] = 3600  # 1 hour
            CONNECTION_EXCELLENT_THRESHOLD_SECONDS: Final[float] = 0.1
            CONNECTION_GOOD_THRESHOLD_SECONDS: Final[float] = 0.5
            CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS: Final[float] = 2.0

            # Query performance thresholds
            QUERY_EXCELLENT_THRESHOLD_MS: Final[int] = 100
            QUERY_GOOD_THRESHOLD_MS: Final[int] = 500
            QUERY_ACCEPTABLE_THRESHOLD_MS: Final[int] = 2000

            # Data size estimation factor (bytes per cell)
            DATA_SIZE_ESTIMATION_FACTOR: Final[int] = 50

            # Oracle hints
            INDEX_HINT: Final[str] = "/*+ INDEX */"
            FULL_HINT: Final[str] = "/*+ FULL */"
            PARALLEL_HINT: Final[str] = "/*+ PARALLEL */"

        class IsolationLevels:
            """Oracle transaction isolation levels."""

            READ_UNCOMMITTED: Final[str] = "READ_UNCOMMITTED"
            READ_COMMITTED: Final[str] = "READ_COMMITTED"
            REPEATABLE_READ: Final[str] = "REPEATABLE_READ"
            SERIALIZABLE: Final[str] = "SERIALIZABLE"

            VALID_LEVELS: Final[list[str]] = [
                READ_UNCOMMITTED,
                READ_COMMITTED,
                REPEATABLE_READ,
                SERIALIZABLE,
            ]

        class OracleEnvironment:
            """Oracle-specific environment variable names and defaults."""

            # Environment variable prefixes
            PREFIX_ORACLE: Final[str] = "ORACLE_"
            PREFIX_FLEXT_TARGET_ORACLE: Final[str] = "FLEXT_TARGET_ORACLE_"

            # Environment variable names
            ENV_HOST: Final[str] = "ORACLE_HOST"
            ENV_PORT: Final[str] = "ORACLE_PORT"
            ENV_USERNAME: Final[str] = "ORACLE_USERNAME"
            ENV_PASSWORD: Final[str] = "ORACLE_PASSWORD"
            ENV_SERVICE_NAME: Final[str] = "ORACLE_SERVICE_NAME"
            ENV_DATABASE_NAME: Final[str] = "ORACLE_DATABASE_NAME"
            ENV_SID: Final[str] = "ORACLE_SID"

            # Environment variable mapping
            ENV_MAPPING: ClassVar[dict[str, str]] = {
                "FLEXT_TARGET_ORACLE_HOST": "host",
                "ORACLE_HOST": "host",
                "FLEXT_TARGET_ORACLE_PORT": "port",
                "ORACLE_PORT": "port",
                "FLEXT_TARGET_ORACLE_SERVICE_NAME": "service_name",
                "ORACLE_SERVICE_NAME": "service_name",
                "FLEXT_TARGET_ORACLE_USERNAME": "username",
                "ORACLE_USERNAME": "username",
                "FLEXT_TARGET_ORACLE_PASSWORD": "password",
                "ORACLE_PASSWORD": "password",
            }

        class OracleDefaults:
            """Oracle-specific default configuration values."""

            # Connection defaults
            DEFAULT_HOST: Final[str] = "localhost"
            DEFAULT_PORT: Final[int] = 1521
            DEFAULT_USERNAME: Final[str] = "system"
            DEFAULT_SERVICE_NAME: Final[str] = "XEPDB1"
            DEFAULT_DATABASE_NAME: Final[str] = "XE"
            DEFAULT_SID: Final[str] = "XE"

            # Pool defaults
            DEFAULT_POOL_MIN: Final[int] = 2
            DEFAULT_POOL_MAX: Final[int] = 20
            DEFAULT_POOL_TIMEOUT: Final[int] = 60
            DEFAULT_CONNECTION_TIMEOUT: Final[int] = (
                c_core.Network.DEFAULT_TIMEOUT
            )  # Reference FlextConstants

            # Query defaults
            DEFAULT_QUERY_TIMEOUT: Final[int] = 60
            DEFAULT_QUERY_LIMIT: Final[int] = 1000
            DEFAULT_BATCH_SIZE: Final[int] = (
                c_core.Performance.BatchProcessing.DEFAULT_SIZE
            )  # Reference FlextConstants

            # Performance defaults
            DEFAULT_COMMIT_SIZE: Final[int] = 1000
            DEFAULT_POOL_RECYCLE: Final[int] = 3600
            DEFAULT_SLOW_QUERY_THRESHOLD: Final[float] = 2.0

        # NOTE: FeatureFlags class moved to utilities.py
        # Use: u.Oracle.FeatureFlags.dispatcher_enabled()

        class OracleEnums:
            """Oracle-specific enumerations."""

            class ConnectionType(StrEnum):
                """Oracle connection types.

                DRY Pattern:
                    StrEnum is the single source of truth. Use ConnectionType.SERVICE_NAME.value
                    or ConnectionType.SERVICE_NAME directly - no base strings needed.
                """

                SERVICE_NAME = "service_name"
                SID = "sid"
                TNS = "tns"

            class QueryType(StrEnum):
                """Oracle query types.

                DRY Pattern:
                    StrEnum is the single source of truth. Use QueryType.SELECT.value
                    or QueryType.SELECT directly - no base strings needed.
                """

                SELECT = "SELECT"
                INSERT = "INSERT"
                UPDATE = "UPDATE"
                DELETE = "DELETE"
                CREATE = "CREATE"
                DROP = "DROP"
                ALTER = "ALTER"

            class DataType(StrEnum):
                """Oracle data types.

                DRY Pattern:
                    StrEnum is the single source of truth. Use DataType.VARCHAR2.value
                    or DataType.VARCHAR2 directly - no base strings needed.
                """

                VARCHAR2 = "VARCHAR2"
                NUMBER = "NUMBER"
                DATE = "DATE"
                TIMESTAMP = "TIMESTAMP"
                CLOB = "CLOB"
                BLOB = "BLOB"
                CHAR = "CHAR"
                RAW = "RAW"

        # ═══════════════════════════════════════════════════════════════════
        # LITERAL TYPES: PEP 695 strict type aliases (Python 3.13+)
        # ═══════════════════════════════════════════════════════════════════
        # Literal types moved to typings.py (t.* namespace) - NO string duplication!
        # Access via: t.ConnectionTypeLiteral, t.QueryTypeLiteral, t.DataTypeLiteral

        class Literals:
            """Type-safe string literals for Oracle operations (deprecated - use direct access).

            Python 3.13+ best practice: Use type keyword for type aliases.
            All Literal types are now at DbOracle level for direct access.
            Use: c.DbOracle.ConnectionTypeLiteral (not c.DbOracle.Literals.ConnectionTypeLiteral)
            """

            # Environment literals - reuse from flext-core Settings.Environment StrEnum
            type EnvironmentLiteral = c_core.Settings.Environment
            """Environment type literal - references flext-core Settings.Environment StrEnum."""

            # Log level literals - reuse from flext-core Settings.LogLevel StrEnum
            type LogLevelLiteral = c_core.Settings.LogLevel
            """Log level literal - references flext-core Settings.LogLevel StrEnum."""

        class Lists:
            """Lists of constants for validation and iteration.

            NOTE: VALID_DATA_TYPES, VALID_CONNECTION_TYPES, and VALID_QUERY_TYPES values
            MUST match OracleEnums.DataType, OracleEnums.ConnectionType, and
            OracleEnums.QueryType StrEnum values exactly.

            DRY Pattern: To avoid duplication, prefer using OracleEnums.DataType.VARCHAR2.value
            or OracleEnums.DataType.VARCHAR2 directly instead of Lists.VALID_DATA_TYPES.
            These lists are kept for backward compatibility and validation convenience.
            """

            # NOTE: Values must match OracleEnums.DataType StrEnum exactly!
            # Valid Oracle data types - matches DataType StrEnum values
            VALID_DATA_TYPES: Final[list[str]] = [
                "VARCHAR2",  # Matches OracleEnums.DataType.VARCHAR2
                "NUMBER",  # Matches OracleEnums.DataType.NUMBER
                "DATE",  # Matches OracleEnums.DataType.DATE
                "TIMESTAMP",  # Matches OracleEnums.DataType.TIMESTAMP
                "CLOB",  # Matches OracleEnums.DataType.CLOB
                "BLOB",  # Matches OracleEnums.DataType.BLOB
                "CHAR",  # Matches OracleEnums.DataType.CHAR
                "RAW",  # Matches OracleEnums.DataType.RAW
            ]
            """Valid Oracle data types - matches DataType StrEnum values."""

            # NOTE: Values must match OracleEnums.ConnectionType StrEnum exactly!
            # Valid connection types - matches ConnectionType StrEnum values
            VALID_CONNECTION_TYPES: Final[list[str]] = [
                "service_name",  # Matches OracleEnums.ConnectionType.SERVICE_NAME
                "sid",  # Matches OracleEnums.ConnectionType.SID
                "tns",  # Matches OracleEnums.ConnectionType.TNS
            ]
            """Valid connection types - matches ConnectionType StrEnum values."""

            # NOTE: Values must match OracleEnums.QueryType StrEnum exactly!
            # Valid query types - matches QueryType StrEnum values
            VALID_QUERY_TYPES: Final[list[str]] = [
                "SELECT",  # Matches OracleEnums.QueryType.SELECT
                "INSERT",  # Matches OracleEnums.QueryType.INSERT
                "UPDATE",  # Matches OracleEnums.QueryType.UPDATE
                "DELETE",  # Matches OracleEnums.QueryType.DELETE
                "CREATE",  # Matches OracleEnums.QueryType.CREATE
                "DROP",  # Matches OracleEnums.QueryType.DROP
                "ALTER",  # Matches OracleEnums.QueryType.ALTER
            ]
            """Valid query types - matches QueryType StrEnum values."""

            # Valid isolation levels
            VALID_ISOLATION_LEVELS: Final[list[str]] = [
                "READ_UNCOMMITTED",
                "READ_COMMITTED",
                "REPEATABLE_READ",
                "SERIALIZABLE",
            ]

            # Oracle system users to exclude
            SYSTEM_USERS: Final[list[str]] = [
                "SYS",
                "SYSTEM",
                "ANONYMOUS",
                "XDB",
                "CTXSYS",
                "MDSYS",
                "WMSYS",
            ]

            # Default schema names
            DEFAULT_SCHEMAS: Final[list[str]] = [
                "SYSTEM",
                "SYS",
                "PUBLIC",
                "USER",
            ]

        class Platform(c_core.Platform):
            """Oracle-specific platform constants extending base Platform."""

            # Network constants
            LOOPBACK_IP: Final[str] = "127.0.0.1"
            LOCALHOST_IP: Final[str] = "127.0.0.1"

            # HTTP methods
            HTTP_METHOD_DELETE: Final[str] = "DELETE"
            HTTP_METHOD_GET: Final[str] = "GET"
            HTTP_METHOD_POST: Final[str] = "POST"
            HTTP_METHOD_PUT: Final[str] = "PUT"
            HTTP_METHOD_PATCH: Final[str] = "PATCH"


# No compatibility aliases - use direct imports only

c = FlextDbOracleConstants

__all__: list[str] = [
    "FlextDbOracleConstants",
    "c",
]

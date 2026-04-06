"""Oracle database constants following unified class pattern.

This module provides Oracle-specific constants organized into nested classes
for connection configuration, query operations, data types, validation rules,
error messages, and performance tuning.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum, unique
from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar, Final

from flext_cli import c as _cli_c

from flext_core import FlextConstants

if TYPE_CHECKING:
    from flext_db_oracle import t


class FlextDbOracleConstants(_cli_c):
    """Oracle database constants extending FlextConstants foundation.

    Usage:
    ```python
    from flext_db_oracle import FlextDbOracleConstants

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
            DEFAULT_TIMEOUT: Final[int] = FlextConstants.DEFAULT_TIMEOUT_SECONDS
            DEFAULT_POOL_MIN: Final[int] = 2
            DEFAULT_POOL_MAX: Final[int] = 20
            DEFAULT_POOL_INCREMENT: Final[int] = 1
            DEFAULT_POOL_TIMEOUT: Final[int] = 60
            DEFAULT_CONNECTION_TIMEOUT: Final[int] = 30

        class Error:
            """Oracle error handling constants."""

            MAX_ERROR_MESSAGE_LENGTH: Final[int] = 500

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
            MAX_QUERY_TIMEOUT: Final[int] = 3600
            MAX_QUERY_ROWS: Final[int] = 100000

        class DataTypes:
            """Oracle data type constants and mappings."""

            DATE_TYPE: Final[str] = "DATE"
            TIMESTAMP_TYPE: Final[str] = "TIMESTAMP"
            DEFAULT_VARCHAR_TYPE: Final[str] = "VARCHAR2(4000)"
            CLOB_TYPE: Final[str] = "CLOB"
            BLOB_TYPE: Final[str] = "BLOB"
            NUMBER_TYPE: Final[str] = "NUMBER"
            INTEGER_TYPE: Final[str] = "NUMBER(38)"
            BOOLEAN_TYPE: Final[str] = "NUMBER(1)"

            SINGER_TYPE_MAP: ClassVar[t.StrMapping] = MappingProxyType({
                "string": "VARCHAR2(4000)",
                "integer": "NUMBER(38)",
                "number": "NUMBER",
                "boolean": "NUMBER(1)",
                "array": "CLOB",
                "t.NormalizedValue": "CLOB",
                "date-time": "TIMESTAMP",
                "date": "DATE",
                "time": "TIMESTAMP",
            })

        class OracleValidation:
            """Oracle-specific validation limits and patterns."""

            MAX_ORACLE_IDENTIFIER_LENGTH: Final[int] = 30
            MAX_IDENTIFIER_LENGTH: Final[int] = 128
            MAX_TABLE_NAME_LENGTH: Final[int] = 128
            MAX_COLUMN_NAME_LENGTH: Final[int] = 128
            MAX_SCHEMA_NAME_LENGTH: Final[int] = 128
            MAX_USERNAME_LENGTH: Final[int] = 128
            MAX_SERVICE_NAME_LENGTH: Final[int] = 128
            MAX_HOSTNAME_LENGTH: Final[int] = 253
            MAX_VARCHAR_LENGTH: Final[int] = 4000
            MIN_COLUMN_FIELDS: Final[int] = 4
            COLUMN_METADATA_FIELD_COUNT: Final[int] = 7
            ORACLE_IDENTIFIER_PATTERN: Final[str] = "^[A-Z][A-Z0-9_$#]*$"
            IDENTIFIER_PATTERN: Final[str] = "^[A-Za-z][A-Za-z0-9_$#]*$"
            SCHEMA_PATTERN: Final[str] = "^[A-Za-z][A-Za-z0-9_$#]*$"
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
            SQL_KEYWORDS: Final[frozenset[str]] = frozenset({
                "SELECT",
                "FROM",
                "WHERE",
                "INSERT",
                "UPDATE",
                "DELETE",
                "CREATE",
                "DROP",
                "ALTER",
                "JOIN",
                "LEFT",
                "RIGHT",
                "INNER",
                "OUTER",
                "ON",
                "ORDER",
                "GROUP",
                "BY",
                "HAVING",
                "UNION",
                "INTERSECT",
                "MINUS",
                "DISTINCT",
                "AS",
                "AND",
                "OR",
                "NOT",
                "IN",
                "EXISTS",
                "BETWEEN",
                "LIKE",
                "IS",
                "NULL",
                "CASE",
                "WHEN",
                "THEN",
                "ELSE",
                "END",
                "WITH",
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
            IDENTIFIER_TOO_LONG: Final[str] = "Identifier exceeds max_length characters"
            IDENTIFIER_INVALID_PATTERN: Final[str] = (
                "Identifier does not match required pattern"
            )
            IDENTIFIER_RESERVED_WORD: Final[str] = "Identifier is a reserved word"
            HOST_TOO_LONG: Final[str] = "Host is too long"
            PORT_OUT_OF_RANGE: Final[str] = (
                "Port must be between {min_port}-{max_port}, got {port}"
            )
            QUERY_TIMEOUT_TOO_HIGH: Final[str] = "Query timeout is too high"

        class OraclePerformance:
            """Oracle-specific performance tuning constants."""

            MILLISECONDS_TO_SECONDS_THRESHOLD: Final[int] = 1000
            DEFAULT_BATCH_SIZE: Final[int] = FlextConstants.DEFAULT_SIZE
            MAX_BATCH_SIZE: Final[int] = (
                FlextConstants.DEFAULT_MAX_COMMAND_RETRIES or 1000
            )
            DEFAULT_COMMIT_SIZE: Final[int] = 1000
            PERFORMANCE_WARNING_THRESHOLD_SECONDS: Final[float] = 5.0
            MAX_DISPLAY_ROWS: Final[int] = 1000
            DEFAULT_POOL_RECYCLE: Final[int] = 3600
            CONNECTION_IDLE_TIMEOUT_SECONDS: Final[int] = 3600
            DATA_SIZE_ESTIMATION_FACTOR: Final[int] = 50
            CONNECTION_EXCELLENT_THRESHOLD_SECONDS: Final[float] = 0.1
            CONNECTION_GOOD_THRESHOLD_SECONDS: Final[float] = 0.5
            CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS: Final[float] = 2.0
            QUERY_EXCELLENT_THRESHOLD_MS: Final[int] = 100
            QUERY_GOOD_THRESHOLD_MS: Final[int] = 500
            QUERY_ACCEPTABLE_THRESHOLD_MS: Final[int] = 2000
            INDEX_HINT: Final[str] = "/*+ INDEX */"
            FULL_HINT: Final[str] = "/*+ FULL */"
            PARALLEL_HINT: Final[str] = "/*+ PARALLEL */"

        class IsolationLevels:
            """Oracle transaction isolation levels."""

            READ_UNCOMMITTED: Final[str] = "READ_UNCOMMITTED"
            READ_COMMITTED: Final[str] = "READ_COMMITTED"
            REPEATABLE_READ: Final[str] = "REPEATABLE_READ"
            SERIALIZABLE: Final[str] = "SERIALIZABLE"
            VALID_LEVELS: Final[t.StrSequence] = (
                "READ_UNCOMMITTED",
                "READ_COMMITTED",
                "REPEATABLE_READ",
                "SERIALIZABLE",
            )

        class OracleEnvironment:
            """Oracle-specific environment variable names and defaults."""

            PREFIX_ORACLE: Final[str] = "ORACLE_"
            PREFIX_FLEXT_TARGET_ORACLE: Final[str] = "FLEXT_TARGET_ORACLE_"
            ENV_HOST: Final[str] = "ORACLE_HOST"
            ENV_PORT: Final[str] = "ORACLE_PORT"
            ENV_USERNAME: Final[str] = "ORACLE_USERNAME"
            ENV_PASSWORD: Final[str] = "ORACLE_PASSWORD"
            ENV_SERVICE_NAME: Final[str] = "ORACLE_SERVICE_NAME"
            ENV_DATABASE_NAME: Final[str] = "ORACLE_DATABASE_NAME"
            ENV_SID: Final[str] = "ORACLE_SID"
            ENV_ENABLE_DISPATCHER: Final[str] = "FLEXT_DB_ORACLE_ENABLE_DISPATCHER"
            ENV_MAPPING: ClassVar[t.StrMapping] = MappingProxyType({
                "FLEXT_TARGET_ORACLE_HOST": "host",
                "ORACLE_HOST": "host",
                "FLEXT_TARGET_ORACLE_PORT": "port",
                "ORACLE_PORT": "port",
                "FLEXT_TARGET_ORACLE_SERVICE_NAME": "service_name",
                "ORACLE_SERVICE_NAME": "service_name",
                "FLEXT_TARGET_ORACLE_USERNAME": "username",
                "ORACLE_USERNAME": "username",
                "FLEXT_TARGET_ORACLE_PASSWORD": "password",  # nosec B105
                "ORACLE_PASSWORD": "password",  # nosec B105
                "FLEXT_TARGET_ORACLE_DATABASE_NAME": "name",
                "ORACLE_DATABASE_NAME": "name",
            })

        class OracleDefaults:
            """Oracle-specific default configuration values."""

            DEFAULT_HOST: Final[str] = FlextConstants.LOCALHOST
            DEFAULT_PORT: Final[int] = 1521
            DEFAULT_USERNAME: Final[str] = "system"
            DEFAULT_SERVICE_NAME: Final[str] = "XEPDB1"
            DEFAULT_DATABASE_NAME: Final[str] = "XE"
            DEFAULT_SID: Final[str] = "XE"
            DEFAULT_POOL_MIN: Final[int] = 2
            DEFAULT_POOL_MAX: Final[int] = 20
            DEFAULT_POOL_TIMEOUT: Final[int] = 60
            DEFAULT_QUERY_TIMEOUT: Final[int] = 60
            DEFAULT_QUERY_LIMIT: Final[int] = 1000
            DEFAULT_COMMIT_SIZE: Final[int] = 1000
            DEFAULT_POOL_RECYCLE: Final[int] = 3600
            DEFAULT_SLOW_QUERY_THRESHOLD: Final[float] = 2.0
            DEFAULT_BATCH_SIZE: Final[int] = FlextConstants.DEFAULT_SIZE

        class OracleEnums:
            """Oracle-specific enumerations."""

            @unique
            class ConnectionType(StrEnum):
                """Oracle connection types.

                DRY Pattern:
                    StrEnum is the single source of truth. Use ConnectionType.SERVICE_NAME.value
                    or ConnectionType.SERVICE_NAME directly - no base strings needed.
                """

                SERVICE_NAME = "service_name"
                SID = "sid"
                TNS = "tns"

            @unique
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

            @unique
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

        class Literals:
            """Type-safe string literals for Oracle operations (deprecated - use direct access).

            Python 3.13+ best practice: Use type keyword for type aliases.
            All Literal types are now at DbOracle level for direct access.
            Use: c.DbOracle.ConnectionTypeLiteral (not c.DbOracle.Literals.ConnectionTypeLiteral)
            """

        class Lists:
            """Lists of constants for validation and iteration.

            NOTE: VALID_DATA_TYPES, VALID_CONNECTION_TYPES, and VALID_QUERY_TYPES values
            MUST match OracleEnums.DataType, OracleEnums.ConnectionType, and
            OracleEnums.QueryType StrEnum values exactly.

            DRY Pattern: To avoid duplication, prefer using OracleEnums.DataType.VARCHAR2.value
            or OracleEnums.DataType.VARCHAR2 directly instead of Lists.VALID_DATA_TYPES.
            These lists are kept for backward compatibility and validation convenience.
            """

            VALID_DATA_TYPES: Final[t.StrSequence] = (
                "VARCHAR2",
                "NUMBER",
                "DATE",
                "TIMESTAMP",
                "CLOB",
                "BLOB",
                "CHAR",
                "RAW",
            )
            VALID_CONNECTION_TYPES: Final[t.StrSequence] = (
                "service_name",
                "sid",
                "tns",
            )
            VALID_QUERY_TYPES: Final[t.StrSequence] = (
                "SELECT",
                "INSERT",
                "UPDATE",
                "DELETE",
                "CREATE",
                "DROP",
                "ALTER",
            )
            VALID_ISOLATION_LEVELS: Final[t.StrSequence] = (
                "READ_UNCOMMITTED",
                "READ_COMMITTED",
                "REPEATABLE_READ",
                "SERIALIZABLE",
            )
            SYSTEM_USERS: Final[t.StrSequence] = (
                "SYS",
                "SYSTEM",
                "XDB",
                "DBSNMP",
                "OUTLN",
            )
            DEFAULT_SCHEMAS: Final[t.StrSequence] = (
                "SYSTEM",
                "SYS",
                "PUBLIC",
            )

        class FeatureFlags:
            """Internal feature flags for the connection pool."""

        class Platform:
            """Oracle-specific platform constants."""

            LOCALHOST_IP: Final[str] = "127.0.0.1"
            LOOPBACK_IP: Final[str] = "127.0.0.1"

        ConnectionTypeLiteral: Final = tuple(Lists.VALID_CONNECTION_TYPES)
        QueryTypeLiteral: Final = tuple(Lists.VALID_QUERY_TYPES)
        DataTypeLiteral: Final = tuple(Lists.VALID_DATA_TYPES)

        @unique
        class ProjectType(StrEnum):
            """Project type literals for package metadata."""

            LIBRARY = "library"
            APPLICATION = "application"
            SERVICE = "service"
            ORACLE_SERVICE = "oracle-service"
            DATABASE_SERVICE = "database-service"
            DATA_WAREHOUSE = "data-warehouse"
            ETL_SERVICE = "etl-service"
            ORACLE_CLIENT = "oracle-client"
            DB_MIGRATION = "db-migration"
            SCHEMA_MANAGER = "schema-manager"
            DATA_PIPELINE = "data-pipeline"
            ORACLE_API = "oracle-api"
            DATABASE_API = "database-api"
            SQL_SERVICE = "sql-service"
            DATA_CONNECTOR = "data-connector"


c = FlextDbOracleConstants

__all__: t.StrSequence = ["FlextDbOracleConstants", "c"]

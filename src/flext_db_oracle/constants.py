"""Oracle database constants following unified class pattern.

This module provides Oracle-specific constants organized into nested classes
for connection configuration, query operations, data types, validation rules,
error messages, and performance tuning.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum, unique
from typing import ClassVar, Final

from flext_core import FlextConstants, c as core_c


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

            DEFAULT_SERVICE_NAME: Final[str] = "XEPDB1"
            DEFAULT_PORT: Final[int] = 1521
            DEFAULT_DATABASE_NAME: Final[str] = "XE"
            DEFAULT_USERNAME: Final[str] = "system"
            DEFAULT_TIMEOUT: Final[int] = core_c.DEFAULT_TIMEOUT_SECONDS
            DEFAULT_POOL_MIN: Final[int] = 2
            DEFAULT_POOL_MAX: Final[int] = 20

        class Error:
            """Oracle error handling constants."""

            MAX_ERROR_MESSAGE_LENGTH: Final[int] = 500

        class OracleNetwork:
            """Oracle-specific network configuration constants."""

            MIN_PORT: Final[int] = 1
            MAX_PORT: Final[int] = 65535
            DEFAULT_PORT: Final[int] = 1521

        class Query:
            """Oracle query and operation constants."""

        class DataTypes:
            """Oracle data type constants and mappings."""

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

            MAX_ORACLE_IDENTIFIER_LENGTH: Final[int] = 30
            MAX_IDENTIFIER_LENGTH: Final[int] = 128
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

        class ErrorMessages:
            """Oracle-specific error messages."""

            HOST_EMPTY: Final[str] = "Host cannot be empty"
            USERNAME_EMPTY: Final[str] = "Username cannot be empty"
            PORT_OUT_OF_RANGE: Final[str] = (
                "Port must be between {min_port}-{max_port}, got {port}"
            )

        class OraclePerformance:
            """Oracle-specific performance tuning constants."""

            MILLISECONDS_TO_SECONDS_THRESHOLD: Final[int] = 1000
            DEFAULT_BATCH_SIZE: Final[int] = core_c.DEFAULT_BATCH_SIZE or core_c.DEFAULT_SIZE
            MAX_BATCH_SIZE: Final[int] = core_c.DEFAULT_MAX_COMMAND_RETRIES or 1000
            CONNECTION_IDLE_TIMEOUT_SECONDS: Final[int] = 3600
            DATA_SIZE_ESTIMATION_FACTOR: Final[int] = 50

        class IsolationLevels:
            """Oracle transaction isolation levels."""

        class OracleEnvironment:
            """Oracle-specific environment variable names and defaults."""

            PREFIX_ORACLE: Final[str] = "ORACLE_"
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

            DEFAULT_HOST: Final[str] = core_c.LOCALHOST
            DEFAULT_PORT: Final[int] = 1521
            DEFAULT_USERNAME: Final[str] = "system"
            DEFAULT_SERVICE_NAME: Final[str] = "XEPDB1"
            DEFAULT_DATABASE_NAME: Final[str] = "XE"
            DEFAULT_POOL_MIN: Final[int] = 2
            DEFAULT_POOL_MAX: Final[int] = 20
            DEFAULT_BATCH_SIZE: Final[int] = core_c.DEFAULT_BATCH_SIZE or core_c.DEFAULT_SIZE

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

            EnvironmentLiteral = FlextConstants.Environment
            LogLevelLiteral = FlextConstants.LogLevel

        class Lists:
            """Lists of constants for validation and iteration.

            NOTE: VALID_DATA_TYPES, VALID_CONNECTION_TYPES, and VALID_QUERY_TYPES values
            MUST match OracleEnums.DataType, OracleEnums.ConnectionType, and
            OracleEnums.QueryType StrEnum values exactly.

            DRY Pattern: To avoid duplication, prefer using OracleEnums.DataType.VARCHAR2.value
            or OracleEnums.DataType.VARCHAR2 directly instead of Lists.VALID_DATA_TYPES.
            These lists are kept for backward compatibility and validation convenience.
            """

            "Valid Oracle data types - matches DataType StrEnum values."
            VALID_CONNECTION_TYPES: Final[list[str]] = ["service_name", "sid", "tns"]
            "Valid connection types - matches ConnectionType StrEnum values."
            "Valid query types - matches QueryType StrEnum values."

        class FeatureFlags:
            """Internal feature flags for the connection pool."""

        class Platform:
            """Oracle-specific platform constants."""

            LOCALHOST_IP: Final[str] = "127.0.0.1"

    class Platform(DbOracle.Platform):
        """Compatibility alias for platform constants at root namespace."""

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

    @unique
    class ConnectionTypeLiteral(StrEnum):
        """Oracle connection type literals."""

        SERVICE_NAME = "service_name"
        SID = "sid"
        TNS = "tns"

    @unique
    class QueryTypeLiteral(StrEnum):
        """Oracle SQL query type literals."""

        SELECT = "SELECT"
        INSERT = "INSERT"
        UPDATE = "UPDATE"
        DELETE = "DELETE"
        CREATE = "CREATE"
        DROP = "DROP"
        ALTER = "ALTER"

    @unique
    class DataTypeLiteral(StrEnum):
        """Oracle data type literals."""

        VARCHAR2 = "VARCHAR2"
        NUMBER = "NUMBER"
        DATE = "DATE"
        TIMESTAMP = "TIMESTAMP"
        CLOB = "CLOB"
        BLOB = "BLOB"
        CHAR = "CHAR"
        RAW = "RAW"


c = FlextDbOracleConstants

__all__: list[str] = ["FlextDbOracleConstants", "c"]

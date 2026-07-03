"""Oracle database constants following unified class pattern.

This module provides Oracle-specific constants organized into nested classes
for connection configuration, query operations, data types, validation rules,
error messages, and performance tuning.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import re
from enum import StrEnum, unique
from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar, Final

from oracledb import (
    DatabaseError as _OracleDatabaseError,
    InterfaceError as _OracleInterfaceError,
)
from sqlalchemy.exc import (
    DatabaseError as _SQLAlchemyDatabaseError,
    OperationalError as _SQLAlchemyOperationalError,
    SQLAlchemyError as _SQLAlchemyError,
)

from flext_cli import c

if TYPE_CHECKING:
    from flext_db_oracle import t


class FlextDbOracleConstants(c):
    """Oracle database constants extending c foundation.

    Usage:
    ```python
    from flext_db_oracle import FlextDbOracleConstants

    port = FlextDbOracleConstants.DbOracle.DEFAULT_PORT
    query = FlextDbOracleConstants.DbOracle.TEST_QUERY
    ```
    """

    class DbOracle:
        """Oracle domain constants namespace with flat SSOT members."""

        EXC_DB_CONNECT: Final[tuple[type[Exception], ...]] = (
            ConnectionError,
            _OracleDatabaseError,
            _OracleInterfaceError,
        )
        """Oracle DB connection boundary catch (oracledb library errors)."""

        EXC_DB_BROAD: Final[tuple[type[Exception], ...]] = (
            ConnectionError,
            OSError,
            _SQLAlchemyDatabaseError,
            _SQLAlchemyError,
            _SQLAlchemyOperationalError,
            _OracleDatabaseError,
            _OracleInterfaceError,
        )
        """Broad Oracle DB boundary catch including SQLAlchemy errors."""

        DEFAULT_CHARSET: Final[str] = "UTF8"
        DEFAULT_SERVICE_NAME: Final[str] = "XEPDB1"
        DEFAULT_PORT: Final[int] = 1521
        DEFAULT_DATABASE_NAME: Final[str] = "XE"
        DEFAULT_SID: Final[str] = "XE"
        DEFAULT_USERNAME: Final[str] = "system"
        DEFAULT_TIMEOUT: Final[int] = c.DEFAULT_TIMEOUT_SECONDS
        DEFAULT_POOL_MIN: Final[int] = 2
        DEFAULT_POOL_MAX: Final[int] = 20
        DEFAULT_POOL_INCREMENT: Final[int] = 1
        DEFAULT_POOL_TIMEOUT: Final[int] = 60
        DEFAULT_CONNECTION_TIMEOUT: Final[int] = c.DEFAULT_TIMEOUT_SECONDS
        DEFAULT_HOST: Final[str] = c.LOCALHOST
        DEFAULT_ARRAY_SIZE: Final[int] = 100
        DEFAULT_QUERY_LIMIT: Final[int] = 1000
        DEFAULT_QUERY_TIMEOUT: Final[int] = 60
        DEFAULT_BATCH_SIZE: Final[int] = c.DEFAULT_SIZE
        DEFAULT_COMMIT_SIZE: Final[int] = 1000
        DEFAULT_POOL_RECYCLE: Final[int] = 3600
        DEFAULT_LISTENER_PORT: Final[int] = DEFAULT_PORT
        DEFAULT_SSL_PORT: Final[int] = 2484

        MIN_PORT: Final[int] = 1
        MAX_PORT: Final[int] = 65535
        MAX_ERROR_MESSAGE_LENGTH: Final[int] = 500
        MAX_QUERY_TIMEOUT: Final[int] = 3600
        MAX_QUERY_ROWS: Final[int] = 100000
        MAX_BATCH_SIZE: Final[int] = c.DEFAULT_MAX_COMMAND_RETRIES or 1000
        MAX_DISPLAY_ROWS: Final[int] = 1000
        MAX_ORACLE_IDENTIFIER_LENGTH: Final[int] = 30
        MAX_IDENTIFIER_LENGTH: Final[int] = 128
        MAX_TABLE_NAME_LENGTH: Final[int] = MAX_IDENTIFIER_LENGTH
        MAX_COLUMN_NAME_LENGTH: Final[int] = MAX_IDENTIFIER_LENGTH
        MAX_SCHEMA_NAME_LENGTH: Final[int] = MAX_IDENTIFIER_LENGTH
        MAX_USERNAME_LENGTH: Final[int] = MAX_IDENTIFIER_LENGTH
        MAX_SERVICE_NAME_LENGTH: Final[int] = MAX_IDENTIFIER_LENGTH
        MAX_HOSTNAME_LENGTH: Final[int] = 253
        MAX_VARCHAR_LENGTH: Final[int] = 4000

        MIN_COLUMN_FIELDS: Final[int] = 4
        COLUMN_METADATA_FIELD_COUNT: Final[int] = 7
        MILLISECONDS_TO_SECONDS_THRESHOLD: Final[int] = 1000
        PERFORMANCE_WARNING_THRESHOLD_SECONDS: Final[float] = 5.0
        CONNECTION_IDLE_TIMEOUT_SECONDS: Final[int] = 3600
        DATA_SIZE_ESTIMATION_FACTOR: Final[int] = 50
        CONNECTION_EXCELLENT_THRESHOLD_SECONDS: Final[float] = 0.1
        CONNECTION_GOOD_THRESHOLD_SECONDS: Final[float] = 0.5
        CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS: Final[float] = 2.0
        QUERY_EXCELLENT_THRESHOLD_MS: Final[int] = 100
        QUERY_GOOD_THRESHOLD_MS: Final[int] = 500
        QUERY_ACCEPTABLE_THRESHOLD_MS: Final[int] = 2000

        TEST_QUERY: Final[str] = "SELECT 1 FROM DUAL"
        DUAL_TABLE: Final[str] = "DUAL"
        DEFAULT_VARCHAR_TYPE: Final[str] = "VARCHAR2(4000)"
        INTEGER_TYPE: Final[str] = "NUMBER(38)"
        BOOLEAN_TYPE: Final[str] = "NUMBER(1)"
        INDEX_HINT: Final[str] = "/*+ INDEX */"
        FULL_HINT: Final[str] = "/*+ FULL */"
        PARALLEL_HINT: Final[str] = "/*+ PARALLEL */"
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
        LOOPBACK_IP: Final[str] = "127.0.0.1"

        ORACLE_IDENTIFIER_PATTERN: Final[str] = "^[A-Z][A-Z0-9_$#]*$"
        ORACLE_IDENTIFIER_RE: ClassVar[t.RegexPattern] = re.compile(
            ORACLE_IDENTIFIER_PATTERN
        )
        IDENTIFIER_PATTERN: Final[str] = "^[A-Za-z][A-Za-z0-9_$#]*$"
        IDENTIFIER_RE: ClassVar[t.RegexPattern] = re.compile(IDENTIFIER_PATTERN)
        SCHEMA_PATTERN: Final[str] = IDENTIFIER_PATTERN
        SCHEMA_RE: ClassVar[t.RegexPattern] = IDENTIFIER_RE
        WHITESPACE_RE: ClassVar[t.RegexPattern] = re.compile(r"\s+")

        @staticmethod
        def collapse_whitespace(value: str) -> str:
            r"""Replace any whitespace run with a single space.

            Sole sanctioned ``re.sub`` entry-point for the Oracle SQL
            builder (``_compile_statement`` and friends previously called
            ``re.sub(r"\s+", " ", ...)`` directly).
            """
            collapsed: str = FlextDbOracleConstants.DbOracle.WHITESPACE_RE.sub(
                " ", value
            )
            return collapsed

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

        @unique
        class ConnectionType(StrEnum):
            """Oracle connection types."""

            SERVICE_NAME = "service_name"
            SID = "sid"
            TNS = "tns"

        @unique
        class QueryType(StrEnum):
            """Oracle query types."""

            SELECT = "SELECT"
            INSERT = "INSERT"
            UPDATE = "UPDATE"
            DELETE = "DELETE"
            CREATE = "CREATE"
            DROP = "DROP"
            ALTER = "ALTER"

        @unique
        class DataType(StrEnum):
            """Oracle data types."""

            VARCHAR2 = "VARCHAR2"
            NUMBER = "NUMBER"
            DATE = "DATE"
            TIMESTAMP = "TIMESTAMP"
            CLOB = "CLOB"
            BLOB = "BLOB"
            CHAR = "CHAR"
            RAW = "RAW"

        @unique
        class IsolationLevel(StrEnum):
            """Oracle transaction isolation levels."""

            READ_UNCOMMITTED = "READ_UNCOMMITTED"
            READ_COMMITTED = "READ_COMMITTED"
            REPEATABLE_READ = "REPEATABLE_READ"
            SERIALIZABLE = "SERIALIZABLE"

        CONNECTION_TYPE_LITERAL: Final[t.StrSequence] = (
            ConnectionType.SERVICE_NAME.value,
            ConnectionType.SID.value,
            ConnectionType.TNS.value,
        )
        QUERY_TYPE_LITERAL: Final[t.StrSequence] = (
            QueryType.SELECT.value,
            QueryType.INSERT.value,
            QueryType.UPDATE.value,
            QueryType.DELETE.value,
            QueryType.CREATE.value,
            QueryType.DROP.value,
            QueryType.ALTER.value,
        )
        DATA_TYPE_LITERAL: Final[t.StrSequence] = (
            DataType.VARCHAR2.value,
            DataType.NUMBER.value,
            DataType.DATE.value,
            DataType.TIMESTAMP.value,
            DataType.CLOB.value,
            DataType.BLOB.value,
            DataType.CHAR.value,
            DataType.RAW.value,
        )
        ISOLATION_LEVEL_LITERAL: Final[t.StrSequence] = (
            IsolationLevel.READ_UNCOMMITTED.value,
            IsolationLevel.READ_COMMITTED.value,
            IsolationLevel.REPEATABLE_READ.value,
            IsolationLevel.SERIALIZABLE.value,
        )

        VALID_CONNECTION_TYPES: Final[frozenset[str]] = frozenset(
            CONNECTION_TYPE_LITERAL
        )
        VALID_QUERY_TYPES: Final[frozenset[str]] = frozenset(QUERY_TYPE_LITERAL)
        VALID_DATA_TYPES: Final[frozenset[str]] = frozenset(DATA_TYPE_LITERAL)
        VALID_ISOLATION_LEVELS: Final[frozenset[str]] = frozenset(
            ISOLATION_LEVEL_LITERAL
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

        SINGER_TYPE_MAP: Final[t.StrMapping] = MappingProxyType({
            "string": DEFAULT_VARCHAR_TYPE,
            "integer": INTEGER_TYPE,
            "number": DataType.NUMBER.value,
            "boolean": BOOLEAN_TYPE,
            "array": DataType.CLOB.value,
            "t.JsonValue": DataType.CLOB.value,
            "date-time": DataType.TIMESTAMP.value,
            "date": DataType.DATE.value,
            "time": DataType.TIMESTAMP.value,
        })
        ENV_MAPPING: Final[t.StrMapping] = MappingProxyType({
            "FLEXT_TARGET_ORACLE_HOST": "host",
            ENV_HOST: "host",
            "FLEXT_TARGET_ORACLE_PORT": "port",
            ENV_PORT: "port",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "service_name",
            ENV_SERVICE_NAME: "service_name",
            "FLEXT_TARGET_ORACLE_USERNAME": "username",
            ENV_USERNAME: "username",
            "FLEXT_TARGET_ORACLE_PASSWORD": "password",  # nosec B105
            ENV_PASSWORD: "password",  # nosec B105
            "FLEXT_TARGET_ORACLE_DATABASE_NAME": "name",
            ENV_DATABASE_NAME: "name",
        })


c = FlextDbOracleConstants

__all__ = ["FlextDbOracleConstants", "c"]

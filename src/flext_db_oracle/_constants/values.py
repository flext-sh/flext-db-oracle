"""FlextDbOracleConstantsValues - Oracle scalar namespace (SSOT).

Owns every runtime scalar, compiled pattern, enum and literal-derived
frozenset of the Oracle domain. The public facade re-exposes this
namespace through inheritance, so consumers keep reading via ``c.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from enum import StrEnum, unique
from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar

from flext_core import c

if TYPE_CHECKING:
    from flext_db_oracle import t


class FlextDbOracleConstantsValues:
    """Oracle domain scalar namespace owned here (ENFORCE-079 SSOT)."""

    DEFAULT_CHARSET: ClassVar[str] = "UTF8"
    DEFAULT_SERVICE_NAME: ClassVar[str] = "XEPDB1"
    DEFAULT_PORT: ClassVar[int] = 1521
    DEFAULT_DATABASE_NAME: ClassVar[str] = "XE"
    DEFAULT_SID: ClassVar[str] = "XE"
    DEFAULT_USERNAME: ClassVar[str] = "system"
    DEFAULT_TIMEOUT: ClassVar[int] = c.DEFAULT_TIMEOUT_SECONDS
    DEFAULT_POOL_MIN: ClassVar[int] = 2
    DEFAULT_POOL_MAX: ClassVar[int] = 20
    DEFAULT_POOL_INCREMENT: ClassVar[int] = 1
    DEFAULT_POOL_TIMEOUT: ClassVar[int] = 60
    DEFAULT_CONNECTION_TIMEOUT: ClassVar[int] = c.DEFAULT_TIMEOUT_SECONDS
    DEFAULT_HOST: ClassVar[str] = c.LOCALHOST
    DEFAULT_ARRAY_SIZE: ClassVar[int] = 100
    DEFAULT_QUERY_LIMIT: ClassVar[int] = 1000
    DEFAULT_QUERY_TIMEOUT: ClassVar[int] = 60
    DEFAULT_BATCH_SIZE: ClassVar[int] = c.DEFAULT_SIZE
    DEFAULT_COMMIT_SIZE: ClassVar[int] = 1000
    DEFAULT_POOL_RECYCLE: ClassVar[int] = 3600
    DEFAULT_LISTENER_PORT: ClassVar[int] = DEFAULT_PORT
    DEFAULT_SSL_PORT: ClassVar[int] = 2484

    MIN_PORT: ClassVar[int] = 1
    MAX_PORT: ClassVar[int] = 65535
    MAX_ERROR_MESSAGE_LENGTH: ClassVar[int] = 500
    MAX_QUERY_TIMEOUT: ClassVar[int] = 3600
    MAX_QUERY_ROWS: ClassVar[int] = 100000
    MAX_BATCH_SIZE: ClassVar[int] = c.DEFAULT_MAX_COMMAND_RETRIES or 1000
    MAX_DISPLAY_ROWS: ClassVar[int] = 1000
    MAX_ORACLE_IDENTIFIER_LENGTH: ClassVar[int] = 30
    MAX_IDENTIFIER_LENGTH: ClassVar[int] = 128
    MAX_TABLE_NAME_LENGTH: ClassVar[int] = MAX_IDENTIFIER_LENGTH
    MAX_COLUMN_NAME_LENGTH: ClassVar[int] = MAX_IDENTIFIER_LENGTH
    MAX_SCHEMA_NAME_LENGTH: ClassVar[int] = MAX_IDENTIFIER_LENGTH
    MAX_USERNAME_LENGTH: ClassVar[int] = MAX_IDENTIFIER_LENGTH
    MAX_SERVICE_NAME_LENGTH: ClassVar[int] = MAX_IDENTIFIER_LENGTH
    MAX_HOSTNAME_LENGTH: ClassVar[int] = 253
    MAX_VARCHAR_LENGTH: ClassVar[int] = 4000

    MIN_COLUMN_FIELDS: ClassVar[int] = 4
    COLUMN_METADATA_FIELD_COUNT: ClassVar[int] = 7
    MILLISECONDS_TO_SECONDS_THRESHOLD: ClassVar[int] = 1000
    PERFORMANCE_WARNING_THRESHOLD_SECONDS: ClassVar[float] = 5.0
    CONNECTION_IDLE_TIMEOUT_SECONDS: ClassVar[int] = 3600
    DATA_SIZE_ESTIMATION_FACTOR: ClassVar[int] = 50
    CONNECTION_EXCELLENT_THRESHOLD_SECONDS: ClassVar[float] = 0.1
    CONNECTION_GOOD_THRESHOLD_SECONDS: ClassVar[float] = 0.5
    CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS: ClassVar[float] = 2.0
    QUERY_EXCELLENT_THRESHOLD_MS: ClassVar[int] = 100
    QUERY_GOOD_THRESHOLD_MS: ClassVar[int] = 500
    QUERY_ACCEPTABLE_THRESHOLD_MS: ClassVar[int] = 2000

    TEST_QUERY: ClassVar[str] = "SELECT 1 FROM DUAL"
    DUAL_TABLE: ClassVar[str] = "DUAL"
    DEFAULT_VARCHAR_TYPE: ClassVar[str] = "VARCHAR2(4000)"
    INTEGER_TYPE: ClassVar[str] = "NUMBER(38)"
    BOOLEAN_TYPE: ClassVar[str] = "NUMBER(1)"
    INDEX_HINT: ClassVar[str] = "/*+ INDEX */"
    FULL_HINT: ClassVar[str] = "/*+ FULL */"
    PARALLEL_HINT: ClassVar[str] = "/*+ PARALLEL */"
    PREFIX_ORACLE: ClassVar[str] = "ORACLE_"
    PREFIX_FLEXT_TARGET_ORACLE: ClassVar[str] = "FLEXT_TARGET_ORACLE_"
    ENV_HOST: ClassVar[str] = "ORACLE_HOST"
    ENV_PORT: ClassVar[str] = "ORACLE_PORT"
    ENV_USERNAME: ClassVar[str] = "ORACLE_USERNAME"
    ENV_PASSWORD: ClassVar[str] = PREFIX_ORACLE + "PASSWORD"
    ENV_SERVICE_NAME: ClassVar[str] = "ORACLE_SERVICE_NAME"
    ENV_DATABASE_NAME: ClassVar[str] = "ORACLE_DATABASE_NAME"
    ENV_SID: ClassVar[str] = "ORACLE_SID"
    ENV_ENABLE_DISPATCHER: ClassVar[str] = "FLEXT_DB_ORACLE_ENABLE_DISPATCHER"
    LOOPBACK_IP: ClassVar[str] = "127.0.0.1"

    ORACLE_IDENTIFIER_PATTERN: ClassVar[str] = "^[A-Z][A-Z0-9_$#]*$"
    ORACLE_IDENTIFIER_RE: ClassVar[t.RegexPattern] = re.compile(
        ORACLE_IDENTIFIER_PATTERN,
    )
    IDENTIFIER_PATTERN: ClassVar[str] = "^[A-Za-z][A-Za-z0-9_$#]*$"
    IDENTIFIER_RE: ClassVar[t.RegexPattern] = re.compile(IDENTIFIER_PATTERN)
    SCHEMA_PATTERN: ClassVar[str] = IDENTIFIER_PATTERN
    SCHEMA_RE: ClassVar[t.RegexPattern] = IDENTIFIER_RE
    WHITESPACE_RE: ClassVar[t.RegexPattern] = re.compile(r"\s+")

    @staticmethod
    def collapse_whitespace(value: str) -> str:
        r"""Replace any whitespace run with a single space.

        Sole sanctioned ``re.sub`` entry-point for the Oracle SQL
        builder (``_compile_statement`` and friends previously called
        ``re.sub(r"\s+", " ", ...)`` directly).

        Returns:
            The resulting ``str``.

        """
        collapsed: str = FlextDbOracleConstantsValues.WHITESPACE_RE.sub(
            " ",
            value,
        )
        return collapsed

    HOST_EMPTY: ClassVar[str] = "Host cannot be empty"
    USERNAME_EMPTY: ClassVar[str] = "Username cannot be empty"
    COLUMN_NAME_EMPTY: ClassVar[str] = "Column name cannot be empty"
    DATA_TYPE_EMPTY: ClassVar[str] = "Data type cannot be empty"
    TABLE_NAME_EMPTY: ClassVar[str] = "Table name cannot be empty"
    SCHEMA_NAME_EMPTY: ClassVar[str] = "Schema name cannot be empty"
    POSITION_INVALID: ClassVar[str] = "Position must be positive"
    COLUMN_ID_INVALID: ClassVar[str] = "Column ID must be positive"
    PORT_INVALID: ClassVar[str] = "Invalid port number"
    CONNECTION_FAILED: ClassVar[str] = "Failed to connect to Oracle database"
    QUERY_EXECUTION_FAILED: ClassVar[str] = "Query execution failed"
    IDENTIFIER_TOO_LONG: ClassVar[str] = "Identifier exceeds max_length characters"
    IDENTIFIER_INVALID_PATTERN: ClassVar[str] = (
        "Identifier does not match required pattern"
    )
    IDENTIFIER_RESERVED_WORD: ClassVar[str] = "Identifier is a reserved word"
    HOST_TOO_LONG: ClassVar[str] = "Host is too long"
    PORT_OUT_OF_RANGE: ClassVar[str] = (
        "Port must be between {min_port}-{max_port}, got {port}"
    )
    QUERY_TIMEOUT_TOO_HIGH: ClassVar[str] = "Query timeout is too high"

    ORACLE_RESERVED: ClassVar[frozenset[str]] = frozenset({
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
    SQL_KEYWORDS: ClassVar[frozenset[str]] = frozenset({
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

        SERVICE_NAME = c.ContextKey.SERVICE_NAME
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

    CONNECTION_TYPE_LITERAL: ClassVar[Sequence[str]] = (
        ConnectionType.SERVICE_NAME.value,
        ConnectionType.SID.value,
        ConnectionType.TNS.value,
    )
    QUERY_TYPE_LITERAL: ClassVar[Sequence[str]] = (
        QueryType.SELECT.value,
        QueryType.INSERT.value,
        QueryType.UPDATE.value,
        QueryType.DELETE.value,
        QueryType.CREATE.value,
        QueryType.DROP.value,
        QueryType.ALTER.value,
    )
    DATA_TYPE_LITERAL: ClassVar[Sequence[str]] = (
        DataType.VARCHAR2.value,
        DataType.NUMBER.value,
        DataType.DATE.value,
        DataType.TIMESTAMP.value,
        DataType.CLOB.value,
        DataType.BLOB.value,
        DataType.CHAR.value,
        DataType.RAW.value,
    )
    ISOLATION_LEVEL_LITERAL: ClassVar[Sequence[str]] = (
        IsolationLevel.READ_UNCOMMITTED.value,
        IsolationLevel.READ_COMMITTED.value,
        IsolationLevel.REPEATABLE_READ.value,
        IsolationLevel.SERIALIZABLE.value,
    )

    VALID_CONNECTION_TYPES: ClassVar[frozenset[str]] = frozenset(
        CONNECTION_TYPE_LITERAL,
    )
    VALID_QUERY_TYPES: ClassVar[frozenset[str]] = frozenset(QUERY_TYPE_LITERAL)
    VALID_DATA_TYPES: ClassVar[frozenset[str]] = frozenset(DATA_TYPE_LITERAL)
    VALID_ISOLATION_LEVELS: ClassVar[frozenset[str]] = frozenset(
        ISOLATION_LEVEL_LITERAL,
    )
    SYSTEM_USERS: ClassVar[Sequence[str]] = ("SYS", "SYSTEM", "XDB", "DBSNMP", "OUTLN")
    DEFAULT_SCHEMAS: ClassVar[Sequence[str]] = ("SYSTEM", "SYS", "PUBLIC")

    SINGER_TYPE_MAP: ClassVar[Mapping[str, str]] = MappingProxyType({
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
    ENV_MAPPING: ClassVar[Mapping[str, str]] = MappingProxyType({
        "FLEXT_TARGET_ORACLE_HOST": "host",
        ENV_HOST: "host",
        "FLEXT_TARGET_ORACLE_PORT": "port",
        ENV_PORT: "port",
        "FLEXT_TARGET_ORACLE_SERVICE_NAME": c.ContextKey.SERVICE_NAME,
        ENV_SERVICE_NAME: c.ContextKey.SERVICE_NAME,
        "FLEXT_TARGET_ORACLE_USERNAME": "username",
        ENV_USERNAME: "username",
        "FLEXT_TARGET_ORACLE_PASSWORD": "password",  # nosec B105
        ENV_PASSWORD: "password",  # nosec B105
        "FLEXT_TARGET_ORACLE_DATABASE_NAME": "name",
        ENV_DATABASE_NAME: "name",
    })


__all__: tuple[str, ...] = ("FlextDbOracleConstantsValues",)

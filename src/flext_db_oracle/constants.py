"""Oracle Database Constants extending flext-core platform constants.

Oracle Database-specific constants that extend flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextConstants

# =============================================================================
# ORACLE-SPECIFIC SEMANTIC CONSTANTS - Modern Python 3.13 Structure
# =============================================================================


class FlextDbOracleConstants(FlextConstants):
    """Oracle database constants following Flext[Area][Module] pattern.

    Single class inheriting from FlextConstants with all Oracle-specific
    constants as internal nested classes, following SOLID principles,
    PEP8, Python 3.13+, and FLEXT structural patterns.

    This class consolidates all Oracle database constants functionality
    into a single entry point with internal organization.
    """

    class Connection:
        """Oracle connection configuration constants."""

        DEFAULT_CHARSET = "UTF8"
        DEFAULT_SERVICE_NAME = "XEPDB1"

        DEFAULT_POOL_INCREMENT = 1

    class Query:
        """Oracle query and operation constants."""

        TEST_QUERY = "SELECT 1 FROM DUAL"
        DUAL_TABLE = "DUAL"

        DEFAULT_ARRAY_SIZE = 100

    class DataTypes:
        """Oracle data type constants and mappings."""

        # Oracle native types
        DATE_TYPE = "DATE"
        TIMESTAMP_TYPE = "TIMESTAMP"
        DEFAULT_VARCHAR_TYPE = "VARCHAR2(4000)"
        CLOB_TYPE = "CLOB"
        BLOB_TYPE = "BLOB"
        NUMBER_TYPE = "NUMBER"

        # Singer to Oracle type mapping
        SINGER_TYPE_MAP: ClassVar[dict[str, str]] = {
            "string": "VARCHAR2(4000)",
            "integer": "NUMBER(38)",
            "number": "NUMBER",
            "boolean": "NUMBER(1)",
            "array": "CLOB",
            "object": "CLOB",
        }

    class OracleValidation:
        """Oracle-specific validation limits and patterns."""

        MAX_IDENTIFIER_LENGTH = 128
        MAX_TABLE_NAME_LENGTH = 128
        MAX_COLUMN_NAME_LENGTH = 128
        MAX_SCHEMA_NAME_LENGTH = 128
        MAX_VARCHAR_LENGTH = 4000
        MIN_COLUMN_FIELDS = 4  # Required fields: name, type, length, nullable
        COLUMN_METADATA_FIELD_COUNT = 7  # Complete metadata fields count

        # Oracle naming patterns
        IDENTIFIER_PATTERN = r"^[A-Za-z][A-Za-z0-9_$#]*$"
        SCHEMA_PATTERN = r"^[A-Za-z][A-Za-z0-9_$#]*$"

        # Oracle reserved words
        ORACLE_RESERVED = frozenset(
            {
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
            }
        )

    class ErrorMessages:
        """Oracle-specific error messages."""

        HOST_EMPTY = "Host cannot be empty"
        USERNAME_EMPTY = "Username cannot be empty"
        COLUMN_NAME_EMPTY = "Column name cannot be empty"
        DATA_TYPE_EMPTY = "Data type cannot be empty"
        TABLE_NAME_EMPTY = "Table name cannot be empty"
        SCHEMA_NAME_EMPTY = "Schema name cannot be empty"
        POSITION_INVALID = "Position must be positive"
        COLUMN_ID_INVALID = "Column ID must be positive"
        PORT_INVALID = "Invalid port number"
        CONNECTION_FAILED = "Failed to connect to Oracle database"
        QUERY_EXECUTION_FAILED = "Query execution failed"

    class OraclePerformance:
        """Oracle-specific performance tuning constants."""

        DEFAULT_COMMIT_SIZE = 1000
        PERFORMANCE_WARNING_THRESHOLD_SECONDS = 5.0
        MAX_DISPLAY_ROWS = 1000

        # Oracle hints
        INDEX_HINT = "/*+ INDEX */"
        FULL_HINT = "/*+ FULL */"
        PARALLEL_HINT = "/*+ PARALLEL */"

    class NetworkValidation:
        """Network-specific validation constants - inherit from flext-core."""

        MIN_PORT = 1
        MAX_PORT = 65535


# No compatibility aliases - use direct imports only


# =============================================================================
# EXPORTS - Oracle Database constants API
# =============================================================================

__all__: list[str] = [
    "FlextDbOracleConstants",
]

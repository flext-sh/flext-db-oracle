"""Oracle Database Constants extending flext-core platform constants.

Oracle Database-specific constants that extend flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core.constants import FlextConstants


class FlextOracleDbConstants(FlextConstants):
    """Oracle Database constants extending flext-core platform constants."""

    # Oracle specific constants
    ORACLE_DEFAULT_PORT = 1521
    ORACLE_TEST_QUERY = "SELECT 1 FROM DUAL"

    # Oracle data type mappings for Singer
    SINGER_TO_ORACLE_TYPE_MAP: ClassVar[dict[str, str]] = {
        "string": "VARCHAR2(4000)",
        "integer": "NUMBER(38)",
        "number": "NUMBER",
        "boolean": "NUMBER(1)",
        "array": "CLOB",
        "object": "CLOB",
    }

    # Oracle date/time types
    ORACLE_DATE_TYPE = "DATE"
    ORACLE_TIMESTAMP_TYPE = "TIMESTAMP"
    ORACLE_DEFAULT_VARCHAR_TYPE = "VARCHAR2(4000)"

    # Validation error messages (extend core messages)
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

    # Network constants (use platform defaults where possible)
    MAX_PORT = 65535  # Standard TCP/UDP port range


# Legacy constants for backward compatibility
ERROR_MSG_HOST_EMPTY = FlextOracleDbConstants.ErrorMessages.HOST_EMPTY
ERROR_MSG_USERNAME_EMPTY = FlextOracleDbConstants.ErrorMessages.USERNAME_EMPTY
ERROR_MSG_COLUMN_NAME_EMPTY = FlextOracleDbConstants.ErrorMessages.COLUMN_NAME_EMPTY
ERROR_MSG_DATA_TYPE_EMPTY = FlextOracleDbConstants.ErrorMessages.DATA_TYPE_EMPTY
ERROR_MSG_TABLE_NAME_EMPTY = FlextOracleDbConstants.ErrorMessages.TABLE_NAME_EMPTY
ERROR_MSG_SCHEMA_NAME_EMPTY = FlextOracleDbConstants.ErrorMessages.SCHEMA_NAME_EMPTY
ERROR_MSG_POSITION_INVALID = FlextOracleDbConstants.ErrorMessages.POSITION_INVALID
ERROR_MSG_COLUMN_ID_INVALID = FlextOracleDbConstants.ErrorMessages.COLUMN_ID_INVALID
ERROR_MSG_PORT_INVALID = FlextOracleDbConstants.ErrorMessages.PORT_INVALID

MAX_PORT = FlextOracleDbConstants.MAX_PORT
ORACLE_DEFAULT_PORT = FlextOracleDbConstants.ORACLE_DEFAULT_PORT
ORACLE_TEST_QUERY = FlextOracleDbConstants.ORACLE_TEST_QUERY
SINGER_TO_ORACLE_TYPE_MAP = FlextOracleDbConstants.SINGER_TO_ORACLE_TYPE_MAP
ORACLE_DATE_TYPE = FlextOracleDbConstants.ORACLE_DATE_TYPE
ORACLE_TIMESTAMP_TYPE = FlextOracleDbConstants.ORACLE_TIMESTAMP_TYPE
ORACLE_DEFAULT_VARCHAR_TYPE = FlextOracleDbConstants.ORACLE_DEFAULT_VARCHAR_TYPE

__all__: list[str] = [
    "ERROR_MSG_COLUMN_ID_INVALID",
    "ERROR_MSG_COLUMN_NAME_EMPTY",
    "ERROR_MSG_DATA_TYPE_EMPTY",
    "ERROR_MSG_HOST_EMPTY",
    "ERROR_MSG_PORT_INVALID",
    "ERROR_MSG_POSITION_INVALID",
    "ERROR_MSG_SCHEMA_NAME_EMPTY",
    "ERROR_MSG_TABLE_NAME_EMPTY",
    "ERROR_MSG_USERNAME_EMPTY",
    "MAX_PORT",
    "ORACLE_DATE_TYPE",
    "ORACLE_DEFAULT_PORT",
    "ORACLE_DEFAULT_VARCHAR_TYPE",
    "ORACLE_TEST_QUERY",
    "ORACLE_TIMESTAMP_TYPE",
    "SINGER_TO_ORACLE_TYPE_MAP",
]

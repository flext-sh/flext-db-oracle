"""Oracle Database Constants.

Centralized constants to avoid duplication across modules.
"""

# Validation error messages
ERROR_MSG_HOST_EMPTY = "Host cannot be empty"
ERROR_MSG_USERNAME_EMPTY = "Username cannot be empty"
ERROR_MSG_COLUMN_NAME_EMPTY = "Column name cannot be empty"
ERROR_MSG_DATA_TYPE_EMPTY = "Data type cannot be empty"
ERROR_MSG_TABLE_NAME_EMPTY = "Table name cannot be empty"
ERROR_MSG_SCHEMA_NAME_EMPTY = "Schema name cannot be empty"
ERROR_MSG_POSITION_INVALID = "Position must be positive"
ERROR_MSG_COLUMN_ID_INVALID = "Column ID must be positive"
ERROR_MSG_PORT_INVALID = "Invalid port number"

# Network constants
MAX_PORT = (1 << 16) - 1  # 65535 - standard TCP/UDP port range

# Oracle specific constants
ORACLE_DEFAULT_PORT = 1521
ORACLE_TEST_QUERY = "SELECT 1 FROM DUAL"

# Oracle data type mappings for Singer
SINGER_TO_ORACLE_TYPE_MAP = {
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

__all__ = [
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

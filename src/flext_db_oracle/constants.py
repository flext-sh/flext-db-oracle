"""Oracle Database Constants extending flext-core platform constants.

Oracle Database-specific constants that extend flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core.constants import FlextConstants

# =============================================================================
# ORACLE-SPECIFIC SEMANTIC CONSTANTS - Modern Python 3.13 Structure
# =============================================================================


class FlextOracleDbSemanticConstants(FlextConstants):
    """Oracle Database semantic constants extending FlextConstants.

    Modern Python 3.13 constants following semantic grouping patterns.
    Extends the FLEXT ecosystem constants with Oracle Database specific
    values while maintaining full backward compatibility.
    """

    class Connection:
      """Oracle connection configuration constants."""

      # CONSUME from single source - NO DUPLICATION
      DEFAULT_PORT = FlextConstants.Infrastructure.DEFAULT_ORACLE_PORT
      MAX_PORT = FlextConstants.Platform.MAX_PORT_NUMBER
      DEFAULT_CHARSET = "UTF8"
      DEFAULT_SERVICE_NAME = "XEPDB1"
      DEFAULT_TIMEOUT = FlextConstants.Defaults.TIMEOUT

      # Connection pool settings
      DEFAULT_POOL_MIN = FlextConstants.Infrastructure.MIN_POOL_SIZE
      DEFAULT_POOL_MAX = FlextConstants.Infrastructure.DEFAULT_POOL_SIZE
      DEFAULT_POOL_INCREMENT = 1
      DEFAULT_POOL_TIMEOUT = FlextConstants.Defaults.TIMEOUT

    class Query:
      """Oracle query and operation constants."""

      TEST_QUERY = "SELECT 1 FROM DUAL"
      DUAL_TABLE = "DUAL"

      # Query limits and pagination
      DEFAULT_FETCH_SIZE = 1000
      MAX_FETCH_SIZE = 10000
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

    class Validation:
      """Validation limits and patterns."""

      MAX_IDENTIFIER_LENGTH = 128
      MAX_TABLE_NAME_LENGTH = 128
      MAX_COLUMN_NAME_LENGTH = 128
      MAX_SCHEMA_NAME_LENGTH = 128

      # Oracle naming patterns
      IDENTIFIER_PATTERN = r"^[A-Za-z][A-Za-z0-9_$#]*$"
      SCHEMA_PATTERN = r"^[A-Za-z][A-Za-z0-9_$#]*$"

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

    class Performance:
      """Performance tuning constants."""

      DEFAULT_COMMIT_SIZE = 1000
      # CONSUME from single source - NO DUPLICATION
      DEFAULT_BATCH_SIZE = FlextConstants.Performance.DEFAULT_BATCH_SIZE
      MAX_BATCH_SIZE = FlextConstants.Performance.MAX_BATCH_SIZE

      # Oracle hints
      INDEX_HINT = "/*+ INDEX */"
      FULL_HINT = "/*+ FULL */"
      PARALLEL_HINT = "/*+ PARALLEL */"


class FlextOracleDbConstants(FlextOracleDbSemanticConstants):
    """Oracle Database constants with backward compatibility.

    Legacy compatibility layer providing both modern semantic access
    and traditional flat constant access patterns for smooth migration.
    """

    # Modern semantic access (Primary API) - direct references
    Connection = FlextOracleDbSemanticConstants.Connection
    Query = FlextOracleDbSemanticConstants.Query
    DataTypes = FlextOracleDbSemanticConstants.DataTypes
    Validation = FlextOracleDbSemanticConstants.Validation
    ErrorMessages = FlextOracleDbSemanticConstants.ErrorMessages
    Performance = FlextOracleDbSemanticConstants.Performance

    # Legacy compatibility - flat access patterns (DEPRECATED - use semantic access)
    ORACLE_DEFAULT_PORT = FlextOracleDbSemanticConstants.Connection.DEFAULT_PORT
    MAX_PORT = FlextOracleDbSemanticConstants.Connection.MAX_PORT
    DEFAULT_CHARSET = FlextOracleDbSemanticConstants.Connection.DEFAULT_CHARSET
    DEFAULT_SERVICE_NAME = (
      FlextOracleDbSemanticConstants.Connection.DEFAULT_SERVICE_NAME
    )
    DEFAULT_TIMEOUT = FlextOracleDbSemanticConstants.Connection.DEFAULT_TIMEOUT

    ORACLE_TEST_QUERY = FlextOracleDbSemanticConstants.Query.TEST_QUERY
    DUAL_TABLE = FlextOracleDbSemanticConstants.Query.DUAL_TABLE
    DEFAULT_FETCH_SIZE = FlextOracleDbSemanticConstants.Query.DEFAULT_FETCH_SIZE

    ORACLE_DATE_TYPE = FlextOracleDbSemanticConstants.DataTypes.DATE_TYPE
    ORACLE_TIMESTAMP_TYPE = FlextOracleDbSemanticConstants.DataTypes.TIMESTAMP_TYPE
    ORACLE_DEFAULT_VARCHAR_TYPE = (
      FlextOracleDbSemanticConstants.DataTypes.DEFAULT_VARCHAR_TYPE
    )
    SINGER_TO_ORACLE_TYPE_MAP = FlextOracleDbSemanticConstants.DataTypes.SINGER_TYPE_MAP

    MAX_IDENTIFIER_LENGTH = (
      FlextOracleDbSemanticConstants.Validation.MAX_IDENTIFIER_LENGTH
    )
    MAX_COLUMN_NAME_LENGTH = (
      FlextOracleDbSemanticConstants.Validation.MAX_COLUMN_NAME_LENGTH
    )
    IDENTIFIER_PATTERN = FlextOracleDbSemanticConstants.Validation.IDENTIFIER_PATTERN


# =============================================================================
# LEGACY CONSTANTS - Backward compatibility module-level aliases
# =============================================================================

# Connection constants (DEPRECATED - use FlextOracleDbConstants.Connection.*)
ORACLE_DEFAULT_PORT = FlextOracleDbSemanticConstants.Connection.DEFAULT_PORT
MAX_PORT = FlextOracleDbSemanticConstants.Connection.MAX_PORT
DEFAULT_CHARSET = FlextOracleDbSemanticConstants.Connection.DEFAULT_CHARSET
DEFAULT_SERVICE_NAME = FlextOracleDbSemanticConstants.Connection.DEFAULT_SERVICE_NAME
DEFAULT_TIMEOUT = FlextOracleDbSemanticConstants.Connection.DEFAULT_TIMEOUT

# Query constants (DEPRECATED - use FlextOracleDbConstants.Query.*)
ORACLE_TEST_QUERY = FlextOracleDbSemanticConstants.Query.TEST_QUERY
DUAL_TABLE = FlextOracleDbSemanticConstants.Query.DUAL_TABLE
DEFAULT_FETCH_SIZE = FlextOracleDbSemanticConstants.Query.DEFAULT_FETCH_SIZE

# Data type constants (DEPRECATED - use FlextOracleDbConstants.DataTypes.*)
ORACLE_DATE_TYPE = FlextOracleDbSemanticConstants.DataTypes.DATE_TYPE
ORACLE_TIMESTAMP_TYPE = FlextOracleDbSemanticConstants.DataTypes.TIMESTAMP_TYPE
ORACLE_DEFAULT_VARCHAR_TYPE = (
    FlextOracleDbSemanticConstants.DataTypes.DEFAULT_VARCHAR_TYPE
)
SINGER_TO_ORACLE_TYPE_MAP = FlextOracleDbSemanticConstants.DataTypes.SINGER_TYPE_MAP

# Error message constants (DEPRECATED - use FlextOracleDbConstants.ErrorMessages.*)
ERROR_MSG_HOST_EMPTY = FlextOracleDbSemanticConstants.ErrorMessages.HOST_EMPTY
ERROR_MSG_USERNAME_EMPTY = FlextOracleDbSemanticConstants.ErrorMessages.USERNAME_EMPTY
ERROR_MSG_COLUMN_NAME_EMPTY = (
    FlextOracleDbSemanticConstants.ErrorMessages.COLUMN_NAME_EMPTY
)
ERROR_MSG_DATA_TYPE_EMPTY = FlextOracleDbSemanticConstants.ErrorMessages.DATA_TYPE_EMPTY
ERROR_MSG_TABLE_NAME_EMPTY = (
    FlextOracleDbSemanticConstants.ErrorMessages.TABLE_NAME_EMPTY
)
ERROR_MSG_SCHEMA_NAME_EMPTY = (
    FlextOracleDbSemanticConstants.ErrorMessages.SCHEMA_NAME_EMPTY
)
ERROR_MSG_POSITION_INVALID = (
    FlextOracleDbSemanticConstants.ErrorMessages.POSITION_INVALID
)
ERROR_MSG_COLUMN_ID_INVALID = (
    FlextOracleDbSemanticConstants.ErrorMessages.COLUMN_ID_INVALID
)
ERROR_MSG_PORT_INVALID = FlextOracleDbSemanticConstants.ErrorMessages.PORT_INVALID

# =============================================================================
# EXPORTS - Oracle Database constants API
# =============================================================================

__all__: list[str] = [
    # Module-level legacy constants (sorted alphabetically)
    "DEFAULT_CHARSET",
    "DEFAULT_FETCH_SIZE",
    "DEFAULT_SERVICE_NAME",
    "DEFAULT_TIMEOUT",
    "DUAL_TABLE",
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
    # Legacy Compatibility (Backward Compatibility)
    "FlextOracleDbConstants",
    # Modern Semantic Constants (Primary API)
    "FlextOracleDbSemanticConstants",
]

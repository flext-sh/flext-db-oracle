from typing import ClassVar

from _typeshed import Incomplete
from flext_core.constants import FlextConstants

__all__ = [
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
    "FlextOracleDbConstants",
    "FlextOracleDbSemanticConstants",
]

class FlextOracleDbSemanticConstants(FlextConstants):
    class Connection:
        DEFAULT_PORT: Incomplete
        MAX_PORT: Incomplete
        DEFAULT_CHARSET: str
        DEFAULT_SERVICE_NAME: str
        DEFAULT_TIMEOUT: Incomplete
        DEFAULT_POOL_MIN: Incomplete
        DEFAULT_POOL_MAX: Incomplete
        DEFAULT_POOL_INCREMENT: int
        DEFAULT_POOL_TIMEOUT: Incomplete

    class Query:
        TEST_QUERY: str
        DUAL_TABLE: str
        DEFAULT_FETCH_SIZE: int
        MAX_FETCH_SIZE: int
        DEFAULT_ARRAY_SIZE: int

    class DataTypes:
        DATE_TYPE: str
        TIMESTAMP_TYPE: str
        DEFAULT_VARCHAR_TYPE: str
        CLOB_TYPE: str
        BLOB_TYPE: str
        NUMBER_TYPE: str
        SINGER_TYPE_MAP: ClassVar[dict[str, str]]

    class Validation:
        MAX_IDENTIFIER_LENGTH: int
        MAX_TABLE_NAME_LENGTH: int
        MAX_COLUMN_NAME_LENGTH: int
        MAX_SCHEMA_NAME_LENGTH: int
        IDENTIFIER_PATTERN: str
        SCHEMA_PATTERN: str

    class ErrorMessages:
        HOST_EMPTY: str
        USERNAME_EMPTY: str
        COLUMN_NAME_EMPTY: str
        DATA_TYPE_EMPTY: str
        TABLE_NAME_EMPTY: str
        SCHEMA_NAME_EMPTY: str
        POSITION_INVALID: str
        COLUMN_ID_INVALID: str
        PORT_INVALID: str
        CONNECTION_FAILED: str
        QUERY_EXECUTION_FAILED: str

    class Performance:
        DEFAULT_COMMIT_SIZE: int
        DEFAULT_BATCH_SIZE: Incomplete
        MAX_BATCH_SIZE: Incomplete
        INDEX_HINT: str
        FULL_HINT: str
        PARALLEL_HINT: str

class FlextOracleDbConstants(FlextOracleDbSemanticConstants):
    Connection = FlextOracleDbSemanticConstants.Connection
    Query = FlextOracleDbSemanticConstants.Query
    DataTypes = FlextOracleDbSemanticConstants.DataTypes
    Validation = FlextOracleDbSemanticConstants.Validation
    ErrorMessages = FlextOracleDbSemanticConstants.ErrorMessages
    Performance = FlextOracleDbSemanticConstants.Performance
    ORACLE_DEFAULT_PORT: Incomplete
    MAX_PORT: Incomplete
    DEFAULT_CHARSET: Incomplete
    DEFAULT_SERVICE_NAME: Incomplete
    DEFAULT_TIMEOUT: Incomplete
    ORACLE_TEST_QUERY: Incomplete
    DUAL_TABLE: Incomplete
    DEFAULT_FETCH_SIZE: Incomplete
    ORACLE_DATE_TYPE: Incomplete
    ORACLE_TIMESTAMP_TYPE: Incomplete
    ORACLE_DEFAULT_VARCHAR_TYPE: Incomplete
    SINGER_TO_ORACLE_TYPE_MAP: Incomplete
    MAX_IDENTIFIER_LENGTH: Incomplete
    MAX_COLUMN_NAME_LENGTH: Incomplete
    IDENTIFIER_PATTERN: Incomplete

ORACLE_DEFAULT_PORT: Incomplete
MAX_PORT: Incomplete
DEFAULT_CHARSET: Incomplete
DEFAULT_SERVICE_NAME: Incomplete
DEFAULT_TIMEOUT: Incomplete
ORACLE_TEST_QUERY: Incomplete
DUAL_TABLE: Incomplete
DEFAULT_FETCH_SIZE: Incomplete
ORACLE_DATE_TYPE: Incomplete
ORACLE_TIMESTAMP_TYPE: Incomplete
ORACLE_DEFAULT_VARCHAR_TYPE: Incomplete
SINGER_TO_ORACLE_TYPE_MAP: Incomplete
ERROR_MSG_HOST_EMPTY: Incomplete
ERROR_MSG_USERNAME_EMPTY: Incomplete
ERROR_MSG_COLUMN_NAME_EMPTY: Incomplete
ERROR_MSG_DATA_TYPE_EMPTY: Incomplete
ERROR_MSG_TABLE_NAME_EMPTY: Incomplete
ERROR_MSG_SCHEMA_NAME_EMPTY: Incomplete
ERROR_MSG_POSITION_INVALID: Incomplete
ERROR_MSG_COLUMN_ID_INVALID: Incomplete
ERROR_MSG_PORT_INVALID: Incomplete

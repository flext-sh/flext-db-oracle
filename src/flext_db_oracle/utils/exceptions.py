"""Oracle Database Core Exception Classes."""

from __future__ import annotations


class OracleDBCoreError(Exception):
    """Base exception for Oracle database core operations."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class OracleConnectionError(OracleDBCoreError):
    """Exception raised for database connection errors."""

    def __init__(self, message: str, host: str | None = None, port: int | None = None) -> None:
        super().__init__(message, "CONNECTION_ERROR")
        self.host = host
        self.port = port


class SchemaError(OracleDBCoreError):
    """Exception raised for schema-related errors."""

    def __init__(self, message: str, schema_name: str | None = None, object_name: str | None = None) -> None:
        super().__init__(message, "SCHEMA_ERROR")
        self.schema_name = schema_name
        self.object_name = object_name


class SQLError(OracleDBCoreError):
    """Exception raised for SQL execution errors."""

    def __init__(self, message: str, sql: str | None = None, oracle_code: str | None = None) -> None:
        super().__init__(message, oracle_code or "SQL_ERROR")
        self.sql = sql
        self.oracle_code = oracle_code


class ValidationError(OracleDBCoreError):
    """Exception raised for data validation errors."""

    def __init__(self, message: str, field: str | None = None, value: str | None = None) -> None:
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value


class ConfigurationError(OracleDBCoreError):
    """Exception raised for configuration errors."""

    def __init__(self, message: str, config_key: str | None = None) -> None:
        super().__init__(message, "CONFIGURATION_ERROR")
        self.config_key = config_key


class PoolError(OracleDBCoreError):
    """Exception raised for connection pool errors."""

    def __init__(self, message: str, pool_name: str | None = None) -> None:
        super().__init__(message, "POOL_ERROR")
        self.pool_name = pool_name

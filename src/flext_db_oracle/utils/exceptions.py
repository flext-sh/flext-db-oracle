"""Oracle Database Core Exception Classes."""

from __future__ import annotations


class OracleDBCoreError(Exception):
    """Base exception for Oracle database core operations."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        """Initialize exception.

        Args:
            message: Error message.
            error_code: Optional error code.

        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ConnectionError(OracleDBCoreError):
    """Exception raised for database connection errors."""

    def __init__(
        self, message: str, host: str | None = None, port: int | None = None
    ) -> None:
        """Initialize connection error.

        Args:
            message: Error message.
            host: Database host.
            port: Database port.

        """
        super().__init__(message, "CONNECTION_ERROR")
        self.host = host
        self.port = port


class SchemaError(OracleDBCoreError):
    """Exception raised for schema-related errors."""

    def __init__(
        self,
        message: str,
        schema_name: str | None = None,
        object_name: str | None = None,
    ) -> None:
        """Initialize schema error.

        Args:
            message: Error message.
            schema_name: Schema name.
            object_name: Database object name.

        """
        super().__init__(message, "SCHEMA_ERROR")
        self.schema_name = schema_name
        self.object_name = object_name


class SQLError(OracleDBCoreError):
    """Exception raised for SQL execution errors."""

    def __init__(
        self, message: str, sql: str | None = None, oracle_code: str | None = None
    ) -> None:
        """Initialize SQL error.

        Args:
            message: Error message.
            sql: SQL statement that caused the error.
            oracle_code: Oracle error code.

        """
        super().__init__(message, oracle_code or "SQL_ERROR")
        self.sql = sql
        self.oracle_code = oracle_code


class ValidationError(OracleDBCoreError):
    """Exception raised for data validation errors."""

    def __init__(
        self, message: str, field: str | None = None, value: str | None = None
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message.
            field: Field name that failed validation.
            value: Value that failed validation.

        """
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value


class ConfigurationError(OracleDBCoreError):
    """Exception raised for configuration errors."""


class PoolError(OracleDBCoreError):
    """Exception raised for connection pool errors."""

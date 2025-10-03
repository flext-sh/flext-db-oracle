"""Oracle Database exceptions using FLEXT ecosystem patterns.

All Oracle-specific exceptions follow the standard FlextExceptions pattern with
helper methods for context management and correlation ID support.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final, override

from pydantic import Field, field_validator

from flext_core import FlextExceptions, FlextModels, FlextTypes


class FlextDbOracleExceptions(FlextExceptions):
    """Oracle database exceptions following standard FlextExceptions pattern.

    All Oracle-specific exceptions extend FlextExceptions.BaseError and use
    standardized helper methods for context management and correlation ID tracking.

    This class consolidates all Oracle database exception functionality
    with proper error codes, context, and correlation tracking.
    """

    class ExceptionParams(FlextModels.Entity):
        """Parameters for Oracle exception handling."""

        error_code: str = Field(description="Oracle error code")
        message: str = Field(description="Error message")
        context: FlextTypes.Dict = Field(
            default_factory=dict, description="Additional context"
        )
        sql_statement: str | None = Field(default=None, description="SQL statement")
        connection_info: FlextTypes.StringDict | None = Field(
            default=None, description="Connection information"
        )

        @field_validator("message")
        @classmethod
        def validate_message(cls, v: str) -> str:
            """Validate that message is not empty or whitespace."""
            if not v or not v.strip():
                msg = "Exception message cannot be empty"
                raise ValueError(msg)
            return v

        class Config:
            """Pydantic config for ExceptionParams."""

            frozen = True  # Make it immutable

    class OracleErrorCodes:
        """Oracle-specific error codes."""

        # Generic FLEXT error codes for Oracle operations
        VALIDATION_ERROR: Final[str] = "ORACLE_VALIDATION_ERROR"
        CONFIGURATION_ERROR: Final[str] = "ORACLE_CONFIGURATION_ERROR"
        CONNECTION_ERROR: Final[str] = "ORACLE_CONNECTION_ERROR"
        PROCESSING_ERROR: Final[str] = "ORACLE_PROCESSING_ERROR"
        AUTHENTICATION_ERROR: Final[str] = "ORACLE_AUTHENTICATION_ERROR"
        TIMEOUT_ERROR: Final[str] = "ORACLE_TIMEOUT_ERROR"
        QUERY_ERROR: Final[str] = "ORACLE_QUERY_ERROR"
        METADATA_ERROR: Final[str] = "ORACLE_METADATA_ERROR"

        # Oracle-specific error codes
        CONNECTION_FAILED: Final[str] = "ORA-12541"
        INVALID_USERNAME: Final[str] = "ORA-01017"
        TABLE_NOT_FOUND: Final[str] = "ORA-00942"
        COLUMN_NOT_FOUND: Final[str] = "ORA-00904"
        TIMEOUT: Final[str] = "ORA-12170"
        NETWORK_ERROR: Final[str] = "ORA-12514"

    class OracleBaseError(FlextExceptions.BaseError):
        """Base Oracle database error with standard helper methods."""

        @override
        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize Oracle base error with message and context using helpers.

            Args:
                message: Error message
                **kwargs: Additional context (context, correlation_id, error_code,
                         oracle_code, sql_statement, connection_info)

            """
            # Store Oracle-specific attributes before extracting common kwargs
            self.oracle_code: str | None = None
            self.sql_statement: str | None = None
            self.connection_info: FlextTypes.StringDict | None = None

            if "oracle_code" in kwargs:
                self.oracle_code = (
                    str(kwargs.pop("oracle_code"))
                    if kwargs["oracle_code"] is not None
                    else None
                )
            if "sql_statement" in kwargs:
                self.sql_statement = (
                    str(kwargs.pop("sql_statement"))
                    if kwargs["sql_statement"] is not None
                    else None
                )
            if "connection_info" in kwargs:
                conn_info = kwargs.pop("connection_info")
                self.connection_info = (
                    dict(conn_info) if conn_info is not None else None
                )

            # Extract common parameters using helper
            base_context, correlation_id, error_code = self._extract_common_kwargs(
                kwargs
            )

            # Build context with Oracle-specific fields
            context = self._build_context(
                base_context,
                oracle_code=self.oracle_code,
                sql_statement=self.sql_statement,
                connection_info=self.connection_info,
            )

            # Call parent with complete error information
            super().__init__(
                message,
                code=error_code or "ORACLE_ERROR",
                context=context,
                correlation_id=correlation_id,
            )

    class OracleError(OracleBaseError):
        """General Oracle database error."""

        @override
        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize Oracle error with message and context."""
            super().__init__(message, **kwargs)
            self.error_type = "OracleError"

    class OracleValidationError(OracleBaseError):
        """Oracle validation error."""

        @override
        def __init__(
            self,
            message: str,
            *,
            field: str | None = None,
            value: object = None,
            validation_details: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle validation error with field details.

            Args:
                message: Error message
                field: Field name that failed validation
                value: Invalid value
                validation_details: Detailed validation failure information
                **kwargs: Additional context (context, correlation_id, error_code)

            """
            self.field = field
            self.value = value
            self.validation_details = validation_details

            # Extract common parameters using helper
            base_context, correlation_id, error_code = self._extract_common_kwargs(
                kwargs
            )

            # Build context with validation-specific fields
            context = self._build_context(
                base_context,
                field=field,
                value=value,
                validation_details=validation_details,
            )

            # Call parent with complete error information
            super().__init__(
                message,
                code=error_code or "ORACLE_VALIDATION_ERROR",
                context=context,
                correlation_id=correlation_id,
                **kwargs,
            )
            self.error_type = "ValidationError"

        @classmethod
        def from_field_error(
            cls, field: str, value: object, message: str
        ) -> FlextDbOracleExceptions.OracleValidationError:
            """Create validation error from field details."""
            return cls(
                message=f"Validation failed for field '{field}': {message}",
                field=field,
                value=value,
            )

    class OracleConfigurationError(OracleBaseError):
        """Oracle configuration error."""

        @override
        def __init__(
            self,
            message: str,
            *,
            config_key: str | None = None,
            config_file: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle configuration error with config key details.

            Args:
                message: Error message
                config_key: Configuration key that is invalid
                config_file: Configuration file path
                **kwargs: Additional context (context, correlation_id, error_code)

            """
            self.config_key = config_key
            self.config_file = config_file

            # Extract common parameters using helper
            base_context, correlation_id, error_code = self._extract_common_kwargs(
                kwargs
            )

            # Build context with configuration-specific fields
            context = self._build_context(
                base_context,
                config_key=config_key,
                config_file=config_file,
            )

            # Call parent with complete error information
            super().__init__(
                message,
                code=error_code or "ORACLE_CONFIGURATION_ERROR",
                context=context,
                correlation_id=correlation_id,
                **kwargs,
            )
            self.error_type = "ConfigurationError"

        @classmethod
        def missing_config(
            cls, key: str
        ) -> FlextDbOracleExceptions.OracleConfigurationError:
            """Create error for missing configuration."""
            return cls(message=f"Missing required configuration: {key}", config_key=key)

    class OracleConnectionError(OracleBaseError):
        """Oracle connection error."""

        @override
        def __init__(
            self,
            message: str,
            *,
            host: str | None = None,
            port: int | None = None,
            endpoint: str | None = None,
            service: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle connection error with connection details.

            Args:
                message: Error message
                host: Database host
                port: Database port
                endpoint: Connection endpoint
                service: Service name
                **kwargs: Additional context (context, correlation_id, error_code)

            """
            self.host = host
            self.port = port
            self.endpoint = endpoint
            self.service = service

            # Extract common parameters using helper
            base_context, correlation_id, error_code = self._extract_common_kwargs(
                kwargs
            )

            # Build context with connection-specific fields
            context = self._build_context(
                base_context,
                host=host,
                port=port,
                endpoint=endpoint,
                service=service,
            )

            # Call parent with complete error information
            super().__init__(
                message,
                code=error_code or "ORACLE_CONNECTION_ERROR",
                context=context,
                correlation_id=correlation_id,
                **kwargs,
            )
            self.error_type = "ConnectionError"

    class OracleAuthenticationError(OracleBaseError):
        """Oracle authentication error."""

        @override
        def __init__(
            self,
            message: str,
            *,
            username: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle authentication error with username details.

            Args:
                message: Error message
                username: Username that failed authentication
                **kwargs: Additional context (context, correlation_id, error_code)

            """
            self.username = username

            # Extract common parameters using helper
            base_context, correlation_id, error_code = self._extract_common_kwargs(
                kwargs
            )

            # Build context with authentication-specific fields
            context = self._build_context(
                base_context,
                username=username,
            )

            # Call parent with complete error information
            super().__init__(
                message,
                code=error_code or "ORACLE_AUTHENTICATION_ERROR",
                context=context,
                correlation_id=correlation_id,
                **kwargs,
            )
            self.error_type = "AuthenticationError"

        @classmethod
        def invalid_credentials(
            cls, username: str
        ) -> FlextDbOracleExceptions.OracleAuthenticationError:
            """Create error for invalid credentials."""
            return cls(
                message=f"Invalid credentials for user: {username}", username=username
            )

    class OracleProcessingError(OracleBaseError):
        """Oracle data processing error."""

        @override
        def __init__(
            self,
            message: str,
            *,
            operation: str | None = None,
            data_context: FlextTypes.Dict | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle processing error with operation details.

            Args:
                message: Error message
                operation: Processing operation that failed
                data_context: Data processing context
                **kwargs: Additional context (context, correlation_id, error_code)

            """
            self.operation = operation
            self.data_context = data_context or {}

            # Extract common parameters using helper
            base_context, correlation_id, error_code = self._extract_common_kwargs(
                kwargs
            )

            # Build context with processing-specific fields
            context = self._build_context(
                base_context,
                operation=operation,
                data_context=data_context,
            )

            # Call parent with complete error information
            super().__init__(
                message,
                code=error_code or "ORACLE_PROCESSING_ERROR",
                context=context,
                correlation_id=correlation_id,
                **kwargs,
            )
            self.error_type = "ProcessingError"

        @classmethod
        def data_conversion_failed(
            cls, operation: str, details: str
        ) -> FlextDbOracleExceptions.OracleProcessingError:
            """Create error for data conversion failures."""
            return cls(
                message=f"Data conversion failed during {operation}: {details}",
                operation=operation,
            )

    class OracleTimeoutError(OracleBaseError):
        """Oracle timeout error."""

        @override
        def __init__(
            self,
            message: str,
            *,
            timeout_seconds: float | None = None,
            operation: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle timeout error with timeout details.

            Args:
                message: Error message
                timeout_seconds: Timeout duration in seconds
                operation: Operation that timed out
                **kwargs: Additional context (context, correlation_id, error_code)

            """
            self.timeout_seconds = timeout_seconds
            self.operation = operation

            # Extract common parameters using helper
            base_context, correlation_id, error_code = self._extract_common_kwargs(
                kwargs
            )

            # Build context with timeout-specific fields
            context = self._build_context(
                base_context,
                timeout_seconds=timeout_seconds,
                operation=operation,
            )

            # Call parent with complete error information
            super().__init__(
                message,
                code=error_code or "ORACLE_TIMEOUT_ERROR",
                context=context,
                correlation_id=correlation_id,
                **kwargs,
            )
            self.error_type = "TimeoutError"

        @classmethod
        def query_timeout(
            cls, timeout_seconds: float, query: str | None = None
        ) -> FlextDbOracleExceptions.OracleTimeoutError:
            """Create error for query timeouts."""
            message = f"Query timed out after {timeout_seconds} seconds"
            if query:
                message += f": {query[:100]}..."
            return cls(
                message=message,
                timeout_seconds=timeout_seconds,
                operation="query_execution",
                sql_statement=query,
            )

    class OracleQueryError(OracleBaseError):
        """Oracle query execution error."""

        @override
        def __init__(
            self, message: str, *, query: str | None = None, **kwargs: object
        ) -> None:
            """Initialize Oracle query error with query details.

            Args:
                message: Error message
                query: SQL query that failed
                **kwargs: Additional context (context, correlation_id, error_code)

            """
            self.query = query

            # Extract common parameters using helper
            base_context, correlation_id, error_code = self._extract_common_kwargs(
                kwargs
            )

            # Build context with query-specific fields
            context = self._build_context(
                base_context,
                query=query,
            )

            # Call parent with complete error information
            super().__init__(
                message,
                code=error_code or "ORACLE_QUERY_ERROR",
                context=context,
                correlation_id=correlation_id,
                sql_statement=query,
                **kwargs,
            )
            self.error_type = "QueryError"

    class OracleMetadataError(OracleBaseError):
        """Oracle metadata retrieval error."""

        @override
        def __init__(
            self, message: str, *, table_name: str | None = None, **kwargs: object
        ) -> None:
            """Initialize Oracle metadata error with table name details.

            Args:
                message: Error message
                table_name: Table name for metadata operation
                **kwargs: Additional context (context, correlation_id, error_code)

            """
            self.table_name = table_name

            # Extract common parameters using helper
            base_context, correlation_id, error_code = self._extract_common_kwargs(
                kwargs
            )

            # Build context with metadata-specific fields
            context = self._build_context(
                base_context,
                table_name=table_name,
            )

            # Call parent with complete error information
            super().__init__(
                message,
                code=error_code or "ORACLE_METADATA_ERROR",
                context=context,
                correlation_id=correlation_id,
                **kwargs,
            )
            self.error_type = "MetadataError"

    @classmethod
    def create_validation_error(
        cls, field: str, value: object, message: str
    ) -> FlextDbOracleExceptions.OracleValidationError:
        """Factory method for validation errors."""
        return cls.OracleValidationError.from_field_error(field, value, message)

    @classmethod
    def create_connection_error(
        cls, host: str, port: int, message: str
    ) -> FlextDbOracleExceptions.OracleConnectionError:
        """Factory method for connection errors."""
        return cls.OracleConnectionError(message=message, host=host, port=port)

    @classmethod
    def create_timeout_error(
        cls,
        timeout_seconds: float,
        query: str | None = None,
        message: str | None = None,
    ) -> FlextDbOracleExceptions.OracleTimeoutError:
        """Factory method for timeout errors."""
        if message is None:
            message = f"Operation timed out after {timeout_seconds} seconds"
        return cls.OracleTimeoutError(
            message=message,
            timeout_seconds=timeout_seconds,
            operation="query_execution" if query else "operation",
            sql_statement=query,
        )

    @classmethod
    def create_metadata_error(
        cls, object_name: str, message: str = "Metadata missing"
    ) -> FlextDbOracleExceptions.OracleMetadataError:
        """Factory method for metadata errors."""
        return cls.OracleMetadataError(message=message, table_name=object_name)

    @classmethod
    def create_configuration_error(
        cls, config_key: str, config_file: str | None = None, message: str | None = None
    ) -> FlextDbOracleExceptions.OracleConfigurationError:
        """Factory method for configuration errors."""
        if message is None:
            message = f"Missing required configuration: {config_key}"
        return cls.OracleConfigurationError(
            message=message, config_key=config_key, config_file=config_file
        )

    @classmethod
    def create_query_error(
        cls, sql: str, message: str = "Query execution failed"
    ) -> FlextDbOracleExceptions.OracleQueryError:
        """Factory method for query errors."""
        return cls.OracleQueryError(message=message, query=sql)

    @staticmethod
    def is_oracle_error(error: Exception) -> bool:
        """Check if error is Oracle-specific."""
        return isinstance(error, FlextDbOracleExceptions.OracleBaseError)


__all__: FlextTypes.StringList = [
    "FlextDbOracleExceptions",
]

# Aliases for backward compatibility and convenience
setattr(
    FlextDbOracleExceptions,
    "ValidationError",
    FlextDbOracleExceptions.OracleValidationError,
)
setattr(
    FlextDbOracleExceptions,
    "ConfigurationError",
    FlextDbOracleExceptions.OracleConfigurationError,
)
setattr(
    FlextDbOracleExceptions,
    "ConnectionError",
    FlextDbOracleExceptions.OracleConnectionError,
)
setattr(
    FlextDbOracleExceptions,
    "AuthenticationError",
    FlextDbOracleExceptions.OracleAuthenticationError,
)
setattr(
    FlextDbOracleExceptions,
    "ProcessingError",
    FlextDbOracleExceptions.OracleProcessingError,
)
setattr(
    FlextDbOracleExceptions, "TimeoutError", FlextDbOracleExceptions.OracleTimeoutError
)
setattr(FlextDbOracleExceptions, "QueryError", FlextDbOracleExceptions.OracleQueryError)
setattr(
    FlextDbOracleExceptions,
    "MetadataError",
    FlextDbOracleExceptions.OracleMetadataError,
)

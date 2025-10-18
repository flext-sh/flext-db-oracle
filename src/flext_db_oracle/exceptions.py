"""Oracle database exception hierarchy with error codes and correlation tracking.

This module provides FlextDbOracleExceptions, a namespace class containing Oracle-specific
structured exception types with error codes, correlation IDs, and metadata for comprehensive
error handling in Oracle database operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from dataclasses import dataclass

from flext_core.exceptions import FlextExceptions


class FlextDbOracleExceptions(FlextExceptions):
    """Oracle database exception hierarchy with error codes and correlation tracking.

    Architecture: Layer 1 (Foundation - Oracle Error Hierarchy)
    =========================================================
    Provides Oracle-specific structured exception types extending FlextExceptions
    with Oracle database error codes, correlation IDs, and metadata for comprehensive
    error handling in Oracle database operations.

    **Structural Typing and Protocol Compliance**:
    This class satisfies FlextProtocols.Exception through structural typing
    (duck typing) via the following protocol-compliant interface:
    - Oracle-specific exception classes extending FlextExceptions.BaseError
    - Oracle error codes from FlextDbOracleConstants for consistency
    - Correlation ID generation for distributed tracing
    - Automatic structured logging via structlog
    - Exception chaining with cause preservation
    - Flexible metadata for Oracle context propagation

    **Oracle Exception Hierarchy** (12 types):
    1. **Error**: Base Oracle exception (alias for BaseError)
    2. **ValidationError**: Oracle input validation failures
    3. **ConfigurationError**: Oracle configuration-related errors
    4. **OracleConnectionError**: Oracle database connection failures
    5. **OracleTimeoutError**: Oracle operation timeout errors
    6. **AuthenticationError**: Oracle authentication failures
    7. **AuthorizationError**: Oracle permission failures
    8. **OracleQueryError**: Oracle SQL query errors
    9. **OracleMetadataError**: Oracle schema/metadata errors
    10. **ProcessingError**: Oracle data processing errors
    11. **OracleValidationError**: Oracle-specific validation errors
    12. **OracleOperationError**: General Oracle operation errors
    """

    # =========================================================================
    # ORACLE-SPECIFIC EXCEPTION CLASSES
    # =========================================================================

    class Error(FlextExceptions.BaseError):
        """Base Oracle database exception."""

    # Alias for backward compatibility
    BaseError = Error

    class ValidationError(FlextExceptions.ValidationError):
        """Oracle input validation failures."""

    class ConfigurationError(FlextExceptions.ConfigurationError):
        """Oracle configuration-related errors."""

    class OracleConnectionError(FlextExceptions.ConnectionError):
        """Oracle database connection failures.

        Extends base ConnectionError with Oracle-specific metadata:
        - SID, service_name tracking
        - Oracle error codes (ORA-XXXXX)
        - Connection pool information
        """

        def __init__(
            self,
            message: str,
            *,
            sid: str | None = None,
            service_name: str | None = None,
            oracle_error_code: str | None = None,
            pool_info: dict[str, object] | None = None,
            error_code: str | None = None,
            correlation_id: str | None = None,
            metadata: dict[str, object] | None = None,
            auto_log: bool = False,
            auto_correlation: bool = False,
        ) -> None:
            """Initialize Oracle connection error with database-specific context."""
            # Build metadata with Oracle-specific info
            oracle_metadata = {
                "sid": sid,
                "service_name": service_name,
                "oracle_error_code": oracle_error_code,
                "pool_info": pool_info or {},
            }
            if metadata:
                oracle_metadata.update(metadata)

            super().__init__(
                message,
                error_code=error_code,
                correlation_id=correlation_id,
                metadata=oracle_metadata,
                auto_log=auto_log,
                auto_correlation=auto_correlation,
            )
            self.sid = sid
            self.service_name = service_name
            self.oracle_error_code = oracle_error_code
            self.pool_info = pool_info or {}

    class OracleTimeoutError(FlextExceptions.TimeoutError):
        """Oracle operation timeout errors.

        Extends base TimeoutError with Oracle-specific metadata:
        - SQL statement tracking
        - Oracle execution plan information
        - Query optimization hints
        """

        def __init__(
            self,
            message: str,
            *,
            sql_statement: str | None = None,
            execution_plan: str | None = None,
            optimization_hints: list[str] | None = None,
            error_code: str | None = None,
            correlation_id: str | None = None,
            metadata: dict[str, object] | None = None,
            auto_log: bool = False,
            auto_correlation: bool = False,
        ) -> None:
            """Initialize Oracle timeout error with query context."""
            # Build metadata with Oracle-specific info
            oracle_metadata = {
                "sql_statement": sql_statement,
                "execution_plan": execution_plan,
                "optimization_hints": optimization_hints or [],
            }
            if metadata:
                oracle_metadata.update(metadata)

            super().__init__(
                message,
                error_code=error_code,
                correlation_id=correlation_id,
                metadata=oracle_metadata,
                auto_log=auto_log,
                auto_correlation=auto_correlation,
            )
            self.sql_statement = sql_statement
            self.execution_plan = execution_plan
            self.optimization_hints = optimization_hints or []

    class AuthenticationError(FlextExceptions.AuthenticationError):
        """Oracle authentication failures.

        Extends base AuthenticationError with Oracle-specific metadata:
        - Oracle user/schema tracking
        - Authentication method (password, Kerberos, etc.)
        - Oracle privilege information
        """

        def __init__(
            self,
            message: str,
            *,
            oracle_user: str | None = None,
            auth_method: str | None = None,
            privileges: list[str] | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle authentication error with user context."""
            super().__init__(message, **kwargs)
            self.oracle_user = oracle_user
            self.auth_method = auth_method
            self.privileges = privileges or []

    class AuthorizationError(FlextExceptions.AuthorizationError):
        """Oracle permission and authorization failures.

        Extends base AuthorizationError with Oracle-specific metadata:
        - Oracle object tracking (table, view, procedure)
        - Required privileges
        - Oracle role information
        """

        def __init__(
            self,
            message: str,
            *,
            oracle_object: str | None = None,
            required_privileges: list[str] | None = None,
            oracle_roles: list[str] | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle authorization error with privilege context."""
            super().__init__(message, **kwargs)
            self.oracle_object = oracle_object
            self.required_privileges = required_privileges or []
            self.oracle_roles = oracle_roles or []

    class OracleQueryError(FlextExceptions.BaseError):
        """Oracle SQL query errors.

        Specific exception for Oracle SQL syntax, semantic, and execution errors:
        - SQL statement tracking
        - Oracle error codes (ORA-XXXXX)
        - Bind parameter information
        - Query execution context
        """

        def __init__(
            self,
            message: str,
            *,
            sql_statement: str | None = None,
            oracle_error_code: str | None = None,
            bind_parameters: dict[str, object] | None = None,
            execution_context: dict[str, object] | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle query error with SQL context."""
            super().__init__(message, **kwargs)
            self.sql_statement = sql_statement
            self.oracle_error_code = oracle_error_code
            self.bind_parameters = bind_parameters or {}
            self.execution_context = execution_context or {}

    class OracleMetadataError(FlextExceptions.BaseError):
        """Oracle schema and metadata errors.

        Exception for Oracle schema introspection and metadata operations:
        - Schema/object name tracking
        - Metadata operation type
        - Oracle dictionary table information
        """

        def __init__(
            self,
            message: str,
            *,
            schema_name: str | None = None,
            object_name: str | None = None,
            metadata_operation: str | None = None,
            dictionary_tables: list[str] | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle metadata error with schema context."""
            super().__init__(message, **kwargs)
            self.schema_name = schema_name
            self.object_name = object_name
            self.metadata_operation = metadata_operation
            self.dictionary_tables = dictionary_tables or []

    class ProcessingError(FlextExceptions.BaseError):
        """Oracle data processing errors.

        Exception for Oracle data transformation and processing operations:
        - Processing stage tracking
        - Data type information
        - Transformation pipeline context
        """

        def __init__(
            self,
            message: str,
            *,
            processing_stage: str | None = None,
            data_type: str | None = None,
            transformation_context: dict[str, object] | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle processing error with transformation context."""
            super().__init__(message, **kwargs)
            self.processing_stage = processing_stage
            self.data_type = data_type
            self.transformation_context = transformation_context or {}

    class OracleValidationError(FlextExceptions.ValidationError):
        """Oracle-specific validation errors.

        Extends ValidationError with Oracle domain validation:
        - Oracle identifier validation
        - Oracle data type validation
        - Oracle constraint validation
        """

        def __init__(
            self,
            message: str,
            *,
            oracle_identifier: str | None = None,
            validation_rule: str | None = None,
            oracle_constraint: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle validation error with identifier context."""
            super().__init__(message, **kwargs)
            self.oracle_identifier = oracle_identifier
            self.validation_rule = validation_rule
            self.oracle_constraint = oracle_constraint

    class OracleOperationError(FlextExceptions.BaseError):
        """General Oracle operation errors.

        Catch-all exception for Oracle operations not covered by specific exceptions:
        - Operation type tracking
        - Oracle module/component information
        - Generic Oracle error context
        """

        def __init__(
            self,
            message: str,
            *,
            operation_type: str | None = None,
            oracle_module: str | None = None,
            operation_context: dict[str, object] | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle operation error with module context."""
            super().__init__(message, **kwargs)
            self.operation_type = operation_type
            self.oracle_module = oracle_module
            self.operation_context = operation_context or {}

    # =========================================================================
    # ORACLE EXCEPTION UTILITIES
    # =========================================================================

    @staticmethod
    def create_validation_error(
        message: str,
        field: str | None = None,
        value: object = None,
        **kwargs: object,
    ) -> OracleValidationError:
        """Factory method for creating OracleValidationError instances."""
        return FlextDbOracleExceptions.OracleValidationError(
            message,
            field=field,
            value=value,
            **kwargs,
        )

    @staticmethod
    def create_connection_error(
        message: str,
        host: str | None = None,
        port: int | None = None,
        sid: str | None = None,
        service_name: str | None = None,
        **kwargs: object,
    ) -> OracleConnectionError:
        """Factory method for creating OracleConnectionError instances."""
        return FlextDbOracleExceptions.OracleConnectionError(
            message,
            host=host,
            port=port,
            sid=sid,
            service_name=service_name,
            **kwargs,
        )

    @staticmethod
    def create_query_error(
        message: str,
        sql_statement: str | None = None,
        oracle_error_code: str | None = None,
        **kwargs: object,
    ) -> OracleQueryError:
        """Factory method for creating OracleQueryError instances."""
        return FlextDbOracleExceptions.OracleQueryError(
            message,
            sql_statement=sql_statement,
            oracle_error_code=oracle_error_code,
            **kwargs,
        )

    @staticmethod
    def create_metadata_error(
        message: str,
        schema_name: str | None = None,
        object_name: str | None = None,
        **kwargs: object,
    ) -> OracleMetadataError:
        """Factory method for creating OracleMetadataError instances."""
        return FlextDbOracleExceptions.OracleMetadataError(
            message,
            schema_name=schema_name,
            object_name=object_name,
            **kwargs,
        )

    @staticmethod
    def is_oracle_error(error: object) -> bool:
        """Check if an error is an Oracle database error."""
        return isinstance(error, FlextDbOracleExceptions.BaseError)

    @staticmethod
    def get_oracle_error_code(error: object) -> str | None:
        """Extract Oracle error code from an exception if available."""
        if isinstance(error, FlextDbOracleExceptions.OracleQueryError):
            return error.oracle_error_code
        if isinstance(error, FlextDbOracleExceptions.OracleConnectionError):
            return error.oracle_error_code
        return None

    # =========================================================================
    # ORACLE ERROR CODES AND CONSTANTS
    # =========================================================================

    class OracleErrorCodes:
        """Oracle-specific error codes for structured error handling."""

        # Application-level error codes
        VALIDATION_ERROR: str = "ORACLE_VALIDATION_ERROR"
        CONFIGURATION_ERROR: str = "ORACLE_CONFIGURATION_ERROR"
        CONNECTION_ERROR: str = "ORACLE_CONNECTION_ERROR"
        PROCESSING_ERROR: str = "ORACLE_PROCESSING_ERROR"
        AUTHENTICATION_ERROR: str = "ORACLE_AUTHENTICATION_ERROR"
        TIMEOUT_ERROR: str = "ORACLE_TIMEOUT_ERROR"
        QUERY_ERROR: str = "ORACLE_QUERY_ERROR"
        METADATA_ERROR: str = "ORACLE_METADATA_ERROR"

        # Connection errors
        ORA_01017: str = "ORA-01017"  # Invalid username/password
        ORA_12514: str = "ORA-12514"  # TNS:listener does not know of service
        ORA_12541: str = "ORA-12541"  # TNS:no listener
        ORA_12560: str = "ORA-12560"  # TNS:protocol adapter error

        # Query/Syntax errors
        ORA_00900: str = "ORA-00900"  # Invalid SQL statement
        ORA_00904: str = "ORA-00904"  # Invalid identifier
        ORA_00936: str = "ORA-00936"  # Missing expression
        ORA_01722: str = "ORA-01722"  # Invalid number

        # Permission/Security errors
        ORA_01031: str = "ORA-01031"  # Insufficient privileges
        ORA_01917: str = "ORA-01917"  # User or role does not exist

        # Resource errors
        ORA_00060: str = "ORA-00060"  # Deadlock detected
        ORA_01653: str = "ORA-01653"  # Tablespace full

        # Timeout errors
        ORA_12170: str = "ORA-12170"  # Connect timeout occurred

    # =========================================================================
    # EXCEPTION PARAMETERS DATACLASS
    # =========================================================================

    @dataclass
    class ExceptionParams:
        """Parameters for Oracle exception creation."""

        message: str
        error_code: str
        metadata: dict[str, object] | None = None

        def __post_init__(self) -> None:
            """Validate exception parameters."""
            if not self.message:
                msg = "Exception message cannot be empty"
                raise ValueError(msg)
            if not self.error_code:
                msg = "Error code cannot be empty"
                raise ValueError(msg)
            if self.metadata is None:
                self.metadata = {}


# Zero tolerance: No aliases or compatibility imports
__all__ = ["FlextDbOracleExceptions"]

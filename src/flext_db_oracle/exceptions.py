"""Oracle Database exception hierarchy using flext-core DRY patterns.

Domain-specific exceptions using factory pattern to eliminate 150+ lines of duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core.exceptions import create_module_exception_classes

# Create all standard exception classes using factory pattern - eliminates 150+ lines of duplication
oracle_exceptions = create_module_exception_classes("flext_db_oracle")

# Import generated classes for clean usage
FlextDbOracleError = oracle_exceptions["FlextDbOracleError"]
FlextDbOracleValidationError = oracle_exceptions["FlextDbOracleValidationError"]
FlextDbOracleConfigurationError = oracle_exceptions["FlextDbOracleConfigurationError"]
FlextDbOracleConnectionError = oracle_exceptions["FlextDbOracleConnectionError"]
FlextDbOracleProcessingError = oracle_exceptions["FlextDbOracleProcessingError"]
FlextDbOracleAuthenticationError = oracle_exceptions["FlextDbOracleAuthenticationError"]
FlextDbOracleTimeoutError = oracle_exceptions["FlextDbOracleTimeoutError"]


# Factory function to create domain-specific Oracle exceptions - eliminates ALL duplication
def _create_oracle_domain_exception_class(
    class_name: str,
    message_prefix: str,
    default_message: str,
    context_params: dict[str, type],
) -> type:
    """Create Oracle domain exception class dynamically - complete DRY solution."""

    def init_method(
        self: object,
        message: str = default_message,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle domain exception with context."""
        context: dict[str, object] = {}

        # Process context parameters
        for param_name in context_params:
            value = kwargs.pop(param_name, None)
            if value is not None:
                if param_name == "query" and isinstance(value, str):
                    context[param_name] = value[:200]  # Truncate long queries
                else:
                    context[param_name] = value

        # Add remaining kwargs to context
        context.update(kwargs)

        formatted_message = f"Oracle DB {message_prefix}: {message}"
        super(type(self), self).__init__(formatted_message, **context)

    # Create the class dynamically
    return type(
        class_name,
        (FlextDbOracleError,),
        {
            "__init__": init_method,
            "__doc__": f"Oracle database {message_prefix} errors with {message_prefix}-specific context.",
            "__module__": __name__,
        },
    )


# Create domain-specific exceptions using factory - eliminates 40+ lines of duplication
FlextDbOracleQueryError = _create_oracle_domain_exception_class(
    "FlextDbOracleQueryError",
    "query",
    "Oracle database query error",
    {"query": str, "error_code": str},
)

FlextDbOracleMetadataError = _create_oracle_domain_exception_class(
    "FlextDbOracleMetadataError",
    "metadata",
    "Oracle database metadata error",
    {"schema_name": str, "object_name": str},
)


__all__: list[str] = [
    "FlextDbOracleAuthenticationError",
    "FlextDbOracleConfigurationError",
    "FlextDbOracleConnectionError",
    "FlextDbOracleError",
    "FlextDbOracleMetadataError",
    "FlextDbOracleProcessingError",
    "FlextDbOracleQueryError",
    "FlextDbOracleTimeoutError",
    "FlextDbOracleValidationError",
]

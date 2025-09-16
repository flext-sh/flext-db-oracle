"""Oracle Database mixins providing validation and utility patterns.

This module provides mixin classes for Oracle database operations
with validation and utility functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from dataclasses import dataclass

from flext_core import FlextMixins, FlextResult, FlextTypes, FlextValidations

from flext_db_oracle.constants import FlextDbOracleConstants


class FlextDbOracleMixins(FlextMixins):
    """Unified Oracle utilities using flext-core exclusively.

    NO LOCAL IMPLEMENTATIONS - everything delegates to flext-core.
    Uses FlextValidations.BusinessValidators for all validation logic.
    """

    class OracleValidation:
        """Oracle-specific validation using flext-core BusinessValidators exclusively."""

        @staticmethod
        def validate_identifier(identifier: str) -> FlextResult[str]:
            """Validate Oracle identifier using flext-core BusinessValidators."""
            # Use flext-core BusinessValidators directly
            result = FlextValidations.BusinessValidators.validate_string_field(
                identifier.upper(),
                min_length=1,
                max_length=FlextDbOracleConstants.OracleValidation.MAX_IDENTIFIER_LENGTH,
                pattern=FlextDbOracleConstants.OracleValidation.IDENTIFIER_PATTERN,
            )

            if result.is_failure:
                return FlextResult[str].fail(
                    f"Invalid Oracle identifier: {result.error}"
                )

            validated_identifier = result.unwrap()

            # Oracle-specific business rule: check reserved words
            if (
                validated_identifier
                in FlextDbOracleConstants.OracleValidation.ORACLE_RESERVED
            ):
                return FlextResult[str].fail(
                    f"Identifier '{validated_identifier}' is a reserved word"
                )

            return FlextResult[str].ok(validated_identifier)

    @dataclass
    class ParameterContainer:
        """Simple parameter container using dataclass."""

        params: FlextTypes.Core.Dict | None = None

        def __post_init__(self) -> None:
            """Initialize params dict if None."""
            if self.params is None:
                object.__setattr__(self, "params", {})

        def get(self, key: str, *, default: object = None) -> object:
            """Get parameter value with default fallback."""
            if self.params is None:
                return default
            return self.params.get(key, default)

        def require(self, key: str) -> object:
            """Get required parameter value, raising KeyError if missing."""
            if self.params is None or key not in self.params:
                msg = f"Required parameter '{key}' not provided"
                raise KeyError(msg)
            return self.params[key]

    @dataclass
    class ConnectionConfig:
        """Oracle connection configuration using dataclass."""

        host: str
        port: int
        service_name: str
        username: str
        password: str
        test_connection: bool | None = False

    class ErrorTransformer:
        """Error context transformation using flext-core Result patterns."""

        def __init__(self, context: str) -> None:
            """Initialize error context transformer."""
            self.context = context

        def transform[T](self, result: FlextResult[T]) -> FlextResult[T]:
            """Transform result by adding context to error messages."""
            if result.is_success:
                return result
            return FlextResult[T].fail(f"{self.context}: {result.error}")


# ZERO TOLERANCE: No compatibility aliases - use FlextDbOracleMixins.ClassName directly

__all__ = [
    "FlextDbOracleMixins",
]

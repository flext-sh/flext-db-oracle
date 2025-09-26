"""Oracle Database mixins providing validation and utility patterns.

This module provides mixin classes for Oracle database operations
with validation and utility functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import override

from flext_core import FlextMixins, FlextResult, FlextTypes
from flext_db_oracle.constants import FlextDbOracleConstants


class FlextDbOracleMixins(FlextMixins):
    """Unified Oracle utilities using flext-core exclusivel."""

    class OracleValidation:
        """Oracle-specific validation using FlextModels validation methods exclusively."""

        @staticmethod
        def validate_identifier(identifier: str) -> FlextResult[str]:
            """Validate Oracle identifier using direct validation.

            Returns:
                FlextResult[str]: Validated identifier or error.

            """
            # Convert to uppercase for Oracle convention
            upper_identifier = identifier.upper()

            # Basic validation checks
            if not isinstance(upper_identifier, str) or not upper_identifier.strip():
                return FlextResult[str].fail("Oracle identifier cannot be empty")

            # Length validation
            if (
                len(upper_identifier)
                > FlextDbOracleConstants.Validation.MAX_IDENTIFIER_LENGTH
            ):
                return FlextResult[str].fail(
                    f"Oracle identifier too long (max {FlextDbOracleConstants.Validation.MAX_IDENTIFIER_LENGTH} chars)",
                )

            # Pattern validation
            if not re.match(
                FlextDbOracleConstants.Validation.IDENTIFIER_PATTERN,
                upper_identifier,
            ):
                return FlextResult[str].fail(
                    "Oracle identifier contains invalid characters",
                )

            validated_identifier = upper_identifier

            # Validation passed

            # Oracle-specific business rule: check reserved words
            if (
                validated_identifier
                in FlextDbOracleConstants.Validation.ORACLE_RESERVED
            ):
                return FlextResult[str].fail(
                    f"Identifier '{validated_identifier}' is a reserved word",
                )

            return FlextResult[str].ok(validated_identifier)

    @dataclass
    class ParameterContainer:
        """Simple parameter container using dataclass."""

        params: FlextTypes.Core.Dict | None = None

        def __post_init__(self: object) -> None:
            """Initialize params dict if None."""
            if self.params is None:
                object.__setattr__(self, "params", {})

        def get(self, key: str, *, default: object = None) -> object:
            """Get parameter value with default fallback.

            Returns:
                object: Parameter value or default.

            """
            if self.params is None:
                return default
            return self.params.get(key, default)

        def require(self, key: str) -> object:
            """Get required parameter value, raising KeyError if missing.

            Returns:
                object: Required parameter value.

            Raises:
                KeyError: If the required parameter is missing.

            """
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

        @override
        def __init__(self, context: str) -> None:
            """Initialize error context transformer."""
            self.context = context

        def transform[T](self, result: FlextResult[T]) -> FlextResult[T]:
            """Transform result by adding context to error messages.

            Returns:
                FlextResult[T]: Transformed result.

            """
            if result.is_success:
                return result
            return FlextResult[T].fail(f"{self.context}: {result.error}")


# ZERO TOLERANCE: No compatibility aliases - use FlextDbOracleMixins.ClassName directly

__all__ = [
    "FlextDbOracleMixins",
]

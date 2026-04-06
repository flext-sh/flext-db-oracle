"""FlextDbOracle utilities module."""

from __future__ import annotations

from flext_cli import u as _cli_u

from flext_db_oracle._utilities.db_oracle import FlextDbOracleUtilitiesDbOracle


class FlextDbOracleUtilities(_cli_u):
    """FlextDbOracle utilities extending FlextUtilities with Oracle-specific helpers.

    Architecture: Advanced utilities with ZERO code bloat through:
    - TypeIs/TypeGuard for narrowing (PEP 742)
    - BeforeValidator factories for Pydantic coercion
    - @validated decorators eliminating manual validation
    - Generic parsing utilities for StrEnums (inherited from parent)
    """

    class DbOracle(FlextDbOracleUtilitiesDbOracle):
        """Oracle-specific utility namespace."""


u = FlextDbOracleUtilities

__all__ = ["FlextDbOracleUtilities", "u"]

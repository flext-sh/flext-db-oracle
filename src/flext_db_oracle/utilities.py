"""FlextDbOracle utilities module."""

from __future__ import annotations

from flext_cli import u
from flext_core import FlextUtilitiesReliability
from flext_db_oracle._utilities.db_oracle import FlextDbOracleUtilitiesDbOracle


class FlextDbOracleUtilities(
    u,
    FlextUtilitiesReliability,
    FlextDbOracleUtilitiesDbOracle,
):
    """FlextDbOracle utilities extending FlextUtilities with Oracle-specific helpers.

    Architecture: Advanced utilities with ZERO code bloat through:
    - TypeIs/TypeGuard for narrowing (PEP 742)
    - m.BeforeValidator factories for Pydantic coercion
    - @validated decorators eliminating manual validation
    - Generic parsing utilities for StrEnums (inherited from parent)
    """

    class DbOracle(FlextDbOracleUtilitiesDbOracle):
        """Oracle-specific utility namespace."""


u = FlextDbOracleUtilities

__all__: list[str] = ["FlextDbOracleUtilities", "u"]

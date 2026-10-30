# AUTO-GENERATED FILE — Regenerate with: make gen
"""FlextDbOracle utilities module.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import u

from flext_db_oracle._utilities import (
    FlextDbOracleUtilitiesBase,
    FlextDbOracleUtilitiesDbOracle,
)


class FlextDbOracleUtilities(u):
    """FlextDbOracle utilities extending FlextUtilities with Oracle-specific helpers.

    Architecture: Advanced utilities with ZERO code bloat through:
    - TypeIs/TypeGuard for narrowing (PEP 742)
    - m.BeforeValidator factories for Pydantic coercion
    - @validated decorators eliminating manual validation
    - Generic parsing utilities for StrEnums (inherited from parent)
    """

    class DbOracle(FlextDbOracleUtilitiesDbOracle, FlextDbOracleUtilitiesBase):
        """Oracle-specific utility namespace."""


u = FlextDbOracleUtilities
__all__: list[str] = ["FlextDbOracleUtilities", "u"]

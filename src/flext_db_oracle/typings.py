# AUTO-GENERATED FILE — Regenerate with: make gen
"""FLEXT DB Oracle Types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import FlextCliTypes

from flext_db_oracle._typings import (
    FlextDbOracleTypesDbOracle,
    FlextDbOracleTypingsBase,
)


class FlextDbOracleTypes(FlextCliTypes):
    """Public type facade inheriting its complete canonical owner."""

    class DbOracle(
        FlextDbOracleTypingsBase,
        FlextDbOracleTypesDbOracle,
    ):
        """Public type facade inheriting its namespace canonical owner."""


t = FlextDbOracleTypes

__all__: list[str] = ["FlextDbOracleTypes", "t"]

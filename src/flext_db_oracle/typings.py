"""FLEXT DB Oracle Types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import oracledb
from flext_cli import FlextCliTypes

if TYPE_CHECKING:
    from flext_db_oracle import FlextDbOracleSettings


class FlextDbOracleTypes(FlextCliTypes):
    """Oracle database-specific type definitions extending t via MRO."""

    class DbOracle:
        """Oracle domain namespace (flat members per AGENTS.md §149)."""

        OracleDatabaseError: type[Exception] = oracledb.DatabaseError
        OracleInterfaceError: type[Exception] = oracledb.InterfaceError

        type QueryParameters = FlextCliTypes.JsonMapping
        type CliScalar = FlextCliTypes.Scalar | None
        if TYPE_CHECKING:
            type Settings = FlextDbOracleSettings


t = FlextDbOracleTypes

__all__: list[str] = ["FlextDbOracleTypes", "t"]

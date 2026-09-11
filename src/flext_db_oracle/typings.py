"""FLEXT DB Oracle Types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import oracledb
from flext_cli import t


class FlextDbOracleTypes(t):
    """Oracle database-specific type definitions extending t via MRO."""

    class DbOracle:
        """Oracle domain namespace (flat members per AGENTS.md §149)."""

        OracleDatabaseError: type[Exception] = oracledb.DatabaseError
        OracleInterfaceError: type[Exception] = oracledb.InterfaceError

        type QueryParameters = t.JsonMapping
        type CliScalar = t.Scalar | None


t = FlextDbOracleTypes

__all__: list[str] = ["FlextDbOracleTypes", "t"]

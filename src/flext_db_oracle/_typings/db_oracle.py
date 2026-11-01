"""FLEXT DB Oracle domain type declarations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal

import oracledb
from flext_cli import FlextCliTypes

from flext_db_oracle import FlextDbOracleSettings


class FlextDbOracleTypes(FlextCliTypes):
    """Oracle database-specific type definitions extending t via MRO."""

    class DbOracle:
        """Oracle domain namespace (flat members per AGENTS.md §149)."""

        OracleDatabaseError: type[Exception] = oracledb.DatabaseError
        OracleInterfaceError: type[Exception] = oracledb.InterfaceError

        type QueryParameters = FlextCliTypes.JsonMapping
        type CliScalar = FlextCliTypes.Scalar | None
        type Settings = FlextDbOracleSettings
        type PrivilegeMode = Literal["SYSDBA", "SYSOPER"]


t = FlextDbOracleTypes

__all__: list[str] = ["FlextDbOracleTypes", "t"]

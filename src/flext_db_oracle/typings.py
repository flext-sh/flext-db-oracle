"""FLEXT DB Oracle Types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import FlextCliTypes

from flext_db_oracle._typings import db_oracle as _db_oracle_types


class FlextDbOracleTypes(FlextCliTypes):
    """Oracle database-specific type definitions extending t via MRO."""

    class DbOracle:
        """Oracle domain namespace (flat members per AGENTS.md §149)."""

        OracleDatabaseError = _db_oracle_types.OracleDatabaseError
        OracleInterfaceError = _db_oracle_types.OracleInterfaceError

        QueryParameters = _db_oracle_types.QueryParameters
        CliScalar = _db_oracle_types.CliScalar
        Settings = _db_oracle_types.Settings


t = FlextDbOracleTypes

__all__: list[str] = ["FlextDbOracleTypes", "t"]

"""FLEXT DB Oracle domain type declarations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import oracledb
from flext_cli import FlextCliTypes

if TYPE_CHECKING:
    from flext_db_oracle import FlextDbOracleSettings

OracleDatabaseError: type[Exception] = oracledb.DatabaseError
OracleInterfaceError: type[Exception] = oracledb.InterfaceError

type QueryParameters = FlextCliTypes.JsonMapping
type CliScalar = FlextCliTypes.Scalar | None
type Settings = FlextDbOracleSettings

__all__: list[str] = [
    "CliScalar",
    "OracleDatabaseError",
    "OracleInterfaceError",
    "QueryParameters",
    "Settings",
]

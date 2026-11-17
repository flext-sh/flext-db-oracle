"""FLEXT DB Oracle domain type declarations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar, Literal

import oracledb
from flext_core import t
from sqlalchemy import Connection, DateTime, Engine, Text
from sqlalchemy.sql import Executable

from flext_db_oracle import FlextDbOracleSettings


class FlextDbOracleTypesDbOracle(t):
    """Oracle database-specific type definitions extending t via MRO."""

    class DbOracle:
        """Oracle domain namespace (flat members per AGENTS.md §149).

        ``Oracle*`` members are oracledb driver objects; ``Sql*`` members are the
        SQLAlchemy objects flext-db-oracle owns, so consumers annotate connections,
        engines and statements, and pass column types to ORM row mappings, without
        importing SQLAlchemy. ``SqlDateTime()`` reads Oracle DATE as a naive local
        timestamp; ``SqlText`` maps a CLOB.
        """

    OracleDatabaseError: ClassVar[type[Exception]] = oracledb.DatabaseError
    OracleInterfaceError: ClassVar[type[Exception]] = oracledb.InterfaceError
    SqlDateTime: ClassVar[type[DateTime]] = DateTime
    SqlText: ClassVar[type[Text]] = Text

    type SqlConnection = Connection
    type SqlEngine = Engine
    type SqlExecutable = Executable

    type QueryParameters = t.JsonMapping
    type CliScalar = t.Scalar | None
    type Settings = FlextDbOracleSettings
    type PrivilegeMode = Literal["SYSDBA", "SYSOPER"]


__all__: list[str] = ["FlextDbOracleTypesDbOracle"]

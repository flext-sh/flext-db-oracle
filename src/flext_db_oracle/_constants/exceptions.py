"""Oracle database exception constants.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import t
from oracledb import (
    DatabaseError as OracleDatabaseError,
    InterfaceError as OracleInterfaceError,
)
from sqlalchemy.exc import (
    DatabaseError as SQLAlchemyDatabaseError,
    OperationalError as SQLAlchemyOperationalError,
    SQLAlchemyError,
)


class FlextDbOracleConstantsExceptions:
    """Oracle database exception type tuples."""

    class DbOracle:
        """Oracle domain exception constants."""

        EXC_DB_CONNECT: t.VariadicTuple[type[Exception]] = (
            ConnectionError,
            OracleDatabaseError,
            OracleInterfaceError,
        )
        """Oracle DB connection boundary catch (oracledb library errors)."""

        EXC_DB_BROAD: t.VariadicTuple[type[Exception]] = (
            ConnectionError,
            OSError,
            SQLAlchemyDatabaseError,
            SQLAlchemyError,
            SQLAlchemyOperationalError,
            OracleDatabaseError,
            OracleInterfaceError,
        )
        """Broad Oracle DB boundary catch including SQLAlchemy errors."""


__all__: tuple[str, ...] = ("FlextDbOracleConstantsExceptions",)

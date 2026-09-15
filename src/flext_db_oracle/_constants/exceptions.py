"""Oracle database exception constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from oracledb import (
    DatabaseError as _OracleDatabaseError,
    InterfaceError as _OracleInterfaceError,
)
from sqlalchemy.exc import (
    DatabaseError as _SQLAlchemyDatabaseError,
    OperationalError as _SQLAlchemyOperationalError,
    SQLAlchemyError as _SQLAlchemyError,
)


class FlextDbOracleConstantsExceptions:
    """Oracle database exception type tuples."""

    class DbOracle:
        """Oracle domain exception constants."""

        EXC_DB_CONNECT: tuple[type[Exception], ...] = (
            ConnectionError,
            _OracleDatabaseError,
            _OracleInterfaceError,
        )
        """Oracle DB connection boundary catch (oracledb library errors)."""

        EXC_DB_BROAD: tuple[type[Exception], ...] = (
            ConnectionError,
            OSError,
            _SQLAlchemyDatabaseError,
            _SQLAlchemyError,
            _SQLAlchemyOperationalError,
            _OracleDatabaseError,
            _OracleInterfaceError,
        )
        """Broad Oracle DB boundary catch including SQLAlchemy errors."""

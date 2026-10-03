"""Oracle database constants following unified class pattern.

This module provides Oracle-specific constants organized into nested classes
for connection configuration, query operations, data types, validation rules,
error messages, and performance tuning. The scalar namespace itself is owned
by ``_constants.values`` (ENFORCE-079 SSOT) and inherited through this facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextConstants as c
from flext_db_oracle._constants.exceptions import FlextDbOracleConstantsExceptions
from flext_db_oracle._constants.values import FlextDbOracleConstantsValues


class FlextDbOracleConstants(c):
    """Oracle database constants extending c foundation.

    Usage:
    ```python
    from flext_db_oracle import FlextDbOracleConstants

    port = FlextDbOracleConstants.DbOracle.DEFAULT_PORT
    query = FlextDbOracleConstants.DbOracle.TEST_QUERY
    ```
    """

    class DbOracle(
        FlextDbOracleConstantsExceptions.DbOracle,
        FlextDbOracleConstantsValues.DbOracle,
    ):
        """Oracle domain constants namespace with flat SSOT members.

        Exception-catch tuples (``EXC_DB_CONNECT``, ``EXC_DB_BROAD``) are owned
        by ``flext_db_oracle._constants`` and inherited through this facade
        subclass; every scalar, pattern, enum and literal-derived frozenset is
        owned by ``_constants.values`` and inherited from there.
        """


c = FlextDbOracleConstants

__all__ = ["FlextDbOracleConstants", "c"]

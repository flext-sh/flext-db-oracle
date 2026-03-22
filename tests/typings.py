"""Test type aliases for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsTypes

from flext_db_oracle import FlextDbOracleTypes


class FlextDbOracleTestTypes(FlextTestsTypes, FlextDbOracleTypes):
    """Test type aliases for flext-db-oracle."""

    class DbOracle(FlextDbOracleTypes.DbOracle):
        """DbOracle domain test type aliases."""

        class Tests:
            """Test-specific type aliases."""


t = FlextDbOracleTestTypes
__all__ = ["FlextDbOracleTestTypes", "t"]

"""Test utilities for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsUtilities

from flext_db_oracle import FlextDbOracleUtilities


class FlextDbOracleTestUtilities(FlextTestsUtilities, FlextDbOracleUtilities):
    """Test utilities for flext-db-oracle."""

    class DbOracle(FlextDbOracleUtilities.DbOracle):
        """DbOracle domain test utilities."""

        class Tests:
            """Test-specific utilities."""


u = FlextDbOracleTestUtilities
__all__ = ["FlextDbOracleTestUtilities", "u"]

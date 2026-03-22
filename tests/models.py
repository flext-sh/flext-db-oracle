"""Test models for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsModels

from flext_db_oracle import FlextDbOracleModels


class FlextDbOracleTestModels(FlextTestsModels, FlextDbOracleModels):
    """Test models for flext-db-oracle."""

    class DbOracle(FlextDbOracleModels.DbOracle):
        """DbOracle domain test models."""

        class Tests:
            """Test-specific models."""


m = FlextDbOracleTestModels
__all__ = ["FlextDbOracleTestModels", "m"]

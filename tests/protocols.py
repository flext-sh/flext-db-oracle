"""Test protocols for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsProtocols

from flext_db_oracle import FlextDbOracleProtocols


class TestsFlextDbOracleProtocols(FlextTestsProtocols, FlextDbOracleProtocols):
    """Test protocols for flext-db-oracle."""

    class DbOracle(FlextDbOracleProtocols.DbOracle):
        """DbOracle domain test protocols."""

        class Tests:
            """Test-specific protocols."""


p = TestsFlextDbOracleProtocols
__all__ = ["TestsFlextDbOracleProtocols", "p"]

"""Test protocol definitions for flext-db-oracle.

Provides TestsFlextDbOracleProtocols, combining FlextTestsProtocols with
FlextDbOracleProtocols for test-specific protocol definitions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle.protocols import FlextDbOracleProtocols
from flext_tests.protocols import FlextTestsProtocols


class TestsFlextDbOracleProtocols(FlextTestsProtocols, FlextDbOracleProtocols):
    """Test protocols combining FlextTestsProtocols and FlextDbOracleProtocols.

    Provides access to:
    - p.Tests.Docker.* (from FlextTestsProtocols)
    - p.Tests.Factory.* (from FlextTestsProtocols)
    - p.DbOracle.* (from FlextDbOracleProtocols)
    """

    class Tests:
        """Project-specific test protocols.

        Extends FlextTestsProtocols.Tests with DbOracle-specific protocols.
        """

        class DbOracle:
            """DbOracle-specific test protocols."""


# Runtime aliases
p = TestsFlextDbOracleProtocols
p = TestsFlextDbOracleProtocols

__all__ = ["TestsFlextDbOracleProtocols", "p"]

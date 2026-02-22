"""Test protocol definitions for flext-db-oracle.

Provides TestsFlextDbOracleProtocols, combining FlextTestsProtocols with
FlextDbOracleProtocols for test-specific protocol definitions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests.protocols import FlextTestsProtocols

from flext_db_oracle.protocols import FlextDbOracleProtocols


class TestsFlextDbOracleProtocols(FlextTestsProtocols, FlextDbOracleProtocols):
    """Test protocols combining FlextTestsProtocols and FlextDbOracleProtocols.

    Provides access to:
    - tp.Tests.Docker.* (from FlextTestsProtocols)
    - tp.Tests.Factory.* (from FlextTestsProtocols)
    - tp.DbOracle.* (from FlextDbOracleProtocols)
    """

    class Tests:
        """Project-specific test protocols.

        Extends FlextTestsProtocols.Tests with DbOracle-specific protocols.
        """

        class DbOracle:
            """DbOracle-specific test protocols."""


# Runtime aliases
p = TestsFlextDbOracleProtocols
tp = TestsFlextDbOracleProtocols

__all__ = ["TestsFlextDbOracleProtocols", "p", "tp"]

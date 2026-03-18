"""Test protocol definitions for flext-db-oracle.

Provides TestsFlextDbOracleProtocols, combining p with
FlextDbOracleProtocols for test-specific protocol definitions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import p

from flext_db_oracle.protocols import FlextDbOracleProtocols


class TestsFlextDbOracleProtocols(p, FlextDbOracleProtocols):
    """Test protocols combining p and FlextDbOracleProtocols.

    Provides access to:
    - p.Tests.Docker.* (from p)
    - p.Tests.Factory.* (from p)
    - p.DbOracle.* (from FlextDbOracleProtocols)
    """

    class Tests(p.Tests):
        """Project-specific test protocols.

        Extends p.Tests with DbOracle-specific protocols.
        """

        class DbOracle:
            """DbOracle-specific test protocols."""


__all__ = ["TestsFlextDbOracleProtocols", "p"]

p = TestsFlextDbOracleProtocols

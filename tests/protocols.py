"""Test protocols for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import p
from flext_tests import FlextTestsProtocols


class TestsFlextDbOracleProtocols(FlextTestsProtocols, p):
    """Test protocols for flext-db-oracle."""

    class Tests(FlextTestsProtocols.Tests):
        """Test-specific protocols."""


p = TestsFlextDbOracleProtocols

__all__: list[str] = ["TestsFlextDbOracleProtocols", "p"]

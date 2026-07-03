"""Test constants for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsConstants

from flext_db_oracle import c


class TestsFlextDbOracleConstants(FlextTestsConstants, c):
    """Test constants for flext-db-oracle."""

    class Tests(FlextTestsConstants.Tests):
        """Test-specific constants."""


c = TestsFlextDbOracleConstants

__all__: list[str] = ["TestsFlextDbOracleConstants", "c"]

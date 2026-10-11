"""Test models for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsModels

from flext_db_oracle import FlextDbOracleModels


class TestsFlextDbOracleModels(FlextTestsModels, FlextDbOracleModels):
    """Test models for flext-db-oracle."""

    class Tests(FlextTestsModels.Tests):
        """Test-specific models."""


m = TestsFlextDbOracleModels

__all__: list[str] = ["TestsFlextDbOracleModels", "m"]

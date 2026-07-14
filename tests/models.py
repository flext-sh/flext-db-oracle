"""Test models for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tests import FlextTestsModels

from flext_db_oracle import m

if TYPE_CHECKING:
    from tests import t


class TestsFlextDbOracleModels(FlextTestsModels, m):
    """Test models for flext-db-oracle."""

    class Tests(FlextTestsModels.Tests):
        """Test-specific models."""

        class StubResult(m.DbOracle.DbOracleDomainModel):
            """Minimal result stub for dynamic integration tests."""

            failure: bool = False
            error: str = ""

        class StubPluginEntity(m.DbOracle.DbOracleDomainModel):
            """Stub plugin entity compatible with service integration tests."""

            name: str
            plugin_version: str
            description: str
            author: str
            plugin_type: str
            metadata: t.MappingKV[str, t.FlatContainer]


m = TestsFlextDbOracleModels

__all__: list[str] = ["TestsFlextDbOracleModels", "m"]

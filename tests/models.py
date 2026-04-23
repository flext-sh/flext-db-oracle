"""Test models for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Mapping,
)

from flext_tests import FlextTestsModels

from flext_db_oracle import FlextDbOracleModels
from tests import TestsFlextDbOracleTypes


class TestsFlextDbOracleModels(FlextTestsModels, FlextDbOracleModels):
    """Test models for flext-db-oracle."""

    class DbOracle(FlextDbOracleModels.DbOracle):
        """DbOracle domain test models."""

        class Tests:
            """Test-specific models."""

            class StubResult(FlextDbOracleModels.DbOracle.DbOracleDomainModel):
                """Minimal result stub for dynamic integration tests."""

                failure: bool = False
                error: str = ""

            class StubPluginEntity(FlextDbOracleModels.DbOracle.DbOracleDomainModel):
                """Stub plugin entity compatible with service integration tests."""

                name: str
                plugin_version: str
                description: str
                author: str
                plugin_type: str
                metadata: Mapping[str, TestsFlextDbOracleTypes.FlatContainer]

                @classmethod
                def create(
                    cls,
                    *,
                    name: str,
                    plugin_version: str,
                    description: str,
                    author: str,
                    plugin_type: str,
                    metadata: Mapping[str, TestsFlextDbOracleTypes.FlatContainer],
                ) -> TestsFlextDbOracleModels.DbOracle.Tests.StubPluginEntity:
                    """Create a stub plugin entity with the expected plugin API shape."""
                    return cls(
                        name=name,
                        plugin_version=plugin_version,
                        description=description,
                        author=author,
                        plugin_type=plugin_type,
                        metadata=metadata,
                    )


m = TestsFlextDbOracleModels
__all__: list[str] = ["TestsFlextDbOracleModels", "m"]

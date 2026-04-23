"""Test type aliases for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Callable,
    Mapping,
)

from flext_tests import FlextTestsTypes

from flext_db_oracle import FlextDbOracleTypes, m, p


class TestsFlextDbOracleTypes(FlextTestsTypes, FlextDbOracleTypes):
    """Test type aliases for flext-db-oracle."""

    class DbOracle(FlextDbOracleTypes.DbOracle):
        """DbOracle domain test type aliases."""

        class Tests:
            """Test-specific type aliases."""

            type ApiCoverageReturn = (
                bool
                | m.ConfigMap
                | p.Result[Mapping[str, FlextDbOracleTypes.FlatContainer]]
                | p.Result[str]
                | p.Result[FlextDbOracleTypes.StrSequence]
            )
            type ApiCoverageCallable = Callable[[], ApiCoverageReturn]


t = TestsFlextDbOracleTypes
__all__: list[str] = ["TestsFlextDbOracleTypes", "t"]

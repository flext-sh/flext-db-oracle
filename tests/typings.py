"""Test type aliases for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from flext_tests import FlextTestsTypes

from flext_db_oracle import p, t


class TestsFlextDbOracleTypes(FlextTestsTypes, t):
    """Test type aliases for flext-db-oracle."""

    class Tests(FlextTestsTypes.Tests):
        """Test-specific type aliases."""

        type ApiCoverageReturn = (
            bool
            | p.ConfigMap
            | p.Result[Mapping[str, t.FlatContainer]]
            | p.Result[str]
            | p.Result[t.StrSequence]
        )
        type ApiCoverageCallable = Callable[[], ApiCoverageReturn]
        type ProtocolContract = tuple[str, type, tuple[str, ...]]


t = TestsFlextDbOracleTypes
__all__: list[str] = ["TestsFlextDbOracleTypes", "t"]

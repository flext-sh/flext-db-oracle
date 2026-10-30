"""Test type aliases for flext-db-oracle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from flext_tests import FlextTestsTypes

from flext_db_oracle import FlextDbOracleTypes
from tests import m, p


class TestsFlextDbOracleTypes(FlextTestsTypes, FlextDbOracleTypes):
    """Test type aliases for flext-db-oracle."""

    class Tests(FlextTestsTypes.Tests):
        """Test-specific type aliases."""

        type ApiCoverageReturn = (
            bool
            | m.ConfigMap
            | p.Result[Mapping[str, FlextDbOracleTypes.FlatContainer]]
            | p.Result[str]
            | p.Result[Sequence[str]]
        )
        type ApiCoverageCallable = Callable[[], ApiCoverageReturn]
        type ProtocolContract = tuple[str, type, FlextDbOracleTypes.VariadicTuple[str]]


t = TestsFlextDbOracleTypes
__all__: list[str] = ["TestsFlextDbOracleTypes", "t"]

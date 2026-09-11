"""Test constants for flext-db-oracle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from flext_tests import FlextTestsConstants

from flext_db_oracle import c


class TestsFlextDbOracleConstants(FlextTestsConstants, c):
    """Test constants for flext-db-oracle."""

    class Tests(FlextTestsConstants.Tests):
        """Test-specific constants."""

        ORACLE_CONTAINER = "flext-oracle-db-test"
        SINGER_TYPE_MAP_TEST_CASES: Mapping[str, str] = MappingProxyType({
            "string": "VARCHAR2(4000)",
            "integer": "NUMBER(38)",
            "number": "NUMBER",
            "boolean": "NUMBER(1)",
            "array": "CLOB",
            "t.JsonValue": "CLOB",
            "date-time": "TIMESTAMP",
            "date": "DATE",
            "time": "TIMESTAMP",
        })


c = TestsFlextDbOracleConstants

__all__: list[str] = ["TestsFlextDbOracleConstants", "c"]

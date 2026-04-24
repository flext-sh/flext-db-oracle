"""Unit tests for flext_db_oracle.typings module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import tm

from tests import t


class TestsFlextDbOracleTypingsUnit:
    """Test FlextDbOracleTypes functionality."""

    def test_types_access(self) -> None:
        """Test types can be accessed."""
        tm.that(t, none=False)

"""Unit tests for flext_db_oracle.typings module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleTypes


class TestFlextDbOracleTypes:
    """Test FlextDbOracleTypes functionality."""

    def test_types_access(self) -> None:
        """Test types can be accessed."""
        assert FlextDbOracleTypes is not None

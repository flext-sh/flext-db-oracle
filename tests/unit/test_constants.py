"""Unit tests for flext_db_oracle.constants module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleConstants


class TestFlextDbOracleConstants:
    """Test FlextDbOracleConstants functionality."""

    def test_constants_access(self) -> None:
        """Test constants can be accessed."""
        assert FlextDbOracleConstants is not None
        assert hasattr(FlextDbOracleConstants, "Network")

    def test_network_constants(self) -> None:
        """Test network constants."""
        assert FlextDbOracleConstants.Network.MIN_PORT == 1024
        assert FlextDbOracleConstants.Network.MAX_PORT == 65535

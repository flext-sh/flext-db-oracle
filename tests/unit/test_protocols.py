"""Unit tests for flext_db_oracle.protocols module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleProtocols


class TestFlextDbOracleProtocols:
    """Test FlextDbOracleProtocols functionality."""

    def test_protocols_access(self) -> None:
        """Test protocols can be accessed."""
        assert FlextDbOracleProtocols is not None

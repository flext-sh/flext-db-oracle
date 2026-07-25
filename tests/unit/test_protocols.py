"""Unit tests for flext_db_oracle.protocols module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import tm

from tests.protocols import p


class TestsFlextDbOracleProtocolsUnit:
    """Test FlextDbOracleProtocols functionality."""

    def test_protocols_access(self) -> None:
        """Test protocols can be accessed."""
        tm.that(p, none=False)

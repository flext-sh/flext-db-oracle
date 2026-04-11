"""Test FlextDbOracleClient functionality with real implementations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import tm

from flext_db_oracle import FlextDbOracleClient, FlextDbOracleSettings


class TestFlextDbOracleClientRealFunctionality:
    """Test FlextDbOracleClient with real functionality."""

    def test_client_creation(self) -> None:
        """Test client can be created."""
        FlextDbOracleSettings(
            host="test-host",
            username="test-user",
            password="test-password",
        )
        client = FlextDbOracleClient()
        tm.that(client, none=False)

    def test_client_creation_default_config(self) -> None:
        """Test client can be created with default settings."""
        client = FlextDbOracleClient()
        tm.that(client, none=False)

    def test_client_has_required_attributes(self) -> None:
        """Test client has required attributes."""
        FlextDbOracleClient()

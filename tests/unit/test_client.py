"""Test FlextDbOracleClient functionality with real implementations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleClient, FlextDbOracleSettings


class TestFlextDbOracleClientRealFunctionality:
    """Test FlextDbOracleClient with real functionality."""

    def test_client_creation(self) -> None:
        """Test client can be created."""
        # Create config first
        FlextDbOracleSettings(
            host="test-host",
            username="test-user",
            password="test-password",
        )
        # Create client without passing config (it will create default internally)
        client = FlextDbOracleClient()
        assert client is not None
        assert hasattr(client, "logger")

    def test_client_creation_default_config(self) -> None:
        """Test client can be created with default config."""
        client = FlextDbOracleClient()
        assert client is not None
        assert hasattr(client, "debug")
        assert hasattr(client, "current_connection")

    def test_client_has_required_attributes(self) -> None:
        """Test client has required attributes."""
        client = FlextDbOracleClient()
        assert hasattr(client, "debug")
        assert hasattr(client, "current_connection")
        assert hasattr(client, "user_preferences")
        assert hasattr(client, "logger")

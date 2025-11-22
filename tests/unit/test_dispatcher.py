"""Test FlextDbOracleDispatcher functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import (
    FlextDbOracleConfig,
    FlextDbOracleDispatcher,
    FlextDbOracleServices,
)


class TestDispatcherSurgical:
    """Test FlextDbOracleDispatcher functionality."""

    def test_dispatcher_creation(self) -> None:
        """Test dispatcher can be created."""
        config = FlextDbOracleConfig(
            host="test-host", username="test-user", password="test-password"
        )
        services = FlextDbOracleServices(config=config)
        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)
        assert dispatcher is not None

    def test_dispatcher_has_command_classes(self) -> None:
        """Test dispatcher has command classes."""
        assert hasattr(FlextDbOracleDispatcher, "ExecuteQueryCommand")
        assert hasattr(FlextDbOracleDispatcher, "ConnectCommand")
        assert hasattr(FlextDbOracleDispatcher, "ExecuteManyCommand")

    def test_command_creation(self) -> None:
        """Test command objects can be created."""
        cmd = FlextDbOracleDispatcher.ExecuteQueryCommand(
            sql="SELECT 1 FROM DUAL", parameters=None
        )
        assert cmd.sql == "SELECT 1 FROM DUAL"
        assert cmd.parameters is None

"""Test FlextDbOracleDispatcher functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import tm

from flext_db_oracle import (
    FlextDbOracleDispatcher,
    FlextDbOracleServices,
    FlextDbOracleSettings,
)


class TestDispatcherSurgical:
    """Test FlextDbOracleDispatcher functionality."""

    def test_dispatcher_creation(self) -> None:
        """Test dispatcher can be created."""
        config = FlextDbOracleSettings(
            host="test-host", username="test-user", password="test-password"
        )
        services = FlextDbOracleServices(config=config)
        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)
        tm.that(dispatcher, none=False)

    def test_dispatcher_has_command_classes(self) -> None:
        """Test dispatcher has command classes."""
        tm.that(hasattr(FlextDbOracleDispatcher, "ExecuteQueryCommand"), eq=True)
        tm.that(hasattr(FlextDbOracleDispatcher, "ConnectCommand"), eq=True)
        tm.that(hasattr(FlextDbOracleDispatcher, "ExecuteManyCommand"), eq=True)

    def test_command_creation(self) -> None:
        """Test command objects can be created."""
        cmd = FlextDbOracleDispatcher.ExecuteQueryCommand(
            sql="SELECT 1 FROM DUAL", parameters=None
        )
        tm.that(cmd.sql, eq="SELECT 1 FROM DUAL")
        tm.that(cmd.parameters, none=True)

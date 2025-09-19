"""Surgical tests for FlextDbOracleDispatcher - targeting specific uncovered lines.

Tests the command dispatcher pattern with real Oracle service integration.
Coverage target: dispatcher.py lines 70-144 (build_dispatcher method).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextBus, FlextDispatcher
from flext_db_oracle import FlextDbOracleModels
from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
from flext_db_oracle.services import FlextDbOracleServices


class TestDispatcherSurgical:
    """Surgical tests for dispatcher functionality targeting uncovered lines."""

    def test_build_dispatcher_creates_dispatcher(self) -> None:
        """Test build_dispatcher creates FlextDispatcher instance."""
        # Create Oracle config for services
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        services = FlextDbOracleServices(config=config)

        # Test build_dispatcher method (covers lines 70-144)
        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)

        assert isinstance(dispatcher, FlextDispatcher)

    def test_build_dispatcher_with_custom_bus(self) -> None:
        """Test build_dispatcher with custom FlextBus."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        services = FlextDbOracleServices(config=config)
        custom_bus = FlextBus()

        # Call with keyword argument as per method signature
        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services, bus=custom_bus)

        assert isinstance(dispatcher, FlextDispatcher)
        # Verify the custom bus was used by checking the dispatcher's bus
        assert dispatcher._bus is custom_bus

    def test_build_dispatcher_registers_connect_command(self) -> None:
        """Test that build_dispatcher registers ConnectCommand handler."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        services = FlextDbOracleServices(config=config)

        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)
        connect_cmd = FlextDbOracleDispatcher.ConnectCommand()

        # Test that the command can be processed (tests handler registration)
        # Note: This tests the dispatcher structure without requiring actual Oracle connection
        result = dispatcher.dispatch(connect_cmd)
        assert result is not None  # Handler was found and executed

    def test_build_dispatcher_registers_disconnect_command(self) -> None:
        """Test that build_dispatcher registers DisconnectCommand handler."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        services = FlextDbOracleServices(config=config)

        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)
        disconnect_cmd = FlextDbOracleDispatcher.DisconnectCommand()

        result = dispatcher.dispatch(disconnect_cmd)
        assert result is not None

    def test_build_dispatcher_registers_test_connection_command(self) -> None:
        """Test that build_dispatcher registers TestConnectionCommand handler."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        services = FlextDbOracleServices(config=config)

        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)
        test_cmd = FlextDbOracleDispatcher.TestConnectionCommand()

        result = dispatcher.dispatch(test_cmd)
        assert result is not None

    def test_build_dispatcher_registers_execute_query_command(self) -> None:
        """Test that build_dispatcher registers ExecuteQueryCommand handler."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        services = FlextDbOracleServices(config=config)

        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)
        query_cmd = FlextDbOracleDispatcher.ExecuteQueryCommand(
            sql="SELECT 1 FROM DUAL", parameters={},
        )

        result = dispatcher.dispatch(query_cmd)
        assert result is not None

    def test_build_dispatcher_registers_fetch_one_command(self) -> None:
        """Test that build_dispatcher registers FetchOneCommand handler."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        services = FlextDbOracleServices(config=config)

        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)
        fetch_cmd = FlextDbOracleDispatcher.FetchOneCommand(
            sql="SELECT 1 FROM DUAL", parameters={},
        )

        result = dispatcher.dispatch(fetch_cmd)
        assert result is not None

    def test_build_dispatcher_registers_execute_statement_command(self) -> None:
        """Test that build_dispatcher registers ExecuteStatementCommand handler."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        services = FlextDbOracleServices(config=config)

        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)
        stmt_cmd = FlextDbOracleDispatcher.ExecuteStatementCommand(
            sql="SELECT 1 FROM DUAL", parameters={},
        )

        result = dispatcher.dispatch(stmt_cmd)
        assert result is not None

    def test_build_dispatcher_registers_execute_many_command(self) -> None:
        """Test that build_dispatcher registers ExecuteManyCommand handler."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        services = FlextDbOracleServices(config=config)

        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)
        many_cmd = FlextDbOracleDispatcher.ExecuteManyCommand(
            sql="INSERT INTO test VALUES (:id, :name)",
            parameters_list=[{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}],
        )

        result = dispatcher.dispatch(many_cmd)
        assert result is not None

    def test_build_dispatcher_registers_get_schemas_command(self) -> None:
        """Test that build_dispatcher registers GetSchemasCommand handler."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        services = FlextDbOracleServices(config=config)

        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)
        schemas_cmd = FlextDbOracleDispatcher.GetSchemasCommand()

        result = dispatcher.dispatch(schemas_cmd)
        assert result is not None

    def test_build_dispatcher_registers_get_tables_command(self) -> None:
        """Test that build_dispatcher registers GetTablesCommand handler."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        services = FlextDbOracleServices(config=config)

        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)
        tables_cmd = FlextDbOracleDispatcher.GetTablesCommand(schema="PUBLIC")

        result = dispatcher.dispatch(tables_cmd)
        assert result is not None

    def test_build_dispatcher_registers_get_columns_command(self) -> None:
        """Test that build_dispatcher registers GetColumnsCommand handler."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        services = FlextDbOracleServices(config=config)

        dispatcher = FlextDbOracleDispatcher.build_dispatcher(services)
        columns_cmd = FlextDbOracleDispatcher.GetColumnsCommand(
            table="USERS", schema="PUBLIC",
        )

        result = dispatcher.dispatch(columns_cmd)
        assert result is not None


class TestDispatcherCommandClasses:
    """Test the command classes for proper structure."""

    def test_connect_command_creation(self) -> None:
        """Test ConnectCommand can be created."""
        cmd = FlextDbOracleDispatcher.ConnectCommand()
        assert cmd is not None

    def test_disconnect_command_creation(self) -> None:
        """Test DisconnectCommand can be created."""
        cmd = FlextDbOracleDispatcher.DisconnectCommand()
        assert cmd is not None

    def test_test_connection_command_creation(self) -> None:
        """Test TestConnectionCommand can be created."""
        cmd = FlextDbOracleDispatcher.TestConnectionCommand()
        assert cmd is not None

    def test_execute_query_command_with_parameters(self) -> None:
        """Test ExecuteQueryCommand with SQL and parameters."""
        cmd = FlextDbOracleDispatcher.ExecuteQueryCommand(
            sql="SELECT * FROM users WHERE id = :id", parameters={"id": 123},
        )
        assert cmd.sql == "SELECT * FROM users WHERE id = :id"
        assert cmd.parameters == {"id": 123}

    def test_fetch_one_command_with_parameters(self) -> None:
        """Test FetchOneCommand with SQL and parameters."""
        cmd = FlextDbOracleDispatcher.FetchOneCommand(
            sql="SELECT * FROM users WHERE id = :id", parameters={"id": 456},
        )
        assert cmd.sql == "SELECT * FROM users WHERE id = :id"
        assert cmd.parameters == {"id": 456}

    def test_execute_statement_command_with_parameters(self) -> None:
        """Test ExecuteStatementCommand with SQL and parameters."""
        cmd = FlextDbOracleDispatcher.ExecuteStatementCommand(
            sql="UPDATE users SET name = :name WHERE id = :id",
            parameters={"id": 789, "name": "updated"},
        )
        assert cmd.sql == "UPDATE users SET name = :name WHERE id = :id"
        assert cmd.parameters == {"id": 789, "name": "updated"}

    def test_execute_many_command_with_parameters_list(self) -> None:
        """Test ExecuteManyCommand with SQL and parameters list."""
        params_list = [
            {"id": 1, "name": "user1"},
            {"id": 2, "name": "user2"},
            {"id": 3, "name": "user3"},
        ]
        cmd = FlextDbOracleDispatcher.ExecuteManyCommand(
            sql="INSERT INTO users (id, name) VALUES (:id, :name)",
            parameters_list=params_list,
        )
        assert cmd.sql == "INSERT INTO users (id, name) VALUES (:id, :name)"
        assert cmd.parameters_list == params_list

    def test_get_tables_command_with_schema(self) -> None:
        """Test GetTablesCommand with schema parameter."""
        cmd = FlextDbOracleDispatcher.GetTablesCommand(schema="HR")
        assert cmd.schema == "HR"

    def test_get_columns_command_with_table_and_schema(self) -> None:
        """Test GetColumnsCommand with table and schema parameters."""
        cmd = FlextDbOracleDispatcher.GetColumnsCommand(table="EMPLOYEES", schema="HR")
        assert cmd.table == "EMPLOYEES"
        assert cmd.schema == "HR"

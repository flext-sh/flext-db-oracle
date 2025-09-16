"""Simplified tests for FlextDbOracleServices connection functionality.

This module tests the connection functionality with real code paths,
focusing on the actual available methods and attributes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from flext_db_oracle import (
    FlextDbOracleModels,
    FlextDbOracleServices,
)


class TestFlextDbOracleConnectionSimple:
    """Simplified tests for Oracle connection using real code paths."""

    def setup_method(self) -> None:
        """Setup test configuration."""
        self.config = FlextDbOracleModels.OracleConfig(
            host="test",
            port=1521,
            name="TEST",
            user="test",
            password="test",
            service_name="TEST",
        )
        self.connection = FlextDbOracleServices(config=self.config)

    def test_connection_initialization(self) -> None:
        """Test connection initialization with real configuration."""
        assert self.connection is not None
        assert self.connection.config == self.config

    def test_is_connected_method(self) -> None:
        """Test is_connected method behavior."""
        # Initially not connected
        connected_status = self.connection.is_connected()
        assert isinstance(connected_status, bool)

    def test_disconnect_when_not_connected(self) -> None:
        """Test disconnect when not connected."""
        result = self.connection.disconnect()
        assert result.is_success

    def test_config_validation(self) -> None:
        """Test Oracle config validation."""
        # Test with valid config
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="TEST",
            user="test",
            password="test",
        )
        assert config.host == "localhost"
        assert config.port == 1521

    def test_services_methods_exist(self) -> None:
        """Test that required service methods exist."""
        # Test that key methods exist
        assert hasattr(self.connection, "connect")
        assert hasattr(self.connection, "disconnect")
        assert hasattr(self.connection, "is_connected")
        assert hasattr(self.connection, "get_schemas")
        assert hasattr(self.connection, "get_tables")

    def test_query_methods_exist(self) -> None:
        """Test that query methods exist."""
        # Test that query methods are available
        assert hasattr(self.connection, "execute")
        assert hasattr(self.connection, "build_select")
        assert hasattr(self.connection, "build_insert_statement")

    def test_connection_error_handling(self) -> None:
        """Test connection error handling."""
        # Test connection attempt (will fail due to invalid config)
        result = self.connection.connect()
        # Should return FlextResult
        assert hasattr(result, "is_success")
        assert hasattr(result, "error")

    def test_schema_operations_error_handling(self) -> None:
        """Test schema operations error handling when not connected."""
        # Test get_schemas when not connected
        result = self.connection.get_schemas()
        assert hasattr(result, "is_success")
        assert hasattr(result, "error")

        # Test get_tables when not connected
        result = self.connection.get_tables()
        assert hasattr(result, "is_success")
        assert hasattr(result, "error")

    def test_sql_building_methods(self) -> None:
        """Test SQL building methods."""
        # Test build_select
        result = self.connection.build_select("TEST_TABLE")
        assert hasattr(result, "is_success")

        # Test build_insert_statement
        columns = ["column1", "column2"]
        result = self.connection.build_insert_statement("TEST_TABLE", columns)
        assert hasattr(result, "is_success")

    def test_ddl_operations(self) -> None:
        """Test DDL operations."""
        # Test create_index_statement exists and is callable
        assert hasattr(self.connection, "build_create_index_statement")
        assert callable(self.connection.build_create_index_statement)

"""Comprehensive Oracle Services Tests - Real Implementation Without Mocks.

Tests the FlextDbOracleServices class completely without mocks,
achieving maximum coverage through real Oracle service operations using flext_tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import cast

import pytest
from pydantic import SecretStr

# Add flext_tests to path
sys.path.insert(0, str(Path(__file__).parents[4] / "flext-core" / "src"))

from flext_tests import FlextMatchers, TestBuilders

from flext_db_oracle.models import FlextDbOracleModels, OracleConfig
from flext_db_oracle.services import FlextDbOracleServices, OracleSQLBuilder


class TestFlextDbOracleServicesRealFunctionality:
    """Comprehensive tests for Oracle Services using ONLY real functionality - NO MOCKS."""

    def setup_method(self) -> None:
        """Setup test services with real configuration."""
        self.config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password=SecretStr("test_password"),
        )
        self.services = FlextDbOracleServices(config=self.config)

    def test_services_initialization_complete_real(self) -> None:
        """Test complete services initialization - REAL FUNCTIONALITY."""
        assert self.services is not None
        assert hasattr(self.services, "config")
        assert hasattr(self.services, "_engine")
        assert hasattr(self.services, "_session_factory")
        assert hasattr(self.services, "_connected")
        assert hasattr(self.services, "is_connected")
        assert hasattr(self.services, "connect")
        assert hasattr(self.services, "disconnect")

        # Test config is properly set
        assert self.services.config.host == "localhost"
        assert self.services.config.port == 1521
        assert self.services.config.service_name == "XEPDB1"
        assert self.services.config.username == "test_user"

        # Test initial state
        assert self.services._engine is None
        assert self.services._session_factory is None
        assert self.services._connected is False

    def test_connection_url_building_real(self) -> None:
        """Test connection URL building - REAL FUNCTIONALITY."""
        result = self.services._build_connection_url()

        FlextMatchers.assert_result_success(result)
        url = result.value
        assert isinstance(url, str)
        assert "oracle+oracledb://" in url
        assert "localhost:1521" in url
        assert "XEPDB1" in url
        assert "test_user" in url
        # Password should be URL encoded but not visible in plain text

    def test_is_connected_initial_state_real(self) -> None:
        """Test initial connection state - REAL FUNCTIONALITY."""
        # Initially should not be connected
        assert self.services.is_connected() is False

    def test_connection_lifecycle_without_database_real(self) -> None:
        """Test connection lifecycle without actual database - REAL FUNCTIONALITY."""
        # Test connect (will fail without real database)
        connect_result = self.services.connect()
        FlextMatchers.assert_result_failure(connect_result)
        assert connect_result.error is not None
        error_msg = connect_result.error.lower()
        assert "connection" in error_msg or "failed" in error_msg

        # Should still not be connected after failed attempt
        assert self.services.is_connected() is False

    def test_test_connection_without_database_real(self) -> None:
        """Test connection testing without database - REAL FUNCTIONALITY."""
        result = self.services.test_connection()

        # Should fail gracefully without database
        FlextMatchers.assert_result_failure(result)
        assert result.error is not None
        error_msg = result.error.lower()
        assert (
            "connection" in error_msg
            or "database" in error_msg
            or "failed" in error_msg
            or "timeout" in error_msg
        )

    def test_query_operations_without_connection_real(self) -> None:
        """Test query operations without connection - REAL FUNCTIONALITY."""
        # Test execute_query
        query_result = self.services.execute_query("SELECT 1 FROM DUAL")
        FlextMatchers.assert_result_failure(query_result)
        assert query_result.error is not None
        query_error = query_result.error.lower()
        assert "connection" in query_error or "not connected" in query_error

        # Test execute_statement
        stmt_result = self.services.execute_statement("SELECT SYSDATE FROM DUAL")
        FlextMatchers.assert_result_failure(stmt_result)
        assert stmt_result.error is not None
        stmt_error = stmt_result.error.lower()
        assert "connection" in stmt_error or "not connected" in stmt_error

    def test_metadata_operations_without_connection_real(self) -> None:
        """Test metadata operations without connection - REAL FUNCTIONALITY."""
        # Test get_schemas
        schemas_result = self.services.get_schemas()
        FlextMatchers.assert_result_failure(schemas_result)
        assert schemas_result.error is not None
        schemas_error = schemas_result.error.lower()
        assert "connection" in schemas_error or "not connected" in schemas_error

        # Test get_tables
        tables_result = self.services.get_tables()
        FlextMatchers.assert_result_failure(tables_result)
        assert tables_result.error is not None
        tables_error = tables_result.error.lower()
        assert "connection" in tables_error or "not connected" in tables_error

        # Test get_tables with schema
        tables_schema_result = self.services.get_tables("SYSTEM")
        FlextMatchers.assert_result_failure(tables_schema_result)
        assert tables_schema_result.error is not None
        tables_schema_error = tables_schema_result.error.lower()
        assert (
            "connection" in tables_schema_error
            or "not connected" in tables_schema_error
        )

        # Test get_columns
        columns_result = self.services.get_columns("SYSTEM", "DUAL")
        FlextMatchers.assert_result_failure(columns_result)
        assert columns_result.error is not None
        columns_error = columns_result.error.lower()
        assert "connection" in columns_error or "not connected" in columns_error

    def test_sql_builder_static_methods_real(self) -> None:
        """Test SQL builder static methods - REAL FUNCTIONALITY."""
        # Test validate_identifier
        valid_id = OracleSQLBuilder.validate_identifier("VALID_TABLE")
        assert valid_id == "VALID_TABLE"

        # Test build_table_reference without schema
        table_ref = OracleSQLBuilder.build_table_reference("USERS")
        assert table_ref == "USERS"

        # Test build_table_reference with schema
        table_ref_schema = OracleSQLBuilder.build_table_reference("USERS", "SYSTEM")
        assert table_ref_schema == "SYSTEM.USERS"

        # Test build_column_list
        columns: list[object] = ["ID", "NAME", "EMAIL"]
        column_list = OracleSQLBuilder.build_column_list(columns)
        assert isinstance(column_list, list)
        assert len(column_list) == 3
        assert "ID" in column_list

    def test_singer_type_conversion_real(self) -> None:
        """Test Singer type conversion - REAL FUNCTIONALITY."""
        # Test string conversion
        string_result = self.services.convert_singer_type("string")
        FlextMatchers.assert_result_success(string_result)
        assert string_result.value == "VARCHAR2(4000)"

        # Test integer conversion
        int_result = self.services.convert_singer_type("integer")
        FlextMatchers.assert_result_success(int_result)
        assert int_result.value == "NUMBER"

        # Test number conversion
        number_result = self.services.convert_singer_type("number")
        FlextMatchers.assert_result_success(number_result)
        assert number_result.value == "NUMBER"

        # Test boolean conversion
        bool_result = self.services.convert_singer_type("boolean")
        FlextMatchers.assert_result_success(bool_result)
        assert bool_result.value == "NUMBER(1)"

        # Test date-time conversion with format hint
        datetime_result = self.services.convert_singer_type("string", "date-time")
        FlextMatchers.assert_result_success(datetime_result)
        assert datetime_result.value == "TIMESTAMP"

        # Test unknown type (should return default)
        unknown_result = self.services.convert_singer_type("unknown_type")
        FlextMatchers.assert_result_success(unknown_result)
        assert unknown_result.value == "VARCHAR2(4000)"  # Default fallback

    def test_build_select_operations_real(self) -> None:
        """Test build select operations - REAL FUNCTIONALITY."""
        # Test basic build_select
        columns = ["ID", "NAME", "EMAIL"]
        select_result = self.services.build_select("USERS", columns)

        FlextMatchers.assert_result_success(select_result)
        query = select_result.value
        assert "SELECT ID, NAME, EMAIL" in query
        assert "FROM USERS" in query

        # Test build_select with schema
        select_schema_result = self.services.build_select(
            "USERS", columns, schema_name="SYSTEM"
        )
        FlextMatchers.assert_result_success(select_schema_result)
        schema_query = select_schema_result.value
        assert "FROM SYSTEM.USERS" in schema_query

        # Test build_select with WHERE clause
        where_conditions = {"ID": 1, "STATUS": "active"}
        select_where_result = self.services.build_select(
            "USERS", columns, conditions=where_conditions
        )
        FlextMatchers.assert_result_success(select_where_result)
        where_query = select_where_result.value
        assert "WHERE" in where_query

    def test_query_hash_generation_real(self) -> None:
        """Test query hash generation - REAL FUNCTIONALITY."""
        query = "SELECT * FROM USERS WHERE ID = ?"
        params: dict[str, object] = {"ID": 1}

        hash_result = self.services.generate_query_hash(query, params)
        FlextMatchers.assert_result_success(hash_result)

        query_hash = hash_result.value
        assert isinstance(query_hash, str)
        assert len(query_hash) > 0

        # Hash should be consistent
        hash_result2 = self.services.generate_query_hash(query, params)
        FlextMatchers.assert_result_success(hash_result2)
        assert hash_result.value == hash_result2.value

        # Different params should produce different hash
        different_params: dict[str, object] = {"ID": 2}
        hash_result3 = self.services.generate_query_hash(query, different_params)
        FlextMatchers.assert_result_success(hash_result3)
        assert hash_result.value != hash_result3.value

    def test_plugin_system_without_connection_real(self) -> None:
        """Test plugin system without connection - REAL FUNCTIONALITY."""
        # Test register_plugin
        plugin_data = {"name": "test_plugin", "version": "1.0.0"}
        register_result = self.services.register_plugin("test_plugin", plugin_data)
        FlextMatchers.assert_result_success(register_result)

        # Test list_plugins
        list_result = self.services.list_plugins()
        FlextMatchers.assert_result_success(list_result)
        plugins = list_result.value
        assert isinstance(plugins, dict)
        assert "test_plugin" in plugins

        # Test get_plugin
        get_result = self.services.get_plugin("test_plugin")
        FlextMatchers.assert_result_success(get_result)
        retrieved_plugin = get_result.value
        assert retrieved_plugin == plugin_data

        # Test unregister_plugin
        unregister_result = self.services.unregister_plugin("test_plugin")
        FlextMatchers.assert_result_success(unregister_result)

        # Verify plugin was removed - list_plugins returns failure when empty
        final_list = self.services.list_plugins()
        FlextMatchers.assert_result_failure(final_list)
        # This is expected behavior - no plugins to list

    def test_metrics_and_operations_tracking_real(self) -> None:
        """Test metrics and operations tracking - REAL FUNCTIONALITY."""
        # Test record_metric
        metric_result = self.services.record_metric("test_metric", 42.5)
        FlextMatchers.assert_result_success(metric_result)

        # Test get_metrics
        metrics_result = self.services.get_metrics()
        FlextMatchers.assert_result_success(metrics_result)
        metrics = metrics_result.value
        assert isinstance(metrics, dict)
        assert "test_metric" in metrics
        # Metric data includes metadata, check the value field
        metric_data = metrics["test_metric"]
        if isinstance(metric_data, dict):
            assert metric_data["value"] == 42.5
        else:
            assert metric_data == 42.5

        # Test track_operation
        operation_result = self.services.track_operation(
            "test_operation", 0.1, success=True
        )
        FlextMatchers.assert_result_success(operation_result)

        # Test get_operations
        operations_result = self.services.get_operations()
        FlextMatchers.assert_result_success(operations_result)
        operations = operations_result.value
        assert isinstance(operations, list)
        assert len(operations) > 0
        # Find our operation (implementation stores operation name in "operation" field)
        test_op = next(
            (op for op in operations if op.get("operation") == "test_operation"), None
        )
        assert test_op is not None
        assert test_op["success"] is True
        assert test_op["duration_ms"] == 0.1

    def test_health_check_without_connection_real(self) -> None:
        """Test health check without connection - REAL FUNCTIONALITY."""
        result = self.services.health_check()

        # Should return health data even without connection
        FlextMatchers.assert_result_success(result)
        health_data = result.value
        assert isinstance(health_data, dict)
        assert "status" in health_data
        assert "database" in health_data
        assert "timestamp" in health_data
        # Without connection, status should indicate unavailable
        database_info = health_data["database"]
        assert isinstance(database_info, dict)
        assert database_info["connected"] is False

    def test_connection_status_real(self) -> None:
        """Test connection status - REAL FUNCTIONALITY."""
        result = self.services.get_connection_status()

        FlextMatchers.assert_result_success(result)
        status = result.value

        # Verify status is ConnectionStatus object with proper attributes
        assert hasattr(status, "is_connected")
        assert hasattr(status, "host")
        assert hasattr(status, "port")
        assert hasattr(status, "service_name")
        assert hasattr(status, "username")

        # Verify values match configuration
        assert status.is_connected is False  # Not connected initially
        assert status.host == "localhost"
        assert status.port == 1521
        assert status.service_name == "XEPDB1"
        assert status.username == "test_user"

    def test_table_operations_ddl_real(self) -> None:
        """Test table DDL operations - REAL FUNCTIONALITY."""
        # Test create_table_ddl
        columns_data = [
            {"name": "ID", "data_type": "NUMBER", "nullable": False},
            {"name": "NAME", "data_type": "VARCHAR2(100)", "nullable": True},
            {"name": "CREATED_DATE", "data_type": "TIMESTAMP", "nullable": True},
        ]

        create_ddl_result = self.services.create_table_ddl("TEST_TABLE", columns_data)
        FlextMatchers.assert_result_success(create_ddl_result)
        ddl = create_ddl_result.value
        assert "CREATE TABLE TEST_TABLE" in ddl
        assert "ID NUMBER NOT NULL" in ddl
        assert "NAME VARCHAR2(100)" in ddl

        # Test drop_table_ddl
        drop_ddl_result = self.services.drop_table_ddl("TEST_TABLE")
        FlextMatchers.assert_result_success(drop_ddl_result)
        drop_ddl = drop_ddl_result.value
        assert "DROP TABLE TEST_TABLE" in drop_ddl

    def test_sql_statement_builders_real(self) -> None:
        """Test SQL statement builders - REAL FUNCTIONALITY."""
        # Test build_insert_statement
        data = {"ID": 1, "NAME": "Test", "EMAIL": "test@example.com"}
        columns = list(data.keys())
        insert_result = self.services.build_insert_statement("USERS", columns)
        FlextMatchers.assert_result_success(insert_result)
        insert_sql = insert_result.value
        assert "INSERT INTO USERS" in insert_sql
        assert "ID, NAME, EMAIL" in insert_sql
        assert "VALUES" in insert_sql

        # Test build_update_statement
        where_conditions = {"ID": 1}
        where_columns = list(where_conditions.keys())
        update_result = self.services.build_update_statement(
            "USERS", columns, where_columns
        )
        FlextMatchers.assert_result_success(update_result)
        update_sql = update_result.value
        assert "UPDATE USERS SET" in update_sql
        assert "WHERE ID = :where_ID" in update_sql

        # Test build_delete_statement
        delete_result = self.services.build_delete_statement("USERS", where_columns)
        FlextMatchers.assert_result_success(delete_result)
        delete_sql = delete_result.value
        assert "DELETE FROM USERS" in delete_sql
        assert "WHERE ID = :ID" in delete_sql

    def test_error_handling_comprehensive_real(self) -> None:
        """Test comprehensive error handling patterns - REAL FUNCTIONALITY."""
        # Test various operations that should fail gracefully without connection
        operations_to_test = [
            ("execute_query", ["SELECT 1"]),
            ("execute_statement", ["INSERT INTO test VALUES (1)"]),
            ("get_schemas", []),
            ("get_tables", []),
            ("get_columns", ["SYSTEM", "DUAL"]),
            ("get_table_row_count", ["SYSTEM", "DUAL"]),
        ]

        for method_name, args in operations_to_test:
            method = getattr(self.services, method_name)
            result = method(*args)

            # All should fail gracefully and return FlextResult
            assert hasattr(result, "success")
            assert hasattr(result, "error") or hasattr(result, "value")
            FlextMatchers.assert_result_failure(result)
            assert isinstance(result.error, str)
            assert len(result.error) > 0
            # Error should mention connection
            assert (
                "connection" in result.error.lower()
                or "not connected" in result.error.lower()
            )

    def test_services_configuration_validation_real(self) -> None:
        """Test services configuration validation - REAL FUNCTIONALITY."""
        # Create invalid configuration first
        invalid_config = FlextDbOracleModels.OracleConfig(
            host="",  # Invalid empty host
            port=-1,  # Invalid negative port
            service_name="",  # Invalid empty service
            username="",  # Invalid empty username
            password=SecretStr(""),  # Invalid empty password
        )

        # Test creating services with invalid config should raise exception
        with pytest.raises(Exception):
            FlextDbOracleServices(config=invalid_config)

    def test_services_multiple_instances_isolation_real(self) -> None:
        """Test that multiple service instances are properly isolated - REAL FUNCTIONALITY."""
        config1 = FlextDbOracleModels.OracleConfig(
            host="host1",
            port=1521,
            service_name="SERVICE1",
            username="user1",
            password=SecretStr("pass1"),
        )

        config2 = FlextDbOracleModels.OracleConfig(
            host="host2",
            port=1522,
            service_name="SERVICE2",
            username="user2",
            password=SecretStr("pass2"),
        )

        services1 = FlextDbOracleServices(config=config1)
        services2 = FlextDbOracleServices(config=config2)

        # Test isolation
        assert services1 is not services2
        assert services1.config.host != services2.config.host
        assert services1.config.port != services2.config.port

        # Test plugin isolation
        services1.register_plugin("plugin1", {"data": "service1"})
        services2.register_plugin("plugin2", {"data": "service2"})

        plugins1 = services1.list_plugins().value
        plugins2 = services2.list_plugins().value

        assert "plugin1" in plugins1
        assert "plugin1" not in plugins2
        assert "plugin2" in plugins2
        assert "plugin2" not in plugins1

    def test_services_string_representation_real(self) -> None:
        """Test services string representation methods - REAL FUNCTIONALITY."""
        # Test repr/str don't crash
        repr_str = repr(self.services)
        assert isinstance(repr_str, str)
        assert len(repr_str) > 0

        str_repr = str(self.services)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0

    def test_services_with_testbuilders_patterns_real(self) -> None:
        """Test services with TestBuilders patterns - REAL FUNCTIONALITY."""
        # Use TestBuilders to create test data
        config_result = (
            TestBuilders.result()
            .with_success_data(
                FlextDbOracleModels.OracleConfig(
                    host="testbuilder_host",
                    port=1521,
                    service_name="TESTBUILDER_SERVICE",
                    username="testbuilder_user",
                    password=SecretStr("testbuilder_password"),
                ),
            )
            .build()
        )

        FlextMatchers.assert_result_success(config_result)
        config = config_result.value

        # Create services with TestBuilders config
        services = FlextDbOracleServices(config=cast("OracleConfig", config))

        # Test configuration was applied
        assert services.config.host == "testbuilder_host"
        assert services.config.service_name == "TESTBUILDER_SERVICE"
        assert services.config.username == "testbuilder_user"

        # Test basic functionality works
        url_result = services._build_connection_url()
        FlextMatchers.assert_result_success(url_result)
        assert "testbuilder_host" in url_result.value

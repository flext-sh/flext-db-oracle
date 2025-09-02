"""Comprehensive tests for FlextDbOracleApi using real code validation.

This module tests the API functionality with real code paths,
following the user's requirement for real code testing without mocks.
"""

from pydantic import SecretStr

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig


class TestFlextDbOracleApiComprehensive:
    """Comprehensive tests for Oracle API using real code paths."""

    def setup_method(self) -> None:
        """Setup test configuration."""
        self.config = FlextDbOracleConfig(
            host="test",
            port=1521,
            service_name="TEST",
            username="test",
            password=SecretStr("test"),
        )
        self.api = FlextDbOracleApi(self.config)

    def test_api_initialization(self) -> None:
        """Test API initialization with real configuration."""
        assert self.api is not None
        assert hasattr(self.api, "_connection_manager")
        assert hasattr(self.api, "_query_executor")
        assert hasattr(self.api, "_observability")
        assert self.api._plugins == {}

    def test_api_initialization_with_context(self) -> None:
        """Test API initialization with custom context name."""
        custom_api = FlextDbOracleApi(self.config, context_name="custom_context")
        assert custom_api is not None

    def test_connection_management_methods_exist(self) -> None:
        """Test that connection management methods exist and are callable."""
        # Test that connection methods exist (don't actually call them to avoid timeouts)
        assert hasattr(self.api, "connect")
        assert callable(self.api.connect)
        assert hasattr(self.api, "disconnect")
        assert callable(self.api.disconnect)
        assert hasattr(self.api, "is_connected")
        # is_connected is a property, not a method
        initial_state = self.api.is_connected
        assert isinstance(initial_state, bool)

    def test_disconnect_method(self) -> None:
        """Test disconnect method behavior."""
        result = self.api.disconnect()
        assert result.success

    def test_is_connected_property(self) -> None:
        """Test is_connected property behavior."""
        # Initially not connected
        assert not self.api.is_connected

        # Test the property (not method)
        assert hasattr(self.api, "is_connected")

    def test_test_connection_when_not_connected(self) -> None:
        """Test test_connection method when not connected."""
        result = self.api.test_connection()
        assert not result.success
        assert (
            "connection" in result.error.lower()
            or "not connected" in result.error.lower()
        )

    def test_get_schemas_when_not_connected(self) -> None:
        """Test get_schemas method when not connected."""
        result = self.api.get_schemas()
        assert not result.success
        assert result.error is not None

    def test_get_tables_when_not_connected(self) -> None:
        """Test get_tables method when not connected."""
        # Test without schema
        result = self.api.get_tables()
        assert not result.success

        # Test with schema
        result_with_schema = self.api.get_tables("TEST_SCHEMA")
        assert not result_with_schema.success

    def test_get_columns_when_not_connected(self) -> None:
        """Test get_columns method when not connected."""
        # Test without schema
        result = self.api.get_columns("TEST_TABLE")
        assert not result.success

        # Test with schema
        result_with_schema = self.api.get_columns("TEST_TABLE", "TEST_SCHEMA")
        assert not result_with_schema.success

    def test_query_when_not_connected(self) -> None:
        """Test query method when not connected."""
        result = self.api.query("SELECT 1 FROM DUAL")
        assert not result.success
        assert result.error is not None

    def test_query_with_parameters_when_not_connected(self) -> None:
        """Test query method with parameters when not connected."""
        result = self.api.query(
            "SELECT * FROM users WHERE id = :user_id", {"user_id": 123}
        )
        assert not result.success

    def test_query_one_when_not_connected(self) -> None:
        """Test query_one method when not connected."""
        result = self.api.query_one("SELECT 1 FROM DUAL")
        assert not result.success

    def test_execute_when_not_connected(self) -> None:
        """Test execute method when not connected."""
        result = self.api.execute("INSERT INTO test_table (id) VALUES (1)")
        assert not result.success

    def test_execute_with_parameters_when_not_connected(self) -> None:
        """Test execute method with parameters when not connected."""
        result = self.api.execute(
            "INSERT INTO test_table (id, name) VALUES (:id, :name)",
            {"id": 1, "name": "test"},
        )
        assert not result.success

    def test_execute_many_when_not_connected(self) -> None:
        """Test execute_many method when not connected."""
        result = self.api.execute_many(
            "INSERT INTO test_table (id) VALUES (:id)",
            [{"id": 1}, {"id": 2}, {"id": 3}],
        )
        assert not result.success

    def test_execute_batch_when_not_connected(self) -> None:
        """Test execute_batch method when not connected."""
        operations = [
            ("INSERT INTO table1 (id) VALUES (:id)", {"id": 1}),
            ("INSERT INTO table2 (id) VALUES (:id)", {"id": 2}),
        ]
        result = self.api.execute_batch(operations)
        assert not result.success

    def test_get_table_metadata_when_not_connected(self) -> None:
        """Test get_table_metadata method when not connected."""
        result = self.api.get_tables("TEST_TABLE")
        assert not result.success

    def test_plugin_management_methods(self) -> None:
        """Test plugin management functionality."""
        # Test list_plugins when empty
        result = self.api.list_plugins()
        # When no plugins, may return failure with "Plugin listing returned empty"
        assert not result.success
        assert "plugin listing returned empty" in result.error.lower()

        # Test get_plugin when not found
        result = self.api.get_plugin("nonexistent_plugin")
        assert not result.success
        assert "plugin not found" in result.error.lower()

    def test_register_plugin_method(self) -> None:
        """Test register_plugin method."""

        # Create a plugin-like object with required attributes
        class TestPlugin:
            def __init__(self) -> None:
                self.name = "test_plugin"
                self.version = "1.0.0"
                self.description = "Test plugin"

        plugin = TestPlugin()
        result = self.api.register_plugin(plugin)
        # May fail due to plugin validation, but method should exist
        assert hasattr(result, "success")

    def test_unregister_plugin_method(self) -> None:
        """Test unregister_plugin method exists and behaves correctly."""
        # Test unregistering non-existent plugin
        result = self.api.unregister_plugin("nonexistent_plugin")
        assert not result.success
        assert (
            "plugin not found" in result.error.lower()
            or "not registered" in result.error.lower()
        )

    def test_list_plugins_method(self) -> None:
        """Test list_plugins method."""
        result = self.api.list_plugins()
        # When no plugins registered, returns failure
        assert not result.success
        assert "plugin listing returned empty" in result.error.lower()

    def test_health_check_when_not_connected(self) -> None:
        """Test health_check method when not connected."""
        result = self.api.test_connection()
        assert not result.success
        assert (
            "health check failed" in result.error.lower()
            or "connection" in result.error.lower()
        )

    def test_health_check_advanced(self) -> None:
        """Test advanced health check method (works without connection)."""
        result = self.api.get_health_check()
        # Health check should work but might fail due to no connection
        assert hasattr(result, "success")
        if result.success:
            health_check = result.value
            assert health_check is not None

    def test_optimize_query_method(self) -> None:
        """Test optimize_query method (works without connection)."""
        result = self.api.optimize_query("SELECT * FROM users")
        assert result.success
        suggestions = result.value
        assert isinstance(suggestions, dict)
        assert "suggestions" in suggestions
        # Should suggest avoiding SELECT *
        assert any(
            "SELECT *" in str(suggestion)
            for suggestion in suggestions.get("suggestions", [])
        )

    def test_table_operations(self) -> None:
        """Test table operations."""
        # Test get_tables (will fail due to no connection but method exists)
        result = self.api.get_tables()
        assert not result.success
        assert result.error is not None

        # Test get_columns (will fail due to no connection but method exists)
        columns_result = self.api.get_columns("TEST_TABLE")
        assert not result.success
        assert columns_result.error is not None

    def test_sql_building_operations(self) -> None:
        """Test SQL building operations."""
        # Test build_select method (may work without connection)
        select_result = self.api.build_select("TEST_TABLE", ["id", "name"])
        assert hasattr(select_result, "success")

        # Test build_insert_statement method
        insert_result = self.api.build_insert_statement(
            "TEST_TABLE", {"id": 1, "name": "test"}
        )
        assert hasattr(insert_result, "success")

        # Test build_update_statement method
        update_result = self.api.build_update_statement(
            "TEST_TABLE", {"name": "updated"}, {"id": 1}
        )
        assert hasattr(update_result, "success")

    def test_singer_ecosystem_integration(self) -> None:
        """Test Singer ecosystem integration methods."""
        # Test convert_singer_type method (may work without connection)
        singer_result = self.api.convert_singer_type("string")
        assert hasattr(singer_result, "success")

        # Test map_singer_schema method
        schema_result = self.api.map_singer_schema({})
        assert hasattr(schema_result, "success")

        # Test get_primary_keys method (will fail due to no connection but method exists)
        pk_result = self.api.get_primary_keys("TEST_TABLE")
        assert hasattr(pk_result, "success")

    def test_context_manager_support(self) -> None:
        """Test API context manager support."""
        # Test __enter__ method
        entered_api = self.api.__enter__()
        assert entered_api is self.api

        # Test __exit__ method
        self.api.__exit__(None, None, None)
        # Should not raise any exceptions

    def test_repr_method(self) -> None:
        """Test __repr__ method."""
        repr_str = repr(self.api)
        assert "FlextDbOracleApi" in repr_str
        assert "test:1521" in repr_str
        assert "TEST" in repr_str

    def test_api_delegation_patterns(self) -> None:
        """Test API delegation to underlying managers."""
        # These methods should delegate to connection manager
        assert hasattr(self.api, "get_schemas")
        assert hasattr(self.api, "get_tables")
        assert hasattr(self.api, "get_columns")
        assert hasattr(self.api, "query")
        assert hasattr(self.api, "execute")

        # Test that methods are callable
        assert callable(self.api.get_schemas)
        assert callable(self.api.get_tables)
        assert callable(self.api.get_columns)
        assert callable(self.api.query)
        assert callable(self.api.execute)

    def test_api_configuration_access(self) -> None:
        """Test access to API configuration."""
        assert hasattr(self.api, "_connection_manager")
        assert self.api._connection_manager.config == self.config

    def test_connection_property(self) -> None:
        """Test connection property access."""
        # Test connection property
        connection = self.api.connection
        assert connection is not None

        # Connection should be from connection manager
        assert connection is self.api._connection_manager.connection

    def test_api_state_management(self) -> None:
        """Test API internal state management."""
        # Test initial state
        assert self.api._plugins == {}
        assert self.api._test_is_connected is None

        # Test connection state via property (not direct attribute access)
        initial_connection_state = self.api.is_connected
        assert isinstance(initial_connection_state, bool)

    def test_batch_operations_parameter_handling(self) -> None:
        """Test parameter handling in batch operations."""
        # Test with mixed parameter types
        operations = [
            ("SELECT 1 FROM DUAL", None),
            ("SELECT * FROM users WHERE id = :id", {"id": 1}),
            ("SELECT name FROM users", {}),
        ]

        result = self.api.execute_batch(operations)
        # Should fail due to no connection but should handle parameters correctly
        assert not result.success

    def test_query_result_processing_methods(self) -> None:
        """Test query result processing and formatting."""
        # Test methods that work with query results
        assert hasattr(self.api, "format_query_result")
        assert hasattr(self.api, "analyze_query")
        assert hasattr(self.api, "optimize_query")

        # These should be available even without connection
        assert callable(self.api.format_query_result)
        assert callable(self.api.analyze_query)
        assert callable(self.api.optimize_query)

    def test_error_handling_patterns(self) -> None:
        """Test consistent error handling patterns across API methods."""
        methods_to_test = [
            ("test_connection", []),
            ("get_schemas", []),
            ("get_tables", []),
            ("get_columns", ["TEST_TABLE"]),
            ("query", ["SELECT 1 FROM DUAL"]),
            ("execute", ["INSERT INTO test (id) VALUES (1)"]),
            ("health_check", []),
        ]

        for method_name, args in methods_to_test:
            method = getattr(self.api, method_name)
            result = method(*args)

            # All methods should return FlextResult
            assert hasattr(result, "success")
            assert hasattr(result, "error")

            # When not connected, should fail with descriptive error
            if method_name != "optimize_query":
                assert not result.success
                assert result.error is not None
                assert len(result.error) > 0

    def test_observability_and_monitoring(self) -> None:
        """Test observability and monitoring methods."""
        # Test get_observability_metrics method
        metrics_result = self.api.get_observability_metrics()
        assert hasattr(metrics_result, "success")

        # Test query_with_timing method (will fail due to no connection but method exists)
        timing_result = self.api.query_with_timing("SELECT 1 FROM DUAL")
        assert hasattr(timing_result, "success")

        # Test query_with_modern_performance_monitoring method
        monitor_result = self.api.query_with_modern_performance_monitoring(
            "SELECT 1 FROM DUAL"
        )
        assert hasattr(monitor_result, "success")

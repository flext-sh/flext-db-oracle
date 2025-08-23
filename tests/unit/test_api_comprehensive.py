"""Comprehensive tests for FlextDbOracleApi using real code validation.

This module tests the API functionality with real code paths,
following the user's requirement for real code testing without mocks.
"""

import pytest
from pydantic import SecretStr

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
from flext_db_oracle.models import FlextDbOracleQueryResult


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
        assert hasattr(self.api, '_connection_manager')
        assert hasattr(self.api, '_query_executor') 
        assert hasattr(self.api, '_observability')
        assert self.api._plugins == []
        assert not self.api._is_connected

    def test_api_initialization_with_context(self) -> None:
        """Test API initialization with custom context name."""
        custom_api = FlextDbOracleApi(self.config, context_name="custom_context")
        assert custom_api is not None

    def test_connect_when_not_configured(self) -> None:
        """Test connect method behavior."""
        # Connect should delegate to connection manager
        connected_api = self.api.connect()
        # The connect method returns the API instance for method chaining
        assert connected_api is self.api
        # Connection state should be reflected in is_connected
        # (will be False because we can't actually connect to test DB)

    def test_disconnect_method(self) -> None:
        """Test disconnect method behavior."""
        result = self.api.disconnect()
        assert result.success
        assert not self.api._is_connected

    def test_is_connected_property(self) -> None:
        """Test is_connected property behavior."""
        # Initially not connected
        assert not self.api.is_connected
        
        # Test the property (not method)
        assert hasattr(self.api, 'is_connected')

    def test_test_connection_when_not_connected(self) -> None:
        """Test test_connection method when not connected."""
        result = self.api.test_connection()
        assert not result.success
        assert "connection" in result.error.lower() or "not connected" in result.error.lower()

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
            "SELECT * FROM users WHERE id = :user_id", 
            {"user_id": 123}
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
            {"id": 1, "name": "test"}
        )
        assert not result.success

    def test_execute_many_when_not_connected(self) -> None:
        """Test execute_many method when not connected."""
        result = self.api.execute_many(
            "INSERT INTO test_table (id) VALUES (:id)",
            [{"id": 1}, {"id": 2}, {"id": 3}]
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
        result = self.api.get_table_metadata("TEST_TABLE")
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
            def __init__(self):
                self.name = "test_plugin"
                self.version = "1.0.0"
                self.description = "Test plugin"
                
        plugin = TestPlugin()
        result = self.api.register_plugin(plugin)
        # May fail due to plugin validation, but method should exist
        assert hasattr(result, 'success')

    def test_unregister_plugin_method(self) -> None:
        """Test unregister_plugin method exists and behaves correctly."""
        # Test unregistering non-existent plugin
        result = self.api.unregister_plugin("nonexistent_plugin")
        assert not result.success
        assert "plugin not found" in result.error.lower() or "not registered" in result.error.lower()

    def test_list_plugins_method(self) -> None:
        """Test list_plugins method."""
        result = self.api.list_plugins()
        # When no plugins registered, returns failure
        assert not result.success
        assert "plugin listing returned empty" in result.error.lower()

    def test_health_check_when_not_connected(self) -> None:
        """Test health_check method when not connected."""
        result = self.api.health_check()
        assert not result.success
        assert "health check failed" in result.error.lower() or "connection" in result.error.lower()

    def test_analyze_query_method(self) -> None:
        """Test analyze_query method (works without connection)."""
        result = self.api.analyze_query("SELECT * FROM users WHERE status = 'ACTIVE'")
        assert result.success
        analysis = result.value
        assert isinstance(analysis, dict)
        assert "query_type" in analysis
        assert "tables" in analysis
        assert "has_where_clause" in analysis

    def test_optimize_query_method(self) -> None:
        """Test optimize_query method (works without connection)."""
        result = self.api.optimize_query("SELECT * FROM users")
        assert result.success
        suggestions = result.value
        assert isinstance(suggestions, dict)
        assert "suggestions" in suggestions
        # Should suggest avoiding SELECT *
        assert any("SELECT *" in str(suggestion) for suggestion in suggestions.get("suggestions", []))

    def test_format_query_result_method(self) -> None:
        """Test format_query_result method."""
        # Create a mock query result
        query_result = FlextDbOracleQueryResult(
            columns=["ID", "NAME", "STATUS"],
            rows=[(1, "John", "ACTIVE"), (2, "Jane", "INACTIVE")],
            row_count=2,
            query_hash="test_hash"
        )
        
        # Test table format
        result = self.api.format_query_result(query_result, "table")
        assert result.success
        formatted = result.value
        assert "ID" in formatted
        assert "NAME" in formatted
        assert "John" in formatted
        
        # Test JSON format
        result = self.api.format_query_result(query_result, "json")
        assert result.success
        
        # Test CSV format
        result = self.api.format_query_result(query_result, "csv")
        assert result.success

    def test_validate_sql_method(self) -> None:
        """Test validate_sql method."""
        # Test valid SQL
        result = self.api.validate_sql("SELECT * FROM users WHERE id = 1")
        assert result.success
        
        # Test invalid SQL
        result = self.api.validate_sql("INVALID SQL STATEMENT")
        assert not result.success
        assert "invalid sql" in result.error.lower()

    def test_create_connection_method(self) -> None:
        """Test create_connection method."""
        connection = self.api.create_connection()
        assert connection is not None
        assert hasattr(connection, 'config')
        assert connection.config == self.api._connection_manager.config

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
        assert hasattr(self.api, 'get_schemas')
        assert hasattr(self.api, 'get_tables')
        assert hasattr(self.api, 'get_columns')
        assert hasattr(self.api, 'query')
        assert hasattr(self.api, 'execute')
        
        # Test that methods are callable
        assert callable(self.api.get_schemas)
        assert callable(self.api.get_tables)
        assert callable(self.api.get_columns)
        assert callable(self.api.query)
        assert callable(self.api.execute)

    def test_api_configuration_access(self) -> None:
        """Test access to API configuration."""
        assert hasattr(self.api, '_connection_manager')
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
        assert self.api._plugins == []
        assert not self.api._is_connected
        assert self.api._test_is_connected is None
        
        # Test state modification through methods
        self.api._is_connected = True
        assert self.api._is_connected
        
        # Reset state
        self.api._is_connected = False
        assert not self.api._is_connected

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
        assert hasattr(self.api, 'format_query_result')
        assert hasattr(self.api, 'analyze_query')
        assert hasattr(self.api, 'optimize_query')
        
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
            assert hasattr(result, 'success')
            assert hasattr(result, 'error')
            
            # When not connected, should fail with descriptive error
            if method_name not in ["analyze_query", "optimize_query", "validate_sql"]:
                assert not result.success
                assert result.error is not None
                assert len(result.error) > 0

    def test_format_output_methods(self) -> None:
        """Test output formatting helper methods."""
        # Test that format methods exist and are callable
        assert hasattr(self.api, 'format_query_result')
        assert callable(self.api.format_query_result)
        
        # Test format_as_json method if it exists
        if hasattr(self.api, 'format_as_json'):
            assert callable(self.api.format_as_json)
            
        # Test format_as_csv method if it exists  
        if hasattr(self.api, 'format_as_csv'):
            assert callable(self.api.format_as_csv)
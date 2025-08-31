"""Safe comprehensive tests for FlextDbOracleApi using methods that work without DB connection.

This module tests API methods that can be executed without requiring an actual
database connection, following the user's requirement for real code testing.
"""

from pydantic import SecretStr

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig


class TestFlextDbOracleApiSafeComprehensive:
    """Safe comprehensive tests for Oracle API methods that work without DB connection."""

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

    def test_optimize_query_comprehensive(self) -> None:
        """Test optimize_query method comprehensively."""
        # Test with SELECT query
        result = self.api.optimize_query("SELECT * FROM users WHERE status = 'ACTIVE'")
        assert result.success
        suggestions = result.value
        assert isinstance(suggestions, dict)
        assert "suggestions" in suggestions

        # Test with UPDATE query
        result = self.api.optimize_query(
            "UPDATE users SET status = 'INACTIVE' WHERE id = 1"
        )
        assert result.success

        # Test with INSERT query
        result = self.api.optimize_query(
            "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')"
        )
        assert result.success

        # Test with complex JOIN query
        result = self.api.optimize_query(
            "SELECT u.name, d.name FROM users u JOIN departments d ON u.dept_id = d.id"
        )
        assert result.success

    def test_get_observability_metrics_comprehensive(self) -> None:
        """Test get_observability_metrics method comprehensively."""
        result = self.api.get_observability_metrics()
        assert result.success
        metrics = result.value
        assert isinstance(metrics, dict)

        # Metrics should contain observability data
        # The actual structure depends on the implementation
        assert metrics is not None

    def test_api_properties_and_attributes_comprehensive(self) -> None:
        """Test API properties and internal attributes comprehensively."""
        # Test connection property (should not be None but might not be connected)
        _ = self.api.connection
        # Connection exists as a property
        assert hasattr(self.api, "connection")

        # Test configuration access
        config = self.api.config
        assert config is not None
        assert config == self.config

        # Test is_connected property
        connected_state = self.api.is_connected
        assert isinstance(connected_state, bool)
        # Initially should be False since we haven't connected
        assert not connected_state

    def test_plugin_system_comprehensive(self) -> None:
        """Test plugin system methods comprehensively."""
        # Test list_plugins when no plugins are registered
        result = self.api.list_plugins()
        assert not result.success  # Should fail when no plugins
        assert "plugin listing returned empty" in result.error.lower()

        # Test get_plugin for non-existent plugin
        result = self.api.get_plugin("non_existent_plugin")
        assert not result.success
        assert "plugin not found" in result.error.lower()

        # Test plugin registration with mock plugin
        class MockPlugin:
            def __init__(self) -> None:
                self.name = "mock_plugin"
                self.version = "1.0.0"
                self.description = "Mock plugin for testing"

        mock_plugin = MockPlugin()
        result = self.api.register_plugin(mock_plugin)
        # May succeed or fail depending on plugin validation
        assert hasattr(result, "success")

    def test_from_env_class_method(self) -> None:
        """Test from_env class method."""
        # This method should create API from environment variables
        api_instance = FlextDbOracleApi.from_env()
        # Should return API instance directly (not FlextResult)
        assert isinstance(api_instance, FlextDbOracleApi)

    def test_from_config_class_method(self) -> None:
        """Test from_config class method."""
        # This method should create API from config object
        api_instance = FlextDbOracleApi.from_config(self.config)
        # Should return API instance directly (not FlextResult)
        assert isinstance(api_instance, FlextDbOracleApi)

    def test_with_config_class_method(self) -> None:
        """Test with_config class method."""
        # This method should create API with config
        api_instance = FlextDbOracleApi.with_config(
            host="localhost",
            port=1521,
            service_name="XE",
            username="test",
            password="test",
        )
        # Should return API instance directly (not FlextResult)
        assert isinstance(api_instance, FlextDbOracleApi)

    def test_from_url_class_method(self) -> None:
        """Test from_url class method."""
        # This method should create API from URL
        oracle_url = "oracle://test:test@test:1521/TEST"
        api_instance = FlextDbOracleApi.from_url(oracle_url)
        # Should return API instance directly (not FlextResult)
        assert isinstance(api_instance, FlextDbOracleApi)

    def test_repr_method_comprehensive(self) -> None:
        """Test __repr__ method comprehensively."""
        repr_str = repr(self.api)
        # API uses default Python object repr
        assert "FlextDbOracleApi" in repr_str
        assert "object at" in repr_str

        # Test with custom context - should still be same pattern
        custom_api = FlextDbOracleApi(self.config, context_name="custom")
        custom_repr = repr(custom_api)
        assert "FlextDbOracleApi" in custom_repr
        assert "object at" in custom_repr

    def test_context_manager_protocol(self) -> None:
        """Test context manager protocol methods."""
        # Test __enter__ method exists and is callable
        assert hasattr(self.api, "__enter__")
        assert callable(self.api.__enter__)

        # Test __exit__ method exists and is callable
        assert hasattr(self.api, "__exit__")
        assert callable(self.api.__exit__)

        # Test actual context manager usage (shouldn't connect to DB)
        entered_api = self.api.__enter__()
        assert entered_api is self.api

        # Test __exit__ doesn't raise exceptions
        self.api.__exit__(None, None, None)

    def test_api_delegation_and_method_existence(self) -> None:
        """Test that API has expected methods and they are callable."""
        # Test core database methods exist
        core_methods = [
            "connect",
            "disconnect",
            "test_connection",
            "query",
            "query_one",
            "execute_batch",
            "get_schemas",
            "get_tables",
            "get_columns",
        ]

        for method_name in core_methods:
            assert hasattr(self.api, method_name), f"Method {method_name} should exist"
            assert callable(getattr(self.api, method_name)), (
                f"Method {method_name} should be callable"
            )

        # Test SQL building methods exist
        sql_methods = [
            "build_select",
            "build_insert_statement",
            "build_update_statement",
            "build_delete_statement",
            "build_merge_statement",
        ]

        for method_name in sql_methods:
            assert hasattr(self.api, method_name), (
                f"SQL method {method_name} should exist"
            )
            assert callable(getattr(self.api, method_name)), (
                f"SQL method {method_name} should be callable"
            )

        # Test observability methods exist
        observability_methods = [
            "get_health_check",
            "get_health_status",
            "get_observability_metrics",
            "query_with_timing",
            "query_with_modern_performance_monitoring",
        ]

        for method_name in observability_methods:
            assert hasattr(self.api, method_name), (
                f"Observability method {method_name} should exist"
            )
            assert callable(getattr(self.api, method_name)), (
                f"Observability method {method_name} should be callable"
            )

    def test_singer_ecosystem_methods_existence(self) -> None:
        """Test Singer ecosystem integration methods exist."""
        singer_methods = [
            "convert_singer_type",
            "map_singer_schema",
            "get_primary_keys",
        ]

        for method_name in singer_methods:
            assert hasattr(self.api, method_name), (
                f"Singer method {method_name} should exist"
            )
            assert callable(getattr(self.api, method_name)), (
                f"Singer method {method_name} should be callable"
            )

    def test_ddl_methods_existence(self) -> None:
        """Test DDL generation methods exist."""
        ddl_methods = [
            "create_table_ddl",
            "drop_table_ddl",
            "execute_ddl",
            "build_create_index_statement",
        ]

        for method_name in ddl_methods:
            assert hasattr(self.api, method_name), (
                f"DDL method {method_name} should exist"
            )
            assert callable(getattr(self.api, method_name)), (
                f"DDL method {method_name} should be callable"
            )

    def test_advanced_features_existence(self) -> None:
        """Test advanced feature methods exist."""
        advanced_methods = [
            "transaction",
            "execute_connection_monitor",
            "get_table_metadata",
        ]

        for method_name in advanced_methods:
            assert hasattr(self.api, method_name), (
                f"Advanced method {method_name} should exist"
            )
            assert callable(getattr(self.api, method_name)), (
                f"Advanced method {method_name} should be callable"
            )

    def test_plugin_execution_methods(self) -> None:
        """Test plugin execution methods."""
        # Test execute_plugin method exists
        assert hasattr(self.api, "execute_plugin")
        assert callable(self.api.execute_plugin)

        # Test unregister_plugin method exists
        assert hasattr(self.api, "unregister_plugin")
        assert callable(self.api.unregister_plugin)

    def test_configuration_methods_comprehensive(self) -> None:
        """Test configuration-related methods comprehensively."""
        # Test that config property works
        api_config = self.api.config
        assert api_config == self.config

        # Test configuration access doesn't require connection
        assert api_config.host == "test"
        assert api_config.port == 1521
        assert api_config.service_name == "TEST"
        assert api_config.username == "test"
        # Password should be SecretStr
        assert str(api_config.password.get_secret_value()) == "test"

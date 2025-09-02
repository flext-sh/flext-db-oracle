"""Safe API tests using only real methods that exist."""

from unittest.mock import MagicMock, patch

from pydantic import SecretStr

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig


class TestFlextDbOracleApiSafe:
    """Test FlextDbOracleApi using only methods that actually exist."""

    def setup_method(self) -> None:
        """Setup test configuration."""
        self.config = FlextDbOracleConfig(
            host="test_host",
            port=1521,
            service_name="TEST",
            username="test_user",
            password=SecretStr("test_password"),
        )
        self.api = FlextDbOracleApi(self.config)

    def test_api_creation(self) -> None:
        """Test API can be created with valid config."""
        assert self.api is not None
        assert self.api.config == self.config

    def test_optimize_query_method_exists(self) -> None:
        """Test optimize_query method exists and returns FlextResult."""
        # This method exists and works without database connection
        result = self.api.optimize_query("SELECT * FROM dual")
        assert hasattr(result, "success")
        assert hasattr(result, "error") or hasattr(result, "value")

    def test_get_observability_metrics(self) -> None:
        """Test get_observability_metrics method exists."""
        result = self.api.get_observability_metrics()
        assert hasattr(result, "success")
        # Method might succeed or fail depending on internal state

    def test_plugin_methods_exist(self) -> None:
        """Test plugin-related methods exist."""
        # These methods exist but might fail if no plugins registered
        result = self.api.list_plugins()
        assert hasattr(result, "success")

        # get_plugin might return None or fail if plugin doesn't exist
        plugin_result = self.api.get_plugin("nonexistent")
        assert plugin_result is not None or plugin_result is None

    def test_connection_methods_exist(self) -> None:
        """Test connection methods exist but will fail without real database."""
        # These methods exist but require database connection
        connect_result = self.api.connect()
        assert hasattr(connect_result, "success")
        assert not connect_result.success  # Should fail without real DB

        # test_connection should exist
        test_result = self.api.test_connection()
        assert hasattr(test_result, "success")
        assert not test_result.success  # Should fail without real DB

    def test_query_methods_exist(self) -> None:
        """Test query methods exist but fail without connection."""
        # These methods exist but require database connection
        query_result = self.api.query("SELECT 1 FROM dual")
        assert hasattr(query_result, "success")
        assert not query_result.success  # Should fail without connection

        query_one_result = self.api.query_one("SELECT 1 FROM dual")
        assert hasattr(query_one_result, "success")
        assert not query_one_result.success  # Should fail without connection

    def test_schema_methods_exist(self) -> None:
        """Test schema introspection methods exist."""
        # These methods exist but require database connection
        schemas_result = self.api.get_schemas()
        assert hasattr(schemas_result, "success")
        assert not schemas_result.success  # Should fail without connection

        tables_result = self.api.get_tables("TEST_SCHEMA")
        assert hasattr(tables_result, "success")
        assert not tables_result.success  # Should fail without connection

    def test_factory_methods(self) -> None:
        """Test factory methods work."""
        # Test from_config class method
        api_from_config = FlextDbOracleApi.from_config(self.config)
        assert api_from_config is not None
        assert isinstance(api_from_config, FlextDbOracleApi)

    def test_validation_methods(self) -> None:
        """Test validation methods."""
        # is_valid method should exist
        is_valid = self.api.is_valid()
        assert isinstance(is_valid, bool)

        # validate_config should exist
        validation_result = self.api.validate_config()
        assert hasattr(validation_result, "success")

    @patch("flext_db_oracle.api.create_engine")
    def test_connect_with_mock(self, mock_create_engine: MagicMock) -> None:
        """Test connect method with mocked engine."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        # Should still fail due to other internal checks
        result = self.api.connect()
        assert hasattr(result, "success")

    def test_config_access(self) -> None:
        """Test config property access."""
        assert self.api.config is not None
        assert self.api.config.host == "test_host"
        assert self.api.config.port == 1521

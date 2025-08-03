"""Tests for API methods missing coverage.

Tests specifically targeting API methods that are not covered
by existing tests to improve overall coverage.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from flext_core import FlextResult

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.config import FlextDbOracleConfig


class TestApiMissingCoverage:
    """Test API methods missing coverage."""

    @pytest.fixture
    def config(self) -> FlextDbOracleConfig:
        """Create test config."""
        return FlextDbOracleConfig(
            host="localhost",
            port=1521,
            username="test",
            password="test",
            service_name="xe",
        )

    @pytest.fixture
    def api(self, config: FlextDbOracleConfig) -> FlextDbOracleApi:
        """Create test API."""
        return FlextDbOracleApi(config, "test")

    def test_get_health_status_not_connected(self, api: FlextDbOracleApi) -> None:
        """Test health status when not connected."""
        result = api.get_health_status()

        assert result.is_success
        assert result.data is not None
        assert result.data.status == "unhealthy"
        assert "not connected" in result.data.message.lower()

    @patch("flext_db_oracle.api.FlextDbOracleApi.query")
    def test_get_health_status_connected_success(
        self,
        mock_query: Mock,
        api: FlextDbOracleApi,
    ) -> None:
        """Test health status when connected and healthy."""
        # Mock the connection manager to indicate connected
        api._connection_manager = Mock()
        api._connection_manager.is_connected = True

        # Create successful query result
        from flext_db_oracle.types import TDbOracleQueryResult

        mock_query_result = TDbOracleQueryResult(
            rows=[(1,)],
            columns=["result"],
            row_count=1,
            execution_time_ms=0.0,
        )
        mock_query.return_value = FlextResult.ok(mock_query_result)

        result = api.get_health_status()

        assert result.is_success
        assert result.data.status == "healthy"
        mock_query.assert_called_once_with("SELECT 1 FROM DUAL")

    @patch("flext_db_oracle.api.FlextDbOracleApi.query")
    def test_get_health_status_connected_degraded(
        self,
        mock_query: Mock,
        api: FlextDbOracleApi,
    ) -> None:
        """Test health status when connected but query fails."""
        api._is_connected = True
        api._connection = Mock()
        mock_query.return_value = FlextResult.fail("Query failed")

        result = api.get_health_status()

        assert result.is_success
        assert result.data.status == "degraded"
        assert "Query failed" in result.data.message

    def test_get_observability_metrics(self, api: FlextDbOracleApi) -> None:
        """Test observability metrics retrieval."""
        api._is_connected = True
        # Also need to set a mock connection for is_connected to return True
        api._connection = Mock()

        result = api.get_observability_metrics()

        assert result.is_success
        assert "context" in result.data
        assert "is_connected" in result.data
        assert result.data["is_connected"] is True

    def test_get_observability_metrics_exception(self, api: FlextDbOracleApi) -> None:
        """Test observability metrics with exception."""
        api._observability = Mock()
        api._observability.is_monitoring_active.side_effect = Exception(
            "Monitoring error",
        )

        result = api.get_observability_metrics()

        assert result.is_failure
        assert "Failed to get metrics" in result.error

    def test_test_connection_with_observability_disconnected(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """Test connection test with observability when disconnected."""
        result = api.test_connection_with_observability()

        assert result.is_success
        assert result.data["status"] == "disconnected"

    def test_test_connection_with_observability_connected(
        self,
        api: FlextDbOracleApi,
    ) -> None:
        """Test connection test with observability when connected."""
        api._is_connected = True

        # Mock the connection and its execute_query method
        mock_connection = Mock()
        mock_connection.execute_query.return_value = FlextResult.ok([("1",)])
        api._connection = mock_connection

        result = api.test_connection_with_observability()

        assert result.is_success
        assert result.data["status"] == "healthy"
        assert result.data["query_success"] is True

    @patch("flext_db_oracle.api.FlextDbOracleApi.test_connection")
    def test_test_connection_with_observability_exception(
        self,
        mock_test_connection: Mock,
        api: FlextDbOracleApi,
    ) -> None:
        """Test connection test with observability exception."""
        api._is_connected = True
        api._connection = Mock()
        mock_test_connection.side_effect = Exception("Connection error")

        result = api.test_connection_with_observability()

        assert result.is_failure
        assert "Connection test failed" in result.error

    def test_register_plugin_success(self, api: FlextDbOracleApi) -> None:
        """Test successful plugin registration."""
        from flext_plugin import FlextPlugin

        plugin = FlextPlugin(name="test", version="1.0", config={})
        api._plugin_platform = Mock()
        api._plugin_platform.load_plugin.return_value = FlextResult.ok(None)

        result = api.register_plugin(plugin)

        assert result.is_success

    def test_register_plugin_failure(self, api: FlextDbOracleApi) -> None:
        """Test failed plugin registration."""
        from flext_plugin import FlextPlugin

        plugin = FlextPlugin(name="test", version="1.0", config={})
        api._plugin_platform = Mock()
        api._plugin_platform.load_plugin.return_value = FlextResult.fail("Load failed")

        result = api.register_plugin(plugin)

        assert result.is_failure
        assert "Failed to register plugin" in result.error

    def test_register_plugin_exception(self, api: FlextDbOracleApi) -> None:
        """Test plugin registration exception."""
        from flext_plugin import FlextPlugin

        plugin = FlextPlugin(name="test", version="1.0", config={})
        api._plugin_platform = Mock()
        api._plugin_platform.load_plugin.side_effect = Exception("Plugin error")

        result = api.register_plugin(plugin)

        assert result.is_failure
        assert "Plugin registration error" in result.error

    def test_unregister_plugin_success(self, api: FlextDbOracleApi) -> None:
        """Test successful plugin unregistration."""
        # First add a plugin to the registry
        from flext_plugin import FlextPlugin

        mock_plugin = Mock(spec=FlextPlugin)
        mock_plugin.name = "test_plugin"
        api._plugins["test_plugin"] = mock_plugin

        result = api.unregister_plugin("test_plugin")

        assert result.is_success
        assert "test_plugin" not in api._plugins

    def test_unregister_plugin_failure(self, api: FlextDbOracleApi) -> None:
        """Test failed plugin unregistration."""
        api._plugin_platform = Mock()
        api._plugin_platform.unload_plugin.return_value = FlextResult.fail(
            "Unload failed",
        )

        result = api.unregister_plugin("test_plugin")

        assert result.is_failure

    def test_execute_plugin_success(self, api: FlextDbOracleApi) -> None:
        """Test successful plugin execution."""
        mock_plugin = Mock()
        mock_plugin.config = Mock()
        mock_plugin.config.callable_obj = Mock(return_value="plugin result")

        api.get_plugin = Mock(return_value=FlextResult.ok(mock_plugin))

        result = api.execute_plugin("test_plugin", arg1="value1")

        assert result.is_success
        assert result.data == "plugin result"

    def test_execute_plugin_not_found(self, api: FlextDbOracleApi) -> None:
        """Test plugin execution when plugin not found."""
        api.get_plugin = Mock(return_value=FlextResult.fail("Plugin not found"))

        result = api.execute_plugin("test_plugin")

        assert result.is_failure
        assert "Plugin not found" in result.error

    def test_execute_plugin_not_callable(self, api: FlextDbOracleApi) -> None:
        """Test plugin execution when plugin not callable."""
        mock_plugin = Mock()
        # Properly mock the config to have no callable_obj
        mock_plugin.config = Mock()
        mock_plugin.config.callable_obj = None

        api.get_plugin = Mock(return_value=FlextResult.ok(mock_plugin))

        result = api.execute_plugin("test_plugin")

        assert result.is_failure
        assert "not callable" in result.error

    def test_list_plugins_success(self, api: FlextDbOracleApi) -> None:
        """Test successful plugin listing."""
        from flext_plugin import FlextPlugin

        plugins = [FlextPlugin(name="test", version="1.0", config={})]

        api._plugin_platform = Mock()
        api._plugin_platform.plugin_service = Mock()
        api._plugin_platform.plugin_service.registry = Mock()
        api._plugin_platform.plugin_service.registry.list_plugins.return_value = plugins

        result = api.list_plugins()

        assert result.is_success
        assert len(result.data) == 1
        assert result.data[0].name == "test"

    def test_list_plugins_no_registry(self, api: FlextDbOracleApi) -> None:
        """Test plugin listing with no registry."""
        api._plugin_platform = Mock()
        api._plugin_platform.plugin_service = Mock(spec=[])  # No registry attribute

        result = api.list_plugins()

        assert result.is_success
        assert result.data == []

    def test_list_plugins_exception(self, api: FlextDbOracleApi) -> None:
        """Test plugin listing exception."""
        api._plugin_platform = Mock()
        api._plugin_platform.plugin_service = None

        result = api.list_plugins()

        assert result.is_failure

    def test_get_plugin_success(self, api: FlextDbOracleApi) -> None:
        """Test successful plugin retrieval."""
        from flext_plugin import FlextPlugin

        plugin = FlextPlugin(name="test", version="1.0", config={})

        api._plugin_platform = Mock()
        api._plugin_platform.plugin_service = Mock()
        api._plugin_platform.plugin_service.registry = Mock()
        api._plugin_platform.plugin_service.registry.get_plugin.return_value = plugin

        result = api.get_plugin("test")

        assert result.is_success
        assert result.data.name == "test"

    def test_get_plugin_not_found(self, api: FlextDbOracleApi) -> None:
        """Test plugin retrieval when not found."""
        api._plugin_platform = Mock()
        api._plugin_platform.plugin_service = Mock()
        api._plugin_platform.plugin_service.registry = Mock()
        api._plugin_platform.plugin_service.registry.get_plugin.return_value = None

        result = api.get_plugin("test")

        assert result.is_failure
        assert "not found" in result.error

    def test_execute_connection_monitor(self, api: FlextDbOracleApi) -> None:
        """Test connection monitor plugin execution."""
        api.execute_plugin = Mock(return_value=FlextResult.ok({"status": "healthy"}))

        result = api.execute_connection_monitor(param="value")

        assert result.is_success
        api.execute_plugin.assert_called_once_with(
            "oracle_connection_monitor",
            param="value",
        )

    def test_optimize_query(self, api: FlextDbOracleApi) -> None:
        """Test query optimization functionality."""
        result = api.optimize_query("SELECT * FROM table")

        assert result.is_success
        assert result.data is not None

        # Check analysis result structure
        analysis = result.data
        assert "sql_length" in analysis
        assert "has_joins" in analysis
        assert "has_subqueries" in analysis
        assert "suggestions" in analysis

        # Verify specific analysis results
        assert analysis["sql_length"] == len("SELECT * FROM table")
        assert analysis["has_joins"] is False
        assert isinstance(analysis["suggestions"], list)

    def test_context_manager(self, api: FlextDbOracleApi) -> None:
        """Test context manager functionality."""
        api._is_connected = False
        api.connect = Mock(return_value=api)
        api.disconnect = Mock(return_value=api)

        with api:
            pass

        api.connect.assert_called_once()
        api.disconnect.assert_called_once()

    def test_context_manager_already_connected(self, api: FlextDbOracleApi) -> None:
        """Test context manager when already connected."""
        # Mock is_connected property using patch
        with patch.object(type(api), "is_connected", new=property(lambda self: True)):
            api.connect = Mock()
            api.disconnect = Mock(return_value=api)

            with api:
                pass

            api.connect.assert_not_called()
            api.disconnect.assert_called_once()

    def test_execute_ddl_not_connected(self, api: FlextDbOracleApi) -> None:
        """Test execute_ddl when not connected - BACKWARD COMPATIBILITY."""
        result = api.execute_ddl("CREATE TABLE test (id NUMBER)")

        assert result.is_failure
        assert "Database not connected" in result.error

    def test_execute_ddl_success(self, api: FlextDbOracleApi) -> None:
        """Test successful execute_ddl - BACKWARD COMPATIBILITY."""
        # Mock the query executor to simulate successful DDL execution
        mock_query_executor = Mock()
        mock_query_result = Mock()
        mock_query_result.is_success = True
        mock_query_executor.execute_query.return_value = mock_query_result
        api._query_executor = mock_query_executor

        result = api.execute_ddl("CREATE TABLE test (id NUMBER)")

        assert result.is_success
        mock_query_executor.execute_query.assert_called_once_with(
            "CREATE TABLE test (id NUMBER)",
            None,
        )

    def test_execute_ddl_failure(self, api: FlextDbOracleApi) -> None:
        """Test failed execute_ddl - BACKWARD COMPATIBILITY."""
        # Mock the query executor to simulate DDL execution failure
        mock_query_executor = Mock()
        mock_query_result = Mock()
        mock_query_result.is_success = False
        mock_query_result.error = "DDL execution failed"
        mock_query_executor.execute_query.return_value = mock_query_result
        api._query_executor = mock_query_executor

        result = api.execute_ddl("INVALID DDL STATEMENT")

        assert result.is_failure
        assert "DDL execution failed" in result.error

    def test_properties(self, config: FlextDbOracleConfig) -> None:
        """Test API properties."""
        api = FlextDbOracleApi(config)

        assert api.config is config
        assert api.connection is None
        assert not api.is_connected

        # Set connection to test property
        mock_connection = Mock()
        api._connection = mock_connection
        api._is_connected = True

        assert api.connection is mock_connection
        assert api.is_connected

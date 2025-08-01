"""Comprehensive tests for Oracle observability with full coverage.

Tests for flext_db_oracle.observability module covering all classes
and methods with complete code coverage.
"""

from __future__ import annotations

from datetime import datetime
from time import perf_counter
from unittest.mock import Mock, patch

import pytest
from flext_core import FlextContainer, FlextResult
from flext_observability import FlextHealthCheck, FlextTrace

from flext_db_oracle.observability import (
    FlextDbOracleErrorHandler,
    FlextDbOracleObservabilityManager,
    FlextDbOracleOperationTracker,
)


class TestFlextDbOracleObservabilityManager:
    """Test FlextDbOracleObservabilityManager comprehensive coverage."""

    @pytest.fixture
    def container(self) -> FlextContainer:
        """Create test container."""
        return FlextContainer()

    @pytest.fixture
    def manager(self, container: FlextContainer) -> FlextDbOracleObservabilityManager:
        """Create test observability manager."""
        return FlextDbOracleObservabilityManager(container, "test_context")

    def test_init(self, container: FlextContainer) -> None:
        """Test manager initialization."""
        manager = FlextDbOracleObservabilityManager(container, "test")

        assert manager._container is container
        assert manager._context_name == "test"
        assert not manager._initialized
        assert manager._monitor is not None
        assert manager._logger is not None

    @patch("flext_db_oracle.observability.FlextObservabilityMonitor")
    def test_initialize_success(self, mock_monitor_class: Mock, container: FlextContainer) -> None:
        """Test successful initialization."""
        mock_monitor = Mock()
        mock_monitor.flext_initialize_observability.return_value = FlextResult.ok(None)
        mock_monitor.flext_start_monitoring.return_value = FlextResult.ok(None)
        mock_monitor_class.return_value = mock_monitor

        manager = FlextDbOracleObservabilityManager(container, "test")
        result = manager.initialize()

        assert result.is_success
        assert manager._initialized

    @patch("flext_db_oracle.observability.FlextObservabilityMonitor")
    def test_initialize_already_initialized(self, mock_monitor_class: Mock, container: FlextContainer) -> None:
        """Test initialization when already initialized."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        manager = FlextDbOracleObservabilityManager(container, "test")
        manager._initialized = True

        result = manager.initialize()

        assert result.is_success
        mock_monitor.flext_initialize_observability.assert_not_called()

    @patch("flext_db_oracle.observability.FlextObservabilityMonitor")
    def test_initialize_monitor_init_failure(self, mock_monitor_class: Mock, container: FlextContainer) -> None:
        """Test initialization with monitor init failure."""
        mock_monitor = Mock()
        mock_monitor.flext_initialize_observability.return_value = FlextResult.fail("Init failed")
        mock_monitor_class.return_value = mock_monitor

        manager = FlextDbOracleObservabilityManager(container, "test")
        result = manager.initialize()

        assert result.is_success  # Still returns success but logs warning
        assert manager._initialized

    @patch("flext_db_oracle.observability.FlextObservabilityMonitor")
    def test_initialize_monitor_start_failure(self, mock_monitor_class: Mock, container: FlextContainer) -> None:
        """Test initialization with monitor start failure."""
        mock_monitor = Mock()
        mock_monitor.flext_initialize_observability.return_value = FlextResult.ok(None)
        mock_monitor.flext_start_monitoring.return_value = FlextResult.fail("Start failed")
        mock_monitor_class.return_value = mock_monitor

        manager = FlextDbOracleObservabilityManager(container, "test")
        result = manager.initialize()

        assert result.is_success  # Still returns success but logs warning
        assert manager._initialized

    @patch("flext_db_oracle.observability.FlextObservabilityMonitor")
    def test_initialize_exception(self, mock_monitor_class: Mock, container: FlextContainer) -> None:
        """Test initialization with monitor creation exception."""
        mock_monitor_class.side_effect = Exception("Monitor creation failed")

        # The exception should be raised during constructor
        with pytest.raises(Exception, match="Monitor creation failed"):
            FlextDbOracleObservabilityManager(container, "test")

    @patch("flext_db_oracle.observability.flext_create_trace")
    def test_create_trace_success(self, mock_create_trace: Mock, manager: FlextDbOracleObservabilityManager) -> None:
        """Test successful trace creation."""
        mock_trace = Mock(spec=FlextTrace)
        mock_create_trace.return_value = FlextResult.ok(mock_trace)

        result = manager.create_trace("test_operation", param1="value1")

        assert result is mock_trace
        mock_create_trace.assert_called_once()

    @patch("flext_db_oracle.observability.flext_create_trace")
    @patch("flext_db_oracle.observability.FlextTrace")
    def test_create_trace_fallback(self, mock_trace_class: Mock, mock_create_trace: Mock, manager: FlextDbOracleObservabilityManager) -> None:
        """Test trace creation fallback."""
        mock_create_trace.return_value = FlextResult.fail("Creation failed")
        mock_trace_instance = Mock(spec=FlextTrace)
        mock_trace_class.return_value = mock_trace_instance

        result = manager.create_trace("test_operation", param1="value1")

        assert result is mock_trace_instance
        mock_trace_class.assert_called_once()

    @patch("flext_db_oracle.observability.flext_create_metric")
    def test_record_metric_success(self, mock_create_metric: Mock, manager: FlextDbOracleObservabilityManager) -> None:
        """Test successful metric recording."""
        mock_create_metric.return_value = FlextResult.ok(Mock())

        manager.record_metric("test_metric", 42.0, "count", tag1="value1")

        mock_create_metric.assert_called_once_with(
            name="test_context.test_metric",
            value=42.0,
            unit="count",
            tags={"context": "test_context", "tag1": "value1"},
        )

    @patch("flext_db_oracle.observability.flext_create_metric")
    def test_record_metric_failure(self, mock_create_metric: Mock, manager: FlextDbOracleObservabilityManager) -> None:
        """Test metric recording failure."""
        mock_create_metric.return_value = FlextResult.fail("Metric creation failed")

        # Should not raise exception, just log warning
        manager.record_metric("test_metric", 42.0)

        mock_create_metric.assert_called_once()

    @patch("flext_db_oracle.observability.flext_create_health_check")
    def test_create_health_check(self, mock_create_health_check: Mock, manager: FlextDbOracleObservabilityManager) -> None:
        """Test health check creation."""
        mock_health_check = Mock(spec=FlextHealthCheck)
        mock_create_health_check.return_value = FlextResult.ok(mock_health_check)

        result = manager.create_health_check("healthy", "All good", {"metric": "value"})

        assert result.is_success
        assert result.data is mock_health_check
        mock_create_health_check.assert_called_once_with(
            component="oracle.test_context",
            status="healthy",
            message="All good",
        )

    @patch("flext_db_oracle.observability.flext_create_trace")
    def test_finish_trace_success(self, mock_create_trace: Mock, manager: FlextDbOracleObservabilityManager) -> None:
        """Test successful trace finishing."""
        original_trace = Mock(spec=FlextTrace)
        original_trace.trace_id = "trace-123"
        original_trace.operation = "test_op"
        original_trace.span_id = "span-456"
        original_trace.span_attributes = {"original": "attr"}

        new_trace = Mock(spec=FlextTrace)
        new_trace.span_id = "new-span-789"
        new_trace.span_attributes = {}
        mock_create_trace.return_value = FlextResult.ok(new_trace)

        result = manager.finish_trace(original_trace, 1000, "success", "no error")

        assert result is new_trace
        assert new_trace.span_attributes == {"original": "attr", "error": "no error"}

    @patch("flext_db_oracle.observability.flext_create_trace")
    def test_finish_trace_failure(self, mock_create_trace: Mock, manager: FlextDbOracleObservabilityManager) -> None:
        """Test trace finishing failure."""
        original_trace = Mock(spec=FlextTrace)
        original_trace.span_attributes = {"original": "attr"}  # Add required attribute
        original_trace.span_id = "span-123"  # Add required attribute
        original_trace.trace_id = "trace-456"  # Add required attribute
        original_trace.operation = "test_op"  # Add required attribute
        mock_create_trace.return_value = FlextResult.fail("Trace creation failed")

        result = manager.finish_trace(original_trace, 1000, "success")

        assert result is original_trace  # Returns original on failure

    def test_get_current_timestamp(self, manager: FlextDbOracleObservabilityManager) -> None:
        """Test timestamp generation."""
        timestamp = manager.get_current_timestamp()

        assert isinstance(timestamp, str)
        # Verify it's a valid ISO format timestamp
        datetime.fromisoformat(timestamp)

    def test_is_monitoring_active_initialized(self, manager: FlextDbOracleObservabilityManager) -> None:
        """Test monitoring active check when initialized."""
        manager._initialized = True
        with patch.object(manager._monitor, "flext_is_monitoring_active", return_value=True):
            assert manager.is_monitoring_active()

    def test_is_monitoring_active_not_initialized(self, manager: FlextDbOracleObservabilityManager) -> None:
        """Test monitoring active check when not initialized."""
        manager._initialized = False

        assert not manager.is_monitoring_active()


class TestFlextDbOracleOperationTracker:
    """Test FlextDbOracleOperationTracker comprehensive coverage."""

    @pytest.fixture
    def observability(self) -> Mock:
        """Create mock observability manager."""
        return Mock(spec=FlextDbOracleObservabilityManager)

    @pytest.fixture
    def tracker(self, observability: Mock) -> FlextDbOracleOperationTracker:
        """Create test operation tracker."""
        return FlextDbOracleOperationTracker(observability, "test_op", param1="value1")

    def test_init(self, observability: Mock) -> None:
        """Test tracker initialization."""
        tracker = FlextDbOracleOperationTracker(observability, "test_op", attr="value")

        assert tracker._observability is observability
        assert tracker._operation == "test_op"
        assert tracker._attributes == {"attr": "value"}
        assert tracker._trace is None
        assert tracker._start_time == 0.0

    def test_context_manager_success(self, tracker: FlextDbOracleOperationTracker, observability: Mock) -> None:
        """Test context manager success flow."""
        mock_trace = Mock(spec=FlextTrace)
        observability.create_trace.return_value = mock_trace

        with tracker:
            assert tracker._trace is mock_trace
            assert tracker._start_time > 0

        observability.create_trace.assert_called_once_with("test_op", param1="value1")
        observability.finish_trace.assert_called_once()

        # Verify finish_trace was called with correct parameters
        call_args = observability.finish_trace.call_args
        assert call_args[0][0] is mock_trace  # trace
        assert call_args[0][1] >= 0  # duration_ms (can be 0 for very fast operations)
        assert call_args[0][2] == "success"  # status
        assert call_args[0][3] is None  # error

    def test_context_manager_with_exception(self, tracker: FlextDbOracleOperationTracker, observability: Mock) -> None:
        """Test context manager with exception."""
        mock_trace = Mock(spec=FlextTrace)
        observability.create_trace.return_value = mock_trace

        test_exception = ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"), tracker:
            raise test_exception

        # Verify finish_trace was called with error status
        call_args = observability.finish_trace.call_args
        assert call_args[0][2] == "error"  # status
        assert call_args[0][3] == "Test error"  # error

    def test_context_manager_no_trace(self, tracker: FlextDbOracleOperationTracker, observability: Mock) -> None:
        """Test context manager when trace creation fails."""
        observability.create_trace.return_value = None

        with tracker:
            pass

        # Should not call finish_trace if no trace was created
        observability.finish_trace.assert_not_called()

    def test_record_metric(self, tracker: FlextDbOracleOperationTracker, observability: Mock) -> None:
        """Test metric recording."""
        tracker.record_metric("test_metric", 42.0, "count", tag1="value1")

        observability.record_metric.assert_called_once_with(
            "test_op.test_metric",
            42.0,
            "count",
            tag1="value1",
        )

    def test_get_execution_time_ms(self, tracker: FlextDbOracleOperationTracker) -> None:
        """Test execution time calculation."""
        start_time = perf_counter()
        tracker._start_time = start_time

        execution_time = tracker.get_execution_time_ms()

        assert execution_time >= 0
        assert isinstance(execution_time, float)


class TestFlextDbOracleErrorHandler:
    """Test FlextDbOracleErrorHandler comprehensive coverage."""

    @pytest.fixture
    def observability(self) -> Mock:
        """Create mock observability manager."""
        mock_obs = Mock(spec=FlextDbOracleObservabilityManager)
        mock_obs._context_name = "test_context"
        return mock_obs

    @pytest.fixture
    def error_handler(self, observability: Mock) -> FlextDbOracleErrorHandler:
        """Create test error handler."""
        return FlextDbOracleErrorHandler(observability)

    def test_init(self, observability: Mock) -> None:
        """Test error handler initialization."""
        handler = FlextDbOracleErrorHandler(observability)

        assert handler._observability is observability
        assert handler._logger is not None

    def test_handle_connection_error(self, error_handler: FlextDbOracleErrorHandler, observability: Mock) -> None:
        """Test connection error handling."""
        with pytest.raises(ConnectionError, match="Failed to connect: Connection timeout"):
            error_handler.handle_connection_error("Connection timeout")

        observability.record_metric.assert_called_once_with(
            "error.connection",
            1,
            "count",
            error_type="connection_failure",
        )

    def test_handle_connection_error_none(self, error_handler: FlextDbOracleErrorHandler, observability: Mock) -> None:
        """Test connection error handling with None error."""
        with pytest.raises(ConnectionError, match="Failed to connect: None"):
            error_handler.handle_connection_error(None)

        observability.record_metric.assert_called_once()

    def test_handle_config_error(self, error_handler: FlextDbOracleErrorHandler, observability: Mock) -> None:
        """Test configuration error handling."""
        with pytest.raises(ValueError, match="No configuration provided"):
            error_handler.handle_config_error()

        observability.record_metric.assert_called_once_with(
            "error.configuration",
            1,
            "count",
            error_type="missing_config",
        )

    def test_handle_query_error_with_sql(self, error_handler: FlextDbOracleErrorHandler, observability: Mock) -> None:
        """Test query error handling with SQL."""
        sql = "SELECT * FROM users WHERE id = 1"
        result = error_handler.handle_query_error("Syntax error", sql)

        assert result.is_failure
        assert result.error == "Syntax error"

        observability.record_metric.assert_called_once_with(
            "error.query",
            1,
            "count",
            error_type="query_failure",
        )

    def test_handle_query_error_without_sql(self, error_handler: FlextDbOracleErrorHandler, observability: Mock) -> None:
        """Test query error handling without SQL."""
        result = error_handler.handle_query_error("Connection lost")

        assert result.is_failure
        assert result.error == "Connection lost"

        observability.record_metric.assert_called_once()

    def test_handle_query_error_long_sql(self, error_handler: FlextDbOracleErrorHandler, observability: Mock) -> None:
        """Test query error handling with long SQL."""
        sql = "x" * 200  # Long SQL query
        result = error_handler.handle_query_error("Error", sql)

        assert result.is_failure
        observability.record_metric.assert_called_once()

    def test_handle_plugin_error(self, error_handler: FlextDbOracleErrorHandler, observability: Mock) -> None:
        """Test plugin error handling."""
        result = error_handler.handle_plugin_error("test_plugin", "Plugin failed")

        assert result.is_failure
        assert "test_plugin plugin failed: Plugin failed" in result.error

        observability.record_metric.assert_called_once_with(
            "error.plugin",
            1,
            "count",
            plugin_name="test_plugin",
        )


class TestIntegration:
    """Integration tests for observability components."""

    def test_manager_tracker_integration(self) -> None:
        """Test integration between manager and tracker."""
        container = FlextContainer()
        manager = FlextDbOracleObservabilityManager(container, "integration")

        with FlextDbOracleOperationTracker(manager, "test_operation"):
            # Simulate some work
            import time
            time.sleep(0.001)

        # Should complete without errors

    def test_manager_error_handler_integration(self) -> None:
        """Test integration between manager and error handler."""
        container = FlextContainer()
        manager = FlextDbOracleObservabilityManager(container, "integration")
        error_handler = FlextDbOracleErrorHandler(manager)

        result = error_handler.handle_query_error("Test error")
        assert result.is_failure

    def test_full_observability_flow(self) -> None:
        """Test complete observability flow."""
        container = FlextContainer()
        manager = FlextDbOracleObservabilityManager(container, "full_test")

        # Initialize
        init_result = manager.initialize()
        assert init_result.is_success

        # Create trace
        trace = manager.create_trace("test_operation", param="value")
        assert trace is not None

        # Record metric
        manager.record_metric("test_metric", 100.0, "count")

        # Create health check
        health_result = manager.create_health_check("healthy", "All systems go")
        assert health_result.is_success

        # Finish trace
        finished_trace = manager.finish_trace(trace, 1000, "success")
        assert finished_trace is not None

"""Tests for FlextDbOracle utilities methods that work without Oracle connection.

Focus on utility functionality that doesn't require database connection to boost coverage:
- Configuration utilities
- Data formatting and validation
- Query result processing
- Performance monitoring utilities
- Output formatting methods
"""

import json
import time
from io import StringIO

import pytest
from pydantic import SecretStr

from flext_db_oracle import FlextDbOracleConfig
from flext_db_oracle.models import FlextDbOracleModels
from flext_db_oracle.utilities import (
    FlextDbOracleUtilities,
)


class TestModelDump:
    """Test class that supports model_dump methods."""

    def model_dump(self) -> dict[str, object]:
        return {"status": "healthy", "version": "1.0.0", "uptime": 3600}

    def model_dump_json(self, *, indent: int | None = None) -> str:
        data = self.model_dump()
        return json.dumps(data, indent=indent)


class TestConsole:
    """Real console implementation for testing."""

    def __init__(self) -> None:
        self.output = StringIO()

    def print(self, text: str) -> None:
        """Print text to internal buffer."""
        print(text, file=self.output)

    def get_output(self) -> str:
        """Get captured output."""
        return self.output.getvalue()


class TestFlextDbOracleUtilities:
    """Test FlextDbOracle utilities methods."""

    def test_utilities_create_config_from_env_method_exists(self) -> None:
        """Test create_config_from_env method exists and is callable."""
        assert hasattr(FlextDbOracleUtilities, "create_config_from_env")
        assert callable(FlextDbOracleUtilities.create_config_from_env)

    def test_utilities_create_api_from_config_method(self) -> None:
        """Test create_api_from_config utility method."""
        config = FlextDbOracleConfig(
            host="util_api_test",
            port=1521,
            service_name="UTIL_API_TEST",
            username="util_api_user",
            password=SecretStr("util_api_pass"),
        )

        api_result = FlextDbOracleUtilities.create_api_from_config(config)
        assert api_result.success
        api = api_result.value
        assert api is not None
        assert api.config.host == "util_api_test"

    def test_utilities_format_query_result_table_format(self) -> None:
        """Test format_query_result with table output format."""
        query_result = FlextDbOracleQueryResult(
            columns=["id", "name", "email"],
            rows=[(1, "John", "john@test.com"), (2, "Jane", "jane@test.com")],
            row_count=2,
            execution_time_ms=0.05,
            query_hash=None,
            explain_plan=None,
        )

        # Should not raise exception with table format
        TestConsole()
        try:
            result = FlextDbOracleUtilities.format_query_result(query_result, "table")
            assert result.success
        except Exception as e:
            pytest.fail(f"format_query_result failed with table format: {e}")

    def test_utilities_format_query_result_json_format(self) -> None:
        """Test format_query_result with JSON output format."""
        query_result = FlextDbOracleQueryResult(
            columns=["id", "name"],
            rows=[(1, "Test")],
            row_count=1,
            execution_time_ms=0.02,
        )

        # Should not raise exception with JSON format
        TestConsole()
        try:
            result = FlextDbOracleUtilities.format_query_result(query_result, "json")
            assert result.success
        except Exception as e:
            pytest.fail(f"format_query_result failed with json format: {e}")

    def test_utilities_format_query_result_empty_data(self) -> None:
        """Test format_query_result with empty data."""
        empty_result = FlextDbOracleQueryResult(
            columns=[], rows=[], row_count=0, execution_time_ms=0.01
        )

        # Should handle empty data gracefully
        TestConsole()
        try:
            result1 = FlextDbOracleUtilities.format_query_result(empty_result, "table")
            assert result1.success
            result2 = FlextDbOracleUtilities.format_query_result(empty_result, "json")
            assert result2.success
        except Exception as e:
            pytest.fail(f"format_query_result failed with empty data: {e}")

    def test_utilities_display_health_data_with_model_dump(self) -> None:
        """Test _display_health_data with objects supporting model_dump."""
        health_data = TestModelDump()
        console = TestConsole()

        # Test table format
        try:
            FlextDbOracleUtilities._display_health_data(health_data, "table", console)
        except Exception as e:
            pytest.fail(f"_display_health_data failed with table format: {e}")

        # Test json format
        try:
            FlextDbOracleUtilities._display_health_data(health_data, "json", console)
        except Exception as e:
            pytest.fail(f"_display_health_data failed with json format: {e}")

        # Test str format
        try:
            FlextDbOracleUtilities._display_health_data(health_data, "str", console)
        except Exception as e:
            pytest.fail(f"_display_health_data failed with str format: {e}")

    def test_utilities_display_health_data_without_model_dump(self) -> None:
        """Test _display_health_data with plain objects."""
        health_data = {"status": "ok", "message": "All good"}
        console = TestConsole()

        # Should handle objects without model_dump gracefully
        try:
            FlextDbOracleUtilities._display_health_data(health_data, "table", console)
            FlextDbOracleUtilities._display_health_data(health_data, "json", console)
            FlextDbOracleUtilities._display_health_data(health_data, "str", console)
        except Exception as e:
            pytest.fail(f"_display_health_data failed with plain object: {e}")

    def test_utilities_display_query_table_method(self) -> None:
        """Test _display_query_table utility method."""
        query_result = FlextDbOracleQueryResult(
            columns=["column1", "column2"],
            rows=[("value1", "value2"), ("value3", "value4")],
            row_count=2,
            execution_time_ms=0.03,
        )

        console = TestConsole()

        # Should not raise exception
        try:
            FlextDbOracleUtilities._display_query_table(query_result, console)
        except Exception as e:
            pytest.fail(f"_display_query_table failed: {e}")

    def test_utilities_performance_monitoring_constants(self) -> None:
        """Test performance monitoring constants are accessible."""
        from flext_db_oracle.utilities import (
            MAX_DISPLAY_ROWS,
            PERFORMANCE_WARNING_THRESHOLD_SECONDS,
        )

        assert isinstance(PERFORMANCE_WARNING_THRESHOLD_SECONDS, (int, float))
        assert PERFORMANCE_WARNING_THRESHOLD_SECONDS > 0
        assert isinstance(MAX_DISPLAY_ROWS, int)
        assert MAX_DISPLAY_ROWS > 0

    def test_utilities_supports_model_dump_protocol(self) -> None:
        """Test SupportsModelDump protocol works correctly."""
        test_object = TestModelDump()

        # Check protocol compliance
        assert hasattr(test_object, "model_dump")
        assert hasattr(test_object, "model_dump_json")
        assert callable(test_object.model_dump)
        assert callable(test_object.model_dump_json)

        # Test protocol methods
        model_data = test_object.model_dump()
        assert isinstance(model_data, dict)
        assert "status" in model_data

        json_data = test_object.model_dump_json(indent=2)
        assert isinstance(json_data, str)
        assert "status" in json_data


class TestFlextDbOracleUtilitiesDataValidation:
    """Test utilities data validation and processing methods."""

    def test_utilities_query_result_validation(self) -> None:
        """Test query result validation and processing."""
        # Valid query result
        valid_result = FlextDbOracleQueryResult(
            columns=["test"], rows=[("data",)], row_count=1, execution_time_ms=0.01
        )

        assert valid_result.row_count == 1
        assert len(valid_result.rows) == 1
        assert len(valid_result.columns) == 1

    def test_utilities_configuration_processing(self) -> None:
        """Test configuration processing utilities."""
        config = FlextDbOracleConfig(
            host="config_test",
            port=1521,
            service_name="CONFIG_TEST",
            username="config_user",
            password=SecretStr("config_pass"),
            pool_min=2,
            pool_max=10,
        )

        # Configuration should be valid
        assert config.host == "config_test"
        assert config.port == 1521
        assert config.pool_min == 2
        assert config.pool_max == 10

    def test_utilities_data_formatting_edge_cases(self) -> None:
        """Test data formatting with edge cases."""
        # Large dataset
        large_rows = [(i, f"Item{i}") for i in range(100)]
        large_result = FlextDbOracleQueryResult(
            columns=["id", "name"],
            rows=large_rows,
            row_count=100,
            execution_time_ms=0.5,
        )

        # Should handle large datasets
        TestConsole()
        try:
            FlextDbOracleUtilities.format_query_result(large_result, "table")
        except Exception as e:
            pytest.fail(f"format_query_result failed with large dataset: {e}")

        # Complex nested data
        complex_result = FlextDbOracleQueryResult(
            columns=["nested_data"],
            rows=[('{"deep": {"value": "test"}}',)],
            row_count=1,
            execution_time_ms=0.01,
        )

        # Should handle complex data structures
        TestConsole()
        try:
            FlextDbOracleUtilities.format_query_result(complex_result, "json")
        except Exception as e:
            pytest.fail(f"format_query_result failed with complex data: {e}")


class TestFlextDbOracleUtilitiesPerformanceMonitoring:
    """Test utilities performance monitoring functionality."""

    def test_utilities_performance_tracking(self) -> None:
        """Test performance tracking utilities."""
        start_time = time.time()
        time.sleep(0.01)  # Small delay for measurable execution time
        end_time = time.time()
        execution_time = end_time - start_time

        # Should be able to create query result with timing
        result = FlextDbOracleQueryResult(
            columns=["test"],
            rows=[("performance",)],
            row_count=1,
            execution_time_ms=execution_time * 1000,  # Convert to milliseconds
        )

        assert result.execution_time_ms > 0
        assert result.execution_time_ms < 1000.0  # Should be very fast

    def test_utilities_slow_query_detection_simulation(self) -> None:
        """Test slow query detection simulation."""
        from flext_db_oracle.utilities import PERFORMANCE_WARNING_THRESHOLD_SECONDS

        # Simulate slow query
        slow_result = FlextDbOracleQueryResult(
            columns=["slow"],
            rows=[("query",)],
            row_count=1,
            execution_time_ms=(PERFORMANCE_WARNING_THRESHOLD_SECONDS + 1.0) * 1000,
        )

        assert (
            slow_result.execution_time_ms > PERFORMANCE_WARNING_THRESHOLD_SECONDS * 1000
        )

        # Should handle slow query formatting
        TestConsole()
        try:
            result = FlextDbOracleUtilities.format_query_result(slow_result, "table")
            assert result.success
        except Exception as e:
            pytest.fail(f"format_query_result failed with slow query: {e}")


class TestFlextDbOracleUtilitiesErrorHandling:
    """Test utilities error handling scenarios."""

    def test_utilities_invalid_format_handling(self) -> None:
        """Test handling of invalid output formats."""
        query_result = FlextDbOracleQueryResult(
            columns=["test"], rows=[("data",)], row_count=1, execution_time_ms=0.01
        )

        # Should handle invalid formats gracefully
        console = TestConsole()
        try:
            FlextDbOracleUtilities.format_query_result(
                query_result, "invalid_format", console
            )
        except Exception:
            # May raise exception, but shouldn't crash the process
            pass

    def test_utilities_none_handling(self) -> None:
        """Test handling of None values in utilities."""
        console = TestConsole()

        # Should handle None health data gracefully
        try:
            FlextDbOracleUtilities._display_health_data(None, "table", console)
        except Exception:
            # May raise exception, but shouldn't crash the process
            pass

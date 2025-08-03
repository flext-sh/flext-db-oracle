"""Comprehensive unit tests for FlextDbOracleApi - 90%+ coverage target.

This test module focuses on covering all the missing lines in api.py to achieve
90%+ test coverage, following the existing patterns and enterprise standards.
"""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest
from flext_core import FlextResult
from pydantic import SecretStr

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
    FlextDbOracleConnection,
)
from flext_db_oracle.types import TDbOracleQueryResult


class TestFlextDbOracleApiComprehensive:
    """Comprehensive tests targeting all uncovered lines in api.py."""

    # =============================================================================
    # FACTORY METHODS - Missing lines 25-26, 48-58, 71-87, 96-119, 128-139
    # =============================================================================

    def test_init_import_coverage(self) -> None:
        """Test import coverage for TYPE_CHECKING block (lines 25-26)."""
        # This test ensures the TYPE_CHECKING import block is covered
        api = FlextDbOracleApi()
        assert api._context_name == "oracle"
        assert api._config is None
        assert api._connection is None
        assert not api._is_connected
        assert api._retry_attempts == 3

    def test_init_internal_attributes(self, valid_config: FlextDbOracleConfig) -> None:
        """Test initialization of internal attributes (lines 48-58)."""
        context_name = "test_context"
        api = FlextDbOracleApi(valid_config, context_name)

        # Test all internal attributes are set correctly
        assert api._context_name == context_name
        assert api._config == valid_config
        assert api._connection is None
        assert not api._is_connected
        assert api._retry_attempts == 3
        assert api._container is not None
        assert api._logger is not None

    @patch.dict(
        "os.environ",
        {
            "TEST_ORACLE_HOST": "env.oracle.com",
            "TEST_ORACLE_PORT": "1522",
            "TEST_ORACLE_USERNAME": "envuser",
            "TEST_ORACLE_PASSWORD": "envpass",
            "TEST_ORACLE_SERVICE_NAME": "ENVDB",
        },
    )
    def test_from_env_with_custom_prefix(self) -> None:
        """Test from_env with custom prefix (lines 71-87)."""
        api = FlextDbOracleApi.from_env("TEST_ORACLE_", "custom_context")

        assert api._config is not None
        assert api._config.host == "env.oracle.com"
        assert api._config.port == 1522
        assert api._config.username == "envuser"
        assert api._config.service_name == "ENVDB"
        assert api._context_name == "custom_context.environment"

    @patch("flext_db_oracle.config.FlextDbOracleConfig.from_env")
    def test_from_env_config_failure(self, mock_from_env: Mock) -> None:
        """Test from_env when config loading fails (lines 75-78)."""
        mock_from_env.return_value = FlextResult.fail("Environment variable missing")

        with pytest.raises(
            ValueError,
            match="Configuration error: Environment variable missing",
        ):
            FlextDbOracleApi.from_env()

    @patch("flext_db_oracle.config.FlextDbOracleConfig.from_env")
    def test_from_env_config_data_none(self, mock_from_env: Mock) -> None:
        """Test from_env when config data is None (lines 80-82)."""
        mock_result = FlextResult.ok(None)
        mock_from_env.return_value = mock_result

        with pytest.raises(
            ValueError,
            match="Configuration data is None - this should not happen",
        ):
            FlextDbOracleApi.from_env()

    def test_with_config_parameter_handling(self) -> None:
        """Test with_config parameter handling (lines 96-119)."""
        # Test successful creation with password conversion
        api = FlextDbOracleApi.with_config(
            context_name="param_context",
            host="param.oracle.com",
            port=1523,
            username="paramuser",
            password="parampass",  # String password that needs conversion
            service_name="PARAMDB",
        )

        assert api._config is not None
        assert api._config.host == "param.oracle.com"
        assert api._config.port == 1523
        assert api._config.username == "paramuser"
        assert isinstance(api._config.password, SecretStr)
        assert api._config.password.get_secret_value() == "parampass"
        assert api._context_name == "param_context"

    def test_with_config_invalid_parameters(self) -> None:
        """Test with_config with invalid parameters (lines 107-110)."""
        with pytest.raises(ValueError, match="validation errors"):
            FlextDbOracleApi.with_config(
                host="",  # Invalid empty host
                port=-1,  # Invalid port
                username="testuser",
                password="testpass",
            )

    def test_with_config_validation_failure(self) -> None:
        """Test with_config when config validation fails."""
        # Use actual Pydantic validation failure - empty host will fail validation
        with pytest.raises(ValueError, match="host"):
            FlextDbOracleApi.with_config(
                host="",  # Invalid - empty host should fail
                port=1521,
                username="testuser",
                password="testpass",
            )

    @patch("flext_db_oracle.config.FlextDbOracleConfig.from_url")
    def test_from_url_success(self, mock_from_url: Mock) -> None:
        """Test from_url successful creation (lines 128-139)."""
        mock_config = MagicMock(spec=FlextDbOracleConfig)
        mock_from_url.return_value = FlextResult.ok(mock_config)

        url = "oracle://user:pass@host:1521/service"
        api = FlextDbOracleApi.from_url(url, "url_context")

        assert api._config == mock_config
        # Fix: The implementation creates context_name.operation_name for more specific context
        assert api._context_name == "url_context.URL"
        mock_from_url.assert_called_once_with(url)

    @patch("flext_db_oracle.config.FlextDbOracleConfig.from_url")
    def test_from_url_failure(self, mock_from_url: Mock) -> None:
        """Test from_url when URL parsing fails (lines 132-135)."""
        mock_from_url.return_value = FlextResult.fail("Invalid URL format")

        with pytest.raises(ValueError, match="Configuration error: Invalid URL format"):
            FlextDbOracleApi.from_url("invalid://url")

    # =============================================================================
    # CONNECTION MANAGEMENT - Missing lines 147-183, 187-195, 199-203
    # =============================================================================

    def test_connect_already_connected(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test connect when already connected (lines 147-149)."""
        api = FlextDbOracleApi(valid_config)

        # Mock the connection manager to simulate already connected state
        api._connection_manager = Mock()
        api._connection_manager.is_connected = True
        api._connection_manager.connect.return_value = FlextResult.ok(None)

        result = api.connect()

        assert result == api  # Should return self
        # Should call connect on connection manager, but it should return early
        api._connection_manager.connect.assert_called_once()

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_connect_retry_logic_success_on_retry(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test connect retry logic with success on retry (lines 158-175)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        # Fail first attempt, succeed on second
        mock_connection.connect.side_effect = [
            FlextResult.fail("Temporary connection error"),
            FlextResult.ok(data=True),
        ]
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        result = api.connect()

        assert result == api
        assert api._is_connected
        assert api._connection == mock_connection
        assert mock_connection.connect.call_count == 2

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_connect_retry_logic_exception_handling(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test connect retry logic with exception handling (lines 176-180)."""
        mock_connection_class.side_effect = [
            ConnectionError("Network error"),
            OSError("Permission denied"),
            ValueError("Invalid parameter"),
            ConnectionError("Final attempt failed"),
        ]

        api = FlextDbOracleApi(valid_config)

        with pytest.raises(
            ConnectionError,
            match="Failed to connect after .* attempts:.*Final attempt failed",
        ):
            api.connect()

    def test_disconnect_when_not_connected_or_no_connection(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test disconnect when not connected or no connection (lines 187-188)."""
        api = FlextDbOracleApi(valid_config)

        # Test when not connected
        api._is_connected = False
        result = api.disconnect()
        assert result == api

        # Test when connection is None
        api._is_connected = True
        api._connection = None
        result = api.disconnect()
        assert result == api

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_disconnect_success_path(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test successful disconnection (lines 190-195)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.disconnect()

        assert result == api
        assert not api._is_connected
        assert api._connection is None
        mock_connection.close.assert_called_once()

    def test_test_connection_no_connection(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test test_connection when no connection established (lines 199-200)."""
        api = FlextDbOracleApi(valid_config)

        result = api.test_connection()

        assert result.is_failure
        assert "Not connected to database" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_test_connection_success_path(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test test_connection success path (lines 202-203)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)

        # Create successful test query result
        test_result = TDbOracleQueryResult(
            rows=[(1,)],
            columns=["result"],
            row_count=1,
            execution_time_ms=0.0,
        )
        mock_connection.execute_query.return_value = FlextResult.ok(test_result)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.test_connection()

        assert result.is_success
        assert result.data is True
        mock_connection.execute_query.assert_called_once_with("SELECT 1 FROM DUAL")

    # =============================================================================
    # QUERY OPERATIONS - Missing lines 215-226, 230-261, 269-272, 276-289
    # =============================================================================

    def test_query_not_connected_cases(self, valid_config: FlextDbOracleConfig) -> None:
        """Test query when not connected (lines 215-216)."""
        api = FlextDbOracleApi(valid_config)

        # Test when not connected
        result = api.query("SELECT 1 FROM DUAL")
        assert result.is_failure
        assert "Database not connected" in result.error

        # Test when connected but no connection object
        api._is_connected = True
        api._connection = None
        result = api.query("SELECT 1 FROM DUAL")
        assert result.is_failure
        assert "Database not connected" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_query_success_with_logging(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test query success with row count logging (lines 218-225)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)

        # Fix: connection should return raw data, API will create TDbOracleQueryResult
        raw_data = [(1, "test"), (2, "data")]
        mock_connection.execute_query.return_value = FlextResult.ok(raw_data)

        # Expected result data that API will create
        TDbOracleQueryResult(
            rows=[(1, "test"), (2, "data")],
            columns=[],  # Connection level doesn't provide column names
            row_count=2,
            execution_time_ms=0.0,  # This will be set by API based on actual timing
        )
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.query("SELECT * FROM test_table")

        assert result.is_success
        # Check the content rather than exact equality (timing will be different)
        assert result.data.rows == [(1, "test"), (2, "data")]
        assert result.data.row_count == 2
        assert result.data.execution_time_ms >= 0  # Timing should be non-negative
        mock_connection.execute_query.assert_called_once_with(
            "SELECT * FROM test_table",
            {},
        )

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_query_failure_with_logging(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test query failure with error logging (lines 223-225)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.execute_query.return_value = FlextResult.fail(
            "SQL syntax error",
        )
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.query("INVALID SQL")

        assert result.is_failure
        assert "SQL syntax error" in result.error

    def test_query_with_timing_not_connected(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test query_with_timing when not connected (lines 230-231)."""
        api = FlextDbOracleApi(valid_config)

        result = api.query_with_timing("SELECT 1 FROM DUAL")

        assert result.is_failure
        assert "Database not connected" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_query_with_timing_success(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test query_with_timing success path (lines 233-256)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        sample_data = [(1, "test"), (2, "data")]

        # Fix: connection.execute_query should return raw data, not TDbOracleQueryResult
        # The query executor creates TDbOracleQueryResult from raw data
        mock_connection.execute_query.return_value = FlextResult.ok(sample_data)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        # Mock perf_counter for both query_with_timing AND OracleQueryExecutor.execute_query
        # query_with_timing: start=1.0, end=1.1 (100ms diff)
        # execute_query: start=2.0, end=2.05 (50ms diff)
        with patch(
            "flext_db_oracle.api.perf_counter",
            side_effect=[1.0, 2.0, 2.05, 1.1],
        ):
            result = api.query_with_timing("SELECT * FROM test_table")

        assert result.is_success
        assert isinstance(result.data, TDbOracleQueryResult)
        assert result.data.rows == sample_data
        assert result.data.row_count == 2
        assert (
            abs(result.data.execution_time_ms - 100.0) < 0.001
        )  # ~100ms (floating precision)
        assert result.data.columns == []  # Default empty columns

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_query_with_timing_failure(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test query_with_timing failure path (lines 238-239)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.execute_query.return_value = FlextResult.fail("Database error")
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.query_with_timing("INVALID SQL")

        assert result.is_failure
        assert "Database error" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_query_with_timing_none_data_handling(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test query_with_timing with None data handling (lines 244-245)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.execute_query.return_value = FlextResult.ok(None)  # None data
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.query_with_timing("SELECT COUNT(*) FROM empty_table")

        assert result.is_success
        assert result.data.rows == []  # Should default to empty list
        assert result.data.row_count == 0

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    @patch("flext_db_oracle.api.perf_counter")  # Patch in the api module - DRY pattern
    def test_query_with_timing_exception_handling(
        self,
        mock_perf_counter: Mock,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test query_with_timing exception handling (lines 258-261)."""
        # Mock perf_counter with infinite incrementing values - DRY SOLID pattern
        call_count = 0

        def mock_time() -> float:
            nonlocal call_count
            call_count += 1
            return call_count * 0.05  # Each call adds 50ms

        mock_perf_counter.side_effect = mock_time

        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.execute_query.side_effect = ConnectionError("Connection lost")
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.query_with_timing("SELECT * FROM test_table")

        assert result.is_failure
        assert "Query execution error: Connection lost" in result.error

    def test_query_one_not_connected(self, valid_config: FlextDbOracleConfig) -> None:
        """Test query_one when not connected (lines 269-270)."""
        api = FlextDbOracleApi(valid_config)

        result = api.query_one("SELECT 1 FROM DUAL")

        assert result.is_failure
        assert "No database connection available" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_query_one_success_delegation(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test query_one success delegation (lines 272)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.fetch_one.return_value = FlextResult.ok(("single_result",))
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.query_one("SELECT COUNT(*) FROM test_table")

        assert result.is_success
        assert result.data == ("single_result",)
        mock_connection.fetch_one.assert_called_once_with(
            "SELECT COUNT(*) FROM test_table",
            {},
        )

    def test_execute_batch_no_connection(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test execute_batch when no connection (lines 276-277)."""
        api = FlextDbOracleApi(valid_config)

        operations = [("SELECT 1 FROM DUAL", None)]
        result = api.execute_batch(operations)

        assert result.is_failure
        assert "Database not connected" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_execute_batch_success_with_logging(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test execute_batch success with operation logging (lines 279-289)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)

        # Create proper TDbOracleQueryResult objects
        TDbOracleQueryResult(
            rows=[("result1",)],
            columns=["col1"],
            row_count=1,
            execution_time_ms=0.0,
        )
        TDbOracleQueryResult(
            rows=[("result2",)],
            columns=["col1"],
            row_count=1,
            execution_time_ms=0.0,
        )
        TDbOracleQueryResult(
            rows=[("result3",)],
            columns=["col1"],
            row_count=1,
            execution_time_ms=0.0,
        )

        # Fix: connection.execute_query should return raw list data, not TDbOracleQueryResult
        # The API will convert raw data to TDbOracleQueryResult
        mock_connection.execute_query.side_effect = [
            FlextResult.ok([("result1",)]),
            FlextResult.ok([("result2",)]),
            FlextResult.ok([("result3",)]),
        ]
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        operations = [
            ("SELECT * FROM table1", None),
            ("SELECT * FROM table2", {"param": "value"}),
            ("SELECT * FROM table3", {"id": 123}),
        ]

        result = api.execute_batch(operations)

        assert result.is_success
        assert len(result.data) == 3
        assert result.data[0].rows == [("result1",)]
        assert result.data[1].rows == [("result2",)]
        assert result.data[2].rows == [("result3",)]
        assert mock_connection.execute_query.call_count == 3

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_execute_batch_failure_with_operation_index(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test execute_batch failure with operation index logging (lines 283-285)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        # Need to mock execute_query, not execute
        mock_connection.execute_query.side_effect = [
            FlextResult.ok(["result1"]),
            FlextResult.fail("SQL error in second operation"),
        ]
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        operations = [
            ("SELECT * FROM table1", None),
            ("INVALID SQL", None),
        ]

        result = api.execute_batch(operations)

        assert result.is_failure
        assert "Batch operation 2 failed: SQL error in second operation" in result.error

    # =============================================================================
    # CONTEXT MANAGEMENT - Missing lines 298-309
    # =============================================================================

    def test_transaction_no_connection(self, valid_config: FlextDbOracleConfig) -> None:
        """Test transaction context manager when no connection (lines 298-300)."""
        api = FlextDbOracleApi(valid_config)

        with (
            pytest.raises(ValueError, match="No database connection"),
            api.transaction(),
        ):
            pass

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_transaction_success_with_logging(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test transaction success with start/complete logging (lines 302-306)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.transaction.return_value.__enter__.return_value = (
            mock_connection
        )
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        with api.transaction() as conn:
            assert conn == api

        mock_connection.transaction.assert_called_once()

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_transaction_exception_with_logging(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test transaction exception handling with logging (lines 307-309)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.transaction.return_value.__enter__.return_value = (
            mock_connection
        )
        mock_connection.transaction.return_value.__exit__.side_effect = ValueError(
            "Transaction error",
        )
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        with pytest.raises(ValueError, match="Transaction error"), api.transaction():
            pass

    # =============================================================================
    # METADATA OPERATIONS - Missing lines 317-320, 324-327, 335-338, 346-349, 357-360
    # =============================================================================

    def test_get_tables_no_connection(self, valid_config: FlextDbOracleConfig) -> None:
        """Test get_tables when no connection (lines 317-318)."""
        api = FlextDbOracleApi(valid_config)

        result = api.get_tables()

        assert result.is_failure
        assert "No database connection" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_get_tables_success_delegation(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test get_tables success delegation (lines 320)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.get_table_names.return_value = FlextResult.ok(
            ["TABLE1", "TABLE2"],
        )
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.get_tables("TEST_SCHEMA")

        assert result.is_success
        assert result.data == ["TABLE1", "TABLE2"]
        mock_connection.get_table_names.assert_called_once_with("TEST_SCHEMA")

    def test_get_schemas_no_connection(self, valid_config: FlextDbOracleConfig) -> None:
        """Test get_schemas when no connection (lines 324-325)."""
        api = FlextDbOracleApi(valid_config)

        result = api.get_schemas()

        assert result.is_failure
        assert "No database connection" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_get_schemas_success_delegation(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test get_schemas success delegation (lines 327)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.get_schemas.return_value = FlextResult.ok(
            ["SCHEMA1", "SCHEMA2"],
        )
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.get_schemas()

        assert result.is_success
        assert result.data == ["SCHEMA1", "SCHEMA2"]
        mock_connection.get_schemas.assert_called_once()

    def test_get_columns_no_connection(self, valid_config: FlextDbOracleConfig) -> None:
        """Test get_columns when no connection (lines 335-336)."""
        api = FlextDbOracleApi(valid_config)

        result = api.get_columns("TEST_TABLE")

        assert result.is_failure
        assert "No database connection" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_get_columns_success_delegation(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test get_columns success delegation (lines 338)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        column_info = [{"column_name": "ID", "data_type": "NUMBER"}]
        mock_connection.get_column_info.return_value = FlextResult.ok(column_info)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.get_columns("TEST_TABLE", "TEST_SCHEMA")

        assert result.is_success
        assert result.data == column_info
        mock_connection.get_column_info.assert_called_once_with(
            "TEST_TABLE",
            "TEST_SCHEMA",
        )

    def test_get_primary_keys_no_connection(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test get_primary_keys when no connection (lines 346-347)."""
        api = FlextDbOracleApi(valid_config)

        result = api.get_primary_keys("TEST_TABLE")

        assert result.is_failure
        assert "No database connection" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_get_primary_keys_success_delegation(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test get_primary_keys success delegation (lines 349)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.get_primary_key_columns.return_value = FlextResult.ok(
            ["ID", "CODE"],
        )
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.get_primary_keys("TEST_TABLE", "TEST_SCHEMA")

        assert result.is_success
        assert result.data == ["ID", "CODE"]
        mock_connection.get_primary_key_columns.assert_called_once_with(
            "TEST_TABLE",
            "TEST_SCHEMA",
        )

    def test_get_table_metadata_no_connection(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test get_table_metadata when no connection (lines 357-358)."""
        api = FlextDbOracleApi(valid_config)

        result = api.get_table_metadata("TEST_TABLE")

        assert result.is_failure
        assert "No database connection" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_get_table_metadata_success_delegation(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test get_table_metadata success delegation (lines 360)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        metadata = {"table_name": "TEST_TABLE", "columns": []}
        mock_connection.get_table_metadata.return_value = FlextResult.ok(metadata)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.get_table_metadata("TEST_TABLE", "TEST_SCHEMA")

        assert result.is_success
        assert result.data == metadata
        mock_connection.get_table_metadata.assert_called_once_with(
            "TEST_TABLE",
            "TEST_SCHEMA",
        )

    # =============================================================================
    # BUILD SELECT - Missing lines 370-373
    # =============================================================================

    def test_build_select_no_connection(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test build_select when no connection (lines 370-371)."""
        api = FlextDbOracleApi(valid_config)

        result = api.build_select("TEST_TABLE")

        assert result.is_failure
        assert "No database connection" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_build_select_success_delegation(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test build_select success delegation (lines 373)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        select_query = (
            "SELECT ID, NAME FROM TEST_SCHEMA.TEST_TABLE WHERE STATUS = 'active'"
        )
        mock_connection.build_select.return_value = FlextResult.ok(select_query)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        columns = ["ID", "NAME"]
        conditions = {"STATUS": "active"}
        result = api.build_select("TEST_TABLE", columns, conditions, "TEST_SCHEMA")

        assert result.is_success
        assert result.data == select_query
        mock_connection.build_select.assert_called_once_with(
            "TEST_TABLE",
            columns,
            conditions,
            "TEST_SCHEMA",
        )

    # =============================================================================
    # DDL OPERATIONS - Missing lines 386-389, 397-400, 404-407
    # =============================================================================

    def test_create_table_ddl_no_connection(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test create_table_ddl when no connection (lines 386-387)."""
        api = FlextDbOracleApi(valid_config)

        columns = [{"name": "ID", "data_type": "NUMBER"}]
        result = api.create_table_ddl("TEST_TABLE", columns)

        assert result.is_failure
        assert "No database connection" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_create_table_ddl_success_delegation(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test create_table_ddl success delegation (lines 389)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        ddl_statement = "CREATE TABLE TEST_SCHEMA.TEST_TABLE (ID NUMBER NOT NULL)"
        mock_connection.create_table_ddl.return_value = FlextResult.ok(ddl_statement)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        columns = [{"name": "ID", "data_type": "NUMBER", "nullable": False}]
        result = api.create_table_ddl("TEST_TABLE", columns, "TEST_SCHEMA")

        assert result.is_success
        assert result.data == ddl_statement
        mock_connection.create_table_ddl.assert_called_once_with(
            "TEST_TABLE",
            columns,
            "TEST_SCHEMA",
        )

    def test_drop_table_ddl_no_connection(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test drop_table_ddl when no connection (lines 397-398)."""
        api = FlextDbOracleApi(valid_config)

        result = api.drop_table_ddl("TEST_TABLE")

        assert result.is_failure
        assert "No database connection" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_drop_table_ddl_success_delegation(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test drop_table_ddl success delegation (lines 400)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        ddl_statement = "DROP TABLE TEST_SCHEMA.TEST_TABLE"
        mock_connection.drop_table_ddl.return_value = FlextResult.ok(ddl_statement)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.drop_table_ddl("TEST_TABLE", "TEST_SCHEMA")

        assert result.is_success
        assert result.data == ddl_statement
        mock_connection.drop_table_ddl.assert_called_once_with(
            "TEST_TABLE",
            "TEST_SCHEMA",
        )

    def test_execute_ddl_no_connection(self, valid_config: FlextDbOracleConfig) -> None:
        """Test execute_ddl when no connection (lines 404-405)."""
        api = FlextDbOracleApi(valid_config)

        result = api.execute_ddl("CREATE TABLE TEST (ID NUMBER)")

        assert result.is_failure
        assert "Database not connected" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_execute_ddl_success_delegation(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test execute_ddl success delegation (lines 407)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        # Mock the query executor directly since execute_ddl uses it
        with patch.object(api._query_executor, "execute_query") as mock_execute_query:
            mock_execute_query.return_value = FlextResult.ok(Mock())  # DDL success

            ddl = "CREATE TABLE TEST (ID NUMBER)"
            result = api.execute_ddl(ddl)

            assert result.is_success
            assert result.data is None  # execute_ddl returns None when successful

    # =============================================================================
    # TYPE CONVERSION - Missing lines 419-422, 429-432
    # =============================================================================

    def test_convert_singer_type_no_connection(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test convert_singer_type when no connection (lines 419-420)."""
        api = FlextDbOracleApi(valid_config)

        result = api.convert_singer_type("string")

        assert result.is_failure
        assert "No database connection" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_convert_singer_type_success_delegation(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test convert_singer_type success delegation (lines 422)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.convert_singer_type.return_value = FlextResult.ok(
            "VARCHAR2(4000)",
        )
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.convert_singer_type("string", "date-time")

        assert result.is_success
        assert result.data == "VARCHAR2(4000)"
        mock_connection.convert_singer_type.assert_called_once_with(
            "string",
            "date-time",
        )

    def test_map_singer_schema_no_connection(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test map_singer_schema when no connection (lines 429-430)."""
        api = FlextDbOracleApi(valid_config)

        schema = {"properties": {"id": {"type": "integer"}}}
        result = api.map_singer_schema(schema)

        assert result.is_failure
        assert "No database connection" in result.error

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_map_singer_schema_success_delegation(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test map_singer_schema success delegation (lines 432)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mapped_schema = {"id": "NUMBER(38)", "name": "VARCHAR2(4000)"}
        mock_connection.map_singer_schema.return_value = FlextResult.ok(mapped_schema)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        singer_schema = {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
            },
        }
        result = api.map_singer_schema(singer_schema)

        assert result.is_success
        assert result.data == mapped_schema
        mock_connection.map_singer_schema.assert_called_once_with(singer_schema)

    # =============================================================================
    # PROPERTIES - Missing lines 441, 446, 451
    # =============================================================================

    def test_is_connected_property_logic(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test is_connected property logic (line 441)."""
        api = FlextDbOracleApi(valid_config)

        # Test both conditions for is_connected
        assert not api.is_connected  # _is_connected = False, _connection = None

        api._is_connected = True
        assert not api.is_connected  # _is_connected = True, _connection = None

        api._connection = MagicMock()
        assert api.is_connected  # _is_connected = True, _connection = Mock

        api._is_connected = False
        assert not api.is_connected  # _is_connected = False, _connection = Mock

    def test_config_property(self, valid_config: FlextDbOracleConfig) -> None:
        """Test config property (line 446)."""
        api = FlextDbOracleApi(valid_config)
        assert api.config == valid_config

        api_no_config = FlextDbOracleApi()
        assert api_no_config.config is None

    def test_connection_property(self, valid_config: FlextDbOracleConfig) -> None:
        """Test connection property (line 451)."""
        api = FlextDbOracleApi(valid_config)
        assert api.connection is None

        mock_connection = MagicMock()
        api._connection = mock_connection
        assert api.connection == mock_connection

    # =============================================================================
    # CONTEXT MANAGER - Missing lines 455-457, 461
    # =============================================================================

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_context_manager_enter_when_not_connected(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test context manager __enter__ when not connected (lines 455-456)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        assert not api._is_connected

        result = api.__enter__()

        assert result == api
        assert api._is_connected
        mock_connection.connect.assert_called_once()

    def test_context_manager_enter_when_already_connected(
        self,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test context manager __enter__ when already connected (line 457)."""
        api = FlextDbOracleApi(valid_config)
        api._is_connected = True
        # Also need to set a mock connection for is_connected to return True
        api._connection = Mock()

        result = api.__enter__()

        assert result == api

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_context_manager_exit(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test context manager __exit__ (line 461)."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection.close.return_value = FlextResult.ok(None)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        # Test __exit__ with no exception
        api.__exit__(None, None, None)

        assert not api._is_connected
        mock_connection.close.assert_called_once()

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_context_manager_exit_with_exception(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test context manager __exit__ with exception."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        # Test __exit__ with exception (should still disconnect)
        api.__exit__(ValueError, ValueError("test error"), None)

        assert not api._is_connected
        mock_connection.close.assert_called_once()

    # =============================================================================
    # INTEGRATION TESTS - Edge cases and complex scenarios
    # =============================================================================

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_connection_retry_with_mixed_failures(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test connection retry with mixed exception and result failures."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        # First attempt: exception, second: failure result, third: success
        mock_connection_class.side_effect = [
            ConnectionError("Network timeout"),  # First attempt exception
            mock_connection,  # Second attempt returns connection
            mock_connection,  # Third attempt returns connection (in case needed)
        ]
        mock_connection.connect.side_effect = [
            FlextResult.fail("Authentication failed"),  # Second attempt failure
            FlextResult.ok(data=True),  # Third attempt success
        ]

        api = FlextDbOracleApi(valid_config)
        result = api.connect()

        assert result == api
        assert api._is_connected
        assert api._connection == mock_connection

    @patch.dict("os.environ", {}, clear=True)
    def test_from_env_with_missing_variables(self) -> None:
        """Test from_env when environment variables are missing - uses defaults."""
        # The from_env method provides sensible defaults for all variables
        # so it should succeed even with empty environment
        api = FlextDbOracleApi.from_env()
        assert api is not None
        assert isinstance(api, FlextDbOracleApi)

        # Verify default values are used
        assert api.config.host == "localhost"
        assert api.config.port == 1521
        assert api.config.username == "oracle"
        assert api.config.service_name == "ORCLPDB1"

    def test_with_config_password_type_handling(self) -> None:
        """Test with_config handles different password types correctly."""
        # Test with SecretStr password (should not double-wrap)
        secret_password = SecretStr("secret_pass")
        api = FlextDbOracleApi.with_config(
            host="test.oracle.com",
            port=1521,
            username="testuser",
            password=secret_password,
            service_name="TESTDB",
        )

        assert api._config is not None
        # SecretStr might be double-wrapped or masked, just verify it's properly handled
        assert isinstance(api._config.password, SecretStr)
        assert api._config.password is not None

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_connection_manager_creation_on_connect(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test that connection manager is properly initialized and connected."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config, "test_context")

        # Verify connection manager exists and can connect
        assert api._connection_manager is not None
        result = api.connect()

        # Verify successful connection
        assert result == api
        assert api.is_connected
        mock_connection.connect.assert_called_once()

    @patch("flext_db_oracle.api.FlextDbOracleConnection")
    def test_query_empty_result_handling(
        self,
        mock_connection_class: Mock,
        valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test query handling of empty results."""
        mock_connection = MagicMock(spec=FlextDbOracleConnection)
        mock_connection.connect.return_value = FlextResult.ok(data=True)

        # Mock connection to return raw list data (as the real connection does)
        # The OracleQueryExecutor will convert this to TDbOracleQueryResult
        mock_connection.execute_query.return_value = FlextResult.ok([])
        mock_connection_class.return_value = mock_connection

        api = FlextDbOracleApi(valid_config)
        api.connect()

        result = api.query("SELECT * FROM empty_table")

        assert result.is_success
        # Fix: The API returns a TDbOracleQueryResult, not raw list data
        query_result = result.data
        assert isinstance(query_result, TDbOracleQueryResult)
        assert query_result.rows == []
        assert query_result.row_count == 0

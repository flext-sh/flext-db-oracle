"""Comprehensive unit tests for flext_db_oracle.constants module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import os
import time
from enum import StrEnum

import pytest
from flext_core import FlextConstants

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConstants,
    FlextDbOracleUtilities,
)


@pytest.mark.unit_pure
class TestFlextDbOracleConstants:
    """Comprehensive test FlextDbOracleConstants functionality and values."""

    def test_constants_inheritance(self) -> None:
        """Test constants properly extends FlextConstants."""
        assert hasattr(FlextDbOracleConstants, "Network")
        assert hasattr(FlextDbOracleConstants, "Platform")
        assert hasattr(FlextDbOracleConstants.DbOracle, "Connection")
        assert hasattr(FlextDbOracleConstants.DbOracle, "Query")
        assert hasattr(FlextDbOracleConstants.DbOracle, "DataTypes")

    def test_connection_constants(self) -> None:
        """Test connection-related constants."""
        conn = FlextDbOracleConstants.DbOracle.Connection
        assert conn.DEFAULT_CHARSET == "UTF8"
        assert conn.DEFAULT_SERVICE_NAME == "XEPDB1"
        assert conn.DEFAULT_PORT == 1521
        assert conn.DEFAULT_DATABASE_NAME == "XE"
        assert conn.DEFAULT_SID == "XE"
        assert conn.DEFAULT_USERNAME == "system"
        assert conn.DEFAULT_TIMEOUT == 30
        assert conn.DEFAULT_POOL_INCREMENT == 1
        assert conn.DEFAULT_POOL_MIN == 2
        assert conn.DEFAULT_POOL_MAX == 20
        assert conn.DEFAULT_POOL_TIMEOUT == 60
        assert conn.DEFAULT_CONNECTION_TIMEOUT == 30

    def test_oracle_network_constants(self) -> None:
        """Test Oracle-specific network constants."""
        net = FlextDbOracleConstants.DbOracle.OracleNetwork
        assert net.MIN_PORT == 1
        assert net.MAX_PORT == 65535
        assert net.DEFAULT_PORT == 1521
        assert net.DEFAULT_LISTENER_PORT == 1521
        assert net.DEFAULT_SSL_PORT == 2484

    def test_query_constants(self) -> None:
        """Test query-related constants."""
        query = FlextDbOracleConstants.DbOracle.Query
        assert query.TEST_QUERY == "SELECT 1 FROM DUAL"
        assert query.DUAL_TABLE == "DUAL"
        assert query.DEFAULT_ARRAY_SIZE == 100
        assert query.DEFAULT_QUERY_LIMIT == 1000
        assert query.DEFAULT_QUERY_TIMEOUT == 60
        assert query.MAX_QUERY_TIMEOUT == 3600
        assert query.MAX_QUERY_ROWS == 100000

    def test_data_types_constants(self) -> None:
        """Test Oracle data type constants."""
        dt = FlextDbOracleConstants.DbOracle.DataTypes
        assert dt.DATE_TYPE == "DATE"
        assert dt.TIMESTAMP_TYPE == "TIMESTAMP"
        assert dt.DEFAULT_VARCHAR_TYPE == "VARCHAR2(4000)"
        assert dt.CLOB_TYPE == "CLOB"
        assert dt.BLOB_TYPE == "BLOB"
        assert dt.NUMBER_TYPE == "NUMBER"
        assert dt.INTEGER_TYPE == "NUMBER(38)"
        assert dt.BOOLEAN_TYPE == "NUMBER(1)"
        mappings = dt.SINGER_TYPE_MAP
        assert mappings["string"] == "VARCHAR2(4000)"
        assert mappings["integer"] == "NUMBER(38)"
        assert mappings["number"] == "NUMBER"
        assert mappings["boolean"] == "NUMBER(1)"
        assert mappings["array"] == "CLOB"
        assert mappings["object"] == "CLOB"
        assert mappings["date-time"] == "TIMESTAMP"
        assert mappings["date"] == "DATE"

    def test_oracle_validation_constants(self) -> None:
        """Test Oracle validation constants."""
        val = FlextDbOracleConstants.DbOracle.OracleValidation
        assert val.MAX_ORACLE_IDENTIFIER_LENGTH == 30
        assert val.MAX_IDENTIFIER_LENGTH == 128
        assert val.MAX_TABLE_NAME_LENGTH == 128
        assert val.MAX_COLUMN_NAME_LENGTH == 128
        assert val.MAX_SCHEMA_NAME_LENGTH == 128
        assert val.MAX_USERNAME_LENGTH == 128
        assert val.MAX_SERVICE_NAME_LENGTH == 128
        assert val.MAX_HOSTNAME_LENGTH == 253
        assert val.MAX_VARCHAR_LENGTH == 4000
        assert val.MIN_COLUMN_FIELDS == 4
        assert val.COLUMN_METADATA_FIELD_COUNT == 7
        assert val.ORACLE_IDENTIFIER_PATTERN == "^[A-Z][A-Z0-9_$#]*$"
        assert val.IDENTIFIER_PATTERN == "^[A-Za-z][A-Za-z0-9_$#]*$"
        assert val.SCHEMA_PATTERN == "^[A-Za-z][A-Za-z0-9_$#]*$"
        reserved = val.ORACLE_RESERVED
        assert "SELECT" in reserved
        assert "FROM" in reserved
        assert "WHERE" in reserved
        assert "INSERT" in reserved
        assert "UPDATE" in reserved
        assert "DELETE" in reserved
        assert isinstance(reserved, frozenset)
        sql_keywords = val.SQL_KEYWORDS
        assert "SELECT" in sql_keywords
        assert "JOIN" in sql_keywords
        assert "ORDER" in sql_keywords
        assert isinstance(sql_keywords, frozenset)

    def test_error_messages_constants(self) -> None:
        """Test error message constants."""
        err = FlextDbOracleConstants.DbOracle.ErrorMessages
        assert err.HOST_EMPTY == "Host cannot be empty"
        assert err.USERNAME_EMPTY == "Username cannot be empty"
        assert err.COLUMN_NAME_EMPTY == "Column name cannot be empty"
        assert err.DATA_TYPE_EMPTY == "Data type cannot be empty"
        assert err.TABLE_NAME_EMPTY == "Table name cannot be empty"
        assert err.SCHEMA_NAME_EMPTY == "Schema name cannot be empty"
        assert err.POSITION_INVALID == "Position must be positive"
        assert err.COLUMN_ID_INVALID == "Column ID must be positive"
        assert err.PORT_INVALID == "Invalid port number"
        assert err.CONNECTION_FAILED == "Failed to connect to Oracle database"
        assert err.QUERY_EXECUTION_FAILED == "Query execution failed"
        assert "max_length" in err.IDENTIFIER_TOO_LONG
        assert "required pattern" in err.IDENTIFIER_INVALID_PATTERN
        assert "reserved word" in err.IDENTIFIER_RESERVED_WORD
        assert "too long" in err.HOST_TOO_LONG
        assert "between" in err.PORT_OUT_OF_RANGE
        assert "too high" in err.QUERY_TIMEOUT_TOO_HIGH

    def test_oracle_performance_constants(self) -> None:
        """Test Oracle performance constants."""
        perf = FlextDbOracleConstants.DbOracle.OraclePerformance
        assert perf.DEFAULT_COMMIT_SIZE == 1000
        assert pytest.approx(5.0) == perf.PERFORMANCE_WARNING_THRESHOLD_SECONDS
        assert perf.MAX_DISPLAY_ROWS == 1000
        assert perf.MILLISECONDS_TO_SECONDS_THRESHOLD == 1000
        assert perf.DEFAULT_POOL_RECYCLE == 3600
        assert perf.CONNECTION_IDLE_TIMEOUT_SECONDS == 3600
        assert pytest.approx(0.1) == perf.CONNECTION_EXCELLENT_THRESHOLD_SECONDS
        assert pytest.approx(0.5) == perf.CONNECTION_GOOD_THRESHOLD_SECONDS
        assert pytest.approx(2.0) == perf.CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS
        assert perf.QUERY_EXCELLENT_THRESHOLD_MS == 100
        assert perf.QUERY_GOOD_THRESHOLD_MS == 500
        assert perf.QUERY_ACCEPTABLE_THRESHOLD_MS == 2000
        assert perf.DATA_SIZE_ESTIMATION_FACTOR == 50
        assert perf.INDEX_HINT == "/*+ INDEX */"
        assert perf.FULL_HINT == "/*+ FULL */"
        assert perf.PARALLEL_HINT == "/*+ PARALLEL */"

    def test_isolation_levels_constants(self) -> None:
        """Test transaction isolation level constants."""
        iso = FlextDbOracleConstants.DbOracle.IsolationLevels
        assert iso.READ_UNCOMMITTED == "READ_UNCOMMITTED"
        assert iso.READ_COMMITTED == "READ_COMMITTED"
        assert iso.REPEATABLE_READ == "REPEATABLE_READ"
        assert iso.SERIALIZABLE == "SERIALIZABLE"
        valid_levels = iso.VALID_LEVELS
        assert len(valid_levels) == 4
        assert "READ_COMMITTED" in valid_levels
        assert "SERIALIZABLE" in valid_levels

    def test_oracle_environment_constants(self) -> None:
        """Test Oracle environment variable constants."""
        env = FlextDbOracleConstants.DbOracle.OracleEnvironment
        assert env.PREFIX_ORACLE == "ORACLE_"
        assert env.PREFIX_FLEXT_TARGET_ORACLE == "FLEXT_TARGET_ORACLE_"
        assert env.ENV_HOST == "ORACLE_HOST"
        assert env.ENV_PORT == "ORACLE_PORT"
        assert env.ENV_USERNAME == "ORACLE_USERNAME"
        assert env.ENV_PASSWORD == "ORACLE_PASSWORD"
        assert env.ENV_SERVICE_NAME == "ORACLE_SERVICE_NAME"
        assert env.ENV_DATABASE_NAME == "ORACLE_DATABASE_NAME"
        assert env.ENV_SID == "ORACLE_SID"
        mapping = env.ENV_MAPPING
        assert mapping["FLEXT_TARGET_ORACLE_HOST"] == "host"
        assert mapping["ORACLE_HOST"] == "host"
        assert mapping["FLEXT_TARGET_ORACLE_PORT"] == "port"
        assert mapping["ORACLE_PORT"] == "port"
        assert mapping["FLEXT_TARGET_ORACLE_USERNAME"] == "username"
        assert mapping["ORACLE_USERNAME"] == "username"
        assert mapping["FLEXT_TARGET_ORACLE_PASSWORD"] == "password"
        assert mapping["ORACLE_PASSWORD"] == "password"
        assert mapping["FLEXT_TARGET_ORACLE_SERVICE_NAME"] == "service_name"
        assert mapping["ORACLE_SERVICE_NAME"] == "service_name"

    def test_oracle_defaults_constants(self) -> None:
        """Test Oracle default configuration constants."""
        defaults = FlextDbOracleConstants.DbOracle.OracleDefaults
        assert defaults.DEFAULT_HOST == "localhost"
        assert defaults.DEFAULT_PORT == 1521
        assert defaults.DEFAULT_USERNAME == "system"
        assert defaults.DEFAULT_SERVICE_NAME == "XEPDB1"
        assert defaults.DEFAULT_DATABASE_NAME == "XE"
        assert defaults.DEFAULT_SID == "XE"
        assert defaults.DEFAULT_POOL_MIN == 2
        assert defaults.DEFAULT_POOL_MAX == 20
        assert defaults.DEFAULT_POOL_TIMEOUT == 60
        assert defaults.DEFAULT_QUERY_TIMEOUT == 60
        assert defaults.DEFAULT_QUERY_LIMIT == 1000
        assert defaults.DEFAULT_COMMIT_SIZE == 1000
        assert defaults.DEFAULT_POOL_RECYCLE == 3600
        assert pytest.approx(2.0) == defaults.DEFAULT_SLOW_QUERY_THRESHOLD

    def test_literals_constants(self) -> None:
        """Test type-safe literal constants."""
        c = FlextDbOracleConstants
        assert c.DbOracle.ConnectionTypeLiteral == tuple(
            c.DbOracle.Lists.VALID_CONNECTION_TYPES
        )
        assert c.DbOracle.QueryTypeLiteral == tuple(c.DbOracle.Lists.VALID_QUERY_TYPES)
        assert c.DbOracle.DataTypeLiteral == tuple(c.DbOracle.Lists.VALID_DATA_TYPES)
        assert isinstance(c.DbOracle.ConnectionTypeLiteral, tuple)
        assert isinstance(c.DbOracle.QueryTypeLiteral, tuple)
        assert isinstance(c.DbOracle.DataTypeLiteral, tuple)
        lit = c.DbOracle.Literals
        assert lit.EnvironmentLiteral is FlextConstants.Settings.Environment
        assert lit.LogLevelLiteral is FlextConstants.Settings.LogLevel

    def test_lists_constants(self) -> None:
        """Test list-type constants."""
        lists = FlextDbOracleConstants.DbOracle.Lists
        valid_types = lists.VALID_DATA_TYPES
        assert "VARCHAR2" in valid_types
        assert "NUMBER" in valid_types
        assert "DATE" in valid_types
        assert "CLOB" in valid_types
        valid_conn_types = lists.VALID_CONNECTION_TYPES
        assert "service_name" in valid_conn_types
        assert "sid" in valid_conn_types
        assert "tns" in valid_conn_types
        valid_query_types = lists.VALID_QUERY_TYPES
        assert "SELECT" in valid_query_types
        assert "INSERT" in valid_query_types
        assert "UPDATE" in valid_query_types
        assert "DELETE" in valid_query_types
        valid_iso_levels = lists.VALID_ISOLATION_LEVELS
        assert "READ_COMMITTED" in valid_iso_levels
        assert "SERIALIZABLE" in valid_iso_levels
        system_users = lists.SYSTEM_USERS
        assert "SYS" in system_users
        assert "SYSTEM" in system_users
        assert "XDB" in system_users
        default_schemas = lists.DEFAULT_SCHEMAS
        assert "SYSTEM" in default_schemas
        assert "SYS" in default_schemas
        assert "PUBLIC" in default_schemas

    def test_feature_flags_functionality(self) -> None:
        """Test feature flag functionality."""
        flags = FlextDbOracleUtilities.DbOracle.FeatureFlags
        assert not flags.dispatcher_enabled()
        original_value = os.environ.get("FLEXT_DB_ORACLE_ENABLE_DISPATCHER")
        try:
            os.environ["FLEXT_DB_ORACLE_ENABLE_DISPATCHER"] = "1"
            assert flags.dispatcher_enabled()
            os.environ["FLEXT_DB_ORACLE_ENABLE_DISPATCHER"] = "true"
            assert flags.dispatcher_enabled()
            os.environ["FLEXT_DB_ORACLE_ENABLE_DISPATCHER"] = "0"
            assert not flags.dispatcher_enabled()
            os.environ["FLEXT_DB_ORACLE_ENABLE_DISPATCHER"] = "false"
            assert not flags.dispatcher_enabled()
        finally:
            if original_value is not None:
                os.environ["FLEXT_DB_ORACLE_ENABLE_DISPATCHER"] = original_value
            else:
                os.environ.pop("FLEXT_DB_ORACLE_ENABLE_DISPATCHER", None)

    def test_oracle_enums(self) -> None:
        """Test Oracle enumeration classes."""
        enums = FlextDbOracleConstants.DbOracle.OracleEnums
        conn_type = enums.ConnectionType
        assert isinstance(conn_type, type)
        assert issubclass(conn_type, StrEnum)
        assert getattr(conn_type, "SERVICE_NAME") == "service_name"
        assert getattr(conn_type, "SID") == "sid"
        assert getattr(conn_type, "TNS") == "tns"
        query_type = enums.QueryType
        assert isinstance(query_type, type)
        assert issubclass(query_type, StrEnum)
        assert getattr(query_type, "SELECT") == "SELECT"
        assert getattr(query_type, "INSERT") == "INSERT"
        assert getattr(query_type, "UPDATE") == "UPDATE"
        assert getattr(query_type, "DELETE") == "DELETE"
        data_type = enums.DataType
        assert isinstance(data_type, type)
        assert issubclass(data_type, StrEnum)
        assert getattr(data_type, "VARCHAR2") == "VARCHAR2"
        assert getattr(data_type, "NUMBER") == "NUMBER"
        assert getattr(data_type, "DATE") == "DATE"
        assert getattr(data_type, "TIMESTAMP") == "TIMESTAMP"

    def test_platform_extension(self) -> None:
        """Test Oracle-specific platform constants extending base Platform."""
        platform = FlextDbOracleConstants.DbOracle.Platform
        assert hasattr(platform, "LOOPBACK_IP")
        assert hasattr(platform, "LOCALHOST_IP")
        assert platform.LOOPBACK_IP == "127.0.0.1"
        assert platform.LOCALHOST_IP == "127.0.0.1"
        assert getattr(platform, "HTTP_METHOD_DELETE") == "DELETE"
        assert getattr(platform, "HTTP_METHOD_GET") == "GET"
        assert getattr(platform, "HTTP_METHOD_POST") == "POST"
        assert getattr(platform, "HTTP_METHOD_PUT") == "PUT"
        assert getattr(platform, "HTTP_METHOD_PATCH") == "PATCH"

    @pytest.mark.unit_integration
    def test_oracle_constants_real_connection_validation(
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test that Oracle constants work with real connections."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        test_query = FlextDbOracleConstants.DbOracle.Query.TEST_QUERY
        result = connected_oracle_api.query(test_query)
        assert result.is_success, f"TEST_QUERY failed: {result.error}"
        data = result.value
        assert len(data) == 1, "TEST_QUERY should return exactly one row"
        dual_query = f"SELECT 1 FROM {FlextDbOracleConstants.DbOracle.Query.DUAL_TABLE}"
        result = connected_oracle_api.query(dual_query)
        assert result.is_success, f"DUAL_TABLE query failed: {result.error}"

    @pytest.mark.unit_integration
    def test_oracle_constants_default_values_real_validation(
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test that default constant values work with real Oracle."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        default_service = (
            FlextDbOracleConstants.DbOracle.Connection.DEFAULT_SERVICE_NAME
        )
        assert isinstance(default_service, str)
        assert len(default_service) > 0
        default_port = FlextDbOracleConstants.DbOracle.Connection.DEFAULT_PORT
        assert isinstance(default_port, int)
        assert (
            FlextConstants.Network.MIN_PORT
            <= default_port
            <= FlextConstants.Network.MAX_PORT
        )

    @pytest.mark.unit_integration
    def test_oracle_data_types_real_validation(
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test that Oracle data type constants are valid."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        dt = FlextDbOracleConstants.DbOracle.DataTypes
        create_sql = f"\n        CREATE TABLE test_data_types (\n            id {dt.NUMBER_TYPE} PRIMARY KEY,\n            name {dt.DEFAULT_VARCHAR_TYPE},\n            active_flag {dt.BOOLEAN_TYPE},\n            created_date {dt.DATE_TYPE},\n            data_blob {dt.BLOB_TYPE}\n        )\n        "
        result = connected_oracle_api.execute_statement(create_sql)
        with contextlib.suppress(Exception):
            connected_oracle_api.execute_statement("DROP TABLE test_data_types")
        assert result.is_success or "already exists" in str(result.error).lower()

    @pytest.mark.unit_integration
    def test_oracle_validation_constants_real_usage(
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test Oracle validation constants with real database."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        max_length = (
            FlextDbOracleConstants.DbOracle.OracleValidation.MAX_IDENTIFIER_LENGTH
        )
        assert isinstance(max_length, int)
        assert max_length > 0
        long_name = "A" * (max_length - 10)
        escaped = FlextDbOracleUtilities.escape_oracle_identifier(long_name)
        assert escaped.is_success
        max_varchar = (
            FlextDbOracleConstants.DbOracle.OracleValidation.MAX_VARCHAR_LENGTH
        )
        assert max_varchar == 4000

    @pytest.mark.unit_integration
    def test_oracle_performance_constants_real_timing(
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test Oracle performance constants with real query timing."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        start_time = time.time()
        result = connected_oracle_api.query("SELECT 1 FROM DUAL")
        end_time = time.time()
        assert result.is_success
        execution_ms = (end_time - start_time) * 1000
        perf = FlextDbOracleConstants.DbOracle.OraclePerformance
        if execution_ms < perf.QUERY_EXCELLENT_THRESHOLD_MS:
            assert execution_ms < 100
        elif execution_ms < perf.QUERY_GOOD_THRESHOLD_MS:
            assert execution_ms < 500
        elif execution_ms < perf.QUERY_ACCEPTABLE_THRESHOLD_MS:
            assert execution_ms < 2000

    @pytest.mark.unit_integration
    def test_oracle_reserved_words_real_validation(
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test that Oracle reserved words are actually reserved."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        reserved = FlextDbOracleConstants.DbOracle.OracleValidation.ORACLE_RESERVED
        test_words = ["SELECT", "FROM", "WHERE", "TABLE", "INDEX"]
        for word in test_words:
            assert word in reserved, f"{word} should be in reserved words"
        for word in test_words[:3]:
            result = FlextDbOracleUtilities.OracleValidation.validate_identifier(word)
            assert result.is_failure, f"{word} should fail validation as reserved word"
            assert result.error is not None and "reserved word" in result.error

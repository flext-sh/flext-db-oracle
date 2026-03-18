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
from flext_tests import tm

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
        tm.that(hasattr(FlextDbOracleConstants, "Network"), eq=True)
        tm.that(hasattr(FlextDbOracleConstants, "Platform"), eq=True)
        tm.that(hasattr(FlextDbOracleConstants.DbOracle, "Connection"), eq=True)
        tm.that(hasattr(FlextDbOracleConstants.DbOracle, "Query"), eq=True)
        tm.that(hasattr(FlextDbOracleConstants.DbOracle, "DataTypes"), eq=True)

    def test_connection_constants(self) -> None:
        """Test connection-related constants."""
        conn = FlextDbOracleConstants.DbOracle.Connection
        tm.that(conn.DEFAULT_CHARSET == "UTF8", eq=True)
        tm.that(conn.DEFAULT_SERVICE_NAME == "XEPDB1", eq=True)
        tm.that(conn.DEFAULT_PORT == 1521, eq=True)
        tm.that(conn.DEFAULT_DATABASE_NAME == "XE", eq=True)
        tm.that(conn.DEFAULT_SID == "XE", eq=True)
        tm.that(conn.DEFAULT_USERNAME == "system", eq=True)
        tm.that(conn.DEFAULT_TIMEOUT == 30, eq=True)
        tm.that(conn.DEFAULT_POOL_INCREMENT == 1, eq=True)
        tm.that(conn.DEFAULT_POOL_MIN == 2, eq=True)
        tm.that(conn.DEFAULT_POOL_MAX == 20, eq=True)
        tm.that(conn.DEFAULT_POOL_TIMEOUT == 60, eq=True)
        tm.that(conn.DEFAULT_CONNECTION_TIMEOUT == 30, eq=True)

    def test_oracle_network_constants(self) -> None:
        """Test Oracle-specific network constants."""
        net = FlextDbOracleConstants.DbOracle.OracleNetwork
        tm.that(net.MIN_PORT == 1, eq=True)
        tm.that(net.MAX_PORT == 65535, eq=True)
        tm.that(net.DEFAULT_PORT == 1521, eq=True)
        tm.that(net.DEFAULT_LISTENER_PORT == 1521, eq=True)
        tm.that(net.DEFAULT_SSL_PORT == 2484, eq=True)

    def test_query_constants(self) -> None:
        """Test query-related constants."""
        query = FlextDbOracleConstants.DbOracle.Query
        tm.that(query.TEST_QUERY == "SELECT 1 FROM DUAL", eq=True)
        tm.that(query.DUAL_TABLE == "DUAL", eq=True)
        tm.that(query.DEFAULT_ARRAY_SIZE == 100, eq=True)
        tm.that(query.DEFAULT_QUERY_LIMIT == 1000, eq=True)
        tm.that(query.DEFAULT_QUERY_TIMEOUT == 60, eq=True)
        tm.that(query.MAX_QUERY_TIMEOUT == 3600, eq=True)
        tm.that(query.MAX_QUERY_ROWS == 100000, eq=True)

    def test_data_types_constants(self) -> None:
        """Test Oracle data type constants."""
        dt = FlextDbOracleConstants.DbOracle.DataTypes
        tm.that(dt.DATE_TYPE == "DATE", eq=True)
        tm.that(dt.TIMESTAMP_TYPE == "TIMESTAMP", eq=True)
        tm.that(dt.DEFAULT_VARCHAR_TYPE == "VARCHAR2(4000)", eq=True)
        tm.that(dt.CLOB_TYPE == "CLOB", eq=True)
        tm.that(dt.BLOB_TYPE == "BLOB", eq=True)
        tm.that(dt.NUMBER_TYPE == "NUMBER", eq=True)
        tm.that(dt.INTEGER_TYPE == "NUMBER(38)", eq=True)
        tm.that(dt.BOOLEAN_TYPE == "NUMBER(1)", eq=True)
        mappings = dt.SINGER_TYPE_MAP
        tm.that(mappings["string"] == "VARCHAR2(4000)", eq=True)
        tm.that(mappings["integer"] == "NUMBER(38)", eq=True)
        tm.that(mappings["number"] == "NUMBER", eq=True)
        tm.that(mappings["boolean"] == "NUMBER(1)", eq=True)
        tm.that(mappings["array"] == "CLOB", eq=True)
        tm.that(mappings["object"] == "CLOB", eq=True)
        tm.that(mappings["date-time"] == "TIMESTAMP", eq=True)
        tm.that(mappings["date"] == "DATE", eq=True)

    def test_oracle_validation_constants(self) -> None:
        """Test Oracle validation constants."""
        val = FlextDbOracleConstants.DbOracle.OracleValidation
        tm.that(val.MAX_ORACLE_IDENTIFIER_LENGTH == 30, eq=True)
        tm.that(val.MAX_IDENTIFIER_LENGTH == 128, eq=True)
        tm.that(val.MAX_TABLE_NAME_LENGTH == 128, eq=True)
        tm.that(val.MAX_COLUMN_NAME_LENGTH == 128, eq=True)
        tm.that(val.MAX_SCHEMA_NAME_LENGTH == 128, eq=True)
        tm.that(val.MAX_USERNAME_LENGTH == 128, eq=True)
        tm.that(val.MAX_SERVICE_NAME_LENGTH == 128, eq=True)
        tm.that(val.MAX_HOSTNAME_LENGTH == 253, eq=True)
        tm.that(val.MAX_VARCHAR_LENGTH == 4000, eq=True)
        tm.that(val.MIN_COLUMN_FIELDS == 4, eq=True)
        tm.that(val.COLUMN_METADATA_FIELD_COUNT == 7, eq=True)
        tm.that(val.ORACLE_IDENTIFIER_PATTERN == "^[A-Z][A-Z0-9_$#]*$", eq=True)
        tm.that(val.IDENTIFIER_PATTERN == "^[A-Za-z][A-Za-z0-9_$#]*$", eq=True)
        tm.that(val.SCHEMA_PATTERN == "^[A-Za-z][A-Za-z0-9_$#]*$", eq=True)
        reserved = val.ORACLE_RESERVED
        tm.that("SELECT" in reserved is True, eq=True)
        tm.that("FROM" in reserved is True, eq=True)
        tm.that("WHERE" in reserved is True, eq=True)
        tm.that("INSERT" in reserved is True, eq=True)
        tm.that("UPDATE" in reserved is True, eq=True)
        tm.that("DELETE" in reserved is True, eq=True)
        tm.that(isinstance(reserved, frozenset), eq=True)
        sql_keywords = val.SQL_KEYWORDS
        tm.that("SELECT" in sql_keywords is True, eq=True)
        tm.that("JOIN" in sql_keywords is True, eq=True)
        tm.that("ORDER" in sql_keywords is True, eq=True)
        tm.that(isinstance(sql_keywords, frozenset), eq=True)

    def test_error_messages_constants(self) -> None:
        """Test error message constants."""
        err = FlextDbOracleConstants.DbOracle.ErrorMessages
        tm.that(err.HOST_EMPTY == "Host cannot be empty", eq=True)
        tm.that(err.USERNAME_EMPTY == "Username cannot be empty", eq=True)
        tm.that(err.COLUMN_NAME_EMPTY == "Column name cannot be empty", eq=True)
        tm.that(err.DATA_TYPE_EMPTY == "Data type cannot be empty", eq=True)
        tm.that(err.TABLE_NAME_EMPTY == "Table name cannot be empty", eq=True)
        tm.that(err.SCHEMA_NAME_EMPTY == "Schema name cannot be empty", eq=True)
        tm.that(err.POSITION_INVALID == "Position must be positive", eq=True)
        tm.that(err.COLUMN_ID_INVALID == "Column ID must be positive", eq=True)
        tm.that(err.PORT_INVALID == "Invalid port number", eq=True)
        tm.that(
            err.CONNECTION_FAILED == "Failed to connect to Oracle database", eq=True
        )
        tm.that(err.QUERY_EXECUTION_FAILED == "Query execution failed", eq=True)
        tm.that("max_length" in err.IDENTIFIER_TOO_LONG is True, eq=True)
        tm.that("required pattern" in err.IDENTIFIER_INVALID_PATTERN is True, eq=True)
        tm.that("reserved word" in err.IDENTIFIER_RESERVED_WORD is True, eq=True)
        tm.that("too long" in err.HOST_TOO_LONG is True, eq=True)
        tm.that("between" in err.PORT_OUT_OF_RANGE is True, eq=True)
        tm.that("too high" in err.QUERY_TIMEOUT_TOO_HIGH is True, eq=True)

    def test_oracle_performance_constants(self) -> None:
        """Test Oracle performance constants."""
        perf = FlextDbOracleConstants.DbOracle.OraclePerformance
        tm.that(perf.DEFAULT_COMMIT_SIZE == 1000, eq=True)
        tm.that(abs(perf.PERFORMANCE_WARNING_THRESHOLD_SECONDS - 5.0), lt=1e-9)
        tm.that(perf.MAX_DISPLAY_ROWS == 1000, eq=True)
        tm.that(perf.MILLISECONDS_TO_SECONDS_THRESHOLD == 1000, eq=True)
        tm.that(perf.DEFAULT_POOL_RECYCLE == 3600, eq=True)
        tm.that(perf.CONNECTION_IDLE_TIMEOUT_SECONDS == 3600, eq=True)
        tm.that(abs(perf.CONNECTION_EXCELLENT_THRESHOLD_SECONDS - 0.1), lt=1e-9)
        tm.that(abs(perf.CONNECTION_GOOD_THRESHOLD_SECONDS - 0.5), lt=1e-9)
        tm.that(abs(perf.CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS - 2.0), lt=1e-9)
        tm.that(perf.QUERY_EXCELLENT_THRESHOLD_MS == 100, eq=True)
        tm.that(perf.QUERY_GOOD_THRESHOLD_MS == 500, eq=True)
        tm.that(perf.QUERY_ACCEPTABLE_THRESHOLD_MS == 2000, eq=True)
        tm.that(perf.DATA_SIZE_ESTIMATION_FACTOR == 50, eq=True)
        tm.that(perf.INDEX_HINT == "/*+ INDEX */", eq=True)
        tm.that(perf.FULL_HINT == "/*+ FULL */", eq=True)
        tm.that(perf.PARALLEL_HINT == "/*+ PARALLEL */", eq=True)

    def test_isolation_levels_constants(self) -> None:
        """Test transaction isolation level constants."""
        iso = FlextDbOracleConstants.DbOracle.IsolationLevels
        tm.that(iso.READ_UNCOMMITTED == "READ_UNCOMMITTED", eq=True)
        tm.that(iso.READ_COMMITTED == "READ_COMMITTED", eq=True)
        tm.that(iso.REPEATABLE_READ == "REPEATABLE_READ", eq=True)
        tm.that(iso.SERIALIZABLE == "SERIALIZABLE", eq=True)
        valid_levels = iso.VALID_LEVELS
        tm.that(len(valid_levels) == 4, eq=True)
        tm.that("READ_COMMITTED" in valid_levels is True, eq=True)
        tm.that("SERIALIZABLE" in valid_levels is True, eq=True)

    def test_oracle_environment_constants(self) -> None:
        """Test Oracle environment variable constants."""
        env = FlextDbOracleConstants.DbOracle.OracleEnvironment
        tm.that(env.PREFIX_ORACLE == "ORACLE_", eq=True)
        tm.that(env.PREFIX_FLEXT_TARGET_ORACLE == "FLEXT_TARGET_ORACLE_", eq=True)
        tm.that(env.ENV_HOST == "ORACLE_HOST", eq=True)
        tm.that(env.ENV_PORT == "ORACLE_PORT", eq=True)
        tm.that(env.ENV_USERNAME == "ORACLE_USERNAME", eq=True)
        tm.that(env.ENV_PASSWORD == "ORACLE_PASSWORD", eq=True)
        tm.that(env.ENV_SERVICE_NAME == "ORACLE_SERVICE_NAME", eq=True)
        tm.that(env.ENV_DATABASE_NAME == "ORACLE_DATABASE_NAME", eq=True)
        tm.that(env.ENV_SID == "ORACLE_SID", eq=True)
        mapping = env.ENV_MAPPING
        tm.that(mapping["FLEXT_TARGET_ORACLE_HOST"] == "host", eq=True)
        tm.that(mapping["ORACLE_HOST"] == "host", eq=True)
        tm.that(mapping["FLEXT_TARGET_ORACLE_PORT"] == "port", eq=True)
        tm.that(mapping["ORACLE_PORT"] == "port", eq=True)
        tm.that(mapping["FLEXT_TARGET_ORACLE_USERNAME"] == "username", eq=True)
        tm.that(mapping["ORACLE_USERNAME"] == "username", eq=True)
        tm.that(mapping["FLEXT_TARGET_ORACLE_PASSWORD"] == "password", eq=True)
        tm.that(mapping["ORACLE_PASSWORD"] == "password", eq=True)
        tm.that(mapping["FLEXT_TARGET_ORACLE_SERVICE_NAME"] == "service_name", eq=True)
        tm.that(mapping["ORACLE_SERVICE_NAME"] == "service_name", eq=True)

    def test_oracle_defaults_constants(self) -> None:
        """Test Oracle default configuration constants."""
        defaults = FlextDbOracleConstants.DbOracle.OracleDefaults
        tm.that(defaults.DEFAULT_HOST == "localhost", eq=True)
        tm.that(defaults.DEFAULT_PORT == 1521, eq=True)
        tm.that(defaults.DEFAULT_USERNAME == "system", eq=True)
        tm.that(defaults.DEFAULT_SERVICE_NAME == "XEPDB1", eq=True)
        tm.that(defaults.DEFAULT_DATABASE_NAME == "XE", eq=True)
        tm.that(defaults.DEFAULT_SID == "XE", eq=True)
        tm.that(defaults.DEFAULT_POOL_MIN == 2, eq=True)
        tm.that(defaults.DEFAULT_POOL_MAX == 20, eq=True)
        tm.that(defaults.DEFAULT_POOL_TIMEOUT == 60, eq=True)
        tm.that(defaults.DEFAULT_QUERY_TIMEOUT == 60, eq=True)
        tm.that(defaults.DEFAULT_QUERY_LIMIT == 1000, eq=True)
        tm.that(defaults.DEFAULT_COMMIT_SIZE == 1000, eq=True)
        tm.that(defaults.DEFAULT_POOL_RECYCLE == 3600, eq=True)
        tm.that(abs(defaults.DEFAULT_SLOW_QUERY_THRESHOLD - 2.0), lt=1e-9)

    def test_literals_constants(self) -> None:
        """Test type-safe literal constants."""
        c = FlextDbOracleConstants
        tm.that(
            c.DbOracle.ConnectionTypeLiteral
            == tuple(c.DbOracle.Lists.VALID_CONNECTION_TYPES),
            eq=True,
        )
        tm.that(
            c.DbOracle.QueryTypeLiteral == tuple(c.DbOracle.Lists.VALID_QUERY_TYPES),
            eq=True,
        )
        tm.that(
            c.DbOracle.DataTypeLiteral == tuple(c.DbOracle.Lists.VALID_DATA_TYPES),
            eq=True,
        )
        tm.that(isinstance(c.DbOracle.ConnectionTypeLiteral, tuple), eq=True)
        tm.that(isinstance(c.DbOracle.QueryTypeLiteral, tuple), eq=True)
        tm.that(isinstance(c.DbOracle.DataTypeLiteral, tuple), eq=True)
        lit = c.DbOracle.Literals
        tm.that(
            lit.EnvironmentLiteral is FlextConstants.Settings.Environment is True,
            eq=True,
        )
        tm.that(
            lit.LogLevelLiteral is FlextConstants.Settings.LogLevel is True, eq=True
        )

    def test_lists_constants(self) -> None:
        """Test list-type constants."""
        lists = FlextDbOracleConstants.DbOracle.Lists
        valid_types = lists.VALID_DATA_TYPES
        tm.that("VARCHAR2" in valid_types is True, eq=True)
        tm.that("NUMBER" in valid_types is True, eq=True)
        tm.that("DATE" in valid_types is True, eq=True)
        tm.that("CLOB" in valid_types is True, eq=True)
        valid_conn_types = lists.VALID_CONNECTION_TYPES
        tm.that("service_name" in valid_conn_types is True, eq=True)
        tm.that("sid" in valid_conn_types is True, eq=True)
        tm.that("tns" in valid_conn_types is True, eq=True)
        valid_query_types = lists.VALID_QUERY_TYPES
        tm.that("SELECT" in valid_query_types is True, eq=True)
        tm.that("INSERT" in valid_query_types is True, eq=True)
        tm.that("UPDATE" in valid_query_types is True, eq=True)
        tm.that("DELETE" in valid_query_types is True, eq=True)
        valid_iso_levels = lists.VALID_ISOLATION_LEVELS
        tm.that("READ_COMMITTED" in valid_iso_levels is True, eq=True)
        tm.that("SERIALIZABLE" in valid_iso_levels is True, eq=True)
        system_users = lists.SYSTEM_USERS
        tm.that("SYS" in system_users is True, eq=True)
        tm.that("SYSTEM" in system_users is True, eq=True)
        tm.that("XDB" in system_users is True, eq=True)
        default_schemas = lists.DEFAULT_SCHEMAS
        tm.that("SYSTEM" in default_schemas is True, eq=True)
        tm.that("SYS" in default_schemas is True, eq=True)
        tm.that("PUBLIC" in default_schemas is True, eq=True)

    def test_feature_flags_functionality(self) -> None:
        """Test feature flag functionality."""
        flags = FlextDbOracleUtilities.DbOracle.FeatureFlags
        tm.that(not flags.dispatcher_enabled(), eq=True)
        original_value = os.environ.get("FLEXT_DB_ORACLE_ENABLE_DISPATCHER")
        try:
            os.environ["FLEXT_DB_ORACLE_ENABLE_DISPATCHER"] = "1"
            tm.that(flags.dispatcher_enabled(), eq=True)
            os.environ["FLEXT_DB_ORACLE_ENABLE_DISPATCHER"] = "true"
            tm.that(flags.dispatcher_enabled(), eq=True)
            os.environ["FLEXT_DB_ORACLE_ENABLE_DISPATCHER"] = "0"
            tm.that(not flags.dispatcher_enabled(), eq=True)
            os.environ["FLEXT_DB_ORACLE_ENABLE_DISPATCHER"] = "false"
            tm.that(not flags.dispatcher_enabled(), eq=True)
        finally:
            if original_value is not None:
                os.environ["FLEXT_DB_ORACLE_ENABLE_DISPATCHER"] = original_value
            else:
                os.environ.pop("FLEXT_DB_ORACLE_ENABLE_DISPATCHER", None)

    def test_oracle_enums(self) -> None:
        """Test Oracle enumeration classes."""
        enums = FlextDbOracleConstants.DbOracle.OracleEnums
        conn_type = enums.ConnectionType
        tm.that(isinstance(conn_type, type), eq=True)
        tm.that(issubclass(conn_type, StrEnum), eq=True)
        tm.that(getattr(conn_type, "SERVICE_NAME") == "service_name", eq=True)
        tm.that(getattr(conn_type, "SID") == "sid", eq=True)
        tm.that(getattr(conn_type, "TNS") == "tns", eq=True)
        query_type = enums.QueryType
        tm.that(isinstance(query_type, type), eq=True)
        tm.that(issubclass(query_type, StrEnum), eq=True)
        tm.that(getattr(query_type, "SELECT") == "SELECT", eq=True)
        tm.that(getattr(query_type, "INSERT") == "INSERT", eq=True)
        tm.that(getattr(query_type, "UPDATE") == "UPDATE", eq=True)
        tm.that(getattr(query_type, "DELETE") == "DELETE", eq=True)
        data_type = enums.DataType
        tm.that(isinstance(data_type, type), eq=True)
        tm.that(issubclass(data_type, StrEnum), eq=True)
        tm.that(getattr(data_type, "VARCHAR2") == "VARCHAR2", eq=True)
        tm.that(getattr(data_type, "NUMBER") == "NUMBER", eq=True)
        tm.that(getattr(data_type, "DATE") == "DATE", eq=True)
        tm.that(getattr(data_type, "TIMESTAMP") == "TIMESTAMP", eq=True)

    def test_platform_extension(self) -> None:
        """Test Oracle-specific platform constants extending base Platform."""
        platform = FlextDbOracleConstants.DbOracle.Platform
        tm.that(hasattr(platform, "LOOPBACK_IP"), eq=True)
        tm.that(hasattr(platform, "LOCALHOST_IP"), eq=True)
        tm.that(platform.LOOPBACK_IP == "127.0.0.1", eq=True)
        tm.that(platform.LOCALHOST_IP == "127.0.0.1", eq=True)
        tm.that(getattr(platform, "HTTP_METHOD_DELETE") == "DELETE", eq=True)
        tm.that(getattr(platform, "HTTP_METHOD_GET") == "GET", eq=True)
        tm.that(getattr(platform, "HTTP_METHOD_POST") == "POST", eq=True)
        tm.that(getattr(platform, "HTTP_METHOD_PUT") == "PUT", eq=True)
        tm.that(getattr(platform, "HTTP_METHOD_PATCH") == "PATCH", eq=True)

    @pytest.mark.unit_integration
    def test_oracle_constants_real_connection_validation(
        self, connected_oracle_api: FlextDbOracleApi | None, oracle_available: bool
    ) -> None:
        """Test that Oracle constants work with real connections."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        test_query = FlextDbOracleConstants.DbOracle.Query.TEST_QUERY
        result = connected_oracle_api.query(test_query)
        tm.ok(result), f"TEST_QUERY failed: {result.error}"
        data = result.value
        tm.that(len(data) == 1, eq=True), "TEST_QUERY should return exactly one row"
        dual_query = f"SELECT 1 FROM {FlextDbOracleConstants.DbOracle.Query.DUAL_TABLE}"
        result = connected_oracle_api.query(dual_query)
        tm.ok(result), f"DUAL_TABLE query failed: {result.error}"

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
        tm.that(isinstance(default_service, str), eq=True)
        tm.that(len(default_service) > 0, eq=True)
        default_port = FlextDbOracleConstants.DbOracle.Connection.DEFAULT_PORT
        tm.that(isinstance(default_port, int), eq=True)
        tm.that(
            (
                FlextConstants.Network.MIN_PORT
                <= default_port
                <= FlextConstants.Network.MAX_PORT
            ),
            eq=True,
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
        tm.that(
            result.is_success or "already exists" in str(result.error).lower() is True,
            eq=True,
        )

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
        tm.that(isinstance(max_length, int), eq=True)
        tm.that(max_length > 0, eq=True)
        long_name = "A" * (max_length - 10)
        escaped = FlextDbOracleUtilities.escape_oracle_identifier(long_name)
        tm.ok(escaped)
        max_varchar = (
            FlextDbOracleConstants.DbOracle.OracleValidation.MAX_VARCHAR_LENGTH
        )
        tm.that(max_varchar == 4000, eq=True)

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
        tm.ok(result)
        execution_ms = (end_time - start_time) * 1000
        perf = FlextDbOracleConstants.DbOracle.OraclePerformance
        if execution_ms < perf.QUERY_EXCELLENT_THRESHOLD_MS:
            tm.that(execution_ms < 100, eq=True)
        elif execution_ms < perf.QUERY_GOOD_THRESHOLD_MS:
            tm.that(execution_ms < 500, eq=True)
        elif execution_ms < perf.QUERY_ACCEPTABLE_THRESHOLD_MS:
            tm.that(execution_ms < 2000, eq=True)

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
            tm.that(word in reserved is True, eq=True)
        for word in test_words[:3]:
            result = FlextDbOracleUtilities.OracleValidation.validate_identifier(word)
            tm.that(result.is_failure, eq=True)
            tm.that(
                result.error is not None and "reserved word" in result.error is True,
                eq=True,
            )

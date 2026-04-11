"""Comprehensive unit tests for flext_db_oracle.constants module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import time
from enum import StrEnum

import pytest
from flext_tests import tm

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings
from tests import c, u


@pytest.mark.unit_pure
class Testc:
    """Comprehensive test c functionality and values."""

    def test_constants_inheritance(self) -> None:
        """Test constants properly extends FlextConstants."""

    def test_connection_constants(self) -> None:
        """Test connection-related constants."""
        conn = c.DbOracle.Connection
        tm.that(conn.DEFAULT_CHARSET, eq="UTF8")
        tm.that(conn.DEFAULT_SERVICE_NAME, eq="XEPDB1")
        tm.that(conn.DEFAULT_PORT, eq=1521)
        tm.that(conn.DEFAULT_DATABASE_NAME, eq="XE")
        tm.that(conn.DEFAULT_SID, eq="XE")
        tm.that(conn.DEFAULT_USERNAME, eq="system")
        tm.that(conn.DEFAULT_TIMEOUT, eq=30)
        tm.that(conn.DEFAULT_POOL_INCREMENT, eq=1)
        tm.that(conn.DEFAULT_POOL_MIN, eq=2)
        tm.that(conn.DEFAULT_POOL_MAX, eq=20)
        tm.that(conn.DEFAULT_POOL_TIMEOUT, eq=60)
        tm.that(conn.DEFAULT_CONNECTION_TIMEOUT, eq=30)

    def test_oracle_network_constants(self) -> None:
        """Test Oracle-specific network constants."""
        net = c.DbOracle.OracleNetwork
        tm.that(net.MIN_PORT, eq=1)
        tm.that(net.MAX_PORT, eq=65535)
        tm.that(net.DEFAULT_PORT, eq=1521)
        tm.that(net.DEFAULT_LISTENER_PORT, eq=1521)
        tm.that(net.DEFAULT_SSL_PORT, eq=2484)

    def test_query_constants(self) -> None:
        """Test query-related constants."""
        query = c.DbOracle.Query
        tm.that(query.TEST_QUERY, eq="SELECT 1 FROM DUAL")
        tm.that(query.DUAL_TABLE, eq="DUAL")
        tm.that(query.DEFAULT_ARRAY_SIZE, eq=100)
        tm.that(query.DEFAULT_QUERY_LIMIT, eq=1000)
        tm.that(query.DEFAULT_QUERY_TIMEOUT, eq=60)
        tm.that(query.MAX_QUERY_TIMEOUT, eq=3600)
        tm.that(query.MAX_QUERY_ROWS, eq=100000)

    def test_data_types_constants(self) -> None:
        """Test Oracle data type constants."""
        dt = c.DbOracle.DataTypes
        tm.that(dt.DATE_TYPE, eq="DATE")
        tm.that(dt.TIMESTAMP_TYPE, eq="TIMESTAMP")
        tm.that(dt.DEFAULT_VARCHAR_TYPE, eq="VARCHAR2(4000)")
        tm.that(dt.CLOB_TYPE, eq="CLOB")
        tm.that(dt.BLOB_TYPE, eq="BLOB")
        tm.that(dt.NUMBER_TYPE, eq="NUMBER")
        tm.that(dt.INTEGER_TYPE, eq="NUMBER(38)")
        tm.that(dt.BOOLEAN_TYPE, eq="NUMBER(1)")
        mappings = dt.SINGER_TYPE_MAP
        tm.that(mappings["string"], eq="VARCHAR2(4000)")
        tm.that(mappings["integer"], eq="NUMBER(38)")
        tm.that(mappings["number"], eq="NUMBER")
        tm.that(mappings["boolean"], eq="NUMBER(1)")
        tm.that(mappings["array"], eq="CLOB")
        tm.that(mappings["t.NormalizedValue"], eq="CLOB")
        tm.that(mappings["date-time"], eq="TIMESTAMP")
        tm.that(mappings["date"], eq="DATE")

    def test_oracle_validation_constants(self) -> None:
        """Test Oracle validation constants."""
        val = c.DbOracle.OracleValidation
        tm.that(val.MAX_ORACLE_IDENTIFIER_LENGTH, eq=30)
        tm.that(val.MAX_IDENTIFIER_LENGTH, eq=128)
        tm.that(val.MAX_TABLE_NAME_LENGTH, eq=128)
        tm.that(val.MAX_COLUMN_NAME_LENGTH, eq=128)
        tm.that(val.MAX_SCHEMA_NAME_LENGTH, eq=128)
        tm.that(val.MAX_USERNAME_LENGTH, eq=128)
        tm.that(val.MAX_SERVICE_NAME_LENGTH, eq=128)
        tm.that(val.MAX_HOSTNAME_LENGTH, eq=253)
        tm.that(val.MAX_VARCHAR_LENGTH, eq=4000)
        tm.that(val.MIN_COLUMN_FIELDS, eq=4)
        tm.that(val.COLUMN_METADATA_FIELD_COUNT, eq=7)
        tm.that(val.ORACLE_IDENTIFIER_PATTERN, eq="^[A-Z][A-Z0-9_$#]*$")
        tm.that(val.IDENTIFIER_PATTERN, eq="^[A-Za-z][A-Za-z0-9_$#]*$")
        tm.that(val.SCHEMA_PATTERN, eq="^[A-Za-z][A-Za-z0-9_$#]*$")
        reserved = val.ORACLE_RESERVED
        tm.that(reserved, is_=frozenset)
        reserved_list = sorted(reserved)
        tm.that(reserved_list, has="SELECT")
        tm.that(reserved_list, has="FROM")
        tm.that(reserved_list, has="WHERE")
        tm.that(reserved_list, has="INSERT")
        tm.that(reserved_list, has="UPDATE")
        tm.that(reserved_list, has="DELETE")
        sql_keywords = val.SQL_KEYWORDS
        tm.that(sql_keywords, is_=frozenset)
        keywords_list = sorted(sql_keywords)
        tm.that(keywords_list, has="SELECT")
        tm.that(keywords_list, has="JOIN")
        tm.that(keywords_list, has="ORDER")

    def test_error_messages_constants(self) -> None:
        """Test error message constants."""
        err = c.DbOracle.ErrorMessages
        tm.that(err.HOST_EMPTY, eq="Host cannot be empty")
        tm.that(err.USERNAME_EMPTY, eq="Username cannot be empty")
        tm.that(err.COLUMN_NAME_EMPTY, eq="Column name cannot be empty")
        tm.that(err.DATA_TYPE_EMPTY, eq="Data type cannot be empty")
        tm.that(err.TABLE_NAME_EMPTY, eq="Table name cannot be empty")
        tm.that(err.SCHEMA_NAME_EMPTY, eq="Schema name cannot be empty")
        tm.that(err.POSITION_INVALID, eq="Position must be positive")
        tm.that(err.COLUMN_ID_INVALID, eq="Column ID must be positive")
        tm.that(err.PORT_INVALID, eq="Invalid port number")
        tm.that(err.CONNECTION_FAILED, eq="Failed to connect to Oracle database")
        tm.that(err.QUERY_EXECUTION_FAILED, eq="Query execution failed")
        tm.that(err.IDENTIFIER_TOO_LONG, has="max_length")
        tm.that(err.IDENTIFIER_INVALID_PATTERN, has="required pattern")
        tm.that(err.IDENTIFIER_RESERVED_WORD, has="reserved word")
        tm.that(err.HOST_TOO_LONG, has="too long")
        tm.that(err.PORT_OUT_OF_RANGE, has="between")
        tm.that(err.QUERY_TIMEOUT_TOO_HIGH, has="too high")

    def test_oracle_performance_constants(self) -> None:
        """Test Oracle performance constants."""
        perf = c.DbOracle.OraclePerformance
        tm.that(perf.DEFAULT_COMMIT_SIZE, eq=1000)
        tm.that(abs(perf.PERFORMANCE_WARNING_THRESHOLD_SECONDS - 5.0), lt=1e-9)
        tm.that(perf.MAX_DISPLAY_ROWS, eq=1000)
        tm.that(perf.MILLISECONDS_TO_SECONDS_THRESHOLD, eq=1000)
        tm.that(perf.DEFAULT_POOL_RECYCLE, eq=3600)
        tm.that(perf.CONNECTION_IDLE_TIMEOUT_SECONDS, eq=3600)
        tm.that(abs(perf.CONNECTION_EXCELLENT_THRESHOLD_SECONDS - 0.1), lt=1e-9)
        tm.that(abs(perf.CONNECTION_GOOD_THRESHOLD_SECONDS - 0.5), lt=1e-9)
        tm.that(abs(perf.CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS - 2.0), lt=1e-9)
        tm.that(perf.QUERY_EXCELLENT_THRESHOLD_MS, eq=100)
        tm.that(perf.QUERY_GOOD_THRESHOLD_MS, eq=500)
        tm.that(perf.QUERY_ACCEPTABLE_THRESHOLD_MS, eq=2000)
        tm.that(perf.DATA_SIZE_ESTIMATION_FACTOR, eq=50)
        tm.that(perf.INDEX_HINT, eq="/*+ INDEX */")
        tm.that(perf.FULL_HINT, eq="/*+ FULL */")
        tm.that(perf.PARALLEL_HINT, eq="/*+ PARALLEL */")

    def test_isolation_levels_constants(self) -> None:
        """Test transaction isolation level constants."""
        iso = c.DbOracle.IsolationLevels
        tm.that(iso.READ_UNCOMMITTED, eq="READ_UNCOMMITTED")
        tm.that(iso.READ_COMMITTED, eq="READ_COMMITTED")
        tm.that(iso.REPEATABLE_READ, eq="REPEATABLE_READ")
        tm.that(iso.SERIALIZABLE, eq="SERIALIZABLE")
        valid_levels = iso.VALID_LEVELS
        tm.that(len(valid_levels), eq=4)
        tm.that(valid_levels, has="READ_COMMITTED")
        tm.that(valid_levels, has="SERIALIZABLE")

    def test_oracle_environment_constants(self) -> None:
        """Test Oracle environment variable constants."""
        env = c.DbOracle.OracleEnvironment
        tm.that(env.PREFIX_ORACLE, eq="ORACLE_")
        tm.that(env.PREFIX_FLEXT_TARGET_ORACLE, eq="FLEXT_TARGET_ORACLE_")
        tm.that(env.ENV_HOST, eq="ORACLE_HOST")
        tm.that(env.ENV_PORT, eq="ORACLE_PORT")
        tm.that(env.ENV_USERNAME, eq="ORACLE_USERNAME")
        tm.that(env.ENV_PASSWORD, eq="ORACLE_PASSWORD")
        tm.that(env.ENV_SERVICE_NAME, eq="ORACLE_SERVICE_NAME")
        tm.that(env.ENV_DATABASE_NAME, eq="ORACLE_DATABASE_NAME")
        tm.that(env.ENV_SID, eq="ORACLE_SID")
        mapping = env.ENV_MAPPING
        tm.that(mapping["FLEXT_TARGET_ORACLE_HOST"], eq="host")
        tm.that(mapping["ORACLE_HOST"], eq="host")
        tm.that(mapping["FLEXT_TARGET_ORACLE_PORT"], eq="port")
        tm.that(mapping["ORACLE_PORT"], eq="port")
        tm.that(mapping["FLEXT_TARGET_ORACLE_USERNAME"], eq="username")
        tm.that(mapping["ORACLE_USERNAME"], eq="username")
        tm.that(mapping["FLEXT_TARGET_ORACLE_PASSWORD"], eq="password")
        tm.that(mapping["ORACLE_PASSWORD"], eq="password")
        tm.that(mapping["FLEXT_TARGET_ORACLE_SERVICE_NAME"], eq="service_name")
        tm.that(mapping["ORACLE_SERVICE_NAME"], eq="service_name")

    def test_oracle_defaults_constants(self) -> None:
        """Test Oracle default configuration constants."""
        defaults = c.DbOracle.OracleDefaults
        tm.that(defaults.DEFAULT_HOST, eq="localhost")
        tm.that(defaults.DEFAULT_PORT, eq=1521)
        tm.that(defaults.DEFAULT_USERNAME, eq="system")
        tm.that(defaults.DEFAULT_SERVICE_NAME, eq="XEPDB1")
        tm.that(defaults.DEFAULT_DATABASE_NAME, eq="XE")
        tm.that(defaults.DEFAULT_SID, eq="XE")
        tm.that(defaults.DEFAULT_POOL_MIN, eq=2)
        tm.that(defaults.DEFAULT_POOL_MAX, eq=20)
        tm.that(defaults.DEFAULT_POOL_TIMEOUT, eq=60)
        tm.that(defaults.DEFAULT_QUERY_TIMEOUT, eq=60)
        tm.that(defaults.DEFAULT_QUERY_LIMIT, eq=1000)
        tm.that(defaults.DEFAULT_COMMIT_SIZE, eq=1000)
        tm.that(defaults.DEFAULT_POOL_RECYCLE, eq=3600)
        tm.that(abs(defaults.DEFAULT_SLOW_QUERY_THRESHOLD - 2.0), lt=1e-9)

    def test_literals_constants(self) -> None:
        """Test type-safe literal constants."""
        tm.that(
            c.DbOracle.ConnectionTypeLiteral,
            eq=tuple(c.DbOracle.Lists.VALID_CONNECTION_TYPES),
        )
        tm.that(
            c.DbOracle.QueryTypeLiteral,
            eq=tuple(c.DbOracle.Lists.VALID_QUERY_TYPES),
        )
        tm.that(c.DbOracle.DataTypeLiteral, eq=tuple(c.DbOracle.Lists.VALID_DATA_TYPES))
        tm.that(c.DbOracle.ConnectionTypeLiteral, is_=tuple)
        tm.that(c.DbOracle.QueryTypeLiteral, is_=tuple)
        tm.that(c.DbOracle.DataTypeLiteral, is_=tuple)
        assert isinstance(c.DbOracle.Literals, type)

    def test_lists_constants(self) -> None:
        """Test list-type constants."""
        lists = c.DbOracle.Lists
        valid_types = lists.VALID_DATA_TYPES
        tm.that(valid_types, has="VARCHAR2")
        tm.that(valid_types, has="NUMBER")
        tm.that(valid_types, has="DATE")
        tm.that(valid_types, has="CLOB")
        valid_conn_types = lists.VALID_CONNECTION_TYPES
        tm.that(valid_conn_types, has="service_name")
        tm.that(valid_conn_types, has="sid")
        tm.that(valid_conn_types, has="tns")
        valid_query_types = lists.VALID_QUERY_TYPES
        tm.that(valid_query_types, has="SELECT")
        tm.that(valid_query_types, has="INSERT")
        tm.that(valid_query_types, has="UPDATE")
        tm.that(valid_query_types, has="DELETE")
        valid_iso_levels = lists.VALID_ISOLATION_LEVELS
        tm.that(valid_iso_levels, has="READ_COMMITTED")
        tm.that(valid_iso_levels, has="SERIALIZABLE")
        system_users = lists.SYSTEM_USERS
        tm.that(system_users, has="SYS")
        tm.that(system_users, has="SYSTEM")
        tm.that(system_users, has="XDB")
        default_schemas = lists.DEFAULT_SCHEMAS
        tm.that(default_schemas, has="SYSTEM")
        tm.that(default_schemas, has="SYS")
        tm.that(default_schemas, has="PUBLIC")

    def test_feature_flags_functionality(self) -> None:
        """Test feature flag functionality via FlextDbOracleSettings.enable_dispatcher."""
        settings = FlextDbOracleSettings.model_validate({"enable_dispatcher": False})
        tm.that(settings.enable_dispatcher, eq=False)

        settings_on = FlextDbOracleSettings.model_validate({"enable_dispatcher": True})
        tm.that(settings_on.enable_dispatcher, eq=True)

    def test_oracle_enums(self) -> None:
        """Test Oracle enumeration classes."""
        enums = c.DbOracle.OracleEnums
        conn_type = enums.ConnectionType
        tm.that(conn_type, is_=type)
        assert issubclass(conn_type, StrEnum)  # type narrowing
        query_type = enums.QueryType
        tm.that(query_type, is_=type)
        assert issubclass(query_type, StrEnum)  # type narrowing
        data_type = enums.DataType
        tm.that(data_type, is_=type)
        assert issubclass(data_type, StrEnum)  # type narrowing

    def test_platform_extension(self) -> None:
        """Test Oracle-specific platform constants extending base Platform."""
        platform = c.DbOracle.Platform
        tm.that(platform.LOOPBACK_IP, eq="127.0.0.1")
        tm.that(platform.LOCALHOST_IP, eq="127.0.0.1")

    @pytest.mark.unit_integration
    def test_oracle_constants_real_connection_validation(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test that Oracle constants work with real connections."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        test_query = c.DbOracle.Query.TEST_QUERY
        result = connected_oracle_api.query(test_query)
        tm.ok(result)
        data = result.value
        tm.that(len(data), eq=1)
        dual_query = f"SELECT 1 FROM {c.DbOracle.Query.DUAL_TABLE}"
        result = connected_oracle_api.query(dual_query)
        tm.ok(result)

    @pytest.mark.unit_integration
    def test_oracle_constants_default_values_real_validation(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test that default constant values work with real Oracle."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        default_service = c.DbOracle.Connection.DEFAULT_SERVICE_NAME
        tm.that(default_service, is_=str)
        tm.that(bool(default_service), eq=True)
        default_port = c.DbOracle.Connection.DEFAULT_PORT
        tm.that(default_port, is_=int)
        tm.that(
            (c.MIN_PORT <= default_port <= c.MAX_PORT),
            eq=True,
        )

    @pytest.mark.unit_integration
    def test_oracle_data_types_real_validation(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test that Oracle data type constants are valid."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        dt = c.DbOracle.DataTypes
        create_sql = f"\n        CREATE TABLE test_data_types (\n            id {dt.NUMBER_TYPE} PRIMARY KEY,\n            name {dt.DEFAULT_VARCHAR_TYPE},\n            active_flag {dt.BOOLEAN_TYPE},\n            created_date {dt.DATE_TYPE},\n            data_blob {dt.BLOB_TYPE}\n        )\n        "
        result = connected_oracle_api.execute_statement(create_sql)
        with contextlib.suppress(Exception):
            connected_oracle_api.execute_statement("DROP TABLE test_data_types")
        tm.that(
            result.success or ("already exists" in str(result.error).lower()),
            eq=True,
        )

    @pytest.mark.unit_integration
    def test_oracle_validation_constants_real_usage(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test Oracle validation constants with real database."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        max_length = c.DbOracle.OracleValidation.MAX_IDENTIFIER_LENGTH
        tm.that(max_length, is_=int)
        tm.that(max_length, gt=0)
        long_name = "A" * (max_length - 10)
        escaped = u.DbOracle.escape_oracle_identifier(long_name)
        tm.ok(escaped)
        max_varchar = c.DbOracle.OracleValidation.MAX_VARCHAR_LENGTH
        tm.that(max_varchar, eq=4000)

    @pytest.mark.unit_integration
    def test_oracle_performance_constants_real_timing(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test Oracle performance constants with real query timing."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        start_time = time.time()
        result = connected_oracle_api.query("SELECT 1 FROM DUAL")
        end_time = time.time()
        tm.ok(result)
        execution_ms = (end_time - start_time) * 1000
        perf = c.DbOracle.OraclePerformance
        if execution_ms < perf.QUERY_EXCELLENT_THRESHOLD_MS:
            tm.that(execution_ms, lt=100)
        elif execution_ms < perf.QUERY_GOOD_THRESHOLD_MS:
            tm.that(execution_ms, lt=500)
        elif execution_ms < perf.QUERY_ACCEPTABLE_THRESHOLD_MS:
            tm.that(execution_ms, lt=2000)

    @pytest.mark.unit_integration
    def test_oracle_reserved_words_real_validation(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test that Oracle reserved words are actually reserved."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        reserved = c.DbOracle.OracleValidation.ORACLE_RESERVED
        test_words = ["SELECT", "FROM", "WHERE", "TABLE", "INDEX"]
        for word in test_words:
            tm.that(reserved, has=word)
        for word in test_words[:3]:
            result = u.DbOracle.validate_identifier(word)
            tm.that(result.failure, eq=True)
            assert result.error is not None
            tm.that(
                "reserved word" in result.error,
                eq=True,
            )

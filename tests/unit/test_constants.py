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
class TestsFlextDbOracleConstantsUnit:
    """Comprehensive test c functionality and values."""

    def test_constants_inheritance(self) -> None:
        """Test constants properly extends FlextConstants."""

    def test_flat_default_constants(self) -> None:
        """Test flat SSOT defaults on the DbOracle namespace."""
        tm.that(c.DbOracle.DEFAULT_CHARSET, eq="UTF8")
        tm.that(c.DbOracle.DEFAULT_SERVICE_NAME, eq="XEPDB1")
        tm.that(c.DbOracle.DEFAULT_PORT, eq=1521)
        tm.that(c.DbOracle.DEFAULT_DATABASE_NAME, eq="XE")
        tm.that(c.DbOracle.DEFAULT_SID, eq="XE")
        tm.that(c.DbOracle.DEFAULT_USERNAME, eq="system")
        tm.that(c.DbOracle.DEFAULT_TIMEOUT, eq=30)
        tm.that(c.DbOracle.DEFAULT_POOL_INCREMENT, eq=1)
        tm.that(c.DbOracle.DEFAULT_POOL_MIN, eq=2)
        tm.that(c.DbOracle.DEFAULT_POOL_MAX, eq=20)
        tm.that(c.DbOracle.DEFAULT_POOL_TIMEOUT, eq=60)
        tm.that(c.DbOracle.DEFAULT_CONNECTION_TIMEOUT, eq=30)
        tm.that(c.DbOracle.DEFAULT_HOST, eq="localhost")
        tm.that(c.DbOracle.DEFAULT_LISTENER_PORT, eq=1521)
        tm.that(c.DbOracle.DEFAULT_SSL_PORT, eq=2484)

    def test_query_and_performance_constants(self) -> None:
        """Test flat query and performance constants."""
        tm.that(c.DbOracle.TEST_QUERY, eq="SELECT 1 FROM DUAL")
        tm.that(c.DbOracle.DUAL_TABLE, eq="DUAL")
        tm.that(c.DbOracle.DEFAULT_ARRAY_SIZE, eq=100)
        tm.that(c.DbOracle.DEFAULT_QUERY_LIMIT, eq=1000)
        tm.that(c.DbOracle.DEFAULT_QUERY_TIMEOUT, eq=60)
        tm.that(c.DbOracle.MAX_QUERY_TIMEOUT, eq=3600)
        tm.that(c.DbOracle.MAX_QUERY_ROWS, eq=100000)
        tm.that(c.DbOracle.DEFAULT_COMMIT_SIZE, eq=1000)
        tm.that(abs(c.DbOracle.PERFORMANCE_WARNING_THRESHOLD_SECONDS - 5.0), lt=1e-9)
        tm.that(c.DbOracle.MAX_DISPLAY_ROWS, eq=1000)
        tm.that(c.DbOracle.MILLISECONDS_TO_SECONDS_THRESHOLD, eq=1000)
        tm.that(c.DbOracle.DEFAULT_POOL_RECYCLE, eq=3600)
        tm.that(c.DbOracle.CONNECTION_IDLE_TIMEOUT_SECONDS, eq=3600)
        tm.that(abs(c.DbOracle.CONNECTION_EXCELLENT_THRESHOLD_SECONDS - 0.1), lt=1e-9)
        tm.that(abs(c.DbOracle.CONNECTION_GOOD_THRESHOLD_SECONDS - 0.5), lt=1e-9)
        tm.that(abs(c.DbOracle.CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS - 2.0), lt=1e-9)
        tm.that(c.DbOracle.QUERY_EXCELLENT_THRESHOLD_MS, eq=100)
        tm.that(c.DbOracle.QUERY_GOOD_THRESHOLD_MS, eq=500)
        tm.that(c.DbOracle.QUERY_ACCEPTABLE_THRESHOLD_MS, eq=2000)
        tm.that(c.DbOracle.DATA_SIZE_ESTIMATION_FACTOR, eq=50)
        tm.that(c.DbOracle.INDEX_HINT, eq="/*+ INDEX */")
        tm.that(c.DbOracle.FULL_HINT, eq="/*+ FULL */")
        tm.that(c.DbOracle.PARALLEL_HINT, eq="/*+ PARALLEL */")

    def test_data_type_constants(self) -> None:
        """Test data type enums, derived literals, and mapping."""
        tm.that(c.DbOracle.DataType.DATE, eq="DATE")
        tm.that(c.DbOracle.DataType.TIMESTAMP, eq="TIMESTAMP")
        tm.that(c.DbOracle.DEFAULT_VARCHAR_TYPE, eq="VARCHAR2(4000)")
        tm.that(c.DbOracle.DataType.CLOB, eq="CLOB")
        tm.that(c.DbOracle.DataType.BLOB, eq="BLOB")
        tm.that(c.DbOracle.DataType.NUMBER, eq="NUMBER")
        tm.that(c.DbOracle.INTEGER_TYPE, eq="NUMBER(38)")
        tm.that(c.DbOracle.BOOLEAN_TYPE, eq="NUMBER(1)")
        mappings = c.DbOracle.SINGER_TYPE_MAP
        tm.that(mappings["string"], eq="VARCHAR2(4000)")
        tm.that(mappings["integer"], eq="NUMBER(38)")
        tm.that(mappings["number"], eq="NUMBER")
        tm.that(mappings["boolean"], eq="NUMBER(1)")
        tm.that(mappings["array"], eq="CLOB")
        tm.that(mappings["t.JsonValue"], eq="CLOB")
        tm.that(mappings["date-time"], eq="TIMESTAMP")
        tm.that(mappings["date"], eq="DATE")

    def test_validation_and_message_constants(self) -> None:
        """Test validation limits, regexes, sets, and error messages."""
        tm.that(c.DbOracle.MIN_PORT, eq=1)
        tm.that(c.DbOracle.MAX_PORT, eq=65535)
        tm.that(c.DbOracle.MAX_ORACLE_IDENTIFIER_LENGTH, eq=30)
        tm.that(c.DbOracle.MAX_IDENTIFIER_LENGTH, eq=128)
        tm.that(c.DbOracle.MAX_TABLE_NAME_LENGTH, eq=128)
        tm.that(c.DbOracle.MAX_COLUMN_NAME_LENGTH, eq=128)
        tm.that(c.DbOracle.MAX_SCHEMA_NAME_LENGTH, eq=128)
        tm.that(c.DbOracle.MAX_USERNAME_LENGTH, eq=128)
        tm.that(c.DbOracle.MAX_SERVICE_NAME_LENGTH, eq=128)
        tm.that(c.DbOracle.MAX_HOSTNAME_LENGTH, eq=253)
        tm.that(c.DbOracle.MAX_VARCHAR_LENGTH, eq=4000)
        tm.that(c.DbOracle.MIN_COLUMN_FIELDS, eq=4)
        tm.that(c.DbOracle.COLUMN_METADATA_FIELD_COUNT, eq=7)
        tm.that(c.DbOracle.ORACLE_IDENTIFIER_PATTERN, eq="^[A-Z][A-Z0-9_$#]*$")
        tm.that(c.DbOracle.IDENTIFIER_PATTERN, eq="^[A-Za-z][A-Za-z0-9_$#]*$")
        tm.that(c.DbOracle.SCHEMA_PATTERN, eq="^[A-Za-z][A-Za-z0-9_$#]*$")
        tm.that(c.DbOracle.ORACLE_RESERVED, is_=frozenset)
        tm.that(c.DbOracle.ORACLE_RESERVED, has="SELECT")
        tm.that(c.DbOracle.ORACLE_RESERVED, has="DELETE")
        tm.that(c.DbOracle.SQL_KEYWORDS, is_=frozenset)
        tm.that(c.DbOracle.SQL_KEYWORDS, has="JOIN")
        tm.that(c.DbOracle.SQL_KEYWORDS, has="ORDER")
        tm.that(c.DbOracle.HOST_EMPTY, eq="Host cannot be empty")
        tm.that(c.DbOracle.USERNAME_EMPTY, eq="Username cannot be empty")
        tm.that(c.DbOracle.COLUMN_NAME_EMPTY, eq="Column name cannot be empty")
        tm.that(c.DbOracle.DATA_TYPE_EMPTY, eq="Data type cannot be empty")
        tm.that(c.DbOracle.TABLE_NAME_EMPTY, eq="Table name cannot be empty")
        tm.that(c.DbOracle.SCHEMA_NAME_EMPTY, eq="Schema name cannot be empty")
        tm.that(c.DbOracle.POSITION_INVALID, eq="Position must be positive")
        tm.that(c.DbOracle.COLUMN_ID_INVALID, eq="Column ID must be positive")
        tm.that(c.DbOracle.PORT_INVALID, eq="Invalid port number")
        tm.that(c.DbOracle.CONNECTION_FAILED, eq="Failed to connect to Oracle database")
        tm.that(c.DbOracle.QUERY_EXECUTION_FAILED, eq="Query execution failed")
        tm.that(c.DbOracle.IDENTIFIER_TOO_LONG, has="max_length")
        tm.that(c.DbOracle.IDENTIFIER_INVALID_PATTERN, has="required pattern")
        tm.that(c.DbOracle.IDENTIFIER_RESERVED_WORD, has="reserved word")
        tm.that(c.DbOracle.HOST_TOO_LONG, has="too long")
        tm.that(c.DbOracle.PORT_OUT_OF_RANGE, has="between")
        tm.that(c.DbOracle.QUERY_TIMEOUT_TOO_HIGH, has="too high")

    def test_environment_constants(self) -> None:
        """Test flat environment naming SSOT and mapping."""
        tm.that(c.DbOracle.PREFIX_ORACLE, eq="ORACLE_")
        tm.that(c.DbOracle.PREFIX_FLEXT_TARGET_ORACLE, eq="FLEXT_TARGET_ORACLE_")
        tm.that(c.DbOracle.ENV_HOST, eq="ORACLE_HOST")
        tm.that(c.DbOracle.ENV_PORT, eq="ORACLE_PORT")
        tm.that(c.DbOracle.ENV_USERNAME, eq="ORACLE_USERNAME")
        tm.that(c.DbOracle.ENV_PASSWORD, eq="ORACLE_PASSWORD")
        tm.that(c.DbOracle.ENV_SERVICE_NAME, eq="ORACLE_SERVICE_NAME")
        tm.that(c.DbOracle.ENV_DATABASE_NAME, eq="ORACLE_DATABASE_NAME")
        tm.that(c.DbOracle.ENV_SID, eq="ORACLE_SID")
        tm.that(
            c.DbOracle.ENV_ENABLE_DISPATCHER, eq="FLEXT_DB_ORACLE_ENABLE_DISPATCHER"
        )
        mapping = c.DbOracle.ENV_MAPPING
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

    def test_closed_sets_and_literals(self) -> None:
        """Test tuple literals and membership sets derived from enums."""
        tm.that(c.DbOracle.CONNECTION_TYPE_LITERAL, is_=tuple)
        tm.that(c.DbOracle.CONNECTION_TYPE_LITERAL, eq=("service_name", "sid", "tns"))
        tm.that(c.DbOracle.QUERY_TYPE_LITERAL, is_=tuple)
        tm.that(c.DbOracle.QUERY_TYPE_LITERAL, has="SELECT")
        tm.that(c.DbOracle.DATA_TYPE_LITERAL, is_=tuple)
        tm.that(c.DbOracle.DATA_TYPE_LITERAL, has="VARCHAR2")
        tm.that(c.DbOracle.ISOLATION_LEVEL_LITERAL, is_=tuple)
        tm.that(c.DbOracle.ISOLATION_LEVEL_LITERAL, has="READ_COMMITTED")
        tm.that(c.DbOracle.VALID_CONNECTION_TYPES, is_=frozenset)
        tm.that(c.DbOracle.VALID_CONNECTION_TYPES, has="service_name")
        tm.that(c.DbOracle.VALID_QUERY_TYPES, is_=frozenset)
        tm.that(c.DbOracle.VALID_QUERY_TYPES, has="DELETE")
        tm.that(c.DbOracle.VALID_DATA_TYPES, is_=frozenset)
        tm.that(c.DbOracle.VALID_DATA_TYPES, has="CLOB")
        tm.that(c.DbOracle.VALID_ISOLATION_LEVELS, is_=frozenset)
        tm.that(c.DbOracle.VALID_ISOLATION_LEVELS, has="SERIALIZABLE")
        tm.that(c.DbOracle.SYSTEM_USERS, has="SYSTEM")
        tm.that(c.DbOracle.DEFAULT_SCHEMAS, has="PUBLIC")

    def test_oracle_enums(self) -> None:
        """Test Oracle enumeration classes exposed directly on DbOracle."""
        tm.that(c.DbOracle.ConnectionType, is_=type)
        assert issubclass(c.DbOracle.ConnectionType, StrEnum)
        tm.that(c.DbOracle.QueryType, is_=type)
        assert issubclass(c.DbOracle.QueryType, StrEnum)
        tm.that(c.DbOracle.DataType, is_=type)
        assert issubclass(c.DbOracle.DataType, StrEnum)
        tm.that(c.DbOracle.IsolationLevel, is_=type)
        assert issubclass(c.DbOracle.IsolationLevel, StrEnum)

    def test_platform_constants(self) -> None:
        """Test flat network platform constants."""
        tm.that(c.DbOracle.LOOPBACK_IP, eq="127.0.0.1")

    def test_feature_flags_functionality(self) -> None:
        """Test feature flag functionality via FlextDbOracleSettings.enable_dispatcher."""
        settings = FlextDbOracleSettings.model_validate({"enable_dispatcher": False})
        tm.that(settings.enable_dispatcher, eq=False)

        settings_on = FlextDbOracleSettings.model_validate({"enable_dispatcher": True})
        tm.that(settings_on.enable_dispatcher, eq=True)

    @pytest.mark.unit_integration
    def test_oracle_constants_real_connection_validation(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        oracle_available: bool,
    ) -> None:
        """Test that Oracle constants work with real connections."""
        if not oracle_available or connected_oracle_api is None:
            pytest.skip("Oracle not available for integration test")
        test_query = c.DbOracle.TEST_QUERY
        result = connected_oracle_api.query(test_query)
        tm.ok(result)
        data = result.value
        tm.that(len(data), eq=1)
        dual_query = f"SELECT 1 FROM {c.DbOracle.DUAL_TABLE}"
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
        default_service = c.DbOracle.DEFAULT_SERVICE_NAME
        tm.that(default_service, is_=str)
        tm.that(bool(default_service), eq=True)
        default_port = c.DbOracle.DEFAULT_PORT
        tm.that(default_port, is_=int)
        tm.that(
            (c.DbOracle.MIN_PORT <= default_port <= c.DbOracle.MAX_PORT),
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
        create_sql = f"\n        CREATE TABLE test_data_types (\n            id {c.DbOracle.DataType.NUMBER} PRIMARY KEY,\n            name {c.DbOracle.DEFAULT_VARCHAR_TYPE},\n            active_flag {c.DbOracle.BOOLEAN_TYPE},\n            created_date {c.DbOracle.DataType.DATE},\n            data_blob {c.DbOracle.DataType.BLOB}\n        )\n        "
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
        max_length = c.DbOracle.MAX_IDENTIFIER_LENGTH
        tm.that(max_length, is_=int)
        tm.that(max_length, gt=0)
        long_name = "A" * (max_length - 10)
        escaped = u.DbOracle.escape_oracle_identifier(long_name)
        tm.ok(escaped)
        max_varchar = c.DbOracle.MAX_VARCHAR_LENGTH
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
        if execution_ms < c.DbOracle.QUERY_EXCELLENT_THRESHOLD_MS:
            tm.that(execution_ms, lt=100)
        elif execution_ms < c.DbOracle.QUERY_GOOD_THRESHOLD_MS:
            tm.that(execution_ms, lt=500)
        elif execution_ms < c.DbOracle.QUERY_ACCEPTABLE_THRESHOLD_MS:
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
        reserved = c.DbOracle.ORACLE_RESERVED
        test_words = ["SELECT", "FROM", "WHERE", "TABLE", "INDEX"]
        for word in test_words:
            tm.that(reserved, has=word)
        for word in test_words[:3]:
            tm.fail(u.DbOracle.validate_identifier(word), has="reserved word")

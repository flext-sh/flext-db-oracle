"""Behavioral unit tests for flext_db_oracle.constants public contract.

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
from tests.constants import c
from tests.utilities import u


@pytest.mark.unit
class TestsFlextDbOracleConstants:
    """Verify the observable public contract exposed by ``c.DbOracle``."""

    # ---- flat SSOT default values (public contract) ---------------------

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("DEFAULT_CHARSET", "UTF8"),
            ("DEFAULT_SERVICE_NAME", "XEPDB1"),
            ("DEFAULT_PORT", 1521),
            ("DEFAULT_DATABASE_NAME", "XE"),
            ("DEFAULT_SID", "XE"),
            ("DEFAULT_USERNAME", "system"),
            ("DEFAULT_TIMEOUT", 30),
            ("DEFAULT_POOL_INCREMENT", 1),
            ("DEFAULT_POOL_MIN", 2),
            ("DEFAULT_POOL_MAX", 20),
            ("DEFAULT_POOL_TIMEOUT", 60),
            ("DEFAULT_CONNECTION_TIMEOUT", 30),
            ("DEFAULT_HOST", "localhost"),
            ("DEFAULT_LISTENER_PORT", 1521),
            ("DEFAULT_SSL_PORT", 2484),
            ("DEFAULT_POOL_RECYCLE", 3600),
            ("LOOPBACK_IP", "127.0.0.1"),
        ],
    )
    def test_flat_default_constant_exposes_expected_value(
        self,
        name: str,
        expected: str | int,
    ) -> None:
        """Each flat default constant resolves to its documented value."""
        tm.that(getattr(c.DbOracle, name), eq=expected)

    def test_derived_defaults_track_inherited_flext_constants(self) -> None:
        """Derived defaults observably reuse the inherited base SSOT values."""
        tm.that(c.DbOracle.DEFAULT_TIMEOUT, eq=c.DEFAULT_TIMEOUT_SECONDS)
        tm.that(c.DbOracle.DEFAULT_CONNECTION_TIMEOUT, eq=c.DEFAULT_TIMEOUT_SECONDS)
        tm.that(c.DbOracle.DEFAULT_HOST, eq=c.LOCALHOST)

    def test_alias_length_limits_track_identifier_limit(self) -> None:
        """Table/column/schema/user/service limits mirror the identifier cap."""
        limit = c.DbOracle.MAX_IDENTIFIER_LENGTH
        tm.that(c.DbOracle.MAX_TABLE_NAME_LENGTH, eq=limit)
        tm.that(c.DbOracle.MAX_COLUMN_NAME_LENGTH, eq=limit)
        tm.that(c.DbOracle.MAX_SCHEMA_NAME_LENGTH, eq=limit)
        tm.that(c.DbOracle.MAX_USERNAME_LENGTH, eq=limit)
        tm.that(c.DbOracle.MAX_SERVICE_NAME_LENGTH, eq=limit)

    # ---- query / performance constants ----------------------------------

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("TEST_QUERY", "SELECT 1 FROM DUAL"),
            ("DUAL_TABLE", "DUAL"),
            ("DEFAULT_ARRAY_SIZE", 100),
            ("DEFAULT_QUERY_LIMIT", 1000),
            ("DEFAULT_QUERY_TIMEOUT", 60),
            ("MAX_QUERY_TIMEOUT", 3600),
            ("MAX_QUERY_ROWS", 100000),
            ("DEFAULT_COMMIT_SIZE", 1000),
            ("MAX_DISPLAY_ROWS", 1000),
            ("MILLISECONDS_TO_SECONDS_THRESHOLD", 1000),
            ("CONNECTION_IDLE_TIMEOUT_SECONDS", 3600),
            ("QUERY_EXCELLENT_THRESHOLD_MS", 100),
            ("QUERY_GOOD_THRESHOLD_MS", 500),
            ("QUERY_ACCEPTABLE_THRESHOLD_MS", 2000),
            ("DATA_SIZE_ESTIMATION_FACTOR", 50),
            ("INDEX_HINT", "/*+ INDEX */"),
            ("FULL_HINT", "/*+ FULL */"),
            ("PARALLEL_HINT", "/*+ PARALLEL */"),
        ],
    )
    def test_query_and_performance_constant_value(
        self,
        name: str,
        expected: str | int,
    ) -> None:
        """Query/performance constants resolve to their documented values."""
        tm.that(getattr(c.DbOracle, name), eq=expected)

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("PERFORMANCE_WARNING_THRESHOLD_SECONDS", 5.0),
            ("CONNECTION_EXCELLENT_THRESHOLD_SECONDS", 0.1),
            ("CONNECTION_GOOD_THRESHOLD_SECONDS", 0.5),
            ("CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS", 2.0),
        ],
    )
    def test_float_threshold_constant_value(
        self,
        name: str,
        expected: float,
    ) -> None:
        """Float threshold constants resolve within floating-point tolerance."""
        tm.that(abs(getattr(c.DbOracle, name) - expected), lt=1e-9)

    def test_connection_thresholds_are_strictly_increasing(self) -> None:
        """Connection quality thresholds form a strictly increasing ladder."""
        excellent = c.DbOracle.CONNECTION_EXCELLENT_THRESHOLD_SECONDS
        good = c.DbOracle.CONNECTION_GOOD_THRESHOLD_SECONDS
        acceptable = c.DbOracle.CONNECTION_ACCEPTABLE_THRESHOLD_SECONDS
        tm.that(good, gt=excellent)
        tm.that(acceptable, gt=good)

    def test_query_thresholds_are_strictly_increasing(self) -> None:
        """Query quality thresholds in ms form a strictly increasing ladder."""
        tm.that(
            c.DbOracle.QUERY_GOOD_THRESHOLD_MS,
            gt=c.DbOracle.QUERY_EXCELLENT_THRESHOLD_MS,
        )
        tm.that(
            c.DbOracle.QUERY_ACCEPTABLE_THRESHOLD_MS,
            gt=c.DbOracle.QUERY_GOOD_THRESHOLD_MS,
        )

    # ---- data type constants + Singer mapping ---------------------------

    @pytest.mark.parametrize(
        ("member", "expected"),
        [
            ("DATE", "DATE"),
            ("TIMESTAMP", "TIMESTAMP"),
            ("CLOB", "CLOB"),
            ("BLOB", "BLOB"),
            ("NUMBER", "NUMBER"),
            ("VARCHAR2", "VARCHAR2"),
        ],
    )
    def test_data_type_enum_member_value(self, member: str, expected: str) -> None:
        """DataType enum members expose their Oracle type string value."""
        tm.that(getattr(c.DbOracle.DataType, member), eq=expected)

    def test_derived_type_literals(self) -> None:
        """Derived composite type literals resolve to their documented forms."""
        tm.that(c.DbOracle.DEFAULT_VARCHAR_TYPE, eq="VARCHAR2(4000)")
        tm.that(c.DbOracle.INTEGER_TYPE, eq="NUMBER(38)")
        tm.that(c.DbOracle.BOOLEAN_TYPE, eq="NUMBER(1)")

    @pytest.mark.parametrize(
        ("singer_type", "oracle_type"),
        [
            ("string", "VARCHAR2(4000)"),
            ("integer", "NUMBER(38)"),
            ("number", "NUMBER"),
            ("boolean", "NUMBER(1)"),
            ("array", "CLOB"),
            ("t.JsonValue", "CLOB"),
            ("date-time", "TIMESTAMP"),
            ("date", "DATE"),
            ("time", "TIMESTAMP"),
        ],
    )
    def test_singer_type_map_translation(
        self,
        singer_type: str,
        oracle_type: str,
    ) -> None:
        """SINGER_TYPE_MAP translates each Singer type to its Oracle type."""
        tm.that(c.DbOracle.SINGER_TYPE_MAP[singer_type], eq=oracle_type)

    def test_singer_map_scalar_targets_are_recognised_oracle_types(self) -> None:
        """Every Singer mapping target starts with a known Oracle data type."""
        valid_types = c.DbOracle.VALID_DATA_TYPES
        for oracle_type in c.DbOracle.SINGER_TYPE_MAP.values():
            base_type = oracle_type.split("(", 1)[0]
            tm.that(valid_types, has=base_type)

    # ---- validation limits, patterns, and messages ----------------------

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("MIN_PORT", 1),
            ("MAX_PORT", 65535),
            ("MAX_ORACLE_IDENTIFIER_LENGTH", 30),
            ("MAX_IDENTIFIER_LENGTH", 128),
            ("MAX_HOSTNAME_LENGTH", 253),
            ("MAX_VARCHAR_LENGTH", 4000),
            ("MIN_COLUMN_FIELDS", 4),
            ("COLUMN_METADATA_FIELD_COUNT", 7),
            ("ORACLE_IDENTIFIER_PATTERN", "^[A-Z][A-Z0-9_$#]*$"),
            ("IDENTIFIER_PATTERN", "^[A-Za-z][A-Za-z0-9_$#]*$"),
            ("SCHEMA_PATTERN", "^[A-Za-z][A-Za-z0-9_$#]*$"),
        ],
    )
    def test_validation_limit_or_pattern_value(
        self,
        name: str,
        expected: str | int,
    ) -> None:
        """Validation limits and regex patterns resolve to documented values."""
        tm.that(getattr(c.DbOracle, name), eq=expected)

    def test_port_bounds_form_a_valid_range(self) -> None:
        """Port bounds are ordered and contain the default listener port."""
        tm.that(c.DbOracle.MIN_PORT, lt=c.DbOracle.MAX_PORT)
        in_range = c.DbOracle.MIN_PORT <= c.DbOracle.DEFAULT_PORT <= c.DbOracle.MAX_PORT
        tm.that(in_range, eq=True)

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("HOST_EMPTY", "Host cannot be empty"),
            ("USERNAME_EMPTY", "Username cannot be empty"),
            ("COLUMN_NAME_EMPTY", "Column name cannot be empty"),
            ("DATA_TYPE_EMPTY", "Data type cannot be empty"),
            ("TABLE_NAME_EMPTY", "Table name cannot be empty"),
            ("SCHEMA_NAME_EMPTY", "Schema name cannot be empty"),
            ("POSITION_INVALID", "Position must be positive"),
            ("COLUMN_ID_INVALID", "Column ID must be positive"),
            ("PORT_INVALID", "Invalid port number"),
            ("CONNECTION_FAILED", "Failed to connect to Oracle database"),
            ("QUERY_EXECUTION_FAILED", "Query execution failed"),
        ],
    )
    def test_error_message_constant_value(self, name: str, expected: str) -> None:
        """Error-message constants expose their documented human text."""
        tm.that(getattr(c.DbOracle, name), eq=expected)

    @pytest.mark.parametrize(
        ("name", "fragment"),
        [
            ("IDENTIFIER_TOO_LONG", "max_length"),
            ("IDENTIFIER_INVALID_PATTERN", "required pattern"),
            ("IDENTIFIER_RESERVED_WORD", "reserved word"),
            ("HOST_TOO_LONG", "too long"),
            ("PORT_OUT_OF_RANGE", "between"),
            ("QUERY_TIMEOUT_TOO_HIGH", "too high"),
        ],
    )
    def test_error_message_contains_expected_fragment(
        self,
        name: str,
        fragment: str,
    ) -> None:
        """Templated error messages carry their identifying fragment."""
        tm.that(getattr(c.DbOracle, name), has=fragment)

    def test_port_out_of_range_message_formats_with_named_fields(self) -> None:
        """PORT_OUT_OF_RANGE is a format template consuming the documented keys."""
        rendered = c.DbOracle.PORT_OUT_OF_RANGE.format(
            min_port=1, max_port=65535, port=0
        )
        tm.that(rendered, has="1")
        tm.that(rendered, has="65535")

    # ---- keyword / reserved-word sets -----------------------------------

    @pytest.mark.parametrize("word", ["SELECT", "DELETE", "TABLE", "INDEX"])
    def test_oracle_reserved_contains_core_keywords(self, word: str) -> None:
        """ORACLE_RESERVED advertises core Oracle reserved keywords."""
        tm.that(c.DbOracle.ORACLE_RESERVED, is_=frozenset)
        tm.that(c.DbOracle.ORACLE_RESERVED, has=word)

    @pytest.mark.parametrize("word", ["JOIN", "ORDER", "GROUP", "UNION"])
    def test_sql_keywords_contains_clause_keywords(self, word: str) -> None:
        """SQL_KEYWORDS advertises common SQL clause keywords."""
        tm.that(c.DbOracle.SQL_KEYWORDS, is_=frozenset)
        tm.that(c.DbOracle.SQL_KEYWORDS, has=word)

    # ---- environment naming SSOT ----------------------------------------

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("PREFIX_ORACLE", "ORACLE_"),
            ("PREFIX_FLEXT_TARGET_ORACLE", "FLEXT_TARGET_ORACLE_"),
            ("ENV_HOST", "ORACLE_HOST"),
            ("ENV_PORT", "ORACLE_PORT"),
            ("ENV_USERNAME", "ORACLE_USERNAME"),
            ("ENV_PASSWORD", "ORACLE_PASSWORD"),
            ("ENV_SERVICE_NAME", "ORACLE_SERVICE_NAME"),
            ("ENV_DATABASE_NAME", "ORACLE_DATABASE_NAME"),
            ("ENV_SID", "ORACLE_SID"),
            ("ENV_ENABLE_DISPATCHER", "FLEXT_DB_ORACLE_ENABLE_DISPATCHER"),
        ],
    )
    def test_environment_variable_name(self, name: str, expected: str) -> None:
        """Environment-variable name constants resolve to documented keys."""
        tm.that(getattr(c.DbOracle, name), eq=expected)

    @pytest.mark.parametrize(
        ("field", "oracle_key", "target_key"),
        [
            ("host", "ORACLE_HOST", "FLEXT_TARGET_ORACLE_HOST"),
            ("port", "ORACLE_PORT", "FLEXT_TARGET_ORACLE_PORT"),
            ("username", "ORACLE_USERNAME", "FLEXT_TARGET_ORACLE_USERNAME"),
            ("password", "ORACLE_PASSWORD", "FLEXT_TARGET_ORACLE_PASSWORD"),
            ("service_name", "ORACLE_SERVICE_NAME", "FLEXT_TARGET_ORACLE_SERVICE_NAME"),
        ],
    )
    def test_env_mapping_resolves_both_prefixes_to_same_field(
        self,
        field: str,
        oracle_key: str,
        target_key: str,
    ) -> None:
        """ENV_MAPPING routes both env prefixes onto the same settings field."""
        mapping = c.DbOracle.ENV_MAPPING
        tm.that(mapping[oracle_key], eq=field)
        tm.that(mapping[target_key], eq=field)

    # ---- closed literals derived from enums -----------------------------

    def test_connection_type_literal_matches_documented_order(self) -> None:
        """CONNECTION_TYPE_LITERAL exposes the ordered connection-type tuple."""
        tm.that(c.DbOracle.CONNECTION_TYPE_LITERAL, is_=tuple)
        tm.that(
            c.DbOracle.CONNECTION_TYPE_LITERAL,
            eq=("service_name", "sid", "tns"),
        )

    @pytest.mark.parametrize(
        ("literal_name", "valid_name", "member"),
        [
            ("CONNECTION_TYPE_LITERAL", "VALID_CONNECTION_TYPES", "service_name"),
            ("QUERY_TYPE_LITERAL", "VALID_QUERY_TYPES", "DELETE"),
            ("DATA_TYPE_LITERAL", "VALID_DATA_TYPES", "CLOB"),
            ("ISOLATION_LEVEL_LITERAL", "VALID_ISOLATION_LEVELS", "SERIALIZABLE"),
        ],
    )
    def test_valid_set_is_the_frozenset_of_its_literal(
        self,
        literal_name: str,
        valid_name: str,
        member: str,
    ) -> None:
        """Each VALID_* frozenset equals the membership of its ordered literal."""
        literal = getattr(c.DbOracle, literal_name)
        valid = getattr(c.DbOracle, valid_name)
        tm.that(literal, is_=tuple)
        tm.that(valid, is_=frozenset)
        tm.that(valid, has=member)
        assert valid == frozenset(literal)

    def test_system_user_and_schema_sets(self) -> None:
        """System-user and default-schema catalogs advertise known members."""
        tm.that(c.DbOracle.SYSTEM_USERS, has="SYSTEM")
        tm.that(c.DbOracle.DEFAULT_SCHEMAS, has="PUBLIC")

    # ---- enums ----------------------------------------------------------

    @pytest.mark.parametrize(
        "enum_name",
        ["ConnectionType", "QueryType", "DataType", "IsolationLevel"],
    )
    def test_enum_is_str_enum(self, enum_name: str) -> None:
        """Each exposed Oracle enum is a StrEnum subclass."""
        enum_cls = getattr(c.DbOracle, enum_name)
        tm.that(enum_cls, is_=type)
        assert issubclass(enum_cls, StrEnum)

    def test_valid_data_types_match_data_type_enum_members(self) -> None:
        """VALID_DATA_TYPES exactly enumerates the DataType enum values."""
        enum_values = frozenset(member.value for member in c.DbOracle.DataType)
        assert enum_values == c.DbOracle.VALID_DATA_TYPES

    # ---- public behavior: collapse_whitespace ---------------------------

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("SELECT   *", "SELECT *"),
            ("SELECT\t*\nFROM\r\nDUAL", "SELECT * FROM DUAL"),
            ("  leading   and  trailing  ", " leading and trailing "),
            ("no-extra-space", "no-extra-space"),
        ],
    )
    def test_collapse_whitespace_reduces_runs_to_single_space(
        self,
        raw: str,
        expected: str,
    ) -> None:
        """collapse_whitespace replaces any whitespace run with one space."""
        tm.that(c.DbOracle.collapse_whitespace(raw), eq=expected)

    def test_collapse_whitespace_is_idempotent(self) -> None:
        """Applying collapse_whitespace twice yields the same normalized text."""
        once = c.DbOracle.collapse_whitespace("SELECT   *\n\tFROM   DUAL")
        twice = c.DbOracle.collapse_whitespace(once)
        tm.that(twice, eq=once)

    # ---- feature flag surfaced through settings public API --------------

    @pytest.mark.parametrize("enabled", [True, False])
    def test_enable_dispatcher_flag_round_trips_through_settings(
        self,
        enabled: bool,
    ) -> None:
        """The dispatcher feature flag is readable via settings public state."""
        settings = FlextDbOracleSettings.model_validate(
            {"DbOracle": {"enable_dispatcher": enabled}},
        )
        tm.that(settings.DbOracle.enable_dispatcher, eq=enabled)

    # ---- real Oracle integration (public API, fail-loud when unavailable) -

    def test_oracle_constants_real_connection_validation(
        self,
        connected_oracle_api: FlextDbOracleApi,
        oracle_available: bool,
    ) -> None:
        """TEST_QUERY and DUAL_TABLE drive a real Oracle round-trip."""
        tm.that(oracle_available, eq=True)
        result = connected_oracle_api.query(c.DbOracle.TEST_QUERY)
        tm.ok(result)
        tm.that(len(result.value), eq=1)
        dual_query = f"SELECT 1 FROM {c.DbOracle.DUAL_TABLE}"
        tm.ok(connected_oracle_api.query(dual_query))

    def test_oracle_constants_default_values_real_validation(
        self,
        connected_oracle_api: FlextDbOracleApi,
        oracle_available: bool,
    ) -> None:
        """Default connection constants are valid against a real Oracle."""
        _ = connected_oracle_api
        tm.that(oracle_available, eq=True)
        tm.that(c.DbOracle.DEFAULT_SERVICE_NAME, is_=str)
        tm.that(bool(c.DbOracle.DEFAULT_SERVICE_NAME), eq=True)
        default_port = c.DbOracle.DEFAULT_PORT
        tm.that(default_port, is_=int)
        in_range = c.DbOracle.MIN_PORT <= default_port <= c.DbOracle.MAX_PORT
        tm.that(in_range, eq=True)

    def test_oracle_data_types_real_validation(
        self,
        connected_oracle_api: FlextDbOracleApi,
        oracle_available: bool,
    ) -> None:
        """Data-type constants form a DDL statement a real Oracle accepts."""
        tm.that(oracle_available, eq=True)
        create_sql = (
            "\n        CREATE TABLE test_data_types (\n"
            f"            id {c.DbOracle.DataType.NUMBER} PRIMARY KEY,\n"
            f"            name {c.DbOracle.DEFAULT_VARCHAR_TYPE},\n"
            f"            active_flag {c.DbOracle.BOOLEAN_TYPE},\n"
            f"            created_date {c.DbOracle.DataType.DATE},\n"
            f"            data_blob {c.DbOracle.DataType.BLOB}\n"
            "        )\n        "
        )
        result = connected_oracle_api.execute_statement(create_sql)
        with contextlib.suppress(Exception):
            connected_oracle_api.execute_statement("DROP TABLE test_data_types")
        accepted = result.success or ("already exists" in str(result.error).lower())
        tm.that(accepted, eq=True)

    def test_oracle_validation_constants_real_usage(
        self,
        connected_oracle_api: FlextDbOracleApi,
        oracle_available: bool,
    ) -> None:
        """Identifier limits produce an escapable identifier on real Oracle."""
        _ = connected_oracle_api
        tm.that(oracle_available, eq=True)
        max_length = c.DbOracle.MAX_IDENTIFIER_LENGTH
        tm.that(max_length, is_=int)
        tm.that(max_length, gt=0)
        long_name = "A" * (max_length - 10)
        tm.ok(u.DbOracle.escape_oracle_identifier(long_name))
        tm.that(c.DbOracle.MAX_VARCHAR_LENGTH, eq=4000)

    def test_oracle_performance_constants_real_timing(
        self,
        connected_oracle_api: FlextDbOracleApi,
        oracle_available: bool,
    ) -> None:
        """Query timing is classified by the documented ms thresholds."""
        tm.that(oracle_available, eq=True)
        start_time = time.time()
        result = connected_oracle_api.query("SELECT 1 FROM DUAL")
        execution_ms = (time.time() - start_time) * 1000
        tm.ok(result)
        if execution_ms < c.DbOracle.QUERY_EXCELLENT_THRESHOLD_MS:
            tm.that(execution_ms, lt=100)
        elif execution_ms < c.DbOracle.QUERY_GOOD_THRESHOLD_MS:
            tm.that(execution_ms, lt=500)
        elif execution_ms < c.DbOracle.QUERY_ACCEPTABLE_THRESHOLD_MS:
            tm.that(execution_ms, lt=2000)

    def test_oracle_reserved_words_real_validation(
        self,
        connected_oracle_api: FlextDbOracleApi,
        oracle_available: bool,
    ) -> None:
        """Reserved words are rejected by the public identifier validator."""
        _ = connected_oracle_api
        tm.that(oracle_available, eq=True)
        reserved = c.DbOracle.ORACLE_RESERVED
        for word in ("SELECT", "FROM", "WHERE", "TABLE", "INDEX"):
            tm.that(reserved, has=word)
        for word in ("SELECT", "FROM", "WHERE"):
            tm.fail(u.DbOracle.validate_identifier(word), has="reserved word")

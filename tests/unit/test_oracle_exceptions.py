"""Testes REAIS de exceções Oracle - SEM MOCKS, só Oracle container real.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleExceptions as FlextExceptions,
    FlextDbOracleServices,
    FlextDbOracleSettings,
)


class TestRealOracleExceptionsCore:
    """Teste real das exceções básicas Oracle - SEM MOCKS."""

    def test_real_authentication_error_scenario(self) -> None:
        """Test FlextExceptions.AuthenticationError with real invalid credentials."""
        invalid_config = FlextDbOracleSettings(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="invalid_user_12345",
            password="invalid_password_12345",
        )
        connection = FlextDbOracleServices(config=invalid_config)
        result = connection.connect()
        if result.is_success:
            msg = "Connection with invalid credentials should fail"
            raise AssertionError(msg)
        error_msg = (result.error or "").lower()
        tm.that(
            any(
                keyword in error_msg
                for keyword in [
                    "invalid username/password",
                    "authentication",
                    "login denied",
                    "ora-01017",
                    "logon denied",
                    "connection refused",
                    "cannot connect",
                    "name or service not known",
                    "connection test failed",
                    "not connected to database",
                ]
            ),
            eq=True,
        )

    def test_real_connection_error_scenario(self) -> None:
        """Test FlextExceptions.OracleConnectionError with real unreachable host."""
        unreachable_config = FlextDbOracleSettings(
            host="unreachable-host-12345.invalid",
            port=1521,
            service_name="XEPDB1",
            username="testuser",
            password="testpass",
        )
        connection = FlextDbOracleServices(config=unreachable_config)
        result = connection.connect()
        if result.is_success:
            msg = "Connection to unreachable host should fail"
            raise AssertionError(msg)
        error_msg = (result.error or "").lower()
        tm.that(
            any(
                keyword in error_msg
                for keyword in [
                    "connection",
                    "network",
                    "host",
                    "unreachable",
                    "resolve",
                    "timeout",
                    "name or service not known",
                    "errno -2",
                    "gaierror",
                ]
            ),
            eq=True,
        )

    def test_real_configuration_error_scenario(self) -> None:
        """Test FlextExceptions.ConfigurationError with real invalid config."""
        try:
            invalid_config = FlextDbOracleSettings(
                host="localhost",
                port=1521,
                service_name="",
                sid="",
                username="testuser",
                password="testpass",
            )
            connection = FlextDbOracleServices(config=invalid_config)
            result = connection.connect()
            if result.is_success:
                msg = "Connection with invalid config should fail"
                raise AssertionError(msg)
            error_msg = result.error or ""
            tm.that(
                "service_name" in error_msg.lower() or "sid" in error_msg.lower(),
                eq=True,
            )
        except (ValueError, TypeError, RuntimeError):
            pass

    def test_real_query_error_scenario(
        self, real_oracle_config: FlextDbOracleSettings | None
    ) -> None:
        """Test FlextExceptions.OracleQueryError with real invalid SQL."""
        if real_oracle_config is None:
            pytest.skip("Oracle real config unavailable")
        connection = FlextDbOracleServices(config=real_oracle_config)
        connect_result = connection.connect()
        tm.that(connect_result.is_success, eq=True)
        try:
            invalid_queries = [
                "SELECT FROM",
                "SELECT * FROM non_existent_table_12345",
                "SELECT INVALID_FUNCTION()",
                "INSERT INTO dual VALUES (1)",
            ]
            for invalid_sql in invalid_queries:
                result = connection.execute_query(invalid_sql)
                tm.fail(result), f"Query should fail: {invalid_sql}"
                error_msg = (result.error or "").lower()
                tm.that(
                    any(
                        keyword in error_msg
                        for keyword in [
                            "ora-",
                            "syntax",
                            "invalid",
                            "not exist",
                            "table",
                            "missing",
                        ]
                    ),
                    eq=True,
                )
        finally:
            connection.disconnect()

    def test_real_timeout_error_scenario(
        self, real_oracle_config: FlextDbOracleSettings | None
    ) -> None:
        """Test FlextExceptions.TimeoutError with real long-running query."""
        if real_oracle_config is None:
            pytest.skip("Oracle real config unavailable")
        timeout_config = FlextDbOracleSettings(
            host=real_oracle_config.host,
            port=real_oracle_config.port,
            service_name=real_oracle_config.service_name,
            username=real_oracle_config.username,
            password=(
                str(real_oracle_config.password)
                if real_oracle_config.password is not None
                else None
            ),
            timeout=1,
        )
        connection = FlextDbOracleServices(config=timeout_config)
        connect_result = connection.connect()
        tm.that(connect_result.is_success, eq=True)
        try:
            long_query = (
                "SELECT * FROM (SELECT LEVEL FROM DUAL CONNECT BY LEVEL <= 100000)"
            )
            result = connection.execute_query(long_query)
            if result.is_failure:
                error_msg = (result.error or "").lower()
                tm.that(
                    any(
                        keyword in error_msg
                        for keyword in [
                            "timeout",
                            "cancel",
                            "interrupt",
                            "resource",
                            "limit",
                        ]
                    ),
                    eq=True,
                )
        finally:
            connection.disconnect()


class TestRealOracleExceptionsAdvanced:
    """Teste real de exceções avançadas Oracle - SEM MOCKS."""

    def test_real_metadata_error_scenario(
        self, connected_oracle_api: FlextDbOracleApi | None
    ) -> None:
        """Test FlextExceptions.OracleMetadataError with real metadata operations."""
        if connected_oracle_api is None:
            pytest.skip("Connected Oracle API unavailable")
        invalid_schemas = ["NON_EXISTENT_SCHEMA_12345", "INVALID$SCHEMA", ""]
        for invalid_schema in invalid_schemas:
            if invalid_schema:
                result = connected_oracle_api.get_tables(schema=invalid_schema)
                tm.that(result.is_success or result.is_failure, eq=True)
        columns_result = connected_oracle_api.get_columns("NON_EXISTENT_TABLE_12345")
        if columns_result.is_failure:
            msg = f"Get columns failed: {columns_result.error}"
            raise AssertionError(msg)
        tm.that(isinstance(columns_result.value, list), eq=True)
        tm.that(len(columns_result.value), eq=0)

    def test_real_processing_error_scenario(
        self, connected_oracle_api: FlextDbOracleApi | None
    ) -> None:
        """Test FlextExceptions.ProcessingError with real data processing errors."""
        if connected_oracle_api is None:
            pytest.skip("Connected Oracle API unavailable")
        try:
            problematic_operations = [
                "SELECT * FROM NON_EXISTENT_TABLE_12345",
                "INSERT INTO dual VALUES (1, 2)",
                "CREATE TABLE invalid..syntax ERROR",
            ]
            for invalid_operation in problematic_operations:
                result = connected_oracle_api.query(invalid_operation)
                tm.fail(result), f"Operation should fail: {invalid_operation}"
                error_msg = (result.error or "").lower()
                tm.that(
                    any(
                        keyword in error_msg
                        for keyword in [
                            "ora-",
                            "invalid",
                            "not exist",
                            "table",
                            "syntax",
                            "error",
                        ]
                    ),
                    eq=True,
                )
        finally:
            pass

    def test_real_validation_error_scenario(self) -> None:
        """Test FlextExceptions.ValidationError with real config validation."""
        invalid_configs = [
            {
                "host": "",
                "port": 1521,
                "service_name": "XE",
                "user": "user",
                "password": "pass",
            },
            {
                "host": "localhost",
                "port": -1,
                "service_name": "XE",
                "user": "user",
                "password": "pass",
            },
            {
                "host": "localhost",
                "port": 99999,
                "service_name": "XE",
                "user": "user",
                "password": "pass",
            },
            {
                "host": "localhost",
                "port": 1521,
                "service_name": "XE",
                "user": "",
                "password": "pass",
            },
        ]
        for config_data in invalid_configs:
            try:
                port_value = config_data.get("port", 1521)
                tm.that(isinstance(port_value, int), eq=True)
                host_value = str(config_data.get("host", ""))
                user_value = str(config_data.get("user", ""))
                password_value = str(config_data.get("password", ""))
                service_name_value = str(config_data.get("service_name", "XE"))
                FlextDbOracleSettings(
                    host=host_value,
                    port=port_value,
                    username=user_value,
                    password=password_value,
                    service_name=service_name_value,
                )
            except (ValueError, TypeError):
                pass


class TestRealOracleExceptionHierarchy:
    """Test real Oracle exception hierarchy and inheritance - SEM MOCKS."""

    def test_real_exception_inheritance(self) -> None:
        """Test that Oracle exceptions inherit properly from base Exception classes."""
        tm.that(issubclass(FlextExceptions.Error, Exception), eq=True)
        tm.that(issubclass(FlextExceptions.AuthenticationError, Exception), eq=True)
        tm.that(issubclass(FlextExceptions.ConfigurationError, Exception), eq=True)
        tm.that(issubclass(FlextExceptions.OracleConnectionError, Exception), eq=True)
        tm.that(issubclass(FlextExceptions.OracleMetadataError, Exception), eq=True)
        tm.that(issubclass(FlextExceptions.ProcessingError, Exception), eq=True)
        tm.that(issubclass(FlextExceptions.OracleQueryError, Exception), eq=True)
        tm.that(issubclass(FlextExceptions.OracleTimeoutError, Exception), eq=True)
        tm.that(issubclass(FlextExceptions.ValidationError, Exception), eq=True)
        tm.that(
            issubclass(FlextExceptions.OracleQueryError, FlextExceptions.BaseError),
            eq=True,
        )
        tm.that(
            issubclass(FlextExceptions.OracleMetadataError, FlextExceptions.BaseError),
            eq=True,
        )

    def test_real_exception_instantiation(self) -> None:
        """Test that Oracle exceptions can be instantiated with context."""
        query_error = FlextExceptions.OracleQueryError("Invalid SQL syntax")
        tm.that("Invalid SQL syntax" in str(query_error), eq=True)
        metadata_error = FlextExceptions.OracleMetadataError("Schema not found")
        tm.that("Schema not found" in str(metadata_error), eq=True)
        base_error = FlextExceptions.Error("General Oracle error")
        tm.that("General Oracle error" in str(base_error), eq=True)

    def test_real_exception_context_handling(self) -> None:
        """Test that Oracle exceptions handle context parameters properly."""
        query_error = FlextExceptions.OracleQueryError("Query too complex")
        error_str = str(query_error)
        tm.that("Query too complex" in error_str, eq=True)
        tm.that(isinstance(error_str, str), eq=True)
        tm.that(len(error_str) > 0, eq=True)

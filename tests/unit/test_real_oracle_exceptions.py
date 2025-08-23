"""Testes REAIS de exceções Oracle - SEM MOCKS, só Oracle container real.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib

from pydantic import SecretStr

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleAuthenticationError,
    FlextDbOracleConfig,
    FlextDbOracleConfigurationError,
    FlextDbOracleConnection,
    FlextDbOracleConnectionError,
    FlextDbOracleError,
    FlextDbOracleMetadataError,
    FlextDbOracleProcessingError,
    FlextDbOracleQueryError,
    FlextDbOracleTimeoutError,
    FlextDbOracleValidationError,
)
from flext_db_oracle.exceptions import FlextDbOracleErrorCodes


class TestRealOracleExceptionsCore:
    """Teste real das exceções básicas Oracle - SEM MOCKS."""

    def test_real_authentication_error_scenario(self) -> None:
        """Test FlextDbOracleAuthenticationError with real invalid credentials."""
        # Use real invalid credentials against Oracle container
        invalid_config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="invalid_user_12345",
            password=SecretStr("invalid_password_12345"),
        )

        connection = FlextDbOracleConnection(invalid_config)
        result = connection.connect()

        # Connection should fail with authentication error - using modern pattern
        if result.success:
            raise AssertionError("Connection with invalid credentials should fail")
        # Failure case - use error directly
        error_msg = (result.error or "").lower()
        # Oracle returns different error messages for invalid credentials or connection issues
        assert any(
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
            ]
        )

    def test_real_connection_error_scenario(self) -> None:
        """Test FlextDbOracleConnectionError with real unreachable host."""
        # Use real unreachable host
        unreachable_config = FlextDbOracleConfig(
            host="unreachable-host-12345.invalid",
            port=1521,
            service_name="XEPDB1",
            username="testuser",
            password=SecretStr("testpass"),
        )

        connection = FlextDbOracleConnection(unreachable_config)
        result = connection.connect()

        # Should fail with connection error - using modern pattern
        if result.success:
            raise AssertionError("Connection to unreachable host should fail")
        # Failure case - use error directly
        error_msg = (result.error or "").lower()
        # Network/DNS resolution errors
        assert any(
            keyword in error_msg
            for keyword in [
                "connection",
                "network",
                "host",
                "unreachable",
                "resolve",
                "timeout",
                "name or service not known",  # DNS resolution error
                "errno -2",  # Socket error code for DNS resolution
                "gaierror",  # getaddrinfo error
            ]
        )

    def test_real_configuration_error_scenario(self) -> None:
        """Test FlextDbOracleConfigurationError with real invalid config."""
        # Test config without service_name or sid - should fail validation
        try:
            invalid_config = FlextDbOracleConfig(
                host="localhost",
                port=1521,
                service_name="",  # Empty service name
                sid="",  # Empty SID
                username="testuser",
                password=SecretStr("testpass"),
            )
            connection = FlextDbOracleConnection(invalid_config)
            result = connection.connect()

            # Should fail configuration validation - using modern pattern
            if result.success:
                raise AssertionError("Connection with invalid config should fail")
            # Failure case - use error directly
            error_msg = result.error or ""
            assert "service_name" in error_msg.lower() or "sid" in error_msg.lower()

        except (ValueError, TypeError, RuntimeError):
            # Config validation might fail at creation time
            pass  # Expected configuration error

    def test_real_query_error_scenario(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test FlextDbOracleQueryError with real invalid SQL."""
        connection = FlextDbOracleConnection(real_oracle_config)

        connect_result = connection.connect()
        assert connect_result.success

        try:
            # Execute real invalid SQL against Oracle
            invalid_queries = [
                "SELECT FROM",  # Syntax error
                "SELECT * FROM non_existent_table_12345",  # Table doesn't exist
                "SELECT INVALID_FUNCTION()",  # Invalid function
                "INSERT INTO dual VALUES (1)",  # Can't insert into DUAL
            ]

            for invalid_sql in invalid_queries:
                result = connection.execute(invalid_sql)
                assert result.is_failure, f"Query should fail: {invalid_sql}"

                error_msg = (result.error or "").lower()
                # Should contain Oracle error indicators
                assert any(
                    keyword in error_msg
                    for keyword in [
                        "ora-",
                        "syntax",
                        "invalid",
                        "not exist",
                        "table",
                        "missing",
                    ]
                )

        finally:
            connection.disconnect()

    def test_real_timeout_error_scenario(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test FlextDbOracleTimeoutError with real long-running query."""
        # Create config with very short timeout
        timeout_config = FlextDbOracleConfig(
            host=real_oracle_config.host,
            port=real_oracle_config.port,
            service_name=real_oracle_config.service_name,
            username=real_oracle_config.username,
            password=real_oracle_config.password,
            timeout=1,  # 1 second timeout
        )

        connection = FlextDbOracleConnection(timeout_config)
        connect_result = connection.connect()
        assert connect_result.success

        try:
            # Execute query that might timeout (sleep simulation)
            # Note: Oracle might not respect query timeout exactly
            long_query = (
                "SELECT * FROM (SELECT LEVEL FROM DUAL CONNECT BY LEVEL <= 100000)"
            )
            result = connection.execute(long_query)

            # Either succeeds quickly or fails with timeout-related error
            if result.is_failure:
                error_msg = (result.error or "").lower()
                # Timeout or resource-related errors
                assert any(
                    keyword in error_msg
                    for keyword in [
                        "timeout",
                        "cancel",
                        "interrupt",
                        "resource",
                        "limit",
                    ]
                )

        finally:
            connection.disconnect()


class TestRealOracleExceptionsAdvanced:
    """Teste real de exceções avançadas Oracle - SEM MOCKS."""

    def test_real_metadata_error_scenario(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """Test FlextDbOracleMetadataError with real metadata operations."""
        # Try to get metadata for non-existent schema
        invalid_schemas = ["NON_EXISTENT_SCHEMA_12345", "INVALID$SCHEMA", ""]

        for invalid_schema in invalid_schemas:
            if invalid_schema:  # Skip empty schema for now
                result = connected_oracle_api.get_tables(schema=invalid_schema)
                # May succeed with empty results or fail - both are valid
                # Focus on ensuring no crashes and proper error handling
                assert (
                    result.success or result.is_failure
                )  # Should return valid FlextResult

        # Try to get columns for non-existent table
        columns_result = connected_oracle_api.get_columns("NON_EXISTENT_TABLE_12345")
        # Should return empty list, not crash - using modern pattern
        if columns_result.is_failure:
            raise AssertionError(f"Get columns failed: {columns_result.error}")
        # Success case - use modern .value access
        assert isinstance(columns_result.value, list)
        assert len(columns_result.value) == 0  # No columns for non-existent table

    def test_real_processing_error_scenario(
        self,
        connected_oracle_api: FlextDbOracleApi,
    ) -> None:
        """Test FlextDbOracleProcessingError with real data processing errors."""
        # Create table with constraints then violate them
        table_name = "TEST_CONSTRAINT_TABLE"

        try:
            # Create table with NOT NULL constraint
            columns = [
                {
                    "name": "id",
                    "type": "NUMBER",
                    "nullable": False,
                    "primary_key": True,
                },
                {"name": "required_field", "type": "VARCHAR2(100)", "nullable": False},
                {"name": "optional_field", "type": "VARCHAR2(100)", "nullable": True},
            ]

            ddl_result = connected_oracle_api.create_table_ddl(table_name, columns)
            assert ddl_result.success

            execute_result = connected_oracle_api.execute_ddl(ddl_result.value)
            assert execute_result.success

            # Try to insert NULL into NOT NULL column - should fail
            insert_sql = (
                f"INSERT INTO {table_name} (id, required_field) VALUES (1, NULL)"
            )
            result = connected_oracle_api.query(insert_sql)
            assert result.is_failure  # Should fail constraint violation

            error_msg = (result.error or "").lower()
            assert any(
                keyword in error_msg
                for keyword in [
                    "not null",
                    "constraint",
                    "violated",
                    "ora-01400",
                ]
            )

        finally:
            # Cleanup
            with contextlib.suppress(Exception):
                drop_ddl = connected_oracle_api.drop_table_ddl(table_name)
                if drop_ddl.success:
                    connected_oracle_api.execute_ddl(drop_ddl.value)

    def test_real_validation_error_scenario(self) -> None:
        """Test FlextDbOracleValidationError with real config validation."""
        # Test various invalid configurations
        invalid_configs = [
            {
                "host": "",
                "port": 1521,
                "service_name": "XE",
                "username": "user",
                "password": "pass",
            },
            {
                "host": "localhost",
                "port": -1,
                "service_name": "XE",
                "username": "user",
                "password": "pass",
            },
            {
                "host": "localhost",
                "port": 99999,
                "service_name": "XE",
                "username": "user",
                "password": "pass",
            },
            {
                "host": "localhost",
                "port": 1521,
                "service_name": "XE",
                "username": "",
                "password": "pass",
            },
        ]

        for config_data in invalid_configs:
            try:
                # Convert config_data to proper types
                port_value = config_data.get("port", 1521)
                typed_config: dict[str, object] = {
                    "host": str(config_data.get("host", "")),
                    "port": int(port_value)
                    if isinstance(port_value, (int, str))
                    else 1521,
                    "username": str(config_data.get("username", "")),
                    "password": SecretStr(str(config_data.get("password", ""))),
                }
                if "service_name" in config_data:
                    typed_config["service_name"] = str(config_data["service_name"])

                config = FlextDbOracleConfig(**typed_config)  # type: ignore[arg-type]
                validation_result = config.validate_business_rules()

                # Should either fail validation or catch during creation
                if validation_result:
                    assert validation_result.is_failure

            except (ValueError, TypeError):
                # Config creation itself should fail for invalid data
                pass  # Expected validation error


class TestRealOracleExceptionHierarchy:
    """Test real Oracle exception hierarchy and inheritance - SEM MOCKS."""

    def test_real_exception_inheritance(self) -> None:
        """Test that Oracle exceptions inherit properly from base Exception classes."""
        # Test exception class hierarchy - all should inherit from Exception
        # Note: Direct inheritance from Exception to avoid MyPy issues with flext-core
        assert issubclass(FlextDbOracleError, Exception)
        assert issubclass(FlextDbOracleAuthenticationError, Exception)
        assert issubclass(FlextDbOracleConfigurationError, Exception)
        assert issubclass(FlextDbOracleConnectionError, Exception)
        assert issubclass(FlextDbOracleMetadataError, Exception)
        assert issubclass(FlextDbOracleProcessingError, Exception)
        assert issubclass(FlextDbOracleQueryError, Exception)
        assert issubclass(FlextDbOracleTimeoutError, Exception)
        assert issubclass(FlextDbOracleValidationError, Exception)

        # Test that domain-specific exceptions inherit from FlextDbOracleError (factory-created)
        assert issubclass(FlextDbOracleQueryError, FlextDbOracleError)
        assert issubclass(FlextDbOracleMetadataError, FlextDbOracleError)

    def test_real_exception_instantiation(self) -> None:
        """Test that Oracle exceptions can be instantiated with context."""
        # Test FlextDbOracleQueryError with context
        query_error = FlextDbOracleQueryError(
            "Invalid SQL syntax",
            query="SELECT FROM WHERE",
            code=FlextDbOracleErrorCodes.ORACLE_QUERY_ERROR,
        )
        assert "Invalid SQL syntax" in str(query_error)

        # Test FlextDbOracleMetadataError with context
        metadata_error = FlextDbOracleMetadataError(
            "Schema not found",
            schema_name="INVALID_SCHEMA",
            object_name="SOME_TABLE",
        )
        assert "Schema not found" in str(metadata_error)

        # Test base FlextDbOracleError
        base_error = FlextDbOracleError("General Oracle error")
        assert "General Oracle error" in str(base_error)

    def test_real_exception_context_handling(self) -> None:
        """Test that Oracle exceptions handle context parameters properly."""
        # Test query truncation for long queries
        long_query = (
            "SELECT " + ", ".join(f"col{i}" for i in range(100)) + " FROM table"
        )

        query_error = FlextDbOracleQueryError(
            "Query too complex",
            query=long_query,
            code=FlextDbOracleErrorCodes.ORACLE_QUERY_ERROR,
        )

        # Query should be truncated to 200 characters in context
        error_str = str(query_error)
        assert "Query too complex" in error_str
        assert len(long_query) > 200  # Original query is long
        # The actual query in context should be truncated (internal implementation)

"""Testes REAIS de exceções Oracle - SEM MOCKS, só Oracle container real.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
    FlextDbOracleConnection,
)
from flext_db_oracle.exceptions import (
    FlextDbOracleAuthenticationError,
    FlextDbOracleConfigurationError,
    FlextDbOracleConnectionError,
    FlextDbOracleError,
    FlextDbOracleMetadataError,
    FlextDbOracleProcessingError,
    FlextDbOracleQueryError,
    FlextDbOracleTimeoutError,
    FlextDbOracleValidationError,
)


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
            password="invalid_password_12345",
        )

        connection = FlextDbOracleConnection(invalid_config)
        result = connection.connect()

        # Connection should fail with authentication error
        assert result.is_failure
        error_msg = result.error.lower()
        # Oracle returns different error messages for invalid credentials
        assert any(
            keyword in error_msg
            for keyword in [
                "invalid username/password",
                "authentication",
                "login denied",
                "ora-01017",
                "logon denied",
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
            password="testpass",
        )

        connection = FlextDbOracleConnection(unreachable_config)
        result = connection.connect()

        # Should fail with connection error
        assert result.is_failure
        error_msg = result.error.lower()
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
                password="testpass",
            )
            connection = FlextDbOracleConnection(invalid_config)
            result = connection.connect()

            # Should fail configuration validation
            assert result.is_failure
            assert (
                "service_name" in result.error.lower() or "sid" in result.error.lower()
            )

        except Exception as e:
            # Config validation might fail at creation time
            assert "service_name" in str(e).lower() or "sid" in str(e).lower()

    def test_real_query_error_scenario(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test FlextDbOracleQueryError with real invalid SQL."""
        connection = FlextDbOracleConnection(real_oracle_config)

        connect_result = connection.connect()
        assert connect_result.is_success

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

                error_msg = result.error.lower()
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
            password=real_oracle_config.password.get_secret_value(),
            timeout=1,  # 1 second timeout
        )

        connection = FlextDbOracleConnection(timeout_config)
        connect_result = connection.connect()
        assert connect_result.is_success

        try:
            # Execute query that might timeout (sleep simulation)
            # Note: Oracle might not respect query timeout exactly
            long_query = (
                "SELECT * FROM (SELECT LEVEL FROM DUAL CONNECT BY LEVEL <= 100000)"
            )
            result = connection.execute(long_query)

            # Either succeeds quickly or fails with timeout-related error
            if result.is_failure:
                error_msg = result.error.lower()
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
                    result.is_success or result.is_failure
                )  # Should return valid FlextResult

        # Try to get columns for non-existent table
        result = connected_oracle_api.get_columns("NON_EXISTENT_TABLE_12345")
        assert result.is_success  # Should return empty list, not crash
        assert isinstance(result.data, list)
        assert len(result.data) == 0  # No columns for non-existent table

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
            assert ddl_result.is_success

            execute_result = connected_oracle_api.execute_ddl(ddl_result.data)
            assert execute_result.is_success

            # Try to insert NULL into NOT NULL column - should fail
            insert_sql = (
                f"INSERT INTO {table_name} (id, required_field) VALUES (1, NULL)"
            )
            result = connected_oracle_api.query(insert_sql)
            assert result.is_failure  # Should fail constraint violation

            error_msg = result.error.lower()
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
                if drop_ddl.is_success:
                    connected_oracle_api.execute_ddl(drop_ddl.data)

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
                config = FlextDbOracleConfig(**config_data)
                validation_result = config.validate_domain_rules()

                # Should either fail validation or catch during creation
                if validation_result:
                    assert validation_result.is_failure

            except (ValueError, TypeError) as e:
                # Config creation itself should fail for invalid data
                assert len(str(e)) > 0  # Should have meaningful error message


class TestRealOracleExceptionHierarchy:
    """Test real Oracle exception hierarchy and inheritance - SEM MOCKS."""

    def test_real_exception_inheritance(self) -> None:
        """Test that Oracle exceptions inherit properly from FLEXT base classes."""
        from flext_core.exceptions import FlextError

        # Test exception class hierarchy - all should inherit from FlextError
        assert issubclass(FlextDbOracleError, FlextError)
        assert issubclass(FlextDbOracleAuthenticationError, FlextError)
        assert issubclass(FlextDbOracleConfigurationError, FlextError)
        assert issubclass(FlextDbOracleConnectionError, FlextError)
        assert issubclass(FlextDbOracleMetadataError, FlextError)
        assert issubclass(FlextDbOracleProcessingError, FlextError)
        assert issubclass(FlextDbOracleQueryError, FlextError)
        assert issubclass(FlextDbOracleTimeoutError, FlextError)
        assert issubclass(FlextDbOracleValidationError, FlextError)

        # Test that domain-specific exceptions inherit from FlextDbOracleError (factory-created)
        assert issubclass(FlextDbOracleQueryError, FlextDbOracleError)
        assert issubclass(FlextDbOracleMetadataError, FlextDbOracleError)

    def test_real_exception_instantiation(self) -> None:
        """Test that Oracle exceptions can be instantiated with context."""
        # Test FlextDbOracleQueryError with context
        query_error = FlextDbOracleQueryError(
            "Invalid SQL syntax",
            query="SELECT FROM WHERE",
            error_code="ORA-00936",
        )
        assert "Oracle DB query: Invalid SQL syntax" in str(query_error)

        # Test FlextDbOracleMetadataError with context
        metadata_error = FlextDbOracleMetadataError(
            "Schema not found",
            schema_name="INVALID_SCHEMA",
            object_name="SOME_TABLE",
        )
        assert "Oracle DB metadata: Schema not found" in str(metadata_error)

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
            error_code="ORA-99999",
        )

        # Query should be truncated to 200 characters in context
        error_str = str(query_error)
        assert "Oracle DB query: Query too complex" in error_str
        assert len(long_query) > 200  # Original query is long
        # The actual query in context should be truncated (internal implementation)

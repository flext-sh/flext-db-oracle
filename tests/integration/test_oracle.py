"""Integration tests for flext-db-oracle with REAL Oracle connectivity.

These tests use actual Oracle connections to validate real integration scenarios.
Requires Oracle container or environment configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_db_oracle import (
    FlextDbOracleApi,
    FlextDbOracleConfig,
)


class TestOracleIntegration:
    """Integration tests for Oracle database operations using REAL Oracle connectivity."""

    @pytest.mark.integration
    def test_api_full_workflow(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test complete API workflow with real Oracle connection."""
        # Create API instance
        api = FlextDbOracleApi(real_oracle_config)

        # Test connection establishment
        connect_result = api.connect()
        assert connect_result.is_success, f"Connection failed: {connect_result.error}"
        connected_api = connect_result.value

        # Test connection status
        test_result = connected_api.test_connection()
        if test_result.is_failure:
            msg = f"Connection test failed: {test_result.error}"
            raise AssertionError(msg)

        # Test schema operations
        schemas_result = connected_api.get_schemas()
        if schemas_result.is_failure:
            msg = f"Get schemas failed: {schemas_result.error}"
            raise AssertionError(msg)
        schemas = schemas_result.value
        assert len(schemas) > 0, "Should have at least one schema"

        # Test table operations
        tables_result = connected_api.get_tables()
        if tables_result.is_failure:
            msg = f"Get tables failed: {tables_result.error}"
            raise AssertionError(msg)

        # Test query execution
        query_result = connected_api.query("SELECT SYSDATE FROM DUAL")
        if query_result.is_failure:
            msg = f"Query failed: {query_result.error}"
            raise AssertionError(msg)
        query_data = query_result.value
        assert len(query_data) == 1, "Query should return exactly one row"

        # Clean disconnect
        connected_api.disconnect()

    @pytest.mark.integration
    def test_api_error_handling(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test error handling with real Oracle connection."""
        api = FlextDbOracleApi(real_oracle_config)
        connect_result = api.connect()
        assert connect_result.is_success, f"Connection failed: {connect_result.error}"
        connected_api = connect_result.value

        # Test invalid SQL
        invalid_query_result = connected_api.query("INVALID SQL STATEMENT")
        if invalid_query_result.is_success:
            msg = "Invalid SQL should fail"
            raise AssertionError(msg)
        error_msg = invalid_query_result.error or ""
        assert "ORA-" in error_msg or "syntax" in error_msg.lower()

        # Test non-existent table
        nonexistent_table_result = connected_api.query(
            "SELECT * FROM NONEXISTENT_TABLE_12345",
        )
        if nonexistent_table_result.is_success:
            msg = "Query on non-existent table should fail"
            raise AssertionError(msg)

        connected_api.disconnect()

    @pytest.mark.integration
    def test_api_context_manager(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test API context manager functionality with real Oracle."""
        api = FlextDbOracleApi(real_oracle_config)

        # Test context manager usage
        with api:
            # Test operations within context
            test_result = api.test_connection()
            if test_result.is_failure:
                msg = f"Connection test failed: {test_result.error}"
                raise AssertionError(msg)

            query_result = api.query("SELECT 1 FROM DUAL")
            if query_result.is_failure:
                msg = f"Query failed: {query_result.error}"
                raise AssertionError(msg)

        # Connection should be automatically closed after context

    @pytest.mark.integration
    def test_api_metadata_operations(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test metadata operations with real Oracle."""
        api = FlextDbOracleApi(real_oracle_config)
        connect_result = api.connect()
        assert connect_result.is_success, f"Connection failed: {connect_result.error}"
        connected_api = connect_result.value

        # Test schema listing
        schemas_result = connected_api.get_schemas()
        if schemas_result.is_failure:
            msg = f"Get schemas failed: {schemas_result.error}"
            raise AssertionError(msg)
        schemas = schemas_result.value
        assert isinstance(schemas, list)

        # Test table listing for available schemas
        if schemas:
            first_schema = schemas[0]
            tables_result = connected_api.get_tables(first_schema)
            if tables_result.is_failure:
                msg = f"Get tables failed: {tables_result.error}"
                raise AssertionError(msg)

            # If tables exist, test column information
            tables = tables_result.value
            if tables:
                first_table = tables[0]
                table_name = (
                    first_table["name"]
                    if isinstance(first_table, dict)
                    else str(first_table)
                )
                # Cast table_name to string for type safety
                table_name_str = str(table_name)
                columns_result = connected_api.get_columns(table_name_str)
                if columns_result.is_failure:
                    msg = f"Get columns failed: {columns_result.error}"
                    raise AssertionError(msg)
                columns = columns_result.value
                assert isinstance(columns, list)

        connected_api.disconnect()

    @pytest.mark.integration
    def test_api_performance_operations(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test performance-related operations with real Oracle."""
        # Use the config parameter to avoid unused argument warning
        assert real_oracle_config is not None
        # Test health check - method not implemented yet
        pytest.skip("get_health_check method not implemented")

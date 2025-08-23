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
        connected_api = api.connect()
        assert connected_api is not None

        # Test connection status
        test_result = connected_api.test_connection()
        if test_result.is_failure:
            raise AssertionError(f"Connection test failed: {test_result.error}")

        # Test schema operations
        schemas_result = connected_api.get_schemas()
        if schemas_result.is_failure:
            raise AssertionError(f"Get schemas failed: {schemas_result.error}")
        schemas = schemas_result.value
        assert len(schemas) > 0, "Should have at least one schema"

        # Test table operations
        tables_result = connected_api.get_tables()
        if tables_result.is_failure:
            raise AssertionError(f"Get tables failed: {tables_result.error}")

        # Test query execution
        query_result = connected_api.query("SELECT SYSDATE FROM DUAL")
        if query_result.is_failure:
            raise AssertionError(f"Query failed: {query_result.error}")
        query_data = query_result.value
        assert query_data.row_count == 1, "Query should return exactly one row"

        # Clean disconnect
        connected_api.disconnect()

    @pytest.mark.integration
    def test_api_error_handling(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test error handling with real Oracle connection."""
        api = FlextDbOracleApi(real_oracle_config)
        connected_api = api.connect()

        # Test invalid SQL
        invalid_query_result = connected_api.query("INVALID SQL STATEMENT")
        if invalid_query_result.is_success:
            raise AssertionError("Invalid SQL should fail")
        error_msg = invalid_query_result.error or ""
        assert (
            "ORA-" in error_msg
            or "syntax" in error_msg.lower()
        )

        # Test non-existent table
        nonexistent_table_result = connected_api.query(
            "SELECT * FROM NONEXISTENT_TABLE_12345"
        )
        if nonexistent_table_result.is_success:
            raise AssertionError("Query on non-existent table should fail")

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
                raise AssertionError(f"Connection test failed: {test_result.error}")

            query_result = api.query("SELECT 1 FROM DUAL")
            if query_result.is_failure:
                raise AssertionError(f"Query failed: {query_result.error}")

        # Connection should be automatically closed after context

    @pytest.mark.integration
    def test_api_metadata_operations(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test metadata operations with real Oracle."""
        api = FlextDbOracleApi(real_oracle_config)
        connected_api = api.connect()

        # Test schema listing
        schemas_result = connected_api.get_schemas()
        if schemas_result.is_failure:
            raise AssertionError(f"Get schemas failed: {schemas_result.error}")
        schemas = schemas_result.value
        assert isinstance(schemas, list)

        # Test table listing for available schemas
        if schemas:
            first_schema = schemas[0]
            tables_result = connected_api.get_tables(first_schema)
            if tables_result.is_failure:
                raise AssertionError(f"Get tables failed: {tables_result.error}")

            # If tables exist, test column information
            tables = tables_result.value
            if tables:
                first_table = tables[0]
                columns_result = connected_api.get_columns(first_table, first_schema)
                if columns_result.is_failure:
                    raise AssertionError(f"Get columns failed: {columns_result.error}")
                columns = columns_result.value
                assert isinstance(columns, list)

        connected_api.disconnect()

    @pytest.mark.integration
    def test_api_performance_operations(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test performance-related operations with real Oracle."""
        api = FlextDbOracleApi(real_oracle_config)
        connected_api = api.connect()

        # Test health check
        health_result = connected_api.get_health_check()
        if health_result.is_failure:
            raise AssertionError(f"Health check failed: {health_result.error}")

        health_data = health_result.value
        assert hasattr(health_data, "status")
        assert hasattr(health_data, "timestamp")

        # Test observability metrics
        metrics_result = connected_api.get_observability_metrics()
        if metrics_result.is_failure:
            raise AssertionError(f"Metrics failed: {metrics_result.error}")

        metrics = metrics_result.value
        assert isinstance(metrics, dict)
        assert "is_connected" in metrics

        connected_api.disconnect()

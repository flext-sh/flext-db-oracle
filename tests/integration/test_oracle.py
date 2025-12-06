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


@pytest.fixture
def mock_oracle_config() -> FlextDbOracleConfig:
    """Create a mock Oracle config for testing API instantiation."""
    return FlextDbOracleConfig(
        host="mock-host",
        port=1521,
        service_name="mock-service",
        username="mock-user",
        password="mock-pass",
    )


@pytest.mark.unit_pure
class TestOracleIntegration:
    """Integration tests for Oracle database operations using REAL Oracle connectivity."""

    def test_api_instantiation_mock(
        self,
        mock_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test API instantiation with mock config."""
        api = FlextDbOracleApi(config=mock_oracle_config)
        assert api is not None
        assert hasattr(api, "connect")
        assert hasattr(api, "disconnect")
        assert hasattr(api, "query")

    @pytest.mark.oracle
    def test_api_full_workflow(
        self,
        real_oracle_config: FlextDbOracleConfig | None,
        mock_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test complete API workflow with real Oracle connection or skip if not available."""
        config = real_oracle_config or mock_oracle_config

        # Create API instance
        api = FlextDbOracleApi(config=config)

        # If we have real config, try to connect
        if real_oracle_config is not None:
            # This is a real integration test
            connect_result = api.connect()
            if connect_result.is_failure:
                pytest.skip(f"Oracle container not available: {connect_result.error}")

            connected_api = connect_result.value

            # Test connection status
            test_result = connected_api.test_connection()
            assert test_result.is_success, (
                f"Connection test failed: {test_result.error}"
            )

            # Test schema operations
            schemas_result = connected_api.get_schemas()
            assert schemas_result.is_success, (
                f"Get schemas failed: {schemas_result.error}"
            )
            schemas = schemas_result.value
            assert len(schemas) > 0, "Should have at least one schema"

            # Test table operations
            tables_result = connected_api.get_tables()
            assert tables_result.is_success, f"Get tables failed: {tables_result.error}"

            # Test query execution
            query_result = connected_api.query("SELECT SYSDATE FROM DUAL")
            assert query_result.is_success, f"Query failed: {query_result.error}"
            query_data = query_result.value
            assert len(query_data) == 1, "Query should return exactly one row"

            # Clean disconnect
            connected_api.disconnect()
        else:
            # Mock config - just test that API can be created and has expected methods
            assert api is not None
            pytest.skip(
                "Oracle container not available - tested API instantiation only",
            )

    @pytest.mark.oracle
    def test_api_error_handling(
        self,
        real_oracle_config: FlextDbOracleConfig | None,
        mock_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test error handling with real Oracle connection or skip if not available."""
        config = real_oracle_config or mock_oracle_config
        api = FlextDbOracleApi(config=config)

        if real_oracle_config is None:
            pytest.skip("Oracle container not available - skipping error handling test")

        # Connect to Oracle
        connect_result = api.connect()
        if connect_result.is_failure:
            pytest.skip(f"Failed to connect to Oracle: {connect_result.error}")

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

    @pytest.mark.oracle
    def test_api_context_manager(
        self,
        real_oracle_config: FlextDbOracleConfig | None,
        mock_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test API context manager functionality with real Oracle or skip if not available."""
        config = real_oracle_config or mock_oracle_config
        api = FlextDbOracleApi(config=config)

        if real_oracle_config is None:
            pytest.skip(
                "Oracle container not available - skipping context manager test",
            )

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

    @pytest.mark.oracle
    def test_api_metadata_operations(
        self,
        real_oracle_config: FlextDbOracleConfig | None,
        mock_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test metadata operations with real Oracle or skip if not available."""
        config = real_oracle_config or mock_oracle_config
        api = FlextDbOracleApi(config=config)

        if real_oracle_config is None:
            pytest.skip(
                "Oracle container not available - skipping metadata operations test",
            )

        # Connect to Oracle
        connect_result = api.connect()
        if connect_result.is_failure:
            pytest.skip(f"Failed to connect to Oracle: {connect_result.error}")

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

    @pytest.mark.oracle
    def test_database_operations_with_setup(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        test_database_setup: dict[str, str] | None,
    ) -> None:
        """Test database operations using test schema setup."""
        if connected_oracle_api is None or test_database_setup is None:
            pytest.skip(
                "Oracle container not available - skipping database operations test",
            )

        # Test table creation from setup
        assert "test_table" in test_database_setup

        # Test basic CRUD operations
        # Insert data
        insert_result = connected_oracle_api.execute_statement(
            "INSERT INTO test_table (id, name) VALUES (1, 'Test User')",
        )
        assert insert_result.is_success, f"Insert failed: {insert_result.error}"

        # Query data
        query_result = connected_oracle_api.query(
            "SELECT id, name FROM test_table WHERE id = 1",
        )
        assert query_result.is_success, f"Query failed: {query_result.error}"
        data = query_result.value
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["name"] == "Test User"

        # Update data
        update_result = connected_oracle_api.execute_statement(
            "UPDATE test_table SET name = 'Updated User' WHERE id = 1",
        )
        assert update_result.is_success, f"Update failed: {update_result.error}"

        # Verify update
        query_result = connected_oracle_api.query(
            "SELECT name FROM test_table WHERE id = 1",
        )
        assert query_result.is_success
        data = query_result.value
        assert data[0]["name"] == "Updated User"

        # Delete data
        delete_result = connected_oracle_api.execute_statement(
            "DELETE FROM test_table WHERE id = 1",
        )
        assert delete_result.is_success, f"Delete failed: {delete_result.error}"

        # Verify deletion
        query_result = connected_oracle_api.query(
            "SELECT COUNT(*) as count FROM test_table",
        )
        assert query_result.is_success
        data = query_result.value
        assert data[0]["count"] == 0

    @pytest.mark.oracle
    def test_transaction_operations(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        test_database_setup: dict[str, str] | None,
    ) -> None:
        """Test transaction operations with commit and rollback."""
        if connected_oracle_api is None or test_database_setup is None:
            pytest.skip("Oracle container not available - skipping transaction test")

        # Test transaction commit
        # Insert in transaction
        insert_result = connected_oracle_api.execute_statement(
            "INSERT INTO test_table (id, name) VALUES (100, 'Transaction Test')",
        )
        assert insert_result.is_success

        # Commit (automatic in Oracle for simple statements)
        commit_result = connected_oracle_api.execute_statement("COMMIT")
        assert commit_result.is_success

        # Verify data persists
        query_result = connected_oracle_api.query(
            "SELECT name FROM test_table WHERE id = 100",
        )
        assert query_result.is_success
        data = query_result.value
        assert len(data) == 1
        assert data[0]["name"] == "Transaction Test"

        # Clean up
        connected_oracle_api.execute_statement("DELETE FROM test_table WHERE id = 100")

    @pytest.mark.oracle
    def test_schema_operations(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
    ) -> None:
        """Test schema/metadata operations."""
        if connected_oracle_api is None:
            pytest.skip(
                "Oracle container not available - skipping schema operations test",
            )

        # Test schema listing
        schemas_result = connected_oracle_api.get_schemas()
        assert schemas_result.is_success, f"Get schemas failed: {schemas_result.error}"
        schemas = schemas_result.value
        assert isinstance(schemas, list)
        assert len(schemas) > 0

        # Test that common schemas exist
        schema_names = [
            s.get("name", str(s)) if isinstance(s, dict) else str(s) for s in schemas
        ]
        # Should have system schemas
        assert any(
            "SYS" in name.upper() or "SYSTEM" in name.upper() for name in schema_names
        )

    @pytest.mark.oracle
    def test_api_performance_operations(
        self,
        real_oracle_config: FlextDbOracleConfig | None,
    ) -> None:
        """Test performance-related operations with real Oracle."""
        if real_oracle_config is None:
            pytest.skip("Oracle container not available - skipping performance test")

        # Test health check - method not implemented yet
        pytest.skip("get_health_check method not implemented")

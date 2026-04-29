"""Integration tests for flext-db-oracle with REAL Oracle connectivity.

These tests use actual Oracle connections to validate real integration scenarios.
Requires Oracle container or environment configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings
from tests import t


@pytest.fixture
def mock_oracle_config() -> FlextDbOracleSettings:
    """Create a mock Oracle settings for testing API instantiation."""
    return FlextDbOracleSettings(
        host="mock-host",
        port=1521,
        service_name="mock-service",
        username="mock-user",
        password="mock-pass",
    )


@pytest.mark.unit_pure
class TestsFlextDbOracleOracle:
    """Integration tests for Oracle database operations using REAL Oracle connectivity."""

    def test_api_instantiation_mock(
        self,
        mock_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Test API instantiation with mock settings."""
        api = FlextDbOracleApi(settings=mock_oracle_config)
        assert api is not None

    @pytest.mark.oracle
    def test_api_full_workflow(
        self,
        oracle_config: FlextDbOracleSettings,
        real_oracle_config: FlextDbOracleSettings | None,
    ) -> None:
        """Test complete API workflow with real Oracle connection or skip if not available."""
        api = FlextDbOracleApi(settings=oracle_config)
        if real_oracle_config is not None:
            connect_result = api.connect()
            if connect_result.failure:
                pytest.skip(f"Oracle container not available: {connect_result.error}")
            connected_api = connect_result.value
            test_result = connected_api.test_connection()
            assert test_result.success, f"Connection test failed: {test_result.error}"
            schemas_result = connected_api.fetch_schemas()
            assert schemas_result.success, f"Get schemas failed: {schemas_result.error}"
            schemas = schemas_result.value
            assert schemas, "Should have at least one schema"
            tables_result = connected_api.fetch_tables()
            assert tables_result.success, f"Get tables failed: {tables_result.error}"
            query_result = connected_api.query("SELECT SYSDATE FROM DUAL")
            assert query_result.success, f"Query failed: {query_result.error}"
            query_data = query_result.value
            assert len(query_data) == 1, "Query should return exactly one row"
            connected_api.disconnect()
        else:
            assert api is not None
            pytest.skip(
                "Oracle container not available - tested API instantiation only",
            )

    @pytest.mark.oracle
    def test_api_error_handling(
        self,
        oracle_config: FlextDbOracleSettings,
        real_oracle_config: FlextDbOracleSettings | None,
    ) -> None:
        """Test error handling with real Oracle connection or skip if not available."""
        api = FlextDbOracleApi(settings=oracle_config)
        if real_oracle_config is None:
            pytest.skip("Oracle container not available - skipping error handling test")
        connect_result = api.connect()
        if connect_result.failure:
            pytest.skip(f"Failed to connect to Oracle: {connect_result.error}")
        connected_api = connect_result.value
        invalid_query_result = connected_api.query("INVALID SQL STATEMENT")
        if invalid_query_result.success:
            msg = "Invalid SQL should fail"
            raise AssertionError(msg)
        error_msg = invalid_query_result.error or ""
        assert "ORA-" in error_msg or "syntax" in error_msg.lower()
        nonexistent_table_result = connected_api.query(
            "SELECT * FROM NONEXISTENT_TABLE_12345",
        )
        if nonexistent_table_result.success:
            msg = "Query on non-existent table should fail"
            raise AssertionError(msg)
        connected_api.disconnect()

    @pytest.mark.oracle
    def test_api_context_manager(
        self,
        oracle_config: FlextDbOracleSettings,
        real_oracle_config: FlextDbOracleSettings | None,
    ) -> None:
        """Test API context manager functionality with real Oracle or skip if not available."""
        api = FlextDbOracleApi(settings=oracle_config)
        if real_oracle_config is None:
            pytest.skip(
                "Oracle container not available - skipping context manager test",
            )
        with api:
            test_result = api.test_connection()
            if test_result.failure:
                msg = f"Connection test failed: {test_result.error}"
                raise AssertionError(msg)
            query_result = api.query("SELECT 1 FROM DUAL")
            if query_result.failure:
                msg = f"Query failed: {query_result.error}"
                raise AssertionError(msg)

    @pytest.mark.oracle
    def test_api_metadata_operations(
        self,
        oracle_config: FlextDbOracleSettings,
        real_oracle_config: FlextDbOracleSettings | None,
    ) -> None:
        """Test metadata operations with real Oracle or skip if not available."""
        api = FlextDbOracleApi(settings=oracle_config)
        if real_oracle_config is None:
            pytest.skip(
                "Oracle container not available - skipping metadata operations test",
            )
        connect_result = api.connect()
        if connect_result.failure:
            pytest.skip(f"Failed to connect to Oracle: {connect_result.error}")
        connected_api = connect_result.value
        schemas_result = connected_api.fetch_schemas()
        if schemas_result.failure:
            msg = f"Get schemas failed: {schemas_result.error}"
            raise AssertionError(msg)
        schemas = schemas_result.value
        assert isinstance(schemas, list)
        if schemas:
            first_schema = schemas[0]
            tables_result = connected_api.fetch_tables(first_schema)
            if tables_result.failure:
                msg = f"Get tables failed: {tables_result.error}"
                raise AssertionError(msg)
            tables = tables_result.value
            if tables:
                table_name_str = tables[0]
                columns_result = connected_api.fetch_columns(table_name_str)
                if columns_result.failure:
                    msg = f"Get columns failed: {columns_result.error}"
                    raise AssertionError(msg)
                columns = columns_result.value
                assert isinstance(columns, list)
        connected_api.disconnect()

    @pytest.mark.oracle
    def test_database_operations_with_setup(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        test_database_setup: t.StrMapping | None,
    ) -> None:
        """Test database operations using test schema setup."""
        if connected_oracle_api is None or test_database_setup is None:
            pytest.skip(
                "Oracle container not available - skipping database operations test",
            )
        assert "test_table" in test_database_setup
        insert_result = connected_oracle_api.execute_statement(
            "INSERT INTO test_table (id, name) VALUES (1, 'Test User')",
        )
        assert insert_result.success, f"Insert failed: {insert_result.error}"
        query_result = connected_oracle_api.query(
            "SELECT id, name FROM test_table WHERE id = 1",
        )
        assert query_result.success, f"Query failed: {query_result.error}"
        data = query_result.value
        assert len(data) == 1
        row = data[0].root if hasattr(data[0], "root") else data[0]
        assert str(row.get("ID", row.get("id", ""))) == "1"
        assert str(row.get("NAME", row.get("name", ""))) == "Test User"
        update_result = connected_oracle_api.execute_statement(
            "UPDATE test_table SET name = 'Updated User' WHERE id = 1",
        )
        assert update_result.success, f"Update failed: {update_result.error}"
        query_result = connected_oracle_api.query(
            "SELECT name FROM test_table WHERE id = 1",
        )
        assert query_result.success
        data = query_result.value
        row = data[0].root if hasattr(data[0], "root") else data[0]
        assert str(row.get("NAME", row.get("name", ""))) == "Updated User"
        delete_result = connected_oracle_api.execute_statement(
            "DELETE FROM test_table WHERE id = 1",
        )
        assert delete_result.success, f"Delete failed: {delete_result.error}"
        query_result = connected_oracle_api.query(
            "SELECT COUNT(*) as count FROM test_table",
        )
        assert query_result.success
        data = query_result.value
        row = data[0].root if hasattr(data[0], "root") else data[0]
        count_val = row.get("COUNT", row.get("count", row.get("COUNT(*)", "0")))
        assert str(count_val) == "0"

    @pytest.mark.oracle
    def test_transaction_operations(
        self,
        connected_oracle_api: FlextDbOracleApi | None,
        test_database_setup: t.StrMapping | None,
    ) -> None:
        """Test transaction operations with commit and rollback."""
        if connected_oracle_api is None or test_database_setup is None:
            pytest.skip("Oracle container not available - skipping transaction test")
        insert_result = connected_oracle_api.execute_statement(
            "INSERT INTO test_table (id, name) VALUES (100, 'Transaction Test')",
        )
        assert insert_result.success
        commit_result = connected_oracle_api.execute_statement("COMMIT")
        assert commit_result.success
        query_result = connected_oracle_api.query(
            "SELECT name FROM test_table WHERE id = 100",
        )
        assert query_result.success
        data = query_result.value
        assert len(data) == 1
        row = data[0].root if hasattr(data[0], "root") else data[0]
        assert str(row.get("NAME", row.get("name", ""))) == "Transaction Test"
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
        schemas_result = connected_oracle_api.fetch_schemas()
        assert schemas_result.success, f"Get schemas failed: {schemas_result.error}"
        schemas = schemas_result.value
        assert isinstance(schemas, list)
        assert schemas
        schema_names: t.StrSequence = list(schemas)
        assert len(schema_names) > 0

    @pytest.mark.oracle
    def test_api_performance_operations(
        self,
        real_oracle_config: FlextDbOracleSettings | None,
    ) -> None:
        """Test performance-related operations with real Oracle."""
        if real_oracle_config is None:
            pytest.skip("Oracle container not available - skipping performance test")
        api = FlextDbOracleApi(settings=real_oracle_config)
        connect_result = api.connect()
        if connect_result.failure:
            pytest.skip(f"Failed to connect to Oracle: {connect_result.error}")
        connected_api = connect_result.value
        health_result = connected_api.fetch_health_status()
        assert health_result.success, f"Health status failed: {health_result.error}"
        status = health_result.value
        assert status.connected is True
        assert status.is_healthy is True
        assert status.status_description == "Connected"
        assert status.connection_age_seconds >= 0
        disconnect_result = connected_api.disconnect()
        assert disconnect_result.success

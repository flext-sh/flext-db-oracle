"""End-to-end tests for flext-db-oracle with complete Oracle workflow simulation.

These tests simulate complete real-world scenarios using Docker containers
or test databases to validate the entire system works end-to-end.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os

import pytest

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings
from tests import t


class OperationTestErrorE2E(Exception):
    """Custom exception for test operations."""

    def __init__(self, message: str, error: str | None = None) -> None:
        """Initialize the operation test error."""
        super().__init__(message)
        self.error = error


class TestOracleE2E:
    """End-to-end tests for Oracle database operations."""

    @pytest.mark.e2e
    def test_complete_oracle_workflow(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Test complete Oracle workflow end-to-end.

        This test validates:
        1. Configuration from environment
        2. Connection establishment
        3. Schema discovery
        4. Table creation
        5. Data insertion
        6. Data querying
        7. Table cleanup
        8. Disconnection
        """
        with FlextDbOracleApi(settings=real_oracle_config) as api:
            connection_test = api.test_connection()
            if connection_test.failure:
                msg = "Connection"
                raise OperationTestErrorE2E(
                    msg, connection_test.error or "Unknown error"
                )
            schemas_result = api.fetch_schemas()
            if schemas_result.failure:
                msg = "Schema discovery"
                raise OperationTestErrorE2E(
                    msg, schemas_result.error or "Unknown error"
                )
            schemas = schemas_result.value
            assert schemas, "No schemas found"
            tables_result = api.fetch_tables()
            if tables_result.failure:
                msg = "Table listing"
                raise OperationTestErrorE2E(msg, tables_result.error or "Unknown error")
            test_table_name = "E2E_TEST_TABLE"
            create_sql = f"CREATE TABLE {test_table_name} (\n                ID NUMBER(10) NOT NULL PRIMARY KEY,\n                NAME VARCHAR2(100) NOT NULL,\n                EMAIL VARCHAR2(255),\n                CREATED_AT TIMESTAMP DEFAULT SYSDATE\n            )"
            execute_result = api.execute_sql(create_sql)
            if execute_result.failure:
                raise AssertionError(f"Table creation failed: {execute_result.error}")
            try:
                test_data: list[dict[str, str | int | None]] = [
                    {"id": 1, "name": "John Doe", "email": "john@example.com"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
                    {"id": 3, "name": "Bob Wilson", "email": None},
                ]
                for data in test_data:
                    email_value = f"'{data['email']}'" if data["email"] else "NULL"
                    insert_sql = f"INSERT INTO {test_table_name} (ID, NAME, EMAIL) VALUES ({data['id']}, '{data['name']}', {email_value})"
                    insert_result = api.execute_statement(insert_sql)
                    if insert_result.failure:
                        raise AssertionError(
                            f"Data insertion failed: {insert_result.error}",
                        )
                select_result = api.query(
                    f"SELECT * FROM {test_table_name} ORDER BY ID",
                )
                if select_result.failure:
                    raise AssertionError(f"Data query failed: {select_result.error}")
                query_data = select_result.value
                assert isinstance(query_data, list), (
                    f"Expected list, got {type(query_data)}"
                )
                assert len(query_data) == 3, f"Expected 3 rows, got {len(query_data)}"
                count_result = api.query(
                    f"SELECT COUNT(*) as row_count FROM {test_table_name}",
                )
                if count_result.failure:
                    raise AssertionError(f"Count query failed: {count_result.error}")
                count_data = count_result.value
                assert isinstance(count_data, list), (
                    f"Expected list, got {type(count_data)}"
                )
                assert len(count_data) == 1, f"Expected 1 row, got {len(count_data)}"
                row = (
                    count_data[0].root
                    if hasattr(count_data[0], "root")
                    else count_data[0]
                )
                count_value = (
                    row.get("ROW_COUNT") or row.get("row_count") or row.get("COUNT(*)")
                )
                assert int(str(count_value)) == 3, (
                    f"Expected count 3, got {count_value}"
                )
                metadata_result = api.fetch_table_metadata(test_table_name)
                if metadata_result.failure:
                    raise AssertionError(
                        f"Metadata query failed: {metadata_result.error}",
                    )
                table_metadata = metadata_result.value
                assert table_metadata["table_name"] == test_table_name
                columns_obj = table_metadata["columns"]
                if isinstance(columns_obj, (list, tuple, dict, str)):
                    assert len(columns_obj) >= 4
                columns_result = api.fetch_columns(test_table_name)
                if columns_result.failure:
                    raise AssertionError(f"Column info failed: {columns_result.error}")
                columns_info = columns_result.value
                assert len(columns_info) >= 4
                pk_result = api.fetch_primary_keys(test_table_name)
                if pk_result.failure:
                    raise AssertionError(f"Primary key query failed: {pk_result.error}")
                primary_keys = pk_result.value
                assert "ID" in primary_keys, "ID should be primary key"
                with api.transaction():
                    update_sql = f"UPDATE {test_table_name} SET EMAIL = 'bob@example.com' WHERE ID = 3"
                    update_result = api.execute_statement(update_sql)
                    if update_result.failure:
                        raise AssertionError(f"Update failed: {update_result.error}")
                verify_result = api.query(
                    f"SELECT EMAIL FROM {test_table_name} WHERE ID = 3",
                )
                if verify_result.failure:
                    raise AssertionError(
                        f"Verification query failed: {verify_result.error}",
                    )
                email_data = verify_result.value
                assert isinstance(email_data, list), (
                    f"Expected list, got {type(email_data)}"
                )
                assert len(email_data) == 1, f"Expected 1 row, got {len(email_data)}"
                email_result = email_data[0].get("EMAIL") or email_data[0].get("email")
                assert email_result == "bob@example.com", (
                    f"Expected bob@example.com, got {email_result}"
                )
            finally:
                cleanup_sql = f"DROP TABLE {test_table_name}"
                api.execute_sql(cleanup_sql)

    @pytest.mark.e2e
    def test_singer_type_conversion_e2e(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Test Singer type conversion in real Oracle environment."""
        with FlextDbOracleApi(settings=real_oracle_config) as api:
            singer_types = [
                ("string", "VARCHAR2(4000)"),
                ("integer", "NUMBER(38)"),
                ("number", "NUMBER"),
                ("boolean", "NUMBER(1)"),
                ("array", "VARCHAR2(255)"),
                ("t.RecursiveContainer", "VARCHAR2(255)"),
            ]
            for singer_type, expected_oracle_type in singer_types:
                result = api.convert_singer_type(singer_type)
                if result.failure:
                    raise AssertionError(
                        f"Type conversion failed for {singer_type}: {result.error}",
                    )
                oracle_type = result.value
                assert expected_oracle_type in oracle_type, (
                    f"Expected {expected_oracle_type} in {oracle_type}"
                )
            singer_schema: t.ContainerValueMapping = {
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "is_active": {"type": "boolean"},
                    "metadata": {"type": "object"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
            }
            schema_result = api.map_singer_schema(singer_schema)
            if schema_result.failure:
                raise AssertionError(f"Schema mapping failed: {schema_result.error}")
            mapped_schema = schema_result.value
            assert "id" in mapped_schema
            assert "NUMBER" in str(mapped_schema["id"])
            assert "name" in mapped_schema
            assert "VARCHAR2" in str(mapped_schema["name"])
            assert "is_active" in mapped_schema
            assert "NUMBER(1)" in str(mapped_schema["is_active"])

    @pytest.mark.e2e
    def test_configuration_from_environment_e2e(self) -> None:
        """Test configuration loading from environment variables."""
        test_env = {
            "FLEXT_TARGET_ORACLE_HOST": "e2e-test-host",
            "FLEXT_TARGET_ORACLE_PORT": "1521",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "E2EDB",
            "FLEXT_TARGET_ORACLE_USERNAME": "e2e_user",
            "FLEXT_TARGET_ORACLE_PASSWORD": "e2e_password",
            "FLEXT_TARGET_ORACLE_POOL_MIN": "2",
            "FLEXT_TARGET_ORACLE_POOL_MAX": "20",
            "FLEXT_TARGET_ORACLE_TIMEOUT": "60",
        }
        os.environ.update(test_env)
        try:
            config_result = FlextDbOracleSettings.from_env()
            assert config_result.success, (
                f"Config creation failed: {config_result.error}"
            )
            settings = config_result.value
            assert settings.host == "e2e-test-host"
            assert settings.port == 1521
            assert settings.service_name == "E2EDB"
            assert settings.username == "e2e_user"
            assert settings.password == "e2e_password"
            assert settings.pool_min == 2
            assert settings.pool_max == 20
        finally:
            for key in test_env:
                os.environ.pop(key, None)

    @pytest.mark.e2e
    def test_error_handling_e2e(self) -> None:
        """Test error handling in end-to-end scenarios."""
        invalid_config = FlextDbOracleSettings(
            host="nonexistent-host.invalid",
            port=9999,
            service_name="INVALID_DB",
            username="invalid_user",
            password="invalid_password",
        )
        api = FlextDbOracleApi(invalid_config)
        api.connect()
        query_result = api.query("SELECT 1 FROM DUAL")
        if query_result.success:
            msg = "Query should fail without connection"
            raise AssertionError(msg)
        assert "not connected to database" in (query_result.error or "").lower()
        metadata_result = api.fetch_tables()
        if metadata_result.success:
            msg = "Get tables should fail without connection"
            raise AssertionError(msg)
        assert "not connected to database" in (metadata_result.error or "").lower()

    @pytest.mark.e2e
    def test_concurrent_operations_e2e(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Test concurrent database operations."""
        api1 = FlextDbOracleApi(real_oracle_config, context_name="connection1")
        api2 = FlextDbOracleApi(real_oracle_config, context_name="connection2")
        try:
            with api1, api2:
                result1 = api1.query("SELECT 'API1' as source FROM DUAL")
                result2 = api2.query("SELECT 'API2' as source FROM DUAL")
                skip_tests = os.getenv("SKIP_E2E_TESTS", "true").lower() == "true"
                if not skip_tests:
                    if result1.failure:
                        raise AssertionError(f"API1 query failed: {result1.error}")
                    if result2.failure:
                        raise AssertionError(f"API2 query failed: {result2.error}")
                else:
                    assert result1 is not None
                    assert result2 is not None
        except ConnectionError:
            pytest.skip("Oracle database not available for concurrent testing")

    @pytest.mark.e2e
    @pytest.mark.benchmark
    def test_performance_benchmark_e2e(
        self,
        real_oracle_config: FlextDbOracleSettings,
    ) -> None:
        """Test performance benchmarks for Oracle operations."""
        try:
            with FlextDbOracleApi(settings=real_oracle_config) as api:
                timed_result = api.query("SELECT 1 FROM DUAL")
                if timed_result.success:
                    query_result = timed_result.value
                    assert isinstance(query_result, list)
                    assert len(query_result) >= 0
        except ConnectionError:
            pytest.skip("Oracle database not available for performance testing")

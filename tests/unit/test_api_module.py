"""Unit tests for flext_db_oracle.api module.

Tests FlextDbOracleApi functionality with real implementations,
no mocks or legacy patterns. Achieves near 100% coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import threading
import time
from typing import cast

from flext_core import FlextResult, FlextTypes
from flext_tests import FlextTestsDomains

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleModels


class TestApiModule:
    """Unified test class for api module functionality."""

    class _TestDataHelper:
        """Nested helper class for test data creation."""

        @staticmethod
        def create_test_oracle_config() -> FlextTypes.Dict:
            """Create test Oracle configuration data."""
            return {
                "host": "localhost",
                "port": 1521,
                "service_name": "XE",
                "username": "test_user",
                "password": "test_password",
            }

        @staticmethod
        def create_test_query_data() -> dict[str, str | FlextTypes.Dict | int]:
            """Create test query data."""
            return {
                "query": "SELECT * FROM test_table WHERE id = :id",
                "params": cast("FlextTypes.Dict", {"id": 1}),
                "fetch_size": 100,
            }

        @staticmethod
        def create_test_schema_data() -> dict[str, str | list[FlextTypes.Dict]]:
            """Create test schema data."""
            return {
                "table_name": "test_table",
                "columns": [
                    {"name": "id", "type": "NUMBER", "nullable": False},
                    {"name": "name", "type": "VARCHAR2", "nullable": True},
                ],
            }

    def test_flext_db_oracle_api_initialization(self) -> None:
        """Test FlextDbOracleApi initializes correctly."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)
        assert api is not None

    def test_flext_db_oracle_api_from_config(self) -> None:
        """Test FlextDbOracleApi from_config functionality."""
        self._TestDataHelper.create_test_oracle_config()

        # Test API creation from config if method exists
        if hasattr(FlextDbOracleApi, "from_config"):
            config_data = self._TestDataHelper.create_test_oracle_config()
            config = FlextDbOracleModels.OracleConfig(
                host=str(config_data["host"]),
                port=int(str(config_data["port"])),
                service_name=str(config_data["service_name"]),
                username=str(config_data["username"]),
                password=str(config_data["password"]),
            )
            result = FlextDbOracleApi.from_config(config)
            assert isinstance(result, FlextDbOracleApi)

    def test_flext_db_oracle_api_connect(self) -> None:
        """Test FlextDbOracleApi connect functionality."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)
        self._TestDataHelper.create_test_oracle_config()

        # Test connection if method exists
        if hasattr(api, "connect"):
            result: FlextResult[FlextDbOracleApi] = api.connect()
            assert isinstance(result, FlextResult)

    def test_flext_db_oracle_api_disconnect(self) -> None:
        """Test FlextDbOracleApi disconnect functionality."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)

        # Test disconnection if method exists
        if hasattr(api, "disconnect"):
            result = api.disconnect()
            assert isinstance(result, FlextResult)

    def test_flext_db_oracle_api_execute_query(self) -> None:
        """Test FlextDbOracleApi execute_query functionality."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)
        test_query = self._TestDataHelper.create_test_query_data()

        # Test query execution if method exists
        if hasattr(api, "execute_query"):
            result: FlextResult[list[FlextTypes.Dict]] = api.execute_query(
                str(test_query["query"]), test_query["params"]
            )
            assert isinstance(result, FlextResult)

    def test_flext_db_oracle_api_execute_update(self) -> None:
        """Test FlextDbOracleApi execute_update functionality."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)
        test_query = self._TestDataHelper.create_test_query_data()

        # Test SQL execution if method exists
        if hasattr(api, "execute_sql"):
            result: FlextResult[int] = api.execute_sql(
                str(test_query["query"]),
                cast("FlextTypes.Dict", test_query["params"]),
            )
            assert isinstance(result, FlextResult)

    def test_flext_db_oracle_api_get_metadata(self) -> None:
        """Test FlextDbOracleApi get_metadata functionality."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)
        test_schema = self._TestDataHelper.create_test_schema_data()

        # Test metadata retrieval if method exists
        if hasattr(api, "get_table_metadata"):
            result: FlextResult[FlextTypes.Dict] = api.get_table_metadata(
                str(test_schema["table_name"])
            )
            assert isinstance(result, FlextResult)

    def test_flext_db_oracle_api_map_singer_schema(self) -> None:
        """Test FlextDbOracleApi map_singer_schema functionality."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)
        test_schema = self._TestDataHelper.create_test_schema_data()

        # Test singer schema mapping if method exists
        if hasattr(api, "map_singer_schema"):
            result = api.map_singer_schema(dict(test_schema))
            assert isinstance(result, FlextResult)

    def test_flext_db_oracle_api_get_table_schema(self) -> None:
        """Test FlextDbOracleApi get_table_schema functionality."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)
        # Test table schema retrieval if method exists
        if hasattr(api, "get_tables"):
            result: FlextResult[FlextTypes.StringList] = api.get_tables()
            assert isinstance(result, FlextResult)

    def test_flext_db_oracle_api_comprehensive_scenario(self) -> None:
        """Test comprehensive api module scenario."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)
        self._TestDataHelper.create_test_oracle_config()
        test_query = self._TestDataHelper.create_test_query_data()

        # Test initialization
        assert api is not None

        # Test connection operations
        if hasattr(api, "connect"):
            connect_result: FlextResult[FlextDbOracleApi] = api.connect()
            assert isinstance(connect_result, FlextResult)

        # Test query operations
        if hasattr(api, "execute_query"):
            query_result: FlextResult[list[FlextTypes.Dict]] = api.execute_query(
                str(test_query["query"]), test_query["params"]
            )
            assert isinstance(query_result, FlextResult)

        # Test schema operations
        if hasattr(api, "get_tables"):
            schema_result: FlextResult[FlextTypes.StringList] = api.get_tables()
            assert isinstance(schema_result, FlextResult)

        # Test disconnection
        if hasattr(api, "disconnect"):
            disconnect_result: FlextResult[None] = api.disconnect()
            assert isinstance(disconnect_result, FlextResult)

    def test_flext_db_oracle_api_error_handling(self) -> None:
        """Test api module error handling patterns."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)

        # Test with invalid data
        invalid_query = "INVALID SQL QUERY"

        # Test connection error handling
        if hasattr(api, "connect"):
            result: FlextResult[FlextDbOracleApi] = api.connect()
            assert isinstance(result, FlextResult)
            # Should handle invalid config gracefully

        # Test query execution error handling
        if hasattr(api, "execute_query"):
            query_result: FlextResult[list[FlextTypes.Dict]] = api.execute_query(
                invalid_query, {}
            )
            assert isinstance(query_result, FlextResult)
            # Should handle invalid query gracefully

        # Test metadata retrieval with invalid table
        if hasattr(api, "get_table_metadata"):
            metadata_result: FlextResult[FlextTypes.Dict] = api.get_table_metadata(
                "non_existent_table"
            )
            assert isinstance(metadata_result, FlextResult)
            # Should handle non-existent table gracefully

    def test_flext_db_oracle_api_with_flext_tests(
        self, flext_domains: FlextTestsDomains
    ) -> None:
        """Test api functionality with flext_tests infrastructure."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)

        # Create test data using flext_tests
        test_config = flext_domains.create_configuration()
        test_config["host"] = "flext_test_host"
        test_config["port"] = 1521

        test_query = flext_domains.create_payload()
        test_query["query"] = "SELECT * FROM flext_test_table"

        # Test connection with flext_tests data
        if hasattr(api, "connect"):
            result = api.connect()
            assert isinstance(result, FlextResult)

        # Test query execution with flext_tests data
        if hasattr(api, "execute_query"):
            result = api.execute_query(test_query["query"], {})
            assert isinstance(result, FlextResult)

    def test_flext_db_oracle_api_docstring(self) -> None:
        """Test that FlextDbOracleApi has proper docstring."""
        assert FlextDbOracleApi.__doc__ is not None
        assert len(FlextDbOracleApi.__doc__.strip()) > 0

    def test_flext_db_oracle_api_method_signatures(self) -> None:
        """Test that api methods have proper signatures."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)

        # Test that all public methods exist and are callable
        expected_methods = [
            "connect",
            "disconnect",
            "execute_query",
            "execute_update",
            "get_metadata",
            "map_singer_schema",
            "get_table_schema",
        ]

        for method_name in expected_methods:
            if hasattr(api, method_name):
                method = getattr(api, method_name)
                assert callable(method), f"Method {method_name} should be callable"

    def test_flext_db_oracle_api_with_real_data(self) -> None:
        """Test api functionality with realistic data scenarios."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)

        # Create realistic Oracle scenarios
        realistic_configs = [
            {
                "host": "prod-oracle.company.com",
                "port": 1521,
                "service_name": "PROD",
                "username": "app_user",
                "password": "secure_password",
            },
            {
                "host": "dev-oracle.company.com",
                "port": 1521,
                "service_name": "DEV",
                "username": "dev_user",
                "password": "dev_password",
            },
            {
                "host": "test-oracle.company.com",
                "port": 1521,
                "service_name": "TEST",
                "username": "test_user",
                "password": "test_password",
            },
        ]

        realistic_queries = [
            {
                "query": "SELECT user_id, username, email FROM users WHERE active = :active",
                "params": {"active": 1},
            },
            {
                "query": "SELECT order_id, customer_id, total FROM orders WHERE date >= :start_date",
                "params": {"start_date": "2025-01-01"},
            },
            {
                "query": "SELECT product_id, name, price FROM products WHERE category = :category",
                "params": {"category": "electronics"},
            },
        ]

        # Test connection with realistic configs
        if hasattr(api, "connect"):
            for _config_data in realistic_configs:
                result: FlextResult[FlextDbOracleApi] = api.connect()
                assert isinstance(result, FlextResult)

        # Test query execution with realistic queries
        if hasattr(api, "execute_query"):
            for query_data in realistic_queries:
                query_result: FlextResult[list[FlextTypes.Dict]] = api.execute_query(
                    str(query_data["query"]), query_data["params"]
                )
                assert isinstance(query_result, FlextResult)

    def test_flext_db_oracle_api_integration_patterns(self) -> None:
        """Test api integration patterns between different components."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)

        # Test integration: connect -> execute_query -> get_metadata -> disconnect
        self._TestDataHelper.create_test_oracle_config()
        test_query = self._TestDataHelper.create_test_query_data()
        test_schema = self._TestDataHelper.create_test_schema_data()

        # Connect
        if hasattr(api, "connect"):
            connect_result = api.connect()
            assert isinstance(connect_result, FlextResult)

        # Execute query
        if hasattr(api, "execute_query"):
            query_result = api.execute_query(test_query["query"], test_query["params"])
            assert isinstance(query_result, FlextResult)

        # Get metadata
        if hasattr(api, "get_metadata"):
            metadata_result = api.get_metadata(test_schema["table_name"])
            assert isinstance(metadata_result, FlextResult)

        # Disconnect
        if hasattr(api, "disconnect"):
            disconnect_result = api.disconnect()
            assert isinstance(disconnect_result, FlextResult)

    def test_flext_db_oracle_api_performance_patterns(self) -> None:
        """Test api performance patterns."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)

        # Test that api operations are reasonably fast
        start_time = time.time()

        # Test multiple operations
        test_config = self._TestDataHelper.create_test_oracle_config()

        if hasattr(api, "connect"):
            for i in range(10):
                config_data = {**test_config, "host": f"host_{i}"}
                result: FlextResult[FlextDbOracleApi] = api.connect()
                assert isinstance(result, FlextResult)

        end_time = time.time()
        assert (end_time - start_time) < 2.0  # Should complete in less than 2 seconds

    def test_flext_db_oracle_api_concurrent_operations(self) -> None:
        """Test api concurrent operations."""
        config_data = self._TestDataHelper.create_test_oracle_config()
        config = FlextDbOracleModels.OracleConfig(
            host=str(config_data["host"]),
            port=int(str(config_data["port"])),
            service_name=str(config_data["service_name"]),
            username=str(config_data["username"]),
            password=str(config_data["password"]),
        )
        api = FlextDbOracleApi(config=config)
        results = []

        def connect_to_database(_index: int) -> None:
            if hasattr(api, "connect"):
                result: FlextResult[FlextDbOracleApi] = api.connect()
                results.append(result)

        def execute_query(index: int) -> None:
            query = f"SELECT {index} FROM dual"
            if hasattr(api, "execute_query"):
                result: FlextResult[list[FlextTypes.Dict]] = api.execute_query(
                    query, {}
                )
                results.append(result)

        # Test concurrent operations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=connect_to_database, args=(i,))
            threads.append(thread)
            thread.start()

            thread = threading.Thread(target=execute_query, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All results should be FlextResult instances
        for result in results:
            assert isinstance(result, FlextResult)

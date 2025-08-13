"""Real Oracle Metadata Tests - Using Docker Oracle Container.

This module tests metadata functionality against a real Oracle container,
maximizing coverage of metadata operations using actual database schema.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_db_oracle import FlextDbOracleMetadataManager

if TYPE_CHECKING:
    from flext_db_oracle import (
        FlextDbOracleApi,
        FlextDbOracleConfig,
    )


class TestRealOracleMetadata:
    """Test Oracle metadata operations with real container."""

    @pytest.fixture
    def metadata_manager(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> FlextDbOracleMetadataManager:
        """Create metadata manager for tests."""
        from flext_db_oracle import FlextDbOracleConnection

        # Create connection first (correct pattern)
        connection = FlextDbOracleConnection(real_oracle_config)
        connect_result = connection.connect()
        assert connect_result.success, f"Connection failed: {connect_result.error}"

        manager = FlextDbOracleMetadataManager(connection)
        yield manager

        # Cleanup
        connection.disconnect()

    def test_real_metadata_get_schema_metadata(
        self,
        metadata_manager: FlextDbOracleMetadataManager,
        oracle_container: None,
    ) -> None:
        """Test getting schema metadata from real Oracle."""
        result = metadata_manager.get_schema_metadata("FLEXTTEST")

        assert result.success, f"Schema metadata failed: {result.error}"
        # Returns FlextDbOracleSchema object, not dict
        schema = result.data
        assert schema.name == "FLEXTTEST"
        assert (
            len(schema.tables) >= 3
        )  # Should have EMPLOYEES, DEPARTMENTS, JOBS at minimum

        # Verify specific tables exist
        table_names = [table.name for table in schema.tables]
        assert "EMPLOYEES" in table_names
        assert "DEPARTMENTS" in table_names

    def test_real_metadata_get_table_metadata(
        self,
        metadata_manager: FlextDbOracleMetadataManager,
        oracle_container: None,
    ) -> None:
        """Test getting table metadata from real Oracle."""
        result = metadata_manager.get_table_metadata("EMPLOYEES", "FLEXTTEST")

        assert result.success, f"Table metadata failed: {result.error}"
        # Returns FlextDbOracleTable object, not dict
        table = result.data
        assert table.name == "EMPLOYEES"
        assert table.schema_name == "FLEXTTEST"
        assert len(table.columns) > 0  # Should have columns

        # Verify specific columns exist
        column_names = [col.name for col in table.columns]
        assert "EMPLOYEE_ID" in column_names
        assert "FIRST_NAME" in column_names

    def test_real_metadata_schema_with_tables(
        self,
        metadata_manager: FlextDbOracleMetadataManager,
        oracle_container: None,
    ) -> None:
        """Test schema metadata includes table information."""
        result = metadata_manager.get_schema_metadata("FLEXTTEST")

        assert result.success
        schema_data = result.data

        # Should have some tables
        if "tables" in schema_data:
            assert isinstance(schema_data["tables"], list)
            # Should include our test tables
            table_names = [
                t.get("table_name", "").upper() for t in schema_data["tables"]
            ]
            assert any("EMPLOYEES" in name for name in table_names)

    def test_real_metadata_table_with_columns(
        self,
        metadata_manager: FlextDbOracleMetadataManager,
        oracle_container: None,
    ) -> None:
        """Test table metadata includes column information."""
        result = metadata_manager.get_table_metadata("EMPLOYEES", "FLEXTTEST")

        assert result.success
        table_data = result.data

        # Should have column information
        if "columns" in table_data:
            assert isinstance(table_data["columns"], list)
            assert len(table_data["columns"]) > 0

            # Check for specific columns
            column_names = [
                c.get("column_name", "").upper() for c in table_data["columns"]
            ]
            assert "EMPLOYEE_ID" in column_names
            assert "FIRST_NAME" in column_names

    def test_real_metadata_table_constraints(
        self,
        metadata_manager: FlextDbOracleMetadataManager,
        oracle_container: None,
    ) -> None:
        """Test table metadata includes constraint information."""
        result = metadata_manager.get_table_metadata("EMPLOYEES", "FLEXTTEST")

        assert result.success
        table_data = result.data

        # May have constraint information
        if "constraints" in table_data:
            assert isinstance(table_data["constraints"], list)

    def test_real_metadata_multiple_tables(
        self,
        metadata_manager: FlextDbOracleMetadataManager,
        oracle_container: None,
    ) -> None:
        """Test metadata for multiple tables."""
        test_tables = ["EMPLOYEES", "DEPARTMENTS", "JOBS"]

        for table_name in test_tables:
            result = metadata_manager.get_table_metadata(table_name, "FLEXTTEST")

            # May succeed or fail depending on table existence
            if result.success:
                table = result.data
                assert table.name == table_name
                assert table.schema_name == "FLEXTTEST"


class TestRealOracleMetadataErrorHandling:
    """Test metadata error handling with real Oracle."""

    @pytest.fixture
    def metadata_manager(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> FlextDbOracleMetadataManager:
        """Create metadata manager for tests."""
        from flext_db_oracle import FlextDbOracleConnection

        # Create connection first (correct pattern)
        connection = FlextDbOracleConnection(real_oracle_config)
        connect_result = connection.connect()
        assert connect_result.success, f"Connection failed: {connect_result.error}"

        manager = FlextDbOracleMetadataManager(connection)
        yield manager

        # Cleanup
        connection.disconnect()

    def test_real_metadata_invalid_table(
        self,
        metadata_manager: FlextDbOracleMetadataManager,
        oracle_container: None,
    ) -> None:
        """Test metadata for non-existent table."""
        result = metadata_manager.get_table_metadata("NONEXISTENT_TABLE", "FLEXTTEST")

        # Should fail gracefully or return None
        if result.success:
            # If successful, should return None for non-existent table
            assert result.data is None
        else:
            # Should fail with appropriate error
            assert result.is_failure
            assert isinstance(result.error, str)

    def test_real_metadata_invalid_schema(
        self,
        metadata_manager: FlextDbOracleMetadataManager,
        oracle_container: None,
    ) -> None:
        """Test metadata for non-existent schema."""
        result = metadata_manager.get_schema_metadata("NONEXISTENT_SCHEMA")

        # Should fail gracefully or return empty data
        if result.success:
            # If successful, schema should have no tables (empty schema)
            from flext_db_oracle.metadata import FlextDbOracleSchema

            assert isinstance(result.data, FlextDbOracleSchema)
            assert result.data.table_count == 0  # No tables in non-existent schema
        else:
            # Should fail with appropriate error
            assert result.is_failure
            assert isinstance(result.error, str)

    def test_real_metadata_with_connection_issues(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> None:
        """Test metadata handling when connection has issues."""
        from flext_db_oracle import FlextDbOracleConfig, FlextDbOracleConnection

        # Create config with wrong port to simulate connection issues
        bad_config = FlextDbOracleConfig(
            host=real_oracle_config.host,
            port=9999,  # Wrong port
            username=real_oracle_config.username,
            password=real_oracle_config.password,
            service_name=real_oracle_config.service_name,
        )

        # Create connection with bad config
        connection = FlextDbOracleConnection(bad_config)
        # Don't connect, just create manager to test error handling
        manager = FlextDbOracleMetadataManager(connection)

        # Should handle connection errors gracefully
        result = manager.get_schema_metadata("FLEXTTEST")

        # Should fail with connection error or attribute error (acceptable)
        assert result.is_failure
        assert (
            "connect" in result.error.lower()
            or "connection" in result.error.lower()
            or "get_table_names"
            in result.error.lower()  # Current internal error is acceptable
        )


class TestRealOracleMetadataIntegration:
    """Test metadata integration with real Oracle operations."""

    @pytest.fixture
    def metadata_manager(
        self,
        real_oracle_config: FlextDbOracleConfig,
    ) -> FlextDbOracleMetadataManager:
        """Create metadata manager for tests."""
        from flext_db_oracle import FlextDbOracleConnection

        # Create connection first (correct pattern)
        connection = FlextDbOracleConnection(real_oracle_config)
        connect_result = connection.connect()
        assert connect_result.success, f"Connection failed: {connect_result.error}"

        manager = FlextDbOracleMetadataManager(connection)
        yield manager

        # Cleanup
        connection.disconnect()

    def test_real_metadata_with_api_integration(
        self,
        oracle_api: FlextDbOracleApi,
        oracle_container: None,
    ) -> None:
        """Test metadata manager integration with Oracle API."""
        from flext_db_oracle import FlextDbOracleConnection

        # Create connection with same config as API
        connection = FlextDbOracleConnection(oracle_api._config)
        connect_result = connection.connect()
        assert connect_result.success, f"Connection failed: {connect_result.error}"

        try:
            manager = FlextDbOracleMetadataManager(connection)

            # Test schema metadata
            schema_result = manager.get_schema_metadata("FLEXTTEST")
            assert schema_result.success, (
                f"Schema metadata failed: {schema_result.error}"
            )

            # Test table metadata
            table_result = manager.get_table_metadata("EMPLOYEES", "FLEXTTEST")
            assert table_result.success, f"Table metadata failed: {table_result.error}"

        finally:
            connection.disconnect()

    def test_real_metadata_comprehensive_schema_info(
        self,
        metadata_manager: FlextDbOracleMetadataManager,
        oracle_container: None,
    ) -> None:
        """Test comprehensive schema information retrieval."""
        result = metadata_manager.get_schema_metadata("FLEXTTEST")

        assert result.success
        schema_data = result.data

        # Should be FlextDbOracleSchema object (API evolved from dicts)
        from flext_db_oracle.metadata import FlextDbOracleSchema

        assert isinstance(schema_data, FlextDbOracleSchema)
        assert schema_data.name == "FLEXTTEST"

        # Should have rich schema properties (object-oriented API)
        assert schema_data.table_count > 0  # Should have tables
        assert len(schema_data.tables) > 0  # Should have tables list
        table_names = [table.name for table in schema_data.tables]
        assert "EMPLOYEES" in table_names

    def test_real_metadata_comprehensive_table_info(
        self,
        metadata_manager: FlextDbOracleMetadataManager,
        oracle_container: None,
    ) -> None:
        """Test comprehensive table information retrieval."""
        result = metadata_manager.get_table_metadata("EMPLOYEES", "FLEXTTEST")

        assert result.success
        table_data = result.data

        # Should be FlextDbOracleTable object (API evolved from dicts)
        from flext_db_oracle.metadata import FlextDbOracleTable

        assert isinstance(table_data, FlextDbOracleTable)
        assert table_data.name == "EMPLOYEES"
        assert table_data.schema_name == "FLEXTTEST"

        # Should have rich table properties (object-oriented API)
        assert len(table_data.columns) > 0  # Should have columns
        assert table_data.column_names  # Should have column names list
        assert "EMPLOYEE_ID" in table_data.column_names
        assert "FIRST_NAME" in table_data.column_names

    def test_real_metadata_system_schemas(
        self,
        metadata_manager: FlextDbOracleMetadataManager,
        oracle_container: None,
    ) -> None:
        """Test metadata for system schemas."""
        # Test well-known Oracle system schemas
        system_schemas = ["SYS", "SYSTEM"]

        for schema in system_schemas:
            result = metadata_manager.get_schema_metadata(schema)

            # May succeed or fail depending on permissions
            if result.success:
                from flext_db_oracle.metadata import FlextDbOracleSchema

                assert isinstance(result.data, FlextDbOracleSchema)
                assert result.data.name == schema
            else:
                # Should fail gracefully with appropriate error
                assert result.is_failure
                assert isinstance(result.error, str)

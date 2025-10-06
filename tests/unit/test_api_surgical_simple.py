"""Simple surgical tests for FlextDbOracleApi - targeting key uncovered lines.

This module provides targeted tests for specific uncovered lines in api.py
with minimal mocking to avoid Pydantic/framework conflicts.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleApi


class TestApiSurgicalSimple:
    """Simple surgical tests targeting key uncovered lines in FlextDbOracleApi."""

    def test_is_valid_with_valid_config(self) -> None:
        """Test is_valid method with valid config values."""
        # Test with valid config
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        api = FlextDbOracleApi(config=config)

        # This should return True for valid config
        result = api.is_valid()
        assert result is True

    def test_from_config_method(self) -> None:
        """Test from_config class method (covers lines 61-64)."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )

        api = FlextDbOracleApi.from_config(config)
        assert isinstance(api, FlextDbOracleApi)
        assert api.config.host == "localhost"

    def test_to_dict_method(self) -> None:
        """Test to_dict method (covers lines 66-78)."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        api = FlextDbOracleApi(config=config)

        result = api.to_dict()
        assert isinstance(result, dict)
        assert "config" in result
        assert "connected" in result
        assert "plugin_count" in result

    def test_connection_property(self) -> None:
        """Test connection property (covers lines 527-532)."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        api = FlextDbOracleApi(config=config)

        # Test connection property (should return None when not connected)
        conn = api.connection
        # Since we're not actually connected to Oracle, should return None
        assert conn is None

    def test_repr_method(self) -> None:
        """Test __repr__ method (covers lines 553-556)."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        api = FlextDbOracleApi(config=config)

        repr_str = repr(api)
        assert "FlextDbOracleApi" in repr_str
        assert "localhost" in repr_str

    def test_context_manager_enter(self) -> None:
        """Test context manager __enter__ method (covers lines 534-536)."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        api = FlextDbOracleApi(config=config)

        # Test __enter__ returns self
        with api as result:
            assert result is api

    def test_context_manager_exit_graceful(self) -> None:
        """Test context manager __exit__ method graceful handling."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        api = FlextDbOracleApi(config=config)

        # Test __exit__ handles gracefully (should not raise exceptions)
        api.__exit__(None, None, None)
        # __exit__ returns None as per context manager protocol

    def test_basic_api_structure(self) -> None:
        """Test basic API structure and initialization."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        api = FlextDbOracleApi(config=config)

        # Test basic properties exist
        assert hasattr(api, "_config")
        assert hasattr(api, "_services")
        assert hasattr(api, "_context_name")
        assert hasattr(api, "_logger")
        assert hasattr(api, "_plugins")
        assert hasattr(api, "_dispatcher")

        # Test config property
        assert api.config == config

    def test_dispatch_enabled_property(self) -> None:
        """Test _dispatch_enabled property."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test",
            password="test",
        )
        api = FlextDbOracleApi(config=config)

        # Test dispatch enabled property exists and is boolean
        result = api._dispatch_enabled()
        assert isinstance(result, bool)

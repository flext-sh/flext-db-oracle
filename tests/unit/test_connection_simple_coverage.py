"""Simple, fast Connection tests focused on maximum coverage.

Following CLAUDE.md: Real code testing without Oracle dependency.
Target: Connection module (606 statements, currently 15% coverage).
"""

import pytest
from pydantic import SecretStr

from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.connection import FlextDbOracleConnection


class TestConnectionBasicCoverage:
    """Fast, simple tests targeting Connection coverage without database dependency."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.config = FlextDbOracleConfig(
            host="test-host",
            port=1521,
            service_name="TEST",
            username="test",
            password=SecretStr("test"),
        )

    def test_connection_initialization(self) -> None:
        """Test connection initialization patterns."""
        # Basic initialization
        conn = FlextDbOracleConnection(self.config)
        assert conn.config == self.config
        assert not conn.is_connected()
        assert conn._engine is None  # SQLAlchemy engine not initialized

        # Different pool sizes
        pool_config = FlextDbOracleConfig(
            host="pool-test",
            port=1521,
            service_name="POOL",
            username="pool",
            password=SecretStr("pool"),
            pool_min=2,
            pool_max=10,
        )
        pool_conn = FlextDbOracleConnection(pool_config)
        assert pool_conn.config.pool_min == 2
        assert pool_conn.config.pool_max == 10

    def test_connection_properties(self) -> None:
        """Test connection properties without requiring database."""
        conn = FlextDbOracleConnection(self.config)

        # Basic properties
        assert conn.config == self.config
        assert conn.is_connected() is False
        # Check internal SQLAlchemy components are not connected
        assert conn._engine is None

        # String representations
        str_repr = str(conn)
        assert "FlextDbOracleConnection" in str_repr or "test-host" in str_repr

        repr_str = repr(conn)
        assert "FlextDbOracleConnection" in repr_str

    def test_connection_operations_disconnected(self) -> None:
        """Test connection operations when disconnected (should fail gracefully)."""
        conn = FlextDbOracleConnection(self.config)

        # Test operations should fail when not connected
        test_result = conn.test_connection()
        assert not test_result.success
        assert (
            "connection" in test_result.error.lower()
            or "not connected" in test_result.error.lower()
        )

        # Query operations should fail
        query_result = conn.query("SELECT 1 FROM dual")
        assert not query_result.success

        # Execute operations should fail
        execute_result = conn.execute("CREATE TABLE test (id INT)")
        assert not execute_result.success

    def test_connection_metadata_operations_disconnected(self) -> None:
        """Test metadata operations when disconnected."""
        conn = FlextDbOracleConnection(self.config)

        # Metadata operations should fail gracefully when not connected
        if hasattr(conn, "get_schemas"):
            schemas_result = conn.get_schemas()
            assert not schemas_result.success
            assert "not connected" in schemas_result.error.lower()

        if hasattr(conn, "get_tables"):
            tables_result = conn.get_tables()
            assert not tables_result.success

        if hasattr(conn, "get_columns"):
            columns_result = conn.get_columns("TEST_TABLE")
            assert not columns_result.success

    def test_connection_context_managers(self) -> None:
        """Test connection context managers when not connected."""
        conn = FlextDbOracleConnection(self.config)

        # Session context manager should fail when not connected
        if hasattr(conn, "session"):
            with (
                pytest.raises(Exception, match=r"(?i).*not connected.*"),
                conn.session(),
            ):
                pass

        # Transaction context manager should fail when not connected
        if hasattr(conn, "transaction"):
            with (
                pytest.raises(Exception, match=r"(?i).*(not connected|database).*"),
                conn.transaction(),
            ):
                pass

    def test_connection_configuration_validation(self) -> None:
        """Test connection with various configuration edge cases."""
        # Minimal valid config
        minimal_config = FlextDbOracleConfig(
            host="minimal",
            port=1521,
            service_name="MIN",
            username="min",
            password=SecretStr("min"),
        )
        minimal_conn = FlextDbOracleConnection(minimal_config)
        assert isinstance(minimal_conn, FlextDbOracleConnection)

        # Config with custom timeout
        timeout_config = FlextDbOracleConfig(
            host="timeout-test",
            port=1521,
            service_name="TIMEOUT",
            username="timeout",
            password=SecretStr("timeout"),
            timeout=30.0,
        )
        timeout_conn = FlextDbOracleConnection(timeout_config)
        assert timeout_conn.config.timeout == 30.0

    def test_connection_error_handling(self) -> None:
        """Test connection error handling patterns."""
        # Invalid host config (should fail gracefully)
        invalid_config = FlextDbOracleConfig(
            host="invalid-nonexistent-host-12345",
            port=1521,
            service_name="INVALID",
            username="invalid",
            password=SecretStr("invalid"),
        )
        invalid_conn = FlextDbOracleConnection(invalid_config)

        # Connection attempt should fail gracefully
        connect_result = invalid_conn.connect()
        assert not connect_result.success
        assert any(
            word in connect_result.error.lower()
            for word in ["connection", "host", "name or service not known", "timeout"]
        )

    def test_connection_internal_state(self) -> None:
        """Test connection internal state management."""
        conn = FlextDbOracleConnection(self.config)

        # Initial state
        assert not conn.is_connected()

        # Test internal attributes exist
        assert hasattr(conn, "config")
        assert hasattr(conn, "_engine") or hasattr(conn, "connection")

        # Test disconnect on unconnected connection (should be safe)
        disconnect_result = conn.disconnect()
        # Should either succeed (no-op) or fail gracefully
        assert isinstance(disconnect_result.success, bool)


class TestConnectionEdgeCases:
    """Test connection edge cases and error conditions."""

    def setup_method(self) -> None:
        self.config = FlextDbOracleConfig(
            host="edge-test",
            port=1521,
            service_name="EDGE",
            username="edge",
            password=SecretStr("edge"),
        )

    def test_connection_with_special_characters(self) -> None:
        """Test connection config with special characters."""
        special_config = FlextDbOracleConfig(
            host="test-host",
            port=1521,
            service_name="TEST_DB",
            username="test_user",
            password=SecretStr("pass@word!123"),
        )
        conn = FlextDbOracleConnection(special_config)
        assert isinstance(conn, FlextDbOracleConnection)

    def test_connection_extreme_timeouts(self) -> None:
        """Test connection with extreme timeout values."""
        # Very short timeout
        short_config = FlextDbOracleConfig(
            host="short-timeout",
            port=1521,
            service_name="SHORT",
            username="short",
            password=SecretStr("short"),
            timeout=0.1,
        )
        short_conn = FlextDbOracleConnection(short_config)
        assert short_conn.config.timeout == 0.1

        # Very long timeout
        long_config = FlextDbOracleConfig(
            host="long-timeout",
            port=1521,
            service_name="LONG",
            username="long",
            password=SecretStr("long"),
            timeout=300.0,
        )
        long_conn = FlextDbOracleConnection(long_config)
        assert long_conn.config.timeout == 300.0

    def test_connection_methods_existence(self) -> None:
        """Test that expected connection methods exist."""
        conn = FlextDbOracleConnection(self.config)

        # Core methods should exist
        expected_methods = [
            "connect",
            "disconnect",
            "is_connected",
            "test_connection",
            "query",
            "execute",
            "execute_many",
        ]

        for method in expected_methods:
            assert hasattr(conn, method), f"Connection should have {method} method"
            assert callable(getattr(conn, method)), f"{method} should be callable"

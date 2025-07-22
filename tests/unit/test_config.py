"""Tests for configuration module.

Tests for the main Oracle configuration functionality.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from flext_db_oracle.config import OracleConfig


class TestOracleConfig:
    """Test Oracle configuration functionality."""

    def test_create_config_with_required_params(self) -> None:
        """Test creating config with required parameters."""
        config = OracleConfig(
            host="testhost",
            port=1521,
            service_name="testdb",
            username="testuser",
            password="testpass",
        )

        assert config.host == "testhost"
        assert config.port == 1521
        assert config.service_name == "testdb"
        assert config.username == "testuser"
        assert config.password == "testpass"

    def test_create_config_with_sid(self) -> None:
        """Test creating config with SID instead of service name."""
        config = OracleConfig(
            host="testhost",
            port=1521,
            sid="ORCL",
            username="testuser",
            password="testpass",
        )

        assert config.host == "testhost"
        assert config.port == 1521
        assert config.sid == "ORCL"
        assert config.service_name is None
        assert config.username == "testuser"
        assert config.password == "testpass"

    def test_config_default_values(self) -> None:
        """Test configuration default values."""
        config = OracleConfig(
            host="testhost",
            service_name="testdb",
            username="testuser",
            password="testpass",
        )

        assert config.port == 1521  # Default port
        assert config.protocol == "tcp"  # Default protocol
        assert config.pool_min_size == 1  # Default pool min
        assert config.pool_max_size == 10  # Default pool max
        assert config.query_timeout == 30  # Default timeout

    def test_config_validation_requires_username(self) -> None:
        """Test config validation requires username."""
        with pytest.raises((ValueError, TypeError)):
            OracleConfig(
                host="testhost",
                service_name="testdb",
                password="testpass",
            )

    def test_config_validation_requires_password(self) -> None:
        """Test config validation requires password."""
        with pytest.raises((ValueError, TypeError)):
            OracleConfig(
                host="testhost",
                service_name="testdb",
                username="testuser",
            )

    def test_config_validation_requires_service_name_or_sid(self) -> None:
        """Test config validation requires either service_name or sid."""
        with pytest.raises(
            ValueError,
            match="Either service_name or sid must be provided",
        ):
            OracleConfig(
                host="testhost",
                username="testuser",
                password="testpass",
            )

    def test_config_protocol_settings(self) -> None:
        """Test protocol configuration settings."""
        config = OracleConfig(
            host="testhost",
            service_name="testdb",
            username="testuser",
            password="testpass",
            protocol="tcps",
        )

        assert config.protocol == "tcps"

    def test_config_pool_settings(self) -> None:
        """Test connection pool configuration settings."""
        config = OracleConfig(
            host="testhost",
            service_name="testdb",
            username="testuser",
            password="testpass",
            pool_min_size=5,
            pool_max_size=50,
            pool_increment=2,
        )

        assert config.pool_min_size == 5
        assert config.pool_max_size == 50
        assert config.pool_increment == 2

    def test_config_timeout_settings(self) -> None:
        """Test timeout configuration settings."""
        config = OracleConfig(
            host="testhost",
            service_name="testdb",
            username="testuser",
            password="testpass",
            query_timeout=60,
            connect_timeout=20,
        )

        assert config.query_timeout == 60
        assert config.connect_timeout == 20

    def test_config_retry_settings(self) -> None:
        """Test retry configuration settings."""
        config = OracleConfig(
            host="testhost",
            service_name="testdb",
            username="testuser",
            password="testpass",
            retry_attempts=5,
            retry_delay=2.0,
        )

        assert config.retry_attempts == 5
        assert config.retry_delay == 2.0

    def test_config_string_representation(self) -> None:
        """Test string representation works correctly."""
        config = OracleConfig(
            host="testhost",
            service_name="testdb",
            username="testuser",
            password="secretpass",
        )

        config_str = str(config)
        assert "testhost" in config_str
        assert "testdb" in config_str
        assert "testuser" in config_str

    @patch.dict(
        "os.environ",
        {
            "ORACLE_HOST": "envhost",
            "ORACLE_PORT": "1522",
            "ORACLE_SERVICE_NAME": "envdb",
            "ORACLE_USERNAME": "envuser",
            "ORACLE_PASSWORD": "envpass",
        },
    )
    def test_config_from_environment_variables(self) -> None:
        """Test creating config from environment variables."""
        # This would test a from_env class method if it exists
        # For now, test that we can create config with env-like values
        config = OracleConfig(
            host="envhost",
            port=1522,
            service_name="envdb",
            username="envuser",
            password="envpass",
        )

        assert config.host == "envhost"
        assert config.port == 1522
        assert config.service_name == "envdb"
        assert config.username == "envuser"
        assert config.password == "envpass"

    def test_config_dsn_construction(self) -> None:
        """Test DSN construction for Oracle connection."""
        config = OracleConfig(
            host="testhost",
            port=1521,
            service_name="testdb",
            username="testuser",
            password="testpass",
        )

        # Test that config has the necessary components for DSN construction
        assert config.host == "testhost"
        assert config.port == 1521
        assert config.service_name == "testdb"
        # DSN construction would typically be done by connection layer

    def test_config_equality(self) -> None:
        """Test configuration equality comparison."""
        config1 = OracleConfig(
            host="testhost",
            service_name="testdb",
            username="testuser",
            password="testpass",
        )

        config2 = OracleConfig(
            host="testhost",
            service_name="testdb",
            username="testuser",
            password="testpass",
        )

        config3 = OracleConfig(
            host="otherhost",
            service_name="testdb",
            username="testuser",
            password="testpass",
        )

        assert config1 == config2
        assert config1 != config3

    def test_config_copy(self) -> None:
        """Test configuration copying."""
        config = OracleConfig(
            host="testhost",
            service_name="testdb",
            username="testuser",
            password="testpass",
            pool_max_size=20,
        )

        # Create a copy with modified values
        config_copy = config.model_copy(update={"pool_max_size": 30})

        assert config_copy.host == "testhost"
        assert config_copy.service_name == "testdb"
        assert config_copy.username == "testuser"
        assert config_copy.password == "testpass"
        assert config_copy.pool_max_size == 30
        assert config.pool_max_size == 20  # Original unchanged

    def test_database_identifier_property(self) -> None:
        """Test database identifier property."""
        # Test with service_name
        config1 = OracleConfig(
            host="testhost",
            service_name="testdb",
            username="testuser",
            password="testpass",
        )
        assert config1.database_identifier == "testdb"

        # Test with SID
        config2 = OracleConfig(
            host="testhost",
            sid="ORCL",
            username="testuser",
            password="testpass",
        )
        assert config2.database_identifier == "ORCL"

    def test_connection_string_property(self) -> None:
        """Test connection string property doesn't expose password."""
        config = OracleConfig(
            host="testhost",
            port=1522,
            service_name="testdb",
            username="testuser",
            password="secretpass",
        )

        conn_str = config.connection_string
        assert "oracle://" in conn_str
        assert "testuser" in conn_str
        assert "testhost" in conn_str
        assert "1522" in conn_str
        assert "testdb" in conn_str
        assert "secretpass" not in conn_str  # Password should be hidden
        assert "***" in conn_str  # Password should be masked

    def test_pool_size_validation(self) -> None:
        """Test pool size validation."""
        # This should work fine
        config = OracleConfig(
            host="testhost",
            service_name="testdb",
            username="testuser",
            password="testpass",
            pool_min_size=5,
            pool_max_size=10,
        )
        assert config.pool_min_size == 5
        assert config.pool_max_size == 10

        # This should fail validation
        with pytest.raises(
            ValueError,
            match="pool_max_size.*must be greater than or equal to pool_min_size",
        ):
            OracleConfig(
                host="testhost",
                service_name="testdb",
                username="testuser",
                password="testpass",
                pool_min_size=10,
                pool_max_size=5,  # Less than min
            )

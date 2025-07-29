"""Unit tests for FlextDbOracleConfig - comprehensive validation."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from flext_core import FlextResult

from flext_db_oracle import FlextDbOracleConfig


class TestFlextDbOracleConfig:
    """Comprehensive tests for Oracle configuration."""

    def test_config_creation_with_service_name(self) -> None:
        """Test config creation with service name."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="ORCLCDB",
        )

        assert config.host == "localhost"
        assert config.port == 1521
        assert config.username == "testuser"
        assert config.password.get_secret_value() == "testpass"
        assert config.service_name == "ORCLCDB"
        assert config.sid is None

    def test_config_creation_with_sid(self) -> None:
        """Test config creation with SID."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            username="testuser",
            password="testpass",
            sid="ORCL",
        )

        assert config.sid == "ORCL"
        assert config.service_name is None

    def test_domain_rules_validation_success(
        self, valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test successful domain rules validation."""
        result = valid_config.validate_domain_rules()
        assert result.is_success
        assert result.data is None

    def test_domain_rules_validation_no_identifier(self) -> None:
        """Test validation failure when no SID or service_name."""
        with pytest.raises(
            ValueError, match="Either SID or service_name must be provided",
        ):
            FlextDbOracleConfig(
                host="localhost",
                port=1521,
                username="testuser",
                password="testpass",
            )

    def test_domain_rules_validation_invalid_pool_settings(self) -> None:
        """Test validation failure for invalid pool settings."""
        with pytest.raises(ValueError, match="pool_max must be >= pool_min"):
            FlextDbOracleConfig(
                host="localhost",
                port=1521,
                username="testuser",
                password="testpass",
                service_name="ORCLCDB",
                pool_min=10,
                pool_max=5,
            )

    def test_domain_rules_validation_empty_host(self) -> None:
        """Test validation failure for empty host."""
        with pytest.raises(ValueError, match="Host cannot be empty"):
            FlextDbOracleConfig(
                host="",
                port=1521,
                username="testuser",
                password="testpass",
                service_name="ORCLCDB",
            )

    def test_from_env_success(self, test_environment_variables: dict[str, str]) -> None:
        """Test successful configuration from environment variables."""
        result = FlextDbOracleConfig.from_env()

        assert result.is_success
        config = result.data
        assert config.host == "test.oracle.com"
        assert config.port == 1521
        assert config.username == "testuser"
        assert config.service_name == "ORCLCDB"

    def test_from_env_with_custom_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test configuration from environment with custom prefix."""
        monkeypatch.setenv("CUSTOM_HOST", "custom.oracle.com")
        monkeypatch.setenv("CUSTOM_PORT", "1522")
        monkeypatch.setenv("CUSTOM_USERNAME", "customuser")
        monkeypatch.setenv("CUSTOM_PASSWORD", "custompass")
        monkeypatch.setenv("CUSTOM_SERVICE_NAME", "CUSTOM")

        result = FlextDbOracleConfig.from_env("CUSTOM_")

        assert result.is_success
        config = result.data
        assert config.host == "custom.oracle.com"
        assert config.port == 1522
        assert config.username == "customuser"

    def test_from_env_failure(self) -> None:
        """Test environment configuration failure."""
        with patch.dict(os.environ, {}, clear=True):
            result = FlextDbOracleConfig.from_env()
            # Should still succeed with defaults, but test error handling
            assert isinstance(result, FlextResult)

    def test_from_url_service_name(self) -> None:
        """Test configuration from URL with service name."""
        url = "oracle://user:pass@host:1521/service"
        result = FlextDbOracleConfig.from_url(url)

        assert result.is_success
        config = result.data
        assert config.host == "host"
        assert config.port == 1521
        assert config.username == "user"
        assert config.password.get_secret_value() == "pass"
        assert config.service_name == "service"

    def test_from_url_invalid(self) -> None:
        """Test configuration from invalid URL."""
        # Test with a URL that will cause an actual parsing exception
        result = FlextDbOracleConfig.from_url("oracle://[invalid:bracket:syntax")
        assert result.is_failure
        assert "Failed to parse URL" in result.error

    def test_to_connect_params(self, valid_config: FlextDbOracleConfig) -> None:
        """Test conversion to connection parameters."""
        params = valid_config.to_connect_params()

        assert params["host"] == "localhost"
        assert params["port"] == 1521
        assert params["user"] == "testuser"
        assert params["password"] == "testpass"
        assert params["service_name"] == "ORCLCDB"
        assert params["encoding"] == "UTF-8"

    def test_to_pool_params(self, valid_config: FlextDbOracleConfig) -> None:
        """Test conversion to pool parameters."""
        params = valid_config.to_pool_params()

        assert params["min"] == 1
        assert params["max"] == 10
        assert params["timeout"] == 30

    def test_get_connection_string_service_name(
        self, valid_config: FlextDbOracleConfig,
    ) -> None:
        """Test connection string with service name."""
        conn_str = valid_config.get_connection_string()
        assert conn_str == "localhost:1521/ORCLCDB"

    def test_get_connection_string_sid(self) -> None:
        """Test connection string with SID."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            username="testuser",
            password="testpass",
            sid="ORCL",
        )

        conn_str = config.get_connection_string()
        assert conn_str == "localhost:1521:ORCL"

    def test_from_dict_success(self) -> None:
        """Test configuration from dictionary."""
        config_dict = {
            "host": "localhost",
            "port": 1521,
            "username": "testuser",
            "password": "testpass",
            "service_name": "ORCLCDB",
        }

        result = FlextDbOracleConfig.from_dict(config_dict)
        assert result.is_success
        config = result.data
        assert config.host == "localhost"

    def test_from_dict_validation_failure(self) -> None:
        """Test configuration from dictionary with validation failure."""
        config_dict = {
            "host": "",  # Invalid empty host
            "port": 1521,
            "username": "testuser",
            "password": "testpass",
            "service_name": "ORCLCDB",
        }

        result = FlextDbOracleConfig.from_dict(config_dict)
        assert result.is_failure
        assert "Configuration creation failed" in result.error

    def test_ssl_configuration(self) -> None:
        """Test SSL configuration settings."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="ORCLCDB",
            ssl_enabled=True,
            ssl_cert_path="/path/to/cert.pem",
        )

        params = config.to_connect_params()
        assert params["ssl_context"] is True
        assert params["ssl_cert_path"] == "/path/to/cert.pem"

    def test_ssl_validation_failure(self) -> None:
        """Test SSL validation failure when cert path missing."""
        config = FlextDbOracleConfig(
            host="localhost",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="ORCLCDB",
            ssl_enabled=True,
            # Missing ssl_cert_path
        )

        result = config.validate_domain_rules()
        assert result.is_failure
        assert "ssl_cert_path required when SSL is enabled" in result.error

    def test_string_representation(self, valid_config: FlextDbOracleConfig) -> None:
        """Test string representation without sensitive data."""
        str_repr = str(valid_config)
        assert "FlextDbOracleConfig" in str_repr
        assert "localhost" in str_repr
        assert "testuser" in str_repr
        assert "testpass" not in str_repr  # Password should not be visible

    def test_field_validators(self) -> None:
        """Test field validators for host and username."""
        # Test host validation
        with pytest.raises(ValueError, match="Host cannot be empty"):
            FlextDbOracleConfig(
                host="   ",  # Whitespace only
                port=1521,
                username="testuser",
                password="testpass",
                service_name="ORCLCDB",
            )

        # Test username validation
        with pytest.raises(ValueError, match="Username cannot be empty"):
            FlextDbOracleConfig(
                host="localhost",
                port=1521,
                username="   ",  # Whitespace only
                password="testpass",
                service_name="ORCLCDB",
            )

    def test_port_validation(self) -> None:
        """Test port range validation."""
        with pytest.raises(ValueError, match=r".*"):
            FlextDbOracleConfig(
                host="localhost",
                port=70000,  # Out of range
                username="testuser",
                password="testpass",
                service_name="ORCLCDB",
            )

    def test_pool_configuration_validation_errors(self) -> None:
        """Test pool configuration validation edge cases."""
        # Create a valid config first, then modify with model_copy
        base_config = FlextDbOracleConfig(
            host="localhost",
            username="test",
            password="test",
            service_name="test",
        )

        # Test pool_max < pool_min by using model_copy
        config = base_config.model_copy(update={"pool_min": 10, "pool_max": 5})
        result = config.validate_domain_rules()
        assert result.is_failure
        assert "pool_max must be >= pool_min" in result.error

        # Test pool_increment > pool_max
        config = base_config.model_copy(update={"pool_max": 5, "pool_increment": 10})
        result = config.validate_domain_rules()
        assert result.is_failure
        assert "pool_increment cannot exceed pool_max" in result.error

    def test_ssl_configuration_with_cert_path(self) -> None:
        """Test SSL configuration requiring cert path."""
        # Test SSL enabled but no cert path - should be caught by validate_domain_rules
        config = FlextDbOracleConfig(
            host="localhost",
            username="test",
            password="test",
            service_name="test",
            ssl_enabled=True,
            # ssl_cert_path not provided
        )

        result = config.validate_domain_rules()
        assert result.is_failure
        assert "ssl_cert_path required when SSL is enabled" in result.error

    def test_from_env_parsing_errors(self) -> None:
        """Test from_env handles parsing errors gracefully."""
        with patch.dict(
            os.environ,
            {
                "FLEXT_TARGET_ORACLE_PORT": "invalid-port",
            },
        ):
            result = FlextDbOracleConfig.from_env()
            assert result.is_failure
            assert "Failed to create config from environment" in result.error

    def test_from_dict_creation_error(self) -> None:
        """Test from_dict handles creation errors."""
        config_dict = {
            "host": "",  # This will fail validation
            "username": "test",
            "password": "test",
            "service_name": "test",
        }

        result = FlextDbOracleConfig.from_dict(config_dict)
        assert result.is_failure
        assert "Configuration creation failed" in result.error

    def test_from_url_parsing_error(self) -> None:
        """Test from_url handles parsing errors properly."""
        with patch("urllib.parse.urlparse", side_effect=ValueError("Mock error")):
            result = FlextDbOracleConfig.from_url("oracle://test@localhost/db")
            assert result.is_failure
            assert "Failed to parse URL" in result.error

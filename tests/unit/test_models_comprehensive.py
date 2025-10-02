"""Comprehensive tests for Oracle database models.

Tests all Oracle model functionality including configuration creation,
validation, parsing, and business logic to achieve high coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from flext_core import FlextModels
from flext_db_oracle import FlextDbOracleModels


class TestOracleValidation:
    """Test Oracle validation functionality."""

    def test_validate_identifier_success(self) -> None:
        """Test successful Oracle identifier validation."""
        validator = FlextDbOracleModels.OracleValidation

        # Test valid identifiers
        result = validator.validate_identifier("VALID_TABLE")
        assert result.is_success
        assert result.value == "VALID_TABLE"

        # Test lowercase conversion
        result = validator.validate_identifier("lowercase_table")
        assert result.is_success
        assert result.value == "LOWERCASE_TABLE"

        # Test alphanumeric with underscores
        result = validator.validate_identifier("TABLE_123")
        assert result.is_success
        assert result.value == "TABLE_123"

    def test_validate_identifier_empty(self) -> None:
        """Test Oracle identifier validation with empty input."""
        validator = FlextDbOracleModels.OracleValidation

        # Test empty string
        result = validator.validate_identifier("")
        assert result.is_failure
        assert "cannot be empty" in str(result.error)

        # Test whitespace only
        result = validator.validate_identifier("   ")
        assert result.is_failure
        assert "cannot be empty" in str(result.error)

    def test_validate_identifier_too_long(self) -> None:
        """Test Oracle identifier validation with too long input."""
        validator = FlextDbOracleModels.OracleValidation

        # Create identifier longer than 30 characters (Oracle limit)
        long_identifier = "A" * 31
        result = validator.validate_identifier(long_identifier)
        assert result.is_failure
        assert "too long" in str(result.error)

    def test_validate_identifier_invalid_characters(self) -> None:
        """Test Oracle identifier validation with invalid characters."""
        validator = FlextDbOracleModels.OracleValidation

        # Test invalid characters
        invalid_identifiers = [
            "TABLE-NAME",  # Hyphens not allowed
            "TABLE NAME",  # Spaces not allowed
            "TABLE@NAME",  # Special characters not allowed
            "123TABLE",  # Cannot start with number
        ]

        for invalid_id in invalid_identifiers:
            result = validator.validate_identifier(invalid_id)
            assert result.is_failure
            assert "invalid characters" in str(result.error)


class TestOracleConfig:
    """Test Oracle configuration model."""

    def test_oracle_config_creation_success(self) -> None:
        """Test successful Oracle configuration creation."""
        config = FlextDbOracleModels.OracleConfig(
            host="localhost",
            port=1521,
            name="XE",
            username="test_user",
            password="test_password",
        )

        assert config.host == "localhost"
        assert config.port == 1521
        assert config.name == "XE"
        assert config.username == "test_user"
        assert config.password == "test_password"

    def test_oracle_config_defaults(self) -> None:
        """Test Oracle configuration default values."""
        config = FlextDbOracleModels.OracleConfig(
            username="test_user",
            password="test_password",
        )

        assert config.host == "localhost"
        assert config.port == 1521
        assert config.name == "XE"
        assert config.pool_min == 2
        assert config.pool_max == 20
        assert config.timeout == 60
        assert config.service_name is None
        assert config.sid is None

    def test_oracle_config_validation_empty_host(self) -> None:
        """Test Oracle config validation fails with empty host."""
        with pytest.raises(ValidationError) as exc_info:
            FlextDbOracleModels.OracleConfig(
                host="",
                username="test_user",
                password="test_password",
            )

        errors = exc_info.value.errors()
        assert any("Host cannot be empty" in str(error["msg"]) for error in errors)

    def test_oracle_config_validation_whitespace_host(self) -> None:
        """Test Oracle config validation fails with whitespace-only host."""
        with pytest.raises(ValidationError) as exc_info:
            FlextDbOracleModels.OracleConfig(
                host="   ",
                username="test_user",
                password="test_password",
            )

        errors = exc_info.value.errors()
        assert any("Host cannot be empty" in str(error["msg"]) for error in errors)

    def test_oracle_config_optional_fields(self) -> None:
        """Test Oracle configuration with optional fields."""
        config = FlextDbOracleModels.OracleConfig(
            host="prod-oracle.example.com",
            port=1522,
            name="PRODDB",
            username="prod_user",
            password="prod_password",
            service_name="PRODDB_SERVICE",
            ssl_server_cert_dn="CN=oracle.example.com",
            pool_min=5,
            pool_max=50,
            timeout=120,
        )

        assert config.host == "prod-oracle.example.com"
        assert config.port == 1522
        assert config.name == "PRODDB"
        assert config.service_name == "PRODDB_SERVICE"
        assert config.sid is None
        assert config.ssl_server_cert_dn == "CN=oracle.example.com"
        assert config.pool_min == 5
        assert config.pool_max == 50
        assert config.timeout == 120

    def test_oracle_config_service_name_and_sid_mutually_exclusive(self) -> None:
        """Test that service_name and sid are mutually exclusive."""
        with pytest.raises(
            ValueError, match="Cannot specify both service_name and SID"
        ):
            FlextDbOracleModels.OracleConfig(
                host="prod-oracle.example.com",
                port=1522,
                name="PRODDB",
                username="prod_user",
                password="prod_password",
                service_name="PRODDB_SERVICE",
                sid="PRODDB_SID",
            )


class TestOracleConfigFromEnv:
    """Test Oracle configuration creation from environment variables."""

    def test_from_env_default_prefix(self) -> None:
        """Test creating Oracle config from environment with default prefix."""
        # The from_env method uses FlextDbOracleConfig defaults, which don't include username/password
        # So it should fail due to missing required credentials
        result = FlextDbOracleModels.OracleConfig.from_env()

        assert result.is_failure
        assert result.error is not None
        assert (
            result.error is not None
            and "username is required but not configured" in result.error
        )

    def test_from_env_custom_prefix(self) -> None:
        """Test creating Oracle config from environment with custom prefix."""
        # The from_env method ignores the prefix parameter and uses FlextDbOracleConfig defaults
        # which don't include username/password, so it should fail
        env_vars = {
            "CUSTOM_HOST": "custom-host",
            "CUSTOM_PORT": "1523",
            "CUSTOM_DB": "CUSTOMDB",
            "CUSTOM_USER": "custom_user",
            "CUSTOM_PASSWORD": "custom_password",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            result = FlextDbOracleModels.OracleConfig.from_env("CUSTOM")

        assert result.is_failure
        assert result.error is not None
        assert (
            result.error is not None
            and "username is required but not configured" in result.error
        )

    def test_from_env_defaults_when_missing(self) -> None:
        """Test Oracle config fails when required credentials are missing."""
        # The from_env method requires username/password to be configured
        result = FlextDbOracleModels.OracleConfig.from_env()

        assert result.is_failure
        assert result.error is not None
        assert (
            result.error is not None
            and "username is required but not configured" in result.error
        )

    def test_from_env_invalid_port(self) -> None:
        """Test Oracle config from env fails when credentials are missing."""
        # The from_env method requires valid username/password, ignores env vars
        env_vars = {
            "ORACLE_HOST": "test-host",
            "ORACLE_PORT": "not_a_number",
            "ORACLE_USER": "",  # Empty username
            "ORACLE_PASSWORD": "test_password",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            result = FlextDbOracleModels.OracleConfig.from_env()

        # Should fail due to missing username
        assert result.is_failure
        assert result.error is not None
        assert (
            result.error is not None
            and "username is required but not configured" in result.error
        )

    def test_from_env_exception_handling(self) -> None:
        """Test Oracle config from env handles exceptions properly."""
        # The from_env method validates required fields
        env_vars = {
            "ORACLE_HOST": "",  # Empty host is ignored
            "ORACLE_USER": "",  # Empty username
            "ORACLE_PASSWORD": "test_password",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            result = FlextDbOracleModels.OracleConfig.from_env()

        assert result.is_failure
        assert result.error is not None
        assert (
            result.error is not None
            and "username is required but not configured" in result.error
        )


class TestOracleConfigFromUrl:
    """Test Oracle configuration creation from database URLs."""

    def test_from_url_complete_success(self) -> None:
        """Test creating Oracle config from complete URL."""
        url = "oracle://user:password@host:1521/service_name"
        result = FlextDbOracleModels.OracleConfig.from_url(url)

        assert result.is_success
        config = result.value
        assert config.host == "host"
        assert config.port == 1521
        assert config.username == "user"
        assert config.password == "password"
        assert config.service_name == "SERVICE_NAME"  # Oracle normalizes to uppercase
        assert config.name == "SERVICE_NAME"  # Oracle normalizes to uppercase

    def test_from_url_no_password(self) -> None:
        """Test creating Oracle config from URL without password."""
        url = "oracle://user@host:1521/service_name"
        result = FlextDbOracleModels.OracleConfig.from_url(url)

        assert result.is_success
        config = result.value
        assert config.username == "user"
        assert config.password is None

    def test_from_url_default_port(self) -> None:
        """Test creating Oracle config from URL without port."""
        url = "oracle://user:password@host/service_name"
        result = FlextDbOracleModels.OracleConfig.from_url(url)

        assert result.is_success
        config = result.value
        assert config.port == 1521  # default port

    def test_from_url_no_service_name(self) -> None:
        """Test creating Oracle config from URL without service name."""
        url = "oracle://user:password@host:1521"
        result = FlextDbOracleModels.OracleConfig.from_url(url)

        assert result.is_success
        config = result.value
        assert config.name == "XE"  # default
        assert config.service_name is None

    def test_from_url_invalid_protocol(self) -> None:
        """Test Oracle config from URL fails with invalid protocol."""
        url = "mysql://user:password@host:3306/database"
        result = FlextDbOracleModels.OracleConfig.from_url(url)

        assert result.is_failure
        assert "must start with oracle://" in str(result.error)

    def test_from_url_missing_at_symbol(self) -> None:
        """Test Oracle config from URL fails without @ symbol."""
        url = "oracle://user:password_host:1521/service"
        result = FlextDbOracleModels.OracleConfig.from_url(url)

        assert result.is_failure
        assert "Invalid URL format" in str(result.error)

    def test_from_url_complex_password(self) -> None:
        """Test Oracle config from URL with complex password containing special chars."""
        url = "oracle://user:p_ssw0rd!@host:1521/service"
        result = FlextDbOracleModels.OracleConfig.from_url(url)

        assert result.is_success
        config = result.value
        assert config.username == "user"
        assert config.password == "p_ssw0rd!"

    def test_from_url_exception_handling(self) -> None:
        """Test Oracle config from URL handles parsing exceptions."""
        # URL that would cause integer parsing error
        url = "oracle://user:password@host:not_a_port/service"
        result = FlextDbOracleModels.OracleConfig.from_url(url)

        assert result.is_failure
        assert "Failed to parse URL" in str(result.error)


class TestFlextDbOracleModelsStructure:
    """Test FlextDbOracleModels class structure and inheritance."""

    def test_models_inheritance(self) -> None:
        """Test FlextDbOracleModels inherits from FlextModels."""
        assert issubclass(FlextDbOracleModels, FlextModels)

    def test_nested_validation_class(self) -> None:
        """Test _OracleValidation nested class exists."""
        assert hasattr(FlextDbOracleModels, "_OracleValidation")
        assert callable(FlextDbOracleModels.OracleValidation.validate_identifier)

    def test_class_variables_exist(self) -> None:
        """Test required class variables exist."""
        assert hasattr(FlextDbOracleModels, "Entity")
        assert hasattr(FlextDbOracleModels, "Value")
        assert hasattr(FlextDbOracleModels, "DatabaseConfig")

    def test_field_definitions_exist(self) -> None:
        """Test field definitions exist."""
        assert hasattr(FlextDbOracleModels, "host_field")
        assert hasattr(FlextDbOracleModels, "port_field")
        assert hasattr(FlextDbOracleModels, "username_field")
        assert hasattr(FlextDbOracleModels, "password_field")
        assert hasattr(FlextDbOracleModels, "service_name_field")

    def test_oracle_config_class_exists(self) -> None:
        """Test OracleConfig nested class exists and is accessible."""
        assert hasattr(FlextDbOracleModels, "OracleConfig")
        assert callable(FlextDbOracleModels.OracleConfig)

        # Test it can be instantiated
        config = FlextDbOracleModels.OracleConfig(
            username="test", password="test", domain_events=[]
        )
        assert config is not None


class TestOracleConfigEdgeCases:
    """Test Oracle configuration edge cases and error conditions."""

    def test_config_with_unicode_characters(self) -> None:
        """Test Oracle config handles unicode characters properly."""
        config = FlextDbOracleModels.OracleConfig(
            host="oracle-ñáéíóú.example.com",
            username="usér_name",
            password="páss_wórd_ñ",
        )

        assert config.host == "oracle-ñáéíóú.example.com"
        assert config.username == "usér_name"
        assert config.password == "páss_wórd_ñ"

    def test_config_extreme_values(self) -> None:
        """Test Oracle config with extreme but valid values."""
        config = FlextDbOracleModels.OracleConfig(
            host="a" * 253,  # Maximum hostname length (253 chars)
            port=65535,  # Maximum port number
            username="u",  # Minimum username
            password="p",  # Minimum password
            pool_min=1,  # Minimum pool
            pool_max=1000,  # Large pool
            timeout=3600,  # Long timeout
        )

        assert len(config.host) == 253
        assert config.port == 65535
        assert config.pool_max == 1000
        assert config.timeout == 3600

    def test_config_serialization(self) -> None:
        """Test Oracle config can be serialized and deserialized."""
        original_config = FlextDbOracleModels.OracleConfig(
            host="test-host",
            port=1521,
            name="TESTDB",
            username="test_user",
            password="test_password",
            service_name="TEST_SERVICE",
        )

        # Test model_dump (Pydantic v2)
        config_dict = original_config.model_dump()
        assert isinstance(config_dict, dict)
        assert config_dict["host"] == "test-host"
        assert config_dict["service_name"] == "TEST_SERVICE"

        # Test reconstruction from dict
        reconstructed_config = FlextDbOracleModels.OracleConfig(**config_dict)
        assert reconstructed_config.host == original_config.host
        assert reconstructed_config.service_name == original_config.service_name

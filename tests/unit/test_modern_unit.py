"""Modern unit tests for flext-db-oracle.

These tests demonstrate modern pytest patterns that pass strict linting:
- ruff with ALL rules enabled
- mypy --strict
- bandit security checks
- PEP 8 compliance
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from flext_db_oracle.config import OracleConfig


def test_oracle_config_creation():
    """Test Oracle configuration creation with valid parameters."""
    config = OracleConfig(
        username="test_user",
        password="test_password",
        service_name="XE",
    )

    assert config.username == "test_user"
    assert config.password == "test_password"  # noqa: S105
    assert config.service_name == "XE"
    assert config.host == "localhost"
    assert config.port == 1521


def test_oracle_config_validation_missing_service_and_sid():
    """Test that validation fails when both service_name and sid are missing."""
    with pytest.raises(ValidationError):
        OracleConfig(
            username="test_user",
            password="test_password",
        )


def test_oracle_config_connection_string():
    """Test connection string generation for logging."""
    config = OracleConfig(
        username="test_user",
        password="test_password",
        service_name="XE",
        host="oracle.example.com",
        port=1521,
    )

    expected = "oracle://test_user:***@oracle.example.com:1521/XE"
    assert config.connection_string == expected


def test_oracle_config_pool_validation():
    """Test pool size validation."""
    with pytest.raises(ValidationError):
        OracleConfig(
            username="test_user",
            password="test_password",
            service_name="XE",
            pool_min_size=10,
            pool_max_size=5,  # Invalid: max < min
        )

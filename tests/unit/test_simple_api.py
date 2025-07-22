"""Tests for simple API module.
Tests for the simple API functionality providing easy Oracle setup.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

from flext_db_oracle.config import OracleConfig
from flext_db_oracle.simple_api import (
    create_connection_service,
    setup_oracle_db,
)


class TestSetupOracleDb:
    """Test setup_oracle_db function."""

    def test_setup_with_provided_config(self) -> None:
        """Test setup with provided config."""
        config = OracleConfig(
            host="testhost",
            port=1521,
            service_name="testdb",
            username="testuser",
            password="testpass",
        )
        result = setup_oracle_db(config)
        assert result.success
        assert result.data == config

    def test_setup_with_no_config_uses_default(self) -> None:
        """Test setup with no config creates default."""
        result = setup_oracle_db()
        assert result.success
        assert isinstance(result.data, OracleConfig)

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
    def test_setup_uses_environment_variables(self) -> None:
        """Test setup uses environment variables."""
        result = setup_oracle_db()
        assert result.success
        config = result.data
        assert config.host == "envhost"
        assert config.port == 1522
        assert config.service_name == "envdb"
        assert config.username == "envuser"
        assert config.password == "envpass"

    @patch.dict("os.environ", {"ORACLE_PORT": "invalid_port"})
    def test_setup_handles_invalid_config(self) -> None:
        """Test setup handles invalid configuration."""
        # This will cause int() conversion to fail
        result = setup_oracle_db()
        assert not result.success
        assert "Failed to setup Oracle DB" in result.error


class TestCreateConnectionService:
    """Test connection service creation functionality."""

    @patch("flext_db_oracle.simple_api.OracleConnectionService")
    def test_create_connection_service_success(self, mock_service_class: Mock) -> None:
        """Test successful connection service creation."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        config = OracleConfig(
            host="testhost",
            port=1521,
            service_name="testdb",
            username="testuser",
            password="testpass",
        )
        result = create_connection_service(config)
        assert result.success
        assert result.data == mock_service
        mock_service_class.assert_called_once_with(config)

    def test_create_connection_service_invalid_config(self) -> None:
        """Test service creation with invalid config."""
        result = create_connection_service(None)
        assert not result.success
        assert "configuration" in result.error.lower()

    @patch("flext_db_oracle.simple_api.OracleConnectionService")
    def test_create_connection_service_failure(self, mock_service_class: Mock) -> None:
        """Test service creation failure."""
        mock_service_class.side_effect = Exception("Service creation failed")
        config = OracleConfig(
            host="testhost",
            port=1521,
            service_name="testdb",
            username="testuser",
            password="testpass",
        )
        result = create_connection_service(config)
        assert not result.success
        assert "Failed to create connection service" in result.error
        assert "Service creation failed" in result.error


class TestIntegrationScenarios:
    """Test integration scenarios using simple API."""

    @patch.dict(
        "os.environ",
        {
            "ORACLE_HOST": "localhost",
            "ORACLE_PORT": "1522",
            "ORACLE_SERVICE_NAME": "envdb",
            "ORACLE_USERNAME": "envuser",
            "ORACLE_PASSWORD": "envpass",
        },
    )
    @patch("flext_db_oracle.simple_api.OracleConnectionService")
    def test_full_setup_workflow(self, mock_service_class: Mock) -> None:
        """Test complete setup workflow."""
        # Setup service mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        # Setup configuration
        config_result = setup_oracle_db()
        assert config_result.success
        # Create service
        service_result = create_connection_service(config_result.data)
        assert service_result.success

    @patch("flext_db_oracle.simple_api.OracleConnectionService")
    def test_setup_and_service_creation(self, mock_service_class: Mock) -> None:
        """Test setup and service creation."""
        # Setup mocks
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        # Setup database config
        config_result = setup_oracle_db()
        assert config_result.success
        # Create service
        service_result = create_connection_service(config_result.data)
        assert service_result.success
        assert service_result.data is not None

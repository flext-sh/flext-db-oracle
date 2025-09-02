"""Test field definitions and validation."""

from flext_db_oracle import FlextDbOracleModels


class TestFlextDbOracleModels:
    """Test FlextDbOracleModels fields."""

    def test_host_field_exists(self) -> None:
        """Test host field exists."""
        assert hasattr(FlextDbOracleModels, "host_field")
        assert FlextDbOracleModels.host_field is not None

    def test_port_field_exists(self) -> None:
        """Test port field exists."""
        assert hasattr(FlextDbOracleModels, "port_field")
        assert FlextDbOracleModels.port_field is not None

    def test_username_field_exists(self) -> None:
        """Test username field exists."""
        assert hasattr(FlextDbOracleModels, "username_field")
        assert FlextDbOracleModels.username_field is not None

    def test_password_field_exists(self) -> None:
        """Test password field exists."""
        assert hasattr(FlextDbOracleModels, "password_field")
        assert FlextDbOracleModels.password_field is not None

    def test_service_name_field_exists(self) -> None:
        """Test service_name field exists."""
        assert hasattr(FlextDbOracleModels, "service_name_field")
        assert FlextDbOracleModels.service_name_field is not None

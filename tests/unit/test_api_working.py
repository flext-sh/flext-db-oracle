"""Working API tests using only real methods that exist and work."""

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig
from pydantic import SecretStr


class TestFlextDbOracleApiWorking:
    """Test FlextDbOracleApi using only methods that work without hanging."""
    
    def setup_method(self) -> None:
        """Setup test configuration."""
        self.config = FlextDbOracleConfig(
            host="test_host",
            port=1521, 
            service_name="TEST",
            username="test_user",
            password=SecretStr("test_password")
        )
        self.api = FlextDbOracleApi(self.config)

    def test_api_creation(self) -> None:
        """Test API can be created with valid config."""
        assert self.api is not None
        assert self.api.config == self.config

    def test_config_access(self) -> None:
        """Test config property access."""
        assert self.api.config is not None
        assert self.api.config.host == "test_host"
        assert self.api.config.port == 1521

    def test_is_valid_method(self) -> None:
        """Test is_valid method."""
        is_valid = self.api.is_valid()
        assert isinstance(is_valid, bool)

    def test_factory_methods(self) -> None:
        """Test factory methods work."""
        # Test from_config class method
        api_from_config = FlextDbOracleApi.from_config(self.config)
        assert api_from_config is not None
        assert isinstance(api_from_config, FlextDbOracleApi)

    def test_dict_serialization(self) -> None:
        """Test dict serialization methods."""
        # These should work without database
        as_dict = self.api.to_dict()
        assert isinstance(as_dict, dict)
        
        basic_dict = self.api.to_dict_basic()
        assert isinstance(basic_dict, dict)
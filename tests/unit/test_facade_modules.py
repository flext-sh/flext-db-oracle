"""Tests for facade modules to achieve 100% coverage.

These modules are simple facades that re-export functionality from other modules.
Testing ensures imports work correctly and all statements are covered.
"""

import flext_db_oracle.cli as cli_module
import flext_db_oracle.config as config_module
import flext_db_oracle.fields as fields_module
import flext_db_oracle.metadata as metadata_module


def test_cli_facade_imports() -> None:
    """Test CLI facade module imports and __all__."""
    # Test import and __all__ content
    assert hasattr(cli_module, "__all__")
    assert "FlextDbOracleCliApplication" in cli_module.__all__
    assert "FlextDbOracleUtilities" in cli_module.__all__
    assert "get_app" in cli_module.__all__
    assert "oracle_cli" in cli_module.__all__

    # Test actual imports work
    assert hasattr(cli_module, "FlextDbOracleCliApplication")
    assert hasattr(cli_module, "FlextDbOracleUtilities")
    assert hasattr(cli_module, "get_app")
    assert hasattr(cli_module, "oracle_cli")


def test_config_facade_imports() -> None:
    """Test config facade module imports and __all__."""
    # Test import and __all__ content
    assert hasattr(config_module, "__all__")
    assert "FlextDbOracleConfig" in config_module.__all__

    # Test actual import works
    assert hasattr(config_module, "FlextDbOracleConfig")


def test_fields_facade_imports() -> None:
    """Test fields facade module imports and __all__."""
    # Test import and __all__ content
    assert hasattr(fields_module, "__all__")
    assert "ConnectionFields" in fields_module.__all__
    assert "DatabaseMetadataFields" in fields_module.__all__
    assert "QueryFields" in fields_module.__all__
    assert "ValidationFields" in fields_module.__all__

    # Test actual imports work
    assert hasattr(fields_module, "ConnectionFields")
    assert hasattr(fields_module, "DatabaseMetadataFields")
    assert hasattr(fields_module, "QueryFields")
    assert hasattr(fields_module, "ValidationFields")


def test_metadata_facade_imports() -> None:
    """Test metadata facade module imports and __all__."""
    # Test import and __all__ content
    assert hasattr(metadata_module, "__all__")
    assert "FlextDbOracleMetadataManager" in metadata_module.__all__

    # Test actual import works
    assert hasattr(metadata_module, "FlextDbOracleMetadataManager")

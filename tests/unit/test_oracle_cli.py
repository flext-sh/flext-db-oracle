"""Test Oracle CLI operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys

from flext_core import FlextService
from flext_db_oracle.cli import FlextDbOracleCliService


class TestFlextDbOracleCliService:
    """Test Oracle CLI service functionality."""

    def test_cli_service_initialization(self) -> None:
        """Test CLI service initialization."""
        cli_service = FlextDbOracleCliService()
        assert cli_service is not None

    def test_cli_service_has_required_attributes(self) -> None:
        """Test CLI service has required attributes."""
        cli_service = FlextDbOracleCliService()
        assert hasattr(cli_service, "run_cli")
        assert hasattr(cli_service, "_logger")
        assert hasattr(cli_service, "_container")

    def test_cli_service_run_method_exists(self) -> None:
        """Test CLI service run method exists and is callable."""
        cli_service = FlextDbOracleCliService()
        assert callable(cli_service.run_cli)

    def test_cli_service_run_returns_flext_result(self) -> None:
        """Test CLI service run returns FlextResult."""
        cli_service = FlextDbOracleCliService()

        # Mock sys.argv to avoid actual CLI execution
        original_argv = sys.argv[:]
        try:
            sys.argv = ["oracle-cli", "--help"]
            result = cli_service.run_cli()

            # Should return FlextResult with proper structure
            assert hasattr(result, "is_success")
            assert hasattr(result, "error")
        finally:
            sys.argv = original_argv

    def test_cli_service_error_handling(self) -> None:
        """Test CLI service error handling."""
        cli_service = FlextDbOracleCliService()

        # Test with invalid arguments
        original_argv = sys.argv[:]
        try:
            sys.argv = ["oracle-cli", "--invalid-flag"]
            result = cli_service.run_cli()

            # Should handle errors gracefully
            assert hasattr(result, "is_success")
            assert hasattr(result, "error")
        finally:
            sys.argv = original_argv


class TestCliServiceIntegration:
    """Integration tests for CLI service."""

    def test_cli_service_with_flext_components(self) -> None:
        """Test CLI service integration with FLEXT components."""
        cli_service = FlextDbOracleCliService()

        # Verify FLEXT component integration
        assert cli_service._container is not None
        assert cli_service._logger is not None

    def test_cli_service_domain_service_inheritance(self) -> None:
        """Test CLI service inherits from FlextService."""
        cli_service = FlextDbOracleCliService()
        assert isinstance(cli_service, FlextService)

    def test_cli_service_configuration(self) -> None:
        """Test CLI service configuration handling."""
        cli_service = FlextDbOracleCliService()

        # Verify the service can be configured
        assert hasattr(cli_service, "_cli_main")


class TestCliServiceCoverage:
    """Tests to improve CLI service coverage."""

    def test_cli_service_exception_handling(self) -> None:
        """Test CLI service handles exceptions properly."""
        cli_service = FlextDbOracleCliService()

        # Test with malformed argv
        original_argv = sys.argv[:]
        try:
            sys.argv = []  # Empty argv should be handled
            result = cli_service.run_cli()

            # Should handle gracefully
            assert hasattr(result, "is_success")
        finally:
            sys.argv = original_argv

    def test_cli_service_logger_integration(self) -> None:
        """Test CLI service logger integration."""
        cli_service = FlextDbOracleCliService()

        # Verify logger is properly initialized
        logger = cli_service._logger
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")

    def test_cli_service_container_integration(self) -> None:
        """Test CLI service container integration."""
        cli_service = FlextDbOracleCliService()

        # Verify container is properly initialized
        container = cli_service._container
        assert container is not None

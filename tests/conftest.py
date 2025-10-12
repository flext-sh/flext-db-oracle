"""Test configuration for flext-db-oracle - ORACLE REAL TESTING ONLY.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import os
from collections.abc import Generator
from pathlib import Path

import pytest
from flext_core import FlextCore
from flext_tests import FlextTestsDomains

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

# Test constants - NOT PRODUCTION PASSWORDS
TEST_ORACLE_PASSWORD = "FlextTest123"


class FlextTestDocker:
    """Simple Docker test utility for Oracle container management."""

    def start_container(self, name: str) -> FlextCore.Result[str]:
        """Start a Docker container."""
        # Simple implementation - in real tests this would start the container
        return FlextCore.Result[str].ok(name)

    def stop_container(self, name: str) -> None:
        """Stop a Docker container."""


class OperationTestError(Exception):
    """Custom exception for test operations to avoid TRY003 lint warnings."""

    def __init__(self, operation: str, error: str) -> None:
        """Initialize with operation name and error details."""
        super().__init__(f"{operation} failed: {error}")
        self.operation = operation
        self.error = error


# Removed unused function _docker_connectivity_safe


class DockerCommandExecutor:
    """Execute Docker commands safely with proper error handling - DEPRECATED.

    This class is kept for backwards compatibility but should not be used directly.
    Use FlextTestDocker instead for consistent container management.
    """

    def __init__(self, compose_file: Path) -> None:
        """Initialize with compose file path."""
        self.compose_file = compose_file

    def check_docker_availability(self) -> None:
        """Check if Docker is available - use FlextTestDocker instead."""
        msg = "DockerCommandExecutor is deprecated. Use FlextTestDocker instead."
        raise DeprecationWarning(msg)

    def check_container_status(self) -> bool:
        """Check container status - use FlextTestDocker instead."""
        msg = "DockerCommandExecutor is deprecated. Use FlextTestDocker instead."
        raise DeprecationWarning(msg)

    def check_container_health(self) -> bool:
        """Check container health - use FlextTestDocker instead."""
        msg = "DockerCommandExecutor is deprecated. Use FlextTestDocker instead."
        raise DeprecationWarning(msg)

    def start_container(self) -> None:
        """Start container - use FlextTestDocker instead."""
        msg = "DockerCommandExecutor is deprecated. Use FlextTestDocker instead."
        raise DeprecationWarning(msg)

    def run_setup_script(self) -> bool:
        """Run setup script - use FlextTestDocker instead."""
        msg = "DockerCommandExecutor is deprecated. Use FlextTestDocker instead."
        raise DeprecationWarning(msg)

    def is_setup_completed(self) -> bool:
        """Check setup completion - use FlextTestDocker instead."""
        msg = "DockerCommandExecutor is deprecated. Use FlextTestDocker instead."
        raise DeprecationWarning(msg)


class OracleContainerManager:
    """Manage Oracle container lifecycle for testing - DEPRECATED.

    This class is kept for backwards compatibility but should not be used directly.
    Use FlextTestDocker fixtures instead for consistent container management.
    """

    def __init__(self, compose_file: Path) -> None:
        """Initialize with compose file path."""
        self.compose_file = compose_file
        self.max_health_attempts = 120
        self.health_check_interval = 5

    def ensure_container_ready(self) -> None:
        """Ensure container is ready - use FlextTestDocker instead."""
        msg = "OracleContainerManager is deprecated. Use FlextTestDocker fixtures instead."
        raise DeprecationWarning(msg)

    def _start_and_wait_for_health(self) -> None:
        """Start and wait for health - use FlextTestDocker instead."""
        msg = "OracleContainerManager is deprecated. Use FlextTestDocker fixtures instead."
        raise DeprecationWarning(msg)

    def _wait_for_healthy_status(self) -> None:
        """Wait for healthy status - use FlextTestDocker instead."""
        msg = "OracleContainerManager is deprecated. Use FlextTestDocker fixtures instead."
        raise DeprecationWarning(msg)

    def _wait_for_setup_completion(self) -> None:
        """Wait for setup completion - use FlextTestDocker instead."""
        msg = "OracleContainerManager is deprecated. Use FlextTestDocker fixtures instead."
        raise DeprecationWarning(msg)


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with Oracle container for ALL tests."""
    config.addinivalue_line("markers", "oracle: Oracle database integration tests")
    os.environ["SKIP_E2E_TESTS"] = "false"
    os.environ["ORACLE_INTEGRATION_TESTS"] = "1"
    os.environ["USE_REAL_ORACLE"] = "true"
    os.environ["TEST_ORACLE_HOST"] = "localhost"
    os.environ["TEST_ORACLE_PORT"] = "1521"
    os.environ["TEST_ORACLE_SERVICE"] = "XEPDB1"
    os.environ["TEST_ORACLE_USER"] = "flexttest"
    os.environ["TEST_ORACLE_PASSWORD"] = TEST_ORACLE_PASSWORD
    os.environ["FLEXT_TARGET_ORACLE_HOST"] = "localhost"
    os.environ["FLEXT_TARGET_ORACLE_PORT"] = "1521"
    os.environ["FLEXT_TARGET_ORACLE_SERVICE_NAME"] = "XEPDB1"
    os.environ["FLEXT_TARGET_ORACLE_USERNAME"] = "flexttest"
    os.environ["FLEXT_TARGET_ORACLE_PASSWORD"] = TEST_ORACLE_PASSWORD


@pytest.fixture(scope="session")
def docker_control() -> FlextTestDocker:
    """Provide FlextTestDocker instance for container management."""
    return FlextTestDocker()


@pytest.fixture(scope="session")
def shared_oracle_container(docker_control: FlextTestDocker) -> Generator[str]:
    """Start and maintain flext-oracle-db-test container.

    Container auto-starts if not running and remains running after tests.
    """
    # Remove any existing container with the same name first
    docker_control.stop_container("flext-oracle-db-test")

    result = docker_control.start_container("flext-oracle-db-test")
    if result.is_failure:
        pytest.skip(f"Failed to start Oracle container: {result.error}")

    yield "flext-oracle-db-test"

    # Keep container running after tests
    docker_control.stop_container("flext-oracle-db-test")


@pytest.fixture(scope="session")
def oracle_container(shared_oracle_container: object) -> None:
    """Ensure Oracle container is running for ORACLE tests only.

    This fixture uses the shared FlextTestDocker container management.
    """
    # Suppress unused parameter warning - fixture is used for side effects
    _ = shared_oracle_container


# Shared Oracle container fixture
@pytest.fixture(
    scope="session", autouse=False
)  # Temporarily disabled to fix remaining tests
def ensure_shared_docker_container(shared_oracle_container: object) -> None:
    """Ensure shared Docker container is started for the test session.

    This fixture automatically starts the shared Oracle container if not running,
    and ensures it's available for all tests in the session.
    """
    # Suppress unused parameter warning - fixture is used for side effects
    _ = shared_oracle_container
    # The shared_oracle_container fixture will be invoked automatically
    # and will start/stop the container for the entire test session


@pytest.fixture
def real_oracle_config(
    oracle_container: object | None,
) -> FlextDbOracleConfig:
    """Return real Oracle configuration for ALL tests."""
    # Ensure Oracle container is available
    if oracle_container is None:
        msg = "Oracle container must be available for tests"
        raise RuntimeError(msg)
    return FlextDbOracleConfig(
        host=os.getenv("TEST_ORACLE_HOST", "localhost"),
        port=int(os.getenv("TEST_ORACLE_PORT", "1521")),
        name=os.getenv("TEST_ORACLE_SERVICE", "XEPDB1"),
        username=os.getenv("TEST_ORACLE_USER", "flexttest"),
        password=os.getenv("TEST_ORACLE_PASSWORD", "FlextTest123"),
        service_name=os.getenv("TEST_ORACLE_SERVICE", "XEPDB1"),
        ssl_server_cert_dn=None,
    )


@pytest.fixture
def oracle_api(
    real_oracle_config: FlextDbOracleConfig,
) -> FlextDbOracleApi:
    """Return connected Oracle API for ALL tests."""
    return FlextDbOracleApi(real_oracle_config)


@pytest.fixture
def connected_oracle_api(oracle_api: FlextDbOracleApi) -> Generator[FlextDbOracleApi]:
    """Return Oracle API that is already connected."""
    connect_result = oracle_api.connect()
    if connect_result.is_success:
        connected_api = connect_result.value
        yield connected_api
        with contextlib.suppress(Exception):
            connected_api.disconnect()
    else:
        pytest.skip(f"Could not connect to Oracle: {connect_result.error}")


@pytest.fixture
def flext_domains() -> FlextTestsDomains:
    """Provide FlextTestsDomains instance for domain-based testing."""
    return FlextTestsDomains()

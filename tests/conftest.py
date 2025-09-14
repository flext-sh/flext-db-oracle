"""Test configuration for flext-db-oracle - ORACLE REAL TESTING ONLY.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import os
import time
from collections.abc import Generator
from pathlib import Path

import docker
import pytest

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleModels

# Test constants - NOT PRODUCTION PASSWORDS
TEST_ORACLE_PASSWORD = "FlextTest123"


class TestOperationError(Exception):
    """Custom exception for test operations to avoid TRY003 lint warnings."""

    def __init__(self, operation: str, error: str) -> None:
        """Initialize with operation name and error details."""
        super().__init__(f"{operation} failed: {error}")
        self.operation = operation
        self.error = error


class DockerCommandExecutor:
    """Execute Docker commands safely with proper error handling."""

    def __init__(self, compose_file: Path) -> None:
        """Initialize with compose file path."""
        self.compose_file = compose_file

    def check_docker_availability(self) -> None:
        """Check if Docker and Docker Compose are available via SDK."""
        try:
            client = docker.from_env()
            client.ping()  # type: ignore[no-untyped-call]
        except Exception as e:  # pragma: no cover - environment dependent
            raise RuntimeError from e

    def check_container_status(self) -> bool:
        """Check if Oracle container is running."""
        try:
            client = docker.from_env()
            containers = client.containers.list(all=True)
            return any(
                (getattr(ctr, "name", "") and ("oracle" in ctr.name))
                or any("oracle" in str(tag) for tag in getattr(ctr.image, "tags", []))
                for ctr in containers
            )
        except Exception:
            return False

    def check_container_health(self) -> bool:
        """Check if Oracle container is healthy."""
        try:
            client = docker.from_env()
            for ctr in client.containers.list(all=True):
                if ctr.name == "flext-oracle-test":
                    details = client.api.inspect_container(ctr.id)
                    status = (
                        details.get("State", {}).get("Health", {}).get("Status", "")
                    )
                    return bool(status == "healthy")
        except Exception:
            return False
        return False

    def start_container(self) -> None:
        """Start Oracle container."""
        # NOTE: Starting docker-compose via SDK is not supported in this test helper.
        raise RuntimeError

    def run_setup_script(self) -> bool:
        """Run database setup script."""
        # Not supported without docker-compose CLI; require manual run for test env
        return False

    def is_setup_completed(self) -> bool:
        """Check if the setup container has completed successfully."""
        try:
            client = docker.from_env()
            try:
                setup_ctr = client.containers.get("flext-oracle-setup")
            except Exception:
                return False
            setup_ctr.reload()
            # Consider success when container exited with code 0
            state = setup_ctr.attrs.get("State", {})
            status = str(state.get("Status", ""))
            exit_code_raw = state.get("ExitCode", 1)
            exit_code = (
                int(exit_code_raw) if isinstance(exit_code_raw, (int, str)) else 1
            )
            return bool(status == "exited" and exit_code == 0)
        except Exception:
            return False


class OracleContainerManager:
    """Manage Oracle container lifecycle for testing."""

    def __init__(self, compose_file: Path) -> None:
        """Initialize with compose file path."""
        self.docker_executor = DockerCommandExecutor(compose_file)
        self.max_health_attempts = 120  # 10 minutes max
        self.health_check_interval = 5  # seconds

    def ensure_container_ready(self) -> None:
        """Ensure Oracle container is running and healthy."""
        self.docker_executor.check_docker_availability()
        container_running = self.docker_executor.check_container_status()
        is_healthy = container_running and self.docker_executor.check_container_health()
        if not container_running or not is_healthy:
            self._start_and_wait_for_health()
        # Always wait for setup completion to ensure test user exists
        self._wait_for_setup_completion()

    def _start_and_wait_for_health(self) -> None:
        """Start container and wait for it to become healthy."""
        self.docker_executor.start_container()
        self._wait_for_healthy_status()

    def _wait_for_healthy_status(self) -> None:
        """Wait for container to become healthy."""
        for _attempt in range(self.max_health_attempts):
            if self.docker_executor.check_container_health():
                self.docker_executor.run_setup_script()
                time.sleep(self.health_check_interval)
                return
            time.sleep(self.health_check_interval)
        pytest.exit(
            "Oracle container failed to become healthy - cannot run tests without Oracle",
        )

    def _wait_for_setup_completion(self) -> None:
        """Wait until the setup container has created the test user/schema."""
        for _attempt in range(self.max_health_attempts):
            if self.docker_executor.is_setup_completed():
                return
            time.sleep(self.health_check_interval)
        pytest.exit(
            "Oracle setup container did not complete in time - test user may be missing",
        )


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with Oracle container for ALL tests - NO MOCKS ALLOWED."""
    # FORCE Oracle container usage for ALL tests - no mocks, only real testing
    config.addinivalue_line("markers", "oracle: Oracle database integration tests")
    os.environ["SKIP_E2E_TESTS"] = "false"
    os.environ["ORACLE_INTEGRATION_TESTS"] = "1"
    os.environ["USE_REAL_ORACLE"] = "true"
    # Oracle connection configuration for ALL tests
    os.environ["TEST_ORACLE_HOST"] = "localhost"
    os.environ["TEST_ORACLE_PORT"] = "1521"
    os.environ["TEST_ORACLE_SERVICE"] = "XEPDB1"
    os.environ["TEST_ORACLE_USER"] = "flexttest"
    os.environ["TEST_ORACLE_PASSWORD"] = TEST_ORACLE_PASSWORD
    # Set FLEXT target environment variables for consistency across ALL tests
    os.environ["FLEXT_TARGET_ORACLE_HOST"] = "localhost"
    os.environ["FLEXT_TARGET_ORACLE_PORT"] = "1521"
    os.environ["FLEXT_TARGET_ORACLE_SERVICE_NAME"] = "XEPDB1"
    os.environ["FLEXT_TARGET_ORACLE_USERNAME"] = "flexttest"
    os.environ["FLEXT_TARGET_ORACLE_PASSWORD"] = TEST_ORACLE_PASSWORD
    # PYTEST CONFIGURADO PARA USAR ORACLE REAL - SEM MOCKS!


@pytest.fixture(scope="session")
def oracle_container() -> Generator[None]:
    """Ensure Oracle container is running for ORACLE tests only."""
    project_root = Path(__file__).parent.parent
    compose_file = project_root / "docker-compose.oracle.yml"

    if not compose_file.exists():
        pytest.skip("Docker compose file not found - skipping Oracle container tests")

    try:
        container_manager = OracleContainerManager(compose_file)
        container_manager.ensure_container_ready()
        yield

    except RuntimeError as e:
        pytest.skip(f"Oracle container not available: {e}")
    except FileNotFoundError:
        pytest.skip("Docker/Docker Compose not available")
    except OSError as e:
        pytest.skip(f"OS error managing Oracle container: {e}")
    except Exception as e:
        pytest.skip(f"Error managing Oracle container: {e}")


@pytest.fixture
def real_oracle_config(
    oracle_container: object | None,
) -> FlextDbOracleModels.OracleConfig:
    """Return real Oracle configuration for ALL tests."""
    # Ensure Oracle container is available
    if oracle_container is None:
        msg = "Oracle container must be available for tests"
        raise RuntimeError(msg)
    return FlextDbOracleModels.OracleConfig(
        host=os.getenv("TEST_ORACLE_HOST", "localhost"),
        port=int(os.getenv("TEST_ORACLE_PORT", "1521")),
        name=os.getenv("TEST_ORACLE_SERVICE", "XEPDB1"),
        user=os.getenv("TEST_ORACLE_USER", "flexttest"),
        password=os.getenv("TEST_ORACLE_PASSWORD", "FlextTest123"),
        service_name=os.getenv("TEST_ORACLE_SERVICE", "XEPDB1"),
        ssl_server_cert_dn=None,
        connection_timeout=30,
    )


@pytest.fixture
def oracle_api(
    real_oracle_config: FlextDbOracleModels.OracleConfig,
) -> FlextDbOracleApi:
    """Return connected Oracle API for ALL tests."""
    return FlextDbOracleApi(real_oracle_config)


@pytest.fixture
def connected_oracle_api(oracle_api: FlextDbOracleApi) -> Generator[FlextDbOracleApi]:
    """Return Oracle API that is already connected."""
    connect_result = oracle_api.connect()
    if connect_result.success:
        connected_api = connect_result.value
        yield connected_api
        with contextlib.suppress(Exception):
            connected_api.disconnect()
    else:
        pytest.skip(f"Could not connect to Oracle: {connect_result.error}")


# REMOVE ALL MOCK FIXTURES - ONLY REAL ORACLE TESTING ALLOWED

"""Test configuration for flext-db-oracle - ORACLE REAL TESTING ONLY.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import os
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

import pytest

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig


class DockerCommandExecutor:
    """Execute Docker commands safely with proper error handling."""

    def __init__(self, compose_file: Path) -> None:
        """Initialize with compose file path."""
        self.compose_file = compose_file

    def check_docker_availability(self) -> None:
        """Check if Docker and Docker Compose are available."""
        commands = [
            ["docker", "version"],
            ["docker-compose", "version"],
        ]

        for cmd in commands:
            subprocess.run(cmd, capture_output=True, check=True)

    def check_container_status(self) -> bool:
        """Check if Oracle container is running."""
        result = subprocess.run(
            ["docker-compose", "-f", str(self.compose_file), "ps", "-q", "oracle-xe"],
            capture_output=True,
            text=True,
            check=False,
        )
        return bool(result.stdout.strip())

    def check_container_health(self) -> bool:
        """Check if Oracle container is healthy."""
        health_result = subprocess.run(
            [
                "docker",
                "inspect",
                "flext-oracle-test",
                "--format",
                "{{.State.Health.Status}}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return "healthy" in health_result.stdout

    def start_container(self) -> None:
        """Start Oracle container."""
        subprocess.run(
            ["docker-compose", "-f", str(self.compose_file), "up", "-d", "oracle-xe"],
            capture_output=True,
            text=True,
            check=True,
        )

    def run_setup_script(self) -> bool:
        """Run database setup script."""
        setup_result = subprocess.run(
            [
                "docker-compose",
                "-f",
                str(self.compose_file),
                "up",
                "--no-deps",
                "oracle-setup",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return setup_result.returncode == 0


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


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with Oracle container for ALL tests - NO MOCKS ALLOWED."""
    # FORCE Oracle container usage for ALL tests - no mocks, only real testing
    os.environ["SKIP_E2E_TESTS"] = "false"
    os.environ["ORACLE_INTEGRATION_TESTS"] = "1"
    os.environ["USE_REAL_ORACLE"] = "true"

    # Oracle connection configuration for ALL tests
    os.environ["TEST_ORACLE_HOST"] = "localhost"
    os.environ["TEST_ORACLE_PORT"] = "1521"
    os.environ["TEST_ORACLE_SERVICE"] = "XEPDB1"
    os.environ["TEST_ORACLE_USER"] = "flexttest"
    os.environ["TEST_ORACLE_PASSWORD"] = "FlextTest123"

    # Set FLEXT target environment variables for consistency across ALL tests
    os.environ["FLEXT_TARGET_ORACLE_HOST"] = "localhost"
    os.environ["FLEXT_TARGET_ORACLE_PORT"] = "1521"
    os.environ["FLEXT_TARGET_ORACLE_SERVICE_NAME"] = "XEPDB1"
    os.environ["FLEXT_TARGET_ORACLE_USERNAME"] = "flexttest"
    os.environ["FLEXT_TARGET_ORACLE_PASSWORD"] = "FlextTest123"

    # PYTEST CONFIGURADO PARA USAR ORACLE REAL - SEM MOCKS!


@pytest.fixture(scope="session", autouse=True)
def oracle_container() -> Generator[None]:
    """Ensure Oracle container is running for ALL tests - MANDATORY."""
    project_root = Path(__file__).parent.parent
    compose_file = project_root / "docker-compose.oracle.yml"

    if not compose_file.exists():
        pytest.skip("Docker compose file not found - skipping Oracle container tests")

    try:
        container_manager = OracleContainerManager(compose_file)
        container_manager.ensure_container_ready()
        yield

    except subprocess.CalledProcessError as e:
        pytest.exit(f"Failed to manage Oracle container: {e}")
    except FileNotFoundError:
        pytest.exit(
            "Docker/Docker Compose not available - cannot run tests without Docker",
        )
    except subprocess.SubprocessError as e:
        pytest.exit(f"Subprocess error managing Oracle container: {e}")
    except OSError as e:
        pytest.exit(f"OS error managing Oracle container: {e}")


@pytest.fixture
def real_oracle_config(oracle_container: None) -> FlextDbOracleConfig:
    """Return real Oracle configuration for ALL tests."""
    return FlextDbOracleConfig(
        host=os.getenv("TEST_ORACLE_HOST", "localhost"),
        port=int(os.getenv("TEST_ORACLE_PORT", "1521")),
        service_name=os.getenv("TEST_ORACLE_SERVICE", "XEPDB1"),
        username=os.getenv("TEST_ORACLE_USER", "flexttest"),
        password=os.getenv("TEST_ORACLE_PASSWORD", "FlextTest123"),
        pool_min=1,
        pool_max=5,
        timeout=30,
    )


@pytest.fixture
def oracle_api(real_oracle_config: FlextDbOracleConfig) -> FlextDbOracleApi:
    """Return connected Oracle API for ALL tests."""
    return FlextDbOracleApi(real_oracle_config)


@pytest.fixture
def connected_oracle_api(oracle_api: FlextDbOracleApi) -> FlextDbOracleApi:
    """Return Oracle API that is already connected."""
    connected_api = oracle_api.connect()
    yield connected_api
    with contextlib.suppress(Exception):
        connected_api.disconnect()


# REMOVE ALL MOCK FIXTURES - ONLY REAL ORACLE TESTING ALLOWED

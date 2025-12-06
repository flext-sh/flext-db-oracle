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
from typing import Any

import oracledb
import pytest
from flext_core import FlextLogger
from flext_tests import FlextTestsDocker, FlextTestsDomains

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

logger = FlextLogger(__name__)

# Register FlextTestsDocker pytest fixtures in this module's namespace
FlextTestsDocker.register_pytest_fixtures(namespace=globals())

# Test constants - NOT PRODUCTION PASSWORDS
TEST_ORACLE_PASSWORD = "FlextTest123"


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
    Use FlextTestsDocker instead for consistent container management.
    """

    def __init__(self, compose_file: Path) -> None:
        """Initialize with compose file path."""
        super().__init__()
        self.compose_file = compose_file

    def check_docker_availability(self) -> None:
        """Check if Docker is available - use FlextTestsDocker instead."""
        msg = "DockerCommandExecutor is deprecated. Use FlextTestsDocker instead."
        raise DeprecationWarning(msg)

    def check_container_status(self) -> bool:
        """Check container status - use FlextTestsDocker instead."""
        msg = "DockerCommandExecutor is deprecated. Use FlextTestsDocker instead."
        raise DeprecationWarning(msg)

    def check_container_health(self) -> bool:
        """Check container health - use FlextTestsDocker instead."""
        msg = "DockerCommandExecutor is deprecated. Use FlextTestsDocker instead."
        raise DeprecationWarning(msg)

    def start_container(self) -> None:
        """Start container - use FlextTestsDocker instead."""
        msg = "DockerCommandExecutor is deprecated. Use FlextTestsDocker instead."
        raise DeprecationWarning(msg)

    def run_setup_script(self) -> bool:
        """Run setup script - use FlextTestsDocker instead."""
        msg = "DockerCommandExecutor is deprecated. Use FlextTestsDocker instead."
        raise DeprecationWarning(msg)

    def is_setup_completed(self) -> bool:
        """Check setup completion - use FlextTestsDocker instead."""
        msg = "DockerCommandExecutor is deprecated. Use FlextTestsDocker instead."
        raise DeprecationWarning(msg)


class OracleContainerManager:
    """Manage Oracle container lifecycle for testing - DEPRECATED.

    This class is kept for backwards compatibility but should not be used directly.
    Use FlextTestsDocker fixtures instead for consistent container management.
    """

    def __init__(self, compose_file: Path) -> None:
        """Initialize with compose file path."""
        super().__init__()
        self.compose_file = compose_file
        self.max_health_attempts = 120
        self.health_check_interval = 5

    def ensure_container_ready(self) -> None:
        """Ensure container is ready - use FlextTestsDocker instead."""
        msg = "OracleContainerManager is deprecated. Use FlextTestsDocker fixtures instead."
        raise DeprecationWarning(msg)

    def _start_and_wait_for_health(self) -> None:
        """Start and wait for health - use FlextTestsDocker instead."""
        msg = "OracleContainerManager is deprecated. Use FlextTestsDocker fixtures instead."
        raise DeprecationWarning(msg)

    def _wait_for_healthy_status(self) -> None:
        """Wait for healthy status - use FlextTestsDocker instead."""
        msg = "OracleContainerManager is deprecated. Use FlextTestsDocker fixtures instead."
        raise DeprecationWarning(msg)

    def _wait_for_setup_completion(self) -> None:
        """Wait for setup completion - use FlextTestsDocker instead."""
        msg = "OracleContainerManager is deprecated. Use FlextTestsDocker fixtures instead."
        raise DeprecationWarning(msg)


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with Oracle container for ALL tests."""
    # Add markers for different test types
    config.addinivalue_line("markers", "oracle: Oracle database integration tests")
    config.addinivalue_line(
        "markers",
        "unit_pure: Pure unit tests with no external dependencies",
    )
    config.addinivalue_line(
        "markers",
        "unit_integration: Unit tests that can use real Oracle when available",
    )
    config.addinivalue_line(
        "markers",
        "slow: Slow-running tests that should be run separately",
    )

    # Environment configuration for Oracle tests
    os.environ["SKIP_E2E_TESTS"] = "false"
    os.environ["ORACLE_INTEGRATION_TESTS"] = "1"
    os.environ["USE_REAL_ORACLE"] = "true"


# =============================================================================
# PYTEST HOOKS (Container Lifecycle & Dirty State Management)
# =============================================================================


def pytest_sessionstart(session: pytest.Session) -> None:
    """Cleanup dirty containers BEFORE test session starts."""
    docker = FlextTestsDocker()
    cleanup_result = docker.cleanup_dirty_containers()
    if cleanup_result.is_failure:
        logger.warning(f"Dirty container cleanup failed: {cleanup_result.error}")
    else:
        cleaned = cleanup_result.unwrap()
        if cleaned:
            logger.info("Recreated dirty containers: %s", cleaned)
        else:
            logger.debug("No dirty containers to clean")


def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> None:
    """Mark container dirty on Oracle service failures."""
    if call.excinfo is None:
        return

    exc_type = call.excinfo.type
    exc_msg = str(call.excinfo.value).lower()

    # Lista de erros que indicam FALHA REAL DO SERVIÇO ORACLE
    oracle_service_errors = [
        "ora-",  # Oracle error codes
        "connection refused",
        "connection reset by peer",
        "broken pipe",
        "database not available",
        "tns:",  # TNS errors
    ]

    is_service_failure = any(
        err in str(exc_type).lower() or err in exc_msg for err in oracle_service_errors
    )

    if is_service_failure:
        docker = FlextTestsDocker()
        docker.mark_container_dirty("flext-oracle-db-test")
        logger.error(
            f"ORACLE SERVICE FAILURE detected in {item.nodeid}, "
            f"container marked DIRTY for recreation: {exc_msg}",
        )


@pytest.fixture(scope="session")
def docker_control() -> FlextTestsDocker:
    """Provide FlextTestsDocker instance for container management."""
    return FlextTestsDocker()


@pytest.fixture(scope="session")
def shared_oracle_container(
    docker_control: FlextTestsDocker,
) -> Generator[str]:
    """Start and maintain flext-oracle-db-test container using same pattern as flext-ldap."""
    container_name = "flext-oracle-db-test"

    # Get container config from SHARED_CONTAINERS
    container_config = FlextTestsDocker.SHARED_CONTAINERS.get(container_name)
    if container_config is None:
        pytest.skip(f"Container {container_name} not found in SHARED_CONTAINERS")

    # Get compose file path
    compose_file_value = container_config.get("compose_file")
    if compose_file_value is None:
        pytest.skip(f"Container {container_name} missing compose_file config")
    compose_file = str(compose_file_value)
    if not compose_file.startswith("/"):
        # Relative path, make it absolute from workspace root
        # Workspace root is /home/marlonsc/flext
        # compose_file from SHARED_CONTAINERS is "docker/docker-compose.oracle-db.yml"
        workspace_root = Path("/home/marlonsc/flext")
        compose_file = str(workspace_root / compose_file)

    # REGRA: Só recriar se estiver dirty, senão apenas iniciar se não estiver rodando
    is_dirty = docker_control.is_container_dirty(container_name)

    if is_dirty:
        # Container está dirty - recriar completamente (down -v + up)
        logger.info(
            "Container %s is dirty, recreating with fresh volumes",
            container_name,
        )
        cleanup_result = docker_control.cleanup_dirty_containers()
        if cleanup_result.is_failure:
            pytest.skip(
                f"Failed to recreate dirty container {container_name}: {cleanup_result.error}",
            )
        # cleanup_dirty_containers já faz down -v e up, então container deve estar rodando agora
    else:
        # Container não está dirty - apenas verificar se está rodando e iniciar se necessário
        status = docker_control.get_container_status(container_name)
        container_running = (
            status.is_success
            and isinstance(status.value, FlextTestsDocker.ContainerInfo)
            and status.value.status == FlextTestsDocker.ContainerStatus.RUNNING
        )

        if not container_running:
            # Container não está rodando mas não está dirty - apenas iniciar (sem recriar volumes)
            logger.info(
                "Container %s is not running (but not dirty), starting...",
                container_name,
            )
            service_name = str(container_config.get("service", ""))
            compose_result = docker_control.compose_up(
                compose_file,
                service=service_name or None,
            )
            if compose_result.is_failure:
                pytest.skip(
                    f"Failed to start container {container_name}: {compose_result.error}",
                )
        else:
            # Container está rodando e não está dirty - tudo OK
            logger.debug(
                "Container %s is running and clean, no action needed",
                container_name,
            )

    # AGUARDAR container estar pronto antes de permitir testes
    # Usar healthcheck do Docker se disponível, senão tentar conexão Oracle
    max_wait: int = 300  # segundos (5 minutos para Oracle)
    wait_interval: float = 5.0  # segundos
    waited: float = 0.0

    logger.info("Waiting for container %s to be ready...", container_name)

    while waited < max_wait:
        try:
            # Usar configurações do container
            dsn = oracledb.makedsn("localhost", 1522, service_name="FLEXTDB")
            connection = oracledb.connect(
                user="flext_test",
                password="flext_test_password",
                dsn=dsn,
            )
            connection.close()
            logger.info(f"Container {container_name} is ready after {waited:.1f}s")
            break
        except Exception as e:
            # Container ainda não está pronto, continuar aguardando
            if waited % 30 == 0:  # Log a cada 30 segundos
                logger.debug(
                    f"Container {container_name} not ready yet (waited {waited:.1f}s): {e}",
                )

        time.sleep(wait_interval)
        waited += wait_interval

    if waited >= max_wait:
        pytest.skip(
            f"Container {container_name} did not become ready within {max_wait}s",
        )

    return container_name

    # Keep container running after tests for future test runs
    # Only stop if explicitly requested or if there were infrastructure failures


@pytest.fixture(scope="session")
def oracle_container(shared_oracle_container: object) -> str:
    """Provide Oracle container name for all tests.

    This fixture ensures the Oracle container is running and provides its name.
    """
    # Return the container name
    return shared_oracle_container


# Shared Oracle container fixture - NOW AUTOUSED FOR ALL TESTS
@pytest.fixture(scope="session", autouse=True)
def ensure_shared_docker_container(shared_oracle_container: str) -> None:
    """Ensure shared Docker container is started for ALL tests in the session.

    This fixture automatically starts the shared Oracle container if not running,
    and ensures it's available for all unit and integration tests.
    """
    # Suppress unused parameter warning - fixture ensures container is running
    _ = shared_oracle_container
    # The shared_oracle_container fixture will be invoked automatically
    # and will start/stop the container for the entire test session


@pytest.fixture
def real_oracle_config(
    oracle_container: str | None,
) -> FlextDbOracleConfig | None:
    """Return real Oracle configuration for tests that can use it."""
    # If Oracle container is not available, return None to allow tests to be skipped
    if oracle_container is None:
        return None
    return FlextDbOracleConfig(
        host=os.getenv("TEST_ORACLE_HOST", "localhost"),
        port=int(os.getenv("TEST_ORACLE_PORT", "1521")),
        name=os.getenv("TEST_ORACLE_SERVICE", "XEPDB1"),
        username=os.getenv("TEST_ORACLE_USER", "flexttest"),
        password=os.getenv("TEST_ORACLE_PASSWORD", TEST_ORACLE_PASSWORD),
        service_name=os.getenv("TEST_ORACLE_SERVICE", "XEPDB1"),
        ssl_server_cert_dn=None,
    )


@pytest.fixture
def oracle_api(
    real_oracle_config: FlextDbOracleConfig | None,
) -> FlextDbOracleApi | None:
    """Return Oracle API for tests that can use it."""
    if real_oracle_config is None:
        return None
    return FlextDbOracleApi(config=real_oracle_config)


@pytest.fixture
def connected_oracle_api(
    oracle_api: FlextDbOracleApi | None,
) -> Generator[FlextDbOracleApi | None]:
    """Return Oracle API that is already connected."""
    if oracle_api is None:
        yield None
        return

    connect_result = oracle_api.connect()
    if connect_result.is_success:
        connected_api = connect_result.value
        yield connected_api
        with contextlib.suppress(Exception):
            connected_api.disconnect()
    else:
        # Don't skip - just return None to allow tests to handle gracefully
        yield None


@pytest.fixture
def flext_domains() -> FlextTestsDomains:
    """Provide FlextTestsDomains instance for domain-based testing."""
    return FlextTestsDomains()


@pytest.fixture
def mock_oracle_config() -> FlextDbOracleConfig:
    """Provide mock Oracle config for tests when real Oracle is not available."""
    return FlextDbOracleConfig(
        host="mock-host",
        port=1521,
        service_name="mock-service",
        username="mock-user",
        password="mock-pass",
    )


@pytest.fixture
def oracle_config(
    real_oracle_config: FlextDbOracleConfig | None,
    mock_oracle_config: FlextDbOracleConfig,
) -> FlextDbOracleConfig:
    """Provide Oracle config - real if available, mock otherwise."""
    return real_oracle_config or mock_oracle_config


@pytest.fixture
def oracle_available(connected_oracle_api: FlextDbOracleApi | None) -> bool:
    """Check if Oracle is available for testing."""
    return connected_oracle_api is not None


@pytest.fixture(autouse=True)
def test_cleanup(connected_oracle_api: FlextDbOracleApi | None) -> Generator[None]:
    """Ensure test idempotency by cleaning up test data before and after tests."""
    # Pre-test cleanup - only if Oracle is available
    if connected_oracle_api is not None:
        try:
            # Clean up any test tables/data created by previous tests
            cleanup_queries = [
                "DROP TABLE test_table CASCADE",
                "DROP TABLE flext_test_table CASCADE",
                "DROP TABLE test_data_types CASCADE",
                "DROP SEQUENCE test_seq CASCADE",
                "DROP SEQUENCE flext_test_seq CASCADE",
            ]
            for query in cleanup_queries:
                try:
                    # Use PL/SQL to ignore errors if table doesn't exist
                    plsql_query = f"""
                    BEGIN
                        EXECUTE IMMEDIATE '{query}';
                    EXCEPTION
                        WHEN OTHERS THEN
                            NULL; -- Ignore errors
                    END;
                    """
                    connected_oracle_api.execute_statement(plsql_query)
                except Exception:
                    # Ignore cleanup failures
                    pass
        except Exception:
            # Ignore cleanup failures completely
            pass

    yield

    # Post-test cleanup (ensure clean state for next test) - only if Oracle is available
    if connected_oracle_api is not None:
        try:
            # Additional cleanup after test execution
            post_cleanup_queries = [
                "DROP TABLE temp_test_table CASCADE",
                "DROP TABLE session_test_table CASCADE",
                "DROP TABLE test_oracle_escape CASCADE",
            ]
            for query in post_cleanup_queries:
                try:
                    # Use PL/SQL to ignore errors
                    plsql_query = f"""
                    BEGIN
                        EXECUTE IMMEDIATE '{query}';
                    EXCEPTION
                        WHEN OTHERS THEN
                            NULL; -- Ignore errors
                    END;
                    """
                    connected_oracle_api.execute_statement(plsql_query)
                except Exception:
                    pass
        except Exception:
            pass


@pytest.fixture
def test_database_setup(
    connected_oracle_api: FlextDbOracleApi | None,
) -> Generator[dict[str, str] | None]:
    """Set up test database schema and return test table info."""
    if connected_oracle_api is None:
        yield None
        return

    test_schema = {
        "test_table": "CREATE TABLE test_table (id NUMBER PRIMARY KEY, name VARCHAR2(100))",
        "test_sequence": "CREATE SEQUENCE test_seq START WITH 1 INCREMENT BY 1",
    }

    # Create test schema
    for ddl in test_schema.values():
        try:
            result = connected_oracle_api.execute_statement(ddl)
            if result.is_failure:
                pytest.skip(f"Could not create test schema: {result.error}")
        except Exception as e:
            pytest.skip(f"Test setup failed: {e}")

    yield test_schema

    # Cleanup will be handled by test_cleanup fixture

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
from pydantic import TypeAdapter, ValidationError

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings

logger = FlextLogger(__name__)
_PORT_BINDINGS_ADAPTER = TypeAdapter(dict[str, str])


class OperationTestError(Exception):
    """Custom exception for test operations to avoid TRY003 lint warnings."""

    def __init__(self, operation: str, error: str) -> None:
        """Initialize with operation name and error details."""
        super().__init__(f"{operation} failed: {error}")
        self.operation = operation
        self.error = error


def _normalized_port_bindings(value: object) -> dict[str, str]:
    try:
        return _PORT_BINDINGS_ADAPTER.validate_python(value)
    except ValidationError:
        return {}


def _resolve_oracle_test_port(
    docker_control: FlextTestsDocker, container_name: str
) -> int:
    env_port = os.getenv("TEST_ORACLE_PORT")
    if env_port is not None and env_port.isdigit():
        env_port_int = int(env_port)
        status_result = docker_control.get_container_status(container_name)
        if status_result.is_success:
            status_value = status_result.value
            ports = _normalized_port_bindings(getattr(status_value, "ports", {}))
            for container_port, host_port in ports.items():
                if (
                    container_port.startswith("1521")
                    and host_port.isdigit()
                    and int(host_port) == env_port_int
                ):
                    return env_port_int
    fallback_port = 1522
    container_config = FlextTestsDocker.SHARED_CONTAINERS.get(container_name)
    if container_config is not None:
        configured_port = container_config.get("port")
        if isinstance(configured_port, int):
            fallback_port = configured_port
    for _ in range(30):
        status_result = docker_control.get_container_status(container_name)
        if status_result.is_success:
            status_value = status_result.value
            ports = _normalized_port_bindings(getattr(status_value, "ports", {}))
            for container_port, host_port in ports.items():
                if container_port.startswith("1521") and host_port.isdigit():
                    return int(host_port)
        time.sleep(2)
    return fallback_port


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with Oracle container for ALL tests."""
    config.addinivalue_line("markers", "oracle: Oracle database integration tests")
    config.addinivalue_line(
        "markers", "unit_pure: Pure unit tests with no external dependencies"
    )
    config.addinivalue_line(
        "markers",
        "unit_integration: Unit tests that can use real Oracle when available",
    )
    config.addinivalue_line(
        "markers", "slow: Slow-running tests that should be run separately"
    )
    os.environ["SKIP_E2E_TESTS"] = "false"
    os.environ["ORACLE_INTEGRATION_TESTS"] = "1"
    os.environ["USE_REAL_ORACLE"] = "true"


def pytest_sessionstart(session: pytest.Session) -> None:
    """Cleanup dirty containers BEFORE test session starts."""
    try:
        docker = FlextTestsDocker(workspace_root=Path(__file__).resolve().parents[2])
        dirty_containers = docker.get_dirty_containers()
        if not dirty_containers:
            logger.debug("No dirty containers to clean")
            return
        container_name = "flext-oracle-db-test"
        status_result = docker.get_container_status(container_name)
        if status_result.is_success:
            status = status_result.value
            if status.status == docker.ContainerStatus.RUNNING:
                docker.mark_container_clean(container_name)
                logger.info(
                    f"Container {container_name} is healthy, cleared dirty state"
                )
                return
        cleanup_result = docker.cleanup_dirty_containers()
        if cleanup_result.is_failure:
            logger.warning(f"Dirty container cleanup failed: {cleanup_result.error}")
        else:
            cleaned = cleanup_result.value
            if cleaned:
                logger.info(f"Recreated dirty containers: {cleaned}")
            else:
                logger.debug("No dirty containers to clean")
    except Exception as e:
        logger.warning(f"Docker cleanup skipped (unavailable): {e}")


def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> None:
    """Mark container dirty on Oracle service failures."""
    if call.excinfo is None:
        return
    try:
        exc_type = call.excinfo.type
        exc_msg = str(call.excinfo.value).lower()
        oracle_service_errors = [
            "ora-",
            "connection refused",
            "connection reset by peer",
            "broken pipe",
            "database not available",
            "tns:",
        ]
        is_service_failure = any(
            err in str(exc_type).lower() or err in exc_msg
            for err in oracle_service_errors
        )
        if is_service_failure:
            docker = FlextTestsDocker(
                workspace_root=Path(__file__).resolve().parents[2]
            )
            docker.mark_container_dirty("flext-oracle-db-test")
            logger.error(
                f"ORACLE SERVICE FAILURE detected in {item.nodeid}, container marked DIRTY for recreation: {exc_msg}"
            )
    except Exception:
        pass


@pytest.fixture(scope="session")
def docker_control() -> FlextTestsDocker:
    """Provide FlextTestsDocker instance for container management."""
    return FlextTestsDocker(workspace_root=Path(__file__).resolve().parents[2])


@pytest.fixture(scope="session")
def shared_oracle_container(docker_control: FlextTestsDocker) -> str:
    """Start and maintain flext-oracle-db-test container using same pattern as flext-ldap."""
    container_name = "flext-oracle-db-test"
    container_config = FlextTestsDocker.SHARED_CONTAINERS.get(container_name)
    if container_config is None:
        pytest.skip(f"Container {container_name} not found in SHARED_CONTAINERS")
    compose_file_value = container_config.get("compose_file")
    if compose_file_value is None:
        pytest.skip(f"Container {container_name} missing compose_file config")
    compose_file = str(compose_file_value)
    if not compose_file.startswith("/"):
        workspace_root = Path(__file__).resolve().parents[2]
        compose_file = str(workspace_root / compose_file)
    is_dirty = docker_control.is_container_dirty(container_name)
    if is_dirty:
        logger.info(
            f"Container {container_name} is dirty, recreating with fresh volumes"
        )
        cleanup_result = docker_control.cleanup_dirty_containers()
        if cleanup_result.is_failure:
            pytest.skip(
                f"Failed to recreate dirty container {container_name}: {cleanup_result.error}"
            )
    else:
        status = docker_control.get_container_status(container_name)
        status_value = status.value if status.is_success else None
        status_name = getattr(status_value, "status", None)
        container_running = status.is_success and (
            status_name == FlextTestsDocker.ContainerStatus.RUNNING
        )
        if not container_running:
            logger.info(
                f"Container {container_name} is not running (but not dirty), starting..."
            )
            service_name = str(container_config.get("service", ""))
            compose_result = docker_control.compose_up(
                compose_file, service=service_name or None
            )
            if compose_result.is_failure:
                pytest.skip(
                    f"Failed to start container {container_name}: {compose_result.error}"
                )
        else:
            logger.debug(
                f"Container {container_name} is running and clean, no action needed"
            )
    resolved_port = _resolve_oracle_test_port(docker_control, container_name)
    os.environ["TEST_ORACLE_PORT"] = str(resolved_port)
    max_wait: int = 300
    wait_interval: float = 5.0
    waited: float = 0.0
    logger.info(f"Waiting for container {container_name} to be ready...")
    while waited < max_wait:
        try:
            dsn = oracledb.makedsn("localhost", resolved_port, service_name="FLEXTDB")
            connection = oracledb.connect(
                user="flext_test", password="flext_test_password", dsn=dsn
            )
            connection.close()
            logger.info(f"Container {container_name} is ready after {waited:.1f}s")
            break
        except Exception as e:
            if waited % 30 == 0:
                logger.debug(
                    f"Container {container_name} not ready yet (waited {waited:.1f}s): {e}"
                )
        time.sleep(wait_interval)
        waited += wait_interval
    if waited >= max_wait:
        pytest.skip(
            f"Container {container_name} did not become ready within {max_wait}s"
        )
    return container_name


@pytest.fixture(scope="session")
def oracle_container(shared_oracle_container: str) -> str:
    """Provide Oracle container name for all tests.

    This fixture ensures the Oracle container is running and provides its name.
    """
    return shared_oracle_container


@pytest.fixture(scope="session", autouse=True)
def ensure_shared_docker_container(shared_oracle_container: str) -> None:
    """Ensure shared Docker container is started for ALL tests in the session.

    This fixture automatically starts the shared Oracle container if not running,
    and ensures it's available for all unit and integration tests.
    """
    _ = shared_oracle_container


@pytest.fixture
def real_oracle_config(oracle_container: str | None) -> FlextDbOracleSettings:
    """Return real Oracle configuration for tests that can use it."""
    if oracle_container is None:
        pytest.skip("Oracle container unavailable")
    return FlextDbOracleSettings(
        host=os.getenv("TEST_ORACLE_HOST", "localhost"),
        port=int(os.getenv("TEST_ORACLE_PORT", "1522")),
        name=os.getenv("TEST_ORACLE_SERVICE", "FLEXTDB"),
        username=os.getenv("TEST_ORACLE_USER", "flext_test"),
        password=os.getenv("TEST_ORACLE_PASSWORD", "flext_test_password"),
        service_name=os.getenv("TEST_ORACLE_SERVICE", "FLEXTDB"),
        ssl_server_cert_dn=None,
    )


@pytest.fixture
def oracle_api(
    real_oracle_config: FlextDbOracleSettings,
) -> FlextDbOracleApi:
    """Return Oracle API for tests that can use it."""
    return FlextDbOracleApi(config=real_oracle_config)


@pytest.fixture
def connected_oracle_api(
    oracle_api: FlextDbOracleApi,
) -> Generator[FlextDbOracleApi]:
    """Return Oracle API that is already connected."""
    connect_result = oracle_api.connect()
    if connect_result.is_success:
        connected_api = connect_result.value
        yield connected_api
        with contextlib.suppress(Exception):
            connected_api.disconnect()
    else:
        pytest.skip(f"Failed to connect Oracle API: {connect_result.error}")


@pytest.fixture
def flext_domains() -> FlextTestsDomains:
    """Provide FlextTestsDomains instance for domain-based testing."""
    return FlextTestsDomains()


@pytest.fixture
def mock_oracle_config() -> FlextDbOracleSettings:
    """Provide mock Oracle config for tests when real Oracle is not available."""
    return FlextDbOracleSettings(
        host="mock-host",
        port=1521,
        service_name="mock-service",
        username="mock-user",
        password="mock-pass",
    )


@pytest.fixture
def oracle_config(
    real_oracle_config: FlextDbOracleSettings | None,
    mock_oracle_config: FlextDbOracleSettings,
) -> FlextDbOracleSettings:
    """Provide Oracle config - real if available, mock otherwise."""
    return real_oracle_config or mock_oracle_config


@pytest.fixture
def oracle_available(connected_oracle_api: FlextDbOracleApi | None) -> bool:
    """Check if Oracle is available for testing."""
    return connected_oracle_api is not None


@pytest.fixture(autouse=True)
def test_cleanup(connected_oracle_api: FlextDbOracleApi | None) -> Generator[None]:
    """Ensure test idempotency by cleaning up test data before and after tests."""
    if connected_oracle_api is not None:
        try:
            cleanup_queries = [
                "DROP TABLE test_table CASCADE",
                "DROP TABLE flext_test_table CASCADE",
                "DROP TABLE test_data_types CASCADE",
                "DROP SEQUENCE test_seq CASCADE",
                "DROP SEQUENCE flext_test_seq CASCADE",
            ]
            for query in cleanup_queries:
                try:
                    plsql_query = f"\n                    BEGIN\n                        EXECUTE IMMEDIATE '{query}';\n                    EXCEPTION\n                        WHEN OTHERS THEN\n                            NULL; -- Ignore errors\n                    END;\n                    "
                    connected_oracle_api.execute_statement(plsql_query)
                except Exception:
                    pass
        except Exception:
            pass
    yield
    if connected_oracle_api is not None:
        try:
            post_cleanup_queries = [
                "DROP TABLE temp_test_table CASCADE",
                "DROP TABLE session_test_table CASCADE",
                "DROP TABLE test_oracle_escape CASCADE",
            ]
            for query in post_cleanup_queries:
                try:
                    plsql_query = f"\n                    BEGIN\n                        EXECUTE IMMEDIATE '{query}';\n                    EXCEPTION\n                        WHEN OTHERS THEN\n                            NULL; -- Ignore errors\n                    END;\n                    "
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
    cleanup_ddl = ["DROP TABLE test_table PURGE", "DROP SEQUENCE test_seq"]
    for ddl in cleanup_ddl:
        try:
            connected_oracle_api.execute_statement(ddl)
        except Exception:
            pass
    for ddl in test_schema.values():
        try:
            result = connected_oracle_api.execute_statement(ddl)
            if result.is_failure:
                pytest.skip(f"Could not create test schema: {result.error}")
        except Exception as e:
            pytest.skip(f"Test setup failed: {e}")
    yield test_schema

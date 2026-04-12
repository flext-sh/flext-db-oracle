"""Test configuration for flext-db-oracle - ORACLE REAL TESTING ONLY.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import os
import time
from collections.abc import Callable, Generator
from pathlib import Path

import oracledb
import pytest
from flext_tests import td, tk

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings
from tests import t, u

pytest_plugins = ["flext_tests.conftest_plugin"]


@pytest.fixture
def db_oracle_settings(
    settings_factory: Callable[..., FlextDbOracleSettings],
) -> FlextDbOracleSettings:
    """Provide clean FlextDbOracleSettings for tests."""
    return settings_factory(FlextDbOracleSettings)


logger = u.fetch_logger(__name__)


class OperationTestError(Exception):
    """Custom exception for test operations to avoid TRY003 lint warnings."""

    def __init__(self, operation: str, error: str) -> None:
        """Initialize with operation name and error details."""
        super().__init__(f"{operation} failed: {error}")
        self.operation = operation
        self.error = error


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with Oracle container for ALL tests."""
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
    os.environ["SKIP_E2E_TESTS"] = "false"
    os.environ["ORACLE_INTEGRATION_TESTS"] = "1"
    os.environ["USE_REAL_ORACLE"] = "true"


def pytest_sessionstart(session: pytest.Session) -> None:
    """Cleanup dirty containers BEFORE test session starts."""
    try:
        docker = tk(workspace_root=Path(__file__).resolve().parents[2])
        dirty_containers = docker.dirty_containers
        if not dirty_containers:
            logger.debug("No dirty containers to clean")
            return
        container_name = "flext-oracle-db-test"
        status_result = docker.fetch_container_status(container_name)
        if status_result.success:
            status = status_result.value
            if status.status == docker.ContainerStatus.RUNNING:
                docker.mark_container_clean(container_name)
                logger.info(
                    "Container %s is healthy, cleared dirty state",
                    container_name,
                )
                return
        cleanup_result = docker.cleanup_dirty_containers()
        if cleanup_result.failure:
            logger.warning(f"Dirty container cleanup failed: {cleanup_result.error}")
        else:
            cleaned = cleanup_result.value
            if cleaned:
                logger.info("Recreated dirty containers: %s", cleaned)
            else:
                logger.debug("No dirty containers to clean")
    except (ConnectionError, TimeoutError, OSError, RuntimeError) as e:
        logger.warning(f"Docker cleanup skipped (unavailable): {e}")


def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> None:
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
            docker = tk(workspace_root=Path(__file__).resolve().parents[2])
            docker.mark_container_dirty("flext-oracle-db-test")
            logger.error(
                f"ORACLE SERVICE FAILURE detected in {item.nodeid}, container marked DIRTY for recreation: {exc_msg}",
            )
    except (ConnectionError, TimeoutError, OSError, RuntimeError):
        pass


@pytest.fixture(scope="session")
def docker_control() -> tk:
    """Provide tk instance for container management."""
    return tk(workspace_root=Path(__file__).resolve().parents[2])


@pytest.fixture(scope="session")
def shared_oracle_container(docker_control: tk) -> str:
    """Start and maintain flext-oracle-db-test container using same pattern as flext-ldap."""
    container_name = "flext-oracle-db-test"
    container_settings = tk.SHARED_CONTAINERS.get(container_name)
    if container_settings is None:
        pytest.skip(f"Container {container_name} not found in SHARED_CONTAINERS")
    compose_file_value = container_settings.get("compose_file")
    if compose_file_value is None:
        pytest.skip(f"Container {container_name} missing compose_file settings")
    compose_file = str(compose_file_value)
    if not compose_file.startswith("/"):
        workspace_root = Path(__file__).resolve().parents[2]
        compose_file = str(workspace_root / compose_file)
    is_dirty = docker_control.container_dirty(container_name)
    if is_dirty:
        logger.info(
            "Container %s is dirty, recreating with fresh volumes",
            container_name,
        )
        cleanup_result = docker_control.cleanup_dirty_containers()
        if cleanup_result.failure:
            pytest.skip(
                f"Failed to recreate dirty container {container_name}: {cleanup_result.error}",
            )
    else:
        status = docker_control.fetch_container_status(container_name)
        status_value = status.value if status.success else None
        status_name = getattr(status_value, "status", None)
        container_running = status.success and (
            status_name == tk.ContainerStatus.RUNNING
        )
        if not container_running:
            logger.info(
                "Container %s is not running (but not dirty), starting...",
                container_name,
            )
            service_name = str(container_settings.get("service", ""))
            compose_result = docker_control.compose_up(
                compose_file,
                service=service_name or None,
            )
            if compose_result.failure:
                pytest.skip(
                    f"Failed to start container {container_name}: {compose_result.error}",
                )
        else:
            logger.debug(
                "Container %s is running and clean, no action needed",
                container_name,
            )
    resolved_port = u.DbOracle.Tests.resolve_oracle_test_port(
        docker_control,
        container_name,
    )
    os.environ["TEST_ORACLE_PORT"] = str(resolved_port)
    max_wait: int = 300
    wait_interval: float = 5.0
    waited: float = 0.0
    logger.info("Waiting for container %s to be ready...", container_name)
    while waited < max_wait:
        try:
            dsn = oracledb.makedsn("localhost", resolved_port, service_name="FLEXTDB")
            connection = oracledb.connect(
                user="flext_test",
                password="flext_test_password",
                dsn=dsn,
            )
            connection.close()
            logger.info(f"Container {container_name} is ready after {waited:.1f}s")
            break
        except (oracledb.Error, ConnectionError, TimeoutError, OSError) as e:
            if waited % 30 == 0:
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


@pytest.fixture(scope="session")
def oracle_container(shared_oracle_container: str) -> str:
    """Provide Oracle container name for all tests.

    This fixture ensures the Oracle container is running and provides its name.
    """
    return shared_oracle_container


@pytest.fixture(scope="session")
def ensure_shared_docker_container(shared_oracle_container: str) -> None:
    """Ensure shared Docker container is started for tests that need it.

    Request this fixture explicitly in tests or conftest that need Oracle.
    """
    _ = shared_oracle_container


@pytest.fixture
def real_oracle_settings(oracle_container: str | None) -> FlextDbOracleSettings:
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
def real_oracle_config(
    real_oracle_settings: FlextDbOracleSettings,
) -> FlextDbOracleSettings:
    """Backward-compatible alias for legacy fixture name used in some tests."""
    return real_oracle_settings


@pytest.fixture
def oracle_config(
    real_oracle_config: FlextDbOracleSettings,
) -> FlextDbOracleSettings:
    """Backward-compatible alias for integration tests using ``oracle_config``."""
    return real_oracle_config


@pytest.fixture
def oracle_api(
    real_oracle_settings: FlextDbOracleSettings,
) -> FlextDbOracleApi:
    """Return Oracle API for tests that can use it."""
    return FlextDbOracleApi(settings=real_oracle_settings)


@pytest.fixture
def connected_oracle_api(
    oracle_api: FlextDbOracleApi,
) -> Generator[FlextDbOracleApi]:
    """Return Oracle API that is already connected."""
    connect_result = oracle_api.connect()
    if connect_result.success:
        connected_api = connect_result.value
        yield connected_api
        with contextlib.suppress(Exception):
            connected_api.disconnect()
    else:
        pytest.skip(f"Failed to connect Oracle API: {connect_result.error}")


@pytest.fixture
def flext_domains() -> td:
    """Provide td instance for domain-based testing."""
    return td()


@pytest.fixture
def mock_oracle_settings() -> FlextDbOracleSettings:
    """Provide mock Oracle settings for tests when real Oracle is not available."""
    return FlextDbOracleSettings(
        host="mock-host",
        port=1521,
        service_name="mock-service",
        username="mock-user",
        password="mock-pass",
    )


@pytest.fixture
def oracle_settings(
    real_oracle_settings: FlextDbOracleSettings | None,
    mock_oracle_settings: FlextDbOracleSettings,
) -> FlextDbOracleSettings:
    """Provide Oracle settings - real if available, mock otherwise."""
    return (
        real_oracle_settings
        if real_oracle_settings is not None
        else mock_oracle_settings
    )


@pytest.fixture
def oracle_available(connected_oracle_api: FlextDbOracleApi | None) -> bool:
    """Check if Oracle is available for testing."""
    return connected_oracle_api is not None


@pytest.fixture
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
                except (oracledb.Error, ConnectionError, OSError):
                    pass
        except (oracledb.Error, ConnectionError, OSError):
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
                except (oracledb.Error, ConnectionError, OSError):
                    pass
        except (oracledb.Error, ConnectionError, OSError):
            pass


@pytest.fixture
def test_database_setup(
    connected_oracle_api: FlextDbOracleApi | None,
) -> Generator[t.StrMapping | None]:
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
        except (oracledb.Error, ConnectionError, OSError):
            pass
    for ddl in test_schema.values():
        try:
            result = connected_oracle_api.execute_statement(ddl)
            if result.failure:
                pytest.skip(f"Could not create test schema: {result.error}")
        except (oracledb.Error, ConnectionError, OSError) as e:
            pytest.skip(f"Test setup failed: {e}")
    yield test_schema

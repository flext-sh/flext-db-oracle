"""Test configuration for flext-db-oracle - ORACLE REAL TESTING ONLY.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
import gc
import os
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import oracledb
import pytest

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings
from flext_tests import tk
from tests import c, u

if TYPE_CHECKING:
    from collections.abc import Generator

    from tests import p, t

logger = u.fetch_logger(__name__)

_ORACLE_CONTAINER_NAME = "flext-oracle-db-test"


# NOTE (multi-agent): ADR-005 singleton discipline — drop the settings singleton
# around every test so direct FlextDbOracleSettings(...) construction never leaks.
def pytest_runtest_setup(item: pytest.Item) -> None:
    """Reset the settings singleton before each test for isolation."""
    _ = item
    FlextDbOracleSettings.reset_for_testing()


def pytest_runtest_teardown(item: pytest.Item, nextitem: pytest.Item | None) -> None:
    """Reset the settings singleton after each test to prevent leaks."""
    _ = item, nextitem
    FlextDbOracleSettings.reset_for_testing()


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with Oracle container for ALL tests."""
    _ = config
    os.environ["SKIP_E2E_TESTS"] = "false"
    os.environ["ORACLE_INTEGRATION_TESTS"] = "1"
    os.environ["USE_REAL_ORACLE"] = "true"


def pytest_sessionstart(session: pytest.Session) -> None:
    """Cleanup dirty containers BEFORE test session starts."""
    _ = session
    try:
        _cleanup_dirty_oracle_container()
    except (ConnectionError, TimeoutError, OSError, RuntimeError) as e:
        logger.warning("Docker cleanup skipped (unavailable): %s", e)


def _cleanup_dirty_oracle_container() -> None:
    """Cleanup dirty Oracle test containers before the session starts."""
    if tk.ci_disables_docker():
        return
    container_name = _ORACLE_CONTAINER_NAME
    docker = tk.shared(
        container_name, workspace_root=Path(__file__).resolve().parents[2]
    )
    dirty_containers = docker.dirty_containers
    if not dirty_containers:
        logger.debug("No dirty containers to clean")
        return
    status_result = docker.fetch_container_status(container_name)
    if status_result.success and status_result.value.status == (
        c.Tests.ContainerStatus.RUNNING
    ):
        docker.mark_container_clean(container_name)
        logger.info("Container %s is healthy, cleared dirty state", container_name)
        return
    cleanup_result = docker.cleanup_dirty_containers()
    if cleanup_result.failure:
        logger.warning(f"Dirty container cleanup failed: {cleanup_result.error}")
        return
    cleaned = cleanup_result.value
    if cleaned:
        logger.info(f"Recreated dirty containers: {', '.join(cleaned)}")
        return
    logger.debug("No dirty containers to clean")


def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> None:
    """Mark container dirty on Oracle service failures."""
    if call.excinfo is None:
        return
    with contextlib.suppress(ConnectionError, TimeoutError, OSError, RuntimeError):
        _mark_dirty_on_oracle_service_failure(item, call)


def _mark_dirty_on_oracle_service_failure(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> None:
    """Mark the shared Oracle container dirty when an Oracle service error occurs."""
    if call.excinfo is None:
        return
    # Skip/xfail are not service failures — do not recreate the shared container.
    if call.excinfo.errisinstance(pytest.skip.Exception):
        return
    exc_type = call.excinfo.type
    exc_msg = str(call.excinfo.value).lower()
    oracle_service_errors = (
        "ora-",
        "connection refused",
        "connection reset by peer",
        "broken pipe",
        "database not available",
        "tns:",
    )
    is_service_failure = any(
        err in str(exc_type).lower() or err in exc_msg for err in oracle_service_errors
    )
    if not is_service_failure:
        return
    docker = tk.shared(
        _ORACLE_CONTAINER_NAME, workspace_root=Path(__file__).resolve().parents[2]
    )
    docker.mark_container_dirty(_ORACLE_CONTAINER_NAME)
    logger.error(
        "ORACLE SERVICE FAILURE detected in %s, container marked DIRTY for recreation: %s",
        item.nodeid,
        exc_msg,
    )


@pytest.fixture(scope="session")
def docker_control() -> tk:
    """Provide tk instance for container management."""
    return tk.shared(
        _ORACLE_CONTAINER_NAME, workspace_root=Path(__file__).resolve().parents[2]
    )


@pytest.fixture(scope="session")
def shared_oracle_container(docker_control: tk) -> str:
    """Start and maintain flext-oracle-db-test container.

    Probe budget stays under flext-infra pytest case-timeout (30s). Cold Oracle
    skips cleanly; warm/shared containers that already accept connections pass.
    Long first-boot (SHARED_CONTAINERS startup_timeout=900) is not a per-case wait.
    DB login readiness is enforced by ``connected_oracle_api`` (skip on failure).
    """
    if tk.ci_disables_docker():
        pytest.skip(c.Tests.DOCKER_CI_SKIP_REASON)
    container_name = _ORACLE_CONTAINER_NAME
    probe_budget = c.Tests.DOCKER_PROBE_MAX_WAIT_SECONDS
    target = docker_control.target_config
    if target is not None and target.startup_timeout != probe_budget:
        docker_control.target_config = target.model_copy(
            update={"startup_timeout": probe_budget}
        )
    ensure_result = docker_control.execute()
    if ensure_result.failure:
        pytest.skip(
            f"Oracle container {container_name} unavailable: {ensure_result.error}"
        )
    resolved_port = u.Tests.resolve_oracle_test_port(docker_control, container_name)
    os.environ["TEST_ORACLE_PORT"] = str(resolved_port)
    host = target.host if target is not None else c.LOCALHOST
    # TCP-only probe: oracledb.connect on a half-ready listener leaks sockets that
    # become PytestUnraisableExceptionWarning under filterwarnings=error.
    tcp_ready = docker_control.wait_for_port_ready(
        host, resolved_port, max_wait=probe_budget
    )
    if tcp_ready.failure:
        pytest.skip(
            f"Oracle container {container_name} TCP {host}:{resolved_port} "
            f"not ready within {probe_budget}s probe budget"
        )
    logger.info("Container %s TCP ready on %s:%s", container_name, host, resolved_port)
    return container_name


@pytest.fixture(scope="session")
def oracle_login_ready(shared_oracle_container: str) -> str:
    """Skip live Oracle tests when the shared database refuses a real login.

    A TCP-ready listener does not mean the database accepts sessions: Oracle
    opens the port long before the service is usable. Without this gate the
    tests that consume ``real_oracle_config`` connect directly and report a
    failure instead of skipping on an unavailable database.

    The single probe connection runs with ``ResourceWarning`` suppressed and an
    explicit collection, because a refused ``oracledb.connect`` leaks its socket
    and ``filterwarnings = error`` would otherwise surface it as an unrelated
    ``PytestUnraisableExceptionWarning`` during a later test's teardown.
    """
    host = os.getenv("TEST_ORACLE_HOST", c.LOCALHOST)
    port = int(os.getenv("TEST_ORACLE_PORT", "1522"))
    service = os.getenv("TEST_ORACLE_SERVICE", "FLEXTDB")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ResourceWarning)
        try:
            probe = oracledb.connect(
                user=os.getenv("TEST_ORACLE_USER", "flext_test"),
                password=os.getenv("TEST_ORACLE_PASSWORD", "flext_test_password"),
                dsn=f"{host}:{port}/{service}",
            )
        except (oracledb.Error, OSError) as exc:
            gc.collect()
            pytest.skip(
                f"Oracle {host}:{port}/{service} is not accepting logins: {exc}"
            )
        else:
            with contextlib.suppress(oracledb.Error, OSError):
                probe.close()
        finally:
            gc.collect()

    logger.info("Oracle login ready on %s:%s/%s", host, port, service)
    return shared_oracle_container


@pytest.fixture(scope="session")
def oracle_container(oracle_login_ready: str) -> str:
    """Provide Oracle container name for all tests."""
    return oracle_login_ready


@pytest.fixture
def real_oracle_settings(oracle_container: str) -> FlextDbOracleSettings:
    """Return real Oracle configuration for tests that can use it."""
    _ = oracle_container
    # NOTE (multi-agent): ADR-005 — connection scalars live under the DbOracle
    # namespace; flat constructor kwargs no longer exist.
    return FlextDbOracleSettings.model_validate({
        "DbOracle": {
            "host": os.getenv("TEST_ORACLE_HOST", "localhost"),
            "port": int(os.getenv("TEST_ORACLE_PORT", "1522")),
            "name": os.getenv("TEST_ORACLE_SERVICE", "FLEXTDB"),
            "username": os.getenv("TEST_ORACLE_USER", "flext_test"),
            "password": os.getenv("TEST_ORACLE_PASSWORD", "flext_test_password"),
            "service_name": os.getenv("TEST_ORACLE_SERVICE", "FLEXTDB"),
        }
    })


@pytest.fixture
def real_oracle_config(
    real_oracle_settings: FlextDbOracleSettings,
) -> FlextDbOracleSettings:
    """Backward-compatible alias for legacy fixture name used in some tests."""
    return real_oracle_settings


@pytest.fixture
def oracle_config(real_oracle_config: FlextDbOracleSettings) -> FlextDbOracleSettings:
    """Backward-compatible alias for integration tests using ``oracle_config``."""
    return real_oracle_config


@pytest.fixture
def oracle_api(real_oracle_settings: FlextDbOracleSettings) -> FlextDbOracleApi:
    """Return Oracle API for tests that can use it."""
    return FlextDbOracleApi(settings=real_oracle_settings)


def _assert_oracle_success[TResult](result: p.Result[TResult], operation: str) -> None:
    """Raise with a clear setup error when an Oracle operation fails."""
    if result.failure:
        error = result.error or ""
        msg = f"{operation} failed: {error}"
        raise AssertionError(msg)


def _user_tables(api: FlextDbOracleApi) -> set[str]:
    """Return tables visible in the connected Oracle test schema."""
    result = api.oracle_services.execute_query(
        'SELECT table_name AS "table_name" FROM user_tables'
    )
    _assert_oracle_success(result, "List Oracle test tables")
    return {str(row.root["table_name"]).upper() for row in result.value}


def _ensure_table(api: FlextDbOracleApi, table_name: str, ddl: str) -> None:
    """Create one test table when absent."""
    if table_name.upper() in _user_tables(api):
        return
    result = api.execute_statement(ddl)
    _assert_oracle_success(result, f"Create {table_name}")


def _seed_row(api: FlextDbOracleApi, table_name: str, insert_sql: str) -> None:
    """Execute one seed statement for a freshly prepared sample table."""
    insert_result = api.execute_statement(insert_sql)
    _assert_oracle_success(insert_result, f"Seed {table_name}")


def _ensure_hr_sample_tables(api: FlextDbOracleApi) -> None:
    """Provision minimal HR sample tables required by real API examples.

    Provisioning is idempotent (``CREATE`` when absent, ``MERGE`` for rows) and
    serialized across pytest-xdist workers with the shared FileLock utility, so
    concurrent workers sharing one Oracle container never race each other into
    duplicate-key violations. Rows are never truncated: a truncate would empty
    the tables another worker is reading mid-test.
    """
    _ensure_table(
        api,
        "DEPARTMENTS",
        "CREATE TABLE departments (department_id NUMBER PRIMARY KEY, department_name VARCHAR2(100))",
    )
    _ensure_table(
        api,
        "JOBS",
        "CREATE TABLE jobs (job_id VARCHAR2(20) PRIMARY KEY, job_title VARCHAR2(100))",
    )
    _ensure_table(
        api,
        "EMPLOYEES",
        "CREATE TABLE employees (employee_id NUMBER PRIMARY KEY, first_name VARCHAR2(50), last_name VARCHAR2(50), email VARCHAR2(100), department_id NUMBER, job_id VARCHAR2(20))",
    )
    _seed_row(
        api,
        "DEPARTMENTS",
        """
        MERGE INTO departments target
        USING (SELECT 10 department_id, 'Engineering' department_name FROM dual) source
        ON (target.department_id = source.department_id)
        WHEN MATCHED THEN UPDATE SET target.department_name = source.department_name
        WHEN NOT MATCHED THEN INSERT (department_id, department_name)
        VALUES (source.department_id, source.department_name)
        """,
    )
    _seed_row(
        api,
        "JOBS",
        """
        MERGE INTO jobs target
        USING (SELECT 'DEV' job_id, 'Developer' job_title FROM dual) source
        ON (target.job_id = source.job_id)
        WHEN MATCHED THEN UPDATE SET target.job_title = source.job_title
        WHEN NOT MATCHED THEN INSERT (job_id, job_title)
        VALUES (source.job_id, source.job_title)
        """,
    )
    _seed_row(
        api,
        "EMPLOYEES",
        """
        MERGE INTO employees target
        USING (
            SELECT 1 employee_id, 'Ada' first_name, 'Lovelace' last_name,
                   'ada@example.com' email
            FROM dual
        ) source
        ON (target.employee_id = source.employee_id)
        WHEN MATCHED THEN UPDATE SET
            target.first_name = source.first_name,
            target.last_name = source.last_name,
            target.email = source.email
        WHEN NOT MATCHED THEN INSERT (employee_id, first_name, last_name, email)
        VALUES (
            source.employee_id,
            source.first_name,
            source.last_name,
            source.email
        )
        """,
    )


@pytest.fixture
def connected_oracle_api(oracle_api: FlextDbOracleApi) -> Generator[FlextDbOracleApi]:
    """Return a connected Oracle API or skip when the shared DB is unreachable."""
    connect_result = oracle_api.connect()
    if connect_result.failure:
        pytest.skip(f"Failed to connect Oracle API: {connect_result.error}")
    connected_api = connect_result.value
    with u.Tests.FileLock(
        Path.home() / ".flext" / f"{_ORACLE_CONTAINER_NAME}.seed.lock"
    ):
        _ensure_hr_sample_tables(connected_api)
    yield connected_api
    with contextlib.suppress(Exception):
        connected_api.disconnect()


@pytest.fixture
def oracle_available(connected_oracle_api: FlextDbOracleApi) -> bool:
    """Check if Oracle is available for testing."""
    _ = connected_oracle_api
    return True


@pytest.fixture
def test_database_setup(connected_oracle_api: FlextDbOracleApi) -> t.StrMapping:
    """Set up test database schema and return test table info."""
    test_schema = {
        "test_table": "CREATE TABLE test_table (id NUMBER PRIMARY KEY, name VARCHAR2(100))",
        "test_sequence": "CREATE SEQUENCE test_seq START WITH 1 INCREMENT BY 1",
    }
    cleanup_ddl = ["DROP TABLE test_table PURGE", "DROP SEQUENCE test_seq"]
    for ddl in cleanup_ddl:
        with contextlib.suppress(oracledb.Error, ConnectionError, OSError):
            connected_oracle_api.execute_statement(ddl)
    for ddl in test_schema.values():
        try:
            result = connected_oracle_api.execute_statement(ddl)
            if result.failure:
                msg = f"Could not create test schema: {result.error}"
                raise AssertionError(msg)
        except (oracledb.Error, ConnectionError, OSError) as e:
            msg = f"Test setup failed: {e}"
            raise AssertionError(msg) from e
    return test_schema

"""Unit test configuration with Docker/Oracle integration support.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Unit tests run with Oracle container integration when available.
If Oracle is not available, tests gracefully skip or use mocks.
"""

from __future__ import annotations

import contextlib
import os
import time
from collections.abc import Generator, Mapping
from pathlib import Path

import oracledb
import pytest
from flext_core import FlextLogger
from tests import p
from flext_tests import tk
from pydantic import TypeAdapter, ValidationError

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings
from tests import t

logger: p.Logger = FlextLogger(__name__)
_PORT_BINDINGS_ADAPTER = TypeAdapter(Mapping[str, str])


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _normalized_port_bindings(value: t.NormalizedValue) -> Mapping[str, str]:
    try:
        return _PORT_BINDINGS_ADAPTER.validate_python(value)
    except ValidationError:
        return {}


def _resolve_oracle_test_port(docker_control: tk, container_name: str) -> int:
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
    container_config = tk.SHARED_CONTAINERS.get(container_name)
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


def _wait_for_oracle_ready(port: int, max_wait_seconds: int = 300) -> bool:
    waited_seconds = 0
    while waited_seconds < max_wait_seconds:
        try:
            dsn = oracledb.makedsn("localhost", port, service_name="FLEXTDB")
            connection = oracledb.connect(
                user="flext_test",
                password="flext_test_password",
                dsn=dsn,
            )
            connection.close()
            return True
        except (oracledb.Error, ConnectionError, TimeoutError, OSError):
            time.sleep(5)
            waited_seconds += 5
    return False


def _ensure_shared_oracle_container() -> str | None:
    container_name = "flext-oracle-db-test"
    docker_control = tk(workspace_root=_workspace_root())
    container_config = tk.SHARED_CONTAINERS.get(container_name)
    if container_config is None:
        return None
    compose_file_value = container_config.get("compose_file")
    if compose_file_value is None:
        return None
    compose_file = str(compose_file_value)
    if not compose_file.startswith("/"):
        compose_file = str(_workspace_root() / compose_file)
    status = docker_control.get_container_status(container_name)
    status_value = status.value if status.is_success else None
    status_name = getattr(status_value, "status", None)
    container_running = status.is_success and (
        status_name == tk.ContainerStatus.RUNNING
    )
    if not container_running:
        service_name = str(container_config.get("service", ""))
        compose_result = docker_control.compose_up(
            compose_file,
            service=service_name or None,
        )
        if compose_result.is_failure:
            return None
    resolved_port = _resolve_oracle_test_port(docker_control, container_name)
    os.environ["TEST_ORACLE_HOST"] = "localhost"
    os.environ["TEST_ORACLE_PORT"] = str(resolved_port)
    os.environ["TEST_ORACLE_SERVICE"] = "FLEXTDB"
    os.environ["TEST_ORACLE_USER"] = "flext_test"
    os.environ["TEST_ORACLE_PASSWORD"] = "flext_test_password"
    if not _wait_for_oracle_ready(resolved_port):
        return None
    return container_name


def _is_oracle_container_running() -> bool:
    """Check if Oracle container is running without heavy operations."""
    try:
        docker_control = tk(workspace_root=_workspace_root())
        status_result = docker_control.get_container_status("flext-oracle-db-test")
    except (ConnectionError, TimeoutError, OSError, RuntimeError):
        return False
    return status_result.is_success and (
        getattr(status_result.value, "status", None) == tk.ContainerStatus.RUNNING
    )


def _get_oracle_config_from_container() -> FlextDbOracleSettings | None:
    """Get Oracle config from shared container configuration."""
    if not _is_oracle_container_running():
        return None
    host = os.getenv("TEST_ORACLE_HOST", "localhost")
    port_text = os.getenv("TEST_ORACLE_PORT", "1522")
    if not port_text.isdigit():
        return None
    service = os.getenv("TEST_ORACLE_SERVICE", "FLEXTDB")
    username = os.getenv("TEST_ORACLE_USER", "flext_test")
    password = os.getenv("TEST_ORACLE_PASSWORD", "flext_test_password")
    return FlextDbOracleSettings(
        host=host,
        port=int(port_text),
        name=service,
        username=username,
        password=password,
        service_name=service,
        ssl_server_cert_dn=None,
    )


@pytest.fixture(scope="session")
def shared_oracle_container() -> str | None:
    """Return container name if running, None otherwise."""
    return _ensure_shared_oracle_container()


@pytest.fixture(scope="session", autouse=True)
def ensure_shared_docker_container() -> None:
    _ = _ensure_shared_oracle_container()


@pytest.fixture(scope="session")
def docker_control() -> tk | None:
    """Provide Docker control if available."""
    try:
        return tk(workspace_root=_workspace_root())
    except (ConnectionError, OSError, RuntimeError):
        return None


@pytest.fixture(scope="session")
def oracle_container(shared_oracle_container: str | None) -> str | None:
    """Return container name if available."""
    return shared_oracle_container


@pytest.fixture
def real_oracle_config() -> FlextDbOracleSettings | None:
    """Provide real Oracle config if container is running."""
    if not _is_oracle_container_running():
        return None
    return _get_oracle_config_from_container()


@pytest.fixture
def oracle_api(
    real_oracle_config: FlextDbOracleSettings | None,
) -> FlextDbOracleApi | None:
    """Provide Oracle API with real config if available."""
    if real_oracle_config is None:
        pytest.skip("Oracle configuration unavailable for real API fixture")
    return FlextDbOracleApi(config=real_oracle_config)


@pytest.fixture
def connected_oracle_api(
    oracle_api: FlextDbOracleApi | None,
) -> Generator[FlextDbOracleApi | None]:
    """Return connected Oracle API if available."""
    if oracle_api is None:
        pytest.skip("Oracle API unavailable for connected fixture")
    connect_result = oracle_api.connect()
    if connect_result.is_success:
        connected_api = connect_result.value
        yield connected_api
        with contextlib.suppress(Exception):
            connected_api.disconnect()
    else:
        pytest.skip("Oracle connection unavailable for connected fixture")


@pytest.fixture
def mock_oracle_config() -> FlextDbOracleSettings:
    """Provide mock Oracle config for tests."""
    return FlextDbOracleSettings(
        host="mock-host",
        port=1521,
        service_name="MOCK_SERVICE",
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


@pytest.fixture(autouse=True)
def test_cleanup(
    connected_oracle_api: FlextDbOracleApi | None,
) -> None:
    """Cleanup test data if Oracle is available."""
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
                    plsql_query = f"\n                    BEGIN\n                        EXECUTE IMMEDIATE '{query}';\n                    EXCEPTION\n                        WHEN OTHERS THEN\n                            NULL;\n                    END;\n                    "
                    connected_oracle_api.execute_sql(plsql_query)
                except (oracledb.Error, ConnectionError, OSError):
                    pass
        except (oracledb.Error, ConnectionError, OSError):
            pass


@pytest.fixture
def oracle_available(connected_oracle_api: FlextDbOracleApi | None) -> bool:
    """Check if Oracle is available for testing."""
    return connected_oracle_api is not None

"""Unit test configuration with Docker/Oracle integration support.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Unit tests run with Oracle container integration when available.
If Oracle is not available, tests gracefully skip or use mocks.
"""

from __future__ import annotations

import contextlib
from collections.abc import Generator
from pathlib import Path

import pytest
from flext_core import FlextLogger
from flext_tests import FlextTestsDocker, c

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings

logger: FlextLogger = FlextLogger(__name__)


def _is_oracle_container_running() -> bool:
    """Check if Oracle container is running without heavy operations."""
    try:
        docker = FlextTestsDocker(workspace_root=Path(__file__).resolve().parents[2])
        status_result = docker.get_container_status("flext-oracle-db-test")
        if status_result.is_success:
            return status_result.value.status == c.Tests.Docker.ContainerStatus.RUNNING
    except Exception:
        pass
    return False


def _get_oracle_config_from_container() -> FlextDbOracleSettings | None:
    """Get Oracle config from shared container configuration."""
    try:
        container_config = c.Tests.Docker.SHARED_CONTAINERS.get("flext-oracle-db-test")
        if not container_config:
            return None

        connection = container_config.get("connection", {})
        return FlextDbOracleSettings(
            host=str(connection.get("host", "localhost")),
            port=int(connection.get("port", 1522)),
            service_name=str(connection.get("service_name", "FLEXTDB")),
            username=str(connection.get("username", "flext_test")),
            password=str(connection.get("password", "flext_test_password")),
        )
    except Exception as e:
        logger.debug(f"Failed to get Oracle config from container: {e}")
        return None


@pytest.fixture(scope="session")
def shared_oracle_container() -> str | None:
    """Return container name if running, None otherwise."""
    if _is_oracle_container_running():
        return "flext-oracle-db-test"
    return None


@pytest.fixture(scope="session", autouse=True)
def ensure_shared_docker_container() -> None:
    """No-op for unit tests - container managed by root conftest."""
    pass


@pytest.fixture(scope="session")
def docker_control() -> FlextTestsDocker | None:
    """Provide Docker control if available."""
    try:
        return FlextTestsDocker(workspace_root=Path(__file__).resolve().parents[2])
    except Exception:
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
        return None
    return FlextDbOracleApi(config=real_oracle_config)


@pytest.fixture
def connected_oracle_api(
    oracle_api: FlextDbOracleApi | None,
) -> Generator[FlextDbOracleApi | None]:
    """Return connected Oracle API if available."""
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
        yield None


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
def test_cleanup(connected_oracle_api: FlextDbOracleApi | None) -> Generator[None]:
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
                    plsql_query = f"""
                    BEGIN
                        EXECUTE IMMEDIATE '{query}';
                    EXCEPTION
                        WHEN OTHERS THEN
                            NULL;
                    END;
                    """
                    connected_oracle_api.execute(plsql_query)
                except Exception:
                    pass
        except Exception:
            pass
    return


@pytest.fixture
def oracle_available(connected_oracle_api: FlextDbOracleApi | None) -> bool:
    """Check if Oracle is available for testing."""
    return connected_oracle_api is not None

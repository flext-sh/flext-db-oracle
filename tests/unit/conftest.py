"""Unit test configuration with Docker/Oracle integration support.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Unit tests run with Oracle container integration when available.
If Oracle is not available, tests gracefully skip or use mocks.
"""

from __future__ import annotations

import contextlib
import os
import socket
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from flext_tests import tk

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings
from tests.constants import c
from tests.utilities import u

if TYPE_CHECKING:
    from collections.abc import Generator

    from tests.protocols import p

# Prevent unit tests from hanging on DNS resolution for fake hostnames.
# Without this, socket operations to unresolvable hosts block indefinitely.
socket.setdefaulttimeout(2)

logger: p.Logger = u.fetch_logger(__name__)


def _is_oracle_container_running() -> bool:
    """Check if Oracle container is running without heavy operations."""
    try:
        docker_control = tk(workspace_root=Path(__file__).resolve().parents[3])
        status_result = docker_control.fetch_container_status("flext-oracle-db-test")
    except (ConnectionError, TimeoutError, OSError, RuntimeError):
        return False
    if not status_result.success:
        return False
    container_status: c.Tests.ContainerStatus | None = getattr(
        status_result.value,
        "status",
        None,
    )
    is_running: bool = container_status == c.Tests.ContainerStatus.RUNNING
    return is_running


def _get_oracle_config_from_container() -> FlextDbOracleSettings | None:
    """Get Oracle settings from shared container configuration."""
    if not _is_oracle_container_running():
        return None
    host: str = os.getenv("TEST_ORACLE_HOST", "localhost")
    port_text = os.getenv("TEST_ORACLE_PORT", "1522")
    if not port_text.isdigit():
        return None
    service: str = os.getenv("TEST_ORACLE_SERVICE", "FLEXTDB")
    username: str = os.getenv("TEST_ORACLE_USER", "flext_test")
    password: str = os.getenv("TEST_ORACLE_PASSWORD", "flext_test_password")
    return FlextDbOracleSettings.model_validate({
        "host": host,
        "port": int(port_text),
        "name": service,
        "username": username,
        "password": password,
        "service_name": service,
    })


@pytest.fixture
def real_oracle_config() -> FlextDbOracleSettings | None:
    """Provide real Oracle settings if container is running."""
    if not _is_oracle_container_running():
        pytest.skip("Oracle container not running")
    return _get_oracle_config_from_container()


@pytest.fixture
def oracle_api(
    real_oracle_config: FlextDbOracleSettings | None,
) -> FlextDbOracleApi | None:
    """Provide Oracle API with real settings if available."""
    if real_oracle_config is None:
        pytest.skip("Oracle configuration unavailable for real API fixture")
    return FlextDbOracleApi(settings=real_oracle_config)


@pytest.fixture
def connected_oracle_api(
    oracle_api: FlextDbOracleApi | None,
) -> Generator[FlextDbOracleApi | None]:
    """Return connected Oracle API if available."""
    if oracle_api is None:
        pytest.skip("Oracle API unavailable for connected fixture")
    connect_result = oracle_api.connect()
    if connect_result.success:
        connected_api = connect_result.value
        yield connected_api
        with contextlib.suppress(Exception):
            connected_api.disconnect()
    else:
        pytest.skip("Oracle connection unavailable for connected fixture")


@pytest.fixture
def oracle_available(connected_oracle_api: FlextDbOracleApi | None) -> bool:
    """Check if Oracle is available for testing."""
    return connected_oracle_api is not None

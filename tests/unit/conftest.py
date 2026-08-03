"""Unit test Oracle fixtures backed by the workspace container fixture."""

from __future__ import annotations

import contextlib
import os
import socket
from typing import TYPE_CHECKING

import pytest

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings

if TYPE_CHECKING:
    from collections.abc import Generator


# Prevent unit tests from hanging on network failures.
socket.setdefaulttimeout(2)


@pytest.fixture(autouse=True)
def _isolate_oracle_env_vars() -> Generator[None]:
    """Remove Oracle env vars during unit tests so defaults are observable."""
    prefixes = ("ORACLE_", "FLEXT_TARGET_ORACLE_")
    saved: dict[str, str | None] = {}
    for key in list(os.environ):
        if key.startswith(prefixes):
            saved[key] = os.environ[key]
            del os.environ[key]
    try:
        yield
    finally:
        for key, value in saved.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]


@pytest.fixture
def real_oracle_config(
    real_oracle_settings: FlextDbOracleSettings,
) -> FlextDbOracleSettings:
    """Return the workspace-managed Oracle settings."""
    return real_oracle_settings


@pytest.fixture
def oracle_api(real_oracle_config: FlextDbOracleSettings) -> FlextDbOracleApi:
    """Return an Oracle API configured by the workspace fixture."""
    return FlextDbOracleApi(settings=real_oracle_config)


@pytest.fixture
def connected_oracle_api(oracle_api: FlextDbOracleApi) -> Generator[FlextDbOracleApi]:
    """Return a connected Oracle API or fail with the real error."""
    connect_result = oracle_api.connect()
    if connect_result.failure:
        msg = f"Oracle connection unavailable for connected fixture: {connect_result.error}"
        raise AssertionError(msg)
    connected_api = connect_result.value
    yield connected_api
    with contextlib.suppress(Exception):
        connected_api.disconnect()


@pytest.fixture
def oracle_available(connected_oracle_api: FlextDbOracleApi) -> bool:
    """Return True once the connected Oracle fixture exists."""
    _ = connected_oracle_api
    return True

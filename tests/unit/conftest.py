"""Unit test configuration — no Docker or Oracle dependencies.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Unit tests run in complete isolation. All Docker/Oracle-dependent
fixtures from the root conftest are overridden here so unit tests
never attempt Docker compose or Oracle connections.

Fixtures that return None: tests using them get mock fallbacks.
Fixtures that pytest.skip: tests requiring real Oracle are auto-skipped.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from flext_db_oracle import FlextDbOracleSettings


@pytest.fixture(scope="session")
def shared_oracle_container() -> str | None:
    return None


@pytest.fixture(scope="session", autouse=True)
def ensure_shared_docker_container() -> None:
    pass


@pytest.fixture(scope="session")
def docker_control() -> None:
    return None


@pytest.fixture(scope="session")
def oracle_container() -> str | None:
    return None


@pytest.fixture
def real_oracle_config() -> FlextDbOracleSettings:
    pytest.skip("Oracle not available in unit tests")


@pytest.fixture
def oracle_api() -> None:
    pytest.skip("Oracle not available in unit tests")


@pytest.fixture
def connected_oracle_api() -> Generator[None]:
    pytest.skip("Oracle not available in unit tests")


@pytest.fixture
def mock_oracle_config() -> FlextDbOracleSettings:
    return FlextDbOracleSettings(
        host="mock-host",
        port=1521,
        service_name="MOCK_SERVICE",
        username="mock-user",
        password="mock-pass",
    )


@pytest.fixture
def oracle_config(mock_oracle_config: FlextDbOracleSettings) -> FlextDbOracleSettings:
    return mock_oracle_config


@pytest.fixture(autouse=True)
def test_cleanup() -> Generator[None]:
    return


@pytest.fixture
def oracle_available() -> bool:
    return False


@pytest.fixture
def test_database_setup() -> Generator[None]:
    return None

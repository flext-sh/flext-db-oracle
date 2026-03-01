"""Unit test configuration — no Docker or Oracle dependencies.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Unit tests run in complete isolation. All Docker/Oracle-dependent
fixtures from the root conftest are overridden here to return None
or no-op, so unit tests never attempt Docker compose or Oracle connections.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest


@pytest.fixture(scope="session")
def shared_oracle_container() -> str | None:
    """Override: unit tests don't need Docker containers."""
    return None


@pytest.fixture(scope="session", autouse=True)
def ensure_shared_docker_container() -> None:
    """Override: skip Docker container startup for unit tests."""


@pytest.fixture(scope="session")
def docker_control() -> None:
    """Override: no Docker control for unit tests."""
    return None


@pytest.fixture(scope="session")
def oracle_container() -> str | None:
    """Override: no Oracle container for unit tests."""
    return None


@pytest.fixture
def real_oracle_config() -> None:
    """Override: no real Oracle config for unit tests."""
    return None


@pytest.fixture
def oracle_api() -> None:
    """Override: no Oracle API for unit tests."""
    return None


@pytest.fixture
def connected_oracle_api() -> Generator[None]:
    """Override: no connected Oracle API for unit tests."""
    yield None


@pytest.fixture(autouse=True)
def test_cleanup() -> Generator[None]:
    """Override: no Oracle cleanup needed for unit tests."""
    yield


@pytest.fixture
def oracle_available() -> bool:
    """Override: Oracle is never available in unit tests."""
    return False


@pytest.fixture
def test_database_setup() -> Generator[None]:
    """Override: no database setup for unit tests."""
    yield None

"""Unit-test runtime guards for flext-db-oracle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import socket
from collections.abc import Generator

import pytest
from sqlalchemy import Connection, create_engine

from flext_db_oracle import FlextDbOracleClient

# Prevent unit tests from hanging on network failures.
socket.setdefaulttimeout(2)


@pytest.fixture
def client() -> FlextDbOracleClient:
    """Provide a default, unconnected client instance.

    Returns:
        The unconnected public Oracle client.

    """
    return FlextDbOracleClient()


@pytest.fixture
def memory_connection() -> Generator[Connection]:
    """Open a caller-owned in-memory SQLAlchemy connection.

    Yields:
        The open connection; the engine is disposed at teardown.

    """
    engine = create_engine("sqlite://")
    with engine.connect() as connection:
        yield connection
    engine.dispose()

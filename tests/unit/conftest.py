"""Unit-test runtime guards for flext-db-oracle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import socket

import pytest

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

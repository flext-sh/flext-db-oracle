"""Behavioral contract of the shared test-container registry constants.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from flext_tests import tm

from tests import c


class TestsFlextDbOracleConftestConstants:
    """Behavioral contract of the shared test-container registry constants."""

    @staticmethod
    def test_shared_containers_is_a_mapping() -> None:
        # Act / Assert: public contract exposes a read-mappable registry.
        """Test shared containers is a mapping."""
        tm.that(c.Tests.SHARED_CONTAINERS, is_=Mapping)

    @staticmethod
    def test_shared_containers_registry_is_stable_across_access() -> None:
        # Idempotence: the constant resolves to the same registry each access.
        """Test shared containers registry is stable across access."""
        first = c.Tests.SHARED_CONTAINERS
        second = c.Tests.SHARED_CONTAINERS
        tm.that(dict(first) == dict(second), eq=True)

    @staticmethod
    def test_oracle_container_is_registered() -> None:
        # Act / Assert: the oracle DB test container is part of the contract.
        """Test oracle container is registered."""
        tm.that(c.Tests.ORACLE_CONTAINER in c.Tests.SHARED_CONTAINERS, eq=True)

    @staticmethod
    def test_oracle_container_config_is_a_mapping() -> None:
        """Test oracle container config is a mapping."""
        config = c.Tests.SHARED_CONTAINERS[c.Tests.ORACLE_CONTAINER]
        tm.that(config, is_=Mapping)

    @staticmethod
    @pytest.mark.parametrize(
        ("key", "expected"),
        [
            ("service", "oracle-db"),
            ("port", 1521),
            ("host", "localhost"),
            ("startup_timeout", 900),
            ("compose_file", "docker/docker-compose.oracle-db.yml"),
        ],
    )
    def test_oracle_container_config_exposes_connection_contract(
        key: str, expected: str | int,
    ) -> None:
        # Public contract: oracle container advertises its connection metadata.
        """Test oracle container config exposes connection contract."""
        config = c.Tests.SHARED_CONTAINERS[c.Tests.ORACLE_CONTAINER]
        tm.that(config[key], eq=expected)

    @staticmethod
    def test_oracle_container_config_declares_expected_fields() -> None:
        """Test oracle container config declares expected fields."""
        config = c.Tests.SHARED_CONTAINERS[c.Tests.ORACLE_CONTAINER]
        tm.that(
            sorted(config)
            == ["compose_file", "host", "port", "service", "startup_timeout"],
            eq=True,
        )

    @staticmethod
    def test_missing_container_lookup_raises_key_error() -> None:
        # Error path: unknown container names are not silently defaulted.
        """Test missing container lookup raises key error."""
        with pytest.raises(KeyError):
            _ = c.Tests.SHARED_CONTAINERS["flext-nonexistent-test"]

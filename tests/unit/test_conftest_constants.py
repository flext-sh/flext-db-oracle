from __future__ import annotations

from collections.abc import Mapping

import pytest
from flext_tests import tm

from tests.constants import c


class TestsFlextDbOracleConftestConstants:
    """Behavioral contract of the shared test-container registry constants."""

    ORACLE_CONTAINER = "flext-oracle-db-test"

    def test_shared_containers_is_a_mapping(self) -> None:
        # Act / Assert: public contract exposes a read-mappable registry.
        tm.that(c.Tests.SHARED_CONTAINERS, is_=Mapping)

    def test_shared_containers_registry_is_stable_across_access(self) -> None:
        # Idempotence: the constant resolves to the same registry each access.
        first = c.Tests.SHARED_CONTAINERS
        second = c.Tests.SHARED_CONTAINERS
        tm.that(dict(first) == dict(second), eq=True)

    def test_oracle_container_is_registered(self) -> None:
        # Act / Assert: the oracle DB test container is part of the contract.
        tm.that(self.ORACLE_CONTAINER in c.Tests.SHARED_CONTAINERS, eq=True)

    def test_oracle_container_config_is_a_mapping(self) -> None:
        config = c.Tests.SHARED_CONTAINERS[self.ORACLE_CONTAINER]
        tm.that(config, is_=Mapping)

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
        self,
        key: str,
        expected: str | int,
    ) -> None:
        # Public contract: oracle container advertises its connection metadata.
        config = c.Tests.SHARED_CONTAINERS[self.ORACLE_CONTAINER]
        tm.that(config[key], eq=expected)

    def test_oracle_container_config_declares_expected_fields(self) -> None:
        config = c.Tests.SHARED_CONTAINERS[self.ORACLE_CONTAINER]
        tm.that(
            sorted(config)
            == ["compose_file", "host", "port", "service", "startup_timeout"],
            eq=True,
        )

    def test_missing_container_lookup_raises_key_error(self) -> None:
        # Error path: unknown container names are not silently defaulted.
        with pytest.raises(KeyError):
            _ = c.Tests.SHARED_CONTAINERS["flext-nonexistent-test"]

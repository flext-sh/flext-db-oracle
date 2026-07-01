from __future__ import annotations

from collections.abc import Mapping

from flext_tests import c, tm


class TestsFlextDbOracleConftestConstants:
    def test_oracle_container_in_shared_registry(self) -> None:
        tm.that("flext-oracle-db-test" in c.Tests.SHARED_CONTAINERS, eq=True)

    def test_shared_containers_is_mapping(self) -> None:
        tm.that(c.Tests.SHARED_CONTAINERS, is_=Mapping)

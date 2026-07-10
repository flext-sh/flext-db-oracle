"""Service base for flext-db-oracle tests."""

from __future__ import annotations

from typing import override

from flext_tests import s as tests_s

from flext_db_oracle import m
from tests.settings import TestsFlextDbOracleSettings


class TestsFlextDbOracleServiceBase(tests_s):
    """DB Oracle test service base with source and test settings namespaces."""

    @classmethod
    @override
    def fetch_settings(cls) -> TestsFlextDbOracleSettings:
        """Return the typed DB Oracle+Tests settings singleton."""

    @classmethod
    @override
    def _runtime_bootstrap_options(cls) -> m.RuntimeBootstrapOptions:
        return m.RuntimeBootstrapOptions(settings_type=TestsFlextDbOracleSettings)


s = TestsFlextDbOracleServiceBase

__all__: list[str] = ["TestsFlextDbOracleServiceBase", "s"]

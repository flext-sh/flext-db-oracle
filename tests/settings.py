"""Runtime settings for flext-db-oracle tests."""

from __future__ import annotations

from flext_tests import FlextTestsSettings

from flext_db_oracle import FlextDbOracleSettings


class TestsFlextDbOracleSettings(FlextDbOracleSettings, FlextTestsSettings):
    """DB Oracle settings extended with the shared test namespace."""


__all__: list[str] = ["TestsFlextDbOracleSettings"]

"""Service base for flext-db-oracle tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_tests import FlextTestsServiceBase

from tests import TestsFlextDbOracleSettings, m


class TestsFlextDbOracleServiceBase(FlextTestsServiceBase):
    """DB Oracle test service base with source and test settings namespaces."""

    # NOTE (multi-agent): flext-tests owns fetch_settings; this project
    # declares only its more-specific bootstrap settings type.
    @classmethod
    @override
    def runtime_bootstrap_options(cls) -> m.RuntimeBootstrapOptions:
        return m.RuntimeBootstrapOptions(settings_type=TestsFlextDbOracleSettings)


s = TestsFlextDbOracleServiceBase

__all__: list[str] = ["TestsFlextDbOracleServiceBase", "s"]

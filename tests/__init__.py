# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_tests import d, e, h, r, s, x

    from tests.conftest import *
    from tests.constants import *
    from tests.e2e import *
    from tests.integration import *
    from tests.models import *
    from tests.protocols import *
    from tests.typings import *
    from tests.unit import *
    from tests.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = merge_lazy_imports(
    (
        "tests.e2e",
        "tests.integration",
        "tests.unit",
    ),
    {
        "FlextDbOracleTestConstants": "tests.constants",
        "FlextDbOracleTestModels": "tests.models",
        "FlextDbOracleTestProtocols": "tests.protocols",
        "FlextDbOracleTestTypes": "tests.typings",
        "FlextDbOracleTestUtilities": "tests.utilities",
        "c": ("tests.constants", "FlextDbOracleTestConstants"),
        "conftest": "tests.conftest",
        "constants": "tests.constants",
        "d": "flext_tests",
        "e": "flext_tests",
        "e2e": "tests.e2e",
        "flext_domains": "tests.conftest",
        "h": "flext_tests",
        "integration": "tests.integration",
        "m": ("tests.models", "FlextDbOracleTestModels"),
        "models": "tests.models",
        "p": ("tests.protocols", "FlextDbOracleTestProtocols"),
        "protocols": "tests.protocols",
        "pytest_configure": "tests.conftest",
        "pytest_runtest_makereport": "tests.conftest",
        "pytest_sessionstart": "tests.conftest",
        "r": "flext_tests",
        "s": "flext_tests",
        "t": ("tests.typings", "FlextDbOracleTestTypes"),
        "test_database_setup": "tests.conftest",
        "typings": "tests.typings",
        "u": ("tests.utilities", "FlextDbOracleTestUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": "flext_tests",
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

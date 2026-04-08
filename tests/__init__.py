# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    import tests.conftest as _tests_conftest

    conftest = _tests_conftest
    import tests.constants as _tests_constants

    constants = _tests_constants
    import tests.e2e as _tests_e2e
    from tests.constants import (
        TestsFlextDbOracleConstants,
        TestsFlextDbOracleConstants as c,
    )

    e2e = _tests_e2e
    import tests.exceptions as _tests_exceptions

    exceptions = _tests_exceptions
    import tests.integration as _tests_integration

    integration = _tests_integration
    import tests.models as _tests_models

    models = _tests_models
    import tests.protocols as _tests_protocols
    from tests.models import TestsFlextDbOracleModels, TestsFlextDbOracleModels as m

    protocols = _tests_protocols
    import tests.typings as _tests_typings
    from tests.protocols import (
        TestsFlextDbOracleProtocols,
        TestsFlextDbOracleProtocols as p,
    )

    typings = _tests_typings
    import tests.unit as _tests_unit
    from tests.typings import TestsFlextDbOracleTypes, TestsFlextDbOracleTypes as t

    unit = _tests_unit
    import tests.utilities as _tests_utilities

    utilities = _tests_utilities
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests.utilities import (
        TestsFlextDbOracleUtilities,
        TestsFlextDbOracleUtilities as u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "tests.e2e",
        "tests.integration",
        "tests.unit",
    ),
    {
        "TestsFlextDbOracleConstants": (
            "tests.constants",
            "TestsFlextDbOracleConstants",
        ),
        "TestsFlextDbOracleModels": ("tests.models", "TestsFlextDbOracleModels"),
        "TestsFlextDbOracleProtocols": (
            "tests.protocols",
            "TestsFlextDbOracleProtocols",
        ),
        "TestsFlextDbOracleTypes": ("tests.typings", "TestsFlextDbOracleTypes"),
        "TestsFlextDbOracleUtilities": (
            "tests.utilities",
            "TestsFlextDbOracleUtilities",
        ),
        "c": ("tests.constants", "TestsFlextDbOracleConstants"),
        "conftest": "tests.conftest",
        "constants": "tests.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "e2e": "tests.e2e",
        "exceptions": "tests.exceptions",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "integration": "tests.integration",
        "m": ("tests.models", "TestsFlextDbOracleModels"),
        "models": "tests.models",
        "p": ("tests.protocols", "TestsFlextDbOracleProtocols"),
        "protocols": "tests.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "t": ("tests.typings", "TestsFlextDbOracleTypes"),
        "typings": "tests.typings",
        "u": ("tests.utilities", "TestsFlextDbOracleUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)
_ = _LAZY_IMPORTS.pop("cleanup_submodule_namespace", None)
_ = _LAZY_IMPORTS.pop("install_lazy_exports", None)
_ = _LAZY_IMPORTS.pop("lazy_getattr", None)
_ = _LAZY_IMPORTS.pop("logger", None)
_ = _LAZY_IMPORTS.pop("merge_lazy_imports", None)
_ = _LAZY_IMPORTS.pop("output", None)
_ = _LAZY_IMPORTS.pop("output_reporting", None)

__all__ = [
    "TestsFlextDbOracleConstants",
    "TestsFlextDbOracleModels",
    "TestsFlextDbOracleProtocols",
    "TestsFlextDbOracleTypes",
    "TestsFlextDbOracleUtilities",
    "c",
    "conftest",
    "constants",
    "d",
    "e",
    "e2e",
    "exceptions",
    "h",
    "integration",
    "m",
    "models",
    "p",
    "protocols",
    "r",
    "s",
    "t",
    "typings",
    "u",
    "unit",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

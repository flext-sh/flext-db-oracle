# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Integration package."""

from __future__ import annotations

import typing as _t

from flext_core.constants import FlextConstants as c
from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports
from flext_core.mixins import FlextMixins as x
from flext_core.models import FlextModels as m
from flext_core.protocols import FlextProtocols as p
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s
from flext_core.typings import FlextTypes as t
from flext_core.utilities import FlextUtilities as u
from tests.integration.test_oracle import TestOracleIntegration, mock_oracle_config

if _t.TYPE_CHECKING:
    import tests.integration.test_oracle as _tests_integration_test_oracle

    test_oracle = _tests_integration_test_oracle

    _ = (
        TestOracleIntegration,
        c,
        d,
        e,
        h,
        m,
        mock_oracle_config,
        p,
        r,
        s,
        t,
        test_oracle,
        u,
        x,
    )
_LAZY_IMPORTS = {
    "TestOracleIntegration": "tests.integration.test_oracle",
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "mock_oracle_config": "tests.integration.test_oracle",
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "test_oracle": "tests.integration.test_oracle",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "TestOracleIntegration",
    "c",
    "d",
    "e",
    "h",
    "m",
    "mock_oracle_config",
    "p",
    "r",
    "s",
    "t",
    "test_oracle",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

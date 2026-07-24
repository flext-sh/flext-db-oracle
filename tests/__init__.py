# AUTO-GENERATED FILE — canonical lazy tests facade. Regenerate with: make gen
"""Test package facade exposing the project test aliases lazily."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from tests.base import (
        TestsFlextDbOracleServiceBase as TestsFlextDbOracleServiceBase,
        s as s,
    )
    from tests.constants import (
        TestsFlextDbOracleConstants as TestsFlextDbOracleConstants,
        c as c,
    )
    from tests.models import (
        TestsFlextDbOracleModels as TestsFlextDbOracleModels,
        m as m,
    )
    from tests.protocols import (
        TestsFlextDbOracleProtocols as TestsFlextDbOracleProtocols,
        p,
    )
    from tests.typings import TestsFlextDbOracleTypes as TestsFlextDbOracleTypes, t as t
    from tests.utilities import (
        TestsFlextDbOracleUtilities as TestsFlextDbOracleUtilities,
        u,
    )

_LAZY_IMPORTS = build_lazy_import_map({
    ".constants": ("TestsFlextDbOracleConstants", "c"),
    ".typings": ("TestsFlextDbOracleTypes", "t"),
    ".protocols": ("TestsFlextDbOracleProtocols", "p"),
    ".models": ("TestsFlextDbOracleModels", "m"),
    ".utilities": ("TestsFlextDbOracleUtilities", "u"),
    ".base": ("TestsFlextDbOracleServiceBase", "s"),
})

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

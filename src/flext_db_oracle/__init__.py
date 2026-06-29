# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports
from flext_db_oracle.__version__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)

if _t.TYPE_CHECKING:
    from flext_cli import d as d, h as h, r as r, s as s, x as x
    from flext_db_oracle.api import (
        FlextDbOracleApi as FlextDbOracleApi,
        db_oracle as db_oracle,
    )
    from flext_db_oracle.base import (
        FlextDbOracleServiceBase as FlextDbOracleServiceBase,
    )
    from flext_db_oracle.constants import (
        FlextDbOracleConstants as FlextDbOracleConstants,
        c as c,
    )
    from flext_db_oracle.dispatcher import (
        FlextDbOracleDispatcher as FlextDbOracleDispatcher,
    )
    from flext_db_oracle.exceptions import (
        FlextDbOracleExceptions as FlextDbOracleExceptions,
        e as e,
    )
    from flext_db_oracle.models import (
        FlextDbOracleModels as FlextDbOracleModels,
        m as m,
    )
    from flext_db_oracle.protocols import (
        FlextDbOracleProtocols as FlextDbOracleProtocols,
        p as p,
    )
    from flext_db_oracle.settings import FlextDbOracleSettings as FlextDbOracleSettings
    from flext_db_oracle.typings import FlextDbOracleTypes as FlextDbOracleTypes, t as t
    from flext_db_oracle.utilities import (
        FlextDbOracleUtilities as FlextDbOracleUtilities,
        u as u,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".api": (
            "FlextDbOracleApi",
            "db_oracle",
        ),
        ".base": ("FlextDbOracleServiceBase",),
        ".constants": (
            "FlextDbOracleConstants",
            "c",
        ),
        ".dispatcher": ("FlextDbOracleDispatcher",),
        ".exceptions": (
            "FlextDbOracleExceptions",
            "e",
        ),
        ".models": (
            "FlextDbOracleModels",
            "m",
        ),
        ".protocols": (
            "FlextDbOracleProtocols",
            "p",
        ),
        ".settings": ("FlextDbOracleSettings",),
        ".typings": (
            "FlextDbOracleTypes",
            "t",
        ),
        ".utilities": (
            "FlextDbOracleUtilities",
            "u",
        ),
        "flext_cli": (
            "d",
            "h",
            "r",
            "s",
            "x",
        ),
    },
)


__all__: tuple[str, ...] = (
    "FlextDbOracleApi",
    "FlextDbOracleConstants",
    "FlextDbOracleDispatcher",
    "FlextDbOracleExceptions",
    "FlextDbOracleModels",
    "FlextDbOracleProtocols",
    "FlextDbOracleServiceBase",
    "FlextDbOracleSettings",
    "FlextDbOracleTypes",
    "FlextDbOracleUtilities",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "d",
    "db_oracle",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    public_exports=__all__,
)

# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d, h, r, x

    from flext_db_oracle.__version__ import (
        FlextDbOracleVersion,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version__,
        __version_info__,
    )
    from flext_db_oracle._config import FlextDbOracleConfig, config
    from flext_db_oracle._settings import (
        DbOracleSettings,
        FlextDbOracleSettings,
        settings,
    )
    from flext_db_oracle.api import FlextDbOracleApi, db_oracle
    from flext_db_oracle.base import FlextDbOracleServiceBase, s
    from flext_db_oracle.cli import main
    from flext_db_oracle.client import FlextDbOracleClient
    from flext_db_oracle.constants import FlextDbOracleConstants, c
    from flext_db_oracle.dispatcher import FlextDbOracleDispatcher
    from flext_db_oracle.exceptions import FlextDbOracleExceptions, e
    from flext_db_oracle.models import FlextDbOracleModels, m
    from flext_db_oracle.protocols import FlextDbOracleProtocols, p
    from flext_db_oracle.typings import FlextDbOracleTypes, t
    from flext_db_oracle.utilities import FlextDbOracleUtilities, u


__all__: tuple[str, ...] = (
    "DbOracleSettings",
    "FlextDbOracleApi",
    "FlextDbOracleClient",
    "FlextDbOracleConfig",
    "FlextDbOracleConstants",
    "FlextDbOracleDispatcher",
    "FlextDbOracleExceptions",
    "FlextDbOracleModels",
    "FlextDbOracleProtocols",
    "FlextDbOracleServiceBase",
    "FlextDbOracleSettings",
    "FlextDbOracleTypes",
    "FlextDbOracleUtilities",
    "FlextDbOracleVersion",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "config",
    "d",
    "db_oracle",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "DbOracleSettings": "._settings",
        "FlextDbOracleApi": ".api",
        "FlextDbOracleClient": ".client",
        "FlextDbOracleConfig": "._config",
        "FlextDbOracleConstants": ".constants",
        "FlextDbOracleDispatcher": ".dispatcher",
        "FlextDbOracleExceptions": ".exceptions",
        "FlextDbOracleModels": ".models",
        "FlextDbOracleProtocols": ".protocols",
        "FlextDbOracleServiceBase": ".base",
        "FlextDbOracleSettings": "._settings",
        "FlextDbOracleTypes": ".typings",
        "FlextDbOracleUtilities": ".utilities",
        "FlextDbOracleVersion": ".__version__",
        "__author__": ".__version__",
        "__author_email__": ".__version__",
        "__description__": ".__version__",
        "__license__": ".__version__",
        "__title__": ".__version__",
        "__url__": ".__version__",
        "__version_info__": ".__version__",
        "c": ".constants",
        "config": "._config",
        "d": "flext_core",
        "db_oracle": ".api",
        "e": ".exceptions",
        "h": "flext_core",
        "m": ".models",
        "main": ".cli",
        "p": ".protocols",
        "r": "flext_core",
        "s": ".base",
        "settings": "._settings",
        "t": ".typings",
        "u": ".utilities",
        "x": "flext_core",
    }),
    public_exports=__all__,
)

if not TYPE_CHECKING:
    from flext_db_oracle.__version__ import __version__

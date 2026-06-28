# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)
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
    from flext_db_oracle._models.password import (
        FlextDbOraclePassword as FlextDbOraclePassword,
    )
    from flext_db_oracle._utilities.db_oracle import (
        FlextDbOracleUtilitiesDbOracle as FlextDbOracleUtilitiesDbOracle,
    )
    from flext_db_oracle.api import (
        FlextDbOracleApi as FlextDbOracleApi,
        db_oracle as db_oracle,
    )
    from flext_db_oracle.base import (
        FlextDbOracleServiceBase as FlextDbOracleServiceBase,
    )
    from flext_db_oracle.client import (
        FlextDbOracleClient as FlextDbOracleClient,
        client as client,
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
    from flext_db_oracle.services.api_runtime import (
        FlextDbOracleApiRuntime as FlextDbOracleApiRuntime,
    )
    from flext_db_oracle.services.connection import (
        FlextDbOracleServiceConnection as FlextDbOracleServiceConnection,
    )
    from flext_db_oracle.services.facade import (
        FlextDbOracleServices as FlextDbOracleServices,
    )
    from flext_db_oracle.services.plugin import (
        FlextDbOracleServicePlugin as FlextDbOracleServicePlugin,
    )
    from flext_db_oracle.services.query import (
        FlextDbOracleServiceQuery as FlextDbOracleServiceQuery,
    )
    from flext_db_oracle.services.schema import (
        FlextDbOracleServiceSchema as FlextDbOracleServiceSchema,
    )
    from flext_db_oracle.services.singer import (
        FlextDbOracleServiceSinger as FlextDbOracleServiceSinger,
    )
    from flext_db_oracle.services.sql_builder import (
        FlextDbOracleServiceSqlBuilder as FlextDbOracleServiceSqlBuilder,
    )
    from flext_db_oracle.settings import FlextDbOracleSettings as FlextDbOracleSettings
    from flext_db_oracle.typings import FlextDbOracleTypes as FlextDbOracleTypes, t as t
    from flext_db_oracle.utilities import (
        FlextDbOracleUtilities as FlextDbOracleUtilities,
        u as u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "._models",
        "._utilities",
        ".services",
    ),
    build_lazy_import_map(
        {
            "._models.password": ("FlextDbOraclePassword",),
            "._utilities.db_oracle": ("FlextDbOracleUtilitiesDbOracle",),
            ".api": (
                "FlextDbOracleApi",
                "db_oracle",
            ),
            ".base": ("FlextDbOracleServiceBase",),
            ".client": (
                "FlextDbOracleClient",
                "client",
            ),
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
            ".services.api_runtime": ("FlextDbOracleApiRuntime",),
            ".services.connection": ("FlextDbOracleServiceConnection",),
            ".services.facade": ("FlextDbOracleServices",),
            ".services.plugin": ("FlextDbOracleServicePlugin",),
            ".services.query": ("FlextDbOracleServiceQuery",),
            ".services.schema": ("FlextDbOracleServiceSchema",),
            ".services.singer": ("FlextDbOracleServiceSinger",),
            ".services.sql_builder": ("FlextDbOracleServiceSqlBuilder",),
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
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name=__name__,
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    [
        "__author__",
        "__author_email__",
        "__description__",
        "__license__",
        "__title__",
        "__url__",
        "__version__",
        "__version_info__",
    ],
)

__all__: list[str] = [
    "FlextDbOracleApi",
    "FlextDbOracleApiRuntime",
    "FlextDbOracleClient",
    "FlextDbOracleConstants",
    "FlextDbOracleDispatcher",
    "FlextDbOracleExceptions",
    "FlextDbOracleModels",
    "FlextDbOracleProtocols",
    "FlextDbOracleServiceBase",
    "FlextDbOracleServiceConnection",
    "FlextDbOracleServicePlugin",
    "FlextDbOracleServiceQuery",
    "FlextDbOracleServiceSchema",
    "FlextDbOracleServiceSinger",
    "FlextDbOracleServiceSqlBuilder",
    "FlextDbOracleServices",
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
    "client",
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
]

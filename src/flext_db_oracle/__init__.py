# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle package."""

from __future__ import annotations

from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from flext_core import (
        d,
        e,
        h,
        r,
        x,
    )
    from flext_db_oracle._settings import (
        FlextDbOracleSettings as FlextDbOracleSettings,
        settings as settings,
    )
    from flext_db_oracle.api import (
        FlextDbOracleApi as FlextDbOracleApi,
        db_oracle as db_oracle,
    )
    from flext_db_oracle.base import (
        FlextDbOracleServiceBase as FlextDbOracleServiceBase,
        s as s,
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
    from flext_db_oracle.typings import FlextDbOracleTypes as FlextDbOracleTypes, t as t
    from flext_db_oracle.utilities import (
        FlextDbOracleUtilities as FlextDbOracleUtilities,
        u as u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    (".services",),
    build_lazy_import_map(
        {
            "._settings": ("FlextDbOracleSettings", "settings"),
            ".api": (
                "FlextDbOracleApi",
                "db_oracle",
            ),
            ".base": (
                "FlextDbOracleServiceBase",
                "s",
            ),
            ".constants": (
                "FlextDbOracleConstants",
                "c",
            ),
            ".dispatcher": ("FlextDbOracleDispatcher",),
            ".exceptions": ("FlextDbOracleExceptions",),
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
            ".typings": (
                "FlextDbOracleTypes",
                "t",
            ),
            ".utilities": (
                "FlextDbOracleUtilities",
                "u",
            ),
            "flext_core._root_typing_parts.facades": (
                "d",
                "e",
                "h",
                "r",
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


__all__: tuple[str, ...] = (
    "FlextDbOracleApi",
    "FlextDbOracleApiRuntime",
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
    "d",
    "db_oracle",
    "e",
    "h",
    "m",
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
    _LAZY_IMPORTS,
    public_exports=__all__,
)

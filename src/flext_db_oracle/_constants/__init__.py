# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Constants package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .base import FlextDbOracleConstantsBase
    from .exceptions import FlextDbOracleConstantsExceptions
__all__: tuple[str, ...] = (
    "FlextDbOracleConstantsBase", "FlextDbOracleConstantsExceptions",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("FlextDbOracleConstantsBase",),
            ".exceptions": ("FlextDbOracleConstantsExceptions",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

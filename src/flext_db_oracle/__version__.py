# AUTO-GENERATED FILE — Regenerate with: make gen
"""Package version and metadata for flext-db-oracle.

Subclass of ``FlextVersion`` — overrides only ``_metadata``.
All derived attributes (``__version__``, ``__title__``, etc.) are
computed automatically via ``FlextVersion.__init_subclass__``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from importlib.metadata import PackageMetadata, metadata
from typing import TYPE_CHECKING

from flext_core import FlextVersion, t

if TYPE_CHECKING:
    from flext_core import t


class FlextDbOracleVersion(FlextVersion):
    """flext-db-oracle version — MRO-derived from FlextVersion."""

    _metadata: PackageMetadata | t.StrMapping = metadata("flext-db-oracle")


__version__ = FlextDbOracleVersion.__version__
__version_info__ = FlextDbOracleVersion.__version_info__
__title__ = FlextDbOracleVersion.__title__
__description__ = FlextDbOracleVersion.__description__
__author__ = FlextDbOracleVersion.__author__
__author_email__ = FlextDbOracleVersion.__author_email__
__license__ = FlextDbOracleVersion.__license__
__url__ = FlextDbOracleVersion.__url__
__all__: list[str] = [
    "FlextDbOracleVersion",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
]

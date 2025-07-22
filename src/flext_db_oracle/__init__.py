"""FLEXT DB ORACLE - Enterprise Oracle Database Integration with simplified imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Version 0.7.0 - Enterprise Oracle Database with simplified public API:
- All common imports available from root: from flext_db_oracle import OracleConnectionService
- Built on flext-core foundation for robust Oracle database integration
- Deprecation warnings for internal imports
"""

from __future__ import annotations

import contextlib
import importlib.metadata
import warnings

# Import from flext-core for foundational patterns
from flext_core import (
    BaseConfig,
    BaseConfig as OracleBaseConfig,
    DomainBaseModel,
    DomainBaseModel as BaseModel,
    DomainError as OracleError,
    DomainValueObject as ValueObject,
    ServiceResult,
    ServiceResult as FlextServiceResult,
    ValidationError,
)

try:
    __version__ = importlib.metadata.version("flext-db-oracle")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.7.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())


class FlextDbOracleDeprecationWarning(DeprecationWarning):
    """Custom deprecation warning for FLEXT DB ORACLE import changes."""


def _show_deprecation_warning(old_import: str, new_import: str) -> None:
    """Show deprecation warning for import paths."""
    message_parts = [
        f"⚠️  DEPRECATED IMPORT: {old_import}",
        f"✅ USE INSTEAD: {new_import}",
        "🔗 This will be removed in version 1.0.0",
        "📖 See FLEXT DB ORACLE docs for migration guide",
    ]
    warnings.warn(
        "\n".join(message_parts),
        FlextDbOracleDeprecationWarning,
        stacklevel=3,
    )


# Re-export commonly used imports from flext-core - NO FALLBACKS (per user instructions)

# ================================
# SIMPLIFIED PUBLIC API EXPORTS
# ================================

# Configuration exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_db_oracle.config import OracleConfig

# Application Services exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_db_oracle.application.services import (
        OracleConnectionService,
        OracleQueryService,
        OracleSchemaService,
    )

# Domain Models exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_db_oracle.domain.models import (
        OracleConnectionInfo,
        OracleQueryResult,
        OracleSchemaInfo,
        OracleTableMetadata,
    )

# Utilities exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_db_oracle.utils import run_async_in_sync_context

# ================================
# PUBLIC API EXPORTS
# ================================

__all__ = [
    "BaseModel",
    "FlextDbOracleDeprecationWarning",
    "OracleBaseConfig",
    "OracleConfig",
    "OracleConnectionInfo",
    "OracleConnectionService",
    "OracleError",
    "OracleQueryResult",
    "OracleQueryService",
    "OracleSchemaInfo",
    "OracleSchemaService",
    "OracleTableMetadata",
    "ServiceResult",
    "ValidationError",
    "ValueObject",
    "__version__",
    "__version_info__",
]

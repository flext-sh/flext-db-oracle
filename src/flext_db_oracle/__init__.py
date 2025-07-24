"""FLEXT DB ORACLE - Enterprise Oracle Database Integration with simplified imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Version 0.7.0 - Enterprise Oracle Database with simplified public API:
- All common imports available from root:
  from flext_db_oracle import FlextDbOracleConnectionService
- Built on flext-core foundation for robust Oracle database integration
- Deprecation warnings for internal imports
"""

from __future__ import annotations

import contextlib
import importlib.metadata
import warnings

# Import from flext-core for foundational patterns
from flext_core import (
    FlextResult as ServiceResult,
    FlextValueObject as BaseModel,
    FlextValueObject as DomainBaseModel,
    FlextValueObject as ValueObject,
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
    from flext_db_oracle.config import FlextDbOracleConfig

# Connection layer exports - actual implementations only
with contextlib.suppress(ImportError):
    from flext_db_oracle.connection.connection import FlextDbOracleConnection
    from flext_db_oracle.connection.pool import (
        ConnectionPool,
        FlextDbOracleConnectionPool,
    )

# SQL processing exports - actual implementations only
with contextlib.suppress(ImportError):
    from flext_db_oracle.sql.parser import SQLParser
    from flext_db_oracle.sql.validator import ValidationResult, ValidationRule

# Schema metadata exports - actual implementations only
with contextlib.suppress(ImportError):
    from flext_db_oracle.schema.metadata import (
        ColumnMetadata,
        ConstraintMetadata,
        ConstraintType,
        IndexMetadata,
        ObjectStatus,
        SchemaMetadata,
        TableMetadata,
        ViewMetadata,
    )

# Logging utilities - actual implementations only
with contextlib.suppress(ImportError):
    from flext_db_oracle.logging_utils import get_logger

# ================================
# PUBLIC API EXPORTS
# ================================

__all__ = [
    # Core base classes from flext-core
    "BaseModel",
    # Schema Metadata - actual implementations
    "ColumnMetadata",
    "ConnectionPool",  # Backward compatibility alias
    "ConstraintMetadata",
    "ConstraintType",
    "DomainBaseModel",
    # Configuration - actual implementations
    "FlextDbOracleConfig",
    # Connection and Pool - actual implementations
    "FlextDbOracleConnection",
    "FlextDbOracleConnectionPool",
    # Deprecation warnings
    "FlextDbOracleDeprecationWarning",
    "IndexMetadata",
    "ObjectStatus",
    # SQL Processing - actual implementations
    "SQLParser",
    "SchemaMetadata",
    "ServiceResult",
    "TableMetadata",
    "ValidationResult",
    "ValidationRule",
    "ValueObject",
    "ViewMetadata",
    # Metadata
    "__version__",
    "__version_info__",
    # Utilities - actual implementations
    "get_logger",
]

"""Oracle database type definitions following flext-core patterns.

This module provides type definitions and TypedDict definitions for the
flext-db-oracle library, following the flext-core typing patterns.

The module serves as a central location for:
- TypedDict definitions for structured data
- Generic type parameters and constraints

**LEGACY ALIASES REMOVED** - Use models directly from flext_db_oracle.models

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypedDict, TypeGuard

from flext_core import FlextProtocols

__all__ = [
    # Type aliases and dicts
    "DatabaseColumnDict",
    "DatabaseRowDict",
    "DatabaseRowProtocol",
    "OracleColumnInfo",
    "OracleConnectionInfo",
    "OracleTableInfo",
    "PluginLikeProtocol",
    "SafeStringList",
    # Type guards and utilities
    "has_get_info_method",
    "has_unwrap_or_method",
    "is_database_row",
    "is_dict_like",
    "is_flext_plugin",
    "is_plugin_like",
    "is_result_like",
    "is_string_list",
    "safe_database_row_dict",
    "safe_str_list",
]

# =============================================================================
# LEGACY ALIASES REMOVED - USE MODELS DIRECTLY
# =============================================================================

# All legacy T-prefixed aliases have been REMOVED.
# Use models directly from flext_db_oracle.models:
# - FlextDbOracleColumn (not TDbOracleColumn)
# - FlextDbOracleConnectionStatus (not TDbOracleConnectionStatus)
# - FlextDbOracleQueryResult (not TDbOracleQueryResult)
# - FlextDbOracleSchema (not TDbOracleSchema)
# - FlextDbOracleTable (not TDbOracleTable)

# =============================================================================
# TYPEDDICT DEFINITIONS - For unstructured data interchange
# =============================================================================


class OracleColumnInfo(TypedDict, total=False):
    """TypedDict for Oracle column information from database queries."""

    column_name: str
    data_type: str
    nullable: bool
    data_length: int | None
    data_precision: int | None
    data_scale: int | None
    column_id: int
    default_value: str | None
    comments: str | None


class OracleConnectionInfo(TypedDict, total=False):
    """TypedDict for Oracle connection information."""

    host: str
    port: int
    service_name: str
    username: str
    password: str
    charset: str | None
    pool_min: int | None
    pool_max: int | None
    connect_timeout: int | None


class OracleTableInfo(TypedDict, total=False):
    """TypedDict for Oracle table information from database queries."""

    table_name: str
    schema_name: str
    tablespace_name: str | None
    table_comment: str | None
    column_count: int | None
    row_count: int | None
    created_date: str | None
    last_analyzed: str | None


# =============================================================================
# INLINE TYPE GUARDS - Resolve PyRight "unknown" type warnings
# =============================================================================


# Type alias for plugin protocol from flext-core
type PluginLikeProtocol = FlextProtocols.Extensions.Plugin


def is_plugin_like(obj: object) -> TypeGuard[FlextProtocols.Extensions.Plugin]:
    """Type guard to check if object has plugin-like attributes.

    Resolves PyRight warnings about unknown attribute access on object types.
    """
    return (
        hasattr(obj, "name")
        and hasattr(obj, "version")
        and hasattr(obj, "get_info")
        and callable(getattr(obj, "get_info", None))
    )


def is_flext_plugin(obj: object) -> bool:
    """Type guard for FlextPlugin protocol compatibility.

    Checks if object implements the core FlextPlugin protocol methods.
    """
    return (
        hasattr(obj, "initialize")
        and hasattr(obj, "shutdown")
        and hasattr(obj, "get_info")
        and callable(getattr(obj, "initialize", None))
        and callable(getattr(obj, "shutdown", None))
        and callable(getattr(obj, "get_info", None))
    )


def is_dict_like(obj: object) -> TypeGuard[dict[str, object]]:
    """Type guard for dict-like objects.

    Resolves PyRight warnings about dict access on unknown types.
    """
    return hasattr(obj, "get") and hasattr(obj, "items") and hasattr(obj, "keys")


def is_result_like(obj: object) -> TypeGuard[object]:
    """Type guard for FlextResult-like objects.

    Checks if object has FlextResult-like interface.
    """
    return (
        hasattr(obj, "is_success")
        and hasattr(obj, "is_failure")
        and hasattr(obj, "value")
        and hasattr(obj, "error")
        and hasattr(obj, "unwrap_or")
    )


def has_get_info_method(obj: object) -> TypeGuard[object]:
    """Type guard for objects with get_info method.

    Specifically resolves 'Cannot access attribute "get_info" for class "object"' warnings.
    """
    return hasattr(obj, "get_info") and callable(getattr(obj, "get_info", None))


def has_unwrap_or_method(obj: object) -> bool:
    """Type guard for objects with unwrap_or method.

    Resolves 'Cannot access attribute "unwrap_or" for class "object"' warnings.
    """
    return hasattr(obj, "unwrap_or") and callable(getattr(obj, "unwrap_or", None))


# =============================================================================
# DATABASE TYPE SAFETY - Specific protocols for Oracle data
# =============================================================================


# Python 3.13+ type aliases using modern syntax
type DatabaseRowProtocol = dict[str, object]
type DatabaseRowDict = dict[str, object]
type DatabaseColumnDict = dict[str, str | int | None]
type SafeStringList = list[str]

# Modern type aliases for Oracle-specific data
type OracleConnectionDict = dict[str, str | int | None]
type OracleTableDict = dict[str, str | int | None]
type ValidationResult = bool
type ConfigDict = dict[str, object]


def is_string_list(obj: object) -> TypeGuard[SafeStringList]:
    """Type guard for list of strings."""
    return isinstance(obj, list) and all(isinstance(item, str) for item in obj)


def is_database_row(obj: object) -> TypeGuard[DatabaseRowDict]:
    """Type guard for database row dictionary."""
    return isinstance(obj, dict) and all(isinstance(k, str) for k in obj)


def safe_str_list(obj: object) -> SafeStringList:
    """Convert unknown list to typed string list safely."""
    if is_string_list(obj):
        return obj
    if isinstance(obj, list):
        return [str(item) for item in obj]
    return []


def safe_database_row_dict(obj: object) -> DatabaseRowDict:
    """Convert unknown dict to typed database row dict safely."""
    if is_database_row(obj):
        return obj
    if isinstance(obj, dict):
        return {str(k): v for k, v in obj.items()}
    return {}

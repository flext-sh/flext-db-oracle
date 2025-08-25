"""FLEXT DB Oracle Typings following Flext[Area][Module] pattern.

This module provides the FlextDbOracleTypings class with consolidated
type definitions and TypedDict classes following FLEXT architectural
patterns with DRY principles.

Single consolidated class containing ALL Oracle type definitions organized
internally, following SOLID principles and eliminating duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypedDict, TypeGuard

from flext_core import FlextFactory, FlextProtocols

__all__ = [
    "DatabaseColumnDict",
    "DatabaseRowDict",
    "DatabaseRowProtocol",
    "FlextDbOracleTypings",
    "OracleColumnInfo",
    "OracleConnectionInfo",
    "OracleTableInfo",
    "PluginLikeProtocol",
    "SafeStringList",
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


class FlextDbOracleTypings(FlextFactory):
    """Oracle Database Typings following Flext[Area][Module] pattern.

    Single consolidated class containing ALL Oracle type definitions
    organized internally, following SOLID principles and DRY methodology.

    This class consolidates ALL Oracle typing functionality into a single
    entry point eliminating duplication and multiple small classes.
    """

    # =============================================================================
    # TYPEDDICT DEFINITIONS - Consolidated Oracle data structures
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
    # TYPE ALIASES - Python 3.13+ modern syntax consolidated
    # =============================================================================

    # Core database types
    type DatabaseRowProtocol = dict[str, object]
    type DatabaseRowDict = dict[str, object]
    type DatabaseColumnDict = dict[str, str | int | None]
    type SafeStringList = list[str]

    # Oracle-specific types
    type OracleConnectionDict = dict[str, str | int | None]
    type OracleTableDict = dict[str, str | int | None]
    type ValidationResult = bool
    type ConfigDict = dict[str, object]

    # Plugin types
    type PluginLikeProtocol = FlextProtocols.Extensions.Plugin

    # =============================================================================
    # TYPE GUARDS - Consolidated validation functions
    # =============================================================================

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def is_dict_like(obj: object) -> TypeGuard[dict[str, object]]:
        """Type guard for dict-like objects.

        Resolves PyRight warnings about dict access on unknown types.
        """
        return hasattr(obj, "get") and hasattr(obj, "items") and hasattr(obj, "keys")

    @staticmethod
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

    @staticmethod
    def has_get_info_method(obj: object) -> TypeGuard[object]:
        """Type guard for objects with get_info method.

        Specifically resolves 'Cannot access attribute "get_info" for class "object"' warnings.
        """
        return hasattr(obj, "get_info") and callable(getattr(obj, "get_info", None))

    @staticmethod
    def has_unwrap_or_method(obj: object) -> bool:
        """Type guard for objects with unwrap_or method.

        Resolves 'Cannot access attribute "unwrap_or" for class "object"' warnings.
        """
        return hasattr(obj, "unwrap_or") and callable(getattr(obj, "unwrap_or", None))

    @staticmethod
    def is_string_list(obj: object) -> TypeGuard[SafeStringList]:
        """Type guard for list of strings."""
        return isinstance(obj, list) and all(isinstance(item, str) for item in obj)

    @staticmethod
    def is_database_row(obj: object) -> TypeGuard[DatabaseRowDict]:
        """Type guard for database row dictionary."""
        return isinstance(obj, dict) and all(isinstance(k, str) for k in obj)

    # =============================================================================
    # UTILITY FUNCTIONS - Safe type conversions
    # =============================================================================

    @classmethod
    def safe_str_list(cls, obj: object) -> SafeStringList:
        """Convert unknown list to typed string list safely."""
        if cls.is_string_list(obj):
            return obj
        if isinstance(obj, list):
            return [str(item) for item in obj]
        return []

    @classmethod
    def safe_database_row_dict(cls, obj: object) -> DatabaseRowDict:
        """Convert unknown dict to typed database row dict safely."""
        if cls.is_database_row(obj):
            return obj
        if isinstance(obj, dict):
            return {str(k): v for k, v in obj.items()}
        return {}

    # =============================================================================
    # BACKWARD COMPATIBILITY ALIASES - Consolidated
    # =============================================================================

    # Create compatibility classes as internal references
    class TypeGuards:
        """Backward compatibility - use FlextDbOracleTypings directly."""

        def __getattr__(self, name: str) -> object:
            """Get attribute from FlextDbOracleTypings for backward compatibility."""
            return getattr(FlextDbOracleTypings, name)

    class TypeAliases:
        """Backward compatibility - use FlextDbOracleTypings directly."""

        def __getattr__(self, name: str) -> object:
            """Get attribute from FlextDbOracleTypings for backward compatibility."""
            return getattr(FlextDbOracleTypings, name)


# =============================================================================
# MODULE-LEVEL BACKWARD COMPATIBILITY FUNCTIONS
# =============================================================================

# Type alias for plugin protocol from flext-core
type PluginLikeProtocol = FlextProtocols.Extensions.Plugin

# Python 3.13+ type aliases using modern syntax
type DatabaseRowProtocol = dict[str, object]
type DatabaseRowDict = dict[str, object]
type DatabaseColumnDict = dict[str, str | int | None]
type SafeStringList = list[str]

# Module-level functions for backward compatibility
def is_plugin_like(obj: object) -> TypeGuard[FlextProtocols.Extensions.Plugin]:
    """Backward compatibility wrapper."""
    return FlextDbOracleTypings.is_plugin_like(obj)

def is_flext_plugin(obj: object) -> bool:
    """Backward compatibility wrapper."""
    return FlextDbOracleTypings.is_flext_plugin(obj)

def is_dict_like(obj: object) -> TypeGuard[dict[str, object]]:
    """Backward compatibility wrapper."""
    return FlextDbOracleTypings.is_dict_like(obj)

def is_result_like(obj: object) -> TypeGuard[object]:
    """Backward compatibility wrapper."""
    return FlextDbOracleTypings.is_result_like(obj)

def has_get_info_method(obj: object) -> TypeGuard[object]:
    """Backward compatibility wrapper."""
    return FlextDbOracleTypings.has_get_info_method(obj)

def has_unwrap_or_method(obj: object) -> bool:
    """Backward compatibility wrapper."""
    return FlextDbOracleTypings.has_unwrap_or_method(obj)

def is_string_list(obj: object) -> TypeGuard[SafeStringList]:
    """Backward compatibility wrapper."""
    return FlextDbOracleTypings.is_string_list(obj)

def is_database_row(obj: object) -> TypeGuard[DatabaseRowDict]:
    """Backward compatibility wrapper."""
    return FlextDbOracleTypings.is_database_row(obj)

def safe_str_list(obj: object) -> SafeStringList:
    """Backward compatibility wrapper."""
    return FlextDbOracleTypings.safe_str_list(obj)

def safe_database_row_dict(obj: object) -> DatabaseRowDict:
    """Backward compatibility wrapper."""
    return FlextDbOracleTypings.safe_database_row_dict(obj)

# Module-level backward compatibility aliases
OracleColumnInfo = FlextDbOracleTypings.OracleColumnInfo
OracleConnectionInfo = FlextDbOracleTypings.OracleConnectionInfo
OracleTableInfo = FlextDbOracleTypings.OracleTableInfo

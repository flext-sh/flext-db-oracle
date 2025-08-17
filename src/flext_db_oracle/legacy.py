"""Legacy compatibility facade for flext-db-oracle.

This module provides backward compatibility for APIs that may have been refactored
or renamed during the Pydantic modernization process. It follows the same pattern
as flext-core's legacy.py to ensure consistent facade patterns across the ecosystem.

All imports here should be considered deprecated and may issue warnings.
Modern code should import directly from the appropriate modules.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import warnings
from collections.abc import Mapping

# Import Oracle components for legacy aliases
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.connection import FlextDbOracleConnection

# Import modern implementations to re-export under legacy names
from flext_db_oracle.exceptions import (
    FlextDbOracleAuthenticationError,
    FlextDbOracleConfigurationError,
    FlextDbOracleConnectionError,
    FlextDbOracleError,
    FlextDbOracleErrorCodes,
    FlextDbOracleMetadataError,
    FlextDbOracleProcessingError,
    FlextDbOracleQueryError,
    FlextDbOracleTimeoutError,
    FlextDbOracleValidationError,
)
from flext_db_oracle.metadata import FlextDbOracleMetadataManager
from flext_db_oracle.types import (
    FlextDbOracleConnectionStatus,
)

# Create aliases for backward compatibility
FlextDbOracleMetadata = FlextDbOracleMetadataManager
FlextDbOracleConnectionInfo = FlextDbOracleConnectionStatus


def _deprecation_warning(old_name: str, new_name: str) -> None:
    """Issue a deprecation warning for legacy imports."""
    warnings.warn(
        f"{old_name} is deprecated, use {new_name} instead",
        DeprecationWarning,
        stacklevel=3,
    )


# Legacy aliases for common Oracle services - likely used names
def OracleApi(  # noqa: N802
    config: FlextDbOracleConfig | None = None,
    context_name: str = "oracle",
) -> FlextDbOracleApi:
    """Legacy alias for FlextDbOracleApi."""
    _deprecation_warning("OracleApi", "FlextDbOracleApi")
    return FlextDbOracleApi(config=config, context_name=context_name)


def OracleDatabase(  # noqa: N802
    config: FlextDbOracleConfig | None = None,
    context_name: str = "oracle",
) -> FlextDbOracleApi:
    """Legacy alias for FlextDbOracleApi."""
    _deprecation_warning("OracleDatabase", "FlextDbOracleApi")
    return FlextDbOracleApi(config=config, context_name=context_name)


def OracleConnection(  # noqa: N802
    config: FlextDbOracleConfig | None = None,
) -> FlextDbOracleConnection:
    """Legacy alias for FlextDbOracleConnection."""
    _deprecation_warning("OracleConnection", "FlextDbOracleConnection")
    # Create default config if not provided
    if config is None:
        config = FlextDbOracleConfig()
    return FlextDbOracleConnection(config=config)


def OracleConfig(**kwargs: object) -> FlextDbOracleConfig:  # noqa: N802
    """Legacy alias for FlextDbOracleConfig."""
    _deprecation_warning("OracleConfig", "FlextDbOracleConfig")
    # Use model_validate for Pydantic v2 models
    return FlextDbOracleConfig.model_validate(kwargs)


def OracleMetadata(  # noqa: N802
    connection: FlextDbOracleConnection | None = None,
) -> FlextDbOracleMetadataManager:
    """Legacy alias for FlextDbOracleMetadata."""
    _deprecation_warning("OracleMetadata", "FlextDbOracleMetadataManager")
    # Create default connection if not provided
    if connection is None:
        config = FlextDbOracleConfig()
        connection = FlextDbOracleConnection(config=config)
    return FlextDbOracleMetadata(connection=connection)


# Legacy exception aliases (more concise names that were probably used)
def OracleError(  # noqa: N802
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleError:
    """Legacy alias for FlextDbOracleError."""
    _deprecation_warning("OracleError", "FlextDbOracleError")
    # Merge kwargs into context if both provided
    if context is not None:
        merged_context = dict(context)
        merged_context.update(kwargs)
    else:
        merged_context = kwargs
    return FlextDbOracleError(message, code=code, context=merged_context)


def OracleConnectionError(  # noqa: N802
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleConnectionError:
    """Legacy alias for FlextDbOracleConnectionError."""
    _deprecation_warning("OracleConnectionError", "FlextDbOracleConnectionError")
    # Merge kwargs into context if both provided
    if context is not None:
        merged_context = dict(context)
        merged_context.update(kwargs)
    else:
        merged_context = kwargs
    return FlextDbOracleConnectionError(message, code=code, context=merged_context)


def OracleQueryError(  # noqa: N802
    message: str,
    *,
    query: str | None = None,
    operation: str | None = None,
    execution_time: float | None = None,
    rows_affected: int | None = None,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleQueryError:
    """Legacy alias for FlextDbOracleQueryError."""
    _deprecation_warning("OracleQueryError", "FlextDbOracleQueryError")
    # Convert code if needed
    if code is not None and not isinstance(code, FlextDbOracleErrorCodes):
        # Use default code if conversion not possible
        code = FlextDbOracleErrorCodes.ORACLE_QUERY_ERROR

    # Merge kwargs into context if both provided
    if context is not None:
        merged_context = dict(context)
        merged_context.update(kwargs)
    else:
        merged_context = kwargs
    return FlextDbOracleQueryError(
        message,
        query=query,
        operation=operation,
        execution_time=execution_time,
        rows_affected=rows_affected,
        code=code,
        context=merged_context,
    )


def OracleConfigurationError(  # noqa: N802
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleConfigurationError:
    """Legacy alias for FlextDbOracleConfigurationError."""
    _deprecation_warning("OracleConfigurationError", "FlextDbOracleConfigurationError")
    # Merge kwargs into context if both provided
    if context is not None:
        merged_context = dict(context)
        merged_context.update(kwargs)
    else:
        merged_context = kwargs
    return FlextDbOracleConfigurationError(message, code=code, context=merged_context)


def OracleValidationError(  # noqa: N802
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleValidationError:
    """Legacy alias for FlextDbOracleValidationError."""
    _deprecation_warning("OracleValidationError", "FlextDbOracleValidationError")
    # Merge kwargs into context if both provided
    if context is not None:
        merged_context = dict(context)
        merged_context.update(kwargs)
    else:
        merged_context = kwargs
    return FlextDbOracleValidationError(message, code=code, context=merged_context)


def OracleTimeoutError(  # noqa: N802
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleTimeoutError:
    """Legacy alias for FlextDbOracleTimeoutError."""
    _deprecation_warning("OracleTimeoutError", "FlextDbOracleTimeoutError")
    # Merge kwargs into context if both provided
    if context is not None:
        merged_context = dict(context)
        merged_context.update(kwargs)
    else:
        merged_context = kwargs
    return FlextDbOracleTimeoutError(message, code=code, context=merged_context)


def OracleAuthenticationError(  # noqa: N802
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleAuthenticationError:
    """Legacy alias for FlextDbOracleAuthenticationError."""
    _deprecation_warning(
        "OracleAuthenticationError",
        "FlextDbOracleAuthenticationError",
    )
    # Merge kwargs into context if both provided
    if context is not None:
        merged_context = dict(context)
        merged_context.update(kwargs)
    else:
        merged_context = kwargs
    return FlextDbOracleAuthenticationError(message, code=code, context=merged_context)


def OracleProcessingError(  # noqa: N802
    message: str,
    *,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleProcessingError:
    """Legacy alias for FlextDbOracleProcessingError."""
    _deprecation_warning("OracleProcessingError", "FlextDbOracleProcessingError")
    # Merge kwargs into context if both provided
    if context is not None:
        merged_context = dict(context)
        merged_context.update(kwargs)
    else:
        merged_context = kwargs
    return FlextDbOracleProcessingError(message, code=code, context=merged_context)


def OracleMetadataError(  # noqa: N802
    message: str,
    *,
    schema_name: str | None = None,
    object_name: str | None = None,
    object_type: str | None = None,
    operation: str | None = None,
    code: object | None = None,
    context: Mapping[str, object] | None = None,
    **kwargs: object,
) -> FlextDbOracleMetadataError:
    """Legacy alias for FlextDbOracleMetadataError."""
    _deprecation_warning("OracleMetadataError", "FlextDbOracleMetadataError")
    # Convert code if needed
    if code is not None and not isinstance(code, FlextDbOracleErrorCodes):
        # Use default code if conversion not possible
        code = FlextDbOracleErrorCodes.ORACLE_METADATA_ERROR

    # Merge kwargs into context if both provided
    if context is not None:
        merged_context = dict(context)
        merged_context.update(kwargs)
    else:
        merged_context = kwargs
    return FlextDbOracleMetadataError(
        message,
        schema_name=schema_name,
        object_name=object_name,
        object_type=object_type,
        operation=operation,
        code=code,
        context=merged_context,
    )


# Alternative naming patterns that might have been used
def FlextOracleApi(  # noqa: N802
    config: FlextDbOracleConfig | None = None,
    context_name: str = "oracle",
) -> FlextDbOracleApi:
    """Legacy alias for FlextDbOracleApi (alternate naming)."""
    _deprecation_warning("FlextOracleApi", "FlextDbOracleApi")
    return FlextDbOracleApi(config=config, context_name=context_name)


def SimpleOracleConnection(  # noqa: N802
    config: FlextDbOracleConfig | None = None,
) -> FlextDbOracleConnection:
    """Legacy alias for FlextDbOracleConnection (simple variant)."""
    _deprecation_warning("SimpleOracleConnection", "FlextDbOracleConnection")
    # Create default config if not provided
    if config is None:
        config = FlextDbOracleConfig()
    return FlextDbOracleConnection(config=config)


# Legacy factory function aliases
def create_oracle_connection(
    config: FlextDbOracleConfig | None = None,
) -> FlextDbOracleConnection:
    """Legacy alias for FlextDbOracleConnection constructor."""
    _deprecation_warning("create_oracle_connection", "FlextDbOracleConnection")
    # Create default config if not provided
    if config is None:
        config = FlextDbOracleConfig()
    return FlextDbOracleConnection(config=config)


def create_oracle_api(
    config: FlextDbOracleConfig | None = None,
    context_name: str = "oracle",
) -> FlextDbOracleApi:
    """Legacy alias for FlextDbOracleApi constructor."""
    _deprecation_warning("create_oracle_api", "FlextDbOracleApi")
    return FlextDbOracleApi(config=config, context_name=context_name)


def setup_oracle_database(
    config: FlextDbOracleConfig | None = None,
    context_name: str = "oracle",
) -> FlextDbOracleApi:
    """Legacy alias for FlextDbOracleApi constructor."""
    _deprecation_warning("setup_oracle_database", "FlextDbOracleApi")
    return FlextDbOracleApi(config=config, context_name=context_name)


# Legacy parameter class aliases for backwards compatibility
def OracleMetadataErrorParams(**kwargs: object) -> dict[str, object]:  # noqa: N802
    """Legacy parameter class replaced by keyword arguments."""
    _deprecation_warning(
        "OracleMetadataErrorParams",
        "keyword arguments in FlextDbOracleMetadataError",
    )
    return dict(kwargs)


def OracleQueryErrorParams(**kwargs: object) -> dict[str, object]:  # noqa: N802
    """Legacy parameter class replaced by keyword arguments."""
    _deprecation_warning(
        "OracleQueryErrorParams",
        "keyword arguments in FlextDbOracleQueryError",
    )
    return dict(kwargs)


# Export legacy aliases for backward compatibility
__all__ = [
    # Alternative naming patterns
    "FlextOracleApi",
    # Legacy service aliases
    "OracleApi",
    "OracleAuthenticationError",
    "OracleConfig",
    "OracleConfigurationError",
    "OracleConnection",
    "OracleConnectionError",
    "OracleDatabase",
    # Legacy exception aliases (concise forms)
    "OracleError",
    "OracleMetadata",
    "OracleMetadataError",
    # Legacy parameter classes
    "OracleMetadataErrorParams",
    "OracleProcessingError",
    "OracleQueryError",
    "OracleQueryErrorParams",
    "OracleTimeoutError",
    "OracleValidationError",
    "SimpleOracleConnection",
    "create_oracle_api",
    # Legacy factory functions
    "create_oracle_connection",
    "setup_oracle_database",
]

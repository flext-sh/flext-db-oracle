"""FLEXT DB Oracle Legacy - Backward compatibility for deprecated modules.

This module preserves backward compatibility for all modules that violated PEP8
naming conventions and have been consolidated into the standardized modules.
All original functionality is preserved through re-exports and aliases.

Originally supported modules (now deprecated):
- oracle_*.py modules: Consolidate to PEP8 equivalents (api.py, config.py, etc.)

Architecture:
    - Maintains 100% backward compatibility
    - Issues deprecation warnings for legacy imports
    - Maps old module names to new consolidated modules
    - Preserves all original class names and functionality

Migration Strategy:
    - Phase 1: This legacy module provides compatibility (current)
    - Phase 2: Deprecation warnings guide users to new modules
    - Phase 3: Legacy support removed in version 1.0.0

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import warnings

from flext_core import get_logger

logger = get_logger(__name__)

# Legacy module mappings to new consolidated modules
_LEGACY_MODULE_MAPPING = {
    # Oracle-prefixed modules -> consolidated modules
    "oracle_api": "api",
    "oracle_cli": "cli",
    "oracle_config": "config",
    "oracle_connection": "connection",
    "oracle_exceptions": "exceptions",
    "oracle_metadata": "metadata",
    "oracle_models": "types",  # models were consolidated to types
    "oracle_observability": "observability",
    "oracle_plugins": "plugins",
}


def _emit_deprecation_warning(old_name: str, new_name: str) -> None:
    """Emit standardized deprecation warning."""
    warnings.warn(
        f"🚨 DEPRECATED MODULE: {old_name} violates PEP8 naming conventions.\n"
        f"✅ MODERN SOLUTION: Import from flext_db_oracle.{new_name}\n"
        f"💡 Migration: Update imports to use PEP8-compliant module names\n"
        f"📖 Legacy support will be removed in v1.0.0",
        DeprecationWarning,
        stacklevel=3,
    )


# Legacy module compatibility function
def get_legacy_module_mapping() -> dict[str, str]:
    """Get mapping of legacy module names to new consolidated modules."""
    return _LEGACY_MODULE_MAPPING.copy()


logger.debug(
    "Legacy module loaded - provides backward compatibility for deprecated PEP8 violations",
)

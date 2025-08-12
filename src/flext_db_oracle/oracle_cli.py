"""LEGACY MODULE: oracle_cli.py - Use flext_db_oracle.cli instead.

This module provides backward compatibility for code importing from oracle_cli.
All functionality has been consolidated into the PEP8-compliant cli.py module.

DEPRECATED: This module violates PEP8 naming conventions.
MIGRATION: Import from flext_db_oracle.cli instead.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import warnings

warnings.warn(
    "🚨 DEPRECATED MODULE: oracle_cli violates PEP8 naming conventions.\n"
    "✅ MODERN SOLUTION: Import from flext_db_oracle.cli\n"
    "💡 Migration: Update imports to use PEP8-compliant module names\n"
    "📖 Legacy support will be removed in v1.0.0",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export specific functionality from the consolidated cli module

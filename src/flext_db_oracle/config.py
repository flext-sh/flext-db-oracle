"""Oracle database configuration facade module.

This module provides facade access to configuration functionality from models.py.
Following the FLEXT architectural patterns with consolidated functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle.models import FlextDbOracleConfig

# Re-export configuration for compatibility
__all__ = ["FlextDbOracleConfig"]

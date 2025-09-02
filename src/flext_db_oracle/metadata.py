"""Oracle database metadata facade module.

This module provides facade access to metadata functionality from services.py.
Following the FLEXT architectural patterns with consolidated functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle.services import FlextDbOracleMetadataManager

# Re-export metadata manager for compatibility
__all__ = ["FlextDbOracleMetadataManager"]

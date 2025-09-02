"""Oracle database fields facade module.

This module provides facade access to field functionality from models.py.
Following the FLEXT architectural patterns with consolidated functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle.models import (
    ConnectionFields,
    DatabaseMetadataFields,
    QueryFields,
    ValidationFields,
)

# Re-export field classes for compatibility
__all__ = [
    "ConnectionFields",
    "DatabaseMetadataFields",
    "QueryFields",
    "ValidationFields",
]

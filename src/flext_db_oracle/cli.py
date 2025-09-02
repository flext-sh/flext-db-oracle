"""Oracle database CLI facade module.

This module provides facade access to CLI functionality from client.py.
Following the FLEXT architectural patterns with consolidated functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle.client import FlextDbOracleCliApplication, get_app, oracle_cli
from flext_db_oracle.utilities import FlextDbOracleUtilities

# Re-export CLI components for compatibility
__all__ = ["FlextDbOracleCliApplication", "FlextDbOracleUtilities", "get_app", "oracle_cli"]

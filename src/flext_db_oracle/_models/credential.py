"""Oracle password value object.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_db_oracle._models.base import FlextDbOracleModelsBase


class FlextDbOracleCredentialModel(FlextDbOracleModelsBase.CredentialRoot):
    """Password value object used by Oracle settings."""

    @override
    def __str__(self) -> str:
        """Return wrapped password as plain string."""
        return self.root

    def fetch_secret_value(self) -> str:
        """Return wrapped password for secret consumers."""
        return self.root

    def __hash__(self) -> int:
        """Return hash based on wrapped password value."""
        return hash(self.root)

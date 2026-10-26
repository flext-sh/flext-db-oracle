"""Oracle password value object.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle._models import FlextDbOracleModelsBase


class FlextDbOracleCredentialModel:
    """Credential declarations composed into the Oracle model namespace."""

    class Password(FlextDbOracleModelsBase.CredentialRoot):
        """Password value transported by the origin's root-model contract."""


__all__: tuple[str, ...] = ("FlextDbOracleCredentialModel",)

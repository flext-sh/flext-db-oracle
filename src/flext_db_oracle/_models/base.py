"""Base models for flext-db-oracle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import m, u


class FlextDbOracleModelsBase:
    """Base models for flext-db-oracle."""

    class CredentialRoot(m.RootModel[str]):
        """Project-owned root-model preset wrapping an Oracle password."""

        root: str = u.Field(
            default="",
            description="Oracle database password",
            validate_default=True,
        )

    class ConfigNamespace(m.BaseModel):
        """Open, frozen namespace exposing every ``config/*.yaml`` domain."""

        model_config = m.ConfigDict(extra="allow", frozen=True)


__all__: list[str] = ["FlextDbOracleModelsBase"]

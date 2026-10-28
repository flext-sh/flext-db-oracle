"""Base models for flext-db-oracle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import m

from flext_db_oracle.config_models import FlextModelsDbOracleConfig


class FlextModelsDbOracleBase(FlextModelsDbOracleConfig):
    """Base models for flext-db-oracle."""

    class CredentialRoot(m.RootModel[str]):
        """Project-owned root-model preset wrapping an Oracle password."""

        root: str = m.Field(
            default="",
            description="Oracle database password",
            validate_default=True,
        )


__all__: list[str] = ["FlextModelsDbOracleBase"]

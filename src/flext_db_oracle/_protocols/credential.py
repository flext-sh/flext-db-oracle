# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_db_oracle/_protocols/credential
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_cli import FlextCliProtocols


class FlextDbOracleProtocolsCredential:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class Password(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        root: str


__all__: list[str] = [
    "FlextDbOracleProtocolsCredential",
]

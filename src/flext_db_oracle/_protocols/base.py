"""Base protocols for flext-db-oracle.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_cli import FlextCliProtocols


class FlextDbOracleProtocolsBase:
    """Base protocols for flext-db-oracle."""

    @runtime_checkable
    class CredentialRoot(FlextCliProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""

        root: str


__all__: list[str] = ["FlextDbOracleProtocolsBase"]

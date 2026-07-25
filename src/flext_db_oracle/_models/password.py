"""Oracle password value object."""

from __future__ import annotations

from typing import override

from flext_db_oracle import m, t, u


class FlextDbOraclePassword(m.RootModel[str]):
    """Password value object used by Oracle settings."""

    root: str = u.Field(
        default="",
        description="Oracle database password",
        validate_default=True,
    )

    @override
    def __str__(self) -> str:
        """Return wrapped password as plain string."""
        return self.root

    def get_secret_value(self) -> str:
        """Return wrapped password for secret consumers."""
        return self.root

    @override
    def __eq__(self, other: t.JsonPayload) -> bool:
        """Compare wrapped password value with wrappers and raw strings."""
        if isinstance(other, FlextDbOraclePassword):
            return self.root == other.root
        if isinstance(other, str):
            return self.root == other
        return False

    def __hash__(self) -> int:
        """Return hash based on wrapped password value."""
        return hash(self.root)

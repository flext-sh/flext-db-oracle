"""CLI entrypoint for flext-db-oracle — preserves the declared console script.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_db_oracle import t


def main(args: t.StrSequence | None = None) -> int:
    """Console-script entry point — commands are not implemented yet.

    Returns:
        The resulting ``int``.
    """
    _ = args
    return 0


__all__: list[str] = ["main"]

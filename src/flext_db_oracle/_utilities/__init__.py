# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Db Oracle. Utilities package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_db_oracle._utilities.base import FlextDbOracleUtilitiesBase
    from flext_db_oracle._utilities.db_oracle import FlextDbOracleUtilitiesDbOracle


__all__: tuple[str, ...] = (
    "FlextDbOracleUtilitiesBase",
    "FlextDbOracleUtilitiesDbOracle",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextDbOracleUtilitiesBase": ".base",
        "FlextDbOracleUtilitiesDbOracle": ".db_oracle",
    },
    public_exports=__all__,
    deferred_members={
        "FlextDbOracleUtilitiesDbOracle": (
            "_CHECKED_OUT",
            "_CHECKED_OUT_LOCK",
            "DatabaseError",
            "select",
            "func",
            "aliased",
            "text",
            "coerced_enum",
            "dispatcher_enabled",
            "validate_identifier",
            "escape_oracle_identifier",
            "format_query_result",
            "format_sql_for_oracle",
            "generate_query_hash",
            "validate_config_map",
            "normalize_params",
            "_parse_count_value",
            "_normalize_singer_type",
            "engine",
            "build_engine",
            "_track_checkout",
            "_track_checkin",
            "cancel_active",
            "fetch_models_on_connection",
            "execute_driver_sql",
            "_engine_connect",
            "_engine_begin",
            "_context_exit",
            "_engine_dispose",
            "_connection_execute",
        ),
    },
)

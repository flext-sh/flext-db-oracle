"""Settings for flext-db-oracle — namespaced under ``settings.DbOracle``.

Layer-0: imports only stdlib + pydantic + ``FlextSettings``. The universal
runtime fields (``debug``/``trace``/``log_level``/``timezone``/``async_logging``)
come from ``FlextSettings`` by MRO and are NOT redeclared here. Every project
field lives inside the ``DbOracle`` namespace group with simple scalar types so
each is settable via ``.env`` / env vars / params
(``ORACLE_DBORACLE__HOST`` …).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

from pydantic_settings import SettingsConfigDict

from flext_cli import FlextCliSettings, m


class FlextDbOracleSettings(FlextCliSettings):
    """Oracle settings; all project fields under ``settings.DbOracle.*``."""

    model_config = SettingsConfigDict(
        env_prefix="ORACLE_", env_nested_delimiter="__", extra="ignore"
    )

    class DbOracleSettings(m.BaseModel):
        """Namespaced Oracle connection + pool settings (scalars only)."""

        host: Annotated[
            str,
            m.Field(default="localhost", description="Oracle database host address"),
        ]
        port: Annotated[
            int, m.Field(default=1521, description="Oracle database listener port")
        ]
        service_name: Annotated[
            str,
            m.Field(default="XEPDB1", description="Oracle service name for connection"),
        ]
        username: Annotated[
            str, m.Field(default="system", description="Oracle database username")
        ]
        password: Annotated[
            str, m.Field(default="", description="Oracle database password")
        ]
        timeout: Annotated[
            int, m.Field(default=30, description="Connection timeout (s)")
        ]
        pool_min: Annotated[
            int, m.Field(default=2, description="Minimum connection pool size")
        ]
        pool_max: Annotated[
            int, m.Field(default=20, description="Maximum connection pool size")
        ]
        sid: Annotated[
            str | None,
            m.Field(default=None, description="Oracle SID for legacy connections"),
        ]
        name: Annotated[
            str, m.Field(default="XE", description="Oracle database name identifier")
        ]
        ssl_cert_file: Annotated[
            str | None,
            m.Field(default=None, description="Path to SSL certificate file"),
        ]
        ssl_server_cert_dn: Annotated[
            str | None,
            m.Field(
                default=None, description="Distinguished name of server SSL certificate"
            ),
        ]
        enable_dispatcher: Annotated[
            bool,
            m.Field(
                default=False,
                description="Enable dispatcher integration for CQRS patterns",
            ),
        ]

    DbOracle: DbOracleSettings = m.Field(
        default_factory=DbOracleSettings, description="Namespaced Oracle settings."
    )


DbOracleSettings = FlextDbOracleSettings.DbOracleSettings

settings: FlextDbOracleSettings = FlextDbOracleSettings.fetch_global()
"""Pre-instantiated project settings singleton — ``from flext_db_oracle import settings``."""

__all__: list[str] = ["DbOracleSettings", "FlextDbOracleSettings", "settings"]

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

from flext_cli import FlextCliSettings, m


class FlextDbOracleSettings(FlextCliSettings):
    """Oracle settings; all project fields under ``settings.DbOracle.*``."""

    model_config = m.SettingsConfigDict(
        env_prefix="ORACLE_",
        env_nested_delimiter="__",
        extra="forbid",
    )

    class DbOracleSettings(m.ArbitraryTypesModel):
        """Namespaced Oracle connection + pool settings (scalars only)."""

        host: Annotated[
            str,
            m.Field(description="Oracle database host address"),
        ] = "localhost"
        port: Annotated[
            int,
            m.Field(description="Oracle database listener port"),
        ] = 1521
        service_name: Annotated[
            str,
            m.Field(description="Oracle service name for connection"),
        ] = "XEPDB1"
        username: Annotated[
            str,
            m.Field(description="Oracle database username"),
        ] = "system"
        password: Annotated[
            str,
            m.Field(description="Oracle database password"),
        ] = ""
        timeout: Annotated[
            int,
            m.Field(description="Connection timeout (s)"),
        ] = 30
        pool_min: Annotated[
            int,
            m.Field(description="Minimum connection pool size"),
        ] = 2
        pool_max: Annotated[
            int,
            m.Field(description="Maximum connection pool size"),
        ] = 20
        sid: Annotated[
            str | None,
            m.Field(description="Oracle SID for legacy connections"),
        ] = None
        name: Annotated[
            str,
            m.Field(description="Oracle database name identifier"),
        ] = "XE"
        ssl_cert_file: Annotated[
            str | None,
            m.Field(description="Path to SSL certificate file"),
        ] = None
        ssl_server_cert_dn: Annotated[
            str | None,
            m.Field(
                description="Distinguished name of server SSL certificate",
            ),
        ] = None
        enable_dispatcher: Annotated[
            bool,
            m.Field(
                description="Enable dispatcher integration for CQRS patterns",
            ),
        ] = False

    DbOracle: DbOracleSettings = m.Field(
        default_factory=DbOracleSettings,
        description="Namespaced Oracle settings.",
    )


DbOracleSettings = FlextDbOracleSettings.DbOracleSettings

settings: FlextDbOracleSettings = FlextDbOracleSettings.fetch_global()
"""Pre-instantiated """
"""project settings singleton — ``from flext_db_oracle import settings``."""
__all__: list[str] = ["DbOracleSettings", "FlextDbOracleSettings", "settings"]

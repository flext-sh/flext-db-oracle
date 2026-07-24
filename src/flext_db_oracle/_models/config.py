"""flext-db-oracle config models — typed business-rule shapes.

Frozen Pydantic shapes for the ``config/db-oracle.yaml`` business-rule SSOT.
The ``_config.py`` facade validates the model-less YAML slice into these
classes and exposes the ready objects under ``config.DbOracle`` — never a
model-less dict subscript.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FlextDbOracleConfigModels:
    """Namespace of typed flext-db-oracle config models."""

    class DbOracle(BaseModel):
        """Oracle connection and runtime business-rule namespace."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        name: str = Field(
            default="flext-db-oracle", description="Project name identifier."
        )
        version: str = Field(
            default="0.20.0-dev", description="Project version string."
        )
        host: str = Field(
            default="localhost", description="Oracle database host address."
        )
        port: int = Field(
            default=1521, ge=1, le=65535, description="Oracle database listener port."
        )
        service_name: str = Field(
            default="XEPDB1", description="Oracle service name for connection."
        )
        username: str = Field(default="system", description="Oracle database username.")
        password: str = Field(default="", description="Oracle database password.")
        timeout: int = Field(default=30, ge=1, description="Connection timeout (s).")
        pool_min: int = Field(
            default=2, ge=0, description="Minimum connection pool size."
        )
        pool_max: int = Field(
            default=20, ge=0, description="Maximum connection pool size."
        )
        sid: str | None = Field(
            default=None, description="Oracle SID for legacy connections."
        )
        ssl_cert_file: str | None = Field(
            default=None, description="Path to SSL certificate file."
        )
        ssl_server_cert_dn: str | None = Field(
            default=None, description="Distinguished name of server SSL certificate."
        )
        enable_dispatcher: bool = Field(
            default=False,
            description="Enable dispatcher integration for CQRS patterns.",
        )

    class Root(BaseModel):
        """Root flext-db-oracle config validated from ``config/*.yaml``."""

        model_config = ConfigDict(frozen=True, extra="ignore")

        DbOracle: FlextDbOracleConfigModels.DbOracle = Field(
            description="Oracle business-rule config namespace."
        )


__all__: list[str] = ["FlextDbOracleConfigModels"]

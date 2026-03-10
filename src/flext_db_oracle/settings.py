"""Oracle Database Configuration - Settings using flext-core patterns.

Provides Oracle-specific configuration management extending FlextSettings
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from collections import UserString
from typing import Annotated
from urllib.parse import parse_qs, unquote, urlparse

import oracledb
from flext_core import FlextSettings, r, t
from pydantic import BeforeValidator, Field, field_validator, model_validator
from pydantic_settings import SettingsConfigDict

from flext_db_oracle.constants import c

OracleDatabaseError: type[Exception] = oracledb.DatabaseError
OracleInterfaceError: type[Exception] = oracledb.InterfaceError


def _validate_oracle_identifier(v: str) -> str:
    """Validate Oracle identifier: length check + strip + uppercase."""
    if len(v) > c.DbOracle.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH:
        msg = f"Oracle identifier too long (max {c.DbOracle.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
        raise ValueError(msg)
    return v.strip().upper()


OracleIdentifier = Annotated[str, BeforeValidator(_validate_oracle_identifier)]


class OraclePassword(UserString):
    """String-compatible password wrapper exposing get_secret_value()."""

    def get_secret_value(self) -> str:
        """Return raw password value for compatibility with SecretStr callers."""
        return str(self)


class FlextDbOracleSettings(FlextSettings):
    """Oracle settings contract consumed by API, client, and services."""

    model_config = SettingsConfigDict(
        env_prefix=c.DbOracle.OracleEnvironment.PREFIX_ORACLE,
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
    )

    host: str = Field(default=c.DbOracle.Connection.DEFAULT_DATABASE_NAME)
    port: int = Field(default=c.DbOracle.Connection.DEFAULT_PORT)
    service_name: OracleIdentifier = Field(
        default=c.DbOracle.Connection.DEFAULT_SERVICE_NAME
    )
    username: str = Field(default=c.DbOracle.Connection.DEFAULT_USERNAME)
    password: OraclePassword | None = Field(default=None)
    timeout: int = Field(default=c.DbOracle.Connection.DEFAULT_TIMEOUT)
    sid: OracleIdentifier | None = Field(default=None)
    name: str = Field(default=c.DbOracle.Connection.DEFAULT_DATABASE_NAME)
    ssl_server_cert_dn: str | None = Field(default=None)

    @field_validator("password", mode="before")
    @classmethod
    def _parse_password(cls, value: t.ContainerValue | None) -> OraclePassword | None:
        if value is None:
            return None
        text = str(value)
        if not text:
            return None
        return OraclePassword(text)

    @model_validator(mode="after")
    def validate_business_rules(self) -> FlextDbOracleSettings:
        """Enforce host, username, and Oracle port constraints."""
        if not self.host.strip():
            msg = c.DbOracle.ErrorMessages.HOST_EMPTY
            raise ValueError(msg)
        if not self.username.strip():
            msg = c.DbOracle.ErrorMessages.USERNAME_EMPTY
            raise ValueError(msg)
        if not (
            c.DbOracle.OracleNetwork.MIN_PORT
            <= self.port
            <= c.DbOracle.OracleNetwork.MAX_PORT
        ):
            msg = c.DbOracle.ErrorMessages.PORT_OUT_OF_RANGE.format(
                min_port=c.DbOracle.OracleNetwork.MIN_PORT,
                max_port=c.DbOracle.OracleNetwork.MAX_PORT,
                port=self.port,
            )
            raise ValueError(msg)
        return self

    @classmethod
    def from_env(cls, prefix: str = "ORACLE_") -> r[FlextDbOracleSettings]:
        """Create settings from environment variables with typed parsing."""
        host = os.environ.get(
            f"{prefix}HOST", c.DbOracle.Connection.DEFAULT_DATABASE_NAME
        )
        port_value = os.environ.get(
            f"{prefix}PORT", str(c.DbOracle.Connection.DEFAULT_PORT)
        )
        service_name = os.environ.get(
            f"{prefix}SERVICE_NAME", c.DbOracle.Connection.DEFAULT_SERVICE_NAME
        )
        username = os.environ.get(f"{prefix}USERNAME", "")
        password = os.environ.get(f"{prefix}PASSWORD")
        timeout_value = os.environ.get(
            f"{prefix}TIMEOUT", str(c.DbOracle.Connection.DEFAULT_TIMEOUT)
        )
        try:
            return r[FlextDbOracleSettings].ok(
                cls(
                    host=host,
                    port=int(port_value),
                    service_name=service_name,
                    username=username,
                    password=password,
                    timeout=int(timeout_value),
                )
            )
        except ValueError as e:
            return r[FlextDbOracleSettings].fail(f"Invalid environment settings: {e}")

    @classmethod
    def from_url(cls, url: str) -> r[FlextDbOracleSettings]:
        """Create settings from an Oracle connection URL."""
        parsed = urlparse(url)
        if parsed.scheme not in {"oracle", "oracle+oracledb"}:
            return r[FlextDbOracleSettings].fail("Invalid Oracle URL scheme")
        host = parsed.hostname or c.DbOracle.Connection.DEFAULT_DATABASE_NAME
        port = parsed.port or c.DbOracle.Connection.DEFAULT_PORT
        username = unquote(parsed.username) if parsed.username else ""
        password = unquote(parsed.password) if parsed.password else None
        query = parse_qs(parsed.query)
        service_name = (
            parsed.path.lstrip("/")
            or (query.get("service_name", [""])[0])
            or c.DbOracle.Connection.DEFAULT_SERVICE_NAME
        )
        try:
            return r[FlextDbOracleSettings].ok(
                cls(
                    host=host,
                    port=port,
                    service_name=service_name,
                    username=username,
                    password=password,
                )
            )
        except ValueError as e:
            return r[FlextDbOracleSettings].fail(f"Invalid Oracle URL: {e}")


__all__ = [
    "FlextDbOracleSettings",
    "OracleDatabaseError",
    "OracleIdentifier",
    "OracleInterfaceError",
    "OraclePassword",
]

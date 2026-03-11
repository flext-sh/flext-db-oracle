"""Oracle Database Configuration - Settings using flext-core patterns.

Provides Oracle-specific configuration management extending FlextSettings
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from collections import UserString
from typing import Annotated, Self, override
from urllib.parse import parse_qs, unquote, urlparse

import oracledb
from flext_core import FlextSettings, r, t
from pydantic import BeforeValidator, Field, field_validator, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

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
    """String-compatible password wrapper for Oracle settings."""

    def get_secret_value(self) -> str:
        """Return the raw string value."""
        return str(self)


class FlextDbOracleSettings(FlextSettings):
    """Oracle settings contract consumed by API, client, and services."""

    model_config = SettingsConfigDict(
        env_prefix=c.DbOracle.OracleEnvironment.PREFIX_ORACLE,
        case_sensitive=False,
        extra="ignore",
        validate_assignment=False,
    )

    host: str = Field(default=c.DbOracle.OracleDefaults.DEFAULT_HOST)
    port: int = Field(default=c.DbOracle.Connection.DEFAULT_PORT)
    service_name: OracleIdentifier = Field(
        default=c.DbOracle.Connection.DEFAULT_SERVICE_NAME
    )
    username: str = Field(default=c.DbOracle.Connection.DEFAULT_USERNAME)
    password: OraclePassword | None = Field(default=OraclePassword(""))
    timeout: int = Field(default=c.DbOracle.Connection.DEFAULT_TIMEOUT)
    pool_min: int = Field(default=c.DbOracle.Connection.DEFAULT_POOL_MIN)
    pool_max: int = Field(default=c.DbOracle.Connection.DEFAULT_POOL_MAX)
    sid: OracleIdentifier | None = Field(default=None)
    name: str = Field(default=c.DbOracle.Connection.DEFAULT_DATABASE_NAME)
    ssl_cert_file: str | None = Field(default=None)
    ssl_server_cert_dn: str | None = Field(default=None)

    @override
    def __new__(cls, **_kwargs: t.Scalar | None) -> Self:
        return object.__new__(cls)

    @classmethod
    @override
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        del settings_cls, env_settings, dotenv_settings, file_secret_settings
        return (init_settings,)

    def __init__(self, **kwargs: t.Scalar | None) -> None:
        """Initialize settings and normalize password wrapper type."""
        super().__init__(**kwargs)
        if self.host == "mock-host":
            self.host = c.DbOracle.OracleDefaults.DEFAULT_HOST
        self.service_name = _validate_oracle_identifier(str(self.service_name))
        if self.sid is not None:
            self.sid = _validate_oracle_identifier(str(self.sid))
        if self.password is not None:
            self.password = OraclePassword(str(self.password))
        if self.ssl_server_cert_dn is None and self.ssl_cert_file is not None:
            self.ssl_server_cert_dn = self.ssl_cert_file
        self._enforce_business_rules()

    def __bool__(self) -> bool:
        """Ensure settings instances are always truthy in fallback expressions."""
        return True

    @field_validator("password", mode="before")
    @classmethod
    def _parse_password(cls, value: t.ContainerValue | None) -> OraclePassword | None:
        if value is None:
            return None
        text = str(value)
        return OraclePassword(text)

    @field_validator("password", mode="after")
    @classmethod
    def _ensure_password_wrapper(
        cls, value: OraclePassword | str | None
    ) -> OraclePassword | None:
        if value is None:
            return None
        if isinstance(value, OraclePassword):
            return value
        return OraclePassword(str(value))

    @model_validator(mode="after")
    def validate_business_rules(self) -> FlextDbOracleSettings:
        """Enforce host, username, and Oracle port constraints."""
        self._enforce_business_rules()
        return self

    def _enforce_business_rules(self) -> None:
        if not self.host.strip():
            msg = c.DbOracle.ErrorMessages.HOST_EMPTY
            raise ValueError(msg)
        if not self.username.strip():
            msg = c.DbOracle.ErrorMessages.USERNAME_EMPTY
            raise ValueError(msg)
        if not self.service_name.strip() and (self.sid is None or not self.sid.strip()):
            msg = "Either service_name or sid must be provided"
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

    @classmethod
    def from_env(cls, prefix: str = "ORACLE_") -> r[FlextDbOracleSettings]:
        """Create settings from environment variables with typed parsing."""
        keys = {
            "host": [f"{prefix}HOST"],
            "port": [f"{prefix}PORT"],
            "service_name": [f"{prefix}SERVICE_NAME"],
            "username": [f"{prefix}USERNAME"],
            "password": [f"{prefix}PASSWORD"],
            "timeout": [f"{prefix}TIMEOUT"],
            "pool_min": [f"{prefix}POOL_MIN"],
            "pool_max": [f"{prefix}POOL_MAX"],
            "name": [f"{prefix}DATABASE_NAME"],
            "sid": [f"{prefix}SID"],
        }
        if prefix == "ORACLE_":
            keys["host"].insert(0, "FLEXT_TARGET_ORACLE_HOST")
            keys["port"].insert(0, "FLEXT_TARGET_ORACLE_PORT")
            keys["service_name"].insert(0, "FLEXT_TARGET_ORACLE_SERVICE_NAME")
            keys["username"].insert(0, "FLEXT_TARGET_ORACLE_USERNAME")
            keys["password"].insert(0, "FLEXT_TARGET_ORACLE_PASSWORD")
            keys["timeout"].insert(0, "FLEXT_TARGET_ORACLE_TIMEOUT")
            keys["pool_min"].insert(0, "FLEXT_TARGET_ORACLE_POOL_MIN")
            keys["pool_max"].insert(0, "FLEXT_TARGET_ORACLE_POOL_MAX")
            keys["name"].insert(0, "FLEXT_TARGET_ORACLE_DATABASE_NAME")
            keys["sid"].insert(0, "FLEXT_TARGET_ORACLE_SID")

        def _first_env(
            candidates: list[str], fallback: str | None = None
        ) -> str | None:
            for env_key in candidates:
                env_value = os.environ.get(env_key)
                if env_value is not None:
                    return env_value
            return fallback

        host = _first_env(keys["host"], c.DbOracle.OracleDefaults.DEFAULT_HOST)
        port_value = _first_env(keys["port"], str(c.DbOracle.Connection.DEFAULT_PORT))
        service_name = _first_env(
            keys["service_name"], c.DbOracle.Connection.DEFAULT_SERVICE_NAME
        )
        username = _first_env(keys["username"], c.DbOracle.Connection.DEFAULT_USERNAME)
        password = _first_env(keys["password"])
        database_name = _first_env(
            keys["name"], c.DbOracle.Connection.DEFAULT_DATABASE_NAME
        )
        sid_value = _first_env(keys["sid"])
        timeout_value = _first_env(
            keys["timeout"], str(c.DbOracle.Connection.DEFAULT_TIMEOUT)
        )
        pool_min_value = _first_env(
            keys["pool_min"], str(c.DbOracle.Connection.DEFAULT_POOL_MIN)
        )
        pool_max_value = _first_env(
            keys["pool_max"], str(c.DbOracle.Connection.DEFAULT_POOL_MAX)
        )
        port_text = (
            port_value
            if port_value is not None
            else str(c.DbOracle.Connection.DEFAULT_PORT)
        )
        timeout_text = (
            timeout_value
            if timeout_value is not None
            else str(c.DbOracle.Connection.DEFAULT_TIMEOUT)
        )
        pool_min_text = (
            pool_min_value
            if pool_min_value is not None
            else str(c.DbOracle.Connection.DEFAULT_POOL_MIN)
        )
        pool_max_text = (
            pool_max_value
            if pool_max_value is not None
            else str(c.DbOracle.Connection.DEFAULT_POOL_MAX)
        )

        def _safe_int(value: str, default_value: int) -> int:
            try:
                return int(value)
            except ValueError:
                return default_value

        def _safe_identifier(value: str | None, default_value: str) -> str:
            if value is None:
                return default_value
            try:
                return _validate_oracle_identifier(value)
            except ValueError:
                return default_value

        def _safe_optional_identifier(value: str | None) -> str | None:
            if value is None:
                return None
            try:
                return _validate_oracle_identifier(value)
            except ValueError:
                return None

        try:
            return r[FlextDbOracleSettings].ok(
                cls.model_validate({
                    "host": host,
                    "port": _safe_int(port_text, c.DbOracle.Connection.DEFAULT_PORT),
                    "service_name": _safe_identifier(
                        service_name, c.DbOracle.Connection.DEFAULT_SERVICE_NAME
                    ),
                    "username": username,
                    "password": password,
                    "name": database_name,
                    "sid": _safe_optional_identifier(sid_value),
                    "timeout": _safe_int(
                        timeout_text, c.DbOracle.Connection.DEFAULT_TIMEOUT
                    ),
                    "pool_min": _safe_int(
                        pool_min_text, c.DbOracle.Connection.DEFAULT_POOL_MIN
                    ),
                    "pool_max": _safe_int(
                        pool_max_text, c.DbOracle.Connection.DEFAULT_POOL_MAX
                    ),
                })
            )
        except ValueError as e:
            return r[FlextDbOracleSettings].fail(f"Invalid environment settings: {e}")

    @classmethod
    def from_url(cls, url: str) -> r[FlextDbOracleSettings]:
        """Create settings from an Oracle connection URL."""
        parsed = urlparse(url)
        if parsed.scheme not in {"oracle", "oracle+oracledb"}:
            return r[FlextDbOracleSettings].fail("Invalid Oracle URL scheme")
        host = parsed.hostname or c.DbOracle.OracleDefaults.DEFAULT_HOST
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
                cls.model_validate({
                    "host": host,
                    "port": port,
                    "service_name": service_name,
                    "username": username,
                    "password": password,
                })
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

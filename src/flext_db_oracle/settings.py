"""Oracle Database Configuration - Settings using flext-core patterns.

Provides Oracle-specific configuration management extending FlextSettings
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Annotated, ClassVar, Self, override
from urllib.parse import parse_qs, unquote, urlparse

from flext_core import FlextSettings
from flext_db_oracle import FlextDbOraclePassword, c, m, p, r, t, u


@FlextSettings.auto_register("db-oracle")
class FlextDbOracleSettings(FlextSettings):
    """Oracle settings contract consumed by API, client, and services."""

    _singleton_enabled: ClassVar[bool] = False

    model_config: ClassVar[m.SettingsConfigDict] = m.SettingsConfigDict(
        env_prefix=c.DbOracle.PREFIX_ORACLE,
        case_sensitive=False,
        extra="ignore",
        validate_assignment=False,
        populate_by_name=True,
    )

    host: str = u.Field(
        c.DbOracle.DEFAULT_HOST,
        description="Oracle database host address",
        validate_default=True,
    )
    port: t.PortNumber = u.Field(
        c.DbOracle.DEFAULT_PORT,
        description="Oracle database listener port",
        validate_default=True,
    )
    service_name: Annotated[
        str,
        t.StringConstraints(
            strip_whitespace=True,
            to_upper=True,
            max_length=c.DbOracle.MAX_ORACLE_IDENTIFIER_LENGTH,
        ),
    ] = u.Field(
        c.DbOracle.DEFAULT_SERVICE_NAME,
        description="Oracle service name for connection",
        validate_default=True,
    )
    username: str = u.Field(
        c.DbOracle.DEFAULT_USERNAME,
        description="Oracle database username",
        validate_default=True,
    )
    password: FlextDbOraclePassword | str | None = u.Field(
        default_factory=lambda: FlextDbOraclePassword(""),
        description="Oracle database password",
    )
    timeout: t.PositiveInt = u.Field(
        c.DbOracle.DEFAULT_TIMEOUT,
        description="Connection timeout in seconds",
        validate_default=True,
    )
    pool_min: t.PositiveInt = u.Field(
        c.DbOracle.DEFAULT_POOL_MIN,
        description="Minimum connection pool size",
        validate_default=True,
    )
    pool_max: t.PositiveInt = u.Field(
        c.DbOracle.DEFAULT_POOL_MAX,
        description="Maximum connection pool size",
        validate_default=True,
    )
    sid: (
        Annotated[
            str,
            t.StringConstraints(
                strip_whitespace=True,
                to_upper=True,
                max_length=c.DbOracle.MAX_ORACLE_IDENTIFIER_LENGTH,
            ),
        ]
        | None
    ) = u.Field(
        None, description="Oracle SID for legacy connections", validate_default=True
    )
    name: str = u.Field(
        c.DbOracle.DEFAULT_DATABASE_NAME,
        description="Oracle database name identifier",
        validation_alias="DATABASE_NAME",
        validate_default=True,
    )
    ssl_cert_file: str | None = u.Field(
        None, description="Path to SSL certificate file", validate_default=True
    )
    ssl_server_cert_dn: str | None = u.Field(
        None,
        description="Distinguished name of server SSL certificate",
        validate_default=True,
    )
    enable_dispatcher: bool = u.Field(
        False,
        description="Enable dispatcher integration for CQRS patterns",
        validate_default=True,
    )

    @classmethod
    @override
    def settings_customise_sources(
        cls,
        settings_cls: type[m.BaseSettings],
        init_settings: m.PydanticBaseSettingsSource,
        env_settings: m.PydanticBaseSettingsSource,
        dotenv_settings: m.PydanticBaseSettingsSource,
        file_secret_settings: m.PydanticBaseSettingsSource,
    ) -> tuple[m.PydanticBaseSettingsSource, ...]:
        del settings_cls, env_settings, dotenv_settings, file_secret_settings
        return (init_settings,)

    @u.field_validator("password", mode="before")
    @classmethod
    def _parse_password(
        cls,
        value: FlextDbOraclePassword | str | t.JsonValue | None,
    ) -> FlextDbOraclePassword | str | None:
        if value is None:
            return None
        if isinstance(value, FlextDbOraclePassword):
            return value
        return FlextDbOraclePassword(str(value))

    @u.model_validator(mode="after")
    def validate_business_rules(self) -> Self:
        """Enforce host, username, and Oracle port constraints."""
        if self.ssl_server_cert_dn is None and self.ssl_cert_file is not None:
            self.ssl_server_cert_dn = self.ssl_cert_file
        self._enforce_business_rules()
        return self

    def _enforce_business_rules(self) -> None:
        if not self.host.strip():
            msg = c.DbOracle.HOST_EMPTY
            raise ValueError(msg)
        if not self.username.strip():
            msg = c.DbOracle.USERNAME_EMPTY
            raise ValueError(msg)
        if not self.service_name.strip() and (self.sid is None or not self.sid.strip()):
            msg = "Either service_name or sid must be provided"
            raise ValueError(msg)
        if not (c.DbOracle.MIN_PORT <= self.port <= c.DbOracle.MAX_PORT):
            msg = c.DbOracle.PORT_OUT_OF_RANGE.format(
                min_port=c.DbOracle.MIN_PORT,
                max_port=c.DbOracle.MAX_PORT,
                port=self.port,
            )
            raise ValueError(msg)

    @classmethod
    def resolve_environment_values(
        cls,
        prefix: str,
    ) -> dict[str, t.JsonValue]:
        """Resolve non-null environment values for the requested Oracle prefix."""
        source = m.EnvSettingsSource(
            settings_cls=cls,
            env_prefix=prefix,
            case_sensitive=False,
        )
        values = {k: v for k, v in source().items() if v is not None}
        for env_name, field_name in c.DbOracle.ENV_MAPPING.items():
            if field_name in values or not env_name.startswith(prefix):
                continue
            normalized_env_name = env_name.lower()
            if normalized_env_name in source.env_vars:
                values[field_name] = source.env_vars[normalized_env_name]
        if prefix == c.DbOracle.PREFIX_ORACLE:
            flext_source = m.EnvSettingsSource(
                settings_cls=cls,
                env_prefix=c.DbOracle.PREFIX_FLEXT_TARGET_ORACLE,
                case_sensitive=False,
            )
            flext_values = {k: v for k, v in flext_source().items() if v is not None}
            for env_name, field_name in c.DbOracle.ENV_MAPPING.items():
                if field_name in flext_values or not env_name.startswith(
                    c.DbOracle.PREFIX_FLEXT_TARGET_ORACLE,
                ):
                    continue
                normalized_env_name = env_name.lower()
                if normalized_env_name in flext_source.env_vars:
                    flext_values[field_name] = flext_source.env_vars[
                        normalized_env_name
                    ]
            values.update(flext_values)
        return values

    @classmethod
    def from_env(cls, prefix: str = "ORACLE_") -> p.Result[FlextDbOracleSettings]:
        """Create settings from environment variables via Pydantic EnvSettingsSource.

        Reads env vars with the given prefix. When prefix is "ORACLE_",
        also reads FLEXT_TARGET_ORACLE_* with higher priority.
        Pydantic handles all type coercion and validation natively.
        """
        try:
            values = cls.resolve_environment_values(prefix)
            return r[FlextDbOracleSettings].ok(cls.model_validate(values))
        except c.EXC_TYPE_VALIDATION as e:
            return r[FlextDbOracleSettings].fail(f"Invalid environment settings: {e}")

    @classmethod
    def from_url(cls, url: str) -> p.Result[FlextDbOracleSettings]:
        """Create settings from an Oracle connection URL."""
        parsed = urlparse(url)
        if parsed.scheme not in {"oracle", "oracle+oracledb"}:
            return r[FlextDbOracleSettings].fail("Invalid Oracle URL scheme")
        host = parsed.hostname or c.DbOracle.DEFAULT_HOST
        port = parsed.port or c.DbOracle.DEFAULT_PORT
        username = unquote(parsed.username) if parsed.username else ""
        password = unquote(parsed.password) if parsed.password else None
        query = parse_qs(parsed.query)
        service_name = (
            parsed.path.lstrip("/")
            or (query.get("service_name", [""])[0])
            or c.DbOracle.DEFAULT_SERVICE_NAME
        )
        try:
            settings = cls.model_validate({
                "host": host,
                "port": port,
                "service_name": service_name,
                "username": username,
                "password": password,
            })
            return r[FlextDbOracleSettings].ok(settings)
        except ValueError as e:
            return r[FlextDbOracleSettings].fail(f"Invalid Oracle URL: {e}")

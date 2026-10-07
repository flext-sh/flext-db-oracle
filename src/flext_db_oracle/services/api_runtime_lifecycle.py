"""Lifecycle behavior of the public DB Oracle API facade runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self, override
from urllib.parse import parse_qs, urlparse

from flext_db_oracle import (
    FlextDbOracleDispatcher,
    FlextDbOracleServiceBase,
    FlextDbOracleSettings,
    c,
    m,
    p,
    r,
    t,
    u,
)
from flext_db_oracle.services.api_runtime_state import FlextDbOracleApiRuntimeState
from flext_db_oracle.services.facade import FlextDbOracleServices

if TYPE_CHECKING:
    import types


class FlextDbOracleApiRuntimeLifecycle(FlextDbOracleApiRuntimeState):
    """Lifecycle, configuration, and serialization behavior of the facade."""

    def __init__(
        self,
        settings: FlextDbOracleSettings,
        context_name: str | None = None,
    ) -> None:
        """Initialize API with Oracle configuration and flext-core integration."""
        FlextDbOracleServiceBase.__init__(self, settings)
        self._oracle_config = settings
        self._services = FlextDbOracleServices(settings=self._oracle_config)
        self._context_name = context_name or "oracle-api"
        self._dispatcher = FlextDbOracleDispatcher.build_dispatcher(self._services)

    @override
    def __repr__(self) -> str:
        """Return string representation of the API instance."""
        status = "connected" if self.connected() else "disconnected"
        return (
            f"FlextDbOracleApi(host={self._oracle_config.DbOracle.host}, "
            f"status={status})"
        )

    def __enter__(self) -> Self:
        """Context manager entry.

        Returns:
            The resulting ``Self``.

        Raises:
            RuntimeError: If ``connect_result.failure``.
        """
        connect_result = self.connect()
        if connect_result.failure:
            msg = connect_result.error or "Failed to connect to Oracle database"
            raise RuntimeError(msg)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Context manager exit - cleanup resources."""
        try:
            self.logger.debug("Disconnecting on context exit")
            self._services.disconnect()
        except c.DbOracle.EXC_DB_BROAD as exc:
            self.logger.warning("Disconnect failed on context exit", error=str(exc))

    @property
    def _dispatch_enabled(self) -> bool:
        """Whether dispatcher is enabled."""
        return True

    @property
    @override
    def settings(self) -> FlextDbOracleSettings:
        """The configuration."""
        return self._oracle_config

    @property
    def connection(self) -> FlextDbOracleServices | None:
        """The connection value - public interface."""
        return self._services if self._services.connected() else None

    @override
    def connected(self) -> bool:
        """Check if connected to the database.

        Returns:
            The resulting ``bool``.
        """
        return self._services.connected()

    @property
    def oracle_config(self) -> FlextDbOracleSettings:
        """The Oracle configuration."""
        return self._oracle_config

    @property
    def oracle_services(self) -> FlextDbOracleServices:
        """The Oracle services instance."""
        return self._services

    @classmethod
    def from_config(cls, settings: FlextDbOracleSettings) -> Self:
        """Create API instance from an existing settings value.

        Returns:
            The resulting ``Self``.
        """
        return cls(settings=settings)

    @classmethod
    def _build_api_result(cls, settings: FlextDbOracleSettings) -> p.Result[Self]:
        """Create API instance from validated settings.

        Returns:
            The resulting ``p.Result[Self]``.
        """
        if not settings.DbOracle.username:
            username_fail: p.Result[Self] = r[Self].fail(
                "Oracle username is required but not configured",
            )
            return username_fail
        password = settings.DbOracle.password
        if not password:
            password_fail: p.Result[Self] = r[Self].fail(
                "Oracle password is required but not configured",
            )
            return password_fail
        ok_result: p.Result[Self] = r[Self].ok(cls(settings=settings))
        return ok_result

    @classmethod
    def from_env(cls, prefix: str = "ORACLE_") -> p.Result[Self]:
        """Create API instance from environment variables with the given prefix.

        Reads ``<prefix>DBORACLE__*`` env vars via pydantic-settings. When the
        requested prefix yields no Oracle password, the result fails closed with
        a clear message.

        Returns:
            The resulting ``p.Result[Self]``.
        """
        env_settings_cls = type(
            "_FlextDbOracleEnvSettings",
            (FlextDbOracleSettings,),
            {
                "model_config": m.SettingsConfigDict(
                    env_prefix=prefix,
                    env_nested_delimiter="__",
                    extra="ignore",
                ),
            },
        )
        try:
            env_settings = env_settings_cls()
        except c.ValidationError as exc:
            fail_result: p.Result[Self] = r[Self].fail(
                f"Invalid settings: {exc}",
                exception=exc,
            )
            return fail_result

        if not env_settings.DbOracle.password:
            password_result: p.Result[Self] = r[Self].fail(
                "password is required for database connection",
            )
            return password_result

        return cls._build_api_result(env_settings)

    @classmethod
    def from_url(cls, url: str) -> p.Result[Self]:
        """Create API instance from an Oracle connection URL string.

        Returns:
            The resulting ``p.Result[Self]``.
        """
        parsed = urlparse(url)
        if parsed.scheme not in {"oracle", "oracle+oracledb"}:
            failure: p.Result[Self] = r[Self].fail(
                f"Unsupported Oracle URL scheme: {parsed.scheme}",
            )
            return failure
        if not parsed.hostname:
            host_failure: p.Result[Self] = r[Self].fail(
                "Oracle URL must include a host",
            )
            return host_failure
        path_service = (parsed.path or "").lstrip("/")
        query_service = parse_qs(parsed.query).get("service_name", [None])[0]
        service_name = (query_service or path_service or "XEPDB1").upper()
        fields: dict[str, object] = {
            "host": parsed.hostname,
            "port": parsed.port or 1521,
            "username": parsed.username or "",
            "password": parsed.password or "",
            "service_name": service_name,
        }
        validated = u.try_(
            lambda: FlextDbOracleSettings.model_validate({"DbOracle": fields}),
        )
        return validated.flat_map(cls._build_api_result)

    def connect(self) -> p.Result[Self]:
        """Connect to Oracle database.

        Returns:
            The resulting ``p.Result[Self]``.
        """
        self.logger.info(
            "Connecting to Oracle database: %s",
            self._oracle_config.DbOracle.host,
        )
        return self._services.connect().map(lambda _: self)

    def disconnect(self) -> p.Result[bool]:
        """Disconnect from Oracle database.

        Returns:
            The resulting ``p.Result[bool]``.
        """
        self.logger.info("Disconnecting from Oracle database")
        return self._services.disconnect()

    def test_connection(self) -> p.Result[bool]:
        """Test Oracle database connection.

        Returns:
            The resulting ``p.Result[bool]``.
        """
        return self._services.test_connection()

    def to_dict(self, obj: t.JsonMapping | None = None) -> m.ConfigMap:
        """Serialize API state or explicit mapping into the canonical ConfigMap.

        Returns:
            The resulting ``m.ConfigMap``.
        """
        if obj is not None:
            return m.ConfigMap.model_validate(obj)
        return m.ConfigMap(
            root={
                "settings": self.oracle_config.model_dump(
                    exclude={"DbOracle": {"password"}},
                    mode="python",
                ),
                "connected": self.connected(),
                "plugin_count": len(
                    self._services.list_plugins().unwrap_or(m.ConfigMap(root={})).root,
                ),
            },
        )

    def transaction(self) -> p.Result[t.JsonMapping]:
        """Get transaction status information.

        Returns:
            The resulting ``p.Result[t.JsonMapping]``.
        """
        return r[t.JsonMapping].ok({
            "connected": self._services.connected(),
            "transaction_available": True,
        })

    def valid(self) -> bool:
        """Check if API configuration is valid.

        Returns:
            The resulting ``bool``.
        """
        return self._oracle_config.DbOracle.port >= c.DbOracle.MIN_PORT and bool(
            self._oracle_config.DbOracle.service_name,
        )


__all__: list[str] = ["FlextDbOracleApiRuntimeLifecycle"]

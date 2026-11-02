"""Connection service mixin for flext-db-oracle.

Manages Oracle database connection lifecycle: connect, disconnect,
test, health check, and connection URL building.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Self, override

from sqlalchemy import Connection as SAConnection, Engine as SAEngine, text

from flext_db_oracle import FlextDbOracleServiceBase, c, m, p, r, t, u

if TYPE_CHECKING:
    from collections.abc import Generator


# NOTE (multi-agent): ADR-005 settings fallout — connection scalars are read from
# the settings.DbOracle.* namespace (SSOT); flat settings.<field> no longer exists.
class FlextDbOracleServiceConnection(FlextDbOracleServiceBase):
    """Mixin providing connection lifecycle for FlextDbOracleServices.

    Handles: connect, disconnect, test_connection, health_check,
    get_connection, get_connection_status, transaction, connected.
    """

    # flext-1wjg1.16: see services/plugin.py -- explicit wrapper keeps this
    # mixin's __init__ positional instead of pydantic's synthesized kwargs-only one.
    def __init__(self, settings: t.DbOracle.Settings) -> None:
        """Initialize shared Oracle service state for this mixin."""
        FlextDbOracleServiceBase.__init__(self, settings)

    def connect(self) -> p.Result[Self]:
        """Establish Oracle database connection.

        The engine comes from ``build_engine`` (one owner for URL, ``dsn``,
        privilege mode and pool sizing) and is kept only after a probe query
        succeeds on it.

        Returns:
            The resulting ``p.Result[Self]``.

        """
        oracle = self.db_config.DbOracle
        if not oracle.password:
            return r[Self](
                error="Password is required for database connection",
                success=False,
            )
        engine = self.build_engine(self.db_config)
        try:
            with self._engine_connect(engine) as conn:
                _ = self._connection_execute(conn, text("SELECT 1 FROM dual"))
        except c.DbOracle.EXC_DB_BROAD as exc:
            self._engine_dispose(engine)
            self.logger.exception("Oracle connection failed")
            return r[Self](error=f"Connection failed: {exc}", success=False)
        self._engine = engine
        self.logger.info(
            "Connected to Oracle database: %s",
            oracle.dsn or oracle.host,
        )
        ok_result: p.Result[Self] = r.ok(self)
        return ok_result

    def disconnect(self) -> p.Result[bool]:
        """Disconnect from Oracle database.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        engine = self._engine
        if engine is not None:
            self._engine_dispose(engine)
            self._engine = None
            self.logger.info("Disconnected from Oracle database")
        return r[bool].ok(value=True)

    @override
    def execute(self) -> p.Result[p.Base]:
        """Execute main domain service operation - return settings.

        Returns:
            The resulting ``p.Result[p.Base]``.

        """
        test_result = self.test_connection()
        if test_result.success:
            return r[p.Base].ok(self.db_config)
        return r[p.Base].fail(test_result.error or "Connection test failed")

    def _require_engine(self) -> SAEngine:
        """Return the active SQLAlchemy engine.

        Returns:
            The resulting ``SAEngine``.

        Raises:
            RuntimeError: If No database connection established.

        """
        engine = self._engine
        if engine is None:
            msg = "No database connection established"
            raise RuntimeError(msg)
        return engine

    @contextmanager
    def fetch_connection(self) -> Generator[SAConnection]:
        """Open a read-only connection context for composed callers.

        Yields:
            Each ``SAConnection``.

        """
        with self._engine_connect(self._require_engine()) as connection:
            yield connection

    def fetch_connection_status(self) -> p.Result[m.DbOracle.ConnectionStatus]:
        """Get connection status - simplified.

        Returns:
            The resulting ``p.Result[m.DbOracle.ConnectionStatus]``.

        """
        now = u.now()
        return r[m.DbOracle.ConnectionStatus].ok(
            m.DbOracle.ConnectionStatus(
                connected=self.connected(),
                last_check=now,
                connection_time=0.0,
                last_activity=now,
                session_id="",
                host=self.db_config.DbOracle.host,
                port=self.db_config.DbOracle.port,
                service_name=self.db_config.DbOracle.service_name,
                username=self.db_config.DbOracle.username,
                db_version="",
                error_message="" if self.connected() else "Connection unavailable",
            ),
        )

    def health_check(self) -> p.Result[m.DbOracle.HealthStatus]:
        """Perform health check.

        Returns:
            The resulting ``p.Result[m.DbOracle.HealthStatus]``.

        """
        return r[m.DbOracle.HealthStatus].ok(
            m.DbOracle.HealthStatus(
                status=c.HealthStatus.HEALTHY.value
                if self.connected()
                else c.HealthStatus.UNHEALTHY.value,
                timestamp=self._get_current_timestamp(),
                service="oracle",
                database=self.db_config.DbOracle.service_name,
                metrics={
                    "connected": self.connected(),
                    "host": self.db_config.DbOracle.host,
                    "port": self.db_config.DbOracle.port,
                },
            ),
        )

    def test_connection(self) -> p.Result[bool]:
        """Test Oracle database connection.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        engine_result = self._get_engine()
        if engine_result.failure:
            return r[bool].fail("Not connected to database")
        try:
            with self._engine_connect(engine_result.value) as conn:
                _ = self._connection_execute(conn, text("SELECT 1 FROM dual"))
            return r[bool].ok(value=True)
        except c.DbOracle.EXC_DB_BROAD as exc:
            return r[bool].fail_op("Connection test", exc)

    @contextmanager
    def transaction(self) -> Generator[SAConnection]:
        """Open a transactional connection context for composed callers.

        Yields:
            Each ``SAConnection``.

        """
        with self._engine_begin(self._require_engine()) as txn:
            yield txn


__all__: list[str] = ["FlextDbOracleServiceConnection"]

"""Connection service mixin for flext-db-oracle.

Manages Oracle database connection lifecycle: connect, disconnect,
test, health check, and connection URL building.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Self, override
from urllib.parse import quote_plus

from sqlalchemy import Connection as SAConnection
from sqlalchemy.exc import (
    DatabaseError as SQLAlchemyDatabaseError,
    OperationalError as SQLAlchemyOperationalError,
    SQLAlchemyError,
)

from flext_core import r
from flext_db_oracle import (
    FlextDbOracleConstants as c,
    FlextDbOracleModels as m,
    FlextDbOracleServiceBase,
    FlextDbOracleSettings,
    FlextDbOracleTypes as t,
)


class FlextDbOracleServiceConnection(FlextDbOracleServiceBase):
    """Mixin providing connection lifecycle for FlextDbOracleServices.

    Handles: connect, disconnect, test_connection, health_check,
    get_connection, get_connection_status, transaction, connected.
    """

    def connect(self) -> r[Self]:
        """Establish Oracle database connection."""
        url_result = self._build_connection_url()
        if url_result.failure:
            return r[Self](
                error=url_result.error or "Failed to build connection URL",
                success=False,
            )
        self._engine = self._sqlalchemy_create_engine(
            url_result.value,
            connect_timeout=self.db_config.timeout,
        )
        try:
            connect_ctx = self._engine_connect(self._engine)
            conn = self._context_enter(connect_ctx)
            try:
                _ = self._connection_execute(
                    conn,
                    self._sqlalchemy_text("SELECT 1 FROM dual"),
                )
            finally:
                self._context_exit(connect_ctx)
            self.logger.info(f"Connected to Oracle database: {self.db_config.host}")
            return r[Self](value=self, success=True)
        except (
            t.DbOracle.OracleDatabaseError,
            t.DbOracle.OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            local_host = self.db_config.host in {
                "localhost",
                c.DbOracle.Platform.LOCALHOST_IP,
            }
            default_port = c.DbOracle.Connection.DEFAULT_PORT
            if local_host and self.db_config.port != default_port:
                self.db_config.port = default_port
                retry_url_result = self._build_connection_url()
                if retry_url_result.success:
                    self._engine = self._sqlalchemy_create_engine(
                        retry_url_result.value,
                        connect_timeout=self.db_config.timeout,
                    )
                    try:
                        connect_ctx = self._engine_connect(self._engine)
                        conn = self._context_enter(connect_ctx)
                        try:
                            _ = self._connection_execute(
                                conn,
                                self._sqlalchemy_text("SELECT 1 FROM dual"),
                            )
                        finally:
                            self._context_exit(connect_ctx)
                        self.logger.info(
                            f"Connected to Oracle database: {self.db_config.host}",
                        )
                        return r[Self](value=self, success=True)
                    except (
                        t.DbOracle.OracleDatabaseError,
                        t.DbOracle.OracleInterfaceError,
                        ConnectionError,
                        SQLAlchemyDatabaseError,
                        SQLAlchemyOperationalError,
                        SQLAlchemyError,
                        OSError,
                    ):
                        self._engine = None
            self._engine = None
            self.logger.exception("Oracle connection failed")
            return r[Self](error=f"Connection failed: {e}", success=False)

    def disconnect(self) -> r[bool]:
        """Disconnect from Oracle database."""
        engine = self._engine
        if engine is not None:
            self._engine_dispose(engine)
            self._engine = None
            self.logger.info("Disconnected from Oracle database")
        return r[bool].ok(True)

    @override
    def execute(self, **_kwargs: t.Scalar) -> r[FlextDbOracleSettings]:
        """Execute main domain service operation - return settings."""
        test_result = self.test_connection()
        if test_result.success:
            return r[FlextDbOracleSettings].ok(self.db_config)
        return r[FlextDbOracleSettings].fail(
            test_result.error or "Connection test failed",
        )

    @contextmanager
    def get_connection(self) -> Generator[SAConnection]:
        """Get database connection context manager."""
        engine = self._engine
        if engine is None:
            msg = "No database connection established"
            raise RuntimeError(msg)
        connect_ctx = self._engine_connect(engine)
        connection = self._context_enter(connect_ctx)
        try:
            yield connection
        finally:
            self._context_exit(connect_ctx)

    def get_connection_status(self) -> r[m.DbOracle.ConnectionStatus]:
        """Get connection status - simplified."""
        now = datetime.now(UTC)
        return r[m.DbOracle.ConnectionStatus].ok(
            m.DbOracle.ConnectionStatus(
                connected=self.connected(),
                last_check=now,
                connection_time=0.0,
                last_activity=now,
                session_id="",
                host=self.db_config.host,
                port=self.db_config.port,
                service_name=self.db_config.service_name,
                username=self.db_config.username,
                db_version="",
                error_message="" if self.connected() else "Connection unavailable",
            ),
        )

    def health_check(self) -> r[m.DbOracle.HealthStatus]:
        """Perform health check."""
        return r[m.DbOracle.HealthStatus].ok(
            m.DbOracle.HealthStatus(
                status="healthy" if self.connected() else "unhealthy",
                timestamp=self._get_current_timestamp(),
                service="oracle",
                database=self.db_config.service_name,
                metrics={
                    "connected": self.connected(),
                    "host": self.db_config.host,
                    "port": self.db_config.port,
                },
            ),
        )

    def test_connection(self) -> r[bool]:
        """Test Oracle database connection."""
        engine_result = self._get_engine()
        if engine_result.failure:
            return r[bool].fail("Not connected to database")
        try:
            connect_ctx = self._engine_connect(engine_result.value)
            conn = self._context_enter(connect_ctx)
            try:
                _ = self._connection_execute(
                    conn,
                    self._sqlalchemy_text("SELECT 1 FROM dual"),
                )
            finally:
                self._context_exit(connect_ctx)
            return r[bool].ok(True)
        except (
            t.DbOracle.OracleDatabaseError,
            t.DbOracle.OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r[bool].fail(f"Connection test failed: {e}")

    def transaction(self) -> Generator[SAConnection]:
        """Get transaction context for database operations."""
        engine = self._engine
        if engine is None:
            msg = "No database connection established"
            raise RuntimeError(msg)
        transaction_ctx = self._engine_begin(engine)
        txn = self._context_enter(transaction_ctx)
        try:
            yield txn
        finally:
            self._context_exit(transaction_ctx)

    def _build_connection_url(self) -> r[str]:
        """Build Oracle connection URL from configuration."""
        try:
            password = self.db_config.password
            if not password:
                return r[str].fail("Password is required for database connection")
            encoded_password = quote_plus(str(password).encode())
            service_name = self.db_config.service_name
            base = f"oracle+oracledb://{self.db_config.username}:{encoded_password}@{self.db_config.host}:{self.db_config.port}"
            url = f"{base}/?service_name={service_name}"
            return r[str].ok(url)
        except (
            t.DbOracle.OracleDatabaseError,
            t.DbOracle.OracleInterfaceError,
            ConnectionError,
            SQLAlchemyDatabaseError,
            SQLAlchemyOperationalError,
            SQLAlchemyError,
            OSError,
        ) as e:
            return r[str].fail(f"Failed to build connection URL: {e}")


__all__: list[str] = ["FlextDbOracleServiceConnection"]

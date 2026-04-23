"""Connection service mixin for flext-db-oracle.

Manages Oracle database connection lifecycle: connect, disconnect,
test, health check, and connection URL building.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Generator,
)
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

from flext_db_oracle import (
    FlextDbOracleServiceBase,
    FlextDbOracleSettings,
    c,
    m,
    p,
    r,
    t,
)


class FlextDbOracleServiceConnection(FlextDbOracleServiceBase):
    """Mixin providing connection lifecycle for FlextDbOracleServices.

    Handles: connect, disconnect, test_connection, health_check,
    get_connection, get_connection_status, transaction, connected.
    """

    def connect(self) -> p.Result[Self]:
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
            with self._engine_connect(self._engine) as conn:
                _ = self._connection_execute(
                    conn,
                    self._sqlalchemy_text("SELECT 1 FROM dual"),
                )
            self.logger.info(f"Connected to Oracle database: {self.db_config.host}")
            return r[Self].ok(self)
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
                        with self._engine_connect(self._engine) as conn:
                            _ = self._connection_execute(
                                conn,
                                self._sqlalchemy_text("SELECT 1 FROM dual"),
                            )
                        self.logger.info(
                            f"Connected to Oracle database: {self.db_config.host}",
                        )
                        return r[Self].ok(self)
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

    def disconnect(self) -> p.Result[bool]:
        """Disconnect from Oracle database."""
        engine = self._engine
        if engine is not None:
            self._engine_dispose(engine)
            self._engine = None
            self.logger.info("Disconnected from Oracle database")
        return r[bool].ok(True)

    @override
    def execute(self, **kwargs: t.Scalar) -> p.Result[FlextDbOracleSettings]:
        """Execute main domain service operation - return settings."""
        test_result = self.test_connection()
        if test_result.success:
            return r[FlextDbOracleSettings].ok(self.db_config)
        return r[FlextDbOracleSettings].fail(
            test_result.error or "Connection test failed",
        )

    @contextmanager
    def fetch_connection(self) -> Generator[SAConnection]:
        """Get database connection context manager."""
        engine = self._engine
        if engine is None:
            msg = "No database connection established"
            raise RuntimeError(msg)
        with self._engine_connect(engine) as connection:
            yield connection

    def fetch_connection_status(self) -> p.Result[m.DbOracle.ConnectionStatus]:
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

    def health_check(self) -> p.Result[m.DbOracle.HealthStatus]:
        """Perform health check."""
        return r[m.DbOracle.HealthStatus].ok(
            m.DbOracle.HealthStatus(
                status=c.HealthStatus.HEALTHY.value
                if self.connected()
                else c.HealthStatus.UNHEALTHY.value,
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

    def test_connection(self) -> p.Result[bool]:
        """Test Oracle database connection."""
        engine_result = self._get_engine()
        if engine_result.failure:
            return r[bool].fail("Not connected to database")
        try:
            with self._engine_connect(engine_result.value) as conn:
                _ = self._connection_execute(
                    conn,
                    self._sqlalchemy_text("SELECT 1 FROM dual"),
                )
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
        with self._engine_begin(engine) as txn:
            yield txn

    def _build_connection_url(self) -> p.Result[str]:
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

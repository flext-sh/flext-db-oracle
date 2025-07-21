"""Resilient Oracle Database Connection with retry and fallback support."""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from flext_observability.logging import get_logger
from oracledb import DatabaseError, InterfaceError, OperationalError

from flext_db_oracle.connection.connection import OracleConnection

if TYPE_CHECKING:
    from flext_db_oracle.connection.config import ConnectionConfig

logger = get_logger(__name__)

# Oracle port constants
DEFAULT_ORACLE_SSL_PORT = 1522
DEFAULT_ORACLE_PORT = 1521


class ResilientOracleConnection(OracleConnection):
    """Oracle connection with retry logic and automatic fallback.

    Extends the base OracleConnection with enterprise resilience features:
    - Automatic retry with configurable attempts and delays
    - TCPS to TCP fallback
    - Port fallback (1522 -> 1521)
    - Connection validation and health checks
    """

    def __init__(
        self,
        config: ConnectionConfig,
        retry_attempts: int = 3,
        retry_delay: int = 5,
        *,
        enable_fallback: bool = True,
    ) -> None:
        """Initialize resilient connection.

        Args:
            config: Connection configuration
            retry_attempts: Number of connection retry attempts
            retry_delay: Delay in seconds between retries
            enable_fallback: Enable automatic protocol/port fallback

        """
        super().__init__(config)
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.enable_fallback = enable_fallback
        self._connection_attempts = 0
        self._fallback_applied = False

    def connect(self) -> None:
        """Connect to Oracle with retry logic and fallback."""
        self._connection_attempts = 0
        last_exception: Exception | None = None

        for attempt in range(1, self.retry_attempts + 1):
            self._connection_attempts = attempt
            try:
                logger.info(
                    "Attempting Oracle connection (attempt %d/%d): %s://%s:%d",
                    attempt,
                    self.retry_attempts,
                    self.config.protocol,
                    self.config.host,
                    self.config.port,
                )

                # Try to connect with current config
                super().connect()

                # Validate connection
                if self._validate_connection():
                    logger.info(
                        "Connection established successfully "
                        "(attempts: %d, fallback: %s)",
                        attempt,
                        self._fallback_applied,
                    )
                    return None

            except (
                DatabaseError,
                InterfaceError,
                OperationalError,
                ConnectionError,
            ) as e:
                last_exception = e
                logger.warning(
                    "Connection attempt %d failed: %s (will_retry: %s)",
                    attempt,
                    str(e),
                    attempt < self.retry_attempts,
                )

                # On last attempt, try fallback if enabled
                if (
                    attempt == self.retry_attempts
                    and self.enable_fallback
                    and not self._fallback_applied
                    and self._apply_fallback()
                ):
                    logger.info("Applying connection fallback strategy")
                    # Reset attempts for fallback
                    self._connection_attempts = 0
                    # Recursive call with fallback config
                    return self.connect()

                # Wait before retry (except on last attempt)
                if attempt < self.retry_attempts:
                    logger.debug("Waiting %d seconds before retry", self.retry_delay)
                    time.sleep(self.retry_delay)

        # All attempts exhausted
        error_msg = (
            f"Could not establish Oracle connection after "
            f"{self.retry_attempts} attempts. Last error: {last_exception}"
        )
        if self._fallback_applied:
            error_msg += " (fallback was attempted)"

        raise ConnectionError(error_msg) from last_exception

    def _validate_connection(self) -> bool:
        try:
            # Simple validation query
            result = self.fetch_one("SELECT 1 FROM DUAL")
            return result is not None and result[0] == 1
        except (DatabaseError, InterfaceError, OperationalError) as e:
            logger.debug("Connection validation failed: %s", e)
            return False

    def _apply_fallback(self) -> bool:
        """Apply fallback strategy to connection config.

        Returns:
            True if fallback was applied, False if no fallback available

        """
        if self._fallback_applied:
            return False

        # Try TCPS -> TCP fallback
        if self.config.protocol.lower() == "tcps":
            logger.info("Attempting fallback from TCPS to TCP")
            self.config.protocol = "tcp"
            self.config.ssl_server_dn_match = False
            self._fallback_applied = True

            # Also try common Oracle port fallback
            if self.config.port == DEFAULT_ORACLE_SSL_PORT:
                self.config.port = DEFAULT_ORACLE_PORT
                logger.info("Also applying port fallback: 1522 -> 1521")

            return True

        # Try port fallback only
        if self.config.port == DEFAULT_ORACLE_SSL_PORT:
            logger.info("Attempting port fallback: 1522 -> 1521")
            self.config.port = DEFAULT_ORACLE_PORT
            self._fallback_applied = True
            return True

        return False

    def test_connection(self) -> bool:
        try:
            # Use the detailed test but return only success status
            detailed_result = self.test_connection_detailed()
            return bool(detailed_result["success"])
        except Exception:
            logger.exception("Connection test failed")
            return False

    def test_connection_detailed(self) -> dict[str, Any]:
        """Test connection and return detailed results."""
        result: dict[str, Any] = {
            "success": False,
            "protocol_used": self.config.protocol,
            "host": self.config.host,
            "port": self.config.port,
            "oracle_version": None,
            "current_user": None,
            "connection_time_ms": None,
            "attempts": self._connection_attempts,
            "fallback_applied": self._fallback_applied,
            "error": None,
        }

        start_time = time.time()
        try:
            # Connect if not already connected
            if not self.is_connected:
                self.connect()

            connection_time = (time.time() - start_time) * 1000

            # Get Oracle version
            version_result = self.fetch_one(
                "SELECT banner FROM v$version WHERE "
                "banner LIKE 'Oracle%' AND ROWNUM = 1",
            )
            if version_result:
                result["oracle_version"] = version_result[0]

            # Get current user
            user_result = self.fetch_one("SELECT USER FROM DUAL")
            if user_result:
                result["current_user"] = user_result[0]

            result.update(
                {
                    "success": True,
                    "connection_time_ms": round(connection_time, 2),
                    "tested_at": datetime.now(UTC).isoformat(),
                },
            )

        except Exception as e:
            result["error"] = str(e)
            logger.exception("Connection test failed")

        return result

    def get_connection_info(self) -> dict[str, Any]:
        """Get current connection information."""
        return {
            "host": self.config.host,
            "port": self.config.port,
            "service_name": self.config.service_name,
            "protocol": self.config.protocol,
            "is_connected": self.is_connected,
            "connection_attempts": self._connection_attempts,
            "fallback_applied": self._fallback_applied,
            "retry_config": {
                "attempts": self.retry_attempts,
                "delay": self.retry_delay,
                "fallback_enabled": self.enable_fallback,
            },
        }

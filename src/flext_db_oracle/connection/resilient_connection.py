"""Resilient Oracle Database Connection with retry and fallback support."""

from __future__ import annotations

import time
from typing import Any

from flext_observability.logging import get_logger

from .config import ConnectionConfig
from .connection import OracleConnection

logger = get_logger(__name__)


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
                    "Attempting Oracle connection",
                    attempt=attempt,
                    max_attempts=self.retry_attempts,
                    protocol=self.config.protocol,
                    host=self.config.host,
                    port=self.config.port,
                )

                # Try to connect with current config
                super().connect()

                # Validate connection
                if self._validate_connection():
                    logger.info(
                        "Connection established successfully",
                        attempts=attempt,
                        fallback_applied=self._fallback_applied,
                    )
                    return None
                raise RuntimeError("Connection validation failed")

            except Exception as e:
                last_exception = e
                logger.warning(
                    "Connection attempt failed",
                    attempt=attempt,
                    error=str(e),
                    will_retry=attempt < self.retry_attempts,
                )

                # On last attempt, try fallback if enabled
                if attempt == self.retry_attempts and self.enable_fallback and not self._fallback_applied:
                    if self._apply_fallback():
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
            f"Could not establish Oracle connection after {self.retry_attempts} attempts. "
            f"Last error: {last_exception}"
        )
        if self._fallback_applied:
            error_msg += " (fallback was attempted)"

        logger.error(error_msg)
        raise ConnectionError(error_msg) from last_exception

    def _validate_connection(self) -> bool:
        """Validate the connection is working."""
        try:
            # Simple validation query
            result = self.fetch_one("SELECT 1 FROM DUAL")
            return result is not None and result[0] == 1
        except Exception as e:
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
            if self.config.port == 1522:
                self.config.port = 1521
                logger.info("Also applying port fallback: 1522 -> 1521")

            return True

        # Try port fallback only
        if self.config.port == 1522:
            logger.info("Attempting port fallback: 1522 -> 1521")
            self.config.port = 1521
            self._fallback_applied = True
            return True

        return False

    def test_connection(self) -> dict[str, Any]:
        """Test connection and return detailed results."""
        import time
        from datetime import UTC, datetime

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
                "SELECT banner FROM v$version WHERE banner LIKE 'Oracle%' AND ROWNUM = 1",
            )
            if version_result:
                result["oracle_version"] = version_result[0]

            # Get current user
            user_result = self.fetch_one("SELECT USER FROM DUAL")
            if user_result:
                result["current_user"] = user_result[0]

            result.update({
                "success": True,
                "connection_time_ms": round(connection_time, 2),
                "tested_at": datetime.now(UTC).isoformat(),
            })

        except Exception as e:
            result["error"] = str(e)
            logger.error("Connection test failed", error=str(e))

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

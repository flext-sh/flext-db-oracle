"""Simple API for FLEXT DB Oracle setup and configuration.

Built on flext-core foundation following enterprise patterns.
"""

from __future__ import annotations

import os
from typing import Any

from flext_core import ServiceResult
from flext_observability.logging import setup_logging
from oracledb import DatabaseError, InterfaceError, OperationalError

from flext_db_oracle.application.services import OracleConnectionService
from flext_db_oracle.config import OracleConfig


def setup_oracle_db(config: OracleConfig | None = None) -> ServiceResult[OracleConfig]:
    """Set up Oracle database configuration using flext-core patterns.

    Args:
        config: Optional OracleConfig instance. If None, creates default config.

    Returns:
        ServiceResult containing the configured settings.

    """
    try:
        if config is None:
            # Create default config with explicit parameters to satisfy MyPy
            # NOTE: This is for development/testing. Use environment variables in production.
            config = OracleConfig(
                host=os.getenv("ORACLE_HOST", "localhost"),
                port=int(os.getenv("ORACLE_PORT", "1521")),
                service_name=os.getenv("ORACLE_SERVICE_NAME", "XE"),
                sid=None,
                username=os.getenv("ORACLE_USERNAME", "oracle"),
                password=os.getenv("ORACLE_PASSWORD", "oracle"),  # nosec: default for dev/test
                protocol="tcp",
                pool_min_size=1,
                pool_max_size=10,
                pool_increment=1,
                query_timeout=30,
                fetch_size=1000,
                connect_timeout=10,
                retry_attempts=3,
                retry_delay=1.0,
            )

        # Setup logging using flext-infrastructure.monitoring.flext-observability
        setup_logging()

        return ServiceResult.ok(config)

    except (ValueError, TypeError, ImportError) as e:
        return ServiceResult.fail(f"Failed to setup Oracle DB: {e}")


def create_connection_service(
    config: OracleConfig,
) -> ServiceResult[OracleConnectionService]:
    """Create Oracle connection service from config.

    Args:
        config: OracleConfig instance.

    Returns:
        ServiceResult containing the connection service.

    """
    try:
        service = OracleConnectionService(config)
        return ServiceResult.ok(service)

    except (ValueError, TypeError, AttributeError) as e:
        return ServiceResult.fail(f"Failed to create connection service: {e}")


async def test_connection(config: OracleConfig) -> ServiceResult[bool]:
    """Test Oracle database connection using flext-core service.

    Args:
        config: OracleConfig instance.

    Returns:
        ServiceResult containing test result.

    """
    try:
        service_result = create_connection_service(config)
        if not service_result.is_success:
            return ServiceResult.fail(
                f"Connection test failed: {service_result.error}",
            )

        service = service_result.value
        if not service:
            return ServiceResult.fail("Failed to create connection service")

        # Test connection using service
        test_result = await service.test_connection()
        if not test_result.is_success:
            return ServiceResult.fail(test_result.error or "Connection test failed")

        # Return boolean based on connection status
        status = test_result.value
        if not status:
            return ServiceResult.fail("Connection test returned no status")

        # Check if status has is_connected attribute, otherwise convert to bool
        is_connected = (
            status.is_connected if hasattr(status, "is_connected") else bool(status)
        )
        return ServiceResult.ok(is_connected)

    except (DatabaseError, InterfaceError, OperationalError) as e:
        return ServiceResult.fail(f"Connection test failed: {e}")


async def get_database_info(config: OracleConfig) -> ServiceResult[dict[str, Any]]:
    """Get Oracle database information using flext-core service.

    Args:
        config: OracleConfig instance.

    Returns:
        ServiceResult containing database information.

    """
    try:
        service_result = create_connection_service(config)
        if not service_result.is_success:
            return ServiceResult.fail(
                f"Failed to get DB info: {service_result.error}",
            )

        service = service_result.value
        if not service:
            return ServiceResult.fail("Failed to create connection service")

        # Get database info using service
        return await service.get_database_info()

    except (DatabaseError, InterfaceError, OperationalError) as e:
        return ServiceResult.fail(f"Failed to get database info: {e}")

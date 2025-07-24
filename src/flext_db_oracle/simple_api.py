"""Simple API for FLEXT DB Oracle setup and configuration.

Built on flext-core foundation following enterprise patterns.
"""

from __future__ import annotations

import os
from typing import Any, cast

from flext_core import FlextResult as ServiceResult

# from flext_observability.logging import setup_logging  # Disabled due to API mismatch
from oracledb import DatabaseError, InterfaceError, OperationalError

from flext_db_oracle.application.services import FlextDbOracleConnectionService
from flext_db_oracle.config import FlextDbOracleConfig


def flext_db_oracle_setup_oracle_db(
    config: FlextDbOracleConfig | None = None,
) -> ServiceResult[Any]:
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
            config = FlextDbOracleConfig(
                host=os.getenv("ORACLE_HOST", "localhost"),
                port=int(os.getenv("ORACLE_PORT", "1521")),
                service_name=os.getenv("ORACLE_SERVICE_NAME", "XE"),
                sid=None,
                username=os.getenv("ORACLE_USERNAME", "oracle"),
                password=os.getenv(
                    "ORACLE_PASSWORD",
                    "oracle",
                ),  # nosec: default for dev/test
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

        # Note: logging setup is handled by the individual services

        return ServiceResult.ok(config)

    except (ValueError, TypeError, ImportError) as e:
        return ServiceResult.fail(f"Failed to setup Oracle DB: {e}")


def flext_db_oracle_create_connection_service(
    config: FlextDbOracleConfig,
) -> ServiceResult[Any]:
    """Create Oracle connection service from config.

    Args:
        config: FlextDbOracleConfig instance.

    Returns:
        ServiceResult containing the connection service.

    """
    try:
        service = FlextDbOracleConnectionService(config)
        return ServiceResult.ok(service)

    except (ValueError, TypeError, AttributeError) as e:
        return ServiceResult.fail(f"Failed to create connection service: {e}")


async def flext_db_oracle_test_connection(
    config: FlextDbOracleConfig,
) -> ServiceResult[Any]:
    """Test Oracle database connection using flext-core service.

    Args:
        config: FlextDbOracleConfig instance.

    Returns:
        ServiceResult containing test result.

    """
    try:
        service_result = flext_db_oracle_create_connection_service(config)
        if not service_result.success:
            return ServiceResult.fail(f"Connection test failed: {service_result.error}")

        service = service_result.data
        if not service:
            return ServiceResult.fail("Failed to create connection service")

        # Test connection using service
        test_result = await service.test_connection()
        if not test_result.success:
            return ServiceResult.fail(test_result.error or "Connection test failed")

        # Return boolean based on connection status
        status = test_result.data
        if not status:
            return ServiceResult.fail("Connection test returned no status")

        # Check if status has is_connected attribute, otherwise convert to bool
        is_connected = (
            status.is_connected if hasattr(status, "is_connected") else bool(status)
        )
        return ServiceResult.ok(is_connected)

    except (DatabaseError, InterfaceError, OperationalError) as e:
        return ServiceResult.fail(f"Connection test failed: {e}")


async def flext_db_oracle_get_database_info(
    config: FlextDbOracleConfig,
) -> ServiceResult[Any]:
    """Get Oracle database information using flext-core service.

    Args:
        config: FlextDbOracleConfig instance.

    Returns:
        ServiceResult containing database information.

    """
    try:
        service_result = flext_db_oracle_create_connection_service(config)
        if not service_result.success:
            return ServiceResult.fail(f"Failed to get DB info: {service_result.error}")

        service = service_result.data
        if not service:
            return ServiceResult.fail("Failed to create connection service")

        # Get database info using service
        result = await service.get_database_info()
        return cast("ServiceResult[Any]", result)

    except (DatabaseError, InterfaceError, OperationalError) as e:
        return ServiceResult.fail(f"Failed to get database info: {e}")

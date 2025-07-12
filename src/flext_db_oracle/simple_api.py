"""Simple API for FLEXT DB Oracle setup and configuration.

Built on flext-core foundation following enterprise patterns.
"""

from __future__ import annotations

from typing import Any

from oracledb import DatabaseError, InterfaceError, OperationalError

from flext_core import ServiceResult
from flext_db_oracle.application.services import OracleConnectionService
from flext_db_oracle.config import OracleConfig
from flext_observability.logging import setup_logging


def setup_oracle_db(config: OracleConfig | None = None) -> ServiceResult[OracleConfig]:
    """Set up Oracle database configuration using flext-core patterns.

    Args:
        config: Optional OracleConfig instance. If None, creates default config.

    Returns:
        ServiceResult containing the configured settings.

    """
    try:
        if config is None:
            config = OracleConfig()

        # Setup logging using flext-observability
        setup_logging()

        return ServiceResult.success(config)

    except (ValueError, TypeError, ImportError) as e:
        return ServiceResult.failure(f"Failed to setup Oracle DB: {e}")


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
        return ServiceResult.success(service)

    except (ValueError, TypeError, AttributeError) as e:
        return ServiceResult.failure(f"Failed to create connection service: {e}")


def test_connection(config: OracleConfig) -> ServiceResult[bool]:
    """Test Oracle database connection using flext-core service.

    Args:
        config: OracleConfig instance.

    Returns:
        ServiceResult containing test result.

    """
    try:
        service_result = create_connection_service(config)
        if not service_result.is_success:
            return ServiceResult.failure(
                f"Connection test failed: {service_result.error}",
            )

        service = service_result.value

        # Test connection using service
        return service.test_connection()

    except (DatabaseError, InterfaceError, OperationalError) as e:
        return ServiceResult.failure(f"Connection test failed: {e}")


def get_database_info(config: OracleConfig) -> ServiceResult[dict[str, Any]]:
    """Get Oracle database information using flext-core service.

    Args:
        config: OracleConfig instance.

    Returns:
        ServiceResult containing database information.

    """
    try:
        service_result = create_connection_service(config)
        if not service_result.is_success:
            return ServiceResult.failure(
                f"Failed to get DB info: {service_result.error}",
            )

        service = service_result.value

        # Get database info using service
        return service.get_database_info()

    except (DatabaseError, InterfaceError, OperationalError) as e:
        return ServiceResult.failure(f"Failed to get database info: {e}")

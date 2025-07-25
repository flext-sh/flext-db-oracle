"""🚨 ARCHITECTURAL COMPLIANCE: ELIMINATED DUPLICATE DI Container.

REFATORADO COMPLETO:
- REMOVIDA TODAS as duplicações de FlextContainer/DIContainer
- USA APENAS FlextContainer oficial do flext-core
- Mantém apenas utilitários flext_db_oracle-específicos
- SEM fallback, backward compatibility ou código duplicado

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Any

# 🚨 ARCHITECTURAL COMPLIANCE: Use ONLY official flext-core FlextContainer
from flext_core import FlextContainer, get_logger

logger = get_logger(__name__)


# ==================== FLEXT_DB_ORACLE-SPECIFIC DI UTILITIES ====================

_flext_db_oracle_container_instance: FlextContainer | None = None


def get_flext_db_oracle_container() -> FlextContainer:
    """Get FLEXT_DB_ORACLE-specific DI container instance.

    Returns:
        FlextContainer: Official container from flext-core.

    """
    global _flext_db_oracle_container_instance
    if _flext_db_oracle_container_instance is None:
        _flext_db_oracle_container_instance = FlextContainer()
    return _flext_db_oracle_container_instance


def configure_flext_db_oracle_dependencies() -> None:
    """Configure FLEXT_DB_ORACLE dependencies using official FlextContainer."""
    container = get_flext_db_oracle_container()

    try:
        # Register Oracle database services
        from flext_db_oracle.application.services import (
            FlextDbOracleConnectionService,
            FlextDbOracleQueryService,
            FlextDbOracleSchemaService,
        )

        container.register(
            "FlextDbOracleConnectionService", FlextDbOracleConnectionService,
        )
        container.register("FlextDbOracleQueryService", FlextDbOracleQueryService)
        container.register("FlextDbOracleSchemaService", FlextDbOracleSchemaService)

        logger.info("FLEXT_DB_ORACLE dependencies configured successfully")

    except ImportError as e:
        logger.exception(f"Failed to configure FLEXT_DB_ORACLE dependencies: {e}")


def get_flext_db_oracle_service(service_name: str) -> Any:
    """Get flext_db_oracle service from container.

    Args:
        service_name: Name of service to retrieve.

    Returns:
        Service instance or None if not found.

    """
    container = get_flext_db_oracle_container()
    result = container.get(service_name)

    if result.success:
        return result.data

    logger.warning(
        f"FLEXT_DB_ORACLE service '{service_name}' not found: {result.error}",
    )
    return None


# Initialize flext_db_oracle dependencies on module import
configure_flext_db_oracle_dependencies()

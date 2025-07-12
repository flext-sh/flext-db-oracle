"""FLEXT DB Oracle - Enterprise Oracle Database Integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.

Built on flext-core foundation following DDD and Clean Architecture.
Zero tolerance for code duplication or legacy implementations.

This module provides enterprise-grade Oracle connectivity using modern Python 3.13
patterns and flext-core infrastructure.
"""

from __future__ import annotations

__version__ = "0.7.0"

# Core imports from flext-core (our foundation)
from flext_core import (
    BaseConfig,
    ConfigurationError,
    DomainBaseModel,
    DomainValueObject,
    ServiceResult,
)

# Connection and configuration services
from flext_db_oracle.application.services import (
    OracleConnectionService,
    OracleQueryService,
    OracleSchemaService,
)

# Configuration
from flext_db_oracle.config import OracleConfig

# Oracle-specific domain models
from flext_db_oracle.domain.models import (
    OracleConnectionInfo,
    OracleQueryResult,
    OracleSchemaInfo,
    OracleTableMetadata,
)

__all__ = [
    "BaseConfig",
    "ConfigurationError",
    # Re-exported from flext-core
    "DomainBaseModel",
    "DomainValueObject",
    # Configuration
    "OracleConfig",
    # Core domain models
    "OracleConnectionInfo",
    # Application services
    "OracleConnectionService",
    "OracleQueryResult",
    "OracleQueryService",
    "OracleSchemaInfo",
    "OracleSchemaService",
    "OracleTableMetadata",
    "ServiceResult",
    "__version__",
]

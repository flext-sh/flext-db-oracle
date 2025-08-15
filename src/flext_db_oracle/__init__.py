"""Enterprise Oracle Database integration library for FLEXT ecosystem."""

from __future__ import annotations

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.cli import oracle
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.config_types import MergeStatementConfig
from flext_db_oracle.connection import FlextDbOracleConnection
from flext_db_oracle.constants import FlextOracleDbConstants
from flext_db_oracle.exceptions import (
    FlextDbOracleAuthenticationError,
    FlextDbOracleConfigurationError,
    FlextDbOracleConnectionError,
    FlextDbOracleError,
    FlextDbOracleMetadataError,
    FlextDbOracleProcessingError,
    FlextDbOracleQueryError,
    FlextDbOracleTimeoutError,
    FlextDbOracleValidationError,
)
from flext_db_oracle.metadata import (
    FlextDbOracleColumn,
    FlextDbOracleMetadataManager,
    FlextDbOracleSchema,
    FlextDbOracleTable,
)
from flext_db_oracle.observability import (
    FlextDbOracleErrorHandler,
    FlextDbOracleObservabilityManager,
    FlextDbOracleOperationTracker,
)
from flext_db_oracle.plugins import (
    ORACLE_PLUGINS,
    create_data_validation_plugin,
    create_performance_monitor_plugin,
    create_security_audit_plugin,
    register_all_oracle_plugins,
)
from flext_db_oracle.typings import (
    CreateIndexConfig,
    TDbOracleColumn,
    TDbOracleConnectionStatus,
    TDbOracleQueryResult,
    TDbOracleSchema,
    TDbOracleTable,
)

# Backward compatibility aliases - maintain 100% compatibility
oracle_cli = oracle  # CLI alias for backward compatibility
# Backward compatibility class alias expected by older imports
FlextDbOracleAPI = FlextDbOracleApi

__all__: list[str] = [
    "ORACLE_PLUGINS",
    "CreateIndexConfig",
    "FlextDbOracleAPI",
    "FlextDbOracleApi",
    "FlextDbOracleAuthenticationError",
    "FlextDbOracleColumn",
    "FlextDbOracleConfig",
    "FlextDbOracleConfigurationError",
    "FlextDbOracleConnection",
    "FlextDbOracleConnectionError",
    "FlextDbOracleError",
    "FlextDbOracleErrorHandler",
    "FlextDbOracleMetadataError",
    "FlextDbOracleMetadataManager",
    "FlextDbOracleObservabilityManager",
    "FlextDbOracleOperationTracker",
    "FlextDbOracleProcessingError",
    "FlextDbOracleQueryError",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
    "FlextDbOracleTimeoutError",
    "FlextDbOracleValidationError",
    "FlextOracleDbConstants",
    "MergeStatementConfig",
    "TDbOracleColumn",
    "TDbOracleConnectionStatus",
    "TDbOracleQueryResult",
    "TDbOracleSchema",
    "TDbOracleTable",
    "__version__",
    "__version_info__",
    "create_data_validation_plugin",
    "create_performance_monitor_plugin",
    "create_security_audit_plugin",
    "oracle",
    "oracle_cli",
    "register_all_oracle_plugins",
]

__version__ = "0.9.0"
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())
__author__ = "flext-team"
__description__ = (
    "Modern Oracle Database Integration using SQLAlchemy 2 + oracledb "
    "with flext-core patterns"
)

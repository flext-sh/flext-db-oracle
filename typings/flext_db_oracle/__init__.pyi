from _typeshed import Incomplete

from flext_db_oracle.api import FlextDbOracleApi as FlextDbOracleApi
from flext_db_oracle.config import FlextDbOracleConfig as FlextDbOracleConfig
from flext_db_oracle.config_types import MergeStatementConfig as MergeStatementConfig
from flext_db_oracle.connection import (
    CreateIndexConfig as CreateIndexConfig,
    FlextDbOracleConnection as FlextDbOracleConnection,
)
from flext_db_oracle.constants import FlextOracleDbConstants as FlextOracleDbConstants
from flext_db_oracle.exceptions import (
    FlextDbOracleAuthenticationError as FlextDbOracleAuthenticationError,
    FlextDbOracleConfigurationError as FlextDbOracleConfigurationError,
    FlextDbOracleConnectionError as FlextDbOracleConnectionError,
    FlextDbOracleError as FlextDbOracleError,
    FlextDbOracleMetadataError as FlextDbOracleMetadataError,
    FlextDbOracleProcessingError as FlextDbOracleProcessingError,
    FlextDbOracleQueryError as FlextDbOracleQueryError,
    FlextDbOracleTimeoutError as FlextDbOracleTimeoutError,
    FlextDbOracleValidationError as FlextDbOracleValidationError,
)
from flext_db_oracle.metadata import (
    FlextDbOracleColumn as FlextDbOracleColumn,
    FlextDbOracleMetadataManager as FlextDbOracleMetadataManager,
    FlextDbOracleSchema as FlextDbOracleSchema,
    FlextDbOracleTable as FlextDbOracleTable,
)
from flext_db_oracle.observability import (
    FlextDbOracleErrorHandler as FlextDbOracleErrorHandler,
    FlextDbOracleObservabilityManager as FlextDbOracleObservabilityManager,
    FlextDbOracleOperationTracker as FlextDbOracleOperationTracker,
)
from flext_db_oracle.plugins import (
    ORACLE_PLUGINS as ORACLE_PLUGINS,
    create_data_validation_plugin as create_data_validation_plugin,
    create_performance_monitor_plugin as create_performance_monitor_plugin,
    create_security_audit_plugin as create_security_audit_plugin,
    register_all_oracle_plugins as register_all_oracle_plugins,
)
from flext_db_oracle.typings import (
    TDbOracleColumn as TDbOracleColumn,
    TDbOracleConnectionStatus as TDbOracleConnectionStatus,
    TDbOracleQueryResult as TDbOracleQueryResult,
    TDbOracleSchema as TDbOracleSchema,
    TDbOracleTable as TDbOracleTable,
)

__all__ = [
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
    "register_all_oracle_plugins",
]

FlextDbOracleAPI = FlextDbOracleApi
__version__: str
__version_info__: Incomplete

# Names in __all__ with no definition:
#   oracle
#   oracle_cli

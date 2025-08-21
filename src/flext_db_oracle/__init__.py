"""Enterprise Oracle Database integration library for FLEXT ecosystem."""

from __future__ import annotations

from flext_db_oracle.api import FlextDbOracleApi

# from flext_db_oracle.cli import oracle as _oracle  # Temporarily disabled - CLI deps missing
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.config_types import MergeStatementConfig
from flext_db_oracle.connection import CreateIndexConfig, FlextDbOracleConnection
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
from flext_db_oracle.metadata import FlextDbOracleMetadataManager
from flext_db_oracle.models import (
    FlextDbOracleColumn,
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
from flext_db_oracle.utilities import FlextDbOracleUtilities

# LEGACY IMPORTS REMOVED - Use models directly

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
    "FlextDbOracleUtilities",
    "FlextDbOracleValidationError",
    "FlextOracleDbConstants",
    "MergeStatementConfig",
    # LEGACY EXPORTS REMOVED - Use FlextDbOracle* models directly
    "__version__",
    "__version_info__",
    "create_data_validation_plugin",
    "create_performance_monitor_plugin",
    "create_security_audit_plugin",
    # CLI entrypoint is lazily provided via __getattr__ to avoid heavy deps at import time.
    # "oracle",
    # "oracle_cli",
    "register_all_oracle_plugins",
]

__version__ = "0.9.0"
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())
__author__ = "flext-team"
__description__ = (
    "Modern Oracle Database Integration using SQLAlchemy 2 + oracledb "
    "with flext-core patterns"
)


def __getattr__(name: str) -> object:  # pragma: no cover - import-time laziness
    """Provide lazy access to CLI entrypoints to avoid heavy imports by default.

    Tests may import `oracle_cli` or `oracle`. Only then we import the CLI module,
    preventing unnecessary Rich/Click imports during regular library usage.
    """
    if name in {"oracle", "oracle_cli"}:
        try:
            from flext_db_oracle.cli import oracle  # noqa: PLC0415

            return oracle
        except ImportError:
            msg = "CLI dependencies not available. Install with: pip install 'flext-db-oracle[cli]'"
            raise ImportError(msg) from None
    raise AttributeError(name)

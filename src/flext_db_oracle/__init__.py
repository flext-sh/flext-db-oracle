"""Enterprise Oracle Database integration library for FLEXT ecosystem."""

from __future__ import annotations

import click

from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.config import FlextDbOracleConfig
from flext_db_oracle.config_types import MergeStatementConfig
from flext_db_oracle.connection import CreateIndexConfig, FlextDbOracleConnection, FlextDbOracleConnections
from flext_db_oracle.constants import FlextDbOracleConstants
from flext_db_oracle.exceptions import (
    FlextDbOracleAuthenticationError,
    FlextDbOracleConfigurationError,
    FlextDbOracleConnectionError,
    FlextDbOracleError,
    FlextDbOracleExceptions,
    FlextDbOracleMetadataError,
    FlextDbOracleProcessingError,
    FlextDbOracleQueryError,
    FlextDbOracleTimeoutError,
    FlextDbOracleValidationError,
)
from flext_db_oracle.metadata import FlextDbOracleMetadataManager, FlextDbOracleMetadatas
from flext_db_oracle.models import (
    FlextDbOracleColumn,
    FlextDbOracleSchema,
    FlextDbOracleTable,
)
from flext_db_oracle.observability import FlextDbOracleObservabilityManager, FlextTrace, FlextHealthCheck
from flext_db_oracle.operation_tracker import FlextDbOracleOperationTracker
from flext_db_oracle.error_handler import FlextDbOracleErrorHandler
from flext_db_oracle.plugins import (
    FlextDbOraclePlugins,
    ORACLE_PLUGINS,
    create_data_validation_plugin,
    create_performance_monitor_plugin,
    create_security_audit_plugin,
    register_all_oracle_plugins,
)
from flext_db_oracle.utilities import FlextDbOracleUtilities
from flext_db_oracle.facade import FlextDbOracle

# CLI imports (with lazy loading protection)
try:
    from flext_db_oracle.cli import FlextDbOracleClis
    _CLI_AVAILABLE = True
except ImportError:
    _CLI_AVAILABLE = False

__all__: list[str] = [
    # Unified facade (primary entry point)
    "FlextDbOracle",
    # Core wrapper classes (Flext[Area][Module] pattern)
    "FlextDbOracleConnections",
    "FlextDbOracleExceptions",
    "FlextDbOracleMetadatas",
    "FlextDbOracleObservabilityManager",
    "FlextTrace",
    "FlextHealthCheck",
    "FlextDbOracleOperationTracker",
    "FlextDbOracleErrorHandler",
    "FlextDbOraclePlugins",
    "FlextDbOracleUtilities",
    # Legacy classes (backward compatibility)
    "FlextDbOracleApi",
    "FlextDbOracleConnection",
    "FlextDbOracleMetadataManager",
    "FlextDbOracleObservabilityManager",
    # Configuration
    "FlextDbOracleConfig",
    "FlextDbOracleConstants",
    "CreateIndexConfig",
    "MergeStatementConfig",
    # Models
    "FlextDbOracleColumn",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
    # Exceptions
    "FlextDbOracleAuthenticationError",
    "FlextDbOracleConfigurationError",
    "FlextDbOracleConnectionError",
    "FlextDbOracleError",
    "FlextDbOracleMetadataError",
    "FlextDbOracleProcessingError",
    "FlextDbOracleQueryError",
    "FlextDbOracleTimeoutError",
    "FlextDbOracleValidationError",
    # Plugins
    "ORACLE_PLUGINS",
    "create_data_validation_plugin",
    "create_performance_monitor_plugin",
    "create_security_audit_plugin",
    "register_all_oracle_plugins",
    # Version info
    "__version__",
    "__version_info__",
]

# Conditionally add CLI classes if available
if _CLI_AVAILABLE:
    __all__ += ["FlextDbOracleClis"]

__version__ = "0.9.0"
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())
__author__ = "flext-team"
__description__ = (
    "Modern Oracle Database Integration using SQLAlchemy 2 + oracledb "
    "with flext-core patterns"
)


def __getattr__(name: str) -> click.Command:  # pragma: no cover - import-time laziness
    """Provide lazy access to CLI entrypoints to avoid heavy imports by default.

    Tests may import `oracle_cli` or `oracle`. Only then we import the CLI module,
    preventing unnecessary Rich/Click imports during regular library usage.
    """
    if name in {"oracle", "oracle_cli"}:
        try:
            from flext_db_oracle.cli import oracle_cli  # noqa: PLC0415

            return oracle_cli
        except ImportError:
            msg = "CLI dependencies not available. Install with: pip install 'flext-db-oracle[cli]'"
            raise ImportError(msg) from None
    raise AttributeError(name)

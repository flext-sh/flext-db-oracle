"""FLEXT DB Oracle - Compatibility aliases and backward compatibility classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextTypes

from flext_db_oracle.models import OracleConfig

# Main aliases for backward compatibility
FlextDbOracleConfig = OracleConfig


# Ultra-simple aliases for missing classes - test compatibility
class FlextDbOracleCompatibilityAliases:
    """Unified compatibility class for test backward compatibility."""

    class MetadataManager:
        """MetadataManager compatibility alias."""

    class Table:
        """Table compatibility alias."""

    class Connection:
        """Connection compatibility alias."""

    class ObservabilityManager:
        """ObservabilityManager compatibility alias."""

    class Column:
        """Column compatibility alias."""

    class QueryResult:
        """QueryResult compatibility alias."""

    class Schema:
        """Schema compatibility alias."""

    class OperationTracker:
        """OperationTracker compatibility alias."""


# Compatibility aliases using the unified class
FlextDbOracleMetadataManager = FlextDbOracleCompatibilityAliases.MetadataManager
FlextDbOracleTable = FlextDbOracleCompatibilityAliases.Table
FlextDbOracleConnection = FlextDbOracleCompatibilityAliases.Connection
FlextDbOracleObservabilityManager = (
    FlextDbOracleCompatibilityAliases.ObservabilityManager
)
FlextDbOracleColumn = FlextDbOracleCompatibilityAliases.Column
FlextDbOracleQueryResult = FlextDbOracleCompatibilityAliases.QueryResult
FlextDbOracleSchema = FlextDbOracleCompatibilityAliases.Schema
FlextDbOracleOperationTracker = FlextDbOracleCompatibilityAliases.OperationTracker


__all__: FlextTypes.Core.StringList = [
    "FlextDbOracleColumn",
    "FlextDbOracleCompatibilityAliases",
    "FlextDbOracleConfig",
    "FlextDbOracleConnection",
    "FlextDbOracleMetadataManager",
    "FlextDbOracleObservabilityManager",
    "FlextDbOracleOperationTracker",
    "FlextDbOracleQueryResult",
    "FlextDbOracleSchema",
    "FlextDbOracleTable",
]

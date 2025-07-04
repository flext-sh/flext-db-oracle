"""Oracle Database Core Shared Library.

A comprehensive Oracle database toolkit providing enterprise-grade connectivity,
schema management, SQL parsing, data comparison, and maintenance utilities.

This library serves as the foundation for Oracle database operations across
the PyAuto framework, offering both synchronous and asynchronous APIs.
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "PyAuto Team"
__email__ = "dev@pyauto.com"
__license__ = "Apache-2.0"

# Core connection and configuration
# CLI entry points
from flext_db_oracle.cli.main import main as cli_main

# Data comparison and synchronization
from flext_db_oracle.compare.comparator import DataComparator, SchemaComparator
from flext_db_oracle.compare.differ import DataDiffer, SchemaDiffer
from flext_db_oracle.compare.synchronizer import DataSynchronizer
from flext_db_oracle.connection.config import ConnectionConfig
from flext_db_oracle.connection.connection import OracleConnection
from flext_db_oracle.connection.pool import ConnectionPool

# Maintenance and monitoring
from flext_db_oracle.maintenance.health import HealthChecker
from flext_db_oracle.maintenance.monitor import PerformanceMonitor
from flext_db_oracle.maintenance.optimizer import DatabaseOptimizer

# Schema management
from flext_db_oracle.schema.analyzer import SchemaAnalyzer
from flext_db_oracle.schema.ddl import DDLGenerator
from flext_db_oracle.schema.metadata import (
    ColumnMetadata,
    ConstraintMetadata,
    IndexMetadata,
    SchemaMetadata,
    TableMetadata,
)
from flext_db_oracle.sql.optimizer import QueryOptimizer

# SQL parsing and optimization
from flext_db_oracle.sql.parser import SQLParser
from flext_db_oracle.sql.validator import SQLValidator

# Utilities
from flext_db_oracle.utils.exceptions import (
    ConnectionError,
    OracleDBCoreError,
    SchemaError,
    SQLError,
    ValidationError,
)
from flext_db_oracle.utils.logger import get_logger

__all__ = [
    "ColumnMetadata",
    # Core connection
    "ConnectionConfig",
    "ConnectionError",
    "ConnectionPool",
    "ConstraintMetadata",
    "DDLGenerator",
    # Data operations
    "DataComparator",
    "DataDiffer",
    "DataSynchronizer",
    "DatabaseOptimizer",
    # Maintenance
    "HealthChecker",
    "IndexMetadata",
    "OracleConnection",
    # Utilities
    "OracleDBCoreError",
    "PerformanceMonitor",
    "QueryOptimizer",
    "SQLError",
    # SQL tools
    "SQLParser",
    "SQLValidator",
    # Schema management
    "SchemaAnalyzer",
    "SchemaComparator",
    "SchemaDiffer",
    "SchemaError",
    "SchemaMetadata",
    "TableMetadata",
    "ValidationError",
    "__author__",
    "__email__",
    "__license__",
    # Version and metadata
    "__version__",
    # CLI
    "cli_main",
    "get_logger",
]


def get_version() -> str:
    """Get the library version.

    Returns:
        The current version string.

    """
    return __version__


def get_info() -> dict[str, str]:
    """Get library information.

    Returns:
        Dictionary containing library metadata.

    """
    return {
        "name": "oracledb-core-shared",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "description": "Oracle Database Core Shared Library for PyAuto Framework",
    }

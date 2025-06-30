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
from .cli.main import main as cli_main

# Data comparison and synchronization
from .compare.comparator import DataComparator, SchemaComparator
from .compare.differ import DataDiffer, SchemaDiffer
from .compare.synchronizer import DataSynchronizer
from .connection.config import ConnectionConfig
from .connection.connection import OracleConnection
from .connection.pool import ConnectionPool

# Maintenance and monitoring
from .maintenance.health import HealthChecker
from .maintenance.monitor import PerformanceMonitor
from .maintenance.optimizer import DatabaseOptimizer

# Schema management
from .schema.analyzer import SchemaAnalyzer
from .schema.ddl import DDLGenerator
from .schema.metadata import (
    ColumnMetadata,
    ConstraintMetadata,
    IndexMetadata,
    SchemaMetadata,
    TableMetadata,
)
from .sql.optimizer import QueryOptimizer

# SQL parsing and optimization
from .sql.parser import SQLParser
from .sql.validator import SQLValidator

# Utilities
from .utils.exceptions import (
    ConnectionError,
    OracleDBCoreError,
    SchemaError,
    SQLError,
    ValidationError,
)
from .utils.logger import get_logger

__all__ = [
    # Version and metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # Core connection
    "ConnectionConfig",
    "OracleConnection",
    "ConnectionPool",
    # Schema management
    "SchemaAnalyzer",
    "DDLGenerator",
    "ColumnMetadata",
    "ConstraintMetadata",
    "IndexMetadata",
    "SchemaMetadata",
    "TableMetadata",
    # Data operations
    "DataComparator",
    "SchemaComparator",
    "DataDiffer",
    "SchemaDiffer",
    "DataSynchronizer",
    # SQL tools
    "SQLParser",
    "QueryOptimizer",
    "SQLValidator",
    # Maintenance
    "HealthChecker",
    "PerformanceMonitor",
    "DatabaseOptimizer",
    # Utilities
    "OracleDBCoreError",
    "ConnectionError",
    "SchemaError",
    "SQLError",
    "ValidationError",
    "get_logger",
    # CLI
    "cli_main",
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

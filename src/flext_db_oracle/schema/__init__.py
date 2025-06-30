"""Schema management and metadata modules."""

from .analyzer import SchemaAnalyzer
from .ddl import DDLGenerator
from .metadata import (
    ColumnMetadata,
    ConstraintMetadata,
    IndexMetadata,
    SchemaMetadata,
    TableMetadata,
)

__all__ = [
    "SchemaAnalyzer",
    "DDLGenerator",
    "ColumnMetadata",
    "ConstraintMetadata",
    "IndexMetadata",
    "SchemaMetadata",
    "TableMetadata",
]

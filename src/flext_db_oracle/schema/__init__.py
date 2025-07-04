"""Schema management and metadata modules."""

from flext_db_oracle.schema.analyzer import SchemaAnalyzer
from flext_db_oracle.schema.ddl import DDLGenerator
from flext_db_oracle.schema.metadata import (
    ColumnMetadata,
    ConstraintMetadata,
    IndexMetadata,
    SchemaMetadata,
    TableMetadata,
)

__all__ = [
    "ColumnMetadata",
    "ConstraintMetadata",
    "DDLGenerator",
    "IndexMetadata",
    "SchemaAnalyzer",
    "SchemaMetadata",
    "TableMetadata",
]

"""FLEXT DB Oracle Configuration Types following Flext[Area][Module] pattern.

This module provides the FlextDbOracleConfigTypes class with consolidated
configuration functionality following FLEXT architectural patterns with
DRY principles and SOLID design.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from dataclasses import dataclass

from flext_core import FlextFactory


class FlextDbOracleConfigTypes(FlextFactory):
    """Oracle Database Configuration Types following Flext[Area][Module] pattern.

    Single consolidated class containing all Oracle configuration types
    as internal classes, following SOLID principles and DRY methodology.

    This class consolidates all Oracle configuration functionality
    into a single entry point with internal organization.
    """

    @dataclass
    class MergeStatement:
        """Configuration for Oracle MERGE statement generation."""

        target_table: str
        source_columns: list[str]
        merge_keys: list[str]
        update_columns: list[str] | None = None
        insert_columns: list[str] | None = None
        schema_name: str | None = None
        hints: list[str] | None = None

    @dataclass
    class CreateIndex:
        """Configuration for Oracle CREATE INDEX statement generation."""

        index_name: str
        table_name: str
        columns: list[str]
        unique: bool = False
        schema_name: str | None = None
        tablespace: str | None = None
        parallel: int | None = None

    # Factory methods for creating configurations
    @classmethod
    def create_merge_config(
        cls,
        target_table: str,
        source_columns: list[str],
        merge_keys: list[str],
        update_columns: list[str] | None = None,
        insert_columns: list[str] | None = None,
        schema_name: str | None = None,
        hints: list[str] | None = None,
    ) -> MergeStatement:
        """Create MERGE statement configuration."""
        return cls.MergeStatement(
            target_table=target_table,
            source_columns=source_columns,
            merge_keys=merge_keys,
            update_columns=update_columns,
            insert_columns=insert_columns,
            schema_name=schema_name,
            hints=hints,
        )

    @classmethod
    def create_index_config(
        cls,
        index_name: str,
        table_name: str,
        columns: list[str],
        *,
        unique: bool = False,
        schema_name: str | None = None,
        tablespace: str | None = None,
        parallel: int | None = None,
    ) -> CreateIndex:
        """Create CREATE INDEX configuration."""
        return cls.CreateIndex(
            index_name=index_name,
            table_name=table_name,
            columns=columns,
            unique=unique,
            schema_name=schema_name,
            tablespace=tablespace,
            parallel=parallel,
        )

    # Backward compatibility aliases
    MergeStatementConfig = MergeStatement
    CreateIndexStatementConfig = CreateIndex


__all__ = [
    # Backward compatibility
    "CreateIndexStatementConfig",
    "FlextDbOracleConfigTypes",
    "MergeStatementConfig",
]

# Create backward compatibility module-level aliases
MergeStatementConfig = FlextDbOracleConfigTypes.MergeStatement
CreateIndexStatementConfig = FlextDbOracleConfigTypes.CreateIndex

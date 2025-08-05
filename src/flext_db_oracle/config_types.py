"""FLEXT DB Oracle Configuration Types - SOLID Refactoring Helpers.

This module provides configuration dataclasses to reduce method argument count
following SOLID principles (Single Responsibility Principle).

These types bundle related parameters to improve code readability and
maintainability while reducing the number of arguments passed to functions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MergeStatementConfig:
    """Configuration for Oracle MERGE statement generation - SOLID refactoring."""

    target_table: str
    source_columns: list[str]
    merge_keys: list[str]
    update_columns: list[str] | None = None
    insert_columns: list[str] | None = None
    schema_name: str | None = None
    hints: list[str] | None = None


@dataclass 
class CreateIndexStatementConfig:
    """Configuration for Oracle CREATE INDEX statement generation - SOLID refactoring."""

    index_name: str
    table_name: str
    columns: list[str]
    unique: bool = False
    schema_name: str | None = None
    tablespace: str | None = None
    parallel: int | None = None


__all__ = [
    "MergeStatementConfig",
    "CreateIndexStatementConfig",
]
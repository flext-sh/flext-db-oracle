"""Oracle Database Configuration - Settings using flext-core patterns.

Provides Oracle-specific configuration management extending FlextSettings
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections import UserString
from typing import Annotated

from pydantic import (
    BeforeValidator,
)

from flext_db_oracle.constants import c

try:
    _oracledb_module = __import__("oracledb")
    OracleDatabaseError = _oracledb_module.DatabaseError
    OracleInterfaceError = _oracledb_module.InterfaceError
except (ImportError, AttributeError):
    OracleDatabaseError = ConnectionError
    OracleInterfaceError = ConnectionError


def _validate_oracle_identifier(v: str) -> str:
    """Validate Oracle identifier: length check + strip + uppercase."""
    if len(v) > c.DbOracle.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH:
        msg = f"Oracle identifier too long (max {c.DbOracle.OracleValidation.MAX_ORACLE_IDENTIFIER_LENGTH} chars)"
        raise ValueError(msg)
    return v.strip().upper()


OracleIdentifier = Annotated[str, BeforeValidator(_validate_oracle_identifier)]


class OraclePassword(UserString):
    """String-compatible password wrapper exposing get_secret_value()."""

    def get_secret_value(self) -> str:
        """Return raw password value for compatibility with SecretStr callers."""
        return str(self)

"""FlextDbOracle utilities module."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping
from enum import StrEnum
from typing import Annotated

from flext_core import FlextUtilities, r, u
from flext_db_oracle.constants import c
from flext_db_oracle.settings import FlextDbOracleSettings
from pydantic import BeforeValidator


class FlextDbOracleUtilities(FlextUtilities):
    """FlextDbOracle utilities extending FlextUtilities with Oracle-specific helpers.

    Architecture: Advanced utilities with ZERO code bloat through:
    - TypeIs/TypeGuard for narrowing (PEP 742)
    - BeforeValidator factories for Pydantic coercion
    - @validated decorators eliminating manual validation
    - Generic parsing utilities for StrEnums (inherited from parent)
    """

    # ═══════════════════════════════════════════════════════════════════
    # ORACLE NAMESPACE: Project-specific utilities
    # ═══════════════════════════════════════════════════════════════════

    class DbOracle:
        """Oracle-specific utility namespace.

        This namespace groups all Oracle-specific utilities for better organization
        and cross-project access. Access via u.Oracle.* pattern.

        Example:
            from flext_db_oracle.utilities import u
            result = u.Oracle.Collection.parse_sequence(Status, ["active", "pending"])
            parsed = u.Oracle.Args.parse_kwargs(kwargs, enum_fields)

        """

        class Collection(u.Collection):
            """Collection utilities extending u.Collection via inheritance.

            Exposes all flext-core Collection methods through inheritance hierarchy.
            Access via u.Oracle.Collection.* pattern.
            """

        # ═══════════════════════════════════════════════════════════════════
        # ARGS UTILITIES: @validated, parse_kwargs - ZERO validation boilerplate
        # ═══════════════════════════════════════════════════════════════════

        class Args(u.Args):
            """Args utilities extending u.Args via inheritance.

            Exposes all flext-core Args methods through inheritance hierarchy,
            including validated, validated_with_result, parse_kwargs, and get_enum_params.
            Access via u.Oracle.Args.* pattern.
            """

        # ═══════════════════════════════════════════════════════════════════
        # MODEL UTILITIES: from_dict, merge_defaults, update - ZERO try/except
        # ═══════════════════════════════════════════════════════════════════

        class Model(u.Model):
            """Model utilities extending u.Model via inheritance.

            Exposes all flext-core Model methods through inheritance hierarchy.
            Access via u.Oracle.Model.* pattern.
            """

        # ═══════════════════════════════════════════════════════════════════
        # PYDANTIC UTILITIES: Annotated type factories
        # ═══════════════════════════════════════════════════════════════════

        class Pydantic:
            """Factories for Annotated types."""

            @staticmethod
            def coerced_enum[E: StrEnum](
                enum_cls: type[E],
            ) -> object:
                """Create an Annotated StrEnum type with automatic coercion.

                Args:
                    enum_cls: The StrEnum class to create an annotated type for.

                Returns:
                    An Annotated type that validates and coerces string values to the enum.

                """
                return Annotated[
                    enum_cls,
                    BeforeValidator(u.Enum.coerce_validator(enum_cls)),
                ]

        # ═══════════════════════════════════════════════════════════════════
        # FEATURE FLAGS: Environment-based feature toggles
        # ═══════════════════════════════════════════════════════════════════

        class FeatureFlags:
            """Feature toggles for progressive dispatcher rollout.

            Moved from constants.py to utilities.py to comply with
            architecture rules (constants.py must contain only constants).
            Access via u.Oracle.FeatureFlags.* pattern.
            """

            @staticmethod
            def _env_enabled(flag_name: str, default: str = "0") -> bool:
                """Check if environment flag is enabled."""
                value = os.environ.get(flag_name, default)
                return value.lower() not in {"0", "false", "no"}

            @classmethod
            def dispatcher_enabled(cls) -> bool:
                """Return True when dispatcher integration should be used."""
                return cls._env_enabled("FLEXT_DB_ORACLE_ENABLE_DISPATCHER")

    class OracleValidation:
        """Oracle validation grouping class."""

        @staticmethod
        def validate_identifier(identifier: str) -> r[bool]:
            """Validate an Oracle identifier."""
            if not identifier:
                return r[bool].fail("Empty Oracle identifier")
            if len(identifier) > c.DbOracle.OracleValidation.MAX_IDENTIFIER_LENGTH:
                return r[bool].fail("Oracle identifier too long")
            if identifier.upper() in c.DbOracle.OracleValidation.ORACLE_RESERVED:
                return r[bool].fail("Oracle identifier is reserved word")
            return r[bool].ok(True)

    @staticmethod
    def escape_oracle_identifier(identifier: str) -> r[str]:
        """Escape and validate an Oracle identifier for safe use."""
        if not identifier.strip():
            return r[str].fail("Empty Oracle identifier")
        if not identifier.replace("_", "").isalnum():
            return r[str].fail("Invalid Oracle identifier")
        max_len = c.DbOracle.OracleValidation.MAX_IDENTIFIER_LENGTH
        return r[str].ok(identifier[:max_len])

    @staticmethod
    def format_query_result(
        result: object,
        format_type: str = "table",
    ) -> r[str]:
        """Format a query result to string or JSON."""
        if format_type == "json":
            return r[str].ok(json.dumps(result, default=str))
        return r[str].ok(str(result))

    @staticmethod
    def generate_query_hash(
        query: str,
        params: Mapping[str, object] | None,
    ) -> r[str]:
        """Generate a SHA-256 hash for a query and its parameters."""
        serialized = json.dumps(params or {}, sort_keys=True, default=str)
        payload = f"{query}|{serialized}".encode()
        return r[str].ok(hashlib.sha256(payload).hexdigest()[:16])

    @staticmethod
    def format_sql_for_oracle(sql: str) -> r[str]:
        """Normalize SQL string formatting for Oracle execution."""
        normalized = " ".join(sql.split())
        return r[str].ok(normalized)

    @staticmethod
    def create_config_from_env() -> r[FlextDbOracleSettings]:
        """Create Oracle settings directly from the environment variables."""
        config_result = FlextDbOracleSettings.from_env("FLEXT_DB_ORACLE_")
        if config_result.is_failure:
            return r[FlextDbOracleSettings].fail(config_result.error)
        return r[FlextDbOracleSettings].ok(config_result.value)


u = FlextDbOracleUtilities


__all__ = [
    "FlextDbOracleUtilities",
    "u",
]

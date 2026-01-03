"""FlextDbOracle utilities module."""

from __future__ import annotations

import os
from enum import StrEnum
from typing import Annotated

from flext_core.utilities import FlextUtilities, u
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

    class Oracle:
        """Oracle-specific utility namespace.

        This namespace groups all Oracle-specific utilities for better organization
        and cross-project access. Access via u.Oracle.* pattern.

        Example:
            from flext_db_oracle.utilities import u
            result = u.Oracle.Collection.parse_sequence(Status, ["active", "pending"])
            parsed = u.Oracle.Args.parse_kwargs(kwargs, enum_fields)

        """

        class Collection(u.Collection):
            """Collection utilities extending u_core.Collection via inheritance.

            Exposes all flext-core Collection methods through inheritance hierarchy.
            Access via u.Oracle.Collection.* pattern.
            """

        # ═══════════════════════════════════════════════════════════════════
        # ARGS UTILITIES: @validated, parse_kwargs - ZERO validation boilerplate
        # ═══════════════════════════════════════════════════════════════════

        class Args(u.Args):
            """Args utilities extending u_core.Args via inheritance.

            Exposes all flext-core Args methods through inheritance hierarchy,
            including validated, validated_with_result, parse_kwargs, and get_enum_params.
            Access via u.Oracle.Args.* pattern.
            """

        # ═══════════════════════════════════════════════════════════════════
        # MODEL UTILITIES: from_dict, merge_defaults, update - ZERO try/except
        # ═══════════════════════════════════════════════════════════════════

        class Model(u.Model):
            """Model utilities extending u_core.Model via inheritance.

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
            ) -> type[Annotated[E, BeforeValidator]]:
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


__all__ = [
    "FlextDbOracleUtilities",
]

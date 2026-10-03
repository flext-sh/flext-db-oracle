"""Unit tests for flext_db_oracle.typings module.

Behavioral contract tests for the FlextDbOracleTypes facade: the Oracle
type namespace, its MRO composition over the flext-cli ``t`` facade, the
Oracle exception bindings, and the PEP 695 type aliases it publishes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import oracledb
import pytest
from flext_cli import t as cli_types
from flext_tests import tm

from flext_db_oracle import FlextDbOracleTypes, t, typings as typings_module


class TestsFlextDbOracleTypings:
    """Behavioral contract for the FlextDbOracleTypes facade."""

    @staticmethod
    def test_t_alias_points_to_facade_class() -> None:
        """The module-level ``t`` alias resolves to the facade class."""
        assert t is FlextDbOracleTypes

    @staticmethod
    def test_public_exports_are_declared() -> None:
        """The module publishes exactly its facade class and alias."""
        tm.that(typings_module.__all__, eq=["FlextDbOracleTypes", "t"])

    @staticmethod
    def test_facade_composes_cli_types_via_mro() -> None:
        """Facade extends the flext-cli ``t`` facade so inherited members stay reachable."""
        assert issubclass(FlextDbOracleTypes, cli_types)
        assert hasattr(FlextDbOracleTypes, "Scalar")

    @staticmethod
    def test_oracle_namespace_is_exposed() -> None:
        """The Oracle domain namespace is reachable on the facade."""
        tm.that(FlextDbOracleTypes.DbOracle, none=False)

    @staticmethod
    @pytest.mark.parametrize(
        ("attribute", "expected"),
        [
            ("OracleDatabaseError", oracledb.DatabaseError),
            ("OracleInterfaceError", oracledb.InterfaceError),
        ],
    )
    def test_oracle_exception_bindings_map_to_driver(
        attribute: str, expected: type[Exception],
    ) -> None:
        """Oracle exception aliases bind to the driver's exception classes."""
        bound = getattr(FlextDbOracleTypes.DbOracle, attribute)
        assert bound is expected
        assert issubclass(bound, Exception)

    @staticmethod
    def test_query_parameters_alias_resolves_to_json_mapping() -> None:
        """``QueryParameters`` is a named alias for the cli JSON mapping type."""
        alias = FlextDbOracleTypes.DbOracle.QueryParameters
        assert alias.__value__ is cli_types.JsonMapping

    @staticmethod
    def test_cli_scalar_alias_is_optional_scalar() -> None:
        """``CliScalar`` is a named alias admitting the scalar type or ``None``."""
        alias = FlextDbOracleTypes.DbOracle.CliScalar
        tm.that(alias.__value__.__args__, has=type(None))

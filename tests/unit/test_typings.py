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
from flext_tests import tm

from flext_cli import t as cli_types
from flext_db_oracle import FlextDbOracleTypes, t, typings as typings_module


class TestsFlextDbOracleTypings:
    """Behavioral contract for the FlextDbOracleTypes facade."""

    def test_t_alias_points_to_facade_class(self) -> None:
        """The module-level ``t`` alias resolves to the facade class."""
        assert t is FlextDbOracleTypes

    def test_public_exports_are_declared(self) -> None:
        """The module publishes exactly its facade class and alias."""
        tm.that(typings_module.__all__, eq=["FlextDbOracleTypes", "t"])

    def test_facade_composes_cli_types_via_mro(self) -> None:
        """Facade extends the flext-cli ``t`` facade so inherited members stay reachable."""
        assert issubclass(FlextDbOracleTypes, cli_types)
        assert hasattr(FlextDbOracleTypes, "Scalar")

    def test_oracle_namespace_is_exposed(self) -> None:
        """The Oracle domain namespace is reachable on the facade."""
        tm.that(FlextDbOracleTypes.DbOracle, none=False)

    @pytest.mark.parametrize(
        ("attribute", "expected"),
        [
            ("OracleDatabaseError", oracledb.DatabaseError),
            ("OracleInterfaceError", oracledb.InterfaceError),
        ],
    )
    def test_oracle_exception_bindings_map_to_driver(
        self,
        attribute: str,
        expected: type[Exception],
    ) -> None:
        """Oracle exception aliases bind to the driver's exception classes."""
        bound = getattr(FlextDbOracleTypes.DbOracle, attribute)
        assert bound is expected
        assert issubclass(bound, Exception)

    def test_query_parameters_alias_resolves_to_json_mapping(self) -> None:
        """``QueryParameters`` is a named alias for the cli JSON mapping type."""
        alias = FlextDbOracleTypes.DbOracle.QueryParameters
        tm.that(alias.__name__, eq="QueryParameters")
        assert alias.__value__ is cli_types.JsonMapping

    def test_cli_scalar_alias_is_optional_scalar(self) -> None:
        """``CliScalar`` is a named alias admitting the scalar type or ``None``."""
        alias = FlextDbOracleTypes.DbOracle.CliScalar
        tm.that(alias.__name__, eq="CliScalar")
        tm.that(alias.__value__.__args__, has=type(None))

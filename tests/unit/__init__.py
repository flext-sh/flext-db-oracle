# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import tests.unit.conftest as _tests_unit_conftest

    conftest = _tests_unit_conftest
    import tests.unit.test_api as _tests_unit_test_api

    test_api = _tests_unit_test_api
    import tests.unit.test_cli as _tests_unit_test_cli

    test_cli = _tests_unit_test_cli
    import tests.unit.test_client as _tests_unit_test_client

    test_client = _tests_unit_test_client
    import tests.unit.test_config as _tests_unit_test_config

    test_config = _tests_unit_test_config
    import tests.unit.test_constants as _tests_unit_test_constants

    test_constants = _tests_unit_test_constants
    import tests.unit.test_coverage_baseline as _tests_unit_test_coverage_baseline

    test_coverage_baseline = _tests_unit_test_coverage_baseline
    import tests.unit.test_dispatcher as _tests_unit_test_dispatcher

    test_dispatcher = _tests_unit_test_dispatcher
    import tests.unit.test_exceptions as _tests_unit_test_exceptions

    test_exceptions = _tests_unit_test_exceptions
    import tests.unit.test_fields as _tests_unit_test_fields

    test_fields = _tests_unit_test_fields
    import tests.unit.test_metadata as _tests_unit_test_metadata

    test_metadata = _tests_unit_test_metadata
    import tests.unit.test_models as _tests_unit_test_models

    test_models = _tests_unit_test_models
    import tests.unit.test_oracle_example as _tests_unit_test_oracle_example

    test_oracle_example = _tests_unit_test_oracle_example
    import tests.unit.test_oracle_exceptions as _tests_unit_test_oracle_exceptions

    test_oracle_exceptions = _tests_unit_test_oracle_exceptions
    import tests.unit.test_protocols as _tests_unit_test_protocols

    test_protocols = _tests_unit_test_protocols
    import tests.unit.test_services as _tests_unit_test_services

    test_services = _tests_unit_test_services
    import tests.unit.test_typings as _tests_unit_test_typings

    test_typings = _tests_unit_test_typings
    import tests.unit.test_utilities as _tests_unit_test_utilities

    test_utilities = _tests_unit_test_utilities
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
_LAZY_IMPORTS = {
    "c": ("flext_core.constants", "FlextConstants"),
    "conftest": "tests.unit.conftest",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "test_api": "tests.unit.test_api",
    "test_cli": "tests.unit.test_cli",
    "test_client": "tests.unit.test_client",
    "test_config": "tests.unit.test_config",
    "test_constants": "tests.unit.test_constants",
    "test_coverage_baseline": "tests.unit.test_coverage_baseline",
    "test_dispatcher": "tests.unit.test_dispatcher",
    "test_exceptions": "tests.unit.test_exceptions",
    "test_fields": "tests.unit.test_fields",
    "test_metadata": "tests.unit.test_metadata",
    "test_models": "tests.unit.test_models",
    "test_oracle_example": "tests.unit.test_oracle_example",
    "test_oracle_exceptions": "tests.unit.test_oracle_exceptions",
    "test_protocols": "tests.unit.test_protocols",
    "test_services": "tests.unit.test_services",
    "test_typings": "tests.unit.test_typings",
    "test_utilities": "tests.unit.test_utilities",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "c",
    "conftest",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "test_api",
    "test_cli",
    "test_client",
    "test_config",
    "test_constants",
    "test_coverage_baseline",
    "test_dispatcher",
    "test_exceptions",
    "test_fields",
    "test_metadata",
    "test_models",
    "test_oracle_example",
    "test_oracle_exceptions",
    "test_protocols",
    "test_services",
    "test_typings",
    "test_utilities",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

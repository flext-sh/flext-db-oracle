# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports

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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

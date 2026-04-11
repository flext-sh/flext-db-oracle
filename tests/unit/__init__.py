# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".conftest": ("conftest",),
        ".exceptions": ("exceptions",),
        ".test_api": ("test_api",),
        ".test_cli": ("test_cli",),
        ".test_client": ("test_client",),
        ".test_config": ("test_config",),
        ".test_constants": ("test_constants",),
        ".test_coverage_baseline": ("test_coverage_baseline",),
        ".test_dispatcher": ("test_dispatcher",),
        ".test_exceptions": ("test_exceptions",),
        ".test_fields": ("test_fields",),
        ".test_metadata": ("test_metadata",),
        ".test_models": ("test_models",),
        ".test_oracle_example": ("test_oracle_example",),
        ".test_oracle_exceptions": ("test_oracle_exceptions",),
        ".test_protocols": ("test_protocols",),
        ".test_services": ("test_services",),
        ".test_typings": ("test_typings",),
        ".test_utilities": ("test_utilities",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

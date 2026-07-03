# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export registry."""

from __future__ import annotations

from flext_core.lazy import merge_lazy_imports
from flext_db_oracle.tests._exports_lazy_part_01 import (
    TESTS_FLEXT_DB_ORACLE_LAZY_IMPORTS_PART_01,
)
from flext_db_oracle.tests._exports_lazy_part_02 import (
    TESTS_FLEXT_DB_ORACLE_LAZY_IMPORTS_PART_02,
)

_LOCAL_LAZY_IMPORTS = {
    **TESTS_FLEXT_DB_ORACLE_LAZY_IMPORTS_PART_01,
    **TESTS_FLEXT_DB_ORACLE_LAZY_IMPORTS_PART_02,
}

TESTS_FLEXT_DB_ORACLE_LAZY_IMPORTS = merge_lazy_imports(
    (
        ".e2e",
        ".integration",
        ".unit",
    ),
    _LOCAL_LAZY_IMPORTS,
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name="flext_db_oracle.tests",
)

__all__: list[str] = ["TESTS_FLEXT_DB_ORACLE_LAZY_IMPORTS"]

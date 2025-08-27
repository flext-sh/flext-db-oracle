"""Enterprise Oracle Database integration library for FLEXT ecosystem.

FLEXT Compliant Structure - 7 Modules:
- models.py: All Pydantic models, configurations, and data structures
- services.py: All business services and database operations
- exceptions.py: All custom exceptions and error handling
- constants.py: All project constants and configuration
- client.py: CLI implementation and user interface
- api.py: Main API facade for orchestration
- utilities.py: Oracle-specific utilities extending flext-core FlextUtilities

This structure follows FLEXT architectural patterns with consolidated classes
and eliminates duplication across the codebase with MASSIVE use of flext-core utilities.
"""

from __future__ import annotations

import click

# ruff: noqa: F403
# Import all from each module following flext-core pattern
from flext_db_oracle.api import *
from flext_db_oracle.client import *
from flext_db_oracle.constants import *
from flext_db_oracle.exceptions import *
from flext_db_oracle.models import *
from flext_db_oracle.services import *
from flext_db_oracle.utilities import *

# CLI imports (with lazy loading protection)
try:
    from flext_db_oracle.client import oracle_cli, FlextDbOracleClis
    _CLI_AVAILABLE = True
except ImportError:
    _CLI_AVAILABLE = False

# Note: __all__ is constructed dynamically at runtime from imported modules
# This pattern is necessary for library aggregation but causes pyright warnings
__all__: list[str] = []

# Conditionally add CLI classes if available
if _CLI_AVAILABLE:
    __all__ += ["oracle_cli", "FlextDbOracleClis"]

__version__ = "0.9.0"
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())
__author__ = "flext-team"
__description__ = (
    "Modern Oracle Database Integration using SQLAlchemy 2 + oracledb "
    "with flext-core patterns"
)


def __getattr__(name: str) -> click.Command:  # pragma: no cover - import-time laziness
    """Provide lazy access to CLI entrypoints to avoid heavy imports by default.

    Tests may import `oracle_cli` or `oracle`. Only then we import the CLI module,
    preventing unnecessary Rich/Click imports during regular library usage.
    """
    if name in {"oracle", "oracle_cli"}:
        try:
            from flext_db_oracle.client import oracle_cli  # noqa: PLC0415

            return oracle_cli
        except ImportError:
            msg = "CLI dependencies not available. Install with: pip install 'flext-db-oracle[cli]'"
            raise ImportError(msg) from None
    raise AttributeError(name)

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

from typing import Any

# ruff: noqa: F403
# Import all from each module following flext-core pattern
from flext_db_oracle.api import *
from flext_db_oracle.client import *
from flext_db_oracle.constants import *
from flext_db_oracle.exceptions import *
from flext_db_oracle.models import *
from flext_db_oracle.plugins import *
from flext_db_oracle.services import *
from flext_db_oracle.utilities import *

# Combine all __all__ from all modules
import flext_db_oracle.api as _api
import flext_db_oracle.client as _client
import flext_db_oracle.constants as _constants
import flext_db_oracle.exceptions as _exceptions
import flext_db_oracle.models as _models
import flext_db_oracle.plugins as _plugins
import flext_db_oracle.services as _services
import flext_db_oracle.utilities as _utilities

__all__: list[str] = []
for module in [
    _api,
    _client,
    _constants,
    _exceptions,
    _models,
    _plugins,
    _services,
    _utilities,
]:
    if hasattr(module, "__all__"):
        __all__ += module.__all__

# Remove duplicates and sort
__all__[:] = sorted(set(__all__))

# CLI imports (with lazy loading protection)
try:
    from flext_db_oracle.client import oracle_cli

    __all__ += ["oracle_cli"]
    _CLI_AVAILABLE = True
except ImportError:
    _CLI_AVAILABLE = False

__version__ = "0.9.0"
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())
__author__ = "flext-team"
__description__ = (
    "Modern Oracle Database Integration using SQLAlchemy 2 + oracledb "
    "with flext-core patterns"
)


def __getattr__(name: str) -> Any:  # pragma: no cover - import-time laziness
    """Provide lazy access to CLI entrypoints to avoid heavy imports by default.

    Tests may import `oracle_cli` or `oracle`. Only then we import the CLI module,
    preventing unnecessary Rich/Click imports during regular library usage.
    """
    if name in {"oracle", "oracle_cli"}:
        try:
            from flext_db_oracle.client import oracle_cli

            return oracle_cli
        except ImportError:
            msg = "CLI dependencies not available. Install with: pip install 'flext-db-oracle[cli]'"
            raise ImportError(msg) from None
    raise AttributeError(name)

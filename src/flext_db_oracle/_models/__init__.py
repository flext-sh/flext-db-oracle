"""Internal models package for flext-db-oracle.

Hosts Pydantic ``BaseModel``/``RootModel`` subclasses per AGENTS.md §2.2 —
each declaration lives under ``_models/<name>.py`` and is re-exported by
the parent ``flext_db_oracle.__init__`` lazy map.
"""

from __future__ import annotations

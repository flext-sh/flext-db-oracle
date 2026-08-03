# AGENTS.md — flext-db-oracle

> **Parent workspace law** lives in [`../AGENTS.md`](../AGENTS.md) — read it first.
> Universal engineering core: `~/.agents/UNIVERSAL_CORE.md`. Composition: global skills + parent/root `AGENTS.md` + this scope delta. Do not re-embed universal law.
>
> **Standalone / independent mode:** when `../AGENTS.md` does not resolve, pin the parent raw `AGENTS.md` URL to the same branch/release as this package (never `main`).

<!-- AIHUB-AGENTS-SCOPE-LOCAL-BEGIN -->
**Package:** `flext_db_oracle` · deps: `flext-cli`, `flext-core`

## Overview

Enterprise Oracle database operations library. Base for the Oracle Singer connectors (`flext-tap-oracle`, `flext-target-oracle`, `flext-dbt-oracle`).

## Structure

```text
src/flext_db_oracle/
├── api.py            # FlextDbOracleApi facade
├── base.py client.py dispatcher.py exceptions.py
├── services/         # connection, query, schema, SQL building, Singer, plugins, API runtime
├── constants.py typings.py protocols.py models.py utilities.py   # AUTO-GENERATED facets
└── _models/ _utilities/db_oracle.py
```

## Code Map

| Symbol | Kind | Location | Role |
|--------|------|----------|------|
| `FlextDbOracleApi` | class | `api.py` | facade; ctor resolves `settings.DbOracle.*` |
| `FlextDbOracleClient` | class | `client.py` | connection client |
| `FlextDbOracleDispatcher` | class | `dispatcher.py` | command dispatch |
| `FlextDbOracleServiceQuery` | class | `services/query.py` | query service |

## Conventions (specific to this package)

- **Settings are namespaced** — access `settings.DbOracle.*` (host/port/user/service_name/context_name), never flat `settings.host`. The API ctor resolves them from that namespace.

## Anti-Patterns / Gotchas

- Downstream consumers construct config as nested `{"DbOracle": {...}}` — flat construction is dropped (`extra=ignore`).

## Commands

```bash
make check PROJECT=flext-db-oracle
make test  PROJECT=flext-db-oracle       # tests/{unit,integration,e2e}
```
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->

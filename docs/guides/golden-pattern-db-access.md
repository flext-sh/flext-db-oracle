# Golden Pattern — Database Access (flext-db-oracle / SQLAlchemy 2 / SQLModel)

The single reference for every flext member that touches a database
(dc-recon today; flext-tap-oracle, flext-target-oracle, flext-dbt-oracle and
non-Oracle adapters tomorrow). Consumers depend on **ports**, never on the
concrete adapter: Clean Architecture with the flext-core DI container.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

## Layers

```
consumers (CLI, daemon, services)      — depend only on ports (p.DbOracle)
ports        p.DbOracle.*              — runtime_checkable Protocols
adapter      FlextDbOracleServices     — mixin facade implementing the ports
engine       SQLAlchemy 2 (Engine/Connection/select())
rows         pydantic / SQLModel models validated from native mappings
```

## Rules

1. **Ports first.** Declare the operation in
   `src/flext_db_oracle/_protocols/*_protocols.py`, compose it into
   `p.DbOracle`, then implement it on the mixin. Structural checks
   (`isinstance(svc, p.DbOracle.QueryExecutor)`) prove the contract.
2. **Typed rows via `fetch_models`.** Never hand-parse positional rows:
   `svc.fetch_models(sql_or_select, params, *, model=RowModel)` returns
   `r[Sequence[RowModel]]` with NATIVE column values (dates, decimals — no
   string coercion). The model is pydantic or SQLModel.
3. **Statements over strings where shape matters.** Control tables get
   SQLModel `table=True` models; reads/writes use `select()`/`update()`
   compiled for the Oracle dialect. Raw SQL stays only for engine-owned
   blocks (PL/SQL) and dynamic dictionary views.
4. **One engine factory.** `_engine_factory(url)` on the Connection mixin is
   the only engine constructor; connect/disconnect/test/transaction reuse it.
   Members with another transport (TNS descriptor, thick mode, SYSDBA)
   override the hook — never reimplement the lifecycle.
5. **Batch writes with `execute_many`.** One native executemany round trip
   per batch; empty batch short-circuits to `r[int].ok(0)`.
6. **Results are `r[T]`.** Every fallible operation returns
   `p.Result[...]`; DB errors wrap into typed failures at the adapter
   boundary — consumers catch the port error type, not SQLAlchemy.
7. **DI at the composition root.** Members register the concrete facade
   against the ports it satisfies; resolution flows through the flext-core
   container (`FlextContainer`), so swapping the adapter (another database)
   touches only the root.

## Member adoption sketch

```python
class MemberServiceBase(
    FlextDbOracleServiceQuery,  # execute/fetch_models/execute_many
    FlextDbOracleServiceSchema,  # fetch_columns/fetch_primary_keys
    FlextDbOracleServiceBase,
):
    def _engine_factory(self, url: str) -> SAEngine:
        return u.Member.engine(url)  # member transport (TNS/thick/pools)
```

Control-table example (dc-recon):

```python
stmt = select(CmpFatiaHist).where(
    CmpFatiaHist.owner == owner, CmpFatiaHist.dh_exec >= desde
)
rows = self.fetch_models(stmt, model=CmpFatiaHist).unwrap()
```

## Forward compatibility

A new database = a new adapter package implementing the same
`p.DbOracle`-shaped ports (rename per family) + registration in its
composition root. Consumers and tests written against the ports do not
change.

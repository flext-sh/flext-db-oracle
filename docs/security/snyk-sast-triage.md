# Triagem Snyk Code (SAST) — flext-sh/flext-db-oracle

Gerado do scan Snyk da org Datacosmos (dump 2026-08-06).

**17 achados** — critical 0, high 0, medium 2, low 15

| categoria | achados |
|---|---|
| Use of Hardcoded Passwords | 17 |

## Achados

Coluna **Decisão**: `corrigir` / `falso-positivo` / `risco-aceito`.

| # | sev | categoria | arquivo | linha | CWE | Decisão |
|---|---|---|---|---|---|---|
| 1 | medium | Use of Hardcoded Passwords | `examples/05_simple_working.py` | 28 | - | |
| 2 | medium | Use of Hardcoded Passwords | `examples/07_sqlalchemy2.py` | 35 | - | |
| 3 | low | Use of Hardcoded Passwords | `tests/e2e/test_oracle.py` | 41 | - | |
| 4 | low | Use of Hardcoded Passwords | `tests/integration/test_oracle.py` | 36 | - | |
| 5 | low | Use of Hardcoded Passwords | `tests/unit/test_api.py` | 36 | - | |
| 6 | low | Use of Hardcoded Passwords | `tests/unit/test_cli.py` | 229 | - | |
| 7 | low | Use of Hardcoded Passwords | `tests/unit/test_cli.py` | 265 | - | |
| 8 | low | Use of Hardcoded Passwords | `tests/unit/test_config.py` | 58 | - | |
| 9 | low | Use of Hardcoded Passwords | `tests/unit/test_coverage_baseline.py` | 33 | - | |
| 10 | low | Use of Hardcoded Passwords | `tests/unit/test_coverage_baseline.py` | 65 | - | |
| 11 | low | Use of Hardcoded Passwords | `tests/unit/test_coverage_baseline.py` | 78 | - | |
| 12 | low | Use of Hardcoded Passwords | `tests/unit/test_dispatcher.py` | 25 | - | |
| 13 | low | Use of Hardcoded Passwords | `tests/unit/test_models.py` | 308 | - | |
| 14 | low | Use of Hardcoded Passwords | `tests/unit/test_oracle_example.py` | 275 | - | |
| 15 | low | Use of Hardcoded Passwords | `tests/unit/test_services.py` | 37 | - | |
| 16 | low | Use of Hardcoded Passwords | `tests/unit/test_services.py` | 80 | - | |
| 17 | low | Use of Hardcoded Passwords | `tests/unit/test_services.py` | 478 | - | |

## Como triar

1. Abrir `arquivo:linha` e seguir o fluxo de dados até o sink.
2. Classificar: **corrigir** (entrada externa alcança o sink sem sanitização), **falso-positivo** (credencial de fixture, path de constante — registrar em `.snyk` com justificativa), **risco-aceito** (com prazo de revisão).

Dados brutos: `~/snyk-violations/sast/flext-sh__flext-db-oracle.sast.json`


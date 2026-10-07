# FLEXT DB Oracle Examples

This directory contains the runnable example scripts currently shipped with
`flext-db-oracle`. The README intentionally stays close to the files that exist here so
the commands below remain accurate.

## Available Examples

### `ex_05_simple_working.py`

Minimal configuration example. It tries to load Oracle settings from the environment and
falls back to demo values when those variables are not present.

### `ex_06_cli.py`

CLI-oriented examples for `flext-oracle`. It can scaffold a local `.env` file with
sample variables and run a small command demo when the required Oracle environment is
configured.

### `ex_07_sqlalchemy2.py`

Minimal SQLAlchemy-oriented setup example showing how to build Oracle settings for
integration code.

## Running The Examples

```bash
cd examples

python ex_05_simple_working.py
python ex_06_cli.py
python ex_06_cli.py setup
python ex_06_cli.py demo
python ex_07_sqlalchemy2.py
```

## Environment Notes

For live Oracle-backed runs, configure the variables expected by the examples before
execution:

```bash
export FLEXT_TARGET_ORACLE_HOST=localhost
export FLEXT_TARGET_ORACLE_PORT=1521
export FLEXT_TARGET_ORACLE_SERVICE_NAME=XEPDB1
export FLEXT_TARGET_ORACLE_USERNAME=flext_user
export FLEXT_TARGET_ORACLE_PASSWORD=flext_password
```

`ex_05_simple_working.py` and `ex_07_sqlalchemy2.py` can still be inspected without a live
Oracle instance because they fall back to demo configuration values. `ex_06_cli.py demo`
expects the Oracle connection variables above to be set.

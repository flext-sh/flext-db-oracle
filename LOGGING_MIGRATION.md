# Logging Migration Report for flext-db-oracle

## Summary

Total files with logging imports: 14

## Files to Migrate

- `src/flext_db_oracle/utils/logger.py:5` - `import logging`
- `src/flext_db_oracle/connection/connection.py:5` - `import logging`
- `src/flext_db_oracle/connection/pool.py:5` - `import logging`
- `src/flext_db_oracle/schema/analyzer.py:5` - `import logging`
- `src/flext_db_oracle/schema/ddl.py:5` - `import logging`
- `src/flext_db_oracle/compare/comparator.py:5` - `import logging`
- `src/flext_db_oracle/compare/differ.py:5` - `import logging`
- `src/flext_db_oracle/compare/synchronizer.py:5` - `import logging`
- `src/flext_db_oracle/maintenance/health.py:5` - `import logging`
- `src/flext_db_oracle/maintenance/monitor.py:5` - `import logging`
- `src/flext_db_oracle/maintenance/optimizer.py:5` - `import logging`
- `src/flext_db_oracle/sql/optimizer.py:5` - `import logging`
- `src/flext_db_oracle/sql/parser.py:5` - `import logging`
- `src/flext_db_oracle/sql/validator.py:5` - `import logging`

## Migration Steps

1. Replace logging imports:

   ```python
   # Old
   import logging
   logger = logging.getLogger(__name__)

   # New
   from flext_observability.logging import get_logger
   logger = get_logger(__name__)
   ```

2. Add setup_logging to your main entry point:

   ```python
   from flext_observability import setup_logging

   setup_logging(
       service_name="flext-db-oracle",
       log_level="INFO",
       json_logs=True
   )
   ```

3. Update logging calls to use structured format:

   ```python
   # Old
   logger.info("Processing %s items", count)

   # New
   logger.info("Processing items", count=count)
   ```

See `examples/logging_migration.py` for a complete example.

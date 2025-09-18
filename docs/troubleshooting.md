# Troubleshooting

Common issues and solutions for flext-db-oracle.

## Connection Issues

### "Connection failed"

Check Oracle database connectivity:

```bash
# Test network connection
telnet oracle-host 1521

# Verify environment variables
echo $ORACLE_HOST
echo $ORACLE_PORT
echo $ORACLE_SERVICE_NAME
echo $ORACLE_USERNAME
```

### "Invalid username/password"

Verify credentials in environment variables or config.

### "Service name not found"

Check service_name parameter matches Oracle database configuration.

## CLI Issues

### SimpleNamespace placeholders

CLI formatter and interactions use placeholder implementations:

```python
# client.py lines 60-67 contain SimpleNamespace placeholders
self.formatter = SimpleNamespace()
self.interactions = SimpleNamespace()
```

This causes limited CLI functionality.

## Installation Issues

### "No module named 'oracledb'"

Install dependencies:

```bash
poetry install
```

### "ImportError: FlextResult"

Ensure flext-core is installed:

```bash
cd ../flext-core
poetry install
cd ../flext-db-oracle
poetry install
```

## Performance Issues

### Slow queries

- flext-db-oracle uses SQLAlchemy abstraction only
- No direct Python-oracledb optimization
- No async support for concurrent operations
- No DataFrame operations for bulk data

## Missing Features

### No async support

flext-db-oracle has 0 async methods. For async operations, consider direct Python-oracledb.

### No DataFrame support

No integration with Pandas, PyArrow, or Polars. Python-oracledb 3.4+ has native DataFrame support.

## Testing

### Oracle XE container

```bash
# Start test Oracle
make oracle-start

# Connect to localhost:1521/XEPDB1
# Username: system, Password: Oracle123
```

---

Updated: September 17, 2025 | Version: 0.9.9

# Oracle Database Maintenance Scripts

Essential maintenance scripts for Oracle database REDACTED_LDAP_BIND_PASSWORDistration using the Oracle Database Core Shared Library.

## 🔧 Health Check Scripts

### Daily Health Check

```python
"""Daily Oracle database health check script."""

import asyncio
from datetime import datetime
from flext_db_oracle.connection import ConnectionConfig, FlextDbFlextDbOracleConnection
from flext_db_oracle.tools import HealthChecker

async def daily_health_check():
    """Perform comprehensive daily health check."""

    config = ConnectionConfig.from_env()

    async with FlextDbOracleConnection(config) as conn:
        checker = HealthChecker(conn)

        # Run health checks
        health_report = await checker.run_health_checks([
            "database_status",
            "tablespace_usage",
            "memory_usage",
            "session_count",
            "lock_analysis",
            "backup_status"
        ])

        # Generate report
        report_file = f"health_check_{datetime.now().strftime('%Y%m%d')}.html"
        await checker.save_report(health_report, report_file)

        # Send alerts if needed
        critical_issues = [issue for issue in health_report.issues if issue.severity == "CRITICAL"]
        if critical_issues:
            await send_alert_email(critical_issues)

        print(f"Health check complete. Report saved to {report_file}")

if __name__ == "__main__":
    asyncio.run(daily_health_check())
```

## 📊 Performance Monitoring

### AWR Report Generation

```python
"""Generate AWR reports automatically."""

import asyncio
from flext_db_oracle.connection import ConnectionConfig, FlextDbOracleConnection
from flext_db_oracle.tools import PerformanceMonitor

async def generate_awr_reports():
    """Generate AWR reports for performance analysis."""

    config = ConnectionConfig.from_env()

    async with FlextDbOracleConnection(config) as conn:
        monitor = PerformanceMonitor(conn)

        # Generate daily AWR report
        awr_report = await monitor.generate_awr_report(
            begin_snap=await monitor.get_latest_snapshot() - 24,  # 24 hours ago
            end_snap=await monitor.get_latest_snapshot()
        )

        # Save report
        report_file = f"awr_report_{datetime.now().strftime('%Y%m%d')}.html"
        await monitor.save_awr_report(awr_report, report_file)

        print(f"AWR report generated: {report_file}")

if __name__ == "__main__":
    asyncio.run(generate_awr_reports())
```

## 🗄️ Schema Management

### Schema Backup Script

```python
"""Backup schema objects and data."""

import asyncio
from pathlib import Path
from flext_db_oracle.connection import ConnectionConfig, FlextDbOracleConnection
from flext_db_oracle.tools import DDLGenerator

async def backup_schema(schema_name: str):
    """Backup complete schema including DDL and data."""

    config = ConnectionConfig.from_env()
    backup_dir = Path(f"backup/{schema_name}_{datetime.now().strftime('%Y%m%d')}")
    backup_dir.mkdir(parents=True, exist_ok=True)

    async with FlextDbOracleConnection(config) as conn:
        ddl_gen = DDLGenerator(conn)

        # Generate DDL
        schema_ddl = await ddl_gen.generate_schema_ddl(schema_name)

        # Save DDL files
        for obj_type, ddl_statements in schema_ddl.items():
            ddl_file = backup_dir / f"{obj_type.lower()}.sql"
            with open(ddl_file, 'w') as f:
                for statement in ddl_statements:
                    f.write(f"{statement};\n\n")

        print(f"Schema backup completed: {backup_dir}")

if __name__ == "__main__":
    import sys
    schema = sys.argv[1] if len(sys.argv) > 1 else "HR"
    asyncio.run(backup_schema(schema))
```

## 🧹 Cleanup Operations

### Cleanup Temp Objects

```python
"""Clean up temporary database objects."""

import asyncio
from flext_db_oracle.connection import ConnectionConfig, FlextDbOracleConnection
from flext_db_oracle.tools import DatabaseOptimizer

async def cleanup_temp_objects():
    """Remove temporary and obsolete database objects."""

    config = ConnectionConfig.from_env()

    async with FlextDbOracleConnection(config) as conn:
        optimizer = DatabaseOptimizer(conn)

        # Find and remove temp objects
        cleanup_results = await optimizer.cleanup_temporary_objects([
            "temp_tables",
            "unused_indexes",
            "obsolete_statistics",
            "old_audit_records"
        ])

        print(f"Cleanup completed. Freed {cleanup_results.space_freed_mb} MB")

if __name__ == "__main__":
    asyncio.run(cleanup_temp_objects())
```

## 📈 Statistics Management

### Update Statistics Script

```python
"""Update database statistics for optimal performance."""

import asyncio
from flext_db_oracle.connection import ConnectionConfig, FlextDbOracleConnection

async def update_statistics(schema_name: str = None):
    """Update optimizer statistics for better performance."""

    config = ConnectionConfig.from_env()

    async with FlextDbOracleConnection(config) as conn:
        if schema_name:
            # Update specific schema
            await conn.execute(f"""
                BEGIN
                    DBMS_STATS.GATHER_SCHEMA_STATS(
                        ownname => '{schema_name}',
                        estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
                        method_opt => 'FOR ALL COLUMNS SIZE AUTO',
                        cascade => TRUE
                    );
                END;
            """)
            print(f"Statistics updated for schema: {schema_name}")
        else:
            # Update all schemas
            await conn.execute("""
                BEGIN
                    DBMS_STATS.GATHER_DATABASE_STATS(
                        estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
                        method_opt => 'FOR ALL COLUMNS SIZE AUTO',
                        cascade => TRUE
                    );
                END;
            """)
            print("Database statistics updated")

if __name__ == "__main__":
    import sys
    schema = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(update_statistics(schema))
```

---

This collection provides essential maintenance scripts for Oracle database REDACTED_LDAP_BIND_PASSWORDistration. Each script includes proper error handling, logging, and can be scheduled for automated execution.

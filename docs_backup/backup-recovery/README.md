# Oracle Database Backup and Recovery Guide

Comprehensive guide covering all aspects of Oracle Database backup and recovery, from basic strategies to advanced disaster recovery scenarios.

## 📋 Table of Contents

- [Backup and Recovery Overview](#backup-and-recovery-overview)
- [RMAN (Recovery Manager)](#rman-recovery-manager)
- [Backup Strategies](#backup-strategies)
- [Recovery Scenarios](#recovery-scenarios)
- [Data Guard](#data-guard)
- [Flashback Technologies](#flashback-technologies)
- [Point-in-Time Recovery](#point-in-time-recovery)
- [Disaster Recovery](#disaster-recovery)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🔄 Backup and Recovery Overview

### Backup Types

#### Physical Backups

- **Cold Backups**: Database shutdown during backup
- **Hot Backups**: Database online during backup
- **RMAN Backups**: Using Recovery Manager
- **Image Copies**: Exact copies of database files

#### Logical Backups

- **Data Pump Export**: Schema and table exports
- **Traditional Export**: Legacy export utility
- **Flashback Export**: Point-in-time logical backup

### Recovery Types

#### Instance Recovery

- Automatic recovery after instance crash
- Uses redo logs and undo data
- No DBA intervention required

#### Media Recovery

- Recovery from disk failure
- Uses backup files and archived logs
- Requires DBA intervention

#### Point-in-Time Recovery

- Recovery to specific time/SCN
- Uses backup and archived logs
- May result in data loss

## 🛠️ RMAN (Recovery Manager)

### RMAN Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RMAN Architecture                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │    RMAN     │    │   Target    │    │   Recovery  │     │
│  │  Executable │───▶│  Database   │    │   Catalog   │     │
│  │             │    │             │    │ (Optional)  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │          │
│         │                   ▼                   │          │
│         │            ┌─────────────┐            │          │
│         │            │ Control File│            │          │
│         │            │  Repository │            │          │
│         │            └─────────────┘            │          │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Media     │    │   Server    │    │  Auxiliary  │     │
│  │ Management  │    │  Processes  │    │  Database   │     │
│  │    Layer    │    │             │    │             │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                                                  │
│         ▼                                                  │
│  ┌─────────────┐                                          │
│  │   Backup    │                                          │
│  │   Storage   │                                          │
│  │             │                                          │
│  └─────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
```

### RMAN Configuration

#### Initial RMAN Setup

```bash
# Connect to RMAN
rman target /

# Configure backup retention policy
CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF 30 DAYS;

# Configure backup optimization
CONFIGURE BACKUP OPTIMIZATION ON;

# Configure compression
CONFIGURE COMPRESSION ALGORITHM 'MEDIUM';

# Configure encryption
CONFIGURE ENCRYPTION FOR DATABASE ON;
CONFIGURE ENCRYPTION ALGORITHM 'AES256';

# Configure parallelism
CONFIGURE DEVICE TYPE DISK PARALLELISM 4;

# Configure backup location
CONFIGURE CHANNEL DEVICE TYPE DISK FORMAT '/backup/rman/%U';

# Configure controlfile autobackup
CONFIGURE CONTROLFILE AUTOBACKUP ON;
CONFIGURE CONTROLFILE AUTOBACKUP FORMAT FOR DEVICE TYPE DISK TO '/backup/rman/cf_%F';

# Configure archive log deletion policy
CONFIGURE ARCHIVELOG DELETION POLICY TO APPLIED ON ALL STANDBY;
```

#### Recovery Catalog Setup

```sql
-- Create recovery catalog database
CREATE USER rman_catalog IDENTIFIED BY "CatalogPassword123!"
DEFAULT TABLESPACE rman_ts
TEMPORARY TABLESPACE temp
QUOTA UNLIMITED ON rman_ts;

GRANT RECOVERY_CATALOG_OWNER TO rman_catalog;

-- Connect to catalog and create
rman catalog rman_catalog/CatalogPassword123!@catalog_db

CREATE CATALOG;

-- Register target database
rman target / catalog rman_catalog/CatalogPassword123!@catalog_db

REGISTER DATABASE;
```

### RMAN Backup Operations

#### Full Database Backup

```bash
# Full database backup
BACKUP DATABASE PLUS ARCHIVELOG;

# Full database backup with compression
BACKUP AS COMPRESSED BACKUPSET DATABASE PLUS ARCHIVELOG;

# Full database backup to specific location
BACKUP DATABASE FORMAT '/backup/rman/full_%U' PLUS ARCHIVELOG;

# Full database backup with encryption
BACKUP AS COMPRESSED BACKUPSET ENCRYPTED BY PASSWORD "BackupPassword123!"
DATABASE PLUS ARCHIVELOG;
```

#### Incremental Backups

```bash
# Level 0 incremental backup (equivalent to full backup)
BACKUP INCREMENTAL LEVEL 0 DATABASE;

# Level 1 differential incremental backup
BACKUP INCREMENTAL LEVEL 1 DATABASE;

# Level 1 cumulative incremental backup
BACKUP INCREMENTAL LEVEL 1 CUMULATIVE DATABASE;

# Block change tracking for faster incrementals
ALTER DATABASE ENABLE BLOCK CHANGE TRACKING
USING FILE '/opt/oracle/oradata/change_tracking.f';
```

#### Tablespace and Datafile Backups

```bash
# Backup specific tablespace
BACKUP TABLESPACE users, temp;

# Backup specific datafile
BACKUP DATAFILE 4, 5, 6;

# Backup tablespace with archivelog
BACKUP TABLESPACE users PLUS ARCHIVELOG;

# Backup read-only tablespaces
BACKUP TABLESPACE readonly_data SKIP READONLY;
```

#### Archive Log Backups

```bash
# Backup all archive logs
BACKUP ARCHIVELOG ALL;

# Backup archive logs from specific time
BACKUP ARCHIVELOG FROM TIME 'SYSDATE-1';

# Backup and delete archive logs
BACKUP ARCHIVELOG ALL DELETE INPUT;

# Backup archive logs to multiple locations
BACKUP ARCHIVELOG ALL FORMAT '/backup/arch1/%U', '/backup/arch2/%U';
```

### RMAN Restore and Recovery

#### Complete Database Recovery

```bash
# Startup mount for restore
STARTUP MOUNT;

# Restore and recover database
RESTORE DATABASE;
RECOVER DATABASE;

# Open database
ALTER DATABASE OPEN;

# Restore and recover with archive logs
RESTORE DATABASE;
RECOVER DATABASE USING BACKUP CONTROLFILE;
ALTER DATABASE OPEN RESETLOGS;
```

#### Tablespace Recovery

```bash
# Take tablespace offline
ALTER TABLESPACE users OFFLINE IMMEDIATE;

# Restore and recover tablespace
RESTORE TABLESPACE users;
RECOVER TABLESPACE users;

# Bring tablespace online
ALTER TABLESPACE users ONLINE;
```

#### Datafile Recovery

```bash
# Take datafile offline
ALTER DATABASE DATAFILE '/opt/oracle/oradata/users01.dbf' OFFLINE;

# Restore and recover datafile
RESTORE DATAFILE '/opt/oracle/oradata/users01.dbf';
RECOVER DATAFILE '/opt/oracle/oradata/users01.dbf';

# Bring datafile online
ALTER DATABASE DATAFILE '/opt/oracle/oradata/users01.dbf' ONLINE;
```

#### Point-in-Time Recovery

```bash
# Restore database to specific time
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;

RESTORE DATABASE UNTIL TIME "TO_DATE('2024-01-15 14:30:00', 'YYYY-MM-DD HH24:MI:SS')";
RECOVER DATABASE UNTIL TIME "TO_DATE('2024-01-15 14:30:00', 'YYYY-MM-DD HH24:MI:SS')";

ALTER DATABASE OPEN RESETLOGS;

# Restore to specific SCN
RESTORE DATABASE UNTIL SCN 1234567;
RECOVER DATABASE UNTIL SCN 1234567;
ALTER DATABASE OPEN RESETLOGS;
```

### RMAN Maintenance

#### Backup Validation

```bash
# Validate all backups
VALIDATE BACKUPSET ALL;

# Check database for corruption
BACKUP VALIDATE DATABASE;

# Validate specific backup piece
VALIDATE BACKUPPIECE '/backup/rman/backup_piece_name';

# Check for block corruption
BACKUP VALIDATE CHECK LOGICAL DATABASE;
```

#### Backup Cleanup

```bash
# Delete obsolete backups based on retention policy
DELETE OBSOLETE;

# Delete expired backups
DELETE EXPIRED BACKUP;

# Delete specific backup
DELETE BACKUPSET 123;

# Cross-check backups
CROSSCHECK BACKUP;
CROSSCHECK ARCHIVELOG ALL;

# List backup information
LIST BACKUP SUMMARY;
LIST ARCHIVELOG ALL;
LIST INCARNATION;
```

## 📊 Backup Strategies

### Full Backup Strategy

```bash
#!/bin/bash
# Full backup script

export ORACLE_SID=ORCL
export ORACLE_HOME=/opt/oracle/product/19c
export PATH=$ORACLE_HOME/bin:$PATH

rman target / << EOF
CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF 30 DAYS;
CONFIGURE BACKUP OPTIMIZATION ON;
CONFIGURE COMPRESSION ALGORITHM 'MEDIUM';
CONFIGURE DEVICE TYPE DISK PARALLELISM 4;
CONFIGURE CONTROLFILE AUTOBACKUP ON;

BACKUP AS COMPRESSED BACKUPSET
DATABASE
PLUS ARCHIVELOG
FORMAT '/backup/rman/full_%d_%T_%s_%p'
TAG 'FULL_BACKUP';

DELETE OBSOLETE;
CROSSCHECK BACKUP;
EXIT;
EOF
```

### Incremental Backup Strategy

```bash
#!/bin/bash
# Incremental backup strategy

# Sunday - Level 0 backup
if [ $(date +%u) -eq 7 ]; then
    BACKUP_LEVEL=0
    TAG='LEVEL0_BACKUP'
else
    BACKUP_LEVEL=1
    TAG='LEVEL1_BACKUP'
fi

rman target / << EOF
BACKUP INCREMENTAL LEVEL $BACKUP_LEVEL
AS COMPRESSED BACKUPSET
DATABASE
FORMAT '/backup/rman/inc_${BACKUP_LEVEL}_%d_%T_%s_%p'
TAG '$TAG';

BACKUP ARCHIVELOG ALL
DELETE INPUT
FORMAT '/backup/rman/arch_%d_%T_%s_%p';

DELETE OBSOLETE;
EXIT;
EOF
```

### Hot Backup Strategy (Without RMAN)

```sql
-- Put tablespaces in backup mode
ALTER TABLESPACE system BEGIN BACKUP;
-- Copy datafile at OS level
-- cp /opt/oracle/oradata/system01.dbf /backup/hot/
ALTER TABLESPACE system END BACKUP;

-- Repeat for all tablespaces
ALTER TABLESPACE users BEGIN BACKUP;
-- Copy users datafiles
ALTER TABLESPACE users END BACKUP;

-- Backup control file
ALTER DATABASE BACKUP CONTROLFILE TO '/backup/hot/control.ctl';

-- Backup archive logs
-- Copy all archive log files to backup location
```

## 🔧 Recovery Scenarios

### Complete Database Loss

```bash
# 1. Restore SPFILE
RESTORE SPFILE FROM AUTOBACKUP;

# 2. Start instance with restored SPFILE
STARTUP NOMOUNT;

# 3. Restore control file
RESTORE CONTROLFILE FROM AUTOBACKUP;

# 4. Mount database
ALTER DATABASE MOUNT;

# 5. Restore database
RESTORE DATABASE;

# 6. Recover database
RECOVER DATABASE;

# 7. Open database
ALTER DATABASE OPEN RESETLOGS;
```

### Control File Loss

```bash
# If one control file is lost (and you have multiple copies)
SHUTDOWN IMMEDIATE;
# Copy good control file to replace lost one
cp /opt/oracle/oradata/control01.ctl /opt/oracle/oradata/control02.ctl
STARTUP;

# If all control files are lost
STARTUP NOMOUNT;
RESTORE CONTROLFILE FROM AUTOBACKUP;
ALTER DATABASE MOUNT;
RECOVER DATABASE USING BACKUP CONTROLFILE;
ALTER DATABASE OPEN RESETLOGS;
```

### Redo Log File Loss

```sql
-- If inactive redo log is lost
ALTER DATABASE DROP LOGFILE GROUP 2;
ALTER DATABASE ADD LOGFILE GROUP 2
    ('/opt/oracle/oradata/redo02a.log', '/opt/oracle/oradata/redo02b.log')
    SIZE 100M;

-- If current redo log is lost (may cause data loss)
SHUTDOWN ABORT;
STARTUP MOUNT;
RECOVER DATABASE UNTIL CANCEL;
-- Type CANCEL
ALTER DATABASE OPEN RESETLOGS;
```

### Temporary File Loss

```sql
-- Drop and recreate temporary tablespace
DROP TABLESPACE temp INCLUDING CONTENTS AND DATAFILES;

CREATE TEMPORARY TABLESPACE temp
TEMPFILE '/opt/oracle/oradata/temp01.dbf' SIZE 500M AUTOEXTEND ON;

-- Set as default temporary tablespace
ALTER DATABASE DEFAULT TEMPORARY TABLESPACE temp;
```

### System Tablespace Corruption

```bash
# Restore and recover SYSTEM tablespace
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;

RESTORE TABLESPACE system;
RECOVER TABLESPACE system;

ALTER DATABASE OPEN;
```

## 🔄 Data Guard

### Data Guard Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Data Guard Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                ┌─────────────────┐     │
│  │   Primary       │                │    Standby      │     │
│  │   Database      │                │   Database      │     │
│  │                 │                │                 │     │
│  │  ┌───────────┐  │   Redo Data   │  ┌───────────┐  │     │
│  │  │   LGWR    │  │──────────────▶│  │    RFS    │  │     │
│  │  └───────────┘  │               │  └───────────┘  │     │
│  │                 │               │         │       │     │
│  │  ┌───────────┐  │               │         ▼       │     │
│  │  │   ARCH    │  │──────────────▶│  ┌───────────┐  │     │
│  │  └───────────┘  │  Archive Logs │  │    MRP    │  │     │
│  │                 │               │  └───────────┘  │     │
│  └─────────────────┘               └─────────────────┘     │
│                                                             │
│  ┌─────────────────┐                                       │
│  │   Data Guard    │                                       │
│  │     Broker      │                                       │
│  │                 │                                       │
│  │  ┌───────────┐  │                                       │
│  │  │   DMON    │  │                                       │
│  │  └───────────┘  │                                       │
│  └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

### Physical Standby Setup

#### Primary Database Configuration

```sql
-- Enable archiving
ALTER DATABASE ARCHIVELOG;

-- Set archive log destination
ALTER SYSTEM SET log_archive_dest_1 =
    'LOCATION=/opt/oracle/archive VALID_FOR=(ALL_LOGFILES,ALL_ROLES) DB_UNIQUE_NAME=primary';

ALTER SYSTEM SET log_archive_dest_2 =
    'SERVICE=standby LGWR ASYNC VALID_FOR=(ONLINE_LOGFILES,PRIMARY_ROLE) DB_UNIQUE_NAME=standby';

-- Set archive log format
ALTER SYSTEM SET log_archive_format = 'arch_%t_%s_%r.arc';

-- Enable force logging
ALTER DATABASE FORCE LOGGING;

-- Set standby file management
ALTER SYSTEM SET standby_file_management = AUTO;

-- Configure redo transport
ALTER SYSTEM SET log_archive_config = 'DG_CONFIG=(primary,standby)';
ALTER SYSTEM SET log_archive_max_processes = 4;

-- Set FAL (Fetch Archive Log) parameters
ALTER SYSTEM SET fal_server = standby;
ALTER SYSTEM SET fal_client = primary;
```

#### Standby Database Creation

```bash
# 1. Create parameter file for standby
# Copy primary pfile and modify:
*.db_name='ORCL'
*.db_unique_name='standby'
*.log_archive_config='DG_CONFIG=(primary,standby)'
*.log_archive_dest_1='LOCATION=/opt/oracle/archive VALID_FOR=(ALL_LOGFILES,ALL_ROLES) DB_UNIQUE_NAME=standby'
*.log_archive_dest_2='SERVICE=primary LGWR ASYNC VALID_FOR=(ONLINE_LOGFILES,PRIMARY_ROLE) DB_UNIQUE_NAME=primary'
*.fal_server=primary
*.fal_client=standby
*.standby_file_management=AUTO

# 2. Create standby database using RMAN
rman target sys/password@primary auxiliary sys/password@standby

DUPLICATE TARGET DATABASE
  FOR STANDBY
  FROM ACTIVE DATABASE
  DORECOVER
  SPFILE
    SET db_unique_name='standby'
    SET log_archive_dest_1='LOCATION=/opt/oracle/archive VALID_FOR=(ALL_LOGFILES,ALL_ROLES) DB_UNIQUE_NAME=standby'
    SET log_archive_dest_2='SERVICE=primary LGWR ASYNC VALID_FOR=(ONLINE_LOGFILES,PRIMARY_ROLE) DB_UNIQUE_NAME=primary'
    SET fal_server='primary'
    SET fal_client='standby'
  NOFILENAMECHECK;
```

#### Starting Standby Database

```sql
-- Start standby in mount mode
STARTUP MOUNT;

-- Start managed recovery
ALTER DATABASE RECOVER MANAGED STANDBY DATABASE DISCONNECT FROM SESSION;

-- Check standby status
SELECT process, status, thread#, sequence#, block#, blocks
FROM v$managed_standby;
```

### Logical Standby Setup

#### Convert Physical to Logical Standby

```sql
-- On primary database
EXEC DBMS_LOGSTDBY.BUILD;

-- On standby database (stop managed recovery first)
ALTER DATABASE RECOVER MANAGED STANDBY DATABASE CANCEL;

-- Convert to logical standby
ALTER DATABASE RECOVER TO LOGICAL STANDBY standby_db;

-- Open logical standby
ALTER DATABASE OPEN;

-- Start logical standby apply
ALTER DATABASE START LOGICAL STANDBY APPLY;
```

### Data Guard Broker

#### Broker Configuration

```sql
-- Enable broker on primary
ALTER SYSTEM SET dg_broker_start = TRUE;

-- Enable broker on standby
ALTER SYSTEM SET dg_broker_start = TRUE;

-- Connect to broker and create configuration
dgmgrl /

CREATE CONFIGURATION 'DGConfig' AS
  PRIMARY DATABASE IS 'primary' CONNECT IDENTIFIER IS primary;

ADD DATABASE 'standby' AS
  CONNECT IDENTIFIER IS standby
  MAINTAINED AS PHYSICAL;

ENABLE CONFIGURATION;

-- Show configuration
SHOW CONFIGURATION;
SHOW DATABASE primary;
SHOW DATABASE standby;
```

#### Switchover and Failover

```sql
-- Planned switchover
SWITCHOVER TO standby;

-- Emergency failover
FAILOVER TO standby;

-- Reinstate old primary as standby
REINSTATE DATABASE primary;
```

### Snapshot Standby

#### Create Snapshot Standby

```sql
-- Stop managed recovery
ALTER DATABASE RECOVER MANAGED STANDBY DATABASE CANCEL;

-- Convert to snapshot standby
ALTER DATABASE CONVERT TO SNAPSHOT STANDBY;

-- Open for read-write
ALTER DATABASE OPEN;

-- Perform testing...

-- Convert back to physical standby
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE CONVERT TO PHYSICAL STANDBY;
ALTER DATABASE RECOVER MANAGED STANDBY DATABASE DISCONNECT FROM SESSION;
```

## ⚡ Flashback Technologies

### Flashback Database

#### Configuration

```sql
-- Set flashback retention target
ALTER SYSTEM SET db_flashback_retention_target = 1440; -- 24 hours

-- Set recovery area
ALTER SYSTEM SET db_recovery_file_dest = '/opt/oracle/fast_recovery_area';
ALTER SYSTEM SET db_recovery_file_dest_size = 10G;

-- Enable flashback database
ALTER DATABASE FLASHBACK ON;

-- Check flashback status
SELECT flashback_on FROM v$database;
SELECT oldest_flashback_scn, oldest_flashback_time
FROM v$flashback_database_log;
```

#### Flashback Database Operations

```sql
-- Flashback database to specific time
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;

FLASHBACK DATABASE TO TIMESTAMP
    TO_TIMESTAMP('2024-01-15 14:30:00', 'YYYY-MM-DD HH24:MI:SS');

ALTER DATABASE OPEN RESETLOGS;

-- Flashback database to SCN
FLASHBACK DATABASE TO SCN 1234567;
ALTER DATABASE OPEN RESETLOGS;

-- Flashback database to restore point
CREATE RESTORE POINT before_upgrade GUARANTEE FLASHBACK DATABASE;
-- Perform upgrade...
-- If upgrade fails:
FLASHBACK DATABASE TO RESTORE POINT before_upgrade;
```

### Flashback Table

#### Table-Level Flashback

```sql
-- Enable row movement
ALTER TABLE employees ENABLE ROW MOVEMENT;

-- Flashback table to specific time
FLASHBACK TABLE employees TO TIMESTAMP
    TO_TIMESTAMP('2024-01-15 14:30:00', 'YYYY-MM-DD HH24:MI:SS');

-- Flashback table to SCN
FLASHBACK TABLE employees TO SCN 1234567;

-- Flashback table to restore point
CREATE RESTORE POINT before_delete;
-- Perform delete operations...
FLASHBACK TABLE employees TO RESTORE POINT before_delete;
```

### Flashback Query

#### Query Historical Data

```sql
-- Query data as of specific time
SELECT * FROM employees
AS OF TIMESTAMP TO_TIMESTAMP('2024-01-15 14:30:00', 'YYYY-MM-DD HH24:MI:SS')
WHERE department_id = 10;

-- Query data as of SCN
SELECT * FROM employees AS OF SCN 1234567
WHERE employee_id = 100;

-- Compare current and historical data
SELECT current.employee_id,
       current.salary as current_salary,
       historical.salary as historical_salary,
       current.salary - historical.salary as salary_change
FROM employees current,
     employees AS OF TIMESTAMP TO_TIMESTAMP('2024-01-01', 'YYYY-MM-DD') historical
WHERE current.employee_id = historical.employee_id
  AND current.salary != historical.salary;
```

### Flashback Drop (Recycle Bin)

#### Recycle Bin Operations

```sql
-- Show dropped objects
SHOW RECYCLEBIN;

-- Flashback dropped table
FLASHBACK TABLE employees TO BEFORE DROP;

-- Flashback with rename
FLASHBACK TABLE employees TO BEFORE DROP RENAME TO employees_recovered;

-- Purge recycle bin
PURGE RECYCLEBIN;

-- Purge specific object
PURGE TABLE employees;

-- Disable recycle bin
ALTER SYSTEM SET recyclebin = OFF;
```

## 🚨 Disaster Recovery

### Disaster Recovery Planning

#### Recovery Time Objective (RTO)

- **Definition**: Maximum acceptable downtime
- **Factors**: Business requirements, infrastructure, procedures
- **Measurement**: Time from disaster to full service restoration

#### Recovery Point Objective (RPO)

- **Definition**: Maximum acceptable data loss
- **Factors**: Backup frequency, replication lag, business tolerance
- **Measurement**: Time between last backup and disaster

### Disaster Recovery Strategies

#### Cold Site Strategy

```bash
# Characteristics:
# - Lowest cost option
# - Longest recovery time
# - Requires full restore from backup

# Recovery procedure:
# 1. Procure and setup hardware
# 2. Install Oracle software
# 3. Restore database from backup
# 4. Apply archive logs
# 5. Open database
```

#### Hot Site Strategy

```sql
-- Characteristics:
-- - Highest cost option
-- - Shortest recovery time
-- - Uses Data Guard standby database

-- Recovery procedure:
-- 1. Failover to standby database
FAILOVER TO standby;

-- 2. Redirect application connections
-- 3. Validate data integrity
-- 4. Resume business operations
```

#### Warm Site Strategy

```bash
# Characteristics:
# - Moderate cost option
# - Moderate recovery time
# - Uses recent backups and archive shipping

# Recovery procedure:
# 1. Restore latest backup
# 2. Apply shipped archive logs
# 3. Perform incomplete recovery if needed
# 4. Open database with RESETLOGS
```

### Cross-Platform Disaster Recovery

#### RMAN Cross-Platform Backup

```bash
# Create cross-platform backup
RMAN> CONVERT DATABASE NEW DATABASE 'target_db'
      TRANSPORT SCRIPT '/backup/transport_script.sql'
      TO PLATFORM 'Linux x86 64-bit'
      DB_FILE_NAME_CONVERT '/source/path', '/target/path';
```

#### Data Pump Cross-Platform Export

```bash
# Full database export
expdp system/password FULL=Y DIRECTORY=dp_dir DUMPFILE=full_db.dmp
      LOGFILE=full_db.log COMPRESSION=ALL

# Import on target platform
impdp system/password FULL=Y DIRECTORY=dp_dir DUMPFILE=full_db.dmp
      LOGFILE=full_db_import.log REMAP_TABLESPACE=source_ts:target_ts
```

### Testing Disaster Recovery

#### DR Testing Checklist

1. **Backup Validation**
   - Verify backup integrity
   - Test restore procedures
   - Validate recovery time

2. **Failover Testing**
   - Test Data Guard switchover
   - Validate application connectivity
   - Measure failover time

3. **Failback Testing**
   - Test return to primary site
   - Validate data synchronization
   - Measure failback time

4. **Documentation Update**
   - Update procedures based on test results
   - Document lessons learned
   - Update contact information

## 📋 Best Practices

### Backup Best Practices

#### Strategy Guidelines

- **3-2-1 Rule**: 3 copies of data, 2 different media types, 1 offsite
- **Regular Testing**: Test restore procedures regularly
- **Automation**: Automate backup processes
- **Monitoring**: Monitor backup success/failure
- **Documentation**: Maintain current procedures

#### RMAN Best Practices

```bash
# Use block change tracking for faster incrementals
ALTER DATABASE ENABLE BLOCK CHANGE TRACKING;

# Configure appropriate parallelism
CONFIGURE DEVICE TYPE DISK PARALLELISM 4;

# Use backup compression
CONFIGURE COMPRESSION ALGORITHM 'MEDIUM';

# Enable backup optimization
CONFIGURE BACKUP OPTIMIZATION ON;

# Set appropriate retention policy
CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF 30 DAYS;

# Regular maintenance
DELETE OBSOLETE;
CROSSCHECK BACKUP;
VALIDATE BACKUPSET ALL;
```

### Recovery Best Practices

#### Preparation

- Maintain current documentation
- Practice recovery procedures
- Keep emergency contact list
- Maintain spare hardware inventory
- Document network configurations

#### Execution

- Follow documented procedures
- Validate each step before proceeding
- Maintain communication with stakeholders
- Document all actions taken
- Test database integrity after recovery

### Monitoring and Alerting

#### Backup Monitoring

```sql
-- Monitor backup status
SELECT session_key, input_type, status,
       start_time, end_time, elapsed_seconds
FROM v$rman_backup_job_details
WHERE start_time >= SYSDATE - 7
ORDER BY start_time DESC;

-- Check for backup failures
SELECT * FROM v$rman_backup_job_details
WHERE status = 'FAILED'
  AND start_time >= SYSDATE - 1;

-- Monitor archive log generation
SELECT sequence#, first_time, next_time,
       (next_time - first_time) * 24 * 60 as minutes_to_switch
FROM v$log_history
WHERE first_time >= SYSDATE - 1
ORDER BY first_time;
```

#### Alert Configuration

```sql
-- Set up email notifications for backup failures
-- (Implementation depends on your environment)

-- Monitor database alerts
SELECT message_type, message_level, host_id,
       module_id, message_text, originating_timestamp
FROM dba_outstanding_alerts
ORDER BY originating_timestamp DESC;
```

## 🔧 Troubleshooting

### Common Backup Issues

#### RMAN-20202: Tablespace doesn't exist

```bash
# Cause: Tablespace dropped but still referenced in backup script
# Solution: Update backup script or use dynamic SQL

# Check existing tablespaces
SELECT tablespace_name FROM dba_tablespaces;

# Use dynamic backup script
BACKUP TABLESPACE (SELECT tablespace_name FROM dba_tablespaces
                  WHERE status = 'ONLINE');
```

#### ORA-19809: Limit exceeded for recovery files

```sql
-- Cause: Recovery area full
-- Solution: Increase size or clean up old files

-- Check recovery area usage
SELECT * FROM v$recovery_area_usage;

-- Increase recovery area size
ALTER SYSTEM SET db_recovery_file_dest_size = 20G;

-- Clean up old backups
DELETE OBSOLETE;
DELETE EXPIRED BACKUP;
```

#### RMAN-06059: Expected archived log not found

```bash
# Cause: Missing archive log file
# Solution: Restore from backup or skip if acceptable

# Check for missing archive logs
CROSSCHECK ARCHIVELOG ALL;

# Restore missing archive logs
RESTORE ARCHIVELOG FROM SEQUENCE 100 UNTIL SEQUENCE 150;

# Skip missing logs (data loss possible)
RECOVER DATABASE UNTIL CANCEL;
```

### Common Recovery Issues

#### ORA-01194: File needs more recovery

```sql
-- Cause: Datafile is older than control file
-- Solution: Restore newer backup or use backup control file

-- Check file headers
SELECT file#, checkpoint_change#, checkpoint_time
FROM v$datafile_header;

SELECT checkpoint_change#, checkpoint_time
FROM v$database;

-- Use backup control file for recovery
RECOVER DATABASE USING BACKUP CONTROLFILE;
```

#### ORA-01547: Warning: RECOVER succeeded but OPEN RESETLOGS would fail

```sql
-- Cause: Online redo logs needed for recovery
-- Solution: Apply more redo or use RESETLOGS

-- Check redo log status
SELECT group#, status, archived, first_change#
FROM v$log;

-- Open with RESETLOGS (may cause data loss)
ALTER DATABASE OPEN RESETLOGS;
```

#### ORA-00283: Recovery session canceled due to errors

```bash
# Cause: Various recovery errors
# Solution: Check alert log and trace files

# Check alert log
tail -f $ORACLE_BASE/diag/rdbms/$ORACLE_SID/$ORACLE_SID/trace/alert_$ORACLE_SID.log

# Check for trace files
ls -lt $ORACLE_BASE/diag/rdbms/$ORACLE_SID/$ORACLE_SID/trace/

# Common solutions:
# - Restore missing files
# - Apply correct archive logs
# - Use backup control file
```

---

**Last Updated**: December 2024
**Version**: 1.0
**Maintainer**: Oracle Core Shared Team

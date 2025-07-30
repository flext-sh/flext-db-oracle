# Oracle Database Administration Guide

Comprehensive guide covering all aspects of Oracle Database REDACTED_LDAP_BIND_PASSWORDistration, from installation to advanced maintenance procedures.

## ðŸ"‹ Table of Contents

- [Database Installation](#database-installation)
- [Instance Management](#instance-management)
- [Storage Management](#storage-management)
- [User and Security Management](#user-and-security-management)
- [Performance Monitoring](#performance-monitoring)
- [Maintenance Tasks](#maintenance-tasks)
- [Troubleshooting](#troubleshooting)
- [Automation](#automation)
- [Best Practices](#best-practices)

## ðŸ"§ Database Installation

### Pre-Installation Requirements

#### System Requirements

```bash
# Check system resources
cat /proc/meminfo | grep MemTotal
df -h
cat /proc/cpuinfo | grep processor | wc -l

# Verify kernel parameters
cat /proc/sys/kernel/shmmax
cat /proc/sys/kernel/shmall
cat /proc/sys/kernel/shmmni
cat /proc/sys/fs/file-max

# Required packages (RHEL/CentOS)
yum install -y binutils compat-libcap1 compat-libstdc++-33 \
gcc gcc-c++ glibc glibc-devel ksh libaio libaio-devel \
libgcc libstdc++ libstdc++-devel libXi libXtst make sysstat
```

#### User and Group Creation

```bash
# Create Oracle groups
groupadd -g 54321 oinstall
groupadd -g 54322 dba
groupadd -g 54323 oper
groupadd -g 54324 backupdba
groupadd -g 54325 dgdba
groupadd -g 54326 kmdba
groupadd -g 54327 asmdba
groupadd -g 54328 asmoper
groupadd -g 54329 asmREDACTED_LDAP_BIND_PASSWORD

# Create Oracle user
useradd -u 54321 -g oinstall -G dba,oper,backupdba,dgdba,kmdba,asmdba oracle

# Set password
passwd oracle
```

#### Directory Structure

```bash
# Create Oracle directories
mkdir -p /opt/oracle/product/19c/dbhome_1
mkdir -p /opt/oracle/oradata
mkdir -p /opt/oracle/fast_recovery_area
mkdir -p /opt/oracle/REDACTED_LDAP_BIND_PASSWORD
mkdir -p /opt/oracle/audit

# Set ownership and permissions
chown -R oracle:oinstall /opt/oracle
chmod -R 775 /opt/oracle
```

### Silent Installation

#### Response File Configuration

```ini
# db_install.rsp
oracle.install.responseFileVersion=/oracle/install/rspfmt_dbinstall_response_schema_v19.0.0
oracle.install.option=INSTALL_DB_SWONLY
UNIX_GROUP_NAME=oinstall
INVENTORY_LOCATION=/opt/oracle/oraInventory
ORACLE_HOME=/opt/oracle/product/19c/dbhome_1
ORACLE_BASE=/opt/oracle
oracle.install.db.InstallEdition=EE
oracle.install.db.OSDBA_GROUP=dba
oracle.install.db.OSOPER_GROUP=oper
oracle.install.db.OSBACKUPDBA_GROUP=backupdba
oracle.install.db.OSDGDBA_GROUP=dgdba
oracle.install.db.OSKMDBA_GROUP=kmdba
oracle.install.db.OSRACDBA_GROUP=dba
SECURITY_UPDATES_VIA_MYORACLE_SUPPORT=false
DECLINE_SECURITY_UPDATES=true
```

#### Installation Execution

```bash
# Run installer in silent mode
./runInstaller -silent -responseFile /tmp/db_install.rsp

# Run root scripts
/opt/oracle/oraInventory/orainstRoot.sh
/opt/oracle/product/19c/dbhome_1/root.sh
```

### Database Creation

#### DBCA Silent Creation

```bash
# Create database using DBCA
dbca -silent -createDatabase \
  -templateName General_Purpose.dbc \
  -gdbname ORCL \
  -sid ORCL \
  -responseFile NO_VALUE \
  -characterSet AL32UTF8 \
  -sysPassword SysPassword123 \
  -systemPassword SystemPassword123 \
  -createAsContainerDatabase true \
  -numberOfPDBs 1 \
  -pdbName PDB1 \
  -pdbAdminPassword PdbPassword123 \
  -databaseType MULTIPURPOSE \
  -memoryMgmtType auto_sga \
  -totalMemory 2048 \
  -storageType FS \
  -datafileDestination /opt/oracle/oradata \
  -redoLogFileSize 50 \
  -emConfiguration NONE \
  -ignorePreReqs
```

#### Manual Database Creation

```sql
-- Create parameter file
CREATE SPFILE='/opt/oracle/product/19c/dbhome_1/dbs/spfileORCL.ora' FROM PFILE;

-- Start instance
STARTUP NOMOUNT;

-- Create database
CREATE DATABASE ORCL
USER SYS IDENTIFIED BY SysPassword123
USER SYSTEM IDENTIFIED BY SystemPassword123
LOGFILE GROUP 1 ('/opt/oracle/oradata/ORCL/redo01.log') SIZE 50M,
        GROUP 2 ('/opt/oracle/oradata/ORCL/redo02.log') SIZE 50M,
        GROUP 3 ('/opt/oracle/oradata/ORCL/redo03.log') SIZE 50M
MAXLOGFILES 16
MAXLOGMEMBERS 3
MAXLOGHISTORY 1800
MAXDATAFILES 1024
MAXINSTANCES 8
CHARACTER SET AL32UTF8
NATIONAL CHARACTER SET AL16UTF16
DATAFILE '/opt/oracle/oradata/ORCL/system01.dbf' SIZE 700M REUSE AUTOEXTEND ON NEXT 10240K MAXSIZE UNLIMITED
EXTENT MANAGEMENT LOCAL
SYSAUX DATAFILE '/opt/oracle/oradata/ORCL/sysaux01.dbf' SIZE 550M REUSE AUTOEXTEND ON NEXT 10240K MAXSIZE UNLIMITED
DEFAULT TABLESPACE users
   DATAFILE '/opt/oracle/oradata/ORCL/users01.dbf'
   SIZE 500M REUSE AUTOEXTEND ON MAXSIZE UNLIMITED
DEFAULT TEMPORARY TABLESPACE tempts1
   TEMPFILE '/opt/oracle/oradata/ORCL/temp01.dbf'
   SIZE 20M REUSE AUTOEXTEND ON NEXT 640K MAXSIZE UNLIMITED
UNDO TABLESPACE undotbs1
   DATAFILE '/opt/oracle/oradata/ORCL/undotbs01.dbf'
   SIZE 200M REUSE AUTOEXTEND ON NEXT 5120K MAXSIZE UNLIMITED;

-- Run catalog scripts
@$ORACLE_HOME/rdbms/REDACTED_LDAP_BIND_PASSWORD/catalog.sql
@$ORACLE_HOME/rdbms/REDACTED_LDAP_BIND_PASSWORD/catproc.sql
```

## âš™ï¸ Instance Management

### Startup and Shutdown

#### Startup Modes

```sql
-- Start instance only (NOMOUNT)
STARTUP NOMOUNT;

-- Mount database
ALTER DATABASE MOUNT;

-- Open database
ALTER DATABASE OPEN;

-- Combined startup
STARTUP; -- Equivalent to NOMOUNT + MOUNT + OPEN

-- Force startup
STARTUP FORCE;

-- Restricted mode
STARTUP RESTRICT;

-- Read-only mode
STARTUP MOUNT;
ALTER DATABASE OPEN READ ONLY;
```

#### Shutdown Modes

```sql
-- Normal shutdown (wait for users to disconnect)
SHUTDOWN NORMAL;

-- Immediate shutdown (disconnect users, rollback transactions)
SHUTDOWN IMMEDIATE;

-- Transactional shutdown (wait for transactions to complete)
SHUTDOWN TRANSACTIONAL;

-- Abort shutdown (emergency shutdown)
SHUTDOWN ABORT;
```

### Parameter Management

#### SPFILE Management

```sql
-- Create SPFILE from PFILE
CREATE SPFILE FROM PFILE;

-- Create SPFILE with specific location
CREATE SPFILE='/opt/oracle/product/19c/dbhome_1/dbs/spfileORCL.ora'
FROM PFILE='/tmp/initORCL.ora';

-- Create PFILE from SPFILE
CREATE PFILE FROM SPFILE;

-- View parameter source
SELECT name, value, isdefault, ismodified, issys_modifiable
FROM v$parameter
WHERE name = 'sga_target';
```

#### Parameter Modification

```sql
-- Modify parameter in memory only
ALTER SYSTEM SET sga_target = 1G SCOPE = MEMORY;

-- Modify parameter in SPFILE only
ALTER SYSTEM SET sga_target = 1G SCOPE = SPFILE;

-- Modify parameter in both (default)
ALTER SYSTEM SET sga_target = 1G SCOPE = BOTH;

-- Session-level parameter
ALTER SESSION SET sort_area_size = 1048576;

-- Reset parameter to default
ALTER SYSTEM RESET sga_target SCOPE = SPFILE;
```

### Memory Management

#### Automatic Memory Management (AMM)

```sql
-- Enable AMM
ALTER SYSTEM SET memory_target = 2G;
ALTER SYSTEM SET memory_max_target = 4G;

-- Disable individual component sizing when using AMM
ALTER SYSTEM SET sga_target = 0;
ALTER SYSTEM SET pga_aggregate_target = 0;
```

#### Automatic Shared Memory Management (ASMM)

```sql
-- Enable ASMM for SGA
ALTER SYSTEM SET sga_target = 1G;
ALTER SYSTEM SET sga_max_size = 2G;

-- Individual SGA components (set to 0 for automatic)
ALTER SYSTEM SET shared_pool_size = 0;
ALTER SYSTEM SET db_cache_size = 0;
ALTER SYSTEM SET large_pool_size = 0;
ALTER SYSTEM SET java_pool_size = 0;

-- PGA management
ALTER SYSTEM SET pga_aggregate_target = 500M;
```

#### Manual Memory Management

```sql
-- Set individual SGA components
ALTER SYSTEM SET shared_pool_size = 400M;
ALTER SYSTEM SET db_cache_size = 800M;
ALTER SYSTEM SET large_pool_size = 64M;
ALTER SYSTEM SET java_pool_size = 32M;
ALTER SYSTEM SET log_buffer = 16M;

-- Disable automatic management
ALTER SYSTEM SET sga_target = 0;
ALTER SYSTEM SET memory_target = 0;
```

### Process Management

#### Background Process Monitoring

```sql
-- View background processes
SELECT paddr, name, description
FROM v$bgprocess
WHERE paddr != '00'
ORDER BY name;

-- Check process status
SELECT program, spid, username, terminal
FROM v$process
WHERE program LIKE '%ORACLE%'
ORDER BY program;

-- Monitor session information
SELECT sid, serial#, username, program, machine, status
FROM v$session
WHERE type = 'USER'
ORDER BY username;
```

#### Session Management

```sql
-- Kill session
ALTER SYSTEM KILL SESSION 'sid,serial#' IMMEDIATE;

-- Disconnect session
ALTER SYSTEM DISCONNECT SESSION 'sid,serial#' POST_TRANSACTION;

-- Set resource limits
ALTER PROFILE default LIMIT
    SESSIONS_PER_USER 3
    CPU_PER_SESSION 10000
    CONNECT_TIME 600
    IDLE_TIME 30;
```

## ðŸ'¾ Storage Management

### Tablespace Management

#### Creating Tablespaces

```sql
-- Create permanent tablespace
CREATE TABLESPACE sales_data
DATAFILE '/opt/oracle/oradata/ORCL/sales_data01.dbf' SIZE 100M
AUTOEXTEND ON NEXT 10M MAXSIZE 1G
EXTENT MANAGEMENT LOCAL
SEGMENT SPACE MANAGEMENT AUTO;

-- Create temporary tablespace
CREATE TEMPORARY TABLESPACE temp_large
TEMPFILE '/opt/oracle/oradata/ORCL/temp_large01.dbf' SIZE 500M
AUTOEXTEND ON NEXT 50M MAXSIZE 2G;

-- Create undo tablespace
CREATE UNDO TABLESPACE undotbs2
DATAFILE '/opt/oracle/oradata/ORCL/undotbs02.dbf' SIZE 100M
AUTOEXTEND ON NEXT 10M MAXSIZE 1G;

-- Create bigfile tablespace
CREATE BIGFILE TABLESPACE big_data
DATAFILE '/opt/oracle/oradata/ORCL/big_data01.dbf' SIZE 1G
AUTOEXTEND ON NEXT 100M MAXSIZE 32G;
```

#### Tablespace Maintenance

```sql
-- Add datafile to tablespace
ALTER TABLESPACE sales_data
ADD DATAFILE '/opt/oracle/oradata/ORCL/sales_data02.dbf' SIZE 100M;

-- Resize datafile
ALTER DATABASE DATAFILE '/opt/oracle/oradata/ORCL/sales_data01.dbf' RESIZE 200M;

-- Enable/disable autoextend
ALTER DATABASE DATAFILE '/opt/oracle/oradata/ORCL/sales_data01.dbf'
AUTOEXTEND ON NEXT 10M MAXSIZE 500M;

-- Take tablespace offline/online
ALTER TABLESPACE sales_data OFFLINE;
ALTER TABLESPACE sales_data ONLINE;

-- Make tablespace read-only
ALTER TABLESPACE sales_data READ ONLY;
ALTER TABLESPACE sales_data READ WRITE;

-- Drop tablespace
DROP TABLESPACE sales_data INCLUDING CONTENTS AND DATAFILES;
```

#### Space Monitoring

```sql
-- Tablespace usage
SELECT t.tablespace_name,
       t.total_mb,
       f.free_mb,
       t.total_mb - f.free_mb as used_mb,
       ROUND((t.total_mb - f.free_mb) / t.total_mb * 100, 2) as pct_used
FROM (SELECT tablespace_name, ROUND(SUM(bytes)/1024/1024, 2) as total_mb
      FROM dba_data_files GROUP BY tablespace_name) t,
     (SELECT tablespace_name, ROUND(SUM(bytes)/1024/1024, 2) as free_mb
      FROM dba_free_space GROUP BY tablespace_name) f
WHERE t.tablespace_name = f.tablespace_name
ORDER BY pct_used DESC;

-- Datafile information
SELECT file_name, tablespace_name, bytes/1024/1024 as mb,
       maxbytes/1024/1024 as max_mb, autoextensible
FROM dba_data_files
ORDER BY tablespace_name, file_id;

-- Segment space usage
SELECT owner, segment_name, segment_type, tablespace_name,
       bytes/1024/1024 as mb
FROM dba_segments
WHERE bytes > 100*1024*1024 -- Segments larger than 100MB
ORDER BY bytes DESC;
```

### ASM (Automatic Storage Management)

#### ASM Instance Setup

```bash
# Create ASM parameter file
cat > $ORACLE_HOME/dbs/init+ASM.ora << EOF
instance_type=asm
asm_diskgroups=DATA,FRA
asm_power_limit=1
memory_target=256M
EOF

# Start ASM instance
export ORACLE_SID=+ASM
sqlplus / as sysasm
STARTUP;
```

#### Disk Group Management

```sql
-- Create disk group
CREATE DISKGROUP DATA EXTERNAL REDUNDANCY
DISK '/dev/oracleasm/disk1',
     '/dev/oracleasm/disk2',
     '/dev/oracleasm/disk3';

-- Add disk to disk group
ALTER DISKGROUP DATA ADD DISK '/dev/oracleasm/disk4';

-- Drop disk from disk group
ALTER DISKGROUP DATA DROP DISK disk4;

-- Mount/dismount disk group
ALTER DISKGROUP DATA MOUNT;
ALTER DISKGROUP DATA DISMOUNT;

-- Check disk group status
SELECT name, state, type, total_mb, free_mb
FROM v$asm_diskgroup;

-- Check disk status
SELECT group_number, disk_number, name, path, total_mb, free_mb
FROM v$asm_disk
ORDER BY group_number, disk_number;
```

#### ASM File Management

```sql
-- List ASM files
SELECT name, space, type FROM v$asm_file
WHERE group_number = 1;

-- Create database files in ASM
CREATE TABLESPACE asm_data
DATAFILE '+DATA' SIZE 100M;

-- Backup to ASM
RMAN> BACKUP DATABASE FORMAT '+FRA';
```

### Redo Log Management

#### Redo Log Configuration

```sql
-- Add redo log group
ALTER DATABASE ADD LOGFILE GROUP 4
    ('/opt/oracle/oradata/ORCL/redo04a.log',
     '/opt/oracle/oradata/ORCL/redo04b.log') SIZE 100M;

-- Add member to existing group
ALTER DATABASE ADD LOGFILE MEMBER
    '/opt/oracle/oradata/ORCL/redo01c.log' TO GROUP 1;

-- Drop redo log group (must be inactive)
ALTER DATABASE DROP LOGFILE GROUP 4;

-- Drop redo log member
ALTER DATABASE DROP LOGFILE MEMBER
    '/opt/oracle/oradata/ORCL/redo01c.log';

-- Force log switch
ALTER SYSTEM SWITCH LOGFILE;

-- Clear log file (for corruption)
ALTER DATABASE CLEAR LOGFILE GROUP 2;
```

#### Archive Log Management

```sql
-- Enable archiving
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE ARCHIVELOG;
ALTER DATABASE OPEN;

-- Disable archiving
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE NOARCHIVELOG;
ALTER DATABASE OPEN;

-- Set archive destinations
ALTER SYSTEM SET log_archive_dest_1 =
    'LOCATION=/opt/oracle/archive MANDATORY';
ALTER SYSTEM SET log_archive_dest_2 =
    'LOCATION=/backup/archive OPTIONAL';

-- Archive current log
ALTER SYSTEM ARCHIVE LOG CURRENT;

-- Check archive status
SELECT name, log_mode, archive_change# FROM v$database;

-- View archive information
SELECT sequence#, name, first_time, completion_time
FROM v$archived_log
WHERE completion_time >= SYSDATE - 1
ORDER BY sequence#;
```

## ðŸ‘¥ User and Security Management

### User Management

#### Creating Users

```sql
-- Create user with basic privileges
CREATE USER john_doe IDENTIFIED BY "SecurePassword123!"
DEFAULT TABLESPACE users
TEMPORARY TABLESPACE temp
QUOTA 100M ON users;

-- Grant basic privileges
GRANT CREATE SESSION TO john_doe;
GRANT CREATE TABLE TO john_doe;
GRANT CREATE PROCEDURE TO john_doe;

-- Create user with profile
CREATE USER jane_smith IDENTIFIED BY "SecurePassword123!"
DEFAULT TABLESPACE users
TEMPORARY TABLESPACE temp
PROFILE developer_profile
QUOTA UNLIMITED ON users;
```

#### Profile Management

```sql
-- Create profile
CREATE PROFILE developer_profile LIMIT
    SESSIONS_PER_USER 3
    CPU_PER_SESSION 10000
    CPU_PER_CALL 1000
    CONNECT_TIME 600
    IDLE_TIME 30
    LOGICAL_READS_PER_SESSION 1000000
    LOGICAL_READS_PER_CALL 100000
    PRIVATE_SGA 15K
    COMPOSITE_LIMIT 5000000
    PASSWORD_LIFE_TIME 90
    PASSWORD_GRACE_TIME 7
    PASSWORD_REUSE_TIME 365
    PASSWORD_REUSE_MAX 5
    FAILED_LOGIN_ATTEMPTS 3
    PASSWORD_LOCK_TIME 1
    PASSWORD_VERIFY_FUNCTION ora12c_verify_function;

-- Assign profile to user
ALTER USER john_doe PROFILE developer_profile;

-- Check profile usage
SELECT username, profile, account_status, lock_date, expiry_date
FROM dba_users
WHERE profile = 'DEVELOPER_PROFILE';
```

### Role Management

#### Creating Roles

```sql
-- Create application role
CREATE ROLE app_user;
CREATE ROLE app_REDACTED_LDAP_BIND_PASSWORD;

-- Grant privileges to roles
GRANT CREATE SESSION, CREATE TABLE, CREATE PROCEDURE TO app_user;
GRANT app_user TO app_REDACTED_LDAP_BIND_PASSWORD;
GRANT CREATE USER, ALTER USER, DROP USER TO app_REDACTED_LDAP_BIND_PASSWORD;

-- Create secure role
CREATE ROLE secure_role IDENTIFIED BY "RolePassword123!";
GRANT SELECT ON sensitive_table TO secure_role;

-- Grant role to user
GRANT app_user TO john_doe;
GRANT app_REDACTED_LDAP_BIND_PASSWORD TO jane_smith;

-- Set default roles
ALTER USER john_doe DEFAULT ROLE app_user;
```

#### Role Administration

```sql
-- View role privileges
SELECT role, privilege, REDACTED_LDAP_BIND_PASSWORD_option
FROM role_sys_privs
WHERE role = 'APP_ADMIN';

-- View role grants
SELECT grantee, granted_role, REDACTED_LDAP_BIND_PASSWORD_option, default_role
FROM dba_role_privs
WHERE granted_role = 'APP_USER';

-- Enable/disable roles in session
SET ROLE app_REDACTED_LDAP_BIND_PASSWORD IDENTIFIED BY "RolePassword123!";
SET ROLE ALL EXCEPT secure_role;
SET ROLE NONE;
```

### Privilege Management

#### System Privileges

```sql
-- Grant system privileges
GRANT CREATE ANY TABLE TO john_doe;
GRANT ALTER SYSTEM TO jane_smith WITH ADMIN OPTION;
GRANT SYSDBA TO dba_user;

-- Revoke system privileges
REVOKE CREATE ANY TABLE FROM john_doe;

-- View system privileges
SELECT grantee, privilege, REDACTED_LDAP_BIND_PASSWORD_option
FROM dba_sys_privs
WHERE grantee = 'JOHN_DOE';
```

#### Object Privileges

```sql
-- Grant object privileges
GRANT SELECT, INSERT, UPDATE ON employees TO john_doe;
GRANT ALL ON departments TO jane_smith WITH GRANT OPTION;
GRANT EXECUTE ON hr_package TO app_user;

-- Column-level privileges
GRANT UPDATE (salary, commission) ON employees TO payroll_user;

-- Revoke object privileges
REVOKE INSERT, UPDATE ON employees FROM john_doe;

-- View object privileges
SELECT owner, table_name, privilege, grantable
FROM dba_tab_privs
WHERE grantee = 'JOHN_DOE';
```

## ðŸ"Š Performance Monitoring

### System Performance

#### Wait Events Analysis

```sql
-- Top wait events
SELECT event, total_waits, total_timeouts, time_waited,
       average_wait, time_waited_micro
FROM v$system_event
WHERE wait_class != 'Idle'
ORDER BY time_waited DESC;

-- Session wait events
SELECT sid, event, wait_time, seconds_in_wait, state
FROM v$session_wait
WHERE wait_class != 'Idle'
ORDER BY seconds_in_wait DESC;

-- Historical wait events (from AWR)
SELECT event_name, total_waits, time_waited_micro,
       avg_wait_time_micro
FROM dba_hist_system_event
WHERE snap_id BETWEEN 100 AND 200
  AND wait_class != 'Idle'
ORDER BY time_waited_micro DESC;
```

#### Resource Usage

```sql
-- CPU usage by session
SELECT s.sid, s.serial#, s.username, s.program,
       ss.value as cpu_used_seconds
FROM v$session s, v$sesstat ss, v$statname sn
WHERE s.sid = ss.sid
  AND ss.statistic# = sn.statistic#
  AND sn.name = 'CPU used by this session'
  AND ss.value > 0
ORDER BY ss.value DESC;

-- Memory usage
SELECT name, value/1024/1024 as mb
FROM v$sysstat
WHERE name LIKE '%ga%'
   OR name LIKE '%pga%'
ORDER BY value DESC;

-- I/O statistics
SELECT name, value
FROM v$sysstat
WHERE name LIKE '%read%'
   OR name LIKE '%write%'
ORDER BY value DESC;
```

### SQL Performance

#### Top SQL Statements

```sql
-- Top SQL by elapsed time
SELECT sql_id, executions, elapsed_time/1000000 as elapsed_seconds,
       cpu_time/1000000 as cpu_seconds, buffer_gets, disk_reads,
       SUBSTR(sql_text, 1, 100) as sql_text
FROM v$sql
WHERE elapsed_time > 1000000  -- More than 1 second
ORDER BY elapsed_time DESC;

-- Top SQL by CPU usage
SELECT sql_id, executions, cpu_time/1000000 as cpu_seconds,
       cpu_time/executions/1000000 as avg_cpu_per_exec,
       SUBSTR(sql_text, 1, 100) as sql_text
FROM v$sql
WHERE executions > 0
  AND cpu_time > 1000000
ORDER BY cpu_time DESC;

-- Top SQL by logical reads
SELECT sql_id, executions, buffer_gets,
       buffer_gets/executions as avg_buffer_gets,
       SUBSTR(sql_text, 1, 100) as sql_text
FROM v$sql
WHERE executions > 0
  AND buffer_gets > 100000
ORDER BY buffer_gets DESC;
```

#### Execution Plan Analysis

```sql
-- Current execution plans
SELECT sql_id, child_number, operation, options, object_name,
       cost, cardinality, bytes
FROM v$sql_plan
WHERE sql_id = 'sql_id_here'
ORDER BY id;

-- Plan history from AWR
SELECT sql_id, plan_hash_value, executions_delta,
       elapsed_time_delta/1000000 as elapsed_seconds,
       cpu_time_delta/1000000 as cpu_seconds
FROM dba_hist_sqlstat
WHERE sql_id = 'sql_id_here'
ORDER BY snap_id;
```

### Database Performance

#### Buffer Cache Analysis

```sql
-- Buffer cache hit ratio
SELECT name,
       1 - (physical_reads / (db_block_gets + consistent_gets)) as hit_ratio
FROM v$buffer_pool_statistics;

-- Buffer cache advice
SELECT size_for_estimate/1024/1024 as cache_size_mb,
       size_factor, estd_physical_read_factor,
       estd_physical_reads
FROM v$db_cache_advice
WHERE name = 'DEFAULT'
ORDER BY size_for_estimate;

-- Top segments by buffer gets
SELECT owner, object_name, object_type,
       buffer_gets, disk_reads,
       buffer_gets/disk_reads as cache_ratio
FROM v$segment_statistics
WHERE statistic_name = 'buffer busy waits'
  AND value > 1000
ORDER BY value DESC;
```

#### Shared Pool Analysis

```sql
-- Library cache statistics
SELECT namespace, gets, gethits,
       ROUND(gethits/gets*100, 2) as hit_ratio,
       pins, pinhits,
       ROUND(pinhits/pins*100, 2) as pin_hit_ratio
FROM v$librarycache;

-- Shared pool advice
SELECT shared_pool_size_for_estimate/1024/1024 as pool_size_mb,
       shared_pool_size_factor,
       estd_lc_time_saved_factor
FROM v$shared_pool_advice
ORDER BY shared_pool_size_for_estimate;

-- Top SQL by parse calls
SELECT sql_id, parse_calls, executions,
       parse_calls/executions as parses_per_exec,
       SUBSTR(sql_text, 1, 100) as sql_text
FROM v$sql
WHERE executions > 0
  AND parse_calls > 100
ORDER BY parse_calls DESC;
```

## ðŸ"§ Maintenance Tasks

### Statistics Management

#### Automatic Statistics Collection

```sql
-- Check automatic statistics job
SELECT client_name, status, consumer_group, window_group
FROM dba_autotask_client
WHERE client_name = 'auto optimizer stats collection';

-- Enable/disable automatic statistics
EXEC DBMS_AUTO_TASK_ADMIN.ENABLE(
    client_name => 'auto optimizer stats collection',
    operation => NULL,
    window_name => NULL
);

-- Configure statistics preferences
EXEC DBMS_STATS.SET_GLOBAL_PREFS('ESTIMATE_PERCENT', 'AUTO_SAMPLE_SIZE');
EXEC DBMS_STATS.SET_GLOBAL_PREFS('METHOD_OPT', 'FOR ALL COLUMNS SIZE AUTO');
EXEC DBMS_STATS.SET_GLOBAL_PREFS('DEGREE', 'AUTO');
EXEC DBMS_STATS.SET_GLOBAL_PREFS('CASCADE', 'TRUE');
```

#### Manual Statistics Collection

```sql
-- Gather table statistics
EXEC DBMS_STATS.GATHER_TABLE_STATS(
    ownname => 'HR',
    tabname => 'EMPLOYEES',
    estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO',
    degree => DBMS_STATS.AUTO_DEGREE,
    cascade => TRUE
);

-- Gather schema statistics
EXEC DBMS_STATS.GATHER_SCHEMA_STATS(
    ownname => 'HR',
    estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO',
    degree => DBMS_STATS.AUTO_DEGREE,
    cascade => TRUE
);

-- Gather database statistics
EXEC DBMS_STATS.GATHER_DATABASE_STATS(
    estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO',
    degree => DBMS_STATS.AUTO_DEGREE,
    cascade => TRUE
);

-- Delete statistics
EXEC DBMS_STATS.DELETE_TABLE_STATS('HR', 'EMPLOYEES');
```

### Index Maintenance

#### Index Rebuilding

```sql
-- Check index fragmentation
SELECT owner, index_name, blevel, leaf_blocks,
       num_rows, distinct_keys, clustering_factor
FROM dba_indexes
WHERE owner = 'HR'
  AND blevel > 3;  -- Indexes with high B-level

-- Rebuild index online
ALTER INDEX hr.emp_name_idx REBUILD ONLINE;

-- Rebuild index with new tablespace
ALTER INDEX hr.emp_name_idx REBUILD TABLESPACE index_ts;

-- Rebuild partitioned index
ALTER INDEX hr.sales_date_idx REBUILD PARTITION p_2023_q1;

-- Coalesce index (alternative to rebuild)
ALTER INDEX hr.emp_name_idx COALESCE;
```

#### Index Monitoring

```sql
-- Enable index monitoring
ALTER INDEX hr.emp_name_idx MONITORING USAGE;

-- Check index usage
SELECT index_name, table_name, monitoring, used, start_monitoring
FROM v$object_usage
WHERE index_name = 'EMP_NAME_IDX';

-- Disable monitoring
ALTER INDEX hr.emp_name_idx NOMONITORING USAGE;

-- Find unused indexes
SELECT owner, index_name, table_name
FROM dba_indexes di
WHERE di.owner = 'HR'
  AND NOT EXISTS (
    SELECT 1 FROM v$object_usage ou
    WHERE ou.index_name = di.index_name
      AND ou.used = 'TRUE'
  );
```

### Space Management

#### Segment Shrinking

```sql
-- Enable row movement
ALTER TABLE hr.employees ENABLE ROW MOVEMENT;

-- Shrink table
ALTER TABLE hr.employees SHRINK SPACE;

-- Shrink table and compact
ALTER TABLE hr.employees SHRINK SPACE COMPACT;

-- Shrink index
ALTER INDEX hr.emp_name_idx SHRINK SPACE;

-- Check shrink candidates
SELECT owner, segment_name, segment_type,
       bytes/1024/1024 as mb,
       blocks, empty_blocks
FROM dba_segments
WHERE owner = 'HR'
  AND empty_blocks > 1000;
```

#### Tablespace Cleanup

```sql
-- Move table to different tablespace
ALTER TABLE hr.employees MOVE TABLESPACE new_ts;

-- Rebuild indexes after table move
SELECT 'ALTER INDEX ' || owner || '.' || index_name || ' REBUILD;'
FROM dba_indexes
WHERE table_owner = 'HR'
  AND table_name = 'EMPLOYEES'
  AND status = 'UNUSABLE';

-- Reorganize tablespace
EXEC DBMS_SPACE.SPACE_USAGE('HR', 'EMPLOYEES', 'TABLE',
                           :unformatted_blocks, :unformatted_bytes,
                           :fs1_blocks, :fs1_bytes,
                           :fs2_blocks, :fs2_bytes,
                           :fs3_blocks, :fs3_bytes,
                           :fs4_blocks, :fs4_bytes,
                           :full_blocks, :full_bytes);
```

### Database Maintenance

#### Health Checks

```sql
-- Check database status
SELECT name, open_mode, log_mode, database_role
FROM v$database;

-- Check tablespace usage
SELECT tablespace_name,
       ROUND(used_percent, 2) as pct_used,
       ROUND(used_space/1024/1024, 2) as used_mb,
       ROUND(tablespace_size/1024/1024, 2) as total_mb
FROM dba_tablespace_usage_metrics
WHERE used_percent > 80;

-- Check invalid objects
SELECT owner, object_name, object_type, status
FROM dba_objects
WHERE status = 'INVALID'
ORDER BY owner, object_type, object_name;

-- Compile invalid objects
EXEC DBMS_UTILITY.COMPILE_SCHEMA('HR');
```

#### Log File Analysis

```sql
-- Check alert log for errors
SELECT message_text, message_level, message_type,
       originating_timestamp
FROM x$dbgalertext
WHERE originating_timestamp >= SYSDATE - 1
  AND message_level <= 2
ORDER BY originating_timestamp DESC;

-- Check for ORA errors in alert log
-- (This requires external log parsing tools or custom scripts)

-- Monitor redo generation
SELECT sequence#, first_time, next_time,
       (next_time - first_time) * 24 * 60 as minutes_to_switch,
       blocks * block_size / 1024 / 1024 as mb
FROM v$log_history
WHERE first_time >= SYSDATE - 1
ORDER BY first_time;
```

## ðŸš¨ Troubleshooting

### Common Issues

#### Database Startup Issues

```sql
-- ORA-01078: failure in processing system parameters
-- Check parameter file location and syntax
SHOW PARAMETER spfile;
CREATE PFILE='/tmp/init.ora' FROM SPFILE;

-- ORA-00205: error in identifying control file
-- Check control file locations
SHOW PARAMETER control_files;
-- Restore control file from backup or recreate

-- ORA-01157: cannot identify/lock data file
-- Check datafile locations and permissions
SELECT file_id, file_name, status FROM dba_data_files;
-- Take datafile offline if corrupted
ALTER DATABASE DATAFILE 4 OFFLINE;
```

#### Performance Issues

```sql
-- High CPU usage
-- Identify CPU-intensive sessions
SELECT s.sid, s.serial#, s.username, s.program,
       ss.value as cpu_seconds
FROM v$session s, v$sesstat ss, v$statname sn
WHERE s.sid = ss.sid
  AND ss.statistic# = sn.statistic#
  AND sn.name = 'CPU used by this session'
  AND ss.value > 100
ORDER BY ss.value DESC;

-- High I/O waits
-- Check for I/O bottlenecks
SELECT event, total_waits, time_waited, average_wait
FROM v$system_event
WHERE event LIKE '%read%' OR event LIKE '%write%'
ORDER BY time_waited DESC;

-- Memory pressure
-- Check memory allocation
SELECT component, current_size/1024/1024 as current_mb,
       min_size/1024/1024 as min_mb,
       max_size/1024/1024 as max_mb
FROM v$memory_dynamic_components;
```

#### Space Issues

```sql
-- ORA-01653: unable to extend table
-- Check tablespace space
SELECT tablespace_name,
       ROUND(used_percent, 2) as pct_used
FROM dba_tablespace_usage_metrics
WHERE used_percent > 90;

-- Add space to tablespace
ALTER TABLESPACE users
ADD DATAFILE '/opt/oracle/oradata/ORCL/users02.dbf' SIZE 100M;

-- ORA-00257: archiver error
-- Check archive destination space
SELECT dest_name, status, destination, error
FROM v$archive_dest
WHERE status = 'ERROR';

-- Clean up old archive logs
RMAN> DELETE ARCHIVELOG UNTIL TIME 'SYSDATE-7';
```

### Diagnostic Tools

#### AWR Reports

```sql
-- Generate AWR report
@$ORACLE_HOME/rdbms/REDACTED_LDAP_BIND_PASSWORD/awrrpt.sql

-- Generate AWR comparison report
@$ORACLE_HOME/rdbms/REDACTED_LDAP_BIND_PASSWORD/awrddrpt.sql

-- Create AWR baseline
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_BASELINE(
    start_snap_id => 100,
    end_snap_id => 200,
    baseline_name => 'peak_workload_baseline'
);
```

#### ASH Reports

```sql
-- Generate ASH report
@$ORACLE_HOME/rdbms/REDACTED_LDAP_BIND_PASSWORD/ashrpt.sql

-- ASH analysis for specific time period
SELECT event, count(*) as samples,
       ROUND(count(*) * 10 / 3600 * 100, 2) as pct_activity
FROM v$active_session_history
WHERE sample_time BETWEEN
    TO_DATE('2024-01-15 14:00:00', 'YYYY-MM-DD HH24:MI:SS') AND
    TO_DATE('2024-01-15 15:00:00', 'YYYY-MM-DD HH24:MI:SS')
GROUP BY event
ORDER BY samples DESC;
```

#### ADDM Analysis

```sql
-- Run ADDM manually
DECLARE
    task_name VARCHAR2(30);
BEGIN
    task_name := DBMS_ADDM.ANALYZE_DB(
        begin_snapshot => 100,
        end_snapshot => 200
    );

    DBMS_OUTPUT.PUT_LINE('ADDM task: ' || task_name);
END;
/

-- View ADDM findings
SELECT finding_id, finding_name, impact_type, impact
FROM dba_advisor_findings
WHERE task_name = 'ADDM_task_name'
ORDER BY impact DESC;
```

## ðŸ¤– Automation

### Scheduled Jobs

#### Database Jobs (DBMS_SCHEDULER)

```sql
-- Create job class
EXEC DBMS_SCHEDULER.CREATE_JOB_CLASS(
    job_class_name => 'maintenance_class',
    resource_consumer_group => 'DEFAULT_CONSUMER_GROUP',
    service => 'DEFAULT',
    logging_level => DBMS_SCHEDULER.LOGGING_FULL,
    log_history => 30,
    comments => 'Maintenance job class'
);

-- Create maintenance job
EXEC DBMS_SCHEDULER.CREATE_JOB(
    job_name => 'gather_stats_job',
    job_type => 'PLSQL_BLOCK',
    job_action => 'BEGIN DBMS_STATS.GATHER_DATABASE_STATS(cascade=>TRUE); END;',
    start_date => SYSTIMESTAMP,
    repeat_interval => 'FREQ=DAILY; BYHOUR=2; BYMINUTE=0; BYSECOND=0',
    job_class => 'maintenance_class',
    enabled => TRUE,
    comments => 'Daily statistics gathering'
);

-- Monitor job execution
SELECT job_name, state, last_start_date, last_run_duration,
       next_run_date, run_count, failure_count
FROM dba_scheduler_jobs
WHERE job_name = 'GATHER_STATS_JOB';
```

#### Backup Automation

```bash
#!/bin/bash
# Automated backup script

export ORACLE_SID=ORCL
export ORACLE_HOME=/opt/oracle/product/19c/dbhome_1
export PATH=$ORACLE_HOME/bin:$PATH

# Log file
LOG_FILE="/opt/oracle/REDACTED_LDAP_BIND_PASSWORD/ORCL/backup_$(date +%Y%m%d_%H%M%S).log"

# RMAN backup
rman target / << EOF >> $LOG_FILE 2>&1
CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF 30 DAYS;
CONFIGURE BACKUP OPTIMIZATION ON;
CONFIGURE COMPRESSION ALGORITHM 'MEDIUM';

BACKUP AS COMPRESSED BACKUPSET
DATABASE
PLUS ARCHIVELOG
FORMAT '/backup/rman/%d_%T_%s_%p'
TAG 'DAILY_BACKUP';

DELETE OBSOLETE;
CROSSCHECK BACKUP;

LIST BACKUP SUMMARY;
EXIT;
EOF

# Check backup status
if [ $? -eq 0 ]; then
    echo "Backup completed successfully" >> $LOG_FILE
    # Send success notification
else
    echo "Backup failed" >> $LOG_FILE
    # Send failure notification
fi
```

### Monitoring Scripts

#### Health Check Script

```bash
#!/bin/bash
# Database health check script

export ORACLE_SID=ORCL
export ORACLE_HOME=/opt/oracle/product/19c/dbhome_1
export PATH=$ORACLE_HOME/bin:$PATH

REPORT_FILE="/tmp/db_health_$(date +%Y%m%d).html"

cat > $REPORT_FILE << EOF
<html><head><title>Database Health Report</title></head><body>
<h1>Database Health Report - $(date)</h1>
EOF

# Database status
sqlplus -s / as sysdba << SQL >> $REPORT_FILE
SET MARKUP HTML ON
SELECT 'Database Status' as "Check Type",
       name as "Database Name",
       open_mode as "Status",
       log_mode as "Archive Mode"
FROM v$database;

SELECT 'Tablespace Usage' as "Check Type",
       tablespace_name,
       ROUND(used_percent, 2) as "Used %"
FROM dba_tablespace_usage_metrics
WHERE used_percent > 80;

SELECT 'Invalid Objects' as "Check Type",
       owner, object_type, COUNT(*) as "Count"
FROM dba_objects
WHERE status = 'INVALID'
GROUP BY owner, object_type;
SQL

echo "</body></html>" >> $REPORT_FILE

# Email report
mail -s "Database Health Report" -a $REPORT_FILE dba@company.com < /dev/null
```

## ðŸ"‹ Best Practices

### Security Best Practices

#### Password Management

- Use strong, complex passwords
- Implement password policies
- Regular password rotation
- Avoid default passwords
- Use external authentication when possible

#### Access Control

- Implement least privilege principle
- Use roles instead of direct grants
- Regular access reviews
- Separate REDACTED_LDAP_BIND_PASSWORDistrative duties
- Monitor privileged access

#### Auditing

- Enable comprehensive auditing
- Monitor failed login attempts
- Alert on suspicious activities
- Regular audit log reviews
- Retain audit logs appropriately

### Performance Best Practices

#### Memory Management

- Use Automatic Memory Management (AMM) when appropriate
- Monitor memory usage regularly
- Tune SGA and PGA based on workload
- Use memory advisors for sizing guidance

#### Storage Management

- Use locally managed tablespaces
- Implement appropriate extent sizing
- Monitor space usage proactively
- Use ASM for storage management
- Separate different workload types

#### SQL Performance

- Gather current statistics regularly
- Monitor top SQL statements
- Use SQL tuning advisor
- Implement SQL plan baselines
- Review execution plans regularly

### Maintenance Best Practices

#### Backup and Recovery

- Test backup and recovery procedures regularly
- Implement appropriate retention policies
- Use RMAN for backup operations
- Monitor backup success/failure
- Document recovery procedures

#### Monitoring

- Implement proactive monitoring
- Set up appropriate alerts
- Review AWR reports regularly
- Monitor system resources
- Track performance trends

#### Change Management

- Test changes in non-production first
- Document all changes
- Have rollback procedures ready
- Schedule changes during maintenance windows
- Communicate changes to stakeholders

---

**Last Updated**: December 2024
**Version**: 1.0
**Maintainer**: Oracle Core Shared Team

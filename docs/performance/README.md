# Oracle Database Performance Tuning Guide

This comprehensive guide covers all aspects of Oracle Database performance tuning, monitoring, and optimization.

## ðŸ"‹ Table of Contents

- [Performance Tuning Methodology](#performance-tuning-methodology)
- [Database Design for Performance](#database-design-for-performance)
- [SQL Tuning](#sql-tuning)
- [Instance Tuning](#instance-tuning)
- [Memory Tuning](#memory-tuning)
- [I/O Tuning](#io-tuning)
- [Monitoring and Diagnostics](#monitoring-and-diagnostics)
- [Automatic Performance Features](#automatic-performance-features)
- [Performance Tools](#performance-tools)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)

## ðŸŽ¯ Performance Tuning Methodology

### Top-Down Approach

1. **Business Requirements Analysis**

   - Define performance objectives
   - Identify critical business processes
   - Establish baseline measurements
   - Set realistic performance targets

2. **System-Level Analysis**

   - Operating system performance
   - Hardware resource utilization
   - Network performance
   - Storage subsystem performance

3. **Database Instance Analysis**

   - Instance-level wait events
   - Memory allocation and usage
   - Background process efficiency
   - Parameter configuration

4. **Application Analysis**
   - SQL statement performance
   - Application design patterns
   - Connection management
   - Transaction design

### Performance Tuning Lifecycle

```
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚                Performance Tuning Lifecycle                 â"‚
â"œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¤
â"‚                                                             â"‚
â"‚  â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"    â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"    â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"     â"‚
â"‚  â"‚   Monitor   â"‚â"€â"€â"€â–¶â"‚   Analyze   â"‚â"€â"€â"€â–¶â"‚  Optimize   â"‚     â"‚
â"‚  â"‚             â"‚    â"‚             â"‚    â"‚             â"‚     â"‚
â"‚  â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜    â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜    â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜     â"‚
â"‚         â–²                                        â"‚         â"‚
â"‚         â"‚                                        â–¼         â"‚
â"‚  â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"    â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"    â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"     â"‚
â"‚  â"‚   Verify    â"‚â—€â"€â"€â"€â"‚   Validate  â"‚â—€â"€â"€â"€â"‚ Implement   â"‚     â"‚
â"‚  â"‚             â"‚    â"‚             â"‚    â"‚             â"‚     â"‚
â"‚  â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜    â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜    â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜     â"‚
â"‚                                                             â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
```

### Key Performance Metrics

#### Response Time Components

- **Service Time**: Time spent processing request
- **Wait Time**: Time spent waiting for resources
- **Queue Time**: Time spent in queues
- **Network Time**: Time spent in network transmission

#### Throughput Metrics

- **Transactions per Second (TPS)**
- **SQL Executions per Second**
- **Logical Reads per Second**
- **Physical Reads per Second**
- **Redo Generation Rate**

#### Resource Utilization

- **CPU Utilization**: Percentage of CPU capacity used
- **Memory Utilization**: SGA and PGA usage
- **I/O Utilization**: Disk I/O throughput and latency
- **Network Utilization**: Network bandwidth usage

## ðŸ—ï¸ Database Design for Performance

### Logical Design Considerations

#### Normalization vs. Denormalization

- **Normalization Benefits**:

  - Eliminates data redundancy
  - Ensures data consistency
  - Reduces storage requirements
  - Simplifies data maintenance

- **Denormalization Benefits**:
  - Reduces join operations
  - Improves query performance
  - Simplifies application logic
  - Better for read-heavy workloads

#### Data Type Selection

- **Numeric Types**:

  - Use appropriate precision
  - NUMBER vs. INTEGER considerations
  - BINARY_FLOAT/BINARY_DOUBLE for scientific calculations

- **Character Types**:

  - VARCHAR2 vs. CHAR selection
  - Character set considerations (AL32UTF8)
  - National character set usage

- **Date/Time Types**:
  - DATE vs. TIMESTAMP precision
  - Time zone considerations
  - Interval data types

#### Constraint Design

- **Primary Keys**:

  - Natural vs. surrogate keys
  - Sequence-based vs. UUID
  - Impact on index organization

- **Foreign Keys**:
  - Referential integrity enforcement
  - Index requirements
  - Cascade options impact

### Physical Design Optimization

#### Table Organization

##### Heap Tables

- **Characteristics**: Default table organization
- **Benefits**: Optimal for OLTP workloads
- **Considerations**: Row migration and chaining

##### Index-Organized Tables (IOT)

- **Benefits**: Eliminates table access by rowid
- **Use Cases**: Tables accessed primarily by primary key
- **Considerations**: Overflow area management

##### Clustered Tables

- **Hash Clusters**: Fixed number of hash buckets
- **Index Clusters**: Multiple tables stored together
- **Benefits**: Reduced I/O for related data

##### External Tables

- **Purpose**: Access external files as tables
- **Benefits**: ETL operations without data loading
- **Considerations**: Limited DML operations

#### Partitioning Strategy

##### Range Partitioning

```sql
CREATE TABLE sales (
    sale_date DATE,
    product_id NUMBER,
    amount NUMBER
) PARTITION BY RANGE (sale_date) (
    PARTITION sales_2023_q1 VALUES LESS THAN (DATE '2023-04-01'),
    PARTITION sales_2023_q2 VALUES LESS THAN (DATE '2023-07-01'),
    PARTITION sales_2023_q3 VALUES LESS THAN (DATE '2023-10-01'),
    PARTITION sales_2023_q4 VALUES LESS THAN (DATE '2024-01-01')
);
```

##### List Partitioning

```sql
CREATE TABLE customers (
    customer_id NUMBER,
    region VARCHAR2(20),
    customer_name VARCHAR2(100)
) PARTITION BY LIST (region) (
    PARTITION north_america VALUES ('USA', 'CANADA'),
    PARTITION europe VALUES ('UK', 'GERMANY', 'FRANCE'),
    PARTITION asia VALUES ('JAPAN', 'CHINA', 'INDIA')
);
```

##### Hash Partitioning

```sql
CREATE TABLE orders (
    order_id NUMBER,
    customer_id NUMBER,
    order_date DATE
) PARTITION BY HASH (customer_id)
PARTITIONS 8;
```

##### Composite Partitioning

```sql
CREATE TABLE sales_data (
    sale_date DATE,
    region VARCHAR2(20),
    amount NUMBER
) PARTITION BY RANGE (sale_date)
SUBPARTITION BY LIST (region) (
    PARTITION sales_2023 VALUES LESS THAN (DATE '2024-01-01') (
        SUBPARTITION sales_2023_north VALUES ('USA', 'CANADA'),
        SUBPARTITION sales_2023_europe VALUES ('UK', 'GERMANY')
    )
);
```

### Index Design Strategy

#### B-Tree Indexes

- **Standard Indexes**: Most common index type
- **Unique Indexes**: Enforce uniqueness
- **Composite Indexes**: Multiple columns
- **Function-Based Indexes**: Based on expressions

#### Specialized Indexes

##### Bitmap Indexes

```sql
CREATE BITMAP INDEX idx_gender ON employees(gender);
```

- **Use Cases**: Low cardinality columns
- **Benefits**: Efficient for data warehouse queries
- **Considerations**: Not suitable for OLTP

##### Partial Indexes

```sql
CREATE INDEX idx_active_orders
ON orders(order_date)
WHERE status = 'ACTIVE';
```

##### Invisible Indexes

```sql
CREATE INDEX idx_customer_name
ON customers(customer_name) INVISIBLE;
```

##### Virtual Columns and Indexes

```sql
ALTER TABLE employees
ADD (annual_salary AS (monthly_salary * 12));

CREATE INDEX idx_annual_salary ON employees(annual_salary);
```

## ðŸ"§ SQL Tuning

### SQL Tuning Process

#### 1. Identify Problem SQL

- **Top SQL by Resource Consumption**
- **Long-Running Queries**
- **Frequently Executed Statements**
- **SQL with High Wait Times**

#### 2. Analyze Execution Plans

- **Cost Analysis**: Understand optimizer costs
- **Cardinality Estimates**: Check row count estimates
- **Access Methods**: Evaluate access paths
- **Join Methods**: Analyze join algorithms

#### 3. Gather Additional Information

- **Table and Index Statistics**
- **Bind Variable Values**
- **System Statistics**
- **Optimizer Parameters**

#### 4. Implement Tuning Techniques

- **SQL Rewriting**
- **Hint Usage**
- **Index Creation/Modification**
- **Statistics Update**

### Execution Plan Analysis

#### Understanding Execution Plans

##### Plan Operations

```sql
EXPLAIN PLAN FOR
SELECT e.employee_name, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE e.salary > 50000;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

##### Common Operations

- **TABLE ACCESS FULL**: Full table scan
- **TABLE ACCESS BY INDEX ROWID**: Index-based access
- **INDEX RANGE SCAN**: Range scan on index
- **INDEX UNIQUE SCAN**: Unique index lookup
- **NESTED LOOPS**: Nested loop join
- **HASH JOIN**: Hash join algorithm
- **SORT MERGE JOIN**: Sort-merge join

#### Plan Analysis Tools

##### DBMS_XPLAN Package

```sql
-- Basic plan display
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

-- Plan with runtime statistics
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST'));

-- Plan from AWR
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_AWR('sql_id'));
```

##### Real-Time SQL Monitoring

```sql
SELECT * FROM TABLE(DBMS_SQLTUNE.REPORT_SQL_MONITOR(
    sql_id => 'sql_id_here',
    type => 'HTML'
));
```

### SQL Optimization Techniques

#### Query Rewriting

##### Predicate Pushdown

```sql
-- Before: Filter applied after join
SELECT e.employee_name, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE d.department_name = 'SALES';

-- After: Filter pushed to base table
SELECT e.employee_name, d.department_name
FROM employees e
JOIN (SELECT department_id, department_name
      FROM departments
      WHERE department_name = 'SALES') d
ON e.department_id = d.department_id;
```

##### Subquery Optimization

```sql
-- Correlated subquery (potentially slow)
SELECT employee_name
FROM employees e1
WHERE salary > (SELECT AVG(salary)
                FROM employees e2
                WHERE e2.department_id = e1.department_id);

-- Analytical function (often faster)
SELECT employee_name
FROM (SELECT employee_name, salary,
             AVG(salary) OVER (PARTITION BY department_id) as avg_dept_salary
      FROM employees)
WHERE salary > avg_dept_salary;
```

##### Join Elimination

```sql
-- Unnecessary join
SELECT e.employee_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id;

-- Simplified query
SELECT employee_name FROM employees;
```

#### Index Optimization

##### Covering Indexes

```sql
-- Query requiring table access
SELECT employee_id, employee_name, salary
FROM employees
WHERE department_id = 10;

-- Covering index eliminates table access
CREATE INDEX idx_emp_covering
ON employees(department_id, employee_id, employee_name, salary);
```

##### Index Skip Scan

```sql
-- Composite index on (gender, employee_id)
CREATE INDEX idx_gender_emp_id ON employees(gender, employee_id);

-- Query can use skip scan even without gender predicate
SELECT * FROM employees WHERE employee_id = 100;
```

#### Hint Usage

##### Common Hints

```sql
-- Force index usage
SELECT /*+ INDEX(e, idx_emp_dept) */ employee_name
FROM employees e
WHERE department_id = 10;

-- Force full table scan
SELECT /*+ FULL(e) */ employee_name
FROM employees e
WHERE department_id = 10;

-- Force join method
SELECT /*+ USE_HASH(e, d) */ e.employee_name, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id;

-- Force join order
SELECT /*+ ORDERED */ e.employee_name, d.department_name
FROM employees e, departments d
WHERE e.department_id = d.department_id;
```

##### Parallel Hints

```sql
-- Parallel table scan
SELECT /*+ PARALLEL(employees, 4) */ COUNT(*)
FROM employees;

-- Parallel join
SELECT /*+ PARALLEL(e, 4) PARALLEL(d, 4) */ COUNT(*)
FROM employees e
JOIN departments d ON e.department_id = d.department_id;
```

### Advanced SQL Tuning

#### SQL Plan Management

##### Creating SQL Plan Baselines

```sql
-- Enable automatic capture
ALTER SYSTEM SET optimizer_capture_sql_plan_baselines = TRUE;

-- Manual baseline creation
DECLARE
    l_plans_loaded PLS_INTEGER;
BEGIN
    l_plans_loaded := DBMS_SPM.LOAD_PLANS_FROM_CURSOR_CACHE(
        sql_id => 'sql_id_here'
    );
END;
/
```

##### Managing Baselines

```sql
-- Display baselines
SELECT sql_handle, plan_name, enabled, accepted
FROM dba_sql_plan_baselines
WHERE sql_text LIKE '%your_query%';

-- Evolve baselines
DECLARE
    l_report CLOB;
BEGIN
    l_report := DBMS_SPM.EVOLVE_SQL_PLAN_BASELINE(
        sql_handle => 'sql_handle_here'
    );
    DBMS_OUTPUT.PUT_LINE(l_report);
END;
/
```

#### SQL Profiles

##### Creating SQL Profiles

```sql
-- Run SQL Tuning Advisor
DECLARE
    l_task_name VARCHAR2(30);
BEGIN
    l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
        sql_id => 'sql_id_here',
        task_name => 'tune_sql_task'
    );

    DBMS_SQLTUNE.EXECUTE_TUNING_TASK('tune_sql_task');
END;
/

-- View recommendations
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK('tune_sql_task') FROM DUAL;

-- Implement SQL Profile
EXEC DBMS_SQLTUNE.ACCEPT_SQL_PROFILE('tune_sql_task');
```

## âš™ï¸ Instance Tuning

### Memory Configuration

#### System Global Area (SGA) Sizing

##### Automatic Memory Management

```sql
-- Enable Automatic Memory Management
ALTER SYSTEM SET memory_target = 2G;
ALTER SYSTEM SET memory_max_target = 4G;
```

##### Automatic Shared Memory Management

```sql
-- Enable ASMM for SGA only
ALTER SYSTEM SET sga_target = 1G;
ALTER SYSTEM SET sga_max_size = 2G;
```

##### Manual Memory Management

```sql
-- Manual sizing of SGA components
ALTER SYSTEM SET shared_pool_size = 400M;
ALTER SYSTEM SET db_cache_size = 800M;
ALTER SYSTEM SET large_pool_size = 64M;
ALTER SYSTEM SET java_pool_size = 32M;
ALTER SYSTEM SET log_buffer = 16M;
```

#### Program Global Area (PGA) Tuning

##### PGA Configuration

```sql
-- Automatic PGA management
ALTER SYSTEM SET pga_aggregate_target = 500M;
ALTER SYSTEM SET pga_aggregate_limit = 1G;

-- Workarea sizing policy
ALTER SYSTEM SET workarea_size_policy = AUTO;
```

##### PGA Monitoring

```sql
-- PGA usage statistics
SELECT name, value, unit
FROM v$pgastat
WHERE name IN ('aggregate PGA target parameter',
               'aggregate PGA auto target',
               'total PGA allocated',
               'maximum PGA allocated');

-- PGA advice
SELECT pga_target_for_estimate/1024/1024 as pga_target_mb,
       estd_pga_cache_hit_percentage,
       estd_overalloc_count
FROM v$pga_target_advice
ORDER BY pga_target_for_estimate;
```

### Background Process Tuning

#### Database Writer (DBWn) Optimization

```sql
-- Multiple database writers
ALTER SYSTEM SET db_writer_processes = 4;

-- Asynchronous I/O
ALTER SYSTEM SET disk_asynch_io = TRUE;

-- I/O slaves for platforms without async I/O
ALTER SYSTEM SET dbwr_io_slaves = 4;
```

#### Log Writer (LGWR) Optimization

```sql
-- Redo log buffer sizing
ALTER SYSTEM SET log_buffer = 32M;

-- Log file sync wait reduction
-- Ensure redo logs on fast storage
-- Consider using solid-state drives
-- Optimize redo log file size
```

#### Archiver Process Optimization

```sql
-- Multiple archiver processes
ALTER SYSTEM SET log_archive_max_processes = 4;

-- Archive destination optimization
ALTER SYSTEM SET log_archive_dest_1 =
    'LOCATION=/fast/archive MANDATORY REOPEN=300';
```

### Parameter Optimization

#### Critical Performance Parameters

##### Optimizer Parameters

```sql
-- Optimizer features
ALTER SYSTEM SET optimizer_features_enable = '19.1.0';

-- Optimizer mode
ALTER SYSTEM SET optimizer_mode = ALL_ROWS;

-- Dynamic sampling
ALTER SYSTEM SET optimizer_dynamic_sampling = 2;

-- Adaptive features
ALTER SYSTEM SET optimizer_adaptive_features = TRUE;
```

##### Parallel Processing Parameters

```sql
-- Parallel execution
ALTER SYSTEM SET parallel_max_servers = 20;
ALTER SYSTEM SET parallel_min_servers = 5;

-- Parallel degree policy
ALTER SYSTEM SET parallel_degree_policy = ADAPTIVE;

-- Parallel statement queuing
ALTER SYSTEM SET parallel_servers_target = 16;
```

##### Undo Management Parameters

```sql
-- Undo retention
ALTER SYSTEM SET undo_retention = 3600;

-- Undo tablespace
ALTER SYSTEM SET undo_tablespace = UNDOTBS1;

-- Undo management
ALTER SYSTEM SET undo_management = AUTO;
```

## ðŸ'¾ Memory Tuning

### Buffer Cache Optimization

#### Buffer Cache Sizing

```sql
-- Buffer cache advice
SELECT size_for_estimate/1024/1024 as cache_size_mb,
       size_factor,
       estd_physical_read_factor,
       estd_physical_reads
FROM v$db_cache_advice
WHERE name = 'DEFAULT'
ORDER BY size_for_estimate;
```

#### Multiple Buffer Pools

```sql
-- Create KEEP pool for frequently accessed objects
ALTER SYSTEM SET db_keep_cache_size = 200M;

-- Create RECYCLE pool for large scans
ALTER SYSTEM SET db_recycle_cache_size = 100M;

-- Assign table to KEEP pool
ALTER TABLE important_table STORAGE (BUFFER_POOL KEEP);

-- Assign table to RECYCLE pool
ALTER TABLE large_scan_table STORAGE (BUFFER_POOL RECYCLE);
```

#### Buffer Cache Monitoring

```sql
-- Buffer cache hit ratio
SELECT name,
       physical_reads,
       db_block_gets,
       consistent_gets,
       1 - (physical_reads / (db_block_gets + consistent_gets)) as hit_ratio
FROM v$buffer_pool_statistics;

-- Buffer busy waits
SELECT class, count, time
FROM v$waitstat
WHERE count > 0
ORDER BY time DESC;
```

### Shared Pool Tuning

#### Shared Pool Sizing

```sql
-- Shared pool advice
SELECT shared_pool_size_for_estimate/1024/1024 as pool_size_mb,
       shared_pool_size_factor,
       estd_lc_size/1024/1024 as estd_library_cache_mb,
       estd_lc_memory_objects,
       estd_lc_time_saved_factor
FROM v$shared_pool_advice
ORDER BY shared_pool_size_for_estimate;
```

#### Library Cache Optimization

```sql
-- Library cache statistics
SELECT namespace,
       gets,
       gethits,
       gethitratio,
       pins,
       pinhits,
       pinhitratio,
       reloads,
       invalidations
FROM v$librarycache;

-- Identify statements causing reloads
SELECT sql_id,
       loads,
       invalidations,
       parse_calls,
       executions,
       sql_text
FROM v$sql
WHERE loads > 3
ORDER BY loads DESC;
```

#### Cursor Sharing

```sql
-- Force cursor sharing for literals
ALTER SYSTEM SET cursor_sharing = FORCE;

-- Similar cursor sharing (recommended)
ALTER SYSTEM SET cursor_sharing = SIMILAR;

-- Exact cursor sharing (default)
ALTER SYSTEM SET cursor_sharing = EXACT;
```

### Large Pool Configuration

#### Large Pool Usage

```sql
-- Large pool for parallel execution
ALTER SYSTEM SET large_pool_size = 128M;

-- Monitor large pool usage
SELECT pool,
       name,
       bytes/1024/1024 as mb
FROM v$sgastat
WHERE pool = 'large pool'
ORDER BY bytes DESC;
```

#### RMAN Memory Configuration

```sql
-- Configure RMAN memory usage
CONFIGURE CHANNEL DEVICE TYPE DISK PARMS 'BLKSIZE=1048576';

-- Large pool for RMAN
ALTER SYSTEM SET large_pool_size = 256M;
```

## ðŸ'¿ I/O Tuning

### Storage Configuration

#### Optimal File Placement

- **Separate Redo Logs**: Place on fastest storage
- **Separate Archive Logs**: Use different devices from redo
- **Separate Temp Files**: Dedicated temporary storage
- **Data File Distribution**: Spread across multiple devices

#### Stripe Configuration

- **RAID Configuration**: RAID 10 for performance, RAID 5 for capacity
- **Stripe Size**: Match database block size multiples
- **Controller Cache**: Enable write caching with battery backup

### Database File Optimization

#### Redo Log Optimization

```sql
-- Optimal redo log size (switch every 15-20 minutes)
SELECT sequence#,
       first_time,
       next_time,
       (next_time - first_time) * 24 * 60 as minutes
FROM v$log_history
WHERE first_time > SYSDATE - 1
ORDER BY first_time;

-- Add redo log groups
ALTER DATABASE ADD LOGFILE GROUP 4
    ('/path/to/redo04a.log', '/path/to/redo04b.log') SIZE 1G;

-- Resize redo logs
ALTER DATABASE DROP LOGFILE GROUP 1;
ALTER DATABASE ADD LOGFILE GROUP 1
    ('/path/to/redo01a.log', '/path/to/redo01b.log') SIZE 1G;
```

#### Temporary Tablespace Optimization

```sql
-- Create temporary tablespace with multiple files
CREATE TEMPORARY TABLESPACE temp_new
TEMPFILE '/path/to/temp01.dbf' SIZE 2G,
         '/path/to/temp02.dbf' SIZE 2G,
         '/path/to/temp03.dbf' SIZE 2G
EXTENT MANAGEMENT LOCAL UNIFORM SIZE 1M;

-- Monitor temporary space usage
SELECT tablespace_name,
       total_blocks,
       used_blocks,
       free_blocks,
       (used_blocks/total_blocks)*100 as pct_used
FROM v$sort_segment;
```

### I/O Monitoring and Analysis

#### I/O Statistics

```sql
-- File I/O statistics
SELECT df.tablespace_name,
       df.file_name,
       fs.phyrds,
       fs.phywrts,
       fs.readtim,
       fs.writetim,
       fs.avgiotim
FROM dba_data_files df,
     v$filestat fs
WHERE df.file_id = fs.file#
ORDER BY fs.phyrds + fs.phywrts DESC;

-- Tablespace I/O statistics
SELECT ts.name as tablespace_name,
       SUM(fs.phyrds) as total_reads,
       SUM(fs.phywrts) as total_writes,
       SUM(fs.readtim) as total_read_time,
       SUM(fs.writetim) as total_write_time
FROM v$tablespace ts,
     v$datafile df,
     v$filestat fs
WHERE ts.ts# = df.ts#
  AND df.file# = fs.file#
GROUP BY ts.name
ORDER BY total_reads + total_writes DESC;
```

#### Wait Event Analysis

```sql
-- I/O related wait events
SELECT event,
       total_waits,
       total_timeouts,
       time_waited,
       average_wait
FROM v$system_event
WHERE event LIKE '%read%' OR event LIKE '%write%'
ORDER BY time_waited DESC;

-- Session I/O waits
SELECT sid,
       event,
       seconds_in_wait,
       state,
       p1text,
       p1,
       p2text,
       p2
FROM v$session_wait
WHERE event LIKE '%file%read%' OR event LIKE '%file%write%';
```

### Asynchronous I/O Configuration

#### Enable Async I/O

```sql
-- Enable asynchronous I/O
ALTER SYSTEM SET disk_asynch_io = TRUE;

-- Verify async I/O capability
SELECT name, value
FROM v$parameter
WHERE name = 'disk_asynch_io';

-- Check I/O slaves configuration
SELECT name, value
FROM v$parameter
WHERE name LIKE '%io_slaves%';
```

#### Direct I/O Configuration

```sql
-- Enable direct I/O (OS level configuration)
-- For Oracle on Linux: Use O_DIRECT
-- Set filesystemio_options parameter
ALTER SYSTEM SET filesystemio_options = DIRECTIO;

-- Alternative: Use setall for both direct and async I/O
ALTER SYSTEM SET filesystemio_options = SETALL;
```

## ðŸ"Š Monitoring and Diagnostics

### Automatic Workload Repository (AWR)

#### AWR Configuration

```sql
-- Configure AWR collection interval (60 minutes)
EXEC DBMS_WORKLOAD_REPOSITORY.MODIFY_SNAPSHOT_SETTINGS(
    interval => 60,
    retention => 43200  -- 30 days
);

-- Manual AWR snapshot
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT();

-- AWR baseline creation
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_BASELINE(
    start_snap_id => 100,
    end_snap_id => 200,
    baseline_name => 'peak_workload_baseline'
);
```

#### AWR Reports

```sql
-- Generate AWR report
@$ORACLE_HOME/rdbms/REDACTED_LDAP_BIND_PASSWORD/awrrpt.sql

-- Generate AWR comparison report
@$ORACLE_HOME/rdbms/REDACTED_LDAP_BIND_PASSWORD/awrddrpt.sql

-- SQL-specific AWR report
@$ORACLE_HOME/rdbms/REDACTED_LDAP_BIND_PASSWORD/awrsqrpt.sql
```

### Active Session History (ASH)

#### ASH Analysis

```sql
-- Top wait events in last hour
SELECT event,
       COUNT(*) as sample_count,
       ROUND(COUNT(*) * 10 / 3600 * 100, 2) as pct_activity
FROM v$active_session_history
WHERE sample_time >= SYSDATE - 1/24
  AND event IS NOT NULL
GROUP BY event
ORDER BY sample_count DESC;

-- Top SQL by CPU usage
SELECT sql_id,
       COUNT(*) as cpu_samples,
       ROUND(COUNT(*) * 10 / 3600 * 100, 2) as pct_cpu
FROM v$active_session_history
WHERE sample_time >= SYSDATE - 1/24
  AND session_state = 'ON CPU'
GROUP BY sql_id
ORDER BY cpu_samples DESC;

-- Session activity analysis
SELECT session_id,
       session_serial#,
       user_id,
       program,
       COUNT(*) as samples,
       COUNT(DISTINCT sql_id) as distinct_sql
FROM v$active_session_history
WHERE sample_time >= SYSDATE - 1/24
GROUP BY session_id, session_serial#, user_id, program
ORDER BY samples DESC;
```

#### ASH Reports

```sql
-- Generate ASH report
@$ORACLE_HOME/rdbms/REDACTED_LDAP_BIND_PASSWORD/ashrpt.sql

-- ASH Global report (for RAC)
@$ORACLE_HOME/rdbms/REDACTED_LDAP_BIND_PASSWORD/ashrpti.sql
```

### Real-Time SQL Monitoring

#### SQL Monitoring

```sql
-- Monitor long-running SQL
SELECT sql_id,
       status,
       start_time,
       elapsed_time/1000000 as elapsed_seconds,
       cpu_time/1000000 as cpu_seconds,
       buffer_gets,
       disk_reads
FROM v$sql_monitor
WHERE status = 'EXECUTING'
ORDER BY start_time;

-- Generate SQL monitoring report
SELECT DBMS_SQLTUNE.REPORT_SQL_MONITOR(
    sql_id => 'sql_id_here',
    type => 'HTML'
) FROM DUAL;
```

### Performance Views

#### Key Performance Views

```sql
-- System statistics
SELECT name, value
FROM v$sysstat
WHERE name IN ('user calls',
               'recursive calls',
               'db block gets',
               'consistent gets',
               'physical reads',
               'redo size',
               'sorts (memory)',
               'sorts (disk)');

-- Wait events
SELECT event,
       total_waits,
       total_timeouts,
       time_waited,
       average_wait
FROM v$system_event
WHERE wait_class != 'Idle'
ORDER BY time_waited DESC;

-- Session statistics
SELECT s.sid,
       s.serial#,
       s.username,
       s.program,
       st.value as logical_reads
FROM v$session s,
     v$sesstat st,
     v$statname sn
WHERE s.sid = st.sid
  AND st.statistic# = sn.statistic#
  AND sn.name = 'session logical reads'
  AND st.value > 0
ORDER BY st.value DESC;
```

## ðŸ¤– Automatic Performance Features

### Automatic Database Diagnostic Monitor (ADDM)

#### ADDM Configuration

```sql
-- ADDM runs automatically with each AWR snapshot
-- Manual ADDM analysis
DECLARE
    task_name VARCHAR2(30);
BEGIN
    task_name := DBMS_ADDM.ANALYZE_DB(
        begin_snapshot => 100,
        end_snapshot => 200,
        db_id => (SELECT dbid FROM v$database)
    );

    -- View ADDM findings
    SELECT DBMS_ADDM.GET_REPORT(task_name) FROM DUAL;
END;
/
```

#### ADDM Findings Analysis

```sql
-- View ADDM findings
SELECT task_name,
       finding_id,
       finding_name,
       type,
       impact_type,
       impact
FROM dba_advisor_findings
WHERE task_name LIKE 'ADDM%'
ORDER BY impact DESC;

-- View ADDM recommendations
SELECT task_name,
       finding_id,
       recommendation_id,
       type,
       benefit,
       rationale
FROM dba_advisor_recommendations
WHERE task_name LIKE 'ADDM%'
ORDER BY benefit DESC;
```

### SQL Tuning Advisor

#### Automatic SQL Tuning

```sql
-- Enable automatic SQL tuning
EXEC DBMS_AUTO_TASK_ADMIN.ENABLE(
    client_name => 'sql tuning advisor',
    operation => NULL,
    window_name => NULL
);

-- Configure automatic SQL tuning
EXEC DBMS_SQLTUNE.SET_TUNING_TASK_PARAMETER(
    task_name => 'SYS_AUTO_SQL_TUNING_TASK',
    parameter => 'ACCEPT_SQL_PROFILES',
    value => 'TRUE'
);
```

#### Manual SQL Tuning

```sql
-- Create tuning task
DECLARE
    task_name VARCHAR2(30);
BEGIN
    task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
        sql_id => 'sql_id_here',
        task_name => 'manual_tune_task'
    );

    -- Execute tuning task
    DBMS_SQLTUNE.EXECUTE_TUNING_TASK('manual_tune_task');

    -- View recommendations
    SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK('manual_tune_task') FROM DUAL;
END;
/
```

### Automatic Statistics Collection

#### Statistics Configuration

```sql
-- Enable automatic statistics collection
EXEC DBMS_AUTO_TASK_ADMIN.ENABLE(
    client_name => 'auto optimizer stats collection',
    operation => NULL,
    window_name => NULL
);

-- Configure statistics preferences
EXEC DBMS_STATS.SET_GLOBAL_PREFS(
    pname => 'ESTIMATE_PERCENT',
    pvalue => 'AUTO_SAMPLE_SIZE'
);

EXEC DBMS_STATS.SET_GLOBAL_PREFS(
    pname => 'METHOD_OPT',
    pvalue => 'FOR ALL COLUMNS SIZE AUTO'
);

EXEC DBMS_STATS.SET_GLOBAL_PREFS(
    pname => 'DEGREE',
    pvalue => 'AUTO'
);
```

#### Manual Statistics Collection

```sql
-- Gather table statistics
EXEC DBMS_STATS.GATHER_TABLE_STATS(
    ownname => 'SCHEMA_NAME',
    tabname => 'TABLE_NAME',
    estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO',
    degree => DBMS_STATS.AUTO_DEGREE,
    cascade => TRUE
);

-- Gather schema statistics
EXEC DBMS_STATS.GATHER_SCHEMA_STATS(
    ownname => 'SCHEMA_NAME',
    estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO',
    degree => DBMS_STATS.AUTO_DEGREE,
    cascade => TRUE
);

-- Gather system statistics
EXEC DBMS_STATS.GATHER_SYSTEM_STATS('EXADATA');
```

## ðŸ› ï¸ Performance Tools

### Oracle Enterprise Manager (OEM)

#### Performance Hub

- **Real-time Performance Monitoring**
- **Historical Performance Analysis**
- **SQL Monitoring**
- **ASH Analytics**
- **AWR and ADDM Integration**

#### Performance Tools in OEM

- **SQL Tuning Advisor Integration**
- **SQL Access Advisor**
- **Memory Advisor**
- **Segment Advisor**
- **Undo Advisor**

### SQL Developer Performance Tools

#### SQL Tuning Features

- **Explain Plan Visualization**
- **Autotrace Functionality**
- **SQL Worksheet with Statistics**
- **Real-time SQL Monitor Integration**

### Third-Party Tools

#### Popular Performance Tools

- **Toad for Oracle**: Database development and tuning
- **Quest Spotlight**: Real-time performance monitoring
- **SolarWinds Database Performance Analyzer**: Historical analysis
- **Precise**: Application performance monitoring
- **AppDynamics**: End-to-end application monitoring

### Command-Line Tools

#### SQL\*Plus Performance Commands

```sql
-- Enable autotrace
SET AUTOTRACE ON EXPLAIN STATISTICS

-- Show timing
SET TIMING ON

-- Show SQL execution statistics
SET STATISTICS ON

-- Display execution plan
EXPLAIN PLAN FOR your_sql_statement;
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

#### TKPROF Utility

```bash
# Enable SQL trace
ALTER SESSION SET SQL_TRACE = TRUE;

# Enable 10046 trace with wait events
ALTER SESSION SET EVENTS '10046 trace name context forever, level 12';

# Format trace file with TKPROF
tkprof trace_file.trc output_file.txt explain=username/password
```

## ðŸš¨ Troubleshooting Common Issues

### High CPU Usage

#### Diagnosis Steps

1. **Identify CPU-consuming sessions**

```sql
SELECT s.sid,
       s.serial#,
       s.username,
       s.program,
       s.cpu_time,
       sq.sql_text
FROM v$session s,
     v$sql sq
WHERE s.sql_id = sq.sql_id(+)
  AND s.status = 'ACTIVE'
ORDER BY s.cpu_time DESC;
```

2. **Analyze top CPU-consuming SQL**

```sql
SELECT sql_id,
       executions,
       cpu_time,
       cpu_time/executions as avg_cpu_per_exec,
       sql_text
FROM v$sql
WHERE cpu_time > 1000000  -- More than 1 second total CPU
ORDER BY cpu_time DESC;
```

#### Common Causes and Solutions

- **Inefficient SQL statements**: Tune problematic queries
- **Missing indexes**: Create appropriate indexes
- **Full table scans**: Add indexes or improve predicates
- **Excessive parsing**: Use bind variables
- **CPU-intensive functions**: Optimize PL/SQL code

### High I/O Wait Times

#### Diagnosis Steps

1. **Identify I/O wait events**

```sql
SELECT event,
       total_waits,
       time_waited,
       average_wait
FROM v$system_event
WHERE event LIKE '%read%' OR event LIKE '%write%'
ORDER BY time_waited DESC;
```

2. **Analyze file I/O distribution**

```sql
SELECT df.tablespace_name,
       df.file_name,
       fs.phyrds + fs.phywrts as total_ios,
       fs.readtim + fs.writetim as total_wait_time,
       (fs.readtim + fs.writetim)/(fs.phyrds + fs.phywrts) as avg_wait_time
FROM dba_data_files df,
     v$filestat fs
WHERE df.file_id = fs.file#
  AND fs.phyrds + fs.phywrts > 0
ORDER BY total_wait_time DESC;
```

#### Common Causes and Solutions

- **Hot data files**: Redistribute I/O across multiple devices
- **Inefficient storage**: Use faster storage (SSD)
- **Large table scans**: Create indexes or partition tables
- **Redo log contention**: Increase redo log size or add groups
- **Temporary space contention**: Add temporary files

### Memory Pressure

#### Diagnosis Steps

1. **Check memory allocation**

```sql
SELECT component,
       current_size/1024/1024 as current_mb,
       min_size/1024/1024 as min_mb,
       max_size/1024/1024 as max_mb
FROM v$memory_dynamic_components
ORDER BY current_size DESC;
```

2. **Analyze PGA usage**

```sql
SELECT name,
       value/1024/1024 as value_mb,
       unit
FROM v$pgastat
WHERE name IN ('aggregate PGA target parameter',
               'total PGA allocated',
               'maximum PGA allocated',
               'PGA memory freed back to OS');
```

#### Common Causes and Solutions

- **Undersized SGA**: Increase SGA target
- **PGA pressure**: Increase PGA aggregate target
- **Memory leaks**: Identify and fix application issues
- **Large sorts**: Optimize SQL or increase temp space
- **Session memory**: Review session-specific memory usage

### Lock Contention

#### Diagnosis Steps

1. **Identify blocking sessions**

```sql
SELECT blocking_session,
       sid,
       serial#,
       username,
       program,
       seconds_in_wait,
       event
FROM v$session
WHERE blocking_session IS NOT NULL;
```

2. **Analyze lock types**

```sql
SELECT l.sid,
       l.type,
       l.lmode,
       l.request,
       l.block,
       o.object_name
FROM v$lock l,
     dba_objects o
WHERE l.id1 = o.object_id(+)
  AND l.type IN ('TM', 'TX')
ORDER BY l.block DESC;
```

#### Common Causes and Solutions

- **Long-running transactions**: Commit more frequently
- **Missing indexes on foreign keys**: Create indexes
- **Application design issues**: Review transaction design
- **Deadlocks**: Analyze and resolve deadlock patterns
- **Hot blocks**: Redesign application or data distribution

### Poor SQL Performance

#### Diagnosis Steps

1. **Identify slow SQL**

```sql
SELECT sql_id,
       elapsed_time/1000000 as elapsed_seconds,
       cpu_time/1000000 as cpu_seconds,
       executions,
       elapsed_time/executions/1000000 as avg_elapsed,
       sql_text
FROM v$sql
WHERE elapsed_time > 10000000  -- More than 10 seconds total
  AND executions > 0
ORDER BY elapsed_time DESC;
```

2. **Analyze execution plans**

```sql
-- For specific SQL_ID
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR('sql_id_here', NULL, 'ALLSTATS LAST'));
```

#### Common Causes and Solutions

- **Missing statistics**: Gather current statistics
- **Outdated statistics**: Refresh statistics
- **Missing indexes**: Create appropriate indexes
- **Poor join order**: Use hints or rewrite query
- **Inefficient predicates**: Improve WHERE clauses

## ðŸ"š Additional Resources

### Oracle Documentation

- [Database Performance Tuning Guide](https://docs.oracle.com/en/database/oracle/oracle-database/19/tgdba/)
- [SQL Tuning Guide](https://docs.oracle.com/en/database/oracle/oracle-database/19/tgsql/)
- [Database Reference](https://docs.oracle.com/en/database/oracle/oracle-database/19/refrn/)

### Performance Tuning Scripts

- [AWR Analysis Scripts](./scripts/awr-analysis.sql)
- [ASH Analysis Scripts](./scripts/ash-analysis.sql)
- [SQL Tuning Scripts](./scripts/sql-tuning.sql)
- [I/O Analysis Scripts](./scripts/io-analysis.sql)

### Best Practices

- [Performance Tuning Best Practices](./best-practices/performance-tuning.md)
- [SQL Optimization Guidelines](./best-practices/sql-optimization.md)
- [Memory Management Best Practices](./best-practices/memory-management.md)

---

**Last Updated**: December 2024
**Version**: 1.0
**Maintainer**: Oracle Core Shared Team

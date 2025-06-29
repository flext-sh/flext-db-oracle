# Oracle Database Architecture Documentation

This section provides comprehensive documentation on Oracle Database architecture, internals, and advanced concepts.

## 📋 Table of Contents

- [Database Architecture Overview](#database-architecture-overview)
- [Memory Structures](#memory-structures)
- [Process Architecture](#process-architecture)
- [Storage Structures](#storage-structures)
- [Transaction Management](#transaction-management)
- [Query Processing](#query-processing)
- [Advanced Features](#advanced-features)
- [Performance Architecture](#performance-architecture)
- [High Availability Architecture](#high-availability-architecture)
- [Security Architecture](#security-architecture)

## 🏗️ Database Architecture Overview

### Oracle Database Instance

An Oracle Database instance consists of:

- **Memory structures** (SGA and PGA)
- **Background processes**
- **Parameter files**
- **Alert and trace files**

### Oracle Database

An Oracle Database consists of:

- **Physical structures** (data files, control files, redo log files)
- **Logical structures** (tablespaces, segments, extents, blocks)
- **Schema objects** (tables, indexes, views, procedures)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Oracle Database Architecture              │
├─────────────────────────────────────────────────────────────┤
│  User Processes                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Client    │  │   Client    │  │   Client    │         │
│  │ Application │  │ Application │  │ Application │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
├─────────────────────────────────────────────────────────────┤
│  Oracle Instance                                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ System Global Area (SGA)                               │ │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │ │
│  │ │   Shared    │ │   Database  │ │    Redo     │       │ │
│  │ │    Pool     │ │   Buffer    │ │    Log      │       │ │
│  │ │             │ │    Cache    │ │   Buffer    │       │ │
│  │ └─────────────┘ └─────────────┘ └─────────────┘       │ │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │ │
│  │ │    Large    │ │    Java     │ │   Streams   │       │ │
│  │ │    Pool     │ │    Pool     │ │    Pool     │       │ │
│  │ └─────────────┘ └─────────────┘ └─────────────┘       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  Background Processes                                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │  PMON   │ │  SMON   │ │  DBWR   │ │  LGWR   │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │  CKPT   │ │  ARCH   │ │  RECO   │ │  MMON   │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
├─────────────────────────────────────────────────────────────┤
│  Oracle Database                                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Physical Structures                                     │ │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │ │
│  │ │    Data     │ │   Control   │ │    Redo     │       │ │
│  │ │    Files    │ │    Files    │ │     Log     │       │ │
│  │ │             │ │             │ │    Files    │       │ │
│  │ └─────────────┘ └─────────────┘ └─────────────┘       │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🧠 Memory Structures

### System Global Area (SGA)

The SGA is a shared memory region that contains:

#### Database Buffer Cache

- **Purpose**: Caches frequently accessed data blocks
- **Components**:
  - Default buffer pool
  - Keep buffer pool
  - Recycle buffer pool
  - Non-standard block size pools
- **Management**: LRU (Least Recently Used) algorithm
- **Sizing**: `DB_CACHE_SIZE` parameter

#### Shared Pool

- **Purpose**: Caches SQL statements, PL/SQL code, and data dictionary
- **Components**:
  - Library cache (SQL and PL/SQL)
  - Data dictionary cache
  - Server result cache
  - Reserved pool
- **Sizing**: `SHARED_POOL_SIZE` parameter

#### Redo Log Buffer

- **Purpose**: Caches redo entries before writing to redo log files
- **Characteristics**:
  - Circular buffer
  - Written by LGWR process
  - Critical for transaction recovery
- **Sizing**: `LOG_BUFFER` parameter

#### Large Pool

- **Purpose**: Optional pool for large memory allocations
- **Uses**:
  - Parallel execution
  - RMAN backup operations
  - Shared server processes
- **Sizing**: `LARGE_POOL_SIZE` parameter

#### Java Pool

- **Purpose**: Memory for Java Virtual Machine (JVM)
- **Uses**:
  - Java stored procedures
  - Java applications in database
- **Sizing**: `JAVA_POOL_SIZE` parameter

#### Streams Pool

- **Purpose**: Memory for Oracle Streams operations
- **Uses**:
  - Capture processes
  - Apply processes
  - Buffered queues
- **Sizing**: `STREAMS_POOL_SIZE` parameter

### Program Global Area (PGA)

The PGA is a private memory region for each server process:

#### Components

- **SQL Work Areas**:
  - Sort area
  - Hash area
  - Bitmap merge area
  - Bitmap create area
- **Session Information**:
  - Session variables
  - Cursor state
  - Stack space
- **Private SQL Area**:
  - Bind information
  - Runtime memory structures

#### PGA Memory Management

- **Automatic PGA Memory Management**: `PGA_AGGREGATE_TARGET`
- **Manual PGA Management**: Individual work area parameters
- **PGA Advisor**: Helps optimize PGA memory allocation

## ⚙️ Process Architecture

### User Processes

#### Client Processes

- **SQL\*Plus**: Command-line interface
- **SQL Developer**: Graphical development tool
- **Application processes**: Custom applications
- **Web browser**: For APEX applications

#### Server Processes

- **Dedicated server**: One server process per user session
- **Shared server**: Multiple user sessions share server processes
- **Connection pooling**: Efficient resource utilization

### Background Processes

#### Mandatory Background Processes

##### Process Monitor (PMON)

- **Purpose**: Process cleanup and recovery
- **Functions**:
  - Cleans up failed user processes
  - Releases locks and resources
  - Registers database with listener
  - Monitors dispatcher and shared server processes

##### System Monitor (SMON)

- **Purpose**: Instance and system-level recovery
- **Functions**:
  - Instance recovery at startup
  - Cleans up temporary segments
  - Coalesces free space
  - Recovers failed transactions

##### Database Writer (DBWn)

- **Purpose**: Writes dirty buffers to data files
- **Characteristics**:
  - Multiple DBWn processes possible (DBW0-DBW9, DBWa-DBWj)
  - Triggered by checkpoints, clean shutdown, tablespace offline
  - Uses asynchronous I/O when possible

##### Log Writer (LGWR)

- **Purpose**: Writes redo log buffer to redo log files
- **Triggers**:
  - Commit issued
  - Redo log buffer 1/3 full
  - Every 3 seconds
  - Before DBWn writes

##### Checkpoint (CKPT)

- **Purpose**: Updates control files and data file headers
- **Functions**:
  - Signals DBWn to write dirty buffers
  - Updates checkpoint information
  - Ensures data file consistency

#### Optional Background Processes

##### Archiver (ARCn)

- **Purpose**: Archives filled redo log files
- **Characteristics**:
  - Multiple archiver processes (ARC0-ARC9, ARCa-ARCt)
  - Only active in ARCHIVELOG mode
  - Critical for point-in-time recovery

##### Recoverer (RECO)

- **Purpose**: Resolves distributed transaction failures
- **Functions**:
  - Automatically resolves in-doubt transactions
  - Connects to remote databases
  - Commits or rolls back pending transactions

##### Manageability Monitor (MMON)

- **Purpose**: Automatic Workload Repository (AWR) data collection
- **Functions**:
  - Captures performance statistics
  - Triggers alerts
  - Manages automatic statistics collection

##### Memory Monitor (MMNL)

- **Purpose**: Assists MMON with AWR data
- **Functions**:
  - Writes Active Session History (ASH) data
  - Captures lightweight performance data

##### Queue Monitor (QMNn)

- **Purpose**: Advanced Queuing message processing
- **Functions**:
  - Monitors message queues
  - Processes time-based messages
  - Handles queue propagation

##### Job Queue Coordinator (CJQ0)

- **Purpose**: Coordinates job queue processes
- **Functions**:
  - Manages job queue slaves
  - Schedules job execution
  - Monitors job failures

##### Space Management Coordinator (SMCO)

- **Purpose**: Coordinates space management tasks
- **Functions**:
  - Proactive space management
  - Automatic segment space management
  - Space usage monitoring

## 💾 Storage Structures

### Physical Storage Structures

#### Data Files

- **Purpose**: Store database data
- **Characteristics**:
  - One or more per tablespace
  - Can be autoextended
  - Can be resized online
- **Types**:
  - System data files (SYSTEM, SYSAUX)
  - User data files
  - Temporary data files
  - Undo data files

#### Control Files

- **Purpose**: Store database metadata
- **Contents**:
  - Database name and identifier
  - Data file and redo log file locations
  - Checkpoint information
  - RMAN backup metadata
- **Characteristics**:
  - Multiple copies recommended
  - Binary format
  - Updated continuously

#### Redo Log Files

- **Purpose**: Record all database changes
- **Characteristics**:
  - Circular reuse pattern
  - Multiple groups with multiple members
  - Critical for recovery
- **Types**:
  - Online redo log files
  - Archived redo log files

#### Parameter Files

- **Types**:
  - **PFILE**: Text-based parameter file
  - **SPFILE**: Binary server parameter file
- **Contents**:
  - Instance configuration parameters
  - Database initialization parameters
  - Memory allocation settings

#### Password Files

- **Purpose**: Authenticate privileged users
- **Characteristics**:
  - Stores SYSDBA/SYSOPER passwords
  - Can be shared across RAC instances
  - Supports case-sensitive passwords

### Logical Storage Structures

#### Tablespaces

- **Purpose**: Logical storage containers
- **Types**:
  - **Permanent**: Regular data storage
  - **Temporary**: Sort operations and temporary tables
  - **Undo**: Undo data for transactions
- **Management**:
  - Dictionary-managed
  - Locally-managed (preferred)

#### Segments

- **Purpose**: Storage for database objects
- **Types**:
  - **Table segments**: Store table data
  - **Index segments**: Store index data
  - **Undo segments**: Store undo data
  - **Temporary segments**: Temporary storage
  - **LOB segments**: Large object storage
  - **Cluster segments**: Store clustered tables

#### Extents

- **Purpose**: Contiguous sets of data blocks
- **Characteristics**:
  - Allocated to segments
  - Size determined by storage parameters
  - Can be uniform or variable size

#### Data Blocks

- **Purpose**: Smallest unit of I/O
- **Structure**:
  - **Header**: Block metadata
  - **Table directory**: Table information
  - **Row directory**: Row location information
  - **Free space**: Available space
  - **Row data**: Actual data

#### Block Structure Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Oracle Data Block                        │
├─────────────────────────────────────────────────────────────┤
│ Block Header                                                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Block Type | Block Address | SCN | Checksum | Flags     │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Table Directory                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Table 1 Info | Table 2 Info | ... | Table n Info       │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Row Directory                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Row 1 Offset | Row 2 Offset | ... | Row n Offset       │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Free Space                                                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                   Available Space                       │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Row Data                                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Row n Data | ... | Row 2 Data | Row 1 Data             │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Transaction Management

### ACID Properties

#### Atomicity

- **Definition**: All or nothing transaction execution
- **Implementation**: Undo segments and rollback
- **Mechanisms**:
  - Savepoints for partial rollback
  - Automatic rollback on failure
  - Explicit rollback commands

#### Consistency

- **Definition**: Database remains in valid state
- **Implementation**: Constraints and triggers
- **Mechanisms**:
  - Primary key constraints
  - Foreign key constraints
  - Check constraints
  - Trigger validation

#### Isolation

- **Definition**: Concurrent transactions don't interfere
- **Implementation**: Locking and multiversion concurrency
- **Levels**:
  - Read Uncommitted
  - Read Committed (Oracle default)
  - Repeatable Read
  - Serializable

#### Durability

- **Definition**: Committed changes are permanent
- **Implementation**: Redo logs and recovery
- **Mechanisms**:
  - Write-ahead logging
  - Checkpoint processing
  - Archive log retention

### Concurrency Control

#### Locking Mechanisms

##### Row-Level Locking

- **Characteristics**:
  - Automatic and transparent
  - No lock escalation
  - Minimal blocking
- **Types**:
  - Shared locks (S)
  - Exclusive locks (X)

##### Table-Level Locking

- **Types**:
  - Row Share (RS)
  - Row Exclusive (RX)
  - Share (S)
  - Share Row Exclusive (SRX)
  - Exclusive (X)

##### Deadlock Detection

- **Mechanism**: Automatic deadlock detection
- **Resolution**: Automatic deadlock resolution
- **Notification**: ORA-00060 error to victim

#### Multiversion Concurrency Control (MVCC)

##### Read Consistency

- **Statement-level**: Consistent view for single statement
- **Transaction-level**: Consistent view for entire transaction
- **Implementation**: Undo segments and SCN

##### Flashback Query

- **Purpose**: Query data as of specific time/SCN
- **Syntax**: `AS OF TIMESTAMP` or `AS OF SCN`
- **Limitations**: Undo retention period

### Undo Management

#### Automatic Undo Management

- **Configuration**: `UNDO_MANAGEMENT = AUTO`
- **Tablespace**: Dedicated undo tablespace
- **Retention**: `UNDO_RETENTION` parameter

#### Undo Segments

- **Purpose**: Store before-images of changed data
- **Types**:
  - System undo segments
  - Non-system undo segments
- **Lifecycle**:
  - Active: Currently in use
  - Expired: Past retention period
  - Unexpired: Within retention period

## 🔍 Query Processing

### SQL Processing Phases

#### Parse Phase

1. **Syntax Check**: Verify SQL syntax
2. **Semantic Check**: Verify object existence and privileges
3. **Shared Pool Check**: Look for existing parsed statement
4. **Optimization**: Generate execution plan
5. **Row Source Generation**: Create execution tree

#### Execute Phase

1. **Bind Variable Processing**: Substitute bind values
2. **Privilege Verification**: Final privilege check
3. **SQL Execution**: Execute the generated plan
4. **Return Results**: Fetch and return data

#### Fetch Phase

1. **Array Processing**: Fetch multiple rows
2. **Network Transmission**: Send data to client
3. **Cursor Management**: Maintain cursor state

### Query Optimizer

#### Cost-Based Optimizer (CBO)

- **Purpose**: Generate optimal execution plans
- **Factors**:
  - Table and index statistics
  - System statistics
  - Hardware characteristics
  - Optimizer parameters

#### Statistics Collection

- **Automatic**: `DBMS_STATS` automatic collection
- **Manual**: Explicit statistics gathering
- **Types**:
  - Table statistics (row count, block count)
  - Column statistics (distinct values, histograms)
  - Index statistics (clustering factor, height)
  - System statistics (CPU speed, I/O performance)

#### Execution Plans

- **Components**:
  - Operations (Table Scan, Index Scan, Join)
  - Cost estimates
  - Cardinality estimates
  - Access methods

#### Plan Stability

- **SQL Plan Baselines**: Prevent plan regression
- **SQL Profiles**: Additional optimizer information
- **Stored Outlines**: Legacy plan stability (deprecated)

### Join Methods

#### Nested Loop Join

- **Characteristics**: Good for small result sets
- **Algorithm**: For each row in outer table, scan inner table
- **Use cases**: OLTP queries with selective predicates

#### Hash Join

- **Characteristics**: Good for large result sets
- **Algorithm**: Build hash table on smaller table, probe with larger
- **Use cases**: Data warehouse queries

#### Sort-Merge Join

- **Characteristics**: Both inputs sorted on join key
- **Algorithm**: Merge sorted inputs
- **Use cases**: Large tables with pre-sorted data

## 🚀 Advanced Features

### Partitioning

#### Partitioning Methods

- **Range Partitioning**: Based on value ranges
- **List Partitioning**: Based on discrete value lists
- **Hash Partitioning**: Based on hash function
- **Composite Partitioning**: Combination of methods

#### Benefits

- **Performance**: Partition elimination
- **Manageability**: Partition-wise operations
- **Availability**: Partition-level maintenance

### Parallel Processing

#### Parallel Query

- **Purpose**: Distribute query processing across multiple processes
- **Degree of Parallelism**: Number of parallel processes
- **Parallel Operations**:
  - Table scans
  - Index scans
  - Joins
  - Sorts
  - Aggregations

#### Parallel DML

- **Operations**: INSERT, UPDATE, DELETE
- **Requirements**: Partitioned tables (typically)
- **Restrictions**: Same-session query restrictions

#### Parallel DDL

- **Operations**: CREATE TABLE AS SELECT, CREATE INDEX
- **Benefits**: Faster object creation
- **Considerations**: Resource utilization

### Advanced Security

#### Virtual Private Database (VPD)

- **Purpose**: Row-level security
- **Implementation**: Security policies and functions
- **Types**:
  - Static policies
  - Dynamic policies
  - Context-sensitive policies

#### Oracle Label Security (OLS)

- **Purpose**: Multi-level security
- **Components**:
  - Labels
  - Levels
  - Compartments
  - Groups

#### Transparent Data Encryption (TDE)

- **Purpose**: Encrypt sensitive data
- **Types**:
  - Column-level encryption
  - Tablespace encryption
- **Key Management**: Oracle Wallet or HSM

### Advanced Compression

#### Basic Table Compression

- **Purpose**: Reduce storage requirements
- **Method**: Dictionary-based compression
- **Use cases**: Read-mostly data

#### Advanced Compression

- **OLTP Compression**: For frequently updated data
- **Warehouse Compression**: For data warehouse workloads
- **Archive Compression**: Maximum compression ratio

#### Hybrid Columnar Compression (HCC)

- **Purpose**: Extreme compression for Exadata
- **Methods**:
  - Query Low
  - Query High
  - Archive Low
  - Archive High

## 📊 Performance Architecture

### Buffer Cache Management

#### Buffer States

- **Free**: Available for new data
- **Clean**: Contains valid data, not modified
- **Dirty**: Contains modified data, needs writing

#### Replacement Algorithms

- **LRU**: Least Recently Used
- **Touch Count**: Frequency-based replacement
- **Multiple Buffer Pools**: Different replacement strategies

### I/O Architecture

#### Synchronous I/O

- **Characteristics**: Process waits for I/O completion
- **Use cases**: Small, random I/O operations
- **Performance**: Limited by I/O latency

#### Asynchronous I/O

- **Characteristics**: Process continues while I/O in progress
- **Use cases**: Large, sequential I/O operations
- **Performance**: Higher throughput

#### Direct I/O

- **Purpose**: Bypass OS buffer cache
- **Benefits**: Reduced memory usage, more predictable performance
- **Considerations**: Requires careful configuration

### Wait Events

#### Common Wait Events

- **db file sequential read**: Single block reads
- **db file scattered read**: Multi-block reads
- **log file sync**: Redo log writes
- **enq: TX - row lock contention**: Row locking waits
- **latch: shared pool**: Shared pool contention

#### Wait Event Analysis

- **Purpose**: Identify performance bottlenecks
- **Tools**: AWR, ASH, V$SESSION_WAIT
- **Methodology**: Top-down analysis approach

## 🔧 High Availability Architecture

### Oracle Real Application Clusters (RAC)

#### Architecture Components

- **Shared Storage**: All nodes access same database files
- **Cluster Interconnect**: High-speed network for inter-node communication
- **Voting Disks**: Cluster membership determination
- **Oracle Cluster Registry (OCR)**: Cluster configuration information

#### Cache Fusion

- **Purpose**: Share data blocks between instances
- **Mechanism**: Direct instance-to-instance transfers
- **Benefits**: Eliminates disk I/O for shared data

#### Services and Load Balancing

- **Database Services**: Logical representation of workloads
- **Connection Load Balancing**: Distribute connections
- **Runtime Load Balancing**: Redirect work based on performance

### Oracle Data Guard

#### Architecture Types

- **Physical Standby**: Block-for-block identical copy
- **Logical Standby**: Logically identical, different physical structure
- **Snapshot Standby**: Updateable copy for testing

#### Protection Modes

- **Maximum Protection**: Zero data loss, synchronous
- **Maximum Availability**: Zero data loss, asynchronous fallback
- **Maximum Performance**: Minimal performance impact

#### Redo Transport and Apply

- **LGWR SYNC**: Synchronous redo transport
- **LGWR ASYNC**: Asynchronous redo transport
- **ARCH**: Archive-based redo transport
- **MRP**: Managed Recovery Process for apply

### Automatic Storage Management (ASM)

#### Architecture Benefits

- **Simplified Storage Management**: Automatic file management
- **Load Balancing**: Automatic I/O distribution
- **Redundancy**: Built-in mirroring capabilities
- **Online Operations**: Dynamic storage management

#### ASM Components

- **ASM Instance**: Manages storage metadata
- **ASM Disk Groups**: Collections of disks
- **ASM Files**: Database files stored in ASM
- **ASMCMD**: Command-line interface

## 🛡️ Security Architecture

### Authentication Methods

#### Database Authentication

- **Password Files**: For privileged users
- **OS Authentication**: Using OS credentials
- **Network Authentication**: Kerberos, RADIUS, LDAP

#### External Authentication

- **LDAP Integration**: Centralized user management
- **Single Sign-On (SSO)**: Seamless authentication
- **PKI Authentication**: Certificate-based authentication

### Authorization Framework

#### System Privileges

- **Categories**: Database REDACTED_LDAP_BIND_PASSWORDistration, object management
- **Granting**: Direct grants or through roles
- **Hierarchy**: Some privileges imply others

#### Object Privileges

- **Types**: SELECT, INSERT, UPDATE, DELETE, etc.
- **Granularity**: Table, column, or row level
- **Inheritance**: Through roles and grants

#### Roles

- **Purpose**: Group related privileges
- **Types**: Predefined and user-defined
- **Security**: Can be password-protected

### Auditing Architecture

#### Standard Auditing

- **Database Auditing**: Track database activities
- **OS Auditing**: Audit to operating system
- **Network Auditing**: Track network activities

#### Fine-Grained Auditing (FGA)

- **Purpose**: Audit specific data access
- **Triggers**: Based on content or context
- **Policies**: Define what to audit

#### Unified Auditing

- **Purpose**: Consolidated auditing framework
- **Benefits**: Single audit trail, better performance
- **Components**: Audit policies and unified audit trail

## 📚 Additional Resources

### Oracle Documentation

- [Database Concepts Guide](https://docs.oracle.com/en/database/oracle/oracle-database/19/cncpt/)
- [Database Administrator's Guide](https://docs.oracle.com/en/database/oracle/oracle-database/19/REDACTED_LDAP_BIND_PASSWORD/)
- [Performance Tuning Guide](https://docs.oracle.com/en/database/oracle/oracle-database/19/tgdba/)

### Architecture Deep Dives

- [Oracle Database Architecture](./detailed-architecture.md)
- [Memory Management](./memory-management.md)
- [Storage Internals](./storage-internals.md)
- [Process Deep Dive](./process-architecture.md)

### Best Practices

- [Architecture Best Practices](./best-practices.md)
- [Performance Architecture](./performance-architecture.md)
- [Security Architecture](./security-architecture.md)

---

**Last Updated**: December 2024
**Version**: 1.0
**Maintainer**: Oracle Core Shared Team

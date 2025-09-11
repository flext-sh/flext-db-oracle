# Basic Examples - Oracle Database Core Shared Library

This section provides practical, ready-to-use examples for common Oracle database operations using the Oracle Database Core Shared Library. All examples are designed to be educational and production-ready.

## 🚀 Getting Started Examples

### 1. Basic Database Connection

```python
"""
Basic Oracle database connection example.
Demonstrates secure connection establishment and basic query execution.
"""

import asyncio
from flext_db_oracle.connection import ConnectionConfig, FlextDbFlextDbOracleConnection

async def basic_connection_example():
    """Demonstrate basic database connection and query execution."""

    # Configure connection parameters
    config = ConnectionConfig(
        host="localhost",
        port=1521,
        service_name="ORCL",  # or use sid="ORCL" for SID connection
        user="hr",
        password="secure_password",

        # Optional connection parameters
        pool_min=2,
        pool_max=10,
        pool_increment=2,
        connection_timeout=30,
        retry_count=3
    )

    try:
        # Establish connection
        async with FlextDbOracleConnection(config) as conn:
            print("✅ Successfully connected to Oracle database")

            # Execute simple query
            result = await conn.execute("SELECT SYSDATE FROM DUAL")
            current_time = await result.fetchone()
            print(f"Current database time: {current_time[0]}")

            # Execute query with parameters
            query = """
                SELECT employee_id, first_name, last_name, email, hire_date
                FROM employees
                WHERE department_id = :dept_id
                ORDER BY last_name
            """

            result = await conn.execute(query, {"dept_id": 50})
            employees = await result.fetchall()

            print(f"\nEmployees in department 50:")
            for emp in employees:
                print(f"  {emp[0]}: {emp[1]} {emp[2]} ({emp[3]})")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

# Run the example
if __name__ == "__main__":
    asyncio.run(basic_connection_example())
```

### 2. Environment-Based Configuration

```python
"""
Environment-based configuration example.
Shows how to use environment variables and configuration files.
"""

import os
import asyncio
from pathlib import Path
import yaml
from flext_db_oracle.connection import ConnectionConfig, FlextDbFlextDbOracleConnection

def load_config_from_env():
    """Load database configuration from environment variables."""
    return ConnectionConfig(
        host=os.getenv("ORACLE_HOST", "localhost"),
        port=int(os.getenv("ORACLE_PORT", "1521")),
        service_name=os.getenv("ORACLE_SERVICE_NAME"),
        sid=os.getenv("ORACLE_SID"),  # Alternative to service_name
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),

        # Connection pool settings
        pool_min=int(os.getenv("ORACLE_POOL_MIN", "2")),
        pool_max=int(os.getenv("ORACLE_POOL_MAX", "10")),

        # SSL/TLS settings
        use_ssl=os.getenv("ORACLE_USE_SSL", "false").lower() == "true",
        ssl_ca_cert=os.getenv("ORACLE_SSL_CA_CERT"),
        ssl_cert=os.getenv("ORACLE_SSL_CERT"),
        ssl_key=os.getenv("ORACLE_SSL_KEY")
    )

def load_config_from_file(config_file: str):
    """Load database configuration from YAML file."""
    with open(config_file, 'r') as f:
        config_data = yaml.safe_load(f)

    db_config = config_data['database']
    return ConnectionConfig(**db_config)

async def environment_config_example():
    """Demonstrate environment-based configuration."""

    # Method 1: Environment variables
    print("🔧 Loading configuration from environment variables...")
    env_config = load_config_from_env()

    # Method 2: Configuration file
    config_file = Path("config/database.yaml")
    if config_file.exists():
        print("🔧 Loading configuration from YAML file...")
        file_config = load_config_from_file(str(config_file))
    else:
        print("⚠️ Configuration file not found, using environment config")
        file_config = env_config

    # Use the configuration
    async with FlextDbOracleConnection(file_config) as conn:
        # Test connection with a simple query
        result = await conn.execute("""
            SELECT
                SYS_CONTEXT('USERENV', 'DB_NAME') as db_name,
                SYS_CONTEXT('USERENV', 'SERVER_HOST') as server_host,
                SYS_CONTEXT('USERENV', 'SESSION_USER') as session_user
            FROM DUAL
        """)

        db_info = await result.fetchone()
        print(f"Connected to: {db_info[0]} on {db_info[1]} as {db_info[2]}")

# Example configuration file (config/database.yaml)
example_config = """
database:
  host: "oracle-prod.company.com"
  port: 1521
  service_name: "PROD"
  user: "app_user"
  password: "${ORACLE_PASSWORD}"  # Will be substituted from env var

  # Connection pool settings
  pool_min: 5
  pool_max: 20
  pool_increment: 5
  connection_timeout: 30

  # SSL settings for secure connections
  use_ssl: true
  ssl_ca_cert: "/path/to/ca-cert.pem"

  # Additional options
  retry_count: 3
  query_timeout: 300
"""

if __name__ == "__main__":
    # Create example config file
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    with open(config_dir / "database.yaml", 'w') as f:
        f.write(example_config)

    asyncio.run(environment_config_example())
```

## 📊 Schema Analysis Examples

### 3. Basic Schema Introspection

```python
"""
Schema introspection example.
Demonstrates how to analyze database schema structure.
"""

import asyncio
from flext_db_oracle.connection import ConnectionConfig, FlextDbFlextDbOracleConnection, SchemaAnalyzer

async def schema_analysis_example():
    """Demonstrate basic schema analysis capabilities."""

    config = ConnectionConfig(
        host="localhost",
        port=1521,
        service_name="ORCL",
        user="hr",
        password="password"
    )

    async with FlextDbOracleConnection(config) as conn:
        # Initialize schema analyzer
        analyzer = SchemaAnalyzer(conn)

        # Get schema overview
        print("📊 Analyzing HR schema...")
        schema_info = await analyzer.get_schema_overview("HR")

        print(f"Schema: {schema_info.schema_name}")
        print(f"Tables: {schema_info.table_count}")
        print(f"Views: {schema_info.view_count}")
        print(f"Indexes: {schema_info.index_count}")
        print(f"Procedures: {schema_info.procedure_count}")
        print(f"Functions: {schema_info.function_count}")

        # Analyze specific table
        print("\n🔍 Analyzing EMPLOYEES table...")
        table_info = await analyzer.analyze_table("HR", "EMPLOYEES")

        print(f"Table: {table_info.table_name}")
        print(f"Columns: {len(table_info.columns)}")
        print(f"Indexes: {len(table_info.indexes)}")
        print(f"Constraints: {len(table_info.constraints)}")
        print(f"Estimated rows: {table_info.estimated_rows:,}")
        print(f"Size (MB): {table_info.size_mb:.2f}")

        # Show column details
        print("\nColumn Details:")
        for col in table_info.columns:
            nullable = "NULL" if col.nullable else "NOT NULL"
            print(f"  {col.name}: {col.data_type} {nullable}")

        # Show indexes
        print("\nIndexes:")
        for idx in table_info.indexes:
            unique = "UNIQUE" if idx.is_unique else ""
            columns = ", ".join(idx.columns)
            print(f"  {idx.name}: {unique} INDEX ON ({columns})")

        # Show constraints
        print("\nConstraints:")
        for constraint in table_info.constraints:
            print(f"  {constraint.name}: {constraint.type} - {constraint.definition}")

if __name__ == "__main__":
    asyncio.run(schema_analysis_example())
```

### 4. DDL Generation Example

```python
"""
DDL generation example.
Shows how to generate CREATE statements for database objects.
"""

import asyncio
from pathlib import Path
from flext_db_oracle.connection import ConnectionConfig, FlextDbFlextDbOracleConnection, DDLGenerator

async def ddl_generation_example():
    """Demonstrate DDL generation for database objects."""

    config = ConnectionConfig(
        host="localhost",
        port=1521,
        service_name="ORCL",
        user="hr",
        password="password"
    )

    async with FlextDbOracleConnection(config) as conn:
        # Initialize DDL generator
        ddl_generator = DDLGenerator(conn)

        # Generate DDL for a specific table
        print("🔧 Generating DDL for EMPLOYEES table...")
        table_ddl = await ddl_generator.generate_table_ddl("HR", "EMPLOYEES")

        print("CREATE TABLE Statement:")
        print(table_ddl.create_statement)

        print("\nINDEX Statements:")
        for index_ddl in table_ddl.indexes:
            print(index_ddl)

        print("\nCONSTRAINT Statements:")
        for constraint_ddl in table_ddl.constraints:
            print(constraint_ddl)

        # Generate DDL for entire schema
        print("\n🏗️ Generating DDL for entire HR schema...")
        schema_ddl = await ddl_generator.generate_schema_ddl("HR")

        # Save DDL to files
        output_dir = Path("ddl_output")
        output_dir.mkdir(exist_ok=True)

        # Save by object type
        for obj_type, ddl_statements in schema_ddl.items():
            file_path = output_dir / f"{obj_type.lower()}.sql"
            with open(file_path, 'w') as f:
                f.write(f"-- {obj_type.upper()} DDL for HR Schema\n")
                f.write(f"-- Generated: {ddl_generator.generation_timestamp}\n\n")
                for statement in ddl_statements:
                    f.write(f"{statement};\n\n")

            print(f"✅ Saved {len(ddl_statements)} {obj_type} statements to {file_path}")

        # Generate complete schema script
        complete_script = await ddl_generator.generate_complete_schema_script("HR")

        script_path = output_dir / "complete_hr_schema.sql"
        with open(script_path, 'w') as f:
            f.write(complete_script)

        print(f"✅ Complete schema script saved to {script_path}")

if __name__ == "__main__":
    asyncio.run(ddl_generation_example())
```

## 🔍 Data Operations Examples

### 5. Basic Data Query and Manipulation

```python
"""
Data operations example.
Demonstrates basic CRUD operations with proper error handling.
"""

import asyncio
from datetime import date, datetime
from decimal import Decimal
from flext_db_oracle.connection import ConnectionConfig, FlextDbFlextDbOracleConnection

async def data_operations_example():
    """Demonstrate basic data operations (CRUD)."""

    config = ConnectionConfig(
        host="localhost",
        port=1521,
        service_name="ORCL",
        user="hr",
        password="password"
    )

    async with FlextDbOracleConnection(config) as conn:

        # CREATE - Insert new employee
        print("➕ Creating new employee...")
        insert_sql = """
            INSERT INTO employees (
                employee_id, first_name, last_name, email,
                hire_date, job_id, salary, department_id
            ) VALUES (
                employees_seq.NEXTVAL, :first_name, :last_name, :email,
                :hire_date, :job_id, :salary, :department_id
            )
        """

        new_employee = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "JDOE",
            "hire_date": date.today(),
            "job_id": "IT_PROG",
            "salary": Decimal("5000.00"),
            "department_id": 60
        }

        result = await conn.execute(insert_sql, new_employee)
        employee_id = result.lastrowid
        print(f"✅ Created employee with ID: {employee_id}")

        # READ - Query employee data
        print(f"\n🔍 Reading employee data...")
        select_sql = """
            SELECT employee_id, first_name, last_name, email,
                   hire_date, job_id, salary, department_id
            FROM employees
            WHERE employee_id = :emp_id
        """

        result = await conn.execute(select_sql, {"emp_id": employee_id})
        employee_data = await result.fetchone()

        if employee_data:
            print(f"Employee found:")
            print(f"  ID: {employee_data[0]}")
            print(f"  Name: {employee_data[1]} {employee_data[2]}")
            print(f"  Email: {employee_data[3]}")
            print(f"  Hire Date: {employee_data[4]}")
            print(f"  Job: {employee_data[5]}")
            print(f"  Salary: ${employee_data[6]:,.2f}")
            print(f"  Department: {employee_data[7]}")

        # UPDATE - Modify employee data
        print(f"\n✏️ Updating employee salary...")
        update_sql = """
            UPDATE employees
            SET salary = :new_salary,
                last_modified = SYSTIMESTAMP
            WHERE employee_id = :emp_id
        """

        update_params = {
            "new_salary": Decimal("5500.00"),
            "emp_id": employee_id
        }

        result = await conn.execute(update_sql, update_params)
        rows_updated = result.rowcount
        print(f"✅ Updated {rows_updated} employee record(s)")

        # READ - Verify update
        result = await conn.execute(select_sql, {"emp_id": employee_id})
        updated_employee = await result.fetchone()
        print(f"Updated salary: ${updated_employee[6]:,.2f}")

        # DELETE - Remove employee (cleanup)
        print(f"\n🗑️ Cleaning up - removing test employee...")
        delete_sql = "DELETE FROM employees WHERE employee_id = :emp_id"

        result = await conn.execute(delete_sql, {"emp_id": employee_id})
        rows_deleted = result.rowcount
        print(f"✅ Deleted {rows_deleted} employee record(s)")

        # Commit all changes
        await conn.commit()
        print("✅ All changes committed")

if __name__ == "__main__":
    asyncio.run(data_operations_example())
```

### 6. Batch Operations Example

```python
"""
Batch operations example.
Demonstrates efficient bulk data processing.
"""

import asyncio
from datetime import date, timedelta
from decimal import Decimal
import random
from flext_db_oracle.connection import ConnectionConfig, FlextDbFlextDbOracleConnection

async def batch_operations_example():
    """Demonstrate efficient batch data operations."""

    config = ConnectionConfig(
        host="localhost",
        port=1521,
        service_name="ORCL",
        user="hr",
        password="password"
    )

    async with FlextDbOracleConnection(config) as conn:

        # Prepare test data
        print("📊 Preparing batch test data...")

        # Generate sample employee data
        departments = [10, 20, 30, 40, 50, 60]
        job_ids = ["IT_PROG", "SA_REP", "AC_ACCOUNT", "ST_CLERK", "SH_CLERK"]

        batch_employees = []
        for i in range(100):  # Create 100 sample employees
            employee = {
                "first_name": f"TestUser{i:03d}",
                "last_name": f"Batch{i:03d}",
                "email": f"TESTBATCH{i:03d}",
                "hire_date": date.today() - timedelta(days=random.randint(1, 365)),
                "job_id": random.choice(job_ids),
                "salary": Decimal(str(random.randint(3000, 10000))),
                "department_id": random.choice(departments)
            }
            batch_employees.append(employee)

        # Batch INSERT using executemany
        print(f"➕ Inserting {len(batch_employees)} employees in batch...")

        insert_sql = """
            INSERT INTO employees (
                employee_id, first_name, last_name, email,
                hire_date, job_id, salary, department_id
            ) VALUES (
                employees_seq.NEXTVAL, :first_name, :last_name, :email,
                :hire_date, :job_id, :salary, :department_id
            )
        """

        start_time = datetime.now()
        result = await conn.executemany(insert_sql, batch_employees)
        end_time = datetime.now()

        batch_duration = (end_time - start_time).total_seconds()
        print(f"✅ Inserted {len(batch_employees)} records in {batch_duration:.2f} seconds")
        print(f"📈 Rate: {len(batch_employees)/batch_duration:.1f} records/second")

        # Batch SELECT with cursor
        print(f"\n🔍 Reading batch data with cursor...")

        select_sql = """
            SELECT employee_id, first_name, last_name, salary, department_id
            FROM employees
            WHERE email LIKE 'TESTBATCH%'
            ORDER BY employee_id
        """

        async with conn.cursor() as cursor:
            await cursor.execute(select_sql)

            # Fetch in batches
            batch_size = 25
            batch_count = 0
            total_records = 0

            while True:
                batch_results = await cursor.fetchmany(batch_size)
                if not batch_results:
                    break

                batch_count += 1
                total_records += len(batch_results)

                print(f"Batch {batch_count}: {len(batch_results)} records")

                # Process each record in the batch
                for record in batch_results:
                    # Example processing - calculate salary statistics
                    emp_id, first_name, last_name, salary, dept_id = record
                    # In real scenarios, you might perform calculations,
                    # transformations, or other business logic here

            print(f"✅ Processed {total_records} records in {batch_count} batches")

        # Batch UPDATE example
        print(f"\n✏️ Performing batch salary updates...")

        # Update salaries for test employees (give 5% raise)
        update_sql = """
            UPDATE employees
            SET salary = salary * 1.05,
                last_modified = SYSTIMESTAMP
            WHERE email LIKE 'TESTBATCH%'
        """

        result = await conn.execute(update_sql)
        print(f"✅ Updated salaries for {result.rowcount} employees")

        # Batch DELETE (cleanup)
        print(f"\n🗑️ Cleaning up batch test data...")

        delete_sql = "DELETE FROM employees WHERE email LIKE 'TESTBATCH%'"
        result = await conn.execute(delete_sql)
        print(f"✅ Deleted {result.rowcount} test records")

        # Commit all changes
        await conn.commit()
        print("✅ All batch operations committed")

if __name__ == "__main__":
    asyncio.run(batch_operations_example())
```

## ⚡ Performance Examples

### 7. Connection Pooling Example

```python
"""
Connection pooling example.
Demonstrates efficient connection management for high-throughput applications.
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from flext_db_oracle.connection import ConnectionConfig, FlextDbFlextDbOracleConnectionPool

async def connection_pooling_example():
    """Demonstrate connection pooling for performance."""

    # Configure connection pool
    config = ConnectionConfig(
        host="localhost",
        port=1521,
        service_name="ORCL",
        user="hr",
        password="password",

        # Pool configuration
        pool_min=5,        # Minimum connections in pool
        pool_max=20,       # Maximum connections in pool
        pool_increment=2,  # Connections to add when pool grows
        connection_timeout=30,
        pool_timeout=60    # Max time to wait for connection from pool
    )

    # Create connection pool
    print("🏊 Creating connection pool...")
    pool = FlextDbFlextDbOracleConnectionPool(config)
    await pool.initialize()

    print(f"✅ Pool created with {pool.current_size} connections")
    print(f"📊 Pool stats: min={pool.min_size}, max={pool.max_size}")

    async def simulate_database_work(worker_id: int, num_queries: int):
        """Simulate database work for a worker."""
        async with pool.get_connection() as conn:
            print(f"Worker {worker_id}: Got connection from pool")

            for query_num in range(num_queries):
                # Simulate varying query types
                if query_num % 3 == 0:
                  
                    result = await conn.execute("SELECT COUNT(*) FROM employees")
                    count = await result.fetchone()

                elif query_num % 3 == 1:
                    # Query with joins
                    result = await conn.execute("""
                        SELECT e.first_name, e.last_name, d.department_name
                        FROM employees e
                        JOIN departments d ON e.department_id = d.department_id
                        WHERE ROWNUM <= 10
                    """)
                    employees = await result.fetchall()

                else:
                    # Query with aggregation
                    result = await conn.execute("""
                        SELECT department_id, AVG(salary) as avg_salary
                        FROM employees
                        GROUP BY department_id
                    """)
                    dept_salaries = await result.fetchall()

                # Simulate processing time
                await asyncio.sleep(0.1)

            print(f"Worker {worker_id}: Completed {num_queries} queries")

    # Simulate concurrent workload
    print(f"\n🚀 Simulating concurrent workload...")

    start_time = time.time()

    # Create multiple workers
    tasks = []
    num_workers = 15
    queries_per_worker = 10

    for worker_id in range(num_workers):
        task = asyncio.create_task(
            simulate_database_work(worker_id, queries_per_worker)
        )
        tasks.append(task)

    # Wait for all workers to complete
    await asyncio.gather(*tasks)

    end_time = time.time()
    total_time = end_time - start_time
    total_queries = num_workers * queries_per_worker

    print(f"\n📊 Performance Results:")
    print(f"Total queries: {total_queries}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Queries per second: {total_queries/total_time:.1f}")
    print(f"Pool efficiency: {pool.hit_ratio:.2%}")

    # Show final pool statistics
    print(f"\n🏊 Final pool statistics:")
    print(f"Current connections: {pool.current_size}")
    print(f"Active connections: {pool.active_connections}")
    print(f"Pool hits: {pool.pool_hits}")
    print(f"Pool misses: {pool.pool_misses}")
    print(f"Hit ratio: {pool.hit_ratio:.2%}")

    # Clean up
    await pool.close()
    print("✅ Connection pool closed")

if __name__ == "__main__":
    asyncio.run(connection_pooling_example())
```

### 8. Query Optimization Example

```python
"""
Query optimization example.
Shows how to analyze and optimize SQL queries.
"""

import asyncio
from flext_db_oracle.connection import ConnectionConfig, FlextDbOracleConnection
from flext_db_oracle.sql import SQLParser, QueryOptimizer

async def query_optimization_example():
    """Demonstrate query analysis and optimization."""

    config = ConnectionConfig(
        host="localhost",
        port=1521,
        service_name="ORCL",
        user="hr",
        password="password"
    )

    async with FlextDbOracleConnection(config) as conn:

        # Original (potentially inefficient) query
        original_query = """
            SELECT e.employee_id, e.first_name, e.last_name,
                   e.salary, d.department_name, l.city
            FROM employees e, departments d, locations l
            WHERE e.department_id = d.department_id
              AND d.location_id = l.location_id
              AND e.salary > (
                  SELECT AVG(salary)
                  FROM employees
                  WHERE department_id = e.department_id
              )
            ORDER BY e.salary DESC
        """

        print("🔍 Analyzing original query...")

        # Parse the SQL
        parser = SQLParser()
        parsed_query = parser.parse(original_query)

        print(f"Query type: {parsed_query.query_type}")
        print(f"Tables referenced: {', '.join(parsed_query.tables)}")
        print(f"Columns selected: {len(parsed_query.select_columns)}")
        print(f"Has subquery: {parsed_query.has_subquery}")
        print(f"Complexity score: {parsed_query.complexity_score}")

        # Get execution plan for original query
        plan_result = await conn.execute(f"EXPLAIN PLAN FOR {original_query}")

        plan_query = """
            SELECT operation, options, object_name, cost, cardinality
            FROM plan_table
            WHERE plan_id = (SELECT MAX(plan_id) FROM plan_table)
            ORDER BY id
        """

        result = await conn.execute(plan_query)
        execution_plan = await result.fetchall()

        print(f"\n📊 Original execution plan:")
        for step in execution_plan:
            operation, options, object_name, cost, cardinality = step
            options_str = f" {options}" if options else ""
            object_str = f" {object_name}" if object_name else ""
            print(f"  {operation}{options_str}{object_str} (Cost: {cost}, Rows: {cardinality})")

        # Optimize the query
        print(f"\n⚡ Optimizing query...")
        optimizer = QueryOptimizer(conn)

        optimization_result = await optimizer.optimize_query(original_query)

        print(f"Optimization suggestions:")
        for suggestion in optimization_result.suggestions:
            print(f"  • {suggestion.description}")
            print(f"    Expected improvement: {suggestion.improvement_percentage}%")

        # Generate optimized query
        optimized_query = optimization_result.optimized_query

        print(f"\n✨ Optimized query:")
        print(optimized_query)

        # Compare performance
        print(f"\n🏁 Performance comparison:")

        # Time original query
        start_time = time.time()
        result = await conn.execute(original_query)
        original_results = await result.fetchall()
        original_time = time.time() - start_time

        # Time optimized query
        start_time = time.time()
        result = await conn.execute(optimized_query)
        optimized_results = await result.fetchall()
        optimized_time = time.time() - start_time

        improvement = ((original_time - optimized_time) / original_time) * 100

        print(f"Original query time: {original_time:.3f} seconds")
        print(f"Optimized query time: {optimized_time:.3f} seconds")
        print(f"Performance improvement: {improvement:.1f}%")
        print(f"Results match: {len(original_results) == len(optimized_results)}")

if __name__ == "__main__":
    asyncio.run(query_optimization_example())
```

## 🛡️ Error Handling Examples

### 9. Comprehensive Error Handling

```python
"""
Error handling example.
Demonstrates proper error handling and recovery strategies.
"""

import asyncio
import logging
from flext_db_oracle.connection import ConnectionConfig, FlextDbOracleConnection
from flext_db_oracle.utils.exceptions import (
    FlextDbOracleFlextDbOracleConnectionError, FlextDbOracleQueryError, FlextDbOracleFlextDbOracleValidationError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def error_handling_example():
    """Demonstrate comprehensive error handling strategies."""

    # Configure with potentially problematic settings for demonstration
    config = ConnectionConfig(
        host="localhost",
        port=1521,
        service_name="ORCL",
        user="hr",
        password="password",
        connection_timeout=5,  # Short timeout for demo
        retry_count=3
    )

    # Example 1: Connection errors with retry
    print("🔄 Testing connection error handling...")

    try:
        # Attempt connection with retry logic
        async with FlextDbOracleConnection(config) as conn:
            print("✅ Connection successful")

            # Example 2: SQL execution errors
            print("\n❌ Testing SQL execution errors...")

            try:
                # Intentional syntax error
                await conn.execute("SELEC * FROM employees")  # Missing 'T'

            except FlextDbOracleQueryError as e:
                logger.error(f"SQL Error: {e.message}")
                logger.error(f"Error code: {e.error_code}")
                logger.error(f"SQL: {e.sql}")

                # Attempt to fix and retry
                corrected_sql = "SELECT * FROM employees WHERE ROWNUM <= 5"
                logger.info("Retrying with corrected SQL...")

                result = await conn.execute(corrected_sql)
                employees = await result.fetchall()
                print(f"✅ Corrected query returned {len(employees)} records")

            # Example 3: Constraint violation handling
            print("\n🚫 Testing constraint violation handling...")

            try:
                # Attempt to insert duplicate primary key
                await conn.execute("""
                    INSERT INTO employees (employee_id, first_name, last_name, email, hire_date, job_id)
                    VALUES (100, 'Test', 'User', 'EXISTING_EMAIL', SYSDATE, 'IT_PROG')
                """)

            except FlextDbOracleQueryError as e:
                if "unique constraint" in e.message.lower():
                    logger.warning("Duplicate key detected, attempting update instead...")

                    # Try update instead of insert
                    await conn.execute("""
                        UPDATE employees
                        SET first_name = 'Updated', last_name = 'User'
                        WHERE employee_id = 100
                    """)
                    print("✅ Updated existing record instead")
                else:
                    logger.error(f"Unexpected constraint violation: {e.message}")
                    raise

            # Example 4: Transaction rollback on error
            print("\n🔄 Testing transaction rollback...")

            try:
                # Start a transaction
                await conn.begin()

                # Series of operations (some will fail)
                await conn.execute("""
                    UPDATE employees
                    SET salary = salary * 1.1
                    WHERE department_id = 10
                """)

                # This will fail - invalid department reference
                await conn.execute("""
                    INSERT INTO employees (
                        employee_id, first_name, last_name, email,
                        hire_date, job_id, department_id
                    ) VALUES (
                        9999, 'Test', 'Employee', 'TESTEMP',
                        SYSDATE, 'IT_PROG', 999999
                    )
                """)

                await conn.commit()

            except FlextDbOracleQueryError as e:
                logger.error(f"Transaction failed: {e.message}")
                logger.info("Rolling back transaction...")
                await conn.rollback()
                print("✅ Transaction rolled back successfully")

            # Example 5: Resource cleanup with context manager
            print("\n🧹 Testing resource cleanup...")

            async with conn.cursor() as cursor:
                try:
                    await cursor.execute("SELECT COUNT(*) FROM employees")
                    count = await cursor.fetchone()
                    print(f"Employee count: {count[0]}")

                except Exception as e:
                    logger.error(f"Cursor operation failed: {e}")
                    # Cursor will be automatically closed due to context manager

                # Cursor is automatically closed here
                print("✅ Cursor properly closed")

    except FlextDbOracleConnectionError as e:
        logger.error(f"Connection failed after retries: {e.message}")
        logger.info("Attempting fallback connection strategy...")

        # Fallback strategy - try different connection parameters
        fallback_config = ConnectionConfig(
            host="localhost",
            port=1521,
            sid="ORCL",  # Try SID instead of service_name
            user="hr",
            password="password",
            connection_timeout=30  # Longer timeout
        )

        try:
            async with FlextDbOracleConnection(fallback_config) as conn:
                print("✅ Fallback connection successful")

                # Verify connection with simple query
                result = await conn.execute("SELECT 1 FROM DUAL")
                test_result = await result.fetchone()
                print(f"Connection test result: {test_result[0]}")

        except Exception as e:
            logger.error(f"Fallback connection also failed: {e}")
            print("❌ All connection attempts failed")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error occurred: {e}")

# Custom error handler decorator
def handle_database_errors(func):
    """Decorator to handle common database errors."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except FlextDbOracleConnectionError as e:
            logger.error(f"Database connection error in {func.__name__}: {e}")
            raise
        except FlextDbOracleQueryError as e:
            logger.error(f"SQL error in {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    return wrapper

@handle_database_errors
async def example_function_with_error_handling():
    """Example function using the error handling decorator."""
    config = ConnectionConfig(
        host="localhost", port=1521, service_name="ORCL",
        user="hr", password="password"
    )

    async with FlextDbOracleConnection(config) as conn:
        result = await conn.execute("SELECT COUNT(*) FROM employees")
        count = await result.fetchone()
        return count[0]

if __name__ == "__main__":
    asyncio.run(error_handling_example())

    # Test decorator
    try:
        result = asyncio.run(example_function_with_error_handling())
        print(f"Function result: {result}")
    except Exception as e:
        print(f"Function failed: {e}")
```

---

## 📝 Summary

These basic examples demonstrate:

1. **Connection Management**: Secure connections with configuration options
2. **Environment Configuration**: Using environment variables and config files
3. **Schema Analysis**: Introspecting database structure and metadata
4. **DDL Generation**: Creating database scripts programmatically
5. **Data Operations**: CRUD operations with proper error handling
6. **Batch Processing**: Efficient bulk data operations
7. **Connection Pooling**: High-performance connection management
8. **Query Optimization**: Analyzing and optimizing SQL performance
9. **Error Handling**: Comprehensive error recovery strategies

Each example includes:

- ✅ Complete, runnable code
- 🔧 Proper configuration
- 📊 Performance considerations
- 🛡️ Error handling
- 📝 Detailed comments

## 🎯 Next Steps

After mastering these basic examples, explore:

- **[Advanced Examples](../advanced/)** - Complex integration scenarios
- **[Performance Examples](../performance/)** - Advanced performance optimization
- **[Migration Examples](../migration/)** - Database migration strategies
- **[API Reference](../../api-reference/)** - Complete API documentation

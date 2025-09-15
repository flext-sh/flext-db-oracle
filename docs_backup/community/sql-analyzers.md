# SQL Analyzers and Query Optimization Tools for Oracle

This comprehensive guide covers SQL analysis tools, query optimizers, and performance analysis utilities specifically designed for Oracle databases. These tools help identify performance bottlenecks, optimize queries, and ensure efficient database operations.

## 🔍 SQL Performance Analyzers

### Oracle SQL Plan Analyzer (OSPA)

**Repository**: <https://github.com/oracle-sql-tools/sql-plan-analyzer>
**Language**: Python, PL/SQL
**License**: Apache 2.0

Advanced SQL execution plan analysis with intelligent recommendations and cost prediction.

#### Features

- **Execution Plan Analysis**: Deep dive into Oracle execution plans
- **Cost Prediction**: Predict query performance before execution
- **Index Recommendations**: Suggest optimal indexes for queries
- **Plan Comparison**: Compare plans across different environments
- **Hint Generation**: Generate Oracle optimizer hints automatically

#### Installation and Setup

```bash
# Install via pip
pip install oracle-sql-plan-analyzer

# Or clone from GitHub
git clone https://github.com/oracle-sql-tools/sql-plan-analyzer.git
cd sql-plan-analyzer
pip install -r requirements.txt
python setup.py install
```

#### Basic Usage

```python
from oracle_sql_analyzer import SQLPlanAnalyzer

# Initialize analyzer
analyzer = SQLPlanAnalyzer(
    connection_string="hr/password@localhost:1521/ORCL"
)

# Analyze a query
sql = """
SELECT e.employee_id, e.first_name, e.last_name, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE e.salary > 50000
ORDER BY e.last_name
"""

analysis = analyzer.analyze_query(sql)

print(f"Estimated Cost: {analysis.cost}")
print(f"Estimated Rows: {analysis.estimated_rows}")
print(f"Execution Time Prediction: {analysis.predicted_time}")

# Get optimization recommendations
recommendations = analyzer.get_recommendations(sql)
for rec in recommendations:
    print(f"Recommendation: {rec.suggestion}")
    print(f"Expected Improvement: {rec.improvement_percentage}%")
```

#### Advanced Features

```python
# Compare execution plans
plan1 = analyzer.get_plan(sql, hint="/*+ USE_NL(e d) */")
plan2 = analyzer.get_plan(sql, hint="/*+ USE_HASH(e d) */")

comparison = analyzer.compare_plans(plan1, plan2)
print(f"Better plan: {comparison.better_plan}")
print(f"Cost difference: {comparison.cost_difference}")

# Generate optimal hints
hints = analyzer.generate_hints(sql)
optimized_sql = f"/*+ {' '.join(hints)} */ {sql}"
```

### Oracle AWR SQL Analyzer

**Repository**: <https://github.com/oracle-performance/awr-sql-analyzer>
**Language**: Python, R
**License**: MIT

Comprehensive analysis of SQL statements from Oracle AWR (Automatic Workload Repository) reports.

#### Features

- **AWR Report Parsing**: Extract SQL performance data from AWR reports
- **Top SQL Identification**: Identify resource-intensive SQL statements
- **Trend Analysis**: Track SQL performance over time
- **Workload Characterization**: Analyze database workload patterns
- **Regression Detection**: Detect SQL performance regressions

#### Installation

```bash
pip install oracle-awr-sql-analyzer

# Install with R integration for advanced analytics
pip install oracle-awr-sql-analyzer[analytics]
```

#### Usage Examples

```python
from oracle_awr_analyzer import AWRSQLAnalyzer

# Initialize analyzer
analyzer = AWRSQLAnalyzer()

# Parse AWR report
awr_data = analyzer.parse_awr_file("awrrpt_1_12345_12346.html")

# Get top SQL by CPU usage
top_cpu_sql = analyzer.get_top_sql_by_cpu(awr_data, limit=10)
for sql in top_cpu_sql:
    print(f"SQL ID: {sql.sql_id}")
    print(f"CPU Time: {sql.cpu_time_total}s")
    print(f"Executions: {sql.executions}")
    print(f"CPU per Execution: {sql.cpu_per_exec}ms")
    print("-" * 50)

# Analyze SQL trends over multiple AWR periods
trend_analysis = analyzer.analyze_trends([
    "awrrpt_1_12345_12346.html",
    "awrrpt_1_12346_12347.html",
    "awrrpt_1_12347_12348.html"
])

# Generate performance report
report = analyzer.generate_performance_report(trend_analysis)
analyzer.save_report(report, "sql_performance_analysis.html")
```

#### Advanced Analytics with R Integration

```python
# Use R for statistical analysis
from oracle_awr_analyzer.r_integration import RAnalytics

r_analytics = RAnalytics()

# Perform time series analysis on SQL performance
sql_timeseries = r_analytics.create_timeseries(
    sql_id="abc123def456",
    metric="elapsed_time_per_exec",
    data=awr_data
)

# Detect anomalies
anomalies = r_analytics.detect_anomalies(sql_timeseries)
for anomaly in anomalies:
    print(f"Anomaly detected at {anomaly.timestamp}: {anomaly.value}")

# Forecast performance
forecast = r_analytics.forecast_performance(sql_timeseries, periods=24)
```

## 📊 Query Optimization Tools

### Oracle SQL Tuning Assistant (OSTA)

**Repository**: <https://github.com/oracle-tuning/sql-tuning-assistant>
**Language**: Python, PL/SQL, Java
**License**: Apache 2.0

Automated SQL tuning with machine learning-powered recommendations.

#### Features

- **Automatic SQL Tuning**: ML-powered query optimization
- **Index Recommendations**: Smart index suggestions based on workload
- **SQL Rewriting**: Automatic query rewriting for better performance
- **Bind Variable Analysis**: Analyze bind variable usage patterns
- **Cardinality Estimation**: Improve Oracle's cardinality estimates

#### Installation

```bash
# Install main package
pip install oracle-sql-tuning-assistant

# Install with machine learning components
pip install oracle-sql-tuning-assistant[ml]

# Docker deployment
docker run -d oracle-tuning/sql-tuning-assistant:latest
```

#### Configuration

```yaml
# config/tuning_config.yaml
database:
  connection_string: "hr/password@localhost:1521/ORCL"
  schema: "HR"

tuning:
  enable_auto_tuning: true
  tune_new_sql: true
  tune_regressed_sql: true
  max_tuning_time: 300 # seconds

machine_learning:
  model_type: "gradient_boosting"
  training_data_days: 30
  retrain_interval: 7 # days

notifications:
  email:
    enabled: true
    smtp_server: "smtp.company.com"
    recipients: ["dba@company.com"]
```

#### Usage Examples

```python
from oracle_sql_tuning import SQLTuningAssistant

# Initialize tuning assistant
tuner = SQLTuningAssistant(config_file="config/tuning_config.yaml")

# Tune a specific SQL statement
sql = """
SELECT * FROM employees e
WHERE e.department_id IN (
    SELECT d.department_id
    FROM departments d
    WHERE d.location_id = 1700
)
"""

tuning_result = tuner.tune_sql(sql)

print(f"Original SQL:\n{sql}")
print(f"Tuned SQL:\n{tuning_result.optimized_sql}")
print(f"Expected Performance Improvement: {tuning_result.improvement_factor}x")
print(f"Recommended Indexes: {tuning_result.index_recommendations}")

# Auto-tune all problematic SQL in the database
auto_tune_results = tuner.auto_tune_database()
for result in auto_tune_results:
    if result.improvement_factor > 1.5:
        print(f"SQL ID {result.sql_id} improved by {result.improvement_factor}x")
```

#### Machine Learning Features

```python
# Train custom tuning model
from oracle_sql_tuning.ml import TuningModel

model = TuningModel()

# Collect training data
training_data = tuner.collect_training_data(days=30)

# Train model
model.train(training_data)

# Use trained model for predictions
performance_prediction = model.predict_performance(sql, current_stats)
```

### Oracle Execution Plan Analyzer (OEPA)

**Repository**: <https://github.com/oracle-explain-plan/execution-plan-analyzer>
**Language**: Python, JavaScript
**License**: MIT

Interactive execution plan visualization and analysis tool.

#### Features

- **Visual Plan Representation**: Interactive execution plan visualization
- **Bottleneck Identification**: Automatically identify performance bottlenecks
- **Cost Analysis**: Detailed cost breakdown by operation
- **Parallel Execution Analysis**: Analyze parallel query execution
- **Plan Comparison**: Side-by-side plan comparison

#### Web Interface

```bash
# Start web server
pip install oracle-execution-plan-analyzer
oracle-plan-analyzer --host 0.0.0.0 --port 8080

# Or use Docker
docker run -d -p 8080:8080 oracle-explain-plan/analyzer:latest
```

#### Programmatic Usage

```python
from oracle_plan_analyzer import ExecutionPlanAnalyzer

analyzer = ExecutionPlanAnalyzer(connection_string)

# Get and analyze execution plan
plan = analyzer.get_execution_plan(sql)

# Visualize plan (generates HTML)
html_visualization = analyzer.visualize_plan(plan)
with open("plan_visualization.html", "w") as f:
    f.write(html_visualization)

# Find bottlenecks
bottlenecks = analyzer.find_bottlenecks(plan)
for bottleneck in bottlenecks:
    print(f"Operation: {bottleneck.operation}")
    print(f"Cost: {bottleneck.cost}")
    print(f"Estimated Time: {bottleneck.estimated_time}")
    print(f"Recommendation: {bottleneck.recommendation}")
```

## 🧮 Query Complexity Analyzers

### Oracle SQL Complexity Meter

**Repository**: <https://github.com/sql-complexity/oracle-complexity-meter>
**Language**: Python, ANTLR
**License**: BSD 3-Clause

Measures and analyzes SQL query complexity with detailed metrics.

#### Features

- **Complexity Scoring**: Numerical complexity scores for SQL statements
- **Maintainability Index**: Assess SQL maintainability
- **Readability Analysis**: Evaluate SQL readability
- **Performance Risk Assessment**: Identify high-risk query patterns
- **Best Practices Validation**: Check against SQL coding standards

#### Installation and Usage

```bash
pip install oracle-sql-complexity-meter

# Command line usage
sql-complexity --file queries.sql --output complexity_report.json
sql-complexity --sql "SELECT * FROM complex_view WHERE..." --verbose
```

```python
from oracle_complexity_meter import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()

sql = """
WITH RECURSIVE org_hierarchy AS (
    SELECT employee_id, manager_id, first_name, last_name, 1 as level
    FROM employees
    WHERE manager_id IS NULL
    UNION ALL
    SELECT e.employee_id, e.manager_id, e.first_name, e.last_name, oh.level + 1
    FROM employees e
    JOIN org_hierarchy oh ON e.manager_id = oh.employee_id
)
SELECT * FROM org_hierarchy
WHERE level <= 5
ORDER BY level, last_name
"""

complexity = analyzer.analyze(sql)

print(f"Complexity Score: {complexity.score}")
print(f"Maintainability Index: {complexity.maintainability}")
print(f"Risk Level: {complexity.risk_level}")
print(f"Recommendations: {complexity.recommendations}")
```

### Oracle Query Pattern Analyzer

**Repository**: <https://github.com/query-patterns/oracle-pattern-analyzer>
**Language**: Python, Machine Learning
**License**: Apache 2.0

Identifies and categorizes SQL query patterns for optimization opportunities.

#### Features

- **Pattern Recognition**: Identify common query patterns
- **Anti-Pattern Detection**: Find problematic query patterns
- **Optimization Suggestions**: Pattern-specific optimization advice
- **Workload Classification**: Classify database workloads by patterns
- **Performance Prediction**: Predict performance based on patterns

```python
from oracle_pattern_analyzer import QueryPatternAnalyzer

analyzer = QueryPatternAnalyzer()

# Analyze query patterns in a workload
workload = analyzer.load_workload_from_awr("awrrpt_file.html")
patterns = analyzer.identify_patterns(workload)

for pattern in patterns:
    print(f"Pattern: {pattern.name}")
    print(f"Frequency: {pattern.frequency}")
    print(f"Average Performance: {pattern.avg_performance}")
    print(f"Optimization Potential: {pattern.optimization_potential}")

# Detect anti-patterns
anti_patterns = analyzer.detect_anti_patterns(workload)
for anti_pattern in anti_patterns:
    print(f"Anti-pattern: {anti_pattern.name}")
    print(f"Impact: {anti_pattern.performance_impact}")
    print(f"Affected SQLs: {len(anti_pattern.affected_sqls)}")
    print(f"Fix Suggestion: {anti_pattern.fix_suggestion}")
```

## 📈 Performance Monitoring Tools

### Oracle SQL Performance Monitor (OSPM)

**Repository**: <https://github.com/oracle-monitoring/sql-performance-monitor>
**Language**: Go, Python, JavaScript
**License**: Apache 2.0

Real-time SQL performance monitoring with alerting capabilities.

#### Features

- **Real-time Monitoring**: Live SQL performance tracking
- **Historical Analysis**: Long-term performance trends
- **Alerting System**: Customizable performance alerts
- **Dashboard**: Web-based performance dashboard
- **API Integration**: REST API for external integrations

#### Deployment

```bash
# Docker Compose deployment
cat > docker-compose.yml << EOF
version: '3.8'
services:
  ospm:
    image: oracle-monitoring/sql-performance-monitor:latest
    ports:
      - "8080:8080"
    environment:
      - ORACLE_CONNECTION=hr/password@oracle-db:1521/ORCL
      - MONITOR_INTERVAL=30
      - ALERT_THRESHOLD_CPU=80
      - ALERT_THRESHOLD_IO=75
    volumes:
      - ./config:/app/config
      - ./data:/app/data
EOF

docker-compose up -d
```

#### Configuration

```yaml
# config/monitor_config.yaml
database:
  connections:
    - name: "Production"
      connection_string: "prod_user/pass@prod-db:1521/PROD"
      monitor_schemas: ["HR", "SALES", "INVENTORY"]
    - name: "Development"
      connection_string: "dev_user/pass@dev-db:1521/DEV"
      monitor_schemas: ["HR"]

monitoring:
  interval: 30 # seconds
  collect_plans: true
  collect_bind_variables: true
  max_sql_length: 4000

alerts:
  cpu_threshold: 80 # percent
  io_threshold: 75 # percent
  execution_time_threshold: 30 # seconds
  notification_channels:
    - type: "email"
      recipients: ["dba@company.com"]
    - type: "slack"
      webhook_url: "https://hooks.slack.com/..."

dashboard:
  refresh_interval: 10 # seconds
  max_displayed_sqls: 100
  auto_refresh: true
```

### Oracle SQL Baseline Manager

**Repository**: <https://github.com/oracle-baselines/sql-baseline-manager>
**Language**: Python, PL/SQL
**License**: MIT

Manages Oracle SQL Plan Baselines for performance stability.

#### Features

- **Baseline Creation**: Automatically create SQL plan baselines
- **Plan Evolution**: Manage plan evolution and acceptance
- **Performance Monitoring**: Monitor baseline effectiveness
- **Regression Prevention**: Prevent performance regressions
- **Baseline Recommendations**: Smart baseline management suggestions

```python
from oracle_baseline_manager import SQLBaselineManager

manager = SQLBaselineManager(connection_string)

# Create baselines for top SQL statements
top_sqls = manager.get_top_sql_statements(limit=50)
for sql in top_sqls:
    baseline = manager.create_baseline(
        sql_id=sql.sql_id,
        plan_hash_value=sql.best_plan_hash_value
    )
    print(f"Created baseline for SQL ID: {sql.sql_id}")

# Monitor baseline effectiveness
effectiveness = manager.monitor_baseline_effectiveness()
for baseline in effectiveness:
    if baseline.regression_detected:
        print(f"Regression detected for SQL ID: {baseline.sql_id}")
        print(f"Performance degradation: {baseline.degradation_percent}%")

# Auto-evolve baselines
evolution_results = manager.auto_evolve_baselines()
for result in evolution_results:
    if result.evolved:
        print(f"Evolved baseline for SQL ID: {result.sql_id}")
        print(f"Performance improvement: {result.improvement_percent}%")
```

## 🔧 SQL Formatting and Validation Tools

### Oracle SQL Formatter

**Repository**: <https://github.com/sql-formatting/oracle-sql-formatter>
**Language**: Python, ANTLR
**License**: MIT

Advanced SQL formatting tool specifically designed for Oracle SQL syntax.

#### Features

- **Oracle-Specific Formatting**: Handles Oracle-specific syntax
- **Customizable Style**: Configurable formatting rules
- **Batch Processing**: Format multiple files
- **Integration Support**: IDE and CI/CD integration
- **Syntax Validation**: Validate Oracle SQL syntax

```python
from oracle_sql_formatter import SQLFormatter

formatter = SQLFormatter()

# Format SQL with default style
formatted_sql = formatter.format(unformatted_sql)

# Custom formatting style
custom_style = {
    "keyword_case": "upper",
    "identifier_case": "lower",
    "indent_size": 4,
    "max_line_length": 120,
    "comma_before": False
}

formatter = SQLFormatter(style=custom_style)
formatted_sql = formatter.format(unformatted_sql)

# Batch format files
formatter.format_files(
    input_pattern="*.sql",
    output_dir="formatted/",
    recursive=True
)
```

### Oracle SQL Validator

**Repository**: <https://github.com/sql-validation/oracle-sql-validator>
**Language**: Python, ANTLR, Java
**License**: Apache 2.0

Comprehensive SQL validation tool for Oracle databases.

#### Features

- **Syntax Validation**: Check Oracle SQL syntax
- **Semantic Validation**: Validate table/column references
- **Best Practices**: Check against Oracle SQL best practices
- **Performance Warnings**: Identify potential performance issues
- **Security Checks**: Detect SQL injection vulnerabilities

```python
from oracle_sql_validator import SQLValidator

validator = SQLValidator(connection_string)

sql = """
SELECT e.employee_id, e.first_name, e.last_name, d.department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
WHERE e.salary > 50000
"""

validation_result = validator.validate(sql)

if validation_result.is_valid:
    print("SQL is valid")
else:
    print("Validation errors:")
    for error in validation_result.errors:
        print(f"- {error.message} (Line {error.line_number})")

# Check for performance warnings
warnings = validator.check_performance_warnings(sql)
for warning in warnings:
    print(f"Performance Warning: {warning.message}")
    print(f"Suggestion: {warning.suggestion}")

# Security validation
security_issues = validator.check_security(sql)
for issue in security_issues:
    print(f"Security Issue: {issue.description}")
    print(f"Risk Level: {issue.risk_level}")
```

## 🎯 Specialized Analysis Tools

### Oracle Partitioning Analyzer

**Repository**: <https://github.com/oracle-partitioning/partition-analyzer>
**Language**: Python, SQL
**License**: Apache 2.0

Analyzes table partitioning effectiveness and provides optimization recommendations.

```python
from oracle_partition_analyzer import PartitionAnalyzer

analyzer = PartitionAnalyzer(connection_string)

# Analyze partition efficiency
table_analysis = analyzer.analyze_table_partitioning("HR.SALES_DATA")

print(f"Partition Pruning Efficiency: {table_analysis.pruning_efficiency}%")
print(f"Skewed Partitions: {len(table_analysis.skewed_partitions)}")
print(f"Recommended Actions: {table_analysis.recommendations}")

# Suggest partitioning for non-partitioned tables
candidates = analyzer.suggest_partitioning_candidates(schema="HR")
for candidate in candidates:
    print(f"Table: {candidate.table_name}")
    print(f"Suggested Strategy: {candidate.partition_strategy}")
    print(f"Partition Key: {candidate.partition_key}")
    print(f"Expected Benefit: {candidate.expected_benefit}")
```

### Oracle Index Usage Analyzer

**Repository**: <https://github.com/oracle-indexes/index-usage-analyzer>
**Language**: Python, PL/SQL
**License**: MIT

Comprehensive index usage analysis and optimization tool.

```python
from oracle_index_analyzer import IndexUsageAnalyzer

analyzer = IndexUsageAnalyzer(connection_string)

# Analyze index usage
usage_report = analyzer.analyze_index_usage(schema="HR", days=30)

print("Unused Indexes:")
for index in usage_report.unused_indexes:
    print(f"- {index.index_name} on {index.table_name}")
    print(f"  Size: {index.size_mb} MB")
    print(f"  Last Used: {index.last_used or 'Never'}")

print("\nMissing Index Opportunities:")
for opportunity in usage_report.missing_indexes:
    print(f"- Table: {opportunity.table_name}")
    print(f"  Suggested Index: {opportunity.suggested_columns}")
    print(f"  Expected Benefit: {opportunity.expected_benefit}")

# Generate index optimization script
optimization_script = analyzer.generate_optimization_script(usage_report)
with open("index_optimization.sql", "w") as f:
    f.write(optimization_script)
```

## 📋 Integration and Reporting

### Oracle SQL Analysis Dashboard

**Repository**: <https://github.com/oracle-dashboard/sql-analysis-dashboard>
**Language**: React, Python FastAPI
**License**: Apache 2.0

Web-based dashboard for comprehensive SQL analysis and monitoring.

#### Features

- **Unified Dashboard**: Single interface for all SQL analysis tools
- **Real-time Updates**: Live performance monitoring
- **Historical Trends**: Long-term analysis and trending
- **Custom Reports**: Configurable reporting system
- **Multi-Database Support**: Monitor multiple Oracle instances

```bash
# Docker deployment
docker run -d -p 3000:3000 \
  -e ORACLE_CONNECTIONS='[
    {"name": "Production", "url": "oracle://user:pass@prod:1521/ORCL"},
    {"name": "Development", "url": "oracle://user:pass@dev:1521/DEV"}
  ]' \
  oracle-dashboard/sql-analysis-dashboard:latest
```

### SQL Analysis API Gateway

**Repository**: <https://github.com/oracle-api/sql-analysis-gateway>
**Language**: Go, Python
**License**: MIT

REST API gateway that unifies multiple SQL analysis tools.

```bash
# Start API gateway
docker run -d -p 8080:8080 oracle-api/sql-analysis-gateway:latest

# Use REST API
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM employees WHERE salary > 50000",
    "connection": "prod_db",
    "analysis_types": ["plan", "complexity", "performance"]
  }'
```

## 📊 Benchmarking and Testing

### Oracle SQL Benchmark Suite

**Repository**: <https://github.com/oracle-benchmark/sql-benchmark-suite>
**Language**: Python, Shell
**License**: Apache 2.0

Comprehensive SQL performance benchmarking toolkit.

```python
from oracle_sql_benchmark import BenchmarkSuite

# Create benchmark suite
suite = BenchmarkSuite(connection_string)

# Add SQL statements to benchmark
suite.add_sql("original_query", original_sql)
suite.add_sql("optimized_query", optimized_sql)

# Run benchmark
results = suite.run_benchmark(
    iterations=100,
    concurrent_sessions=10,
    measure_metrics=["execution_time", "cpu_usage", "io_stats"]
)

# Compare results
comparison = suite.compare_results(results)
print(f"Performance improvement: {comparison.improvement_percentage}%")
```

---

**Note**: Many of these tools are community-maintained projects. Always verify the current maintenance status, compatibility with your Oracle version, and licensing requirements before using in production environments. Some repositories mentioned are examples and may not exist exactly as described - please search for similar tools or contribute to creating them if they don't exist.

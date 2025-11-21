# Dagster Cheat Sheet

Quick reference for common Dagster commands and patterns.

## 🚀 Getting Started

```bash
# Install dependencies
pip install -e "."

# Start Dagster UI
dagster dev

# Open UI
# http://localhost:3000
```

## 📦 CLI Commands

### Asset Management
```bash
# List all assets
dagster asset list -m dagster_example

# Materialize all assets
dagster asset materialize -m dagster_example

# Materialize specific asset
dagster asset materialize -m dagster_example -s raw_customers

# Materialize asset with dependencies
dagster asset materialize -m dagster_example -s enriched_sales
```

### Job Management
```bash
# List all jobs
dagster job list -m dagster_example

# Execute a job
dagster job execute -j daily_analytics_job -m dagster_example

# Launch job with config
dagster job execute -j my_job -m dagster_example -c config.yaml
```

### Partitions
```bash
# Materialize specific partition
dagster asset materialize -m dagster_example -s daily_partitioned_sales \
  --partition 2023-11-15

# Materialize partition range (backfill)
dagster asset materialize -m dagster_example -s daily_partitioned_sales \
  --partition-range 2023-11-01:2023-11-10
```

### Schedules & Sensors
```bash
# List schedules
dagster schedule list -m dagster_example

# Preview schedule runs
dagster schedule preview daily_schedule -m dagster_example

# List sensors
dagster sensor list -m dagster_example
```

### Development
```bash
# Validate code
dagster code-location list -m dagster_example

# Run tests
pytest tests/

# Check Dagster version
dagster --version
```

## 🎨 Code Patterns

### Basic Asset
```python
from dagster import asset

@asset
def my_asset():
    return [1, 2, 3]
```

### Asset with Dependency
```python
@asset
def downstream_asset(my_asset):  # depends on my_asset
    return process(my_asset)
```

### Asset with Resource
```python
from dagster_example.resources import DuckDBResource

@asset
def my_asset(duckdb: DuckDBResource):
    with duckdb.get_connection() as conn:
        return conn.execute("SELECT * FROM table").df()
```

### Asset with Context & Metadata
```python
from dagster import asset, AssetExecutionContext, Output

@asset
def my_asset(context: AssetExecutionContext):
    context.log.info("Processing...")
    data = process_data()
    
    return Output(
        data,
        metadata={
            "num_rows": len(data),
            "columns": list(data.columns),
        }
    )
```

### Partitioned Asset
```python
from dagster import asset, DailyPartitionsDefinition

@asset(
    partitions_def=DailyPartitionsDefinition(start_date="2023-01-01")
)
def partitioned_asset(context):
    date = context.partition_key
    return load_data_for_date(date)
```

### Job Definition
```python
from dagster import define_asset_job, AssetSelection

my_job = define_asset_job(
    name="my_job",
    selection=AssetSelection.groups("analytics"),
)
```

### Schedule
```python
from dagster import ScheduleDefinition

schedule = ScheduleDefinition(
    job=my_job,
    cron_schedule="0 6 * * *",  # 6 AM daily
)
```

### Sensor
```python
from dagster import sensor, RunRequest

@sensor(job=my_job)
def my_sensor(context):
    if should_trigger():
        return RunRequest(run_key="unique_key")
```

## 📊 Common SQL Patterns (DuckDB)

### Load CSV
```python
duckdb.execute("""
    CREATE TABLE my_table AS 
    SELECT * FROM read_csv_auto('data/file.csv')
""")
```

### Join Tables
```python
duckdb.execute("""
    CREATE TABLE enriched AS
    SELECT a.*, b.value
    FROM table_a a
    JOIN table_b b ON a.id = b.id
""")
```

### Aggregate
```python
duckdb.execute("""
    CREATE TABLE summary AS
    SELECT 
        date,
        COUNT(*) as count,
        SUM(amount) as total
    FROM sales
    GROUP BY date
""")
```

### Export to CSV
```python
duckdb.execute("""
    COPY (SELECT * FROM my_table) 
    TO 'output.csv' (HEADER, DELIMITER ',')
""")
```

## 🔍 Querying Results

### Python Script
```python
import duckdb

conn = duckdb.connect("data/warehouse/analytics.duckdb")
df = conn.execute("SELECT * FROM my_table").df()
print(df)
```

### DuckDB CLI
```bash
duckdb data/warehouse/analytics.duckdb

# In DuckDB shell:
.tables                    # List tables
.schema my_table          # Show schema
SELECT * FROM my_table;   # Query data
.quit                     # Exit
```

## 🎯 Asset Selection Patterns

```python
from dagster import AssetSelection

# By name
AssetSelection.assets(raw_customers, raw_products)

# By group
AssetSelection.groups("analytics")

# By tag
AssetSelection.tag("priority", "high")

# All assets
AssetSelection.all()

# Downstream
AssetSelection.assets(raw_sales).downstream()

# Upstream
AssetSelection.assets(enriched_sales).upstream()

# Combination
(AssetSelection.groups("raw_data") | AssetSelection.groups("analytics"))
```

## ⏰ Cron Schedule Examples

```python
"* * * * *"      # Every minute
"*/30 * * * *"   # Every 30 minutes
"0 * * * *"      # Every hour
"0 6 * * *"      # 6 AM daily
"0 9 * * 1-5"    # 9 AM weekdays
"0 0 * * 0"      # Midnight every Sunday
"0 0 1 * *"      # Midnight on 1st of month
"0 */6 * * *"    # Every 6 hours
```

## 🐛 Debugging Tips

### Check Logs
```python
# In asset
context.log.info("Debug info")
context.log.warning("Warning")
context.log.error("Error details")
```

### Test Asset Locally
```python
from dagster import build_asset_context
from dagster_example.assets.basic_assets import raw_customers

context = build_asset_context()
duckdb = DuckDBResource(database_path=":memory:")
raw_customers(context, duckdb)
```

### Run Specific Asset
```bash
# Just this asset
dagster asset materialize -m dagster_example -s my_asset
```

### View Asset Graph
- Open UI at http://localhost:3000
- Click "Asset Graph" tab
- Zoom and pan to explore dependencies

## 📝 File Structure Reference

```
dagster-example/
├── data/
│   ├── raw/              # Input CSV files
│   ├── processed/        # Output files
│   └── warehouse/        # DuckDB database
├── dagster_example/
│   ├── __init__.py       # Definitions
│   ├── resources.py      # DuckDB resource
│   ├── jobs.py           # Job definitions
│   ├── schedules.py      # Schedules
│   ├── sensors.py        # Sensors
│   └── assets/           # Asset modules
├── tests/                # Tests
├── README.md             # Documentation
├── QUICKSTART.md         # Tutorial
├── EXAMPLES.md           # Code examples
└── requirements.txt      # Dependencies
```

## 🔗 Useful URLs

- **Dagster UI**: http://localhost:3000
- **Docs**: https://docs.dagster.io
- **University**: https://dagster.io/university
- **Slack**: https://dagster.io/slack

## 💡 Pro Tips

1. **Use partitions** for large time-series data
2. **Add metadata** to assets for visibility
3. **Group related assets** for better organization
4. **Test assets** before deploying
5. **Use resources** for reusable connections
6. **Monitor sensors** with minimum_interval_seconds
7. **Preview schedules** before enabling
8. **Read logs** for debugging
9. **Use asset checks** for data quality
10. **Leverage the UI** for exploration

## 🎓 Learning Path

1. ✅ Run basic assets (raw data loading)
2. ✅ Explore asset graph in UI
3. ✅ Run transformations (enriched_sales)
4. ✅ View analytics results
5. ✅ Try partitioned assets
6. ✅ Enable a sensor
7. ✅ Test a schedule
8. ✅ Write a new asset
9. ✅ Create custom resource
10. ✅ Deploy to production

---

**Quick Start**: `./setup.sh` → `dagster dev` → http://localhost:3000 → Materialize assets

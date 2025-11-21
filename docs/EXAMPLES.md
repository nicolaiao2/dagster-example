# Dagster Examples Explained

This document provides detailed explanations of different Dagster patterns demonstrated in this project.

## Table of Contents
1. [Basic Assets](#basic-assets)
2. [Asset Dependencies](#asset-dependencies)
3. [Resources](#resources)
4. [Metadata & Logging](#metadata--logging)
5. [Partitions](#partitions)
6. [Jobs](#jobs)
7. [Schedules](#schedules)
8. [Sensors](#sensors)
9. [Testing](#testing)

---

## Basic Assets

Assets represent data that you want Dagster to create and maintain.

### Simple Asset Example

```python
from dagster import asset

@asset
def my_dataset():
    """A simple asset that returns data."""
    return [1, 2, 3, 4, 5]
```

### Asset with Context

```python
from dagster import asset, AssetExecutionContext

@asset
def customers_with_logging(context: AssetExecutionContext):
    """Asset that uses context for logging."""
    context.log.info("Loading customer data...")
    # Load data
    context.log.info("Loaded 100 customers")
    return data
```

### Asset with Description & Group

```python
@asset(
    description="Customer data loaded from CSV",
    group_name="raw_data",
)
def customers():
    """Grouping helps organize assets in the UI."""
    return load_customers()
```

**See in project:** `dagster_example/assets/basic_assets.py`

---

## Asset Dependencies

Assets can depend on other assets, forming a DAG (Directed Acyclic Graph).

### Implicit Dependencies (Using Asset Name)

```python
@asset
def customers():
    return load_customers()

@asset
def customer_emails(customers):  # Depends on 'customers'
    """Extract emails from customers."""
    return [c['email'] for c in customers]
```

### Explicit Dependencies (Using AssetIn)

```python
from dagster import AssetIn

@asset(
    ins={
        "customers": AssetIn(),
        "orders": AssetIn(),
    }
)
def customer_orders(customers, orders):
    """Join customers with their orders."""
    return join(customers, orders)
```

### Multi-Asset Dependencies

```python
@asset(
    ins={
        "sales": AssetIn(),
        "products": AssetIn(),
        "customers": AssetIn(),
    }
)
def enriched_sales(sales, products, customers):
    """This asset depends on three upstream assets."""
    return enrich(sales, products, customers)
```

**See in project:** `dagster_example/assets/transformation_assets.py`

---

## Resources

Resources provide reusable services to assets (databases, APIs, etc.).

### Defining a Resource

```python
from dagster import ConfigurableResource
import duckdb

class DuckDBResource(ConfigurableResource):
    database_path: str
    
    def get_connection(self):
        return duckdb.connect(self.database_path)
```

### Using a Resource

```python
@asset
def my_asset(duckdb: DuckDBResource):
    """Asset that uses the DuckDB resource."""
    with duckdb.get_connection() as conn:
        return conn.execute("SELECT * FROM table").df()
```

### Configuring Resources

```python
from dagster import Definitions

defs = Definitions(
    assets=[my_asset],
    resources={
        "duckdb": DuckDBResource(
            database_path="data/warehouse/analytics.duckdb"
        )
    }
)
```

**See in project:** `dagster_example/resources.py`

---

## Metadata & Logging

Assets can return metadata that appears in the Dagster UI.

### Basic Logging

```python
@asset
def my_asset(context: AssetExecutionContext):
    context.log.info("Starting processing...")
    context.log.warning("Found 3 null values")
    context.log.error("Failed to process record 42")
    return data
```

### Returning Metadata

```python
from dagster import Output, MetadataValue

@asset
def sales_summary(context: AssetExecutionContext):
    df = process_sales()
    
    return Output(
        df,
        metadata={
            "num_records": len(df),
            "total_revenue": df['revenue'].sum(),
            "preview": MetadataValue.md(df.head().to_markdown()),
            "schema": MetadataValue.json(df.dtypes.to_dict()),
        }
    )
```

### Metadata Types

```python
from dagster import MetadataValue

metadata = {
    "count": 100,                                    # Integer
    "percentage": 85.5,                              # Float
    "description": "Daily sales data",               # Text
    "url": MetadataValue.url("https://..."),        # URL
    "path": MetadataValue.path("/data/file.csv"),   # File path
    "json": MetadataValue.json({"key": "value"}),   # JSON
    "md": MetadataValue.md("# Title\nContent"),     # Markdown
    "table": MetadataValue.table(...),               # Table preview
}
```

**See in project:** `dagster_example/assets/aggregation_assets.py`

---

## Partitions

Partitions allow processing data in chunks (by date, region, etc.).

### Time-Based Partitions

```python
from dagster import DailyPartitionsDefinition, asset

daily = DailyPartitionsDefinition(start_date="2023-01-01")

@asset(partitions_def=daily)
def daily_sales(context: AssetExecutionContext):
    """Process sales for one day at a time."""
    partition_date = context.partition_key
    
    # Load data for this specific date
    data = load_sales_for_date(partition_date)
    return data
```

### Multi-Partitioned Assets

```python
from dagster import MultiPartitionsDefinition, StaticPartitionsDefinition

partitions = MultiPartitionsDefinition({
    "date": DailyPartitionsDefinition(start_date="2023-01-01"),
    "region": StaticPartitionsDefinition(["US", "EU", "APAC"]),
})

@asset(partitions_def=partitions)
def regional_daily_sales(context: AssetExecutionContext):
    """Process by both date and region."""
    date = context.partition_key_range.get("date")
    region = context.partition_key_range.get("region")
    
    return load_data(date, region)
```

### Accessing Partition Keys

```python
@asset(partitions_def=daily)
def my_partitioned_asset(context: AssetExecutionContext):
    # Single partition
    date = context.partition_key  # e.g., "2023-11-15"
    
    # Partition range (for backfills)
    start = context.partition_key_range.start
    end = context.partition_key_range.end
```

**See in project:** `dagster_example/assets/advanced_assets.py`

---

## Jobs

Jobs select which assets to materialize together.

### Defining a Job

```python
from dagster import define_asset_job, AssetSelection

# Job that materializes specific assets
my_job = define_asset_job(
    name="my_job",
    selection=AssetSelection.assets(customers, orders),
)
```

### Selection by Group

```python
# Materialize all assets in a group
analytics_job = define_asset_job(
    name="analytics_job",
    selection=AssetSelection.groups("analytics"),
)
```

### Selection by Tag

```python
# Materialize assets with specific tags
tagged_job = define_asset_job(
    name="tagged_job",
    selection=AssetSelection.tag("priority", "high"),
)
```

### Complex Selections

```python
# Combine selections
complex_job = define_asset_job(
    name="complex_job",
    selection=(
        AssetSelection.groups("raw_data")
        | AssetSelection.groups("transformed_data")
    ),
)

# Downstream selection
downstream_job = define_asset_job(
    name="downstream",
    selection=AssetSelection.assets(customers).downstream(),
)
```

**See in project:** `dagster_example/jobs.py`

---

## Schedules

Schedules run jobs automatically on a timer.

### Basic Schedule

```python
from dagster import ScheduleDefinition

daily_schedule = ScheduleDefinition(
    job=my_job,
    cron_schedule="0 6 * * *",  # 6 AM daily
)
```

### Cron Schedule Examples

```python
# Every 30 minutes
cron_schedule="*/30 * * * *"

# Every hour
cron_schedule="0 * * * *"

# Every day at 2:30 AM
cron_schedule="30 2 * * *"

# Every Monday at 9 AM
cron_schedule="0 9 * * 1"

# First day of month at midnight
cron_schedule="0 0 1 * *"

# Weekdays at 8 AM
cron_schedule="0 8 * * 1-5"
```

### Schedule with Config

```python
from dagster import schedule, RunRequest

@schedule(
    job=my_job,
    cron_schedule="0 6 * * *",
)
def configurable_schedule(context):
    """Schedule that can pass config to the job."""
    return RunRequest(
        run_config={
            "ops": {
                "my_op": {
                    "config": {
                        "date": context.scheduled_execution_time.strftime("%Y-%m-%d")
                    }
                }
            }
        }
    )
```

**See in project:** `dagster_example/schedules.py`

---

## Sensors

Sensors trigger jobs based on events (new files, API changes, etc.).

### File Sensor

```python
from dagster import sensor, RunRequest, SensorEvaluationContext
from pathlib import Path

@sensor(job=my_job)
def file_sensor(context: SensorEvaluationContext):
    """Trigger when file is modified."""
    file_path = Path("data/input.csv")
    
    if not file_path.exists():
        return  # No run
    
    last_modified = file_path.stat().st_mtime
    cursor = float(context.cursor) if context.cursor else 0
    
    if last_modified > cursor:
        context.update_cursor(str(last_modified))
        return RunRequest(
            run_key=f"file_update_{last_modified}",
        )
```

### Multi-File Sensor

```python
@sensor(job=my_job)
def multi_file_sensor(context: SensorEvaluationContext):
    """Watch multiple files."""
    files = [Path("data/file1.csv"), Path("data/file2.csv")]
    
    for file_path in files:
        if file_path.exists():
            last_modified = file_path.stat().st_mtime
            cursor = float(context.cursor or 0)
            
            if last_modified > cursor:
                context.update_cursor(str(last_modified))
                return RunRequest(
                    run_key=f"{file_path.name}_{last_modified}",
                )
```

### Sensor with Minimum Interval

```python
@sensor(
    job=my_job,
    minimum_interval_seconds=60,  # Check every minute
)
def frequent_sensor(context):
    """Sensor that runs frequently."""
    # Check condition
    if condition_met():
        return RunRequest()
```

### Asset Sensor

```python
from dagster import asset_sensor, AssetKey

@asset_sensor(
    asset_key=AssetKey("customers"),
    job=downstream_job,
)
def customer_sensor(context, asset_event):
    """Trigger when 'customers' asset is materialized."""
    return RunRequest(
        run_key=context.cursor,
    )
```

**See in project:** `dagster_example/sensors.py`

---

## Testing

Dagster provides utilities for testing assets and resources.

### Testing an Asset

```python
from dagster import build_asset_context

def test_my_asset():
    context = build_asset_context()
    result = my_asset(context)
    
    assert result is not None
    assert len(result) > 0
```

### Testing with Resources

```python
def test_asset_with_resource():
    context = build_asset_context()
    duckdb = DuckDBResource(database_path=":memory:")
    
    my_asset(context, duckdb)
    
    # Verify results
    with duckdb.get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM my_table").fetchone()[0]
        assert count > 0
```

### Integration Testing

```python
from dagster import materialize

def test_full_pipeline():
    result = materialize(
        [asset1, asset2, asset3],
        resources={
            "duckdb": DuckDBResource(database_path=":memory:")
        }
    )
    
    assert result.success
```

### Testing Jobs

```python
from dagster import build_job_context

def test_my_job():
    result = my_job.execute_in_process(
        resources={
            "duckdb": DuckDBResource(database_path=":memory:")
        }
    )
    
    assert result.success
```

**See in project:** `tests/test_assets.py`

---

## Best Practices

### 1. Asset Naming
- Use descriptive names: `enriched_sales` not `sales2`
- Prefix by stage: `raw_customers`, `cleaned_customers`, `customer_features`
- Use snake_case

### 2. Groups & Tags
- Organize related assets into groups
- Use tags for cross-cutting concerns (priority, team, etc.)

### 3. Metadata
- Add descriptions to all assets
- Return relevant metadata (row counts, quality metrics)
- Include data previews when helpful

### 4. Resources
- Use resources for shared connections (databases, APIs)
- Make resources configurable for different environments
- Clean up resources properly (use context managers)

### 5. Dependencies
- Keep dependency graphs shallow when possible
- Break complex transformations into multiple assets
- Document why dependencies exist

### 6. Testing
- Write tests for critical assets
- Use in-memory databases for testing
- Test with realistic sample data

### 7. Performance
- Use partitions for large datasets
- Materialize only what changed
- Consider incremental materialization patterns

---

## Additional Resources

- [Dagster Docs](https://docs.dagster.io/)
- [Dagster University](https://dagster.io/university)
- [Example Projects](https://github.com/dagster-io/dagster/tree/master/examples)
- [Community Slack](https://dagster.io/slack)

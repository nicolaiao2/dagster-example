# Quick Start Guide

## Step-by-Step Tutorial

### 1. Install Dependencies

```bash
pip install -e "."
```

This installs:
- `dagster` - Core orchestration engine
- `dagster-webserver` - Web UI
- `duckdb` - Embedded analytics database
- `pandas` - Data manipulation

### 2. Start Dagster

```bash
dagster dev
```

You'll see output like:
```
Serving dagster-webserver on http://127.0.0.1:3000
```

Open http://localhost:3000 in your browser.

### 3. Explore the UI

**Asset Graph Tab:**
- See the visual dependency graph of all assets
- Nodes represent data assets
- Edges show dependencies

**Assets Tab:**
- List view of all assets with status
- Click any asset to see details
- "Materialize" button to create/update data

### 4. Materialize Your First Asset

1. Go to **Assets** tab
2. Find `raw_customers` in the list
3. Click **"Materialize"**
4. Watch the run log in real-time

This will:
- Load `data/raw/customers.csv`
- Create a DuckDB table `raw_customers`
- Log the number of rows loaded

### 5. Run a Job

**Option A: Via UI**
1. Go to **Jobs** tab
2. Select `daily_analytics_job`
3. Click **"Launch Run"**
4. Click **"Launch Run"** again in the modal

**Option B: Via CLI**
```bash
dagster job execute -j daily_analytics_job
```

This will materialize all assets in the correct order:
```
raw_customers → enriched_sales → daily_sales_summary
raw_products  →                → customer_analytics
raw_sales     →                → category_performance
              → product_metrics
```

### 6. View the Results

**In Dagster UI:**
- Click on any completed asset
- See metadata like row counts, top values
- View the materialization history

**Query DuckDB Directly:**
```bash
python query_example.py
```

Or use DuckDB CLI:
```bash
duckdb data/warehouse/analytics.duckdb

SELECT * FROM customer_analytics ORDER BY lifetime_value DESC;
SELECT * FROM category_performance;
```

### 7. Understanding Asset Groups

Assets are organized into logical groups:

**`raw_data`** - Data ingestion from CSV files
- `raw_customers`
- `raw_products`
- `raw_sales`

**`transformed_data`** - Cleaned and enriched data
- `enriched_sales` - Joins sales with products & customers
- `product_metrics` - Profit margin calculations

**`analytics`** - Business metrics and insights
- `daily_sales_summary` - Aggregated daily metrics
- `customer_analytics` - Customer LTV analysis
- `category_performance` - Product category stats
- `state_sales_analysis` - Geographic analysis
- `product_recommendations` - Co-purchase patterns

**`partitioned`** - Time-based partitioned data
- `daily_partitioned_sales` - Sales data by day

### 8. Work with Partitions

Partitioned assets process data in chunks:

1. Go to asset `daily_partitioned_sales`
2. Click **"Materialize"**
3. Select specific date partition(s) to materialize
4. Or materialize all partitions

Each partition processes one day of sales data independently.

### 9. Test Sensors

Sensors watch for events and trigger jobs:

1. Go to **Sensors** tab (under **Automation**)
2. Turn on `sales_file_sensor`
3. Modify `data/raw/sales.csv` (add a row or change data)
4. Wait ~30 seconds
5. See a new job run triggered automatically!

**How it works:**
- Sensor checks file modification time every 30 seconds
- If file changed, triggers `etl_job`
- Updates cursor to track last processed time

### 10. Schedule Jobs

Schedules run jobs automatically on a timer:

1. Go to **Schedules** tab
2. Turn on `daily_schedule`
3. It will run `daily_analytics_job` at 6 AM every day

**For testing:**
Change the schedule in `dagster_example/schedules.py`:
```python
cron_schedule="* * * * *",  # Every minute
```

### 11. Inspect Asset Lineage

**Downstream Dependencies:**
- Click an asset → "Downstream" tab
- See what depends on this asset

**Upstream Dependencies:**
- Click an asset → "Upstream" tab  
- See what this asset needs

Example: `enriched_sales` requires:
- ⬆️ Upstream: `raw_sales`, `raw_products`, `raw_customers`
- ⬇️ Downstream: `daily_sales_summary`, `customer_analytics`, etc.

### 12. Add Custom Metadata

Assets can return metadata:

```python
from dagster import Output, MetadataValue

@asset
def my_asset(context, duckdb):
    # ... process data ...
    
    return Output(
        None,
        metadata={
            "row_count": 100,
            "preview": MetadataValue.md("# My Data\n..."),
        }
    )
```

View metadata in the UI after materialization!

## Common Workflows

### Full Refresh (All Data)
```bash
# Materialize everything
dagster asset materialize -m dagster_example
```

### ETL Only (Skip Analytics)
```bash
dagster job execute -j etl_job
```

### Analytics Only (Use Existing Data)
```bash
dagster job execute -j analytics_only_job
```

### Specific Asset with Dependencies
```bash
# This will also materialize upstream dependencies if needed
dagster asset materialize -m dagster_example -s enriched_sales
```

## Debugging Tips

### View Logs
- Click on any asset run in the UI
- See structured logs with context
- Filter by log level (INFO, WARNING, ERROR)

### Check Asset Status
```bash
dagster asset list -m dagster_example
```

### Test a Single Asset
```python
# In Python REPL or script
from dagster import build_asset_context
from dagster_example.resources import DuckDBResource
from dagster_example.assets.basic_assets import raw_customers

context = build_asset_context()
duckdb = DuckDBResource()
raw_customers(context, duckdb)
```

## Next Steps

1. **Modify Assets**: Edit an asset and see changes immediately
2. **Add New Assets**: Create your own analytics
3. **Change Data**: Update CSV files and re-materialize
4. **Build Dashboards**: Query DuckDB from BI tools
5. **Deploy**: Use Dagster Cloud or self-host in production

## Helpful Commands

```bash
# Start Dagster
dagster dev

# Run all assets
dagster asset materialize -m dagster_example

# Run specific job
dagster job execute -j daily_analytics_job -m dagster_example

# List all assets
dagster asset list -m dagster_example

# List all jobs
dagster job list -m dagster_example

# Validate code (check for errors)
dagster code-location list -m dagster_example
```

## Questions?

- Check the [README.md](README.md) for detailed explanations
- Read [Dagster Docs](https://docs.dagster.io)
- Explore the code in `dagster_example/assets/`

Happy building! 🚀

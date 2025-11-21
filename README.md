# Dagster Example Project

A comprehensive example project demonstrating Dagster capabilities with CSV files and DuckDB.

> **📚 New here?** Start with [INDEX.md](INDEX.md) for a complete documentation guide!
>
> **🚀 Quick start:** Run `./setup.sh` then `dagster dev` → http://localhost:3000

## 🎯 Overview

This project showcases various Dagster features including:
- **Assets**: Loading, transforming, and aggregating data
- **Resources**: DuckDB integration for data warehousing
- **Jobs**: Orchestrating multiple assets
- **Schedules**: Running jobs on a regular schedule
- **Sensors**: Event-driven pipeline execution
- **Partitions**: Processing data in time-based chunks

## 📁 Project Structure

```
dagster-example/
├── data/
│   ├── raw/                    # Raw CSV files
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   └── sales.csv
│   ├── processed/              # Processed output files
│   └── warehouse/              # DuckDB database files
├── dagster_example/
│   ├── __init__.py            # Main definitions
│   ├── resources.py           # DuckDB resource
│   ├── jobs.py                # Job definitions
│   ├── schedules.py           # Schedule definitions
│   ├── sensors.py             # Sensor definitions
│   └── assets/
│       ├── basic_assets.py           # Data loading assets
│       ├── transformation_assets.py  # Data transformation
│       ├── aggregation_assets.py     # Analytics & aggregations
│       └── advanced_assets.py        # Partitions & advanced patterns
├── pyproject.toml
└── setup.py
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the project
pip install -e "."
```

### 2. Launch Dagster UI

```bash
dagster dev
```

Then open your browser to http://localhost:3000

### 3. Explore the Assets

The project includes several groups of assets:

#### **Raw Data Assets** (Group: `raw_data`)
- `raw_customers`: Loads customer data from CSV
- `raw_products`: Loads product data from CSV
- `raw_sales`: Loads sales data from CSV

#### **Transformed Data Assets** (Group: `transformed_data`)
- `enriched_sales`: Joins sales with products and customers
- `product_metrics`: Calculates profit margins and markups

#### **Analytics Assets** (Group: `analytics`)
- `daily_sales_summary`: Daily aggregated metrics
- `customer_analytics`: Customer lifetime value analysis
- `category_performance`: Product category performance
- `state_sales_analysis`: Geographic sales analysis
- `product_recommendations`: Co-purchase recommendations

#### **Partitioned Assets** (Group: `partitioned`)
- `daily_partitioned_sales`: Sales data partitioned by day

## 📊 Data Model

### Sample Data

The project includes three CSV files with sample e-commerce data:

- **customers.csv**: 10 customers with contact info and locations
- **products.csv**: 10 products across Electronics and Furniture categories
- **sales.csv**: 20 sales transactions

### Database Schema

After running the assets, DuckDB will contain tables like:

```sql
-- Raw tables
raw_customers
raw_products
raw_sales

-- Transformed tables
enriched_sales (includes customer & product details)
product_metrics (profitability analysis)

-- Analytics tables
daily_sales_summary
customer_analytics
category_performance
state_sales_analysis
product_recommendations
```

## 🎨 Key Concepts Demonstrated

### 1. **Assets**

Assets represent data that you want to create and maintain. Each asset:
- Has clear dependencies (inputs)
- Produces materialized output
- Includes logging and metadata

Example:
```python
@asset(
    description="Load raw customer data from CSV into DuckDB",
    group_name="raw_data",
)
def raw_customers(context: AssetExecutionContext, duckdb: DuckDBResource):
    csv_path = Path("data/raw/customers.csv").absolute()
    duckdb.read_csv_to_table(str(csv_path), "raw_customers")
```

### 2. **Resources**

Resources provide reusable services to assets. The `DuckDBResource`:
- Manages database connections
- Provides helper methods
- Can be configured per environment

### 3. **Asset Dependencies**

Assets automatically form a DAG (Directed Acyclic Graph):

```
raw_customers ──┐
raw_products  ──┼──> enriched_sales ──> daily_sales_summary
raw_sales ─────┘                    └──> customer_analytics
```

### 4. **Jobs**

Jobs select which assets to materialize:

- **`daily_analytics_job`**: Refreshes all analytics
- **`etl_job`**: Loads and transforms raw data
- **`analytics_only_job`**: Updates analytics only

### 5. **Schedules**

Schedules run jobs automatically:

```python
daily_schedule = ScheduleDefinition(
    job=daily_analytics_job,
    cron_schedule="0 6 * * *",  # 6 AM daily
)
```

### 6. **Sensors**

Sensors trigger jobs based on events:

```python
@sensor(job=etl_job)
def sales_file_sensor(context):
    # Check if sales.csv has been modified
    # Return RunRequest if file changed
```

### 7. **Partitions**

Partitions process data in chunks (e.g., by date):

```python
@asset(partitions_def=DailyPartitionsDefinition(start_date="2023-11-01"))
def daily_partitioned_sales(context, enriched_sales):
    # Process one day at a time
    partition_date = context.partition_key
```

## 🎓 Learning Path

### For Beginners:

1. **Start with Basic Assets**: Look at `basic_assets.py` to see simple data loading
2. **View the Asset Graph**: Open Dagster UI and explore the asset lineage
3. **Materialize an Asset**: Click "Materialize" on `raw_customers`
4. **Check the Database**: Query DuckDB to see the loaded data

### For Intermediate Users:

1. **Explore Transformations**: Study `transformation_assets.py` for SQL transforms
2. **Run a Job**: Execute `daily_analytics_job` to see multiple assets
3. **Add Metadata**: Enhance assets with custom metadata
4. **Create a Schedule**: Modify `schedules.py` to run at different times

### For Advanced Users:

1. **Work with Partitions**: Materialize specific date partitions
2. **Build Sensors**: Create custom sensors for your data sources
3. **Add New Assets**: Extend the project with your own analytics
4. **Configure Resources**: Set up different DuckDB databases for dev/prod

## 🔍 Useful Queries

After materializing all assets, query DuckDB directly:

```python
import duckdb

conn = duckdb.connect("data/warehouse/analytics.duckdb")

# Top customers by revenue
conn.execute("""
    SELECT customer_name, lifetime_value 
    FROM customer_analytics 
    ORDER BY lifetime_value DESC 
    LIMIT 5
""").df()

# Best performing category
conn.execute("""
    SELECT * FROM category_performance
""").df()

# Daily trends
conn.execute("""
    SELECT sale_date, total_revenue, total_profit 
    FROM daily_sales_summary 
    ORDER BY sale_date
""").df()
```

## 🛠️ Common Tasks

### Materialize All Assets
```bash
dagster asset materialize -a
```

### Run a Specific Job
```bash
dagster job execute -j daily_analytics_job
```

### Launch a Run for a Partition
```bash
dagster asset materialize -a daily_partitioned_sales --partition 2023-11-05
```

## 📝 Customization Ideas

1. **Add More Data**: Create additional CSV files for returns, inventory, etc.
2. **New Metrics**: Build assets for customer segmentation or churn analysis
3. **External Sources**: Connect to APIs or databases
4. **Alerts**: Add sensors that notify on data quality issues
5. **Tests**: Write asset tests to validate data quality
6. **Deployment**: Deploy to Dagster Cloud or self-hosted

## 🐛 Troubleshooting

### Import Errors
```bash
# Reinstall in development mode
pip install -e "."
```

### DuckDB Locked
```bash
# Close any open connections and restart Dagster
pkill -f dagster
dagster dev
```

### Assets Not Showing
- Ensure you're in the project directory
- Check that `__init__.py` loads all assets correctly
- Restart the Dagster daemon

## 📚 Resources

- [Dagster Documentation](https://docs.dagster.io/)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [Asset Tutorial](https://docs.dagster.io/concepts/assets/software-defined-assets)
- [Dagster University](https://dagster.io/university)

## 🤝 Contributing

Feel free to extend this example project with:
- Additional asset patterns
- More complex transformations
- Integration with other tools
- Documentation improvements

---

**Happy Learning! 🚀**

For questions or issues, consult the [Dagster community](https://dagster.io/community).

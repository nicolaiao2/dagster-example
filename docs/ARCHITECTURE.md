# Asset Dependency Graph

This document visualizes how assets depend on each other in this project.

## Visual Representation

```
┌─────────────────┐
│   Raw Data      │
│   (CSV Files)   │
└────────┬────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  Basic Assets (Group: raw_data)            │
│                                            │
│  ┌─────────────┐  ┌────────────┐  ┌──────┤
│  │raw_customers│  │raw_products│  │raw_  │
│  └──────┬──────┘  └──────┬─────┘  │sales │
│         │                │         └───┬──┘
└─────────┼────────────────┼─────────────┼───┘
          │                │             │
          └────────┬───────┴─────┬───────┘
                   │             │
                   ▼             ▼
         ┌──────────────────────────────────┐
         │ Transformation Assets            │
         │ (Group: transformed_data)        │
         │                                  │
         │  ┌────────────────┐             │
         │  │enriched_sales  │             │
         │  └────────┬───────┘             │
         │           │                      │
         │  ┌────────────────┐             │
         │  │product_metrics │             │
         │  └────────────────┘             │
         └────────┬───────────────────────┘
                  │
                  ▼
         ┌──────────────────────────────────┐
         │ Analytics Assets                  │
         │ (Group: analytics)                │
         │                                   │
         │  ┌─────────────────────┐         │
         │  │daily_sales_summary  │         │
         │  └─────────────────────┘         │
         │                                   │
         │  ┌─────────────────────┐         │
         │  │customer_analytics   │         │
         │  └─────────────────────┘         │
         │                                   │
         │  ┌─────────────────────┐         │
         │  │category_performance │         │
         │  └─────────────────────┘         │
         │                                   │
         │  ┌─────────────────────┐         │
         │  │state_sales_analysis │         │
         │  └─────────────────────┘         │
         │                                   │
         │  ┌──────────────────────┐        │
         │  │product_recommendations│       │
         │  └──────────────────────┘        │
         └───────────────────────────────────┘

         ┌──────────────────────────────────┐
         │ Partitioned Assets                │
         │ (Group: partitioned)              │
         │                                   │
         │  ┌──────────────────────────┐    │
         │  │daily_partitioned_sales   │    │
         │  │ (by date)                │    │
         │  └──────────────────────────┘    │
         └───────────────────────────────────┘
```

## Detailed Dependencies

### Layer 1: Raw Data (CSV → DuckDB)
```
data/raw/customers.csv  → raw_customers (DuckDB table)
data/raw/products.csv   → raw_products (DuckDB table)
data/raw/sales.csv      → raw_sales (DuckDB table)
```

### Layer 2: Transformations
```
raw_sales + raw_products + raw_customers → enriched_sales
    (JOIN all three tables with calculations)

raw_products → product_metrics
    (Calculate margins and markups)
```

### Layer 3: Analytics
```
enriched_sales → daily_sales_summary
    (Aggregate by date)

enriched_sales → customer_analytics
    (Customer LTV and behavior)

enriched_sales → category_performance
    (Category-level metrics)

enriched_sales → state_sales_analysis
    (Geographic analysis)

enriched_sales → product_recommendations
    (Co-purchase patterns)

enriched_sales → daily_partitioned_sales
    (Partitioned by date)
```

## Data Flow

### Example: From CSV to Analytics

1. **CSV File**: `data/raw/sales.csv`
   ```
   sale_id,customer_id,product_id,quantity,sale_date
   1001,1,101,1,2023-11-01
   ```

2. **Raw Asset**: `raw_sales`
   ```sql
   CREATE TABLE raw_sales AS 
   SELECT * FROM read_csv_auto('data/raw/sales.csv')
   ```

3. **Enriched Asset**: `enriched_sales`
   ```sql
   SELECT 
       s.sale_id,
       c.customer_name,
       p.product_name,
       s.quantity * p.price as total_revenue
   FROM raw_sales s
   JOIN raw_customers c ON s.customer_id = c.customer_id
   JOIN raw_products p ON s.product_id = p.product_id
   ```

4. **Analytics Asset**: `daily_sales_summary`
   ```sql
   SELECT 
       sale_date,
       COUNT(*) as transactions,
       SUM(total_revenue) as revenue
   FROM enriched_sales
   GROUP BY sale_date
   ```

## Job Selections

### `daily_analytics_job`
Materializes: raw_data + transformed_data + analytics groups
```
raw_customers ────┐
raw_products ─────┼──> enriched_sales ──> daily_sales_summary
raw_sales ────────┤                   ├──> customer_analytics
                  │                   ├──> category_performance
                  │                   ├──> state_sales_analysis
                  │                   └──> product_recommendations
                  │
                  └──> product_metrics
```

### `etl_job`
Materializes: raw_data + transformed_data groups only
```
raw_customers ────┐
raw_products ─────┼──> enriched_sales
raw_sales ────────┤
                  └──> product_metrics
```

### `analytics_only_job`
Materializes: analytics group only (assumes raw + transformed exist)
```
enriched_sales ──> daily_sales_summary
(existing)     ├──> customer_analytics
               ├──> category_performance
               ├──> state_sales_analysis
               └──> product_recommendations
```

## Critical Paths

### Fastest Path to Analytics
1. Materialize `raw_customers`, `raw_products`, `raw_sales` (parallel)
2. Materialize `enriched_sales` (depends on all three)
3. Materialize analytics assets (parallel, all depend on enriched_sales)

### Incremental Updates
If only `sales.csv` changes:
1. Re-materialize `raw_sales`
2. Re-materialize `enriched_sales`
3. Re-materialize downstream analytics

## Partitioning Strategy

`daily_partitioned_sales` can be materialized independently for each date:
```
enriched_sales (full) ──> daily_partitioned_sales[2023-11-01]
                      ├──> daily_partitioned_sales[2023-11-02]
                      ├──> daily_partitioned_sales[2023-11-03]
                      └──> ...
```

Each partition processes only data for that specific date.

## Event-Driven Triggers

### Sensor: `sales_file_sensor`
```
data/raw/sales.csv modified
    ↓
Trigger: etl_job
    ↓
Materializes: raw_sales → enriched_sales → product_metrics
```

### Schedule: `daily_schedule`
```
Cron: 6 AM daily
    ↓
Trigger: daily_analytics_job
    ↓
Materializes: Complete pipeline
```

## Asset Characteristics

| Asset | Type | Rows | Update Frequency |
|-------|------|------|------------------|
| raw_customers | Dimension | ~10 | Weekly |
| raw_products | Dimension | ~10 | Weekly |
| raw_sales | Fact | ~20+ | Daily |
| enriched_sales | Fact | ~20+ | Daily |
| product_metrics | Dimension | ~10 | Weekly |
| daily_sales_summary | Aggregate | ~20 | Daily |
| customer_analytics | Aggregate | ~10 | Daily |
| category_performance | Aggregate | ~2 | Daily |
| state_sales_analysis | Aggregate | ~5 | Daily |
| product_recommendations | Recommendation | ~50+ | Daily |

## Performance Considerations

### Parallel Execution
These assets can run in parallel:
- All raw_* assets (no dependencies)
- All analytics assets (same dependency: enriched_sales)

### Sequential Requirements
These must run in sequence:
1. raw_sales (first)
2. enriched_sales (depends on raw_sales)
3. daily_sales_summary (depends on enriched_sales)

### Caching
Dagster will skip re-materialization if:
- Asset code hasn't changed
- Upstream dependencies haven't changed
- Data sources haven't changed (when tracked)

## Extending the Graph

### Adding a New Analytics Asset
```python
@asset(ins={"enriched_sales": AssetIn()})
def my_new_analytics(enriched_sales):
    # Automatically integrates into the graph
    # Will appear downstream of enriched_sales
    pass
```

### Adding a New Data Source
```python
@asset
def raw_returns():
    # New independent data source
    pass

@asset(ins={"raw_returns": AssetIn(), "enriched_sales": AssetIn()})
def sales_with_returns(raw_returns, enriched_sales):
    # Combines new source with existing data
    pass
```

---

View the live graph in the Dagster UI at http://localhost:3000 after running `dagster dev`!

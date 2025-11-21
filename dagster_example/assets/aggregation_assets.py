"""Aggregation assets for analytics and reporting."""

import pandas as pd
from dagster import asset, AssetExecutionContext, Output, MetadataValue
from dagster_example.resources import DuckDBResource


@asset(
    description="Daily sales summary with key metrics",
    deps=["enriched_sales"],
    group_name="analytics",
)
def daily_sales_summary(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> Output[None]:
    """Aggregate sales by day with revenue, cost, and profit metrics."""
    
    query = """
    CREATE OR REPLACE TABLE daily_sales_summary AS
    SELECT 
        sale_date,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT product_id) as unique_products,
        COUNT(*) as total_transactions,
        SUM(quantity) as total_units_sold,
        ROUND(SUM(total_revenue), 2) as total_revenue,
        ROUND(SUM(total_cost), 2) as total_cost,
        ROUND(SUM(total_profit), 2) as total_profit,
        ROUND(SUM(total_profit) / SUM(total_revenue) * 100, 2) as profit_margin_pct
    FROM enriched_sales
    GROUP BY sale_date
    ORDER BY sale_date
    """
    
    context.log.info("Creating daily sales summary")
    with duckdb.get_connection() as conn:
        conn.execute(query)
        
        # Get summary statistics
        stats = conn.execute("""
            SELECT 
                COUNT(*) as days,
                ROUND(AVG(total_revenue), 2) as avg_daily_revenue,
                ROUND(SUM(total_revenue), 2) as total_revenue
            FROM daily_sales_summary
        """).fetchone()
        
        context.log.info(f"Summary covers {stats[0]} days")
        context.log.info(f"Average daily revenue: ${stats[1]}")
        
        return Output(
            None,
            metadata={
                "days_covered": stats[0],
                "avg_daily_revenue": stats[1],
                "total_revenue": stats[2],
            }
        )


@asset(
    description="Customer lifetime value and purchase behavior",
    deps=["enriched_sales"],
    group_name="analytics",
)
def customer_analytics(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> Output[None]:
    """Calculate customer-level metrics including lifetime value."""
    
    query = """
    CREATE OR REPLACE TABLE customer_analytics AS
    SELECT 
        customer_id,
        customer_name,
        city,
        state,
        COUNT(*) as total_purchases,
        SUM(quantity) as total_items_bought,
        ROUND(SUM(total_revenue), 2) as lifetime_value,
        ROUND(AVG(total_revenue), 2) as avg_order_value,
        MIN(sale_date) as first_purchase_date,
        MAX(sale_date) as last_purchase_date
    FROM enriched_sales
    GROUP BY customer_id, customer_name, city, state
    ORDER BY lifetime_value DESC
    """
    
    context.log.info("Creating customer analytics")
    with duckdb.get_connection() as conn:
        conn.execute(query)
        
        # Get top customer
        top_customer = conn.execute("""
            SELECT customer_name, lifetime_value 
            FROM customer_analytics 
            ORDER BY lifetime_value DESC 
            LIMIT 1
        """).fetchone()
        
        context.log.info(f"Top customer: {top_customer[0]} (${top_customer[1]})")
        
        return Output(
            None,
            metadata={
                "top_customer": top_customer[0],
                "top_customer_ltv": top_customer[1],
            }
        )


@asset(
    description="Product performance by category",
    deps=["enriched_sales"],
    group_name="analytics",
)
def category_performance(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> pd.DataFrame:
    """Analyze sales performance by product category."""
    
    query = """
    SELECT 
        category,
        COUNT(DISTINCT product_id) as products_in_category,
        SUM(quantity) as units_sold,
        ROUND(SUM(total_revenue), 2) as revenue,
        ROUND(SUM(total_profit), 2) as profit,
        ROUND(AVG(unit_price), 2) as avg_price,
        ROUND(SUM(total_profit) / SUM(total_revenue) * 100, 2) as profit_margin_pct
    FROM enriched_sales
    GROUP BY category
    ORDER BY revenue DESC
    """
    
    context.log.info("Analyzing category performance")
    with duckdb.get_connection() as conn:
        df = conn.execute(query).df()
        
        # Save to processed data
        output_path = "data/processed/category_performance.csv"
        df.to_csv(output_path, index=False)
        context.log.info(f"Saved category performance to {output_path}")
        
        return df


def get_assets():
    """Return all aggregation assets."""
    return [daily_sales_summary, customer_analytics, category_performance]

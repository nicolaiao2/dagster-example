"""Transformation assets showing data cleaning and joining."""

import pandas as pd
from dagster import asset, AssetExecutionContext
from dagster_example.resources import DuckDBResource


@asset(
    description="Clean and enrich sales data with product and customer information",
    deps=["raw_sales", "raw_products", "raw_customers"],
    group_name="transformed_data",
)
def enriched_sales(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> None:
    """Join sales with products and customers to create enriched sales table."""
    
    query = """
    CREATE OR REPLACE TABLE enriched_sales AS
    SELECT 
        s.sale_id,
        s.sale_date,
        s.quantity,
        c.customer_id,
        c.name as customer_name,
        c.city,
        c.state,
        p.product_id,
        p.product_name,
        p.category,
        p.price as unit_price,
        p.cost as unit_cost,
        s.quantity * p.price as total_revenue,
        s.quantity * p.cost as total_cost,
        s.quantity * (p.price - p.cost) as total_profit
    FROM raw_sales s
    JOIN raw_products p ON s.product_id = p.product_id
    JOIN raw_customers c ON s.customer_id = c.customer_id
    """
    
    context.log.info("Creating enriched sales table")
    with duckdb.get_connection() as conn:
        conn.execute(query)
        result = conn.execute("SELECT COUNT(*) FROM enriched_sales").fetchone()
        count = result[0] if result else 0
        context.log.info(f"Created enriched sales table with {count} records")


@asset(
    description="Calculate product profitability metrics",
    deps=["raw_products"],
    group_name="transformed_data",
)
def product_metrics(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> None:
    """Calculate profit margin and markup for each product."""
    
    query = """
    CREATE OR REPLACE TABLE product_metrics AS
    SELECT 
        product_id,
        product_name,
        category,
        price,
        cost,
        price - cost as profit_per_unit,
        ROUND(((price - cost) / cost) * 100, 2) as markup_percentage,
        ROUND(((price - cost) / price) * 100, 2) as margin_percentage
    FROM raw_products
    ORDER BY margin_percentage DESC
    """
    
    context.log.info("Calculating product metrics")
    with duckdb.get_connection() as conn:
        conn.execute(query)
        
        # Log some insights
        top_margin = conn.execute("""
            SELECT product_name, margin_percentage 
            FROM product_metrics 
            ORDER BY margin_percentage DESC 
            LIMIT 1
        """).fetchone()
        
        top_margin = top_margin if top_margin else ("N/A", 0)
        context.log.info(
            f"Highest margin product: {top_margin[0]} ({top_margin[1]}%)"
        )


def get_assets():
    """Return all transformation assets."""
    return [enriched_sales, product_metrics]

"""Advanced assets demonstrating partitions and complex patterns."""

import pandas as pd
from datetime import datetime
from pathlib import Path
from dagster import (
    asset,
    AssetExecutionContext,
    MonthlyPartitionsDefinition,
    Output,
)
from dagster_example.resources import DuckDBResource

# Define monthly partitions for the month of November 2023
monthly_partitions = MonthlyPartitionsDefinition(start_date="2023-11-01")


@asset(
    description="Sales data partitioned by month",
    partitions_def=monthly_partitions,
    deps=["enriched_sales"],
    group_name="partitioned",
)
def monthly_partitioned_sales(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> Output[pd.DataFrame]:
    """Process sales data for a specific month partition."""
    
    partition_date = context.partition_key
    context.log.info(f"Processing sales for {partition_date}")
    
    query = f"""
    SELECT *
    FROM enriched_sales
    WHERE sale_date >= '{partition_date}' AND sale_date < date_add(DATE '{partition_date}', INTERVAL 1 MONTH)
    """
    
    with duckdb.get_connection() as conn:
        df = conn.execute(query).df()
        
        if len(df) > 0:
            total_revenue = float(df['total_revenue'].sum())
            context.log.info(f"Total Sales in {partition_date}: ${total_revenue:.2f}")
            
            return Output(
                df,
                metadata={
                    "month": partition_date,
                    "num_transactions": int(len(df)),
                    "total_revenue": total_revenue,
                }
            )
        else:
            context.log.info(f"No sales in {partition_date}")
            return Output(
                df,
                metadata={
                    "month": partition_date,
                    "num_transactions": 0,
                    "total_revenue": 0.0,
                }
            )


@asset(
    description="State-level sales analysis",
    deps=["enriched_sales"],
    group_name="analytics",
)
def state_sales_analysis(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> Output[None]:
    """Analyze sales performance by state."""
    
    query = """
    CREATE OR REPLACE TABLE state_sales_analysis AS
    SELECT 
        state,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(*) as total_transactions,
        SUM(quantity) as total_units,
        ROUND(SUM(total_revenue), 2) as total_revenue,
        ROUND(AVG(total_revenue), 2) as avg_transaction_value
    FROM enriched_sales
    GROUP BY state
    ORDER BY total_revenue DESC
    """
    
    context.log.info("Analyzing sales by state")
    with duckdb.get_connection() as conn:
        conn.execute(query)
        
        # Get top state
        result = conn.execute("""
            SELECT state, total_revenue 
            FROM state_sales_analysis 
            ORDER BY total_revenue DESC 
            LIMIT 1
        """).fetchone()
        
        if result:
            context.log.info(f"Top state: {result[0]} (${result[1]})")
            
            return Output(
                None,
                metadata={
                    "top_state": str(result[0]),
                    "top_state_revenue": float(result[1]),
                }
            )
        else:
            context.log.info("No sales data available")
            return Output(
                None,
                metadata={
                    "top_state": None,
                    "top_state_revenue": 0.0,
                }
            )


@asset(
    description="Product recommendations based on sales patterns",
    deps=["enriched_sales"],
    group_name="analytics",
)
def product_recommendations(
    context: AssetExecutionContext,
    duckdb: DuckDBResource,
) -> None:
    """Generate product recommendations based on co-purchase patterns."""
    
    query = """
    CREATE OR REPLACE TABLE product_recommendations AS
    WITH customer_products AS (
        SELECT DISTINCT 
            customer_id,
            product_id,
            product_name
        FROM enriched_sales
    )
    SELECT 
        cp1.product_id as product_id,
        cp1.product_name as product_name,
        cp2.product_id as recommended_product_id,
        cp2.product_name as recommended_product_name,
        COUNT(DISTINCT cp1.customer_id) as co_purchase_count
    FROM customer_products cp1
    JOIN customer_products cp2 
        ON cp1.customer_id = cp2.customer_id 
        AND cp1.product_id != cp2.product_id
    GROUP BY 
        cp1.product_id, 
        cp1.product_name,
        cp2.product_id,
        cp2.product_name
    HAVING co_purchase_count >= 1
    ORDER BY cp1.product_id, co_purchase_count DESC
    """
    
    context.log.info("Generating product recommendations")
    with duckdb.get_connection() as conn:
        conn.execute(query)
        result = conn.execute("SELECT COUNT(*) FROM product_recommendations").fetchone()
        count = result[0] if result else 0
        context.log.info(f"Generated {count} product recommendation pairs")


def get_assets():
    """Return all advanced assets."""
    return [monthly_partitioned_sales, state_sales_analysis, product_recommendations]

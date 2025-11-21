"""Basic assets demonstrating data loading from CSV to DuckDB."""

import pandas as pd
from pathlib import Path
from dagster import asset, AssetExecutionContext
from dagster_example.resources import DuckDBResource


@asset(
    description="Load raw customer data from CSV into DuckDB",
    group_name="raw_data",
)
def raw_customers(context: AssetExecutionContext, duckdb: DuckDBResource) -> None:
    """Load customer data from CSV into DuckDB."""
    csv_path = Path("data/raw/customers.csv").absolute()
    
    context.log.info(f"Loading customers from {csv_path}")
    duckdb.read_csv_to_table(str(csv_path), "raw_customers")
    
    # Log row count
    with duckdb.get_connection() as conn:
        result = conn.execute("SELECT COUNT(*) FROM raw_customers").fetchone()
        count = result[0] if result else 0
        context.log.info(f"Loaded {count} customers")


@asset(
    description="Load raw product data from CSV into DuckDB",
    group_name="raw_data",
)
def raw_products(context: AssetExecutionContext, duckdb: DuckDBResource) -> None:
    """Load product data from CSV into DuckDB."""
    csv_path = Path("data/raw/products.csv").absolute()
    
    context.log.info(f"Loading products from {csv_path}")
    duckdb.read_csv_to_table(str(csv_path), "raw_products")
    
    # Log row count
    with duckdb.get_connection() as conn:
        result = conn.execute("SELECT COUNT(*) FROM raw_products").fetchone()
        count = result[0] if result else 0
        context.log.info(f"Loaded {count} products")


@asset(
    description="Load raw sales data from CSV into DuckDB",
    group_name="raw_data",
)
def raw_sales(context: AssetExecutionContext, duckdb: DuckDBResource) -> None:
    """Load sales data from CSV into DuckDB."""
    csv_path = Path("data/raw/sales.csv").absolute()
    
    context.log.info(f"Loading sales from {csv_path}")
    duckdb.read_csv_to_table(str(csv_path), "raw_sales")
    
    # Log row count
    with duckdb.get_connection() as conn:
        result = conn.execute("SELECT COUNT(*) FROM raw_sales").fetchone()
        count = result[0] if result else 0
        context.log.info(f"Loaded {count} sales records")


def get_assets():
    """Return all basic assets."""
    return [raw_customers, raw_products, raw_sales]

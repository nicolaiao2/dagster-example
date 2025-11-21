"""
Example tests for Dagster assets.

Run with: pytest tests/
"""

import pytest
from dagster import build_asset_context, materialize
from dagster_example.resources import DuckDBResource
from dagster_example.assets.basic_assets import raw_customers, raw_products, raw_sales


def test_raw_customers_asset():
    """Test that raw_customers asset can be materialized."""
    context = build_asset_context()
    duckdb = DuckDBResource(database_path=":memory:")
    
    # Should not raise an exception
    raw_customers(context, duckdb)
    
    # Verify table was created
    with duckdb.get_connection() as conn:
        result = conn.execute("SELECT COUNT(*) FROM raw_customers").fetchone()
        if result:
            assert result[0] > 0, "Should have loaded customer data"
        else:
            pytest.fail("raw_customers table does not exist")

def test_raw_products_asset():
    """Test that raw_products asset can be materialized."""
    context = build_asset_context()
    duckdb = DuckDBResource(database_path=":memory:")
    
    raw_products(context, duckdb)
    
    with duckdb.get_connection() as conn:
        result = conn.execute("SELECT COUNT(*) FROM raw_products").fetchone()
        if result:
            assert result[0] > 0, "Should have loaded product data"
        else:
            pytest.fail("raw_products table does not exist")


def test_raw_sales_asset():
    """Test that raw_sales asset can be materialized."""
    context = build_asset_context()
    duckdb = DuckDBResource(database_path=":memory:")
    
    raw_sales(context, duckdb)
    
    with duckdb.get_connection() as conn:
        result = conn.execute("SELECT COUNT(*) FROM raw_sales").fetchone()
        if result:
            assert result[0] > 0, "Should have loaded sales data"
        else:
            pytest.fail("raw_sales table does not exist")

def test_duckdb_resource():
    """Test DuckDB resource functionality."""
    duckdb = DuckDBResource(database_path=":memory:")
    
    with duckdb.get_connection() as conn:
        # Test basic query
        result = conn.execute("SELECT 1 + 1 as sum").fetchone()
        if result:
            assert result[0] == 2, "Basic arithmetic query should return 2"


# Integration test example
def test_full_pipeline():
    """Test materializing multiple dependent assets."""
    from dagster_example import defs
    
    # Materialize just the raw data assets
    result = materialize(
        [raw_customers, raw_products, raw_sales],
        resources={"duckdb": DuckDBResource(database_path=":memory:")},
    )
    
    assert result.success, "Pipeline should complete successfully"

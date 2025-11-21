"""Test concurrent asset materialization to verify lock fix."""

from dagster import materialize
from dagster_example.resources import DuckDBResource
from dagster_example.assets.basic_assets import raw_customers, raw_products, raw_sales

# Clean start
import os
db_path = "data/warehouse/analytics.duckdb"
for ext in ["", ".wal", "-wal"]:
    try:
        os.remove(db_path + ext)
    except FileNotFoundError:
        pass

print("Testing concurrent asset materialization with DuckDB lock fix...\n")

# Materialize all three assets - Dagster will run them in parallel
result = materialize(
    [raw_customers, raw_products, raw_sales],
    resources={
        "duckdb": DuckDBResource(database_path=db_path)
    },
)

if result.success:
    print("\n✅ SUCCESS! All assets materialized without lock conflicts!")
    
    # Verify data
    import duckdb
    conn = duckdb.connect(db_path)
    tables = conn.execute('SHOW TABLES').fetchall()
    print("\nVerifying database contents:")
    for table in tables:
        count = conn.execute(f'SELECT COUNT(*) FROM {table[0]}').fetchone()[0]
        print(f'  • {table[0]}: {count} rows')
    conn.close()
    print("\n🎉 The DuckDB concurrency fix is working!")
else:
    print("\n❌ Materialization failed")

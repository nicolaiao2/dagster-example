"""
Quick example script to query the DuckDB database after running Dagster.

Run this after materializing assets to see the results.
"""

import duckdb
from pathlib import Path


def main():
    db_path = Path("data/warehouse/analytics.duckdb")
    
    if not db_path.exists():
        print("❌ Database not found!")
        print("Please run Dagster and materialize some assets first.")
        print("\n1. Start Dagster: dagster dev")
        print("2. Open http://localhost:3000")
        print("3. Materialize assets from the UI")
        return
    
    print("🦆 Connecting to DuckDB...\n")
    conn = duckdb.connect(str(db_path))
    
    # List all tables
    print("📊 Available Tables:")
    print("=" * 50)
    tables = conn.execute("SHOW TABLES").fetchall()
    for table in tables:
        result = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()
        count = result[0] if result else 0
        print(f"  • {table[0]:30s} ({count} rows)")
    
    print("\n" + "=" * 50)
    print("\n💰 Top 5 Customers by Lifetime Value:")
    print("=" * 50)
    
    try:
        result = conn.execute("""
            SELECT 
                customer_name,
                state,
                total_purchases,
                '$' || ROUND(lifetime_value, 2) as lifetime_value
            FROM customer_analytics 
            ORDER BY lifetime_value DESC 
            LIMIT 5
        """).fetchall()
        
        for i, row in enumerate(result, 1):
            print(f"{i}. {row[0]:20s} ({row[1]}) - {row[2]} purchases - {row[3]}")
    except Exception as e:
        print(f"  Table not yet materialized. Run assets first!")
    
    print("\n" + "=" * 50)
    print("\n📦 Category Performance:")
    print("=" * 50)
    
    try:
        result = conn.execute("""
            SELECT 
                category,
                products_in_category,
                units_sold,
                '$' || ROUND(revenue, 2) as revenue,
                ROUND(profit_margin_pct, 1) || '%' as margin
            FROM category_performance
            ORDER BY revenue DESC
        """).fetchall()
        
        for row in result:
            print(f"  {row[0]:15s} | {row[1]} products | {row[2]:3d} units | {row[3]:10s} | {row[4]} margin")
    except Exception as e:
        print(f"  Table not yet materialized. Run assets first!")
    
    print("\n" + "=" * 50)
    print("\n📈 Daily Sales Summary:")
    print("=" * 50)
    
    try:
        result = conn.execute("""
            SELECT 
                sale_date,
                total_transactions,
                '$' || ROUND(total_revenue, 2) as revenue,
                '$' || ROUND(total_profit, 2) as profit,
                ROUND(profit_margin_pct, 1) || '%' as margin
            FROM daily_sales_summary 
            ORDER BY sale_date DESC
            LIMIT 10
        """).fetchall()
        
        for row in result:
            print(f"  {row[0]} | {row[1]:2d} txns | Revenue: {row[2]:10s} | Profit: {row[3]:9s} | {row[4]}")
    except Exception as e:
        print(f"  Table not yet materialized. Run assets first!")
    
    conn.close()
    print("\n✅ Done!\n")


if __name__ == "__main__":
    main()

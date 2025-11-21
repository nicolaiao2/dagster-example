#!/usr/bin/env python
"""
Generate random daily sample sales data from 2023-01-01 until today.

- Reads:
    data/raw/customers.csv
    data/raw/products.csv
    data/raw/sales.csv

- Extends:
    data/raw/sales.csv

The script:
- Keeps all existing rows in sales.csv
- Ensures every date in [2023-01-01, today] has >= 1 sale
- For missing days, generates random sales with existing customers/products
"""

from __future__ import annotations

import random
from datetime import date, datetime
from pathlib import Path

import pandas as pd


START_DATE = date(2023, 1, 1)


def load_csvs(raw_dir: Path):
    customers_path = raw_dir / "customers.csv"
    products_path = raw_dir / "products.csv"
    sales_path = raw_dir / "sales.csv"

    if not customers_path.exists():
        raise FileNotFoundError(f"Missing {customers_path}")
    if not products_path.exists():
        raise FileNotFoundError(f"Missing {products_path}")
    if not sales_path.exists():
        raise FileNotFoundError(f"Missing {sales_path}")

    customers = pd.read_csv(customers_path)
    products = pd.read_csv(products_path)
    sales = pd.read_csv(sales_path)

    return customers, products, sales, sales_path


def generate_missing_sales(
    customers: pd.DataFrame,
    products: pd.DataFrame,
    sales: pd.DataFrame,
    start_date: date,
    end_date: date,
    seed: int | None = 42,
) -> pd.DataFrame:
    """Return an extended sales DataFrame with at least one sale per day."""
    if seed is not None:
        random.seed(seed)

    # Ensure sale_date is datetime.date
    if not sales.empty:
        sales = sales.copy()
        sales["sale_date"] = pd.to_datetime(sales["sale_date"]).dt.date

    # All days in the desired period
    all_dates = pd.date_range(start_date, end_date, freq="D").date
    existing_dates = set(sales["sale_date"]) if not sales.empty else set()

    customer_ids = customers["customer_id"].tolist()
    product_ids = products["product_id"].tolist()

    # Start sale_id after the current max, or at 1001 if empty
    if not sales.empty and "sale_id" in sales.columns:
        next_sale_id = int(sales["sale_id"].max()) + 1
    else:
        next_sale_id = 1001

    new_rows = []

    for d in all_dates:
        if d in existing_dates:
            # Already have at least one sale this day; skip
            continue

        # Random number of sales for this day
        num_sales = random.randint(1, 5)

        for _ in range(num_sales):
            cid = random.choice(customer_ids)
            pid = random.choice(product_ids)
            qty = random.randint(1, 5)

            new_rows.append(
                {
                    "sale_id": next_sale_id,
                    "customer_id": cid,
                    "product_id": pid,
                    "quantity": qty,
                    "sale_date": d,
                }
            )
            next_sale_id += 1

    if new_rows:
        new_sales = pd.DataFrame(new_rows)
        # Combine existing + new
        if sales.empty:
            sales_extended = new_sales
        else:
            sales_extended = pd.concat([sales, new_sales], ignore_index=True)
    else:
        # Nothing to add
        sales_extended = sales

    # Sort nicely
    sales_extended = sales_extended.sort_values(["sale_date", "sale_id"]).reset_index(drop=True)

    # Convert sale_date back to ISO string for CSV
    sales_extended["sale_date"] = sales_extended["sale_date"].apply(
        lambda d: d.isoformat() if isinstance(d, (date, datetime)) else str(d)
    )

    return sales_extended


def main():
    base_dir = Path(__file__).resolve().parent
    raw_dir = base_dir / "data" / "raw"

    end_date = date.today()  # today; currently 2025-11-21 for your test

    customers, products, sales, sales_path = load_csvs(raw_dir)
    sales_extended = generate_missing_sales(customers, products, sales, START_DATE, end_date)

    # Overwrite sales.csv
    sales_extended.to_csv(sales_path, index=False)
    print(f"Extended sales data written to {sales_path}")
    print(f"Total rows: {len(sales_extended)}")
    print(f"Date range: {sales_extended['sale_date'].min()} -> {sales_extended['sale_date'].max()}")


if __name__ == "__main__":
    main()

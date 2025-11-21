#!/usr/bin/env python3
"""
Script to open DuckDB UI for exploring the analytics database.

Usage:
    python open_duckdb_ui.py
"""

import sys
import time
from pathlib import Path

import duckdb

# Path to the DuckDB database
DB_PATH = "data/warehouse/analytics.duckdb"


def main():
    db_file = Path(DB_PATH)

    if not db_file.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("Run 'dagster dev' and materialize some assets first.")
        sys.exit(1)

    print(f"Opening DuckDB UI for: {DB_PATH}")
    print("Install & load the 'ui' extension and start the web UI server.")
    print("Navigate to http://localhost:4213 to access the UI.")
    print("Press Ctrl+C here to stop the server.\n")

    conn = None
    try:
        # Connect to the database
        conn = duckdb.connect(DB_PATH)

        # Install & load the DuckDB UI extension
        try:
            print("👉 Installing 'ui' extension (if not already installed)...")
            conn.execute("INSTALL ui;")
            conn.execute("LOAD ui;")
        except Exception as e:
            print("⚠️ Could not install/load 'ui' extension.")
            print(f"   Error: {e}")
            print(
                "\nThis DuckDB build should support the UI, but the extension "
                "repository might be unreachable (network/firewall issue), "
                "or the binary for your platform is missing."
            )
            sys.exit(1)

        # Start the UI HTTP server
        try:
            print("🚀 Starting DuckDB UI server on http://localhost:4213 ...")
            conn.execute("CALL start_ui_server();")
        except Exception as e:
            print("❌ Failed to start DuckDB UI server with 'CALL start_ui_server();'")
            print(f"   Error: {e}")
            print(
                "\nTry upgrading DuckDB and check the UI extension docs: "
                "https://duckdb.org/docs/stable/core_extensions/ui.html"
            )
            sys.exit(1)

        print("\n✅ DuckDB UI server is running.")
        print("Open your browser at: http://localhost:4213")
        print("Press Ctrl+C in this terminal to stop the server.\n")

        # Keep the process alive so the server stays up
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping DuckDB UI server and closing connection...")
        if conn is not None:
            try:
                # Best-effort attempt to stop the UI server cleanly
                conn.execute("CALL stop_ui_server();")
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass
        print("✅ Done.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main()
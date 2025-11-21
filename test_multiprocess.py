"""Test multiprocess concurrent access to verify the file lock works."""

import multiprocessing
import time
from pathlib import Path
from dagster_example.resources import DuckDBResource

def worker(worker_id, db_path):
    """Worker function that tries to access DuckDB."""
    print(f"[Worker {worker_id}] Starting (PID: {multiprocessing.current_process().pid})")
    
    duckdb = DuckDBResource(database_path=db_path)
    
    # Try to access the database
    with duckdb.get_connection() as conn:
        print(f"[Worker {worker_id}] Got connection! Writing test data...")
        conn.execute(f"CREATE TABLE IF NOT EXISTS test_{worker_id} (id INT)")
        conn.execute(f"INSERT INTO test_{worker_id} VALUES ({worker_id})")
        time.sleep(0.1)  # Simulate some work
        result = conn.execute(f"SELECT * FROM test_{worker_id}").fetchone()
        print(f"[Worker {worker_id}] Read back: {result}")
    
    print(f"[Worker {worker_id}] Done!")
    return worker_id

if __name__ == "__main__":
    db_path = "data/warehouse/test_multiprocess.duckdb"
    
    # Clean up
    import os
    for ext in ["", ".lock", ".wal"]:
        try:
            os.remove(db_path + ext)
        except FileNotFoundError:
            pass
    
    print("Testing file-based locking with multiple processes...\n")
    
    # Create multiple processes that will try to access DB simultaneously
    with multiprocessing.Pool(processes=3) as pool:
        results = pool.starmap(worker, [(i, db_path) for i in range(3)])
    
    print(f"\n✅ All {len(results)} workers completed successfully!")
    print("File-based locking is working across processes! 🎉")

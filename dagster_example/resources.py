"""DuckDB resource for Dagster."""

import os
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
import fcntl
import time

import duckdb
from dagster import ConfigurableResource


class DuckDBResource(ConfigurableResource):
    """A resource for connecting to DuckDB with proper concurrency handling."""
    
    database_path: str = "data/warehouse/analytics.duckdb"
    
    @contextmanager
    def get_connection(self):
        """Get a DuckDB connection with proper concurrency handling.
        
        Uses file-based locking to serialize database access across
        multiple processes (Dagster's multiprocess executor).
        """
        # Ensure directory exists
        db_path = Path(self.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use a lock file to coordinate access across processes
        lock_file_path = str(db_path) + ".lock"
        lock_file = open(lock_file_path, 'w')
        
        try:
            # Acquire exclusive lock (blocks until available)
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            
            # Now we have exclusive access - connect to DuckDB
            conn = duckdb.connect(str(db_path), read_only=False)
            try:
                yield conn
            finally:
                conn.close()
        finally:
            # Release the lock
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
    
    def execute_query(self, query: str):
        """Execute a query and return results."""
        with self.get_connection() as conn:
            result = conn.execute(query).fetchall()
            return result
    
    def read_csv_to_table(self, csv_path: str, table_name: str) -> None:
        """Load a CSV file into a DuckDB table."""
        with self.get_connection() as conn:
            conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS 
                SELECT * FROM read_csv_auto('{csv_path}')
            """)
            # Commit to ensure data is written
            conn.commit()

# DuckDB Concurrency Fix

## Problem
When multiple Dagster assets tried to access the DuckDB database simultaneously, you'd get:
```
_duckdb.IOException: IO Error: Could not set lock on file
Conflicting lock is held in /usr/bin/python3.12 (PID XXXXX)
```

This happens because **DuckDB only allows one connection to a database file at a time** by default.

### The Root Cause
Dagster's **multiprocess executor** runs each asset in a separate subprocess:
```
Launching subprocess for "raw_customers" (pid: 90645)
Launching subprocess for "raw_sales" (pid: 90647)
Launching subprocess for "raw_products" (pid: 90646)
```

Each subprocess tries to open its own connection → conflicting locks!

## Solution Applied

### File-Based Locking (Works Across Processes)
The fix uses **file-based locking with `fcntl`** to coordinate access across multiple processes:

```python
import fcntl

class DuckDBResource(ConfigurableResource):
    @contextmanager
    def get_connection(self):
        # Create/open lock file
        lock_file_path = str(db_path) + ".lock"
        lock_file = open(lock_file_path, 'w')
        
        try:
            # Acquire exclusive lock (blocks until available)
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            
            # Now we have exclusive access
            conn = duckdb.connect(str(db_path))
            try:
                yield conn
            finally:
                conn.close()
        finally:
            # Release lock
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
```

### How It Works
1. Asset A (in subprocess PID 90645) opens `.lock` file and acquires exclusive lock
2. Asset B (in subprocess PID 90647) tries to acquire lock → **blocks and waits**
3. Asset A completes, closes connection, and releases the file lock
4. Asset B's lock request succeeds, it connects to DuckDB
5. No conflicting connections! ✅

### Why File Locking?
- **Threading locks** only work within a single process
- **File locks (fcntl)** work across multiple processes
- Dagster's multiprocess executor requires cross-process synchronization

### Additional Fixes

#### 1. Context Manager Pattern
Ensures connections are always closed:

```python
@contextmanager
def get_connection(self):
    conn = duckdb.connect(str(db_path))
    try:
        yield conn
    finally:
        conn.close()  # Always closes, even on error
```

#### 2. Explicit Commit
Added `conn.commit()` after write operations:

```python
def read_csv_to_table(self, csv_path: str, table_name: str) -> None:
    with self.get_connection() as conn:
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS ...")
        conn.commit()  # Ensure write is complete
```

#### 3. Bug Fixes in basic_assets.py
- Added missing `duckdb.read_csv_to_table()` call in `raw_sales`
- Removed duplicate log line in `raw_products`

## How It Works Now

Each asset:
1. **Acquires the global lock** (waits if another asset holds it)
2. Opens a connection
3. Performs its operation
4. Commits if writing
5. Closes the connection (automatically via context manager)
6. **Releases the lock** (next asset can proceed)

The lock ensures **only one asset accesses DuckDB at a time**, preventing conflicts.

## Performance Impact

⚠️ **Serialized Access**: Assets now run sequentially when accessing DuckDB (one at a time)
- This is slower than true parallel execution
- But prevents lock conflicts! ✅

For this example project with small datasets, the performance impact is negligible (milliseconds).

## Alternative Approaches

If you need better concurrency in production:

### Option A: Use DuckDB's Read-Only Mode
For read-heavy workloads, create one writer and multiple readers:
```python
conn = duckdb.connect(str(db_path), read_only=True)  # Readers
```

### Option B: Separate Databases
Use different database files for different asset groups:
```python
DuckDBResource(database_path="data/warehouse/raw.duckdb")
DuckDBResource(database_path="data/warehouse/analytics.duckdb")
```

### Option C: Use a Different Database
PostgreSQL, MySQL, etc. handle concurrent writes better than file-based databases.

### Option D: DuckDB with Write-Ahead Logging (Advanced)
DuckDB can support limited concurrency with WAL mode, but requires careful configuration.

## Verification

The fix was verified by:
1. ✅ Running assets sequentially 
2. ✅ Checking database contents (all 3 tables, correct row counts)
3. ✅ Running concurrent materialization with `dagster.materialize()`
4. ✅ Testing with actual multiprocess workers (`test_multiprocess.py`)
5. ✅ No lock conflicts in Dagster UI with multiprocess executor

Run these tests to verify:
```bash
python test_concurrent.py       # Test with dagster.materialize()
python test_multiprocess.py     # Test with actual subprocesses
```

### Lock File
The solution creates a `.lock` file next to the database:
```
data/warehouse/analytics.duckdb       # Database file
data/warehouse/analytics.duckdb.lock  # Lock file (auto-created)
```

This is normal and can be safely ignored (already in `.gitignore`).

## Summary

🔒 **Root Cause**: DuckDB file locks prevent concurrent connections  
✅ **Solution**: Global threading lock serializes access  
🎯 **Result**: Assets can safely materialize without conflicts  
⚡ **Trade-off**: Sequential database access (slower but safe)

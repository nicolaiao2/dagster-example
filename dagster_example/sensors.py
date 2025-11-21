"""Sensors for event-driven pipelines."""

import os
from pathlib import Path
from dagster import sensor, RunRequest, SensorEvaluationContext, SkipReason
from dagster_example.jobs import etl_job


@sensor(
    job=etl_job,
    description="Trigger ETL when new sales CSV files are detected",
)
def sales_file_sensor(context: SensorEvaluationContext):
    """Watch for new or modified sales CSV files."""
    
    sales_file = Path("data/raw/sales.csv")
    
    if not sales_file.exists():
        return SkipReason("Sales file does not exist")
    
    # Get last modified time
    last_modified = sales_file.stat().st_mtime
    
    # Check cursor (last processed time)
    cursor = float(context.cursor) if context.cursor else 0
    
    if last_modified > cursor:
        context.log.info(f"Detected updated sales file (modified: {last_modified})")
        
        return RunRequest(
            run_key=f"sales_update_{last_modified}",
            run_config={},
        )
    else:
        return SkipReason("No new updates to sales file")


# Example of a more complex sensor
@sensor(
    job=etl_job,
    minimum_interval_seconds=60,  # Check every minute
    description="Example sensor that monitors multiple files",
)
def multi_file_sensor(context: SensorEvaluationContext):
    """Watch for updates to any raw data file."""
    
    raw_files = [
        Path("data/raw/sales.csv"),
        Path("data/raw/customers.csv"),
        Path("data/raw/products.csv"),
    ]
    
    latest_modified = 0
    modified_files = []
    
    for file_path in raw_files:
        if file_path.exists():
            mtime = file_path.stat().st_mtime
            if mtime > latest_modified:
                latest_modified = mtime
                modified_files.append(file_path.name)
    
    cursor = float(context.cursor) if context.cursor else 0
    
    if latest_modified > cursor:
        context.log.info(f"Detected updates in: {', '.join(modified_files)}")
        context.update_cursor(str(latest_modified))
        
        return RunRequest(
            run_key=f"multi_file_update_{latest_modified}",
            run_config={},
        )
    
    return SkipReason("No updates to raw data files")

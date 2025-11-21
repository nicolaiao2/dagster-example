"""Dagster example project with CSV files and DuckDB."""

from dagster import Definitions
from dagster_example.resources import DuckDBResource
from dagster_example.assets import (
    basic_assets,
    transformation_assets,
    aggregation_assets,
    advanced_assets,
)
from dagster_example.jobs import daily_analytics_job, etl_job, analytics_only_job
from dagster_example.schedules import daily_schedule
from dagster_example.sensors import sales_file_sensor, multi_file_sensor


# Define all assets
all_assets = [
    *basic_assets.get_assets(),
    *transformation_assets.get_assets(),
    *aggregation_assets.get_assets(),
    *advanced_assets.get_assets(),
]

# Define resources
resources = {
    "duckdb": DuckDBResource(database_path="data/warehouse/analytics.duckdb"),
}

# Create Definitions object
defs = Definitions(
    assets=all_assets,
    resources=resources,
    jobs=[daily_analytics_job, etl_job, analytics_only_job],
    schedules=[daily_schedule],
    sensors=[sales_file_sensor, multi_file_sensor],
)

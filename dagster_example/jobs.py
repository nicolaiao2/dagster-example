"""Jobs for orchestrating asset materializations."""

from dagster import AssetSelection, define_asset_job


# Job that materializes all analytics assets
daily_analytics_job = define_asset_job(
    name="daily_analytics_job",
    description="Daily job to refresh all analytics tables",
    selection=AssetSelection.groups("raw_data", "transformed_data", "analytics"),
)


# Job for just the ETL pipeline
etl_job = define_asset_job(
    name="etl_job",
    description="ETL pipeline: raw data -> transformed data",
    selection=AssetSelection.groups("raw_data", "transformed_data"),
)


# Job for just analytics
analytics_only_job = define_asset_job(
    name="analytics_only_job",
    description="Run analytics on existing transformed data",
    selection=AssetSelection.groups("analytics"),
)

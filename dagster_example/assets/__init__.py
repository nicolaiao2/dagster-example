"""Assets module - imports all asset groups."""

from dagster_example.assets import (
    basic_assets,
    transformation_assets,
    aggregation_assets,
    advanced_assets,
)

__all__ = [
    "basic_assets",
    "transformation_assets",
    "aggregation_assets",
    "advanced_assets",
]

"""Schedules for running jobs automatically."""

from dagster import ScheduleDefinition
from dagster_example.jobs import daily_analytics_job


# Run analytics every day at 6 AM
daily_schedule = ScheduleDefinition(
    job=daily_analytics_job,
    cron_schedule="0 6 * * *",  # 6 AM every day
    description="Run daily analytics refresh at 6 AM",
)


# You can add more schedules
# weekly_schedule = ScheduleDefinition(
#     job=daily_analytics_job,
#     cron_schedule="0 7 * * 1",  # 7 AM every Monday
# )

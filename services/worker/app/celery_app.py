import os
from celery import Celery
from celery.schedules import crontab

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create Celery app
celery_app = Celery(
    "quilent_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.ingest",
        "app.tasks.alerts",
        "app.tasks.ai",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "ingest-sam-gov-daily": {
        "task": "app.tasks.ingest.ingest_sam_gov",
        "schedule": crontab(hour=6, minute=0),  # 6 AM UTC daily
    },
    "process-alerts-hourly": {
        "task": "app.tasks.alerts.process_pending_alerts",
        "schedule": crontab(minute=0),  # Every hour
    },
}

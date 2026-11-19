
import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL")

celery_app = Celery(
    "storage_service",
    broker=broker_url,
    include=[
        "app.tasks.test_tasks",
        "app.tasks.upload_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Bogota",
    enable_utc=True,
)

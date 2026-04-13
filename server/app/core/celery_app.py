import os

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

# Celery's prefork/spawn pools are unstable on Windows for many local setups.
# Force a single-process worker there to avoid WinError 5 semaphore/lock issues.
windows_worker_overrides = {}
if os.name == "nt":
    windows_worker_overrides = {
        "worker_pool": "solo",
        "worker_concurrency": 1,
    }

celery_app = Celery(
    "smartcope",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.ingestion_tasks"],
)

celery_app.conf.update(
    task_default_queue="ingestion",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    **windows_worker_overrides,
)

# Keep autodiscovery for future task modules, while include above guarantees
# ingestion_tasks is always imported and registered on worker startup.
celery_app.autodiscover_tasks(["app.tasks"])
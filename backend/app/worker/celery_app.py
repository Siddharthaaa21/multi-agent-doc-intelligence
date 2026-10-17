import logging
from celery import Celery
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery Application
celery_app = Celery(
    "strata_orchestrator",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"]
)

# Institutional Task Queue Configurations
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    
    # Fair Task Dispatching: Prefetch 1 task per worker concurrency slot
    # Essential for long-running document analysis workloads (prevent worker starvation)
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Timeouts & Deadlines
    task_time_limit=600,       # Hard limit: 10 minutes per document
    task_soft_time_limit=540,  # Soft limit: 9 minutes
    
    # Test & Eager Mode
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_eager_propagates=True,
    
    # Result Expiration (24 hours)
    result_expires=86400,
)

if __name__ == "__main__":
    celery_app.start()

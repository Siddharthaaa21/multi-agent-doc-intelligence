import logging
from typing import Dict, Any, Optional
import redis
from app.config import settings
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

class QueueInspector:
    """
    Health check and telemetry inspector for distributed Celery workers and Redis queue.
    """

    def __init__(self, broker_url: Optional[str] = None):
        self.broker_url = broker_url or settings.CELERY_BROKER_URL

    def check_redis_health(self) -> Dict[str, Any]:
        """Check direct connectivity to the Redis broker."""
        try:
            r = redis.Redis.from_url(self.broker_url, socket_connect_timeout=1.5, socket_timeout=1.5)
            ping_ok = r.ping()
            queue_len = r.llen("celery")
            info = r.info("server")
            return {
                "redis_online": bool(ping_ok),
                "queue_depth": queue_len,
                "redis_version": info.get("redis_version", "unknown"),
                "uptime_seconds": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            logger.debug(f"Redis health check failed (broker: {self.broker_url}): {e}")
            return {
                "redis_online": False,
                "queue_depth": 0,
                "error": str(e)
            }

    def inspect_celery_workers(self) -> Dict[str, Any]:
        """Inspect Celery control metrics across connected worker nodes."""
        try:
            inspect = celery_app.control.inspect(timeout=1.0)
            active_tasks = inspect.active() or {}
            reserved_tasks = inspect.reserved() or {}
            scheduled_tasks = inspect.scheduled() or {}
            stats = inspect.stats() or {}

            worker_count = len(stats)
            total_active = sum(len(tasks) for tasks in active_tasks.values())
            total_reserved = sum(len(tasks) for tasks in reserved_tasks.values())
            total_scheduled = sum(len(tasks) for tasks in scheduled_tasks.values())

            return {
                "celery_workers_online": worker_count > 0,
                "active_workers_count": worker_count,
                "active_tasks_count": total_active,
                "reserved_tasks_count": total_reserved,
                "scheduled_tasks_count": total_scheduled,
                "workers": list(stats.keys())
            }
        except Exception as e:
            logger.debug(f"Celery worker inspection timed out or unavailable: {e}")
            return {
                "celery_workers_online": False,
                "active_workers_count": 0,
                "active_tasks_count": 0,
                "error": str(e)
            }

    def get_full_queue_status(self) -> Dict[str, Any]:
        """Return combined system status for Redis queue depth and Celery workers."""
        redis_status = self.check_redis_health()
        celery_status = self.inspect_celery_workers()

        is_distributed = redis_status.get("redis_online", False) and celery_status.get("celery_workers_online", False)

        return {
            "mode": "distributed_celery" if is_distributed else "in_process_fallback",
            "distributed_enabled": settings.USE_DISTRIBUTED_QUEUE,
            "broker_url": self.broker_url.split("@")[-1],  # sanitize credentials if any
            "redis": redis_status,
            "celery": celery_status,
            "sla_concurrency_capacity": max(1, celery_status.get("active_workers_count", 1) * 4)
        }

queue_inspector = QueueInspector()

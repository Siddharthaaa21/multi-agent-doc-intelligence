import asyncio
import logging
import time
from typing import Dict, Any, Optional
from celery import Task
from app.worker.celery_app import celery_app
from app.orchestrator.runner import JOB_STORE, runner
from app.orchestrator.graph import orchestrator_graph
from app.models.state import DocumentState

logger = logging.getLogger(__name__)

class CallbackTask(Task):
    """Custom Celery Task base class supporting state synchronization."""
    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"[Celery] Task {task_id} completed successfully.")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"[Celery] Task {task_id} failed with error: {exc}")

async def _execute_orchestrator_async(
    job_id: str,
    raw_text: str,
    filename: str,
    inject_trap: bool = False,
    provider: str = "simulation"
) -> Dict[str, Any]:
    """Execute LangGraph workflow and persist state."""
    # Ensure job state exists in local memory store
    if job_id not in JOB_STORE:
        runner.create_job(
            raw_text=raw_text,
            filename=filename,
            inject_hallucination_trap=inject_trap,
            llm_provider=provider,
            job_id=job_id
        )
    
    return await runner.run_job(job_id)

@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="orchestrate_document_task",
    max_retries=3,
    default_retry_delay=5
)
def orchestrate_document_task(
    self,
    job_id: str,
    raw_text: str,
    filename: str,
    inject_hallucination_trap: bool = False,
    llm_provider: str = "simulation"
) -> Dict[str, Any]:
    """
    Celery task orchestrating multi-agent document analysis in a background worker process.
    Supports automatic retries with exponential backoff on transient LLM or database errors.
    """
    logger.info(f"[Celery Worker] Starting orchestration task for Job {job_id} ({filename})")
    
    try:
        # Run async graph inside worker loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                _execute_orchestrator_async(
                    job_id=job_id,
                    raw_text=raw_text,
                    filename=filename,
                    inject_trap=inject_hallucination_trap,
                    provider=llm_provider
                )
            )
            return {
                "job_id": job_id,
                "status": result.get("status", "completed"),
                "total_turnaround_time_sec": result.get("total_turnaround_time_sec", 0.0),
                "classification": result.get("classification"),
                "metrics_count": len(result.get("financial_metrics", [])),
                "risk_count": len(result.get("risk_factors", [])),
                "guardrail_verified": result.get("guardrail_result", {}).get("is_verified", False)
            }
        finally:
            loop.close()

    except Exception as exc:
        logger.error(f"[Celery Worker] Error executing job {job_id}: {exc}", exc_info=True)
        retry_delay = min(60, 2 ** self.request.retries * 2)
        try:
            raise self.retry(exc=exc, countdown=retry_delay)
        except self.MaxRetriesExceededError:
            logger.critical(f"[Celery Worker] Max retries exceeded for job {job_id}.")
            return {"job_id": job_id, "status": "failed", "error": str(exc)}

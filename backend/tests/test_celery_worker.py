import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.worker.celery_app import celery_app
from app.worker.tasks import orchestrate_document_task
from app.worker.inspector import QueueInspector, queue_inspector
from app.orchestrator.runner import JOB_STORE

@pytest.fixture
def client():
    return TestClient(app)

def test_celery_app_configuration():
    """Verify production settings for task serialization and prefetch multiplier."""
    conf = celery_app.conf
    assert conf.task_serializer == "json"
    assert conf.result_serializer == "json"
    assert conf.worker_prefetch_multiplier == 1
    assert conf.task_acks_late is True
    assert conf.task_time_limit == 600

def test_orchestrate_document_task_eager_execution():
    """Verify that orchestrate_document_task executes workflow and persists state."""
    raw_doc = """
    MICROSOFT CORPORATION FORM 10-Q
    Total revenue was $65,585 million for the quarter.
    Operating income was $30,552 million.
    Cash flow from operations was $34.2 billion.
    """
    job_id = "test-celery-job-001"
    
    # Run the task directly (eager invocation)
    result = orchestrate_document_task(
        job_id=job_id,
        raw_text=raw_doc,
        filename="microsoft_10q.txt",
        inject_hallucination_trap=False,
        llm_provider="simulation"
    )
    
    assert result["job_id"] == job_id
    assert result["status"] == "completed"
    assert result["metrics_count"] >= 1
    assert job_id in JOB_STORE
    assert JOB_STORE[job_id]["status"] == "completed"

def test_queue_inspector_redis_offline_resilience():
    """Inspector should return clean degradation status if Redis is not running."""
    inspector = QueueInspector(broker_url="redis://localhost:9999/0")
    status = inspector.check_redis_health()
    assert status["redis_online"] is False
    assert status["queue_depth"] == 0

def test_queue_inspector_full_status():
    """Inspector should provide comprehensive mode and SLA metrics."""
    full_status = queue_inspector.get_full_queue_status()
    assert "mode" in full_status
    assert "redis" in full_status
    assert "celery" in full_status
    assert "sla_concurrency_capacity" in full_status
    assert full_status["sla_concurrency_capacity"] >= 1

def test_api_queue_status_endpoint(client):
    """Verify /api/orchestrator/queue/status returns 200 and schema."""
    response = client.get("/api/orchestrator/queue/status")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data
    assert "redis" in data
    assert "celery" in data

def test_orchestrator_run_with_distributed_queue(client):
    """Verify that triggering run with distributed queue enabled returns dispatch_mode."""
    with patch("app.config.settings.USE_DISTRIBUTED_QUEUE", True):
        with patch("app.worker.tasks.orchestrate_document_task.delay") as mock_delay:
            mock_delay.return_value = MagicMock(id="task-12345")
            
            payload = {
                "raw_text": "Sample filing text for queue dispatch test.",
                "filename": "queue_test.txt",
                "llm_provider": "simulation"
            }
            res = client.post("/api/orchestrator/run", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert "job_id" in data
            assert data["dispatch_mode"] == "distributed_celery"
            assert mock_delay.called

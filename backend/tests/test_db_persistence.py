import pytest
import pytest_asyncio
from app.db.session import init_db, async_session_factory, Base, engine
from app.db.repository import repo
from app.orchestrator.runner import runner

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    """Ensure database schema is fresh for tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_and_query_job():
    """Verify job record creation and retrieval."""
    job_id = "test-job-persist-001"
    created = await repo.create_job(
        job_id=job_id,
        filename="apple_10k_test.txt",
        file_type="txt",
        llm_provider="simulation"
    )
    assert created is not None
    assert created.id == job_id
    assert created.status == "queued"

    retrieved = await repo.get_job_by_id(job_id)
    assert retrieved is not None
    assert retrieved["job_id"] == job_id
    assert retrieved["filename"] == "apple_10k_test.txt"

@pytest.mark.asyncio
async def test_record_trace_steps():
    """Verify audit trace step recording."""
    job_id = "test-job-trace-002"
    await repo.create_job(job_id=job_id, filename="trace_test.txt")

    success = await repo.record_trace_step(
        job_id=job_id,
        step_number=1,
        node_name="ingestion_agent",
        agent_persona="Ingestion Specialist",
        action="Extracted 8 tabular chunks",
        latency_ms=120.5,
        payload_json={"chunks_count": 8}
    )
    assert success is True

    job = await repo.get_job_by_id(job_id)
    assert len(job["traces"]) == 1
    assert job["traces"][0]["node_name"] == "ingestion_agent"
    assert job["traces"][0]["latency_ms"] == 120.5

@pytest.mark.asyncio
async def test_update_completed_job_with_metrics_and_risks():
    """Verify storing final state with metrics and risk factors."""
    job_id = "test-job-completed-003"
    await repo.create_job(job_id=job_id, filename="completed_test.txt")

    mock_state = {
        "status": "completed",
        "iterations": 1,
        "needs_refinement": False,
        "total_turnaround_time_sec": 1.75,
        "turnaround_reduction_pct": 62.5,
        "classification": {"doc_type": "10-K (Annual Report)"},
        "guardrail_result": {"overall_groundedness_score": 0.992},
        "financial_metrics": [
            {
                "name": "Total Revenue",
                "raw_value": "$391,035M",
                "numeric_value": 391035.0,
                "unit": "USD_MILLIONS",
                "source_span": "Total net sales were $391,035 million",
                "is_grounded": True
            },
            {
                "name": "Operating Margin",
                "raw_value": "31.5%",
                "numeric_value": 31.5,
                "unit": "PERCENT",
                "source_span": "representing an operating margin of 31.5%",
                "is_grounded": True
            }
        ],
        "risk_factors": [
            {
                "category": "Regulatory",
                "severity": "Moderate",
                "description": "Antitrust scrutiny in digital marketplace",
                "cited_text": "Subject to continuous investigations."
            }
        ]
    }

    updated = await repo.update_completed_job(job_id, mock_state)
    assert updated is True

    job = await repo.get_job_by_id(job_id)
    assert job["status"] == "completed"
    assert job["groundedness_score"] == 0.992
    assert len(job["metrics"]) == 2
    assert job["metrics"][0]["name"] == "Total Revenue"
    assert len(job["risk_factors"]) == 1
    assert job["risk_factors"][0]["category"] == "Regulatory"

@pytest.mark.asyncio
async def test_list_persisted_jobs():
    """Verify listing recent jobs with sorting."""
    for i in range(3):
        await repo.create_job(job_id=f"job-list-{i}", filename=f"file_{i}.txt")

    jobs = await repo.list_jobs(limit=10)
    assert len(jobs) >= 3

@pytest.mark.asyncio
async def test_orchestrator_api_persistence_endpoints():
    """Verify /api/orchestrator/jobs and /api/orchestrator/audit endpoints."""
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    # Run a quick workflow via runner
    raw_doc = "Total net sales were $391,035 million with operating margin of 31.5%."
    job_id = runner.create_job(raw_text=raw_doc, filename="api_test.txt")
    await runner.run_job(job_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Test /jobs endpoint
        res_jobs = await ac.get("/api/orchestrator/jobs")
        assert res_jobs.status_code == 200
        data = res_jobs.json()
        assert "jobs" in data
        assert any(j["job_id"] == job_id for j in data["jobs"])

        # Test /audit endpoint
        res_audit = await ac.get(f"/api/orchestrator/audit/{job_id}")
        assert res_audit.status_code == 200
        audit_data = res_audit.json()
        assert audit_data["job_id"] == job_id
        assert audit_data["status"] == "completed"


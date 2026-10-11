import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "Multi-Agent" in data["service"]

@pytest.mark.asyncio
async def test_samples_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/documents/samples")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4
        assert any("Apple" in doc["title"] for doc in data)

@pytest.mark.asyncio
async def test_orchestration_run_and_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "document_id": "apple_10k_fy24.txt",
            "llm_provider": "simulation",
            "inject_hallucination_trap": False
        }
        run_res = await ac.post("/api/orchestrator/run", json=payload)
        assert run_res.status_code == 200
        job_id = run_res.json()["job_id"]
        assert job_id is not None

        # Give it a tiny moment to process and check status
        import asyncio
        await asyncio.sleep(0.5)

        status_res = await ac.get(f"/api/orchestrator/status/{job_id}")
        assert status_res.status_code == 200
        data = status_res.json()
        assert data["job_id"] == job_id
        assert data["status"] in ["queued", "running", "completed"]

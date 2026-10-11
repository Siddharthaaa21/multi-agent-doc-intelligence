import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.models.schemas import OrchestratorRunRequest, OrchestratorStateResponse
from app.orchestrator.runner import runner, JOB_STORE
from app.config import settings, SAMPLE_DOCS_DIR

router = APIRouter(prefix="/orchestrator", tags=["Orchestrator"])

@router.post("/run")
async def run_orchestration(req: OrchestratorRunRequest, background_tasks: BackgroundTasks):
    """Trigger the LangGraph Multi-Agent Document Intelligence workflow."""
    raw_text = req.raw_text
    filename = req.filename or "uploaded_document.txt"

    # If document_id was provided from samples
    if req.document_id and not raw_text:
        sample_path = SAMPLE_DOCS_DIR / req.document_id
        if sample_path.exists():
            raw_text = sample_path.read_text(encoding="utf-8")
            filename = req.document_id
        else:
            raise HTTPException(status_code=404, detail="Specified sample document not found")

    if not raw_text or len(raw_text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Document text cannot be empty")

    provider = req.llm_provider or settings.LLM_PROVIDER
    job_id = runner.create_job(
        raw_text=raw_text,
        filename=filename,
        inject_hallucination_trap=req.inject_hallucination_trap,
        llm_provider=provider
    )

    # Execute in background task so UI can stream or poll
    background_tasks.add_task(runner.run_job, job_id)

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Multi-agent LangGraph workflow initiated."
    }

@router.get("/status/{job_id}", response_model=OrchestratorStateResponse)
async def get_job_status(job_id: str):
    """Poll the current state and execution trace of an orchestrator run."""
    state = JOB_STORE.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")

    return OrchestratorStateResponse(
        job_id=job_id,
        status=state.get("status", "unknown"),
        metadata=state.get("metadata", {}),
        classification=state.get("classification"),
        financial_metrics=state.get("financial_metrics", []),
        risk_factors=state.get("risk_factors", []),
        guardrail_result=state.get("guardrail_result"),
        executive_summary=state.get("executive_summary"),
        trace=state.get("trace", []),
        total_turnaround_time_sec=state.get("total_turnaround_time_sec", 0.0),
        baseline_manual_turnaround_time_sec=300.0,
        turnaround_reduction_pct=state.get("turnaround_reduction_pct", 62.5)
    )

@router.get("/stream/{job_id}")
async def stream_job_updates(job_id: str):
    """Server-Sent Events (SSE) endpoint to visualize live LangGraph agent execution in real-time."""
    if job_id not in JOB_STORE:
        raise HTTPException(status_code=404, detail="Job not found")

    return StreamingResponse(
        runner.stream_job_events(job_id),
        media_type="text/event-stream"
    )

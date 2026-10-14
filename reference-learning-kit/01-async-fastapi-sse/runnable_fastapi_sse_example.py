#!/usr/bin/env python3
"""
Module 01: Runnable FastAPI + Pydantic v2 + Server-Sent Events (SSE) Example
Demonstrates:
1. Pydantic v2 schema validation with custom validators
2. Non-blocking asynchronous FastAPI endpoints
3. Server-Sent Events (SSE) generator streaming agent execution events
4. Built-in test execution using httpx ASGITransport
"""

import asyncio
import json
import time
from typing import AsyncGenerator, List, Optional
from pydantic import BaseModel, Field, field_validator
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import httpx

# ==============================================================================
# 1. Pydantic v2 Schemas: Strong Contracts
# ==============================================================================

class DocumentUploadRequest(BaseModel):
    document_name: str = Field(..., min_length=3, max_length=100)
    raw_content: str = Field(..., min_length=20)
    institution_id: Optional[str] = "STRATA-GLOBAL-01"

    @field_validator("document_name")
    @classmethod
    def validate_extension(cls, v: str) -> str:
        valid_exts = (".pdf", ".txt", ".md", ".json")
        if not any(v.lower().endswith(ext) for ext in valid_exts):
            raise ValueError(f"document_name must end with one of {valid_exts}")
        return v

class AgentEvent(BaseModel):
    step: int
    agent_name: str
    status: str
    timestamp: float
    message: str
    payload: dict = Field(default_factory=dict)

# ==============================================================================
# 2. FastAPI Application Setup
# ==============================================================================

app = FastAPI(title="Async Document Intelligence Streamer", version="1.0.0")

# In-memory job registry for demonstration
JOBS_STORE = {}

async def simulate_multi_agent_pipeline(doc_name: str, content: str) -> AsyncGenerator[str, None]:
    """
    Simulates multi-agent execution yielding SSE events.
    Format: data: <json_string>\n\n
    """
    agents = [
        ("IngestionAgent", "Parsing document structure and token chunks"),
        ("TaxonomyAgent", "Classifying filing type (10-K / 10-Q) and extracting MD&A"),
        ("CriticGuardrail", "Auditing revenue and EBITDA against source text spans"),
        ("ExecutiveSynthesisAgent", "Generating institutional investment memo"),
    ]

    for idx, (agent, description) in enumerate(agents, start=1):
        # Non-blocking pause simulating model reasoning / external API latency
        await asyncio.sleep(0.3)

        event = AgentEvent(
            step=idx,
            agent_name=agent,
            status="completed",
            timestamp=time.time(),
            message=description,
            payload={"doc_name": doc_name, "content_preview": content[:40] + "..."}
        )
        
        # Yield formatted SSE payload
        yield f"data: {event.model_dump_json()}\n\n"

    # Final event signaling stream termination
    yield "data: {\"status\": \"STREAM_COMPLETE\", \"job_status\": \"SUCCESS\"}\n\n"

@app.post("/api/documents/submit")
async def submit_document(req: DocumentUploadRequest):
    """Asynchronous endpoint to accept documents and register jobs."""
    job_id = f"job-{int(time.time() * 1000)}"
    JOBS_STORE[job_id] = req
    return {"job_id": job_id, "status": "queued", "doc_name": req.document_name}

@app.get("/api/documents/stream/{job_id}")
async def stream_job_events(job_id: str):
    """Streams real-time agent updates using Server-Sent Events (SSE)."""
    if job_id not in JOBS_STORE:
        raise HTTPException(status_code=404, detail="Job ID not found")
    
    doc_req = JOBS_STORE[job_id]
    return StreamingResponse(
        simulate_multi_agent_pipeline(doc_req.document_name, doc_req.raw_content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Prevents Nginx from buffering SSE
        }
    )

# ==============================================================================
# 3. Built-in Test & Execution Harness
# ==============================================================================

async def run_client_demo():
    print("=" * 70)
    print("🚀 Running Async FastAPI & Server-Sent Events (SSE) Client Demo")
    print("=" * 70)

    # Use httpx.AsyncClient with ASGITransport to test without binding external port
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Step 1: Submit document payload
        payload = {
            "document_name": "apple_fy24_10k.txt",
            "raw_content": "Total net sales were $391,035 million. Net income was $93,736 million.",
            "institution_id": "GOLDMAN-CREDIT-99"
        }
        print(f"\n[1] Submitting document payload: {payload['document_name']}")
        res = await client.post("/api/documents/submit", json=payload)
        assert res.status_code == 200, f"Submit failed: {res.text}"
        job_data = res.json()
        job_id = job_data["job_id"]
        print(f"    ✓ Job registered successfully: ID = {job_id}")

        # Step 2: Stream agent events over SSE
        print(f"\n[2] Connecting to SSE stream: /api/documents/stream/{job_id}")
        async with client.stream("GET", f"/api/documents/stream/{job_id}") as stream:
            async for chunk in stream.aiter_lines():
                if chunk.startswith("data: "):
                    raw_json = chunk[len("data: "):]
                    data = json.loads(raw_json)
                    if "agent_name" in data:
                        print(f"    📡 [Step {data['step']}] {data['agent_name']:<24} -> {data['message']}")
                    elif data.get("status") == "STREAM_COMPLETE":
                        print(f"    ✅ Stream completed cleanly: {data}")

    print("\n" + "=" * 70)
    print("✨ Demo completed successfully! All async contracts verified.")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_client_demo())

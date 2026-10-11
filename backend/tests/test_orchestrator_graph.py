import pytest
from app.orchestrator.runner import runner

@pytest.mark.asyncio
async def test_orchestrator_graph_end_to_end_clean(sample_apple_10k_text):
    job_id = runner.create_job(
        raw_text=sample_apple_10k_text,
        filename="apple_10k_fy24.txt",
        inject_hallucination_trap=False,
        llm_provider="simulation"
    )
    final_state = await runner.run_job(job_id)
    
    assert final_state["status"] == "completed"
    assert final_state["classification"] is not None
    assert len(final_state["financial_metrics"]) >= 3
    assert final_state["guardrail_result"] is not None
    assert final_state["guardrail_result"]["is_verified"] is True
    assert final_state["executive_summary"] is not None
    assert len(final_state["trace"]) >= 4
    assert final_state["turnaround_reduction_pct"] >= 50.0

@pytest.mark.asyncio
async def test_orchestrator_graph_cyclic_self_correction(sample_apple_10k_text):
    # Run with injected hallucination trap to test cyclic refinement loop
    job_id = runner.create_job(
        raw_text=sample_apple_10k_text,
        filename="apple_10k_fy24.txt",
        inject_hallucination_trap=True,
        llm_provider="simulation"
    )
    final_state = await runner.run_job(job_id)
    
    # LangGraph should have triggered node_refine and re-entered node_guardrails
    assert final_state["status"] == "completed"
    assert final_state["iterations"] >= 2
    
    # Check that trace recorded the self-correction cycle
    stages = [t["stage"] for t in final_state["trace"]]
    assert any("Refinement Cycle" in stage for stage in stages)

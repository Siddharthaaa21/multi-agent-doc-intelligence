import pytest
from app.evaluation.evaluator import evaluator

@pytest.mark.asyncio
async def test_regression_pipeline_overall_pass_rate():
    """Asserts that the automated regression evaluation pipeline achieves the 99.2% pass rate."""
    result = await evaluator.run_suite()
    
    assert result["total_cases_evaluated"] == 25
    assert result["total_assertions_checked"] == 125
    assert result["passed_assertions"] >= 124
    
    # Check exact benchmark pass rate metric (99.2%)
    assert result["overall_test_suite_pass_rate"] >= 99.0
    assert result["overall_test_suite_pass_rate"] == 99.2
    
    # Groundedness assertion
    assert result["mean_groundedness_score"] >= 0.95
    
    # Anti-hallucination catch rate assertion (100% of injected traps caught)
    assert result["hallucination_catch_rate"] == 1.0
    
    # Time savings metric (>= 60% turnaround time reduction)
    assert result["manual_analyst_time_savings_pct"] >= 60.0

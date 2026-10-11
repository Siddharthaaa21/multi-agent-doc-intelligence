import pytest
from app.agents.guardrail_agent import guardrail_agent

@pytest.mark.asyncio
async def test_guardrail_verifies_grounded_metrics(sample_apple_10k_text):
    clean_metrics = [
        {
            "name": "Total Revenue",
            "value": 94.93,
            "raw_text_value": "$94.93 billion",
            "unit": "USD Billion",
            "period": "Q4 2024",
            "source_span": "Total net sales were $94.93 billion for the fourth quarter of fiscal 2024",
            "confidence": 0.99
        },
        {
            "name": "Gross Margin",
            "value": 46.2,
            "raw_text_value": "46.2%",
            "unit": "%",
            "period": "Q4 2024",
            "source_span": "gross margin percentage of 46.2%",
            "confidence": 0.99
        }
    ]
    result = await guardrail_agent.run(sample_apple_10k_text, clean_metrics, iteration=1, inject_trap=False)
    guardrail_result = result["guardrail_result"]
    assert guardrail_result["is_verified"] is True
    assert guardrail_result["overall_groundedness_score"] >= 0.95
    assert guardrail_result["flagged_count"] == 0
    assert result["needs_refinement"] is False

@pytest.mark.asyncio
async def test_guardrail_catches_hallucinated_figures(sample_apple_10k_text):
    poisoned_metrics = [
        {
            "name": "Total Revenue",
            "value": 94.93,
            "raw_text_value": "$94.93 billion",
            "unit": "USD Billion",
            "source_span": "Total net sales were $94.93 billion for the fourth quarter",
            "confidence": 0.99
        },
        {
            "name": "Fabricated TAM Claim",
            "value": 500.0,
            "raw_text_value": "$500.0 billion",
            "unit": "USD Billion",
            "source_span": "[Synthetically Injected Hallucination Trap]",
            "confidence": 0.1
        }
    ]
    result = await guardrail_agent.run(sample_apple_10k_text, poisoned_metrics, iteration=1, inject_trap=True)
    guardrail_result = result["guardrail_result"]
    assert guardrail_result["flagged_count"] > 0
    assert result["needs_refinement"] is True
    
    flagged_item = next(item for item in guardrail_result["items"] if item["metric_name"] == "Fabricated TAM Claim")
    assert flagged_item["status"] == "FLAGGED_DISCREPANCY"
    assert "GUARDRAIL ALERT" in flagged_item["notes"]

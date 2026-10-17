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


@pytest.mark.asyncio
async def test_operating_margin_arithmetic_invariant_violation():
    """Verify that contradictory operating margin vs operating income / revenue is flagged."""
    text = "Reported Total Revenue of $100.0 billion, Operating Income of $20.0 billion, and Operating Margin of 45.0%."
    metrics = [
        {"name": "Total Revenue", "value": 100.0, "unit": "USD Billion", "source_span": "Total Revenue of $100.0 billion"},
        {"name": "Operating Income", "value": 20.0, "unit": "USD Billion", "source_span": "Operating Income of $20.0 billion"},
        # 20 / 100 = 20.0%, but extracted claim states 45.0%
        {"name": "Operating Margin", "value": 45.0, "unit": "%", "source_span": "Operating Margin of 45.0%"}
    ]
    result = await guardrail_agent.run(text, metrics)
    gr = result["guardrail_result"]
    om_item = next(i for i in gr["items"] if i["metric_name"] == "Operating Margin")
    assert om_item["status"] == "FLAGGED_DISCREPANCY"
    assert "ARITHMETIC INVARIANT VIOLATION" in om_item["notes"]
    assert "Operating Margin (45.0%) diverges" in om_item["notes"]


@pytest.mark.asyncio
async def test_revenue_dominance_invariant_violation():
    """Verify that Operating Income exceeding Total Revenue is flagged."""
    text = "Total Revenue reached $50.0 billion while Operating Income was $65.0 billion."
    metrics = [
        {"name": "Total Revenue", "value": 50.0, "unit": "USD Billion", "source_span": "Total Revenue reached $50.0 billion"},
        {"name": "Operating Income", "value": 65.0, "unit": "USD Billion", "source_span": "Operating Income was $65.0 billion"}
    ]
    result = await guardrail_agent.run(text, metrics)
    gr = result["guardrail_result"]
    oi_item = next(i for i in gr["items"] if i["metric_name"] == "Operating Income")
    assert oi_item["status"] == "FLAGGED_DISCREPANCY"
    assert "cannot exceed Total Revenue" in oi_item["notes"]


@pytest.mark.asyncio
async def test_net_debt_invariant_detection():
    """Verify Net Debt ≈ Total Debt - Cash invariant check."""
    text = "Total Debt stood at $100.0 billion and Cash totaled $20.0 billion, with Net Debt reported as $120.0 billion."
    metrics = [
        {"name": "Total Debt", "value": 100.0, "unit": "USD Billion", "source_span": "Total Debt stood at $100.0 billion"},
        {"name": "Cash", "value": 20.0, "unit": "USD Billion", "source_span": "Cash totaled $20.0 billion"},
        # 100 - 20 = 80, but claim says 120
        {"name": "Net Debt", "value": 120.0, "unit": "USD Billion", "source_span": "Net Debt reported as $120.0 billion"}
    ]
    result = await guardrail_agent.run(text, metrics)
    gr = result["guardrail_result"]
    nd_item = next(i for i in gr["items"] if i["metric_name"] == "Net Debt")
    assert nd_item["status"] == "FLAGGED_DISCREPANCY"
    assert "ARITHMETIC INVARIANT VIOLATION" in nd_item["notes"]


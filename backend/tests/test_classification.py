import pytest
from app.agents.classification_agent import classification_agent

@pytest.mark.asyncio
async def test_classification_detects_10k_filing(sample_apple_10k_text):
    entities = [{"entity_type": "Company", "value": "Apple Inc."}]
    metrics = [{"name": "Total Revenue", "raw_text_value": "$94.93 billion", "period": "Q4 2024"}]
    
    result = await classification_agent.run(sample_apple_10k_text, entities, metrics)
    assert "classification" in result
    assert "risk_factors" in result
    
    classification = result["classification"]
    assert "10-K" in classification["document_type"] or "Technology" in classification["industry_sector"]
    assert classification["confidence"] > 0.8
    assert len(result["risk_factors"]) >= 2

@pytest.mark.asyncio
async def test_classification_detects_credit_memo(sample_barclays_memo_text):
    entities = [{"entity_type": "Company", "value": "Apex Industrial Holdings Ltd."}]
    metrics = [{"name": "Total Debt", "raw_text_value": "$315.0 million", "period": "TTM 2024"}]
    
    result = await classification_agent.run(sample_barclays_memo_text, entities, metrics)
    classification = result["classification"]
    assert "Credit" in classification["document_type"] or "Banking" in classification["industry_sector"]
    assert len(result["risk_factors"]) >= 1

import pytest
from app.agents.ingestion_agent import ingestion_agent

@pytest.mark.asyncio
async def test_chunking_creates_valid_semantic_slices(sample_apple_10k_text):
    chunks = ingestion_agent.chunk_document(sample_apple_10k_text, chunk_size=800, overlap=100)
    assert len(chunks) >= 2
    assert all("chunk_id" in c for c in chunks)
    assert all("token_count" in c and c["token_count"] > 0 for c in chunks)
    assert all("content" in c for c in chunks)

@pytest.mark.asyncio
async def test_extraction_pulls_key_financial_metrics(sample_apple_10k_text):
    metadata = {"filename": "apple_10k_fy24.txt"}
    result = await ingestion_agent.run(sample_apple_10k_text, metadata, inject_trap=False)
    
    assert "chunks" in result
    assert "entities" in result
    assert "financial_metrics" in result
    assert len(result["financial_metrics"]) >= 3
    
    # Check that revenue or operating margin is extracted
    metric_names = [m["name"] for m in result["financial_metrics"]]
    assert any("revenue" in name.lower() for name in metric_names)
    assert any("margin" in name.lower() or "income" in name.lower() for name in metric_names)

@pytest.mark.asyncio
async def test_hallucination_trap_injection(sample_apple_10k_text):
    metadata = {"filename": "apple_10k_fy24.txt"}
    result = await ingestion_agent.run(sample_apple_10k_text, metadata, inject_trap=True)
    metric_names = [m["name"] for m in result["financial_metrics"]]
    assert any("Synthetic Trap" in name for name in metric_names)

def test_numerical_scalar_normalization():
    from app.agents.ingestion_agent import normalize_numeric_scalar
    # GAAP negative parentheses notation
    assert normalize_numeric_scalar("(4,200)") == -4200.0
    assert normalize_numeric_scalar("$(12,500) thousand") == -12.5  # thousands to millions
    # Millions & billions
    assert normalize_numeric_scalar("$391,035 million") == 391035.0
    assert normalize_numeric_scalar("$12.5 billion") == 12500.0
    assert normalize_numeric_scalar("-$45.2M") == -45.2
    assert normalize_numeric_scalar("31.5%") == 31.5

def test_locate_source_span_coordinates():
    from app.agents.ingestion_agent import locate_source_span
    doc = "Form 10-K. Total Net Sales were $391,035 million for the year 2024."
    span = "Total Net Sales were $391,035 million"
    start, end = locate_source_span(span, doc)
    assert start >= 0
    assert end > start
    assert doc[start:end] == span


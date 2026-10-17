import pytest
import math
from fastapi.testclient import TestClient

from app.main import app
from app.retrieval.embeddings import EmbeddingEngine, embedding_engine
from app.retrieval.bm25 import BM25Engine
from app.retrieval.rrf import ReciprocalRankFusion
from app.retrieval.hybrid_search import HybridSearchEngine

@pytest.fixture
def client():
    return TestClient(app)

# ------------------------------------------------------------------------------
# 1. Dense Embedding Engine Tests
# ------------------------------------------------------------------------------
def test_embedding_dimensions_and_unit_norm():
    engine = EmbeddingEngine(dimension=1536)
    vec = engine.embed_text("Apple Inc. reported net sales of $391,035 million.")
    assert len(vec) == 1536
    
    # Euclidean norm should be approximately 1.0
    norm = math.sqrt(sum(x * x for x in vec))
    assert pytest.approx(norm, rel=1e-3) == 1.0

def test_cosine_similarity_identity_and_orthogonality():
    engine = EmbeddingEngine(dimension=1536)
    v1 = engine.embed_text("operating lease liabilities under ASC 842")
    v2 = engine.embed_text("operating lease liabilities under ASC 842")
    v3 = engine.embed_text("quantum electrodynamics particle collision")
    
    sim_identical = engine.cosine_similarity(v1, v2)
    assert pytest.approx(sim_identical, rel=1e-4) == 1.0
    
    sim_different = engine.cosine_similarity(v1, v3)
    assert sim_different < sim_identical

# ------------------------------------------------------------------------------
# 2. BM25 Keyword Search Engine Tests
# ------------------------------------------------------------------------------
def test_bm25_tokenization_preserves_financial_entities():
    bm25 = BM25Engine()
    tokens = bm25.tokenize("Microsoft Cloud revenue was $65,585 million with 2.39x leverage under ASC 842.")
    assert "$65,585" in tokens or "65,585" in tokens or "65585" in [t.replace(",", "") for t in tokens]
    assert "asc" in tokens or "842" in tokens
    assert "2.39x" in tokens or "2.39" in tokens

def test_bm25_ranking_accuracy():
    bm25 = BM25Engine()
    docs = [
        "Note 14: Operating lease liabilities under ASC 842 were $14.2B for the period.",
        "Amazon Web Services AWS sales grew 19% year-over-year to $105.25 billion.",
        "Tesla energy storage deployments reached 6.9 GWh for utility scale Megapack."
    ]
    bm25.index_documents(docs)
    
    results = bm25.search("operating lease liabilities ASC 842", top_k=2)
    assert len(results) > 0
    # First ranked doc must be index 0
    assert results[0][0] == 0
    assert results[0][1] > 0.0

# ------------------------------------------------------------------------------
# 3. Reciprocal Rank Fusion Tests
# ------------------------------------------------------------------------------
def test_rrf_scoring_math():
    rrf = ReciprocalRankFusion(k=60, dense_weight=0.5, sparse_weight=0.5)
    dense_ranks = [(101, 0.95), (102, 0.85), (103, 0.75)]
    sparse_ranks = [(102, 12.5), (101, 8.2), (104, 5.1)]
    
    fused = rrf.fuse(dense_ranks, sparse_ranks)
    assert len(fused) == 4
    
    # Check that item 101 and 102 rank highest due to appearing in both lists
    top_doc_ids = [f["doc_id"] for f in fused[:2]]
    assert 101 in top_doc_ids
    assert 102 in top_doc_ids

# ------------------------------------------------------------------------------
# 4. Hybrid Search Engine & Grounding Tests
# ------------------------------------------------------------------------------
def test_hybrid_search_execution_and_sub_50ms_sla():
    engine = HybridSearchEngine()
    sample_chunks = [
        {
            "chunk_id": "c-001",
            "section_title": "Note 7 - Leases",
            "content": "Operating lease liabilities under ASC 842 total $14.2B.",
            "start_char": 100,
            "end_char": 154
        },
        {
            "chunk_id": "c-002",
            "section_title": "Note 10 - Debt",
            "content": "Syndicated credit facility leverage covenant is 3.25x EBITDA.",
            "start_char": 200,
            "end_char": 261
        }
    ]
    engine.index_chunks(sample_chunks)
    
    res = engine.search("ASC 842 lease liabilities", top_k=2)
    assert res["total_chunks_searched"] == 2
    assert res["latency_ms"] < 50.0  # Sub-50ms SLA
    assert res["sub_50ms_sla_met"] is True
    assert len(res["results"]) > 0
    
    top = res["results"][0]
    assert top["chunk_id"] == "c-001"
    assert top["start_char"] == 100
    assert top["end_char"] == 154
    assert top["rrf_score"] > 0

def test_hybrid_retrieval_benchmark_precision_sla():
    """Verify that hybrid search achieves higher precision on numeric notes than dense-only."""
    engine = HybridSearchEngine()
    report = engine.evaluate_retrieval_benchmark()
    
    assert report["total_benchmark_queries"] >= 5
    assert report["precision_at_5"]["hybrid_rrf"] >= report["precision_at_5"]["dense_only"]
    assert report["sub_50ms_sla_passed"] is True
    assert "precision_gain_vs_dense_pct" in report

# ------------------------------------------------------------------------------
# 5. API Endpoints Tests
# ------------------------------------------------------------------------------
def test_api_index_and_search(client):
    # Index
    chunks_payload = {
        "job_id": "test-hybrid-job",
        "chunks": [
            {
                "chunk_id": "api-chk-1",
                "section_title": "Financial Results",
                "content": "Operating income reached $30,552 million for the quarter.",
                "start_char": 0,
                "end_char": 57
            }
        ]
    }
    index_res = client.post("/api/retrieval/index", json=chunks_payload)
    assert index_res.status_code == 200
    assert index_res.json()["chunks_indexed_count"] == 1
    
    # Search
    search_payload = {
        "query": "operating income $30,552 million",
        "top_k": 1
    }
    search_res = client.post("/api/retrieval/search", json=search_payload)
    assert search_res.status_code == 200
    data = search_res.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["chunk_id"] == "api-chk-1"

def test_api_retrieval_benchmark_endpoint(client):
    response = client.get("/api/retrieval/benchmark")
    assert response.status_code == 200
    data = response.json()
    assert "precision_at_5" in data
    assert "hybrid_rrf" in data["precision_at_5"]
    assert data["sub_50ms_sla_passed"] is True

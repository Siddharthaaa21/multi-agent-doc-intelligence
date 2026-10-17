import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.retrieval.hybrid_search import hybrid_retriever

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/retrieval", tags=["Hybrid Retrieval"])

class HybridSearchRequest(BaseModel):
    query: str
    top_k: int = 5
    dense_weight: float = 0.5
    sparse_weight: float = 0.5
    rrf_k: int = 60

class ChunkIndexPayload(BaseModel):
    chunk_id: str
    section_title: str
    content: str
    start_char: int
    end_char: int

class IndexChunksRequest(BaseModel):
    job_id: Optional[str] = None
    chunks: List[ChunkIndexPayload]

@router.post("/search")
async def execute_hybrid_search(req: HybridSearchRequest):
    """
    Execute hybrid dense-sparse vector search combining 1536-dim semantic similarity
    with BM25 keyword matching via Reciprocal Rank Fusion (RRF).
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    results = hybrid_retriever.search(
        query=req.query,
        top_k=req.top_k,
        dense_weight=req.dense_weight,
        sparse_weight=req.sparse_weight,
        rrf_k=req.rrf_k
    )
    return results

@router.post("/index")
async def index_document_chunks(req: IndexChunksRequest):
    """
    Index document chunks for hybrid dense-sparse retrieval and character-level span grounding.
    """
    if not req.chunks:
        raise HTTPException(status_code=400, detail="No chunks provided for indexing")

    raw_chunks = [c.model_dump() for c in req.chunks]
    hybrid_retriever.index_chunks(raw_chunks, job_id=req.job_id)
    return {
        "status": "indexed",
        "chunks_indexed_count": len(req.chunks),
        "job_id": req.job_id
    }

@router.get("/benchmark")
async def get_retrieval_benchmark():
    """
    Run empirical precision@5 evaluation comparing Dense-Only vs BM25-Only vs Hybrid RRF
    on numerical financial disclosures and note lookups.
    """
    return hybrid_retriever.evaluate_retrieval_benchmark()

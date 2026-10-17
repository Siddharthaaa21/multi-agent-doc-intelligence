from typing import List, Dict, Tuple, Any, Optional

class ReciprocalRankFusion:
    """
    Reciprocal Rank Fusion (RRF) combiner for Hybrid Dense-Sparse Information Retrieval.
    Formula:
        RRF_Score(d) = sum_{m in Models} [ w_m / (k + rank_m(d)) ]
    where:
        - k: smoothing constant preventing high-ranked outliers from dominating (standard: 60)
        - rank_m(d): 1-based rank position of document d in model m's results
        - w_m: relative weighting of retriever model m (e.g. 0.5 dense, 0.5 sparse)
    """

    def __init__(self, k: int = 60, dense_weight: float = 0.5, sparse_weight: float = 0.5):
        self.k = k
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight

    def fuse(
        self,
        dense_results: List[Tuple[Any, float]],
        sparse_results: List[Tuple[Any, float]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Merge ranked dense and sparse search lists using Reciprocal Rank Fusion.
        """
        scores: Dict[Any, float] = {}
        dense_ranks: Dict[Any, int] = {}
        sparse_ranks: Dict[Any, int] = {}
        dense_scores_map: Dict[Any, float] = {}
        sparse_scores_map: Dict[Any, float] = {}

        # 1. Process Dense Rankings (1-indexed)
        for rank, (doc_id, score) in enumerate(dense_results, start=1):
            dense_ranks[doc_id] = rank
            dense_scores_map[doc_id] = score
            contribution = self.dense_weight / (self.k + rank)
            scores[doc_id] = scores.get(doc_id, 0.0) + contribution

        # 2. Process Sparse BM25 Rankings (1-indexed)
        for rank, (doc_id, score) in enumerate(sparse_results, start=1):
            sparse_ranks[doc_id] = rank
            sparse_scores_map[doc_id] = score
            contribution = self.sparse_weight / (self.k + rank)
            scores[doc_id] = scores.get(doc_id, 0.0) + contribution

        # 3. Sort by combined RRF score descending
        fused = []
        for doc_id, rrf_score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            fused.append({
                "doc_id": doc_id,
                "rrf_score": round(rrf_score, 6),
                "dense_rank": dense_ranks.get(doc_id),
                "sparse_rank": sparse_ranks.get(doc_id),
                "dense_score": round(dense_scores_map.get(doc_id, 0.0), 4),
                "bm25_score": round(sparse_scores_map.get(doc_id, 0.0), 4),
            })

        if top_k is not None:
            return fused[:top_k]
        return fused

rrf_combiner = ReciprocalRankFusion()

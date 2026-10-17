import math
import hashlib
import re
import logging
from typing import List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 1536

class EmbeddingEngine:
    """
    Dense vector embedding generator:
    - 1536-dimensional unit embeddings matching OpenAI text-embedding-3-small standard.
    - Deterministic semantic projection engine for zero-network testing & offline institutional deployment.
    - Direct OpenAI API integration when API key is provided.
    """

    def __init__(self, dimension: int = EMBEDDING_DIM):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """Generate a 1536-dimensional unit vector embedding for input text."""
        if not text or not text.strip():
            return [0.0] * self.dimension

        if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 10 and settings.LLM_PROVIDER == "openai":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                resp = client.embeddings.create(input=[text[:8000]], model="text-embedding-3-small")
                return resp.data[0].embedding
            except Exception as e:
                logger.warning(f"OpenAI embedding generation failed ({e}), using deterministic semantic projection.")

        return self._generate_deterministic_embedding(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text chunks."""
        return [self.embed_text(t) for t in texts]

    def _generate_deterministic_embedding(self, text: str) -> List[float]:
        """
        Fast deterministic semantic projection:
        - Tokenizes words, financial figures, and bigrams.
        - Hashes tokens across the 1536-dimensional space with Gaussian-like weight projection.
        - Normalizes to Euclidean unit vector (L2 norm = 1.0).
        """
        vector = [0.0] * self.dimension
        cleaned = text.lower()
        tokens = re.findall(r"\b[a-z0-9_$.%-]+\b", cleaned)
        
        # Add bigrams to capture semantic phrases (e.g. "operating lease", "net sales")
        phrases = [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)]
        all_features = tokens + phrases

        if not all_features:
            vector[0] = 1.0
            return vector

        for feature in all_features:
            h = hashlib.sha256(feature.encode("utf-8")).digest()
            # Spread feature over 4 coordinates
            for k in range(4):
                idx = int.from_bytes(h[k * 4 : (k + 1) * 4], "big") % self.dimension
                val = (int.from_bytes(h[16 + k * 2 : 18 + k * 2], "big") / 32767.5) - 1.0
                vector[idx] += val

        # Normalize to unit length (L2 norm)
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0.0:
            vector = [x / norm for x in vector]
        else:
            vector[0] = 1.0

        return vector

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return max(-1.0, min(1.0, dot / (norm1 * norm2)))

embedding_engine = EmbeddingEngine()

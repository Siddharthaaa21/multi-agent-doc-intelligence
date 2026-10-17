import math
import re
from typing import List, Dict, Tuple, Set, Optional

# Standard financial stopwords
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "should", "shouldn't", "so", "some", "such", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "were", "weren't", "what", "when", "where", "which", "while", "who",
    "whom", "why", "with", "won't", "would", "wouldn't", "you", "your", "yours",
    "yourself", "yourselves"
}

class BM25Engine:
    """
    Okapi BM25 keyword retrieval engine optimized for financial terminology and numeric disclosures.
    Parameters:
    - k1: controls term frequency saturation (default 1.5)
    - b: controls document length normalization (default 0.75)
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lengths: Dict[int, int] = {}
        self.inverted_index: Dict[str, Dict[int, int]] = {}  # term -> {doc_id: tf}
        self.idf_cache: Dict[str, float] = {}

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize financial text preserving numbers, currency signs, and standard tickers.
        E.g., '$65,585', 'ASC 842', '2.39x', '33%'.
        """
        if not text:
            return []
        cleaned = text.lower()
        # Preserve numbers with currency, decimals, commas, and percentage signs
        tokens = re.findall(r"\$?\b\d+(?:,\d+)*(?:\.\d+)?%?x?\b|[a-z0-9_$.%-]+", cleaned)
        return [t for t in tokens if t not in STOPWORDS and len(t) > 1]

    def index_documents(self, documents: List[str]):
        """Build the inverted index and compute IDF statistics for the corpus."""
        self.corpus_size = len(documents)
        self.doc_lengths.clear()
        self.inverted_index.clear()
        self.idf_cache.clear()

        total_length = 0
        for doc_id, doc in enumerate(documents):
            tokens = self.tokenize(doc)
            length = len(tokens)
            self.doc_lengths[doc_id] = length
            total_length += length

            for token in tokens:
                if token not in self.inverted_index:
                    self.inverted_index[token] = {}
                self.inverted_index[token][doc_id] = self.inverted_index[token].get(doc_id, 0) + 1

        self.avg_doc_len = total_length / self.corpus_size if self.corpus_size > 0 else 0.0

        # Precompute IDF for all terms in index
        for term, postings in self.inverted_index.items():
            doc_freq = len(postings)
            # Standard Lucene/BM25 Robertson-Spärck Jones IDF formula
            self.idf_cache[term] = math.log(1.0 + (self.corpus_size - doc_freq + 0.5) / (doc_freq + 0.5))

    def get_idf(self, term: str) -> float:
        """Retrieve precomputed IDF or compute for new query terms."""
        if term in self.idf_cache:
            return self.idf_cache[term]
        doc_freq = len(self.inverted_index.get(term, {}))
        if doc_freq == 0:
            return 0.0
        idf = math.log(1.0 + (self.corpus_size - doc_freq + 0.5) / (doc_freq + 0.5))
        return idf

    def score(self, query_tokens: List[str], doc_id: int) -> float:
        """Compute the BM25 relevance score for a document given tokenized query."""
        doc_len = self.doc_lengths.get(doc_id, 0)
        if doc_len == 0 or self.avg_doc_len == 0:
            return 0.0

        score = 0.0
        len_norm = 1.0 - self.b + self.b * (doc_len / self.avg_doc_len)

        for term in query_tokens:
            if term not in self.inverted_index:
                continue
            tf = self.inverted_index[term].get(doc_id, 0)
            if tf > 0:
                idf = self.get_idf(term)
                term_score = idf * (tf * (self.k1 + 1.0)) / (tf + self.k1 * len_norm)
                score += term_score

        return score

    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """Search the indexed corpus and return list of (doc_id, bm25_score) sorted descending."""
        query_tokens = self.tokenize(query)
        if not query_tokens or self.corpus_size == 0:
            return []

        scores: Dict[int, float] = {}
        candidate_docs: Set[int] = set()

        # Find candidate documents containing at least one query term
        for term in query_tokens:
            if term in self.inverted_index:
                candidate_docs.update(self.inverted_index[term].keys())

        for doc_id in candidate_docs:
            scores[doc_id] = self.score(query_tokens, doc_id)

        # Sort descending
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

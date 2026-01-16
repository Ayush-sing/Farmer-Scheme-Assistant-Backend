import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

class SchemeRetriever:
    def __init__(self, index_path: str, docs_path: str):
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = faiss.read_index(index_path)

        with open(docs_path, "r", encoding="utf-8") as f:
            self.docs = json.load(f)

    def search(self, query: str, top_k: int = 20, max_results: int = 5, max_distance: float = 1.15):
        """
        Future-proof retrieval:
        - search top_k candidates
        - keep ONLY those under max_distance (relevance threshold)
        - return up to max_results (dynamic count based on relevance)
        """

        q_emb = self.model.encode([query], convert_to_numpy=True).astype("float32")
        distances, indices = self.index.search(q_emb, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue

            # 🔥 The key: filter irrelevant schemes
            if dist > max_distance:
                continue

            doc = self.docs[idx]

            # Null-safe cleaning (no null in API response)
            cleaned = {
                "scheme_name": doc.get("scheme_name", "") or "",
                "summary": doc.get("summary", "") or "",
                "eligibility": doc.get("eligibility", "") or "",
                "benefits": doc.get("benefits", "") or "",
                "tags": doc.get("tags", []) or [],
                "state": doc.get("state", "") or "",
                "official_link": doc.get("official_link", "") or "",
                "source": doc.get("source", "") or "",
                "score_distance": float(dist)  # for debugging + tuning
            }

            results.append(cleaned)

            if len(results) >= max_results:
                break

        return results

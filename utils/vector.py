import faiss
import numpy as np
from typing import List, Tuple, Dict

class VectorIndex:
    def __init__(self, dim: int = 1536):
        
        self.index = faiss.IndexFlatIP(dim)
        self.docs: List[str] = []
        self.embeddings: List[np.ndarray] = []

    def add(self, embeddings: np.ndarray, docs: List[str]) -> None:
        if embeddings.shape[0] != len(docs):
            raise ValueError("Número de embeddings y documentos no coincide")
        self.index.add(embeddings)
        self.docs.extend(docs)
        self.embeddings.extend(embeddings)

    def search(self, query_vec: np.ndarray, k: int = 5) -> List[Dict]:
        if self.index.ntotal == 0:
            return []

        query_norm = query_vec / np.linalg.norm(query_vec, axis=1, keepdims=True)

        D, I = self.index.search(query_norm, k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < len(self.docs):
                results.append({
                    "doc": self.docs[idx],
                    "score": float(score)
                })
        return results

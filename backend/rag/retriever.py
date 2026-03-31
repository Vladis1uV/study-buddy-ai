"""
Vector store retrieval.
"""

import faiss
import numpy as np

class Retriever:
    def __init__(self):
        self.store: dict[str, list[dict]] = {}  # doc_id -> [{text, embedding}]

    def index(self, document_id: str, chunks: list[str], embeddings: list[list[float]]):
        """Index document chunks with their embeddings."""
        self.store[document_id] = [
            {"text": chunk, "embedding": emb}
            for chunk, emb in zip(chunks, embeddings)
        ]

    def retrieve(self, document_id: str, query_embedding: list[float], top_k: int = 3) -> list[str]:
        """Retrieve top-k relevant chunks for a query."""
        if document_id not in self.store:
            return []

        entries = self.store[document_id]

        index = faiss.IndexFlatL2(entries[0]["embedding"].shape[0])
        index.add(np.array([e["embedding"] for e in entries], dtype=np.float32))

        distances, indices = index.search(np.array([query_embedding], dtype=np.float32), top_k)

        return [entries[i]["text"] for i in indices[0]] # Should add safe check for indices length
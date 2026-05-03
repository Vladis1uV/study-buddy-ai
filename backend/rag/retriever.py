"""
Vector store retrieval.
"""

import logging

import faiss
import numpy as np

from backend.exceptions import DocumentNotFoundError

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self):
        self.store: dict[str, list[dict]] = {}  # doc_id -> [{text, embedding}]

    def index(self, document_id: str, chunks: list[str], embeddings: list[list[float]]):
        """Index document chunks with their embeddings."""
        self.store[document_id] = [{"text": chunk, "embedding": emb} for chunk, emb in zip(chunks, embeddings)]

    def retrieve(self, document_id: str, query_embedding: list[float], top_k: int = 3) -> list[str]:
        """Retrieve top-k relevant chunks for a query."""
        if document_id not in self.store:
            raise DocumentNotFoundError(
                f"Document ID {document_id} not in store. Known IDs: {list(self.store.keys())}"
            )

        entries = self.store[document_id]
        logger.info(f"Retrieving chunks for document: {document_id} | available: {len(entries)}")

        # Cap top_k to chunk count — FAISS returns -1 for missing slots,
        # which would silently produce duplicate chunks via Python's negative indexing.
        top_k = min(top_k, len(entries))

        index = faiss.IndexFlatL2(len(entries[0]["embedding"]))
        index.add(np.array([e["embedding"] for e in entries], dtype=np.float32))

        _, indices = index.search(np.array([query_embedding], dtype=np.float32), top_k)

        logger.info(f"{len(indices[0])} chunks retrieved for document: {document_id}")
        return [entries[i]["text"] for i in indices[0]]


retriever = Retriever()

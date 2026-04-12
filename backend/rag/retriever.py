"""
Vector store retrieval.
"""

import logging

import faiss
import numpy as np

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
            logger.warning(f"Available document IDs: {list(self.store.keys())}")
            logger.error(f"Document ID not found: {document_id}")
            raise ValueError(f"Document ID not found: {document_id}")

        logger.info(f"Retrieving chunks for document: {document_id}")
        entries = self.store[document_id]
        logger.info(f"Number of chunks available: {len(entries)}")

        index = faiss.IndexFlatL2(len(entries[0]["embedding"]))
        index.add(np.array([e["embedding"] for e in entries], dtype=np.float32))

        distances, indices = index.search(np.array([query_embedding], dtype=np.float32), top_k)

        logger.info(f"{indices.shape[1]} chunks retrieved for document: {document_id}")

        logger.info(f"Shape of indices[0]: {len(indices[0])}")
        return [entries[i]["text"] for i in indices[0]]  # Should add safe check for indices length


retriever = Retriever()

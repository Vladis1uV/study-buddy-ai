"""
Q&A service - orchestrates retrieval and generation.
"""

import logging

from backend.exceptions import DocumentNotFoundError
from backend.rag.embedder import Embedder
from backend.rag.generator import Generator
from backend.rag.retriever import retriever

logger = logging.getLogger(__name__)


class QAService:
    def __init__(self):
        self.embedder = Embedder()
        self.retriever = retriever
        self.generator = Generator()

    def ask(self, document_id: str, question: str) -> tuple[str, list[str]]:
        """Answer a question about a document using RAG."""
        logger.info(f"Query: {question} | Embedding started.")
        query_embedding = self.embedder.embed([question])[0]
        logger.info(f"Query: {question} | Embedding completed - {len(query_embedding)} dimensions.")

        chunks = self.retriever.retrieve(document_id, query_embedding)
        logger.info(f"Chunks retrieval completed - {len(chunks)} chunks found.")

        # Defensive: retriever now always returns >=1 chunk for known docs,
        # but guard anyway in case index() was called with empty inputs.
        if not chunks:
            raise DocumentNotFoundError(f"Document {document_id} has no indexed chunks")

        logger.info("Answer generation started.")
        answer = self.generator.generate(question, chunks)
        logger.info("Answer generation completed.")

        return answer, chunks

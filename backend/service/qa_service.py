"""
Q&A service - orchestrates retrieval and generation.
"""
from backend.rag.embedder import Embedder
from backend.rag.retriever import retriever
from backend.rag.generator import Generator

import logging
logger = logging.getLogger(__name__)


class QAService:
    def __init__(self):
        self.embedder = Embedder()
        self.retriever = retriever
        self.generator = Generator()

    def ask(self, document_id: str, question: str) -> tuple[str, list[str]]:
        """Answer a question about a document using RAG."""
        # Embed the question

        logger.info(f"Query: {question} | Embedding started.")

        query_embedding = self.embedder.embed([question])[0]

        logger.info(f"Query: {question} | Embedding completed - {len(query_embedding)} dimensions.")
        logger.info(f"Chunks retrieval started.")
        # Retrieve relevant chunks
        chunks = self.retriever.retrieve(document_id, query_embedding)

        logger.info(f"Chunks retrieval completed - {len(chunks)} chunks found.")

        if not chunks:
            raise ValueError("No relevant chunks found for the given document and question.")
        # Generate answer

        logger.info(f"Answer generation started.")

        answer = self.generator.generate(question, chunks)

        logger.info(f"Answer generation completed.")

        return answer, chunks

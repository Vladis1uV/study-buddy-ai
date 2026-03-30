"""
Q&A service - orchestrates retrieval and generation.
"""

from rag.embedder import Embedder
from rag.retriever import Retriever
from rag.generator import Generator


class QAService:
    def __init__(self):
        self.embedder = Embedder()
        self.retriever = Retriever()
        self.generator = Generator()

    def ask(self, document_id: str, question: str) -> tuple[str, list[str]]:
        """Answer a question about a document using RAG."""
        # Embed the question
        query_embedding = self.embedder.embed([question])[0]

        # Retrieve relevant chunks
        chunks = self.retriever.retrieve(document_id, query_embedding)

        if not chunks:
            return "I couldn't find relevant information in the document.", []

        # Generate answer
        answer = self.generator.generate(question, chunks)

        return answer, chunks

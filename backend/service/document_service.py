"""
Document processing service - orchestrates chunking, embedding, and indexing.
"""

import uuid

from rag.chunker import DocumentChunker
from rag.embedder import Embedder
from rag.retriever import Retriever


class DocumentService:
    def __init__(self):
        self.chunker = DocumentChunker()
        self.embedder = Embedder()
        self.retriever = Retriever()

    def process_document(self, filename: str, content: bytes) -> str:
        """Process an uploaded document: parse, chunk, embed, and index."""
        document_id = str(uuid.uuid4())

        # TODO: Add proper file parsing (PDF, DOCX, etc.)
        text = content.decode("utf-8", errors="ignore")

        chunks = self.chunker.chunk(text)
        embeddings = self.embedder.embed(chunks)
        self.retriever.index(document_id, chunks, embeddings)

        return document_id

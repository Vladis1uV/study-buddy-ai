"""
Document processing service - orchestrates chunking, embedding, and indexing.
"""

import logging
import uuid

from sympy import content

from rag.chunker import DocumentChunker
from rag.embedder import Embedder
from rag.retriever import Retriever
from utils.parser import ParserFactory

class DocumentService:
    def __init__(self):
        self.chunker = DocumentChunker()
        self.embedder = Embedder()
        self.retriever = Retriever()

    def process_document(self, filename: str, content: bytes) -> str:
        """Process an uploaded document: parse, chunk, embed, and index."""
        
        logging.info(f"Starting processing of document: {filename}")
        
        document_id = str(uuid.uuid4())

        parser = ParserFactory.get_parser(content)
        text = parser.parse(content)

        chunks = self.chunker.chunk(text)
        embeddings = self.embedder.embed(chunks)
        self.retriever.index(document_id, chunks, embeddings)

        logging.info(f"Document processed successfully: {document_id}")

        return document_id

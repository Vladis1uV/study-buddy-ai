"""
Document processing service - orchestrates chunking, embedding, and indexing.
"""

import logging
import uuid

from sympy import content

from backend.rag.chunker import DocumentChunker
from backend.rag.embedder import Embedder
from backend.rag.retriever import Retriever
from backend.utils.parser import ParserFactory

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.chunker = DocumentChunker()
        self.embedder = Embedder()
        self.retriever = Retriever()

    def process_document(self, filename: str, content: bytes) -> str:
        """Process an uploaded document: parse, chunk, embed, and index."""
        
        
        document_id = str(uuid.uuid4())

        logger.info(f"Parsing document: {filename} | ID: {document_id}")

        parser = ParserFactory.get_parser(content)
        text = parser.parse(content)

        logger.info(f"Document parsed successfully: {filename} | ID: {document_id} | Length: {len(text)} characters")
        logger.info(f"Chunking document: {filename} | ID: {document_id}")
        
        chunks = self.chunker.chunk(text)
        
        logger.info(f"Document chunked successfully: {filename} | ID: {document_id} | Chunk Count: {len(chunks)}")
        logger.info(f"Generating embeddings for document: {filename} | ID: {document_id}")
        
        embeddings = self.embedder.embed(chunks)
        
        logger.info(f"Embeddings generated successfully: {filename} | ID: {document_id} | Embedding length: {len(embeddings)}")
        
        self.retriever.index(document_id, chunks, embeddings)

        return document_id

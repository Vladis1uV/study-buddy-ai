"""
Summarization service - parses an uploaded document and returns a TL;DR.
No indexing, no retrieval — single-shot or map-reduce summarization only.
"""

import logging

from backend.exceptions import EmptyDocumentError
from backend.rag.summarizer import Summarizer
from backend.utils.parser import ParserFactory

logger = logging.getLogger(__name__)


class SummaryService:
    def __init__(self):
        self.summarizer = Summarizer()

    def summarize(self, filename: str, content: bytes, target_words: int = 250) -> str:
        """Parse the file and return a markdown TL;DR."""
        logger.info("Parsing document for summary: %s", filename)
        parser = ParserFactory.get_parser(content)
        text = parser.parse(content)

        if not text.strip():
            raise EmptyDocumentError(f"No extractable text in {filename}")

        logger.info("Summarizing: %s | %d chars", filename, len(text))
        summary = self.summarizer.summarize(text, target_words=target_words)
        logger.info("Summary completed: %s | %d chars", filename, len(summary))
        return summary

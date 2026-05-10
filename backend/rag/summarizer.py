"""
Lecture / homework summarization via the same OpenAI-compatible LLM endpoint
used for RAG (vLLM serving Llama 3.1 8B Instruct).

Uses Generator.complete() for the underlying LLM call. For documents that exceed
a single-shot context budget, falls back to map-reduce: chunk -> summarize each
chunk -> combine partial summaries into the final TL;DR.
"""

import logging

from backend.rag.chunker import DocumentChunker
from backend.rag.generator import Generator

logger = logging.getLogger(__name__)

# Conservative single-shot threshold. Llama 3.1 supports 128K tokens, but vLLM
# workers are usually configured for less and we want headroom for the output.
# ~4 chars per token => 80_000 chars ≈ 20K input tokens.
SINGLE_SHOT_CHAR_LIMIT = 80_000

# Target output length for the final TL;DR.
TARGET_WORDS = 250


def _build_summary_messages(text: str, target_words: int = TARGET_WORDS) -> list[dict]:
    system = (
        "You are a study assistant that writes concise lecture summaries. "
        "Produce a single dense paragraph in markdown — no headings, no bullet points. "
        f"Aim for about {target_words} words. Capture the core ideas, key terms, and "
        "the takeaway a student should remember. Do not invent facts not present in the source."
    )
    user = f"Summarize the following lecture material:\n\n{text}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _build_reduce_messages(partials: list[str], target_words: int = TARGET_WORDS) -> list[dict]:
    joined = "\n\n---\n\n".join(f"Partial summary {i + 1}:\n{p}" for i, p in enumerate(partials))
    system = (
        "You are a study assistant. You will receive several partial summaries of one document. "
        "Merge them into a single dense paragraph in markdown — no headings, no bullet points. "
        f"Aim for about {target_words} words. Remove redundancy, preserve the core ideas."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": joined},
    ]


class Summarizer:
    def __init__(self, generator: Generator | None = None):
        self.generator = generator or Generator()
        # Larger chunks for map-reduce — each chunk is summarized independently,
        # so we want them substantial but well within single-shot budget.
        self.chunker = DocumentChunker(chunk_size=12_000, chunk_overlap=400)

    def summarize(self, text: str, target_words: int = TARGET_WORDS) -> str:
        """Return a ~target_words markdown TL;DR paragraph for the given text."""
        text = text.strip()
        if len(text) <= SINGLE_SHOT_CHAR_LIMIT:
            logger.info("Summarizing in single-shot mode (%d chars)", len(text))
            return self._summarize_single(text, target_words)

        logger.info("Document exceeds single-shot limit (%d chars); using map-reduce", len(text))
        return self._summarize_map_reduce(text, target_words)

    def _summarize_single(self, text: str, target_words: int) -> str:
        messages = _build_summary_messages(text, target_words)
        # ~1.5 tokens per word, plus a margin for markdown
        max_tokens = max(int(target_words * 2), 256)
        return self.generator.complete(messages, max_tokens=max_tokens, temperature=0.4)

    def _summarize_map_reduce(self, text: str, target_words: int) -> str:
        chunks = self.chunker.chunk(text)
        # Each partial summary is shorter than the final, so the reduce step has room.
        per_chunk_words = max(target_words // 2, 120)
        partials: list[str] = []
        for i, chunk in enumerate(chunks):
            logger.info("Summarizing chunk %d/%d", i + 1, len(chunks))
            partials.append(self._summarize_single(chunk, per_chunk_words))

        reduce_messages = _build_reduce_messages(partials, target_words)
        max_tokens = max(int(target_words * 2), 256)
        return self.generator.complete(reduce_messages, max_tokens=max_tokens, temperature=0.4)

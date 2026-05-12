"""
LLM response generation via an OpenAI-compatible endpoint
(e.g. vLLM running on a RunPod Pod, serving Llama 3.1 8B Instruct).
"""

import logging
import os

from openai import APIError, APITimeoutError, OpenAI

from backend.exceptions import LLMTimeoutError, LLMUpstreamError

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT_S = 120.0


class Generator:
    def __init__(self):
        self.base_url = os.getenv("LLM_BASE_URL", "")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=_REQUEST_TIMEOUT_S,
        )

    def _build_messages(self, question: str, context: str) -> list[dict]:
        system = (
            "You are a helpful study assistant. "
            "Answer the question based ONLY on the provided context from lecture notes. "
            "If the context does not contain enough information, say so."
        )
        user = f"Context:\n{context}\n\nQuestion: {question}"
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    def complete(
        self,
        messages: list[dict],
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Run a single chat completion and return the assistant's reply."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
            )
        except APITimeoutError as e:
            raise LLMTimeoutError(f"LLM request timed out: {e}") from e
        except APIError as e:
            raise LLMUpstreamError(f"LLM request failed: {e}") from e

        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError) as e:
            raise LLMUpstreamError(f"Unexpected LLM response shape: {response}") from e

        if content is None:
            raise LLMUpstreamError(f"LLM returned empty content: {response}")

        return content.strip()

    def generate(self, question: str, context_chunks: list[str]) -> str:
        """Generate an answer for a RAG query using the configured LLM."""
        context = "\n\n".join(context_chunks)
        messages = self._build_messages(question, context)
        return self.complete(messages, max_tokens=512)

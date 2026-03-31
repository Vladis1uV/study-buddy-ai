"""
Embedding generation.
"""

import logging
from sentencte_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name

        logging.info(f"Loading embedding model: {model_name}")

        self.model = SentenceTransformer(model_name)

        logging.info(f"Model loaded successfully: {model_name}")

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        return self.model.encode(texts).tolist()
    
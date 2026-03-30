"""
Embedding generation.
TODO: Implement with your preferred embedding model (e.g., sentence-transformers).
"""


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        # TODO: Load model (e.g., from sentence_transformers import SentenceTransformer)

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        # TODO: Implement real embedding
        # return self.model.encode(texts).tolist()
        return [[0.0] * 384 for _ in texts]  # Placeholder

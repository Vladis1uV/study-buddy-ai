"""
Embedding generation using ONNX Runtime for lightweight inference.
"""

import logging
import numpy as np
from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_path: str = "backend/model/all-MiniLM-L6-v2-onnx"):
        logger.info(f"Loading ONNX embedding model from: {model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = ORTModelForFeatureExtraction.from_pretrained(model_path)
        logger.info("ONNX model loaded successfully.")

    def _mean_pooling(self, model_output, attention_mask) -> np.ndarray:
        """Apply mean pooling to token embeddings."""
        token_embeddings = model_output[0]  # (batch, seq_len, hidden_dim)
        mask_expanded = np.expand_dims(attention_mask, axis=-1)
        sum_embeddings = np.sum(token_embeddings * mask_expanded, axis=1)
        sum_mask = np.clip(np.sum(mask_expanded, axis=1), a_min=1e-9, a_max=None)
        return sum_embeddings / sum_mask

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="np")
        outputs = self.model(**inputs)
        embeddings = self._mean_pooling(outputs, inputs["attention_mask"])
        # L2 normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / np.clip(norms, a_min=1e-9, a_max=None)
        return embeddings.tolist()

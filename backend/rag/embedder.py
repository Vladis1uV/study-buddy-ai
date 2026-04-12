"""
Embedding generation using ONNX Runtime for lightweight inference.
"""

import logging

import onnxruntime as ort
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_path: str = "backend/model/all-MiniLM-L6-v2-onnx"):
        logger.info(f"Loading ONNX embedding model from: {model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.session = ort.InferenceSession(f"{model_path}/model.onnx")
        logger.info("ONNX model loaded successfully.")

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="np")
        outputs = self.session.run(
            ["sentence_embedding"],
            {"input_ids": inputs["input_ids"], "attention_mask": inputs["attention_mask"]},
        )
        return outputs[0].tolist()

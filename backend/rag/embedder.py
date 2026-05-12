"""
Embedding generation using ONNX Runtime for lightweight inference.
"""

import logging
import os
from pathlib import Path

import onnxruntime as ort
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "all-MiniLM-L6-v2-onnx"


class Embedder:
    def __init__(self, model_path: str | Path | None = None):
        model_path = Path(model_path or os.getenv("EMBEDDER_MODEL_PATH", DEFAULT_MODEL_PATH))
        logger.info(f"Loading ONNX embedding model from: {model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        self.session = ort.InferenceSession(str(model_path / "model.onnx"))
        self._input_names = {inp.name for inp in self.session.get_inputs()}
        logger.info(f"ONNX model loaded; inputs={sorted(self._input_names)}")

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="np")
        feed = {name: inputs[name] for name in self._input_names if name in inputs}
        outputs = self.session.run(["sentence_embedding"], feed)
        return outputs[0].tolist()

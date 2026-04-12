"""
Shared pytest fixtures.

IMPORTANT: The Embedder patch at module level must run before any backend
service module is imported — pytest loads conftest.py first, which guarantees
the mock is in place before DocumentService / QAService are instantiated.
"""

from unittest.mock import MagicMock, patch

import pytest

# Patch Embedder at its source so importing backend.main doesn't try to load
# the 87MB ONNX model from disk.

_mock_embedder_instance = MagicMock()
_mock_embedder_instance.embed.side_effect = lambda texts: [[0.0] * 384 for _ in texts]

patch("backend.rag.embedder.Embedder", return_value=_mock_embedder_instance).start()

# Safe to import backend.main now that Embedder is mocked
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """FastAPI test client — no real server, no ONNX model, no RunPod calls."""
    return TestClient(app)


@pytest.fixture
def fake_embedding():
    """A 384-dim zero vector matching all-MiniLM-L6-v2 output shape."""
    return [0.0] * 384

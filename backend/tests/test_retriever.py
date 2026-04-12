import pytest

from backend.rag.retriever import Retriever


@pytest.fixture
def retriever():
    """Fresh Retriever instance per test — avoids sharing the module singleton."""
    return Retriever()


@pytest.fixture
def indexed_retriever(retriever, fake_embedding):
    """Retriever with one document already indexed."""
    chunks = ["Paris is the capital of France.", "The Eiffel Tower is in Paris."]
    embeddings = [fake_embedding, fake_embedding]
    retriever.index("doc-1", chunks, embeddings)
    return retriever


def test_retrieve_unknown_document_raises(retriever, fake_embedding):
    with pytest.raises(ValueError, match="Document ID not found"):
        retriever.retrieve("nonexistent-id", fake_embedding)


def test_index_and_retrieve_returns_chunks(indexed_retriever, fake_embedding):
    results = indexed_retriever.retrieve("doc-1", fake_embedding, top_k=2)
    assert len(results) == 2
    assert all(isinstance(r, str) for r in results)


def test_retrieve_top_k_limits_results(indexed_retriever, fake_embedding):
    results = indexed_retriever.retrieve("doc-1", fake_embedding, top_k=1)
    assert len(results) == 1


def test_multiple_documents_are_isolated(retriever, fake_embedding):
    retriever.index("doc-a", ["Chunk from A"], [fake_embedding])
    retriever.index("doc-b", ["Chunk from B"], [fake_embedding])

    results_a = retriever.retrieve("doc-a", fake_embedding, top_k=1)
    results_b = retriever.retrieve("doc-b", fake_embedding, top_k=1)

    assert results_a == ["Chunk from A"]
    assert results_b == ["Chunk from B"]

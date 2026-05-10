from io import BytesIO
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_document_service(monkeypatch):
    """Replace the module-level document_service in routes with a mock."""
    mock = MagicMock()
    mock.process_document.return_value = "test-doc-id"
    monkeypatch.setattr("backend.api.routes.document_service", mock)
    return mock


@pytest.fixture
def mock_qa_service(monkeypatch):
    """Replace the module-level qa_service in routes with a mock."""
    mock = MagicMock()
    mock.ask.return_value = ("Test answer.", ["chunk 1", "chunk 2"])
    monkeypatch.setattr("backend.api.routes.qa_service", mock)
    return mock


@pytest.fixture
def mock_summary_service(monkeypatch):
    """Replace the module-level summary_service in routes with a mock."""
    mock = MagicMock()
    mock.summarize.return_value = "A concise summary of the lecture."
    monkeypatch.setattr("backend.api.routes.summary_service", mock)
    return mock


# --- Health check ---


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- Upload endpoint ---


def test_upload_valid_file_returns_document_id(client, mock_document_service):
    response = client.post(
        "/api/upload",
        files={"file": ("notes.txt", BytesIO(b"Lecture content here."), "text/plain")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["document_id"] == "test-doc-id"
    assert body["filename"] == "notes.txt"


def test_upload_calls_process_document(client, mock_document_service):
    client.post(
        "/api/upload",
        files={"file": ("notes.txt", BytesIO(b"Some content."), "text/plain")},
    )
    mock_document_service.process_document.assert_called_once()


# --- Ask endpoint ---


def test_ask_valid_request_returns_answer(client, mock_qa_service):
    response = client.post(
        "/api/ask",
        json={"document_id": "test-doc-id", "question": "What is this about?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Test answer."
    assert body["sources"] == ["chunk 1", "chunk 2"]


def test_ask_empty_question_returns_422(client, mock_qa_service):
    response = client.post(
        "/api/ask",
        json={"document_id": "test-doc-id", "question": ""},
    )
    assert response.status_code == 422


def test_ask_empty_document_id_returns_422(client, mock_qa_service):
    response = client.post(
        "/api/ask",
        json={"document_id": "", "question": "What is this about?"},
    )
    assert response.status_code == 422


# --- Summarize endpoint ---


def test_summarize_returns_markdown_summary(client, mock_summary_service):
    response = client.post(
        "/api/summarize",
        files={"file": ("notes.pdf", BytesIO(b"%PDF-1.4 fake pdf content"), "application/pdf")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["summary_markdown"] == "A concise summary of the lecture."
    assert body["original_filename"] == "notes.pdf"


def test_summarize_calls_summary_service(client, mock_summary_service):
    client.post(
        "/api/summarize",
        files={"file": ("notes.pdf", BytesIO(b"some bytes"), "application/pdf")},
    )
    mock_summary_service.summarize.assert_called_once()
    args = mock_summary_service.summarize.call_args[0]
    assert args[0] == "notes.pdf"
    assert args[1] == b"some bytes"


def test_summarize_rejects_oversized_file(client, mock_summary_service):
    big_payload = b"x" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/api/summarize",
        files={"file": ("big.pdf", BytesIO(big_payload), "application/pdf")},
    )
    assert response.status_code == 413
    mock_summary_service.summarize.assert_not_called()

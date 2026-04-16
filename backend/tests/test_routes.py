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

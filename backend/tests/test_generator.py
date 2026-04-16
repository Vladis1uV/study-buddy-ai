"""
Unit tests for the Generator class (RunPod calls are mocked).
"""

from unittest.mock import MagicMock, patch
import pytest
from backend.rag.generator import Generator, _ASST_HEADER, _EOT


def _mock_response(status_code: int, json_body: dict) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_body
    mock.text = str(json_body)
    return mock


@pytest.fixture()
def generator(monkeypatch):
    monkeypatch.setenv("RUNPOD_API_KEY", "test-key")
    monkeypatch.setenv("RUNPOD_ENDPOINT_ID", "test-endpoint")
    return Generator()


def _vllm_response(full_text: str) -> dict:
    return {
        "output": [{"choices": [{"tokens": [full_text]}], "usage": {"input": 3, "output": 10}}],
        "status": "COMPLETED",
    }


class TestBuildPrompt:
    def test_includes_context(self, generator):
        prompt = generator._build_prompt("What is X?", "X is a concept.")
        assert "X is a concept." in prompt

    def test_includes_question(self, generator):
        prompt = generator._build_prompt("What is X?", "some context")
        assert "What is X?" in prompt

    def test_has_llama_chat_tokens(self, generator):
        prompt = generator._build_prompt("q", "ctx")
        assert "<|begin_of_text|>" in prompt
        assert _ASST_HEADER in prompt
        assert _EOT in prompt


class TestGenerate:
    def test_success_extracts_assistant_turn(self, generator):
        answer_text = "This is the answer."
        full_text = f"...prompt stuff...{_ASST_HEADER}\n\n{answer_text}"
        mock_resp = _mock_response(200, _vllm_response(full_text))

        with patch("httpx.post", return_value=mock_resp):
            result = generator.generate("What is X?", ["context chunk"])

        assert result == answer_text

    def test_success_strips_whitespace(self, generator):
        full_text = f"{_ASST_HEADER}\n\n  answer with spaces  "
        mock_resp = _mock_response(200, _vllm_response(full_text))

        with patch("httpx.post", return_value=mock_resp):
            result = generator.generate("q", ["ctx"])

        assert result == "answer with spaces"

    def test_fallback_when_no_marker(self, generator):
        # If vLLM returns text without the assistant marker, return it as-is
        mock_resp = _mock_response(200, _vllm_response("raw output"))

        with patch("httpx.post", return_value=mock_resp):
            result = generator.generate("q", ["ctx"])

        assert result == "raw output"

    def test_raises_on_non_200(self, generator):
        mock_resp = _mock_response(500, {"error": "internal server error"})

        with patch("httpx.post", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="RunPod error 500"):
                generator.generate("q", ["ctx"])

    def test_correct_endpoint_url(self, generator):
        full_text = f"{_ASST_HEADER}\n\nanswer"
        mock_resp = _mock_response(200, _vllm_response(full_text))

        with patch("httpx.post", return_value=mock_resp) as mock_post:
            generator.generate("q", ["ctx"])

        called_url = mock_post.call_args[0][0]
        assert "test-endpoint" in called_url
        assert called_url.endswith("/runsync")

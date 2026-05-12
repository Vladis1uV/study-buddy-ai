"""
Unit tests for the Generator class (OpenAI client is mocked).
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest
from openai import APIError, APITimeoutError

from backend.exceptions import LLMTimeoutError, LLMUpstreamError
from backend.rag.generator import Generator


def _mock_completion(content: str | None) -> MagicMock:
    """Build a mock that mimics openai.types.chat.ChatCompletion."""
    message = MagicMock()
    message.content = content
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.fixture()
def generator(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://test.example.com/v1")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    return Generator()


class TestBuildMessages:
    def test_includes_context(self, generator):
        messages = generator._build_messages("What is X?", "X is a concept.")
        user_content = messages[-1]["content"]
        assert "X is a concept." in user_content

    def test_includes_question(self, generator):
        messages = generator._build_messages("What is X?", "some context")
        user_content = messages[-1]["content"]
        assert "What is X?" in user_content

    def test_has_system_and_user_roles(self, generator):
        messages = generator._build_messages("q", "ctx")
        roles = [m["role"] for m in messages]
        assert roles == ["system", "user"]


class TestGenerate:
    def test_returns_completion_content(self, generator):
        mock = _mock_completion("This is the answer.")
        with patch.object(generator.client.chat.completions, "create", return_value=mock):
            result = generator.generate("What is X?", ["context chunk"])
        assert result == "This is the answer."

    def test_strips_whitespace(self, generator):
        mock = _mock_completion("  answer with spaces  ")
        with patch.object(generator.client.chat.completions, "create", return_value=mock):
            result = generator.generate("q", ["ctx"])
        assert result == "answer with spaces"

    def test_raises_on_timeout(self, generator):
        err = APITimeoutError(request=httpx.Request("POST", "https://test.example.com/v1"))
        with patch.object(generator.client.chat.completions, "create", side_effect=err):
            with pytest.raises(LLMTimeoutError):
                generator.generate("q", ["ctx"])

    def test_raises_on_api_error(self, generator):
        err = APIError(
            "upstream failed",
            request=httpx.Request("POST", "https://test.example.com/v1"),
            body=None,
        )
        with patch.object(generator.client.chat.completions, "create", side_effect=err):
            with pytest.raises(LLMUpstreamError):
                generator.generate("q", ["ctx"])

    def test_raises_on_unexpected_response_shape(self, generator):
        bad = MagicMock()
        bad.choices = []
        with patch.object(generator.client.chat.completions, "create", return_value=bad):
            with pytest.raises(LLMUpstreamError):
                generator.generate("q", ["ctx"])

    def test_raises_on_null_content(self, generator):
        mock = _mock_completion(None)
        with patch.object(generator.client.chat.completions, "create", return_value=mock):
            with pytest.raises(LLMUpstreamError):
                generator.generate("q", ["ctx"])

    def test_uses_configured_model(self, generator):
        mock = _mock_completion("ok")
        with patch.object(
            generator.client.chat.completions, "create", return_value=mock
        ) as mock_create:
            generator.generate("q", ["ctx"])
        assert mock_create.call_args.kwargs["model"] == "test-model"

    def test_passes_max_tokens(self, generator):
        mock = _mock_completion("ok")
        with patch.object(
            generator.client.chat.completions, "create", return_value=mock
        ) as mock_create:
            generator.generate("q", ["ctx"])
        assert mock_create.call_args.kwargs["max_tokens"] == 512

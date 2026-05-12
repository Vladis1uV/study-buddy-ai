"""
Unit tests for the Summarizer (Generator.complete is mocked).
"""

from unittest.mock import MagicMock

import pytest

from backend.rag.summarizer import SINGLE_SHOT_CHAR_LIMIT, Summarizer


def _all_content(messages: list[dict]) -> str:
    return " ".join(m["content"] for m in messages)


@pytest.fixture()
def fake_generator():
    gen = MagicMock()
    gen.complete.return_value = "A concise paragraph summarizing the lecture."
    return gen


@pytest.fixture()
def summarizer(fake_generator):
    return Summarizer(generator=fake_generator)


class TestSingleShot:
    def test_short_text_uses_single_shot(self, summarizer, fake_generator):
        summarizer.summarize("Short lecture about gradients.", target_words=250)
        assert fake_generator.complete.call_count == 1

    def test_returns_generator_output(self, summarizer):
        result = summarizer.summarize("Some lecture text.", target_words=250)
        assert result == "A concise paragraph summarizing the lecture."

    def test_prompt_contains_target_word_count(self, summarizer, fake_generator):
        summarizer.summarize("Some lecture text.", target_words=180)
        messages = fake_generator.complete.call_args[0][0]
        assert "180 words" in _all_content(messages)

    def test_prompt_contains_source_text(self, summarizer, fake_generator):
        summarizer.summarize("The chain rule states that...", target_words=250)
        messages = fake_generator.complete.call_args[0][0]
        assert "The chain rule states that..." in _all_content(messages)


class TestMapReduce:
    def test_long_text_triggers_map_reduce(self, summarizer, fake_generator):
        long_text = "x" * (SINGLE_SHOT_CHAR_LIMIT + 1000)
        summarizer.summarize(long_text, target_words=250)
        # >1 call: at least one per chunk plus one reduce
        assert fake_generator.complete.call_count > 1

    def test_map_reduce_final_call_is_reduce_prompt(self, summarizer, fake_generator):
        long_text = "x" * (SINGLE_SHOT_CHAR_LIMIT + 1000)
        summarizer.summarize(long_text, target_words=250)
        last_messages = fake_generator.complete.call_args_list[-1][0][0]
        assert "Partial summary" in _all_content(last_messages)

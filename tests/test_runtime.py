"""Smoke tests for runtime helpers and chat flow."""

from unittest.mock import Mock
from unittest.mock import patch

from subit_t.runtime.ollama import call_ollama
from subit_t.runtime.chat import run_chat_session
from subit_t.runtime.web import build_user_text, needs_web_search


def test_needs_web_search_detects_live_queries():
    assert needs_web_search("Weather in Kyiv today") is True
    assert needs_web_search("Explain how token refresh works") is False


def test_build_user_text_adds_guidance_when_external_context_exists():
    text = "Weather in Kyiv today"
    user_text = build_user_text(
        text,
        web_results=[{"title": "Example", "url": "https://example.com", "snippet": ""}],
        page_summaries=[{"title": "Example", "url": "https://example.com", "content": "Sunny"}],
    )
    assert "Use the supplied web results" in user_text
    assert "higher-confidence evidence" in user_text


def test_chat_session_supports_help_and_quit():
    inputs = iter(["/help", "/quit"])
    outputs = []

    run_chat_session(
        model="llama3.2",
        timeout=30,
        history_turns=4,
        web=False,
        auto_web=True,
        web_k=5,
        web_timeout=20,
        fetch_pages=0,
        fetch_timeout=15,
        show_sources=False,
        input_fn=lambda prompt: next(inputs),
        output_fn=outputs.append,
    )

    joined = "\n".join(outputs)
    assert "SUBIT-T chat mode" in joined
    assert "Commands: /exit, /quit, /help" in joined


def test_chat_session_auto_web_flow_emits_sources_and_response():
    inputs = iter(["Weather in Kyiv today", "/quit"])
    outputs = []
    web_results = [{"title": "BBC Weather", "url": "https://example.com/weather", "snippet": "Forecast"}]
    page_summaries = [{"title": "BBC Weather", "url": "https://example.com/weather", "content": "Sunny with clouds"}]

    with (
        patch("subit_t.runtime.chat.prepare_external_context", return_value=(web_results, page_summaries, "Web search results:\n1. BBC Weather")),
        patch("subit_t.runtime.chat.call_ollama", return_value="Kyiv will be mild today."),
    ):
        run_chat_session(
            model="llama3.2",
            timeout=30,
            history_turns=4,
            web=False,
            auto_web=True,
            web_k=5,
            web_timeout=20,
            fetch_pages=1,
            fetch_timeout=15,
            show_sources=True,
            input_fn=lambda prompt: next(inputs),
            output_fn=outputs.append,
        )

    joined = "\n".join(outputs)
    assert "[auto-web triggered]" in joined
    assert "[source] BBC Weather - https://example.com/weather" in joined
    assert "Assistant [" in joined
    assert "Kyiv will be mild today." in joined


def test_chat_session_falls_back_when_web_search_fails():
    inputs = iter(["Weather in Kyiv today", "/quit"])
    outputs = []

    with (
        patch("subit_t.runtime.chat.prepare_external_context", side_effect=RuntimeError("search offline")),
        patch("subit_t.runtime.chat.call_ollama", return_value="Local fallback answer."),
    ):
        run_chat_session(
            model="llama3.2",
            timeout=30,
            history_turns=4,
            web=False,
            auto_web=True,
            web_k=5,
            web_timeout=20,
            fetch_pages=1,
            fetch_timeout=15,
            show_sources=True,
            input_fn=lambda prompt: next(inputs),
            output_fn=outputs.append,
        )

    joined = "\n".join(outputs)
    assert "Web search failed: search offline" in joined
    assert "Continuing without external context." in joined
    assert "Local fallback answer." in joined


def test_call_ollama_raises_runtime_error_for_unexpected_payload():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"not_message": {}}

    with patch("subit_t.runtime.ollama.requests.post", return_value=response):
        try:
            call_ollama(model="llama3.2", messages=[{"role": "user", "content": "hi"}], timeout=10)
        except RuntimeError as exc:
            assert "unexpected response payload" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("Expected RuntimeError for malformed Ollama payload")

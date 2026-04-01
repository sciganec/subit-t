"""Helpers for talking to a local Ollama instance."""

from __future__ import annotations

import requests


OLLAMA_URL = "http://localhost:11434/api/chat"


def call_ollama(*, model: str, messages: list[dict], timeout: int) -> str:
    """Send a chat request to a local Ollama server and return message content."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "stream": False,
                "messages": messages,
            },
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError("Ollama is not running on http://localhost:11434") from exc
    except Exception as exc:  # pragma: no cover - surface original request failure
        raise RuntimeError(f"Ollama request failed: {exc}") from exc

    try:
        payload = response.json()
        return payload["message"]["content"]
    except Exception as exc:  # pragma: no cover - malformed payloads are runtime-dependent
        raise RuntimeError(f"Ollama returned an unexpected response payload: {exc}") from exc

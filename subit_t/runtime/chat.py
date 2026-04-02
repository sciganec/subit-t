"""Interactive chat loop for local Ollama sessions."""

from __future__ import annotations

from collections.abc import Callable

from ..encoder import encode
from ..injector import build_prompt
from ..prompts import build_assistant_extra
from .ollama import call_ollama
from .web import build_user_text, needs_web_search, prepare_external_context


def run_chat_session(
    *,
    model: str,
    timeout: int,
    history_turns: int,
    web: bool,
    auto_web: bool,
    web_k: int,
    web_timeout: int,
    fetch_pages: int,
    fetch_timeout: int,
    show_sources: bool,
    assistant: str = "general",
    model_assisted_encoder: bool = False,
    encoder_model: str = "llama3.2",
    encoder_timeout: int = 20,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> None:
    history: list[dict[str, str]] = []

    output_fn("\nSUBIT-T chat mode")
    output_fn("Type your message and press Enter.")
    output_fn("Type /exit or /quit to stop.\n")

    while True:
        try:
            text = input_fn("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("\n")
            break

        if not text:
            continue
        if text.lower() in {"/exit", "/quit"}:
            break
        if text.lower() == "/help":
            output_fn("Commands: /exit, /quit, /help\n")
            continue

        result = encode(
            text,
            model_assisted=model_assisted_encoder,
            model=encoder_model,
            timeout=encoder_timeout,
        )
        use_web = web or (auto_web and needs_web_search(text))
        auto_web_triggered = bool(auto_web and not web and use_web)

        try:
            web_results, page_summaries, extra = prepare_external_context(
                text=text,
                use_web=use_web,
                web_k=web_k,
                web_timeout=web_timeout,
                fetch_pages=fetch_pages if use_web else 0,
                fetch_timeout=fetch_timeout,
            )
        except Exception as exc:
            output_fn(f"Web search failed: {exc}")
            output_fn("Continuing without external context.\n")
            web_results, page_summaries, extra = [], [], ""
            use_web = False
            auto_web_triggered = False

        assistant_extra = build_assistant_extra(assistant)
        prompt_extra = "\n\n".join(part for part in [assistant_extra, extra] if part)
        prompt = build_prompt(result.target_state, result.operator, text, extra=prompt_extra)
        user_text = build_user_text(text, web_results, page_summaries)
        messages = [{"role": "system", "content": prompt}, *history, {"role": "user", "content": user_text}]

        try:
            content = call_ollama(model=model, messages=messages, timeout=timeout)
        except RuntimeError as exc:
            output_fn(f"{exc}\n")
            continue

        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": content})
        if len(history) > history_turns * 2:
            history = history[-history_turns * 2 :]

        if auto_web_triggered:
            output_fn("[auto-web triggered]")
        if web_results and show_sources:
            for item in web_results:
                output_fn(f"[source] {item['title']} - {item['url']}")
        output_fn(f"Assistant [{result.current_state.name} -> {result.operator.value} -> {result.target_state.name}]> {content}\n")

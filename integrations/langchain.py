"""
SUBIT-T x LangChain integration for v3 cyclic routing.
"""

from __future__ import annotations

from typing import Any, Optional

from subit_t.core import State, Op
from subit_t.injector import build_prompt, build_minimal_prompt
from subit_t.router import Router


def _require_langchain():
    try:
        import langchain
        return langchain
    except ImportError:
        raise ImportError(
            "LangChain is required for this integration.\n"
            "Install with: pip install subit-t[langchain]"
        )


class SubitPromptTemplate:
    """Builds LangChain-compatible chat messages from State + Op."""

    def __init__(self, minimal: bool = False):
        self.minimal = minimal

    def format(self, state: State, op: Op, user_input: str = "", extra: str = "") -> list[dict]:
        system = build_minimal_prompt(state, op) if self.minimal else build_prompt(state, op, user_input="", extra=extra)
        messages = [{"role": "system", "content": system}]
        if user_input:
            messages.append({"role": "user", "content": user_input})
        return messages

    def to_langchain(self, state: State, op: Op, user_input: str = "") -> Any:
        _require_langchain()
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_core.prompt_values import ChatPromptValue

        messages = [SystemMessage(content=build_prompt(state, op, user_input=""))]
        if user_input:
            messages.append(HumanMessage(content=user_input))
        return ChatPromptValue(messages=messages)


class SubitRouter:
    """Routes text through SUBIT-T and returns metadata without calling an LLM."""

    def __init__(self, start_state: Optional[State] = None):
        self._start = start_state
        self._subit = Router()

    def route(self, text: str) -> dict:
        record = self._subit.route_text(text, context={"text": text})
        transition = record["transition"]
        encoding = record["encoding"]

        next_state = State(transition["result"]["bits"])
        op = Op(transition["operator"])

        return {
            "state": next_state.name,
            "operator": op.value,
            "who": next_state.who,
            "what": next_state.what,
            "when": next_state.when,
            "state_type": next_state.state_type,
            "prompt": build_prompt(next_state, op, text),
            "encoding": encoding,
            "transition": transition,
        }

    @property
    def history(self) -> list[dict]:
        return self._subit.history

    def op_distribution(self) -> dict:
        return self._subit.op_distribution()

    def stuck_detection(self) -> dict:
        return self._subit.stuck_detection()

    def reset(self) -> None:
        self._subit.reset()


class SubitRouterChain:
    """Full LangChain chain: text -> encode -> route -> LLM response."""

    def __init__(self, llm: Any, minimal_prompt: bool = False, verbose: bool = False):
        _require_langchain()
        self.llm = llm
        self.router = SubitRouter()
        self.tmpl = SubitPromptTemplate(minimal=minimal_prompt)
        self.verbose = verbose

    def invoke(self, inputs: dict) -> dict:
        _require_langchain()

        text = inputs.get("input", "")
        routing = self.router.route(text)
        next_state = State.from_name(routing["state"])
        op = Op(routing["operator"])

        if self.verbose:
            print(f"[SUBIT-T] {routing['state']} | {op.symbol}({op.value}) | {routing['state_type']}")

        prompt_value = self.tmpl.to_langchain(next_state, op, text)
        response = self.llm.invoke(prompt_value.messages)
        output = response.content if hasattr(response, "content") else str(response)

        return {
            "output": output,
            "state": routing["state"],
            "operator": routing["operator"],
            "who": routing["who"],
            "what": routing["what"],
            "when": routing["when"],
            "prompt": routing["prompt"],
        }

    def batch(self, inputs: list[dict]) -> list[dict]:
        return [self.invoke(item) for item in inputs]

    @property
    def history(self) -> list[dict]:
        return self.router.history

    def op_distribution(self) -> dict:
        return self.router.op_distribution()

    def stuck_detection(self) -> dict:
        return self.router.stuck_detection()

    def __or__(self, other: Any) -> Any:
        _require_langchain()
        from langchain_core.runnables import RunnableLambda

        return RunnableLambda(self.invoke) | other

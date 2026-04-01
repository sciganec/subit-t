"""
SUBIT-T Router v2 — operator-driven agent dispatch.

next_state = apply(current_state, operator)

Registration priority:
  (state + op) → state → op → fallback
"""

from __future__ import annotations
import json
from typing import Callable, Optional

from .core import State, Op, TransitionResult, S_PRIME, S_SYNC, S_SCAN, S_CORE
from .encoder import encode, EncoderResult


AgentFn = Callable[[State, Op, dict], dict]


class Router:
    """
    SUBIT-T Router v2.

    Example:
        router = Router()

        @router.on(state="SYNC")
        def coordinator(state, op, ctx):
            return {"action": "coordinate", "ctx": ctx}

        result = router.route_text("We need to coordinate the launch")
    """

    def __init__(self):
        self._by_state_op: dict[tuple[int, str], AgentFn] = {}
        self._by_state:    dict[int, AgentFn] = {}
        self._by_op:       dict[str, AgentFn] = {}
        self._fallback:    Optional[AgentFn]   = None
        self._history:     list[dict] = []

    # ── Registration ─────────────────────────────

    def register(
        self,
        fn:    AgentFn,
        state: Optional[State | str] = None,
        op:    Optional[Op | str]    = None,
    ) -> None:
        if isinstance(state, str) and state: state = State.from_name(state)
        if isinstance(op, str) and op:       op = Op(op)

        if state and op:
            self._by_state_op[(int(state), op.value)] = fn
        elif state:
            self._by_state[int(state)] = fn
        elif op:
            self._by_op[op.value] = fn
        else:
            self._fallback = fn

    def on(self, state=None, op=None):
        """Decorator shorthand for register."""
        def dec(fn):
            self.register(fn, state=state, op=op)
            return fn
        return dec

    # ── Core routing ──────────────────────────────

    def route(
        self,
        current:  State,
        op:       Op,
        context:  Optional[dict] = None,
    ) -> dict:
        """
        Apply operator to current state → dispatch to agent.

        Returns full record including transition metadata.
        """
        ctx = context or {}
        tr  = current.apply(op)

        fn = (
            self._by_state_op.get((tr.result.bits, op.value)) or
            self._by_state.get(tr.result.bits) or
            self._by_op.get(op.value) or
            self._fallback
        )

        agent_result = fn(tr.result, op, ctx) if fn else None

        record = {
            "transition":   tr.to_dict(),
            "agent_result": agent_result,
        }
        self._history.append(record)
        return record

    def route_text(
        self,
        text:    str,
        context: Optional[dict] = None,
    ) -> dict:
        """
        Full pipeline: text → encode → route.

        Returns record with encoding metadata + transition + agent result.
        """
        enc = encode(text)
        record = self.route(enc.current_state, enc.operator, context)
        record["encoding"] = enc.to_dict()
        return record

    def chain(
        self,
        start:   State,
        ops:     list[Op],
        context: Optional[dict] = None,
    ) -> list[dict]:
        """Apply a sequence of operators, feeding each result into the next."""
        ctx, current, log = context or {}, start, []
        for op in ops:
            rec = self.route(current, op, ctx)
            log.append(rec)
            current = State(rec["transition"]["result"]["bits"])
        return log

    # ── Observability ─────────────────────────────

    @property
    def history(self) -> list[dict]:
        return self._history

    def op_distribution(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self._history:
            op = r["transition"]["operator"]
            counts[op] = counts.get(op, 0) + 1
        return counts

    def state_distribution(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self._history:
            name = r["transition"]["result"]["name"]
            counts[name] = counts.get(name, 0) + 1
        return counts

    def stuck_detection(self) -> dict[str, bool]:
        """Detect suspicious routing patterns in v3 history."""
        dist  = self.op_distribution()
        total = sum(dist.values()) or 1
        return {
            "over_inv": dist.get("INV", 0) / total > 0.4,
            "who_heavy": dist.get("WHO_SHIFT", 0) / total > 0.6,
            "what_heavy": dist.get("WHAT_SHIFT", 0) / total > 0.6,
            "when_heavy": dist.get("WHEN_SHIFT", 0) / total > 0.6,
        }

    def idempotent_rate(self) -> float:
        total = len(self._history)
        if not total: return 0.0
        return sum(1 for r in self._history if r["transition"]["idempotent"]) / total

    def reset(self) -> None:
        self._history.clear()

    def export_history(self) -> str:
        return json.dumps(self._history, indent=2, ensure_ascii=False)

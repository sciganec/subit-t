"""
SUBIT-T Encoder - text to (State, Op) for v3 cyclic algebra.

Phase 1: infer current state from text
Phase 2: infer desired direction of movement
Phase 3: choose one operator for the next step in the trajectory
"""

from __future__ import annotations

from dataclasses import dataclass

from .canon import CANON, STATE_WEIGHT, _make_bits
from .core import State, Op


_CURRENT_KW: dict[str, dict[str, list[str]]] = {
    "WHO": {
        "ME": ["i ", "my ", "i'll", "let me", "i will", "i'm", "i've"],
        "WE": ["we ", "our ", "team", "together", "let's", "everyone", "we're"],
        "YOU": ["you ", "your ", "this code", "the issue", "the bug", "review this", "the function"],
        "THEY": ["system", "the model", "data shows", "historically", "evidence", "the pattern"],
    },
    "WHAT": {
        "EXPAND": ["idea", "design", "draft", "brainstorm", "architecture", "document", "new approach", "proposal"],
        "TRANSFORM": ["running", "executing", "deploying", "building", "implementing", "pipeline", "in progress"],
        "REDUCE": ["review", "analyze", "bug", "issue", "problem", "memory leak", "error", "debug", "logs", "outage", "vulnerabilit", "critique", "check", "audit"],
        "PRESERVE": ["log", "store", "archive", "record", "save", "remember", "document", "note"],
    },
    "WHEN": {
        "INITIATE": ["start", "begin", "first", "scratch", "initial", "kick off", "new project", "today", "opening"],
        "SUSTAIN": ["now", "currently", "active", "working", "processing", "right now", "in progress", "asap"],
        "INTEGRATE": ["finish", "complete", "wrap", "close", "done", "final", "commit", "conclude", "merge", "before the release"],
        "RELEASE": ["wait", "pause", "ready", "idle", "standby", "later", "hold", "queue", "pending"],
    },
}

_TARGET_KW: dict[str, dict[str, list[str]]] = {
    "WHO": {
        "ME": ["i will", "let me", "i'll do", "on my own", "autonomously", "i can handle"],
        "WE": ["coordinate", "align", "team effort", "collaborate", "all of us", "share", "together we"],
        "YOU": ["please review", "can you", "analyze this", "evaluate", "give feedback", "check this"],
        "THEY": ["observe", "monitor", "track", "watch", "report on", "the system should"],
    },
    "WHAT": {
        "EXPAND": ["generate", "create", "draft", "propose", "design", "come up with", "write", "document"],
        "TRANSFORM": ["run", "execute", "deploy", "ship", "implement", "apply", "perform", "launch", "build"],
        "REDUCE": ["review", "analyze", "critique", "evaluate", "check", "test", "audit", "debug", "assess", "identify", "investigate"],
        "PRESERVE": ["save", "document", "log", "store", "archive", "keep", "record", "note down"],
    },
    "WHEN": {
        "INITIATE": ["start", "begin", "fresh", "restart", "from scratch", "new", "reset", "kick off", "opening"],
        "SUSTAIN": ["now", "immediately", "right away", "asap", "proceed", "continue", "keep going", "right now"],
        "INTEGRATE": ["finish", "complete", "close", "wrap up", "finalize", "commit", "conclude", "deliver", "before the release"],
        "RELEASE": ["later", "wait", "pause", "when ready", "no rush", "hold", "queue", "standby"],
    },
    "ROLLBACK": {
        "YES": ["rollback", "undo", "revert", "back out", "reset all", "recover", "error recovery"],
    },
}

_WHO_ORDER = ["THEY", "YOU", "ME", "WE"]
_WHAT_ORDER = ["PRESERVE", "REDUCE", "EXPAND", "TRANSFORM"]
_WHEN_ORDER = ["RELEASE", "INTEGRATE", "INITIATE", "SUSTAIN"]


def _score(text: str, kw_map: dict[str, list[str]]) -> dict[str, int]:
    lowered = text.lower()
    return {key: sum(1 for word in words if word in lowered) for key, words in kw_map.items()}


def _pick(scores: dict[str, int], fallback: str) -> tuple[str, int]:
    max_score = max(scores.values())
    if max_score == 0:
        return fallback, 0
    return max(scores, key=scores.get), max_score


def _to_distribution(scores: dict[str, int]) -> dict[str, float]:
    floor = 0.05
    total = sum(scores.values()) or 1
    raw = {key: floor + (value / total) * (1 - floor * len(scores)) for key, value in scores.items()}
    norm = sum(raw.values())
    return {key: value / norm for key, value in raw.items()}


def _forward_steps(order: list[str], current: str, target: str) -> int:
    start = order.index(current)
    end = order.index(target)
    return (end - start) % len(order)


@dataclass
class EncoderResult:
    current_state: State
    target_state: State
    operator: Op
    axis_diff: str
    all_diffs: list[dict]
    who_dist: dict[str, float]
    what_dist: dict[str, float]
    when_dist: dict[str, float]
    op_confidence: float
    operator_distribution: dict[str, float]
    state_distribution: dict[str, float]
    dominant_state_bits: int

    @property
    def where_dist(self) -> dict[str, float]:
        return self.what_dist

    def to_dict(self) -> dict:
        return {
            "current_state": self.current_state.to_dict(),
            "target_state": self.target_state.to_dict(),
            "dominant_state": self.current_state.name,
            "dominant_state_bits": self.dominant_state_bits,
            "operator": self.operator.value,
            "axis_diff": self.axis_diff,
            "op_confidence": self.op_confidence,
            "operator_distribution": self.operator_distribution,
            "distributions": {
                "who": self.who_dist,
                "what": self.what_dist,
                "when": self.when_dist,
                "where": self.what_dist,
            },
            "state_distribution": self.state_distribution,
        }


def encode(text: str) -> EncoderResult:
    """
    Encode text into current state, desired target and a single next-step operator.

    In v3, the chosen operator is always a movement step. The returned target_state
    is the immediate next state after applying that operator.
    """

    lowered = text.lower()

    who_cur_scores = _score(lowered, _CURRENT_KW["WHO"])
    what_cur_scores = _score(lowered, _CURRENT_KW["WHAT"])
    when_cur_scores = _score(lowered, _CURRENT_KW["WHEN"])

    who_cur, _ = _pick(who_cur_scores, "ME")
    what_cur, _ = _pick(what_cur_scores, "EXPAND")
    when_cur, _ = _pick(when_cur_scores, "SUSTAIN")

    who_target_scores = _score(lowered, _TARGET_KW["WHO"])
    what_target_scores = _score(lowered, _TARGET_KW["WHAT"])
    when_target_scores = _score(lowered, _TARGET_KW["WHEN"])
    rollback_score = _score(lowered, _TARGET_KW["ROLLBACK"]).get("YES", 0)

    who_target, _ = _pick(who_target_scores, who_cur)
    what_target, _ = _pick(what_target_scores, what_cur)
    when_target, _ = _pick(when_target_scores, when_cur)

    current_state = State(_make_bits(who_cur, what_cur, when_cur))
    desired_state = State(_make_bits(who_target, what_target, when_target))

    diffs = []
    who_steps = _forward_steps(_WHO_ORDER, who_cur, who_target)
    what_steps = _forward_steps(_WHAT_ORDER, what_cur, what_target)
    when_steps = _forward_steps(_WHEN_ORDER, when_cur, when_target)

    if who_steps:
        diffs.append({"axis": "WHO", "op": Op.WHO_SHIFT.value, "steps": who_steps, "from": who_cur, "to": who_target})
    if what_steps:
        diffs.append({"axis": "WHAT", "op": Op.WHAT_SHIFT.value, "steps": what_steps, "from": what_cur, "to": what_target})
    if when_steps:
        diffs.append({"axis": "WHEN", "op": Op.WHEN_SHIFT.value, "steps": when_steps, "from": when_cur, "to": when_target})

    if rollback_score > 0:
        operator = Op.INV
        axis_diff = "ALL"
        op_confidence = 1.0
    elif diffs:
        chosen = min(diffs, key=lambda item: (item["steps"], {"WHO": 0, "WHAT": 1, "WHEN": 2}[item["axis"]]))
        operator = Op(chosen["op"])
        axis_diff = chosen["axis"]
        op_confidence = 1.0 if chosen["steps"] == 1 else 0.75
    else:
        cycle_priority = [Op.WHAT_SHIFT, Op.WHEN_SHIFT, Op.WHO_SHIFT]
        signal_strength = {
            Op.WHO_SHIFT: sum(who_target_scores.values()),
            Op.WHAT_SHIFT: sum(what_target_scores.values()) + sum(what_cur_scores.values()),
            Op.WHEN_SHIFT: sum(when_target_scores.values()) + sum(when_cur_scores.values()),
        }
        operator = max(cycle_priority, key=lambda op: (signal_strength[op], -cycle_priority.index(op)))
        axis_diff = operator.value.removesuffix("_SHIFT")
        op_confidence = 0.5

    next_state = current_state.apply(operator).result

    op_raw = {
        Op.WHO_SHIFT.value: float(bool(who_steps)),
        Op.WHAT_SHIFT.value: float(bool(what_steps)),
        Op.WHEN_SHIFT.value: float(bool(when_steps)),
        Op.INV.value: float(bool(rollback_score)),
    }
    if not any(op_raw.values()):
        op_raw[operator.value] = 1.0
    op_total = sum(op_raw.values()) or 1.0
    op_dist = {key: value / op_total for key, value in op_raw.items()}
    floor = 0.05
    op_dist = {key: floor + value * (1 - floor * 4) for key, value in op_dist.items()}
    op_norm = sum(op_dist.values())
    op_dist = {key: value / op_norm for key, value in op_dist.items()}

    who_dist = _to_distribution(who_cur_scores)
    what_dist = _to_distribution(what_cur_scores)
    when_dist = _to_distribution(when_cur_scores)

    state_scores = {}
    for bits, entry in CANON.items():
        name = entry[3]
        prior = STATE_WEIGHT.get(name, 0.5)
        score = who_dist.get(entry[0], 0) * what_dist.get(entry[1], 0) * when_dist.get(entry[2], 0) * prior
        state_scores[name] = score
    total_state = sum(state_scores.values()) or 1.0
    state_distribution = {key: value / total_state for key, value in state_scores.items()}
    top_states = dict(sorted(state_distribution.items(), key=lambda item: item[1], reverse=True)[:16])

    return EncoderResult(
        current_state=current_state,
        target_state=next_state,
        operator=operator,
        axis_diff=axis_diff,
        all_diffs=diffs,
        who_dist=who_dist,
        what_dist=what_dist,
        when_dist=when_dist,
        op_confidence=op_confidence,
        operator_distribution=op_dist,
        state_distribution=top_states,
        dominant_state_bits=current_state.bits,
    )

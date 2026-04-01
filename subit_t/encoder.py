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

_FACTUAL_LOOKUP_TERMS = [
    "latest",
    "recent",
    "today",
    "current",
    "right now",
    "this week",
    "news",
    "weather",
    "release",
    "price",
    "stock",
    "version",
]
_LOOKUP_VERBS = [
    "find",
    "look up",
    "search",
    "what happened",
    "what is",
    "who is",
    "when is",
    "summarize",
]
_REVIEW_TERMS = [
    "review this",
    "check this",
    "analyze this",
    "can you review",
    "please review",
    "reviewing",
    "review the",
    "review changes",
    "review pr",
    "safe before we merge",
    "tell me what to change",
]
_CREATION_TERMS = [
    "draft",
    "proposal",
    "from scratch",
    "start building",
    "new architecture",
    "new design",
    "kick off",
]
_BUILD_START_TERMS = [
    "start building",
    "begin building",
    "begin implementing",
    "start implementing",
    "from scratch",
    "from zero",
    "build the",
]
_EXECUTION_TERMS = [
    "run",
    "execute",
    "deploy",
    "ship",
    "launch",
    "apply",
    "perform",
    "build",
    "building",
]
_IMMEDIATE_TERMS = ["now", "immediately", "right away", "asap"]
_TEAM_TERMS = ["we ", "let's", "team", "together", "align", "coordinate"]
_ROOT_CAUSE_TERMS = ["root cause", "outage", "logs", "incident", "failure", "recover", "mitigate"]
_DESIGN_COLLAB_TERMS = ["design", "architecture", "proposal", "plan", "reviewing", "review"]
_DIRECT_REQUEST_TERMS = ["can you", "please", "check whether", "review this", "check this", "analyze this"]
_START_REVIEW_TERMS = ["start reviewing", "begin reviewing", "let's review", "reviewing the"]
_DEPLOYMENT_FAILURE_TERMS = ["deployment failure", "deploy failure", "failed deployment", "rollback deployment"]
_AUDIT_TERMS = ["audit", "auditing", "vulnerabilit", "security module", "security review"]


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


def _contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def _boost(scores: dict[str, int], key: str, amount: int) -> None:
    scores[key] = scores.get(key, 0) + amount


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
    routing_reason: str
    signal_summary: dict[str, bool]

    @property
    def where_dist(self) -> dict[str, float]:
        return self.what_dist

    @property
    def next_state(self) -> State:
        return self.target_state

    def to_dict(self) -> dict:
        return {
            "current_state": self.current_state.to_dict(),
            "target_state": self.target_state.to_dict(),
            "next_state": self.target_state.to_dict(),
            "dominant_state": self.current_state.name,
            "dominant_state_bits": self.dominant_state_bits,
            "operator": self.operator.value,
            "axis_diff": self.axis_diff,
            "op_confidence": self.op_confidence,
            "routing_reason": self.routing_reason,
            "signal_summary": self.signal_summary,
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

    factual_lookup = _contains_any(lowered, _FACTUAL_LOOKUP_TERMS) and _contains_any(lowered, _LOOKUP_VERBS)
    review_request = _contains_any(lowered, _REVIEW_TERMS)
    creation_request = _contains_any(lowered, _CREATION_TERMS)
    build_start_request = _contains_any(lowered, _BUILD_START_TERMS)
    execution_request = _contains_any(lowered, _EXECUTION_TERMS)
    immediate_request = _contains_any(lowered, _IMMEDIATE_TERMS)
    team_request = _contains_any(lowered, _TEAM_TERMS)
    incident_request = _contains_any(lowered, _ROOT_CAUSE_TERMS)
    design_collab_request = team_request and _contains_any(lowered, _DESIGN_COLLAB_TERMS)
    direct_request = _contains_any(lowered, _DIRECT_REQUEST_TERMS)
    start_review_request = _contains_any(lowered, _START_REVIEW_TERMS)
    deployment_failure_request = _contains_any(lowered, _DEPLOYMENT_FAILURE_TERMS)
    audit_request = _contains_any(lowered, _AUDIT_TERMS)
    rollback_detected = _contains_any(lowered, _TARGET_KW["ROLLBACK"]["YES"])

    who_cur_scores = _score(lowered, _CURRENT_KW["WHO"])
    what_cur_scores = _score(lowered, _CURRENT_KW["WHAT"])
    when_cur_scores = _score(lowered, _CURRENT_KW["WHEN"])

    if factual_lookup:
        _boost(who_cur_scores, "THEY", 4)
        _boost(what_cur_scores, "EXPAND", 3)
        _boost(when_cur_scores, "SUSTAIN", 2)
    if review_request:
        _boost(who_cur_scores, "YOU", 4)
        _boost(what_cur_scores, "REDUCE", 4)
        _boost(when_cur_scores, "SUSTAIN", 2)
    if start_review_request:
        _boost(when_cur_scores, "INITIATE", 4)
    if creation_request:
        _boost(who_cur_scores, "ME", 2)
        _boost(what_cur_scores, "EXPAND", 4)
        _boost(when_cur_scores, "INITIATE", 4)
    if build_start_request:
        _boost(who_cur_scores, "ME", 4)
        _boost(what_cur_scores, "EXPAND", 2)
        _boost(when_cur_scores, "INITIATE", 2)
    if execution_request and immediate_request:
        _boost(who_cur_scores, "ME", 2)
        _boost(what_cur_scores, "TRANSFORM", 4)
        _boost(when_cur_scores, "SUSTAIN", 3)
    if team_request:
        _boost(who_cur_scores, "WE", 3)
    if build_start_request:
        who_cur_scores["WE"] = max(0, who_cur_scores.get("WE", 0) - 2)
    if direct_request:
        _boost(who_cur_scores, "YOU", 3)
        who_cur_scores["WE"] = max(0, who_cur_scores.get("WE", 0) - 2)
    if incident_request:
        _boost(who_cur_scores, "THEY", 2)
        _boost(what_cur_scores, "REDUCE", 3)
        _boost(when_cur_scores, "SUSTAIN", 2)
    if audit_request:
        _boost(who_cur_scores, "ME", 2)
        _boost(what_cur_scores, "REDUCE", 4)
        _boost(when_cur_scores, "SUSTAIN", 1)
    if deployment_failure_request:
        _boost(who_cur_scores, "WE", 4)
        _boost(what_cur_scores, "TRANSFORM", 5)
        _boost(when_cur_scores, "SUSTAIN", 3)
    if rollback_detected:
        _boost(what_cur_scores, "EXPAND", 3)
    if review_request and team_request:
        _boost(who_cur_scores, "WE", 2)
        _boost(what_cur_scores, "REDUCE", 2)

    who_cur, _ = _pick(who_cur_scores, "ME")
    what_cur, _ = _pick(what_cur_scores, "EXPAND")
    when_cur, _ = _pick(when_cur_scores, "SUSTAIN")

    who_target_scores = _score(lowered, _TARGET_KW["WHO"])
    what_target_scores = _score(lowered, _TARGET_KW["WHAT"])
    when_target_scores = _score(lowered, _TARGET_KW["WHEN"])
    rollback_score = _score(lowered, _TARGET_KW["ROLLBACK"]).get("YES", 0)

    if factual_lookup:
        rollback_score += 3
        _boost(who_target_scores, "THEY", 2)
    if review_request:
        _boost(who_target_scores, "YOU", 2)
        _boost(what_target_scores, "EXPAND", 4)
    if start_review_request:
        _boost(who_target_scores, "WE", 3)
        _boost(what_target_scores, "EXPAND", 3)
    if creation_request:
        _boost(who_target_scores, "ME", 2)
        _boost(what_target_scores, "TRANSFORM", 4)
        _boost(when_target_scores, "INITIATE", 2)
    if build_start_request:
        _boost(who_target_scores, "ME", 3)
        _boost(what_target_scores, "EXPAND", 2)
        _boost(when_target_scores, "SUSTAIN", 5)
    if audit_request:
        _boost(what_target_scores, "EXPAND", 5)
        _boost(who_target_scores, "ME", 2)
    if execution_request:
        _boost(what_target_scores, "TRANSFORM", 3)
    if execution_request and immediate_request:
        _boost(when_target_scores, "RELEASE", 4)
    if team_request:
        _boost(who_target_scores, "WE", 3)
    if design_collab_request:
        _boost(what_target_scores, "TRANSFORM", 4)
    if incident_request and ("recover" in lowered or "mitigate" in lowered or "fix" in lowered):
        _boost(what_target_scores, "TRANSFORM", 3)
    if incident_request and ("identify" in lowered or "caused" in lowered or "cause" in lowered):
        _boost(what_target_scores, "TRANSFORM", 2)
    if direct_request:
        _boost(who_target_scores, "YOU", 3)
        who_target_scores["WE"] = max(0, who_target_scores.get("WE", 0) - 2)
    if deployment_failure_request:
        _boost(who_target_scores, "WE", 4)
        _boost(what_target_scores, "TRANSFORM", 3)
        _boost(when_target_scores, "SUSTAIN", 2)

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

    routing_reason = "fallback_cycle"
    if factual_lookup and rollback_score > 0:
        operator = Op.INV
        axis_diff = "ALL"
        op_confidence = 1.0
        routing_reason = "factual_lookup_requires_external_grounding"
    elif rollback_score > 0:
        operator = Op.INV
        axis_diff = "ALL"
        op_confidence = 1.0
        routing_reason = "explicit_rollback_signal"
    elif diffs:
        chosen = min(diffs, key=lambda item: (item["steps"], {"WHO": 0, "WHAT": 1, "WHEN": 2}[item["axis"]]))
        if execution_request and immediate_request and when_steps:
            chosen = next(item for item in diffs if item["axis"] == "WHEN")
            routing_reason = "immediate_execution_prefers_when_shift"
        elif review_request and what_steps:
            chosen = next(item for item in diffs if item["axis"] == "WHAT")
            routing_reason = "review_request_prefers_what_shift"
        elif build_start_request and when_steps:
            chosen = next(item for item in diffs if item["axis"] == "WHEN")
            routing_reason = "build_start_prefers_when_shift"
        elif creation_request and what_steps:
            chosen = next(item for item in diffs if item["axis"] == "WHAT")
            routing_reason = "creation_request_prefers_what_shift"
        elif design_collab_request and what_steps:
            chosen = next(item for item in diffs if item["axis"] == "WHAT")
            routing_reason = "design_collaboration_prefers_what_shift"
        else:
            routing_reason = f"closest_axis_step_{chosen['axis'].lower()}"
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
        if review_request:
            signal_strength[Op.WHAT_SHIFT] += 4
        if design_collab_request:
            signal_strength[Op.WHAT_SHIFT] += 4
        if build_start_request:
            signal_strength[Op.WHEN_SHIFT] += 5
        if incident_request:
            signal_strength[Op.WHAT_SHIFT] += 2
        if audit_request:
            signal_strength[Op.WHAT_SHIFT] += 6
        operator = max(cycle_priority, key=lambda op: (signal_strength[op], -cycle_priority.index(op)))
        axis_diff = operator.value.removesuffix("_SHIFT")
        op_confidence = 0.5
        routing_reason = "fallback_signal_strength"

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
        routing_reason=routing_reason,
        signal_summary={
            "factual_lookup": factual_lookup,
            "review_request": review_request,
            "creation_request": creation_request,
            "build_start_request": build_start_request,
            "execution_request": execution_request,
            "immediate_request": immediate_request,
            "team_request": team_request,
            "incident_request": incident_request,
            "design_collab_request": design_collab_request,
            "direct_request": direct_request,
            "start_review_request": start_review_request,
            "deployment_failure_request": deployment_failure_request,
            "audit_request": audit_request,
        },
    )

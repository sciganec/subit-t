"""
SUBIT-T Encoder: Dimension-based semantic mapping.
Maps natural language to the 64-state WHO x WHAT x WHEN cyclic lattice.
"""

import json
import os
import re
from dataclasses import dataclass

from .canon import CANON, STATE_WEIGHT, _make_bits
from .core import State, Op

# Axis Order for Forward Steps
_WHO_ORDER = ["THEY", "YOU", "ME", "WE"]
_WHAT_ORDER = ["PRESERVE", "REDUCE", "EXPAND", "TRANSFORM"]
_WHEN_ORDER = ["RELEASE", "INTEGRATE", "INITIATE", "SUSTAIN"]

# Internal Dictionary (Simplified for space, but must be consistent)
_CURRENT_KW = {
    "WHO": {
        "ME": ["i ", "my ", "i'll", "let me", "i will", "i'm", "i've", "as for me", "myself"],
        "WE": ["we ", "our ", "team", "together", "let's", "everyone", "we're", "squad", "group", "collective"],
        "YOU": ["you ", "your ", "your code", "the issue", "the bug", "review this", "the function", "examine this", "check this"],
        "THEY": ["system", "the model", "data shows", "historically", "evidence", "the pattern", "it shows"],
    },
    "WHAT": {
        "EXPAND": ["idea", "design", "draft", "brainstorm", "architecture", "document", "new approach", "proposal", "ideate", "generate"],
        "TRANSFORM": ["running", "executing", "deploying", "building", "implementing", "pipeline", "in progress", "perform", "apply"],
        "REDUCE": ["review", "analyze", "bug", "issue", "problem", "memory leak", "error", "debug", "logs", "outage", "vulnerabilit", "critique", "check", "audit", "glitch", "flaw", "defect", "examine", "inspect", "scrutinize"],
        "PRESERVE": ["log", "store", "archive", "record", "save", "remember", "document", "note", "keep"],
    },
    "WHEN": {
        "INITIATE": ["start", "begin", "first", "scratch", "initial", "kick off", "new project", "today", "opening", "commence", "launch", "trigger"],
        "SUSTAIN": ["now", "currently", "active", "working", "processing", "right now", "in progress", "asap", "presently", "forthwith"],
        "INTEGRATE": ["finish", "complete", "wrap", "close", "done", "final", "commit", "conclude", "merge", "before the release", "end", "terminate", "finalize"],
        "RELEASE": ["wait", "pause", "ready", "idle", "standby", "later", "hold", "queue", "pending"],
    },
}

_TARGET_KW = {
    "WHO": {
        "ME": ["i will", "let me", "i'll do", "on my own", "autonomously", "i can handle", "myself will"],
        "WE": ["coordinate", "align", "team effort", "collaborate", "all of us", "share", "together we", "collective effort", "squad effort"],
        "YOU": ["please review", "can you", "analyze this", "evaluate", "give feedback", "check this", "examine this", "inspect this"],
        "THEY": ["observe", "monitor", "track", "watch", "report on", "the system should", "it should"],
    },
    "WHAT": {
        "EXPAND": ["generate", "create", "draft", "propose", "design", "come up with", "write", "document", "ideate"],
        "TRANSFORM": ["run", "execute", "deploy", "ship", "implement", "apply", "perform", "launch", "build"],
        "REDUCE": ["review", "analyze", "critique", "evaluate", "check", "test", "audit", "debug", "assess", "identify", "investigate", "examine", "inspect", "scrutinize"],
        "PRESERVE": ["save", "document", "log", "store", "archive", "keep", "record", "note down"],
    },
    "WHEN": {
        "INITIATE": ["start", "begin", "fresh", "restart", "from scratch", "new", "reset", "kick off", "opening", "commence", "initiate", "trigger"],
        "SUSTAIN": ["now", "immediately", "right away", "asap", "proceed", "continue", "keep going", "right now", "presently", "forthwith"],
        "INTEGRATE": ["finish", "complete", "close", "wrap up", "finalize", "commit", "conclude", "deliver", "before the release", "end", "terminate"],
        "RELEASE": ["later", "wait", "pause", "when ready", "no rush", "hold", "queue", "standby"],
    },
    "ROLLBACK": {
        "YES": ["rollback", "revert", "undo", "go back", "reverse", "undo that", "cancel last"]
    }
}

# Signal Terms (Legacy mapped to intents)
_FACTUAL_LOOKUP_TERMS = ["what is", "tell me about", "historically", "data shows"]
_LOOKUP_VERBS = ["find", "search", "lookup", "explore"]
_REVIEW_TERMS = ["review", "critique", "feedback", "evaluate", "check this"]
_CREATION_TERMS = ["create", "generate", "new project", "fresh start"]
_BUILD_START_TERMS = ["let's build", "start implementing", "kick off", "ready to develop"]
_EXECUTION_TERMS = ["run this", "execute", "perform", "deploy now"]
_IMMEDIATE_TERMS = ["asap", "immediately", "right now", "now"]
_TEAM_TERMS = ["team", "we", "our", "all of us", "collective"]
_ROOT_CAUSE_TERMS = ["outage", "broken", "critical bug", "fixed", "incident"]
_DESIGN_COLLAB_TERMS = ["ideate", "brainstorm", "design together", "architecture", "proposal"]
_DIRECT_REQUEST_TERMS = ["you do it", "your task", "fix this"]
_START_REVIEW_TERMS = ["start review", "begin audit"]
_DEPLOYMENT_FAILURE_TERMS = ["failed build", "crash on deploy"]
_AUDIT_TERMS = ["security audit", "risk assessment", "vulnerabilit"]

def _env_flag(name: str, default: bool = False) -> bool:
    val = os.getenv(name, str(default)).lower()
    return val in ("true", "1", "yes", "on")

def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)

def _score(text: str, kw_map: dict[str, list[str]]) -> dict[str, int]:
    lowered = text.lower()
    scores = {}
    for key, words in kw_map.items():
        count = 0
        for word in words:
            pattern = rf"\b{re.escape(word.strip())}\b"
            if re.search(pattern, lowered):
                word_count = len(word.split())
                count += (word_count ** 2) * 2 if word_count > 1 else 1 
        scores[key] = count
    return scores

def _pick(scores: dict[str, int], fallback: str, priority_order: list[str] | None = None) -> tuple[str, int]:
    if not scores or all(v == 0 for v in scores.values()):
        return fallback, 0
    max_val = max(scores.values())
    candidates = [k for k, v in scores.items() if v == max_val]
    if len(candidates) == 1:
        return candidates[0], max_val
    if priority_order:
        for p in priority_order:
            if p in candidates:
                return p, max_val
    return candidates[0], max_val

def _boost(scores: dict[str, int], key: str, amount: int):
    if key in scores:
        scores[key] += amount
    else:
        scores[key] = amount

def _to_distribution(scores: dict[str, int]) -> dict[str, float]:
    total = sum(scores.values())
    if total == 0:
        return {k: 1.0 / len(scores) for k in scores.keys()}
    return {k: v / total for k, v in scores.items()}

def _forward_steps(order, current, target):
    return (order.index(target) - order.index(current)) % len(order)

def _detect_intents(lowered: str) -> dict:
    review_request = _contains_any(lowered, _REVIEW_TERMS)
    design_collab_request = _contains_any(lowered, _DESIGN_COLLAB_TERMS)
    build_start_request = _contains_any(lowered, _BUILD_START_TERMS)
    incident_request = _contains_any(lowered, _ROOT_CAUSE_TERMS)
    audit_request = _contains_any(lowered, _AUDIT_TERMS)
    creation_request = _contains_any(lowered, _CREATION_TERMS)
    execution_request = _contains_any(lowered, _EXECUTION_TERMS)
    immediate_request = _contains_any(lowered, _IMMEDIATE_TERMS)
    factual_lookup = _contains_any(lowered, _FACTUAL_LOOKUP_TERMS) and _contains_any(lowered, _LOOKUP_VERBS)
    team_request = _contains_any(lowered, _TEAM_TERMS)
    rollback_score = sum(1 for w in _TARGET_KW["ROLLBACK"]["YES"] if w in lowered)
    
    return {
        "review_request": review_request,
        "design_collab_request": design_collab_request,
        "build_start_request": build_start_request,
        "incident_request": incident_request,
        "audit_request": audit_request,
        "creation_request": creation_request,
        "execution_request": execution_request,
        "immediate_request": immediate_request,
        "factual_lookup": factual_lookup,
        "team_request": team_request,
        "rollback_score": rollback_score,
        "rollback_detected": rollback_score > 0
    }

def _apply_adjustments(who_scores, what_scores, when_scores, intents):
    if intents["review_request"] or intents["incident_request"]:
        _boost(what_scores, "REDUCE", 3)
    if intents["design_collab_request"]:
        _boost(what_scores, "EXPAND", 3)
    if intents["creation_request"]:
        _boost(what_scores, "EXPAND", 4)
    if intents["execution_request"]:
        _boost(what_scores, "TRANSFORM", 4)
    if intents["team_request"]:
        _boost(who_scores, "WE", 2)
    if intents["rollback_detected"]:
        _boost(what_scores, "EXPAND", 3)
    if intents["review_request"] and intents["team_request"]:
        _boost(who_scores, "WE", 4)
        _boost(what_scores, "REDUCE", 4)

    if who_scores.get("YOU", 0) > 2:
        who_scores["ME"] = max(0, who_scores.get("ME", 0) - 4)
    if who_scores.get("WE", 0) > 2:
        who_scores["ME"] = max(0, who_scores.get("ME", 0) - 4)
        who_scores["YOU"] = max(0, who_scores.get("YOU", 0) - 2)
    if what_scores.get("TRANSFORM", 0) > 2:
        what_scores["EXPAND"] = max(0, what_scores.get("EXPAND", 0) - 4)
    if what_scores.get("REDUCE", 0) > 2:
        what_scores["EXPAND"] = max(0, what_scores.get("EXPAND", 0) - 4)

def _determine_operator(
    *,
    diffs,
    who_target_scores,
    what_cur_scores,
    what_target_scores,
    when_cur_scores,
    when_target_scores,
    review_request,
    design_collab_request,
    build_start_request,
    incident_request,
    audit_request,
    creation_request,
    execution_request,
    immediate_request,
    rollback_detected,
    rollback_score,
    factual_lookup,
    team_request=False,
    **kwargs
) -> tuple[Op, str, float, str]:
    if factual_lookup and rollback_score > 0:
        return Op.INV, "ALL", 1.0, "factual_lookup_grounding"
    if rollback_score > 0:
        return Op.INV, "ALL", 1.0, "explicit_rollback"

    if diffs:
        chosen = min(diffs, key=lambda item: (item["steps"], {"WHO": 0, "WHAT": 1, "WHEN": 2}[item["axis"]]))
        if execution_request and immediate_request and any(d["axis"] == "WHEN" for d in diffs):
            chosen = next(d for d in diffs if d["axis"] == "WHEN")
            reason = "immediate_prefers_when"
        elif review_request and any(d["axis"] == "WHAT" for d in diffs):
            chosen = next(d for d in diffs if d["axis"] == "WHAT")
            reason = "review_prefers_what"
        elif build_start_request and any(d["axis"] == "WHEN" for d in diffs):
            chosen = next(d for d in diffs if d["axis"] == "WHEN")
            reason = "build_start_prefers_when"
        elif creation_request and any(d["axis"] == "WHAT" for d in diffs):
            chosen = next(d for d in diffs if d["axis"] == "WHAT")
            reason = "creation_prefers_what"
        elif design_collab_request and any(d["axis"] == "WHAT" for d in diffs):
            chosen = next(d for d in diffs if d["axis"] == "WHAT")
            reason = "design_prefers_what"
        else:
            reason = f"closest_axis_{chosen['axis'].lower()}"
        return Op(chosen["op"]), chosen["axis"], (1.0 if chosen["steps"] == 1 else 0.75), reason

    cycle_priority = [Op.WHAT_SHIFT, Op.WHEN_SHIFT, Op.WHO_SHIFT]
    signals = {
        Op.WHO_SHIFT: sum(who_target_scores.values()),
        Op.WHAT_SHIFT: sum(what_target_scores.values()) + sum(what_cur_scores.values()),
        Op.WHEN_SHIFT: sum(when_target_scores.values()) + sum(when_cur_scores.values()),
    }
    if review_request: signals[Op.WHAT_SHIFT] += 8
    if build_start_request: signals[Op.WHEN_SHIFT] += 8
    if audit_request: signals[Op.WHAT_SHIFT] += 10
    op = max(cycle_priority, key=lambda o: (signals[o], -cycle_priority.index(o)))
    return op, op.value.removesuffix("_SHIFT"), 0.5, "signal_fallback"

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
    model_assisted: bool
    model_reason: str | None

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
            "model_assisted": self.model_assisted,
            "model_reason": self.model_reason,
            "operator_distribution": self.operator_distribution,
            "distributions": {
                "who": self.who_dist,
                "what": self.what_dist,
                "when": self.when_dist,
            },
            "state_distribution": self.state_distribution,
        }

def encode(text: str, *, model_assisted: bool | None = None, model: str | None = None, timeout: int = 20) -> EncoderResult:
    lowered = text.lower()
    if model_assisted is None:
        model_assisted = _env_flag("SUBIT_ENCODER_MODEL_ASSISTED", default=False)
    
    who_cur_scores = _score(lowered, _CURRENT_KW["WHO"])
    what_cur_scores = _score(lowered, _CURRENT_KW["WHAT"])
    when_cur_scores = _score(lowered, _CURRENT_KW["WHEN"])

    intents = _detect_intents(lowered)
    _apply_adjustments(who_cur_scores, what_cur_scores, when_cur_scores, intents)

    who_cur, _ = _pick(who_cur_scores, "ME", priority_order=["YOU", "WE", "THEY", "ME"])
    what_cur, _ = _pick(what_cur_scores, "EXPAND", priority_order=["TRANSFORM", "REDUCE", "EXPAND", "PRESERVE"])
    when_cur, _ = _pick(when_cur_scores, "SUSTAIN", priority_order=["SUSTAIN", "INITIATE", "INTEGRATE", "RELEASE"])

    who_target_scores = _score(lowered, _TARGET_KW["WHO"])
    what_target_scores = _score(lowered, _TARGET_KW["WHAT"])
    when_target_scores = _score(lowered, _TARGET_KW["WHEN"])

    who_target, _ = _pick(who_target_scores, who_cur, priority_order=["YOU", "WE", "THEY", "ME"])
    what_target, _ = _pick(what_target_scores, what_cur, priority_order=["TRANSFORM", "REDUCE", "EXPAND", "PRESERVE"])
    when_target, _ = _pick(when_target_scores, when_cur, priority_order=["SUSTAIN", "INITIATE", "INTEGRATE", "RELEASE"])

    current_state = State(_make_bits(who_cur, what_cur, when_cur))
    diffs = []
    who_steps = _forward_steps(_WHO_ORDER, who_cur, who_target)
    if who_steps: diffs.append({"axis": "WHO", "op": Op.WHO_SHIFT.value, "steps": who_steps})
    what_steps = _forward_steps(_WHAT_ORDER, what_cur, what_target)
    if what_steps: diffs.append({"axis": "WHAT", "op": Op.WHAT_SHIFT.value, "steps": what_steps})
    when_steps = _forward_steps(_WHEN_ORDER, when_cur, when_target)
    if when_steps: diffs.append({"axis": "WHEN", "op": Op.WHEN_SHIFT.value, "steps": when_steps})

    operator, axis_diff, op_confidence, routing_reason = _determine_operator(
        diffs=diffs,
        who_target_scores=who_target_scores,
        what_cur_scores=what_cur_scores,
        what_target_scores=what_target_scores,
        when_cur_scores=when_cur_scores,
        when_target_scores=when_target_scores,
        **intents
    )

    next_state = current_state.apply(operator).result
    who_dist = _to_distribution(who_cur_scores)
    what_dist = _to_distribution(what_cur_scores)
    when_dist = _to_distribution(when_cur_scores)

    state_scores = {entry[3]: who_dist.get(entry[0], 0)*what_dist.get(entry[1], 0)*when_dist.get(entry[2], 0)*STATE_WEIGHT.get(entry[3],0.5) for bits, entry in CANON.items()}
    total = sum(state_scores.values()) or 1.0
    state_distribution = {k: v/total for k,v in sorted(state_scores.items(), key=lambda x: x[1], reverse=True)[:16]}

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
        operator_distribution={},
        state_distribution=state_distribution,
        dominant_state_bits=current_state.bits,
        routing_reason=routing_reason,
        signal_summary=intents,
        model_assisted=False,
        model_reason=None
    )

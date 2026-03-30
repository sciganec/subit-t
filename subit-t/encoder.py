"""
SUBIT-T Encoder — text → (State, Op)

Two-phase approach:
  Phase 1: determine current state  (where is the agent now)
  Phase 2: determine target state   (where should it go)
  Phase 3: operator = axis that differs between current and target

This avoids the idempotent problem of single-phase encoding where
the operator is derived from the same signal as the state.
"""

from __future__ import annotations
from dataclasses import dataclass

from .canon import CANON, _make_bits, WHO, WHERE, WHEN
from .core import State, Op


# ─────────────────────────────────────────────
# Keyword tables
# ─────────────────────────────────────────────

_CURRENT_KW: dict[str, dict[str, list[str]]] = {
    "WHO": {
        "ME":   ["i ", "my ", "i'll", "let me", "i will", "i'm", "i've"],
        "WE":   ["we ", "our ", "team", "together", "let's", "everyone", "we're"],
        "YOU":  ["you ", "your ", "this code", "the issue", "the bug", "review this", "the function"],
        "THEY": ["system", "the model", "data shows", "historically", "evidence", "the pattern"],
    },
    "WHERE": {
        "EAST":  ["idea", "design", "draft", "brainstorm", "architecture", "document", "new approach", "proposal"],
        "SOUTH": ["running", "executing", "deploying", "building", "implementing", "pipeline", "in progress"],
        "WEST":  ["review", "analyze", "bug", "issue", "problem", "memory leak", "error", "debug",
                  "logs", "outage", "vulnerabilit", "critique", "check", "audit"],
        "NORTH": ["log", "store", "archive", "record", "save", "remember", "document", "note"],
    },
    "WHEN": {
        "SPRING": ["start", "begin", "first", "scratch", "initial", "kick off", "new project", "today", "opening"],
        "SUMMER": ["now", "currently", "active", "working", "processing", "right now", "in progress", "asap"],
        "AUTUMN": ["finish", "complete", "wrap", "close", "done", "final", "commit",
                   "conclude", "merge", "pending", "before the release"],
        "WINTER": ["wait", "pause", "ready", "idle", "standby", "later", "hold", "queue", "pending"],
    },
}

_TARGET_KW: dict[str, dict[str, list[str]]] = {
    "WHO": {
        "ME":   ["i will", "let me", "i'll do", "on my own", "autonomously", "i can handle"],
        "WE":   ["coordinate", "align", "team effort", "collaborate", "all of us", "share", "together we"],
        "YOU":  ["please review", "can you", "analyze this", "evaluate", "give feedback", "check this"],
        "THEY": ["observe", "monitor", "track", "watch", "report on", "the system should"],
    },
    "WHERE": {
        "EAST":  ["generate", "create", "draft", "propose", "design", "come up with", "write", "document"],
        "SOUTH": ["run", "execute", "deploy", "ship", "implement", "apply", "perform", "launch", "build"],
        "WEST":  ["review", "analyze", "critique", "evaluate", "check", "test", "audit",
                  "debug", "assess", "identify", "investigate"],
        "NORTH": ["save", "document", "log", "store", "archive", "keep", "record", "note down"],
    },
    "WHEN": {
        "SPRING": ["start", "begin", "fresh", "restart", "from scratch", "new", "reset", "kick off", "opening"],
        "SUMMER": ["now", "immediately", "right away", "asap", "proceed", "continue", "keep going", "right now"],
        "AUTUMN": ["finish", "complete", "close", "wrap up", "finalize", "commit",
                   "conclude", "deliver", "before the release", "pending changes"],
        "WINTER": ["later", "wait", "pause", "when ready", "no rush", "hold", "queue", "standby"],
    },
}


# ─────────────────────────────────────────────
# Scoring
# ─────────────────────────────────────────────

def _score(text: str, kw_map: dict[str, list[str]]) -> dict[str, int]:
    t = text.lower()
    return {k: sum(1 for w in kws if w in t) for k, kws in kw_map.items()}


def _pick(scores: dict[str, int], fallback: str) -> tuple[str, int]:
    """Returns (best_key, max_score)."""
    m = max(scores.values())
    if m == 0:
        return fallback, 0
    return max(scores, key=scores.get), m


def _to_distribution(scores: dict[str, int]) -> dict[str, float]:
    """Normalize scores to probability distribution with a small floor."""
    floor = 0.05
    total = sum(scores.values()) or 1
    raw = {k: floor + (v / total) * (1 - floor * len(scores)) for k, v in scores.items()}
    s = sum(raw.values())
    return {k: v / s for k, v in raw.items()}


# ─────────────────────────────────────────────
# EncoderResult
# ─────────────────────────────────────────────

@dataclass
class EncoderResult:
    current_state:  State
    target_state:   State
    operator:       Op
    axis_diff:      str          # which axis differs: WHO / WHERE / WHEN
    all_diffs:      list[dict]   # all differing axes
    who_dist:       dict[str, float]
    where_dist:     dict[str, float]
    when_dist:      dict[str, float]
    op_confidence:  float        # 1.0 if diff found, 0.5 if fallback

    def to_dict(self) -> dict:
        return {
            "current_state":  self.current_state.to_dict(),
            "target_state":   self.target_state.to_dict(),
            "dominant_state": self.current_state.name,
            "operator":       self.operator.value,
            "axis_diff":      self.axis_diff,
            "op_confidence":  self.op_confidence,
            "distributions": {
                "who":   self.who_dist,
                "where": self.where_dist,
                "when":  self.when_dist,
            },
        }


# ─────────────────────────────────────────────
# Encoder
# ─────────────────────────────────────────────

def encode(text: str) -> EncoderResult:
    """
    Two-phase encoder: text → (current_state, target_state, operator)

    Phase 1 — current state: where is the agent right now?
    Phase 2 — target state:  where should the agent go?
    Phase 3 — operator:      which axis differs? → pick operator for that axis.
    """
    t = text.lower()

    # ── Phase 1: current state ───────────────────
    who_cur_s   = _score(t, _CURRENT_KW["WHO"])
    where_cur_s = _score(t, _CURRENT_KW["WHERE"])
    when_cur_s  = _score(t, _CURRENT_KW["WHEN"])

    who_cur,   _ = _pick(who_cur_s,   "ME")
    where_cur, _ = _pick(where_cur_s, "EAST")
    when_cur,  _ = _pick(when_cur_s,  "SUMMER")

    # ── Phase 2: target state ────────────────────
    who_tgt_s   = _score(t, _TARGET_KW["WHO"])
    where_tgt_s = _score(t, _TARGET_KW["WHERE"])
    when_tgt_s  = _score(t, _TARGET_KW["WHEN"])

    who_tgt,   _ = _pick(who_tgt_s,   who_cur)
    where_tgt, _ = _pick(where_tgt_s, where_cur)
    when_tgt,  _ = _pick(when_tgt_s,  when_cur)

    # ── Phase 3: operator from axis difference ───
    # Priority: WHO > WHEN > WHERE
    diffs = []
    if who_tgt != who_cur:
        diffs.append({"axis": "WHO",   "op": "MERGE",  "from": who_cur,   "to": who_tgt})
    if when_tgt != when_cur:
        op_name = "INIT" if when_tgt == "SPRING" else "ACT"
        diffs.append({"axis": "WHEN",  "op": op_name,  "from": when_cur,  "to": when_tgt})
    if where_tgt != where_cur:
        diffs.append({"axis": "WHERE", "op": "EXPAND", "from": where_cur, "to": where_tgt})

    if diffs:
        chosen_diff = diffs[0]
        op = Op(chosen_diff["op"])
        axis_diff = chosen_diff["axis"]
        op_confidence = 1.0
    else:
        # No difference found — apply fallback
        # If WE signal present → MERGE, else → INIT
        we_score = who_cur_s.get("WE", 0)
        if we_score > 0:
            op = Op.MERGE
            who_tgt = "WE"
            axis_diff = "WHO"
        else:
            op = Op.INIT
            when_tgt = "SPRING"
            axis_diff = "WHEN"
        op_confidence = 0.5

    cur_bits = (WHO[who_cur] << 4) | (WHERE[where_cur] << 2) | WHEN[when_cur]
    tgt_bits = (WHO[who_tgt] << 4) | (WHERE[where_tgt] << 2) | WHEN[when_tgt]

    cur_entry = CANON.get(cur_bits)
    tgt_entry = CANON.get(tgt_bits)

    cur_state = State(cur_bits) if cur_entry else State.from_dims(who_cur, where_cur, when_cur)
    tgt_state = State(tgt_bits) if tgt_entry else State.from_dims(who_tgt, where_tgt, when_tgt)

    return EncoderResult(
        current_state=cur_state,
        target_state=tgt_state,
        operator=op,
        axis_diff=axis_diff,
        all_diffs=diffs,
        who_dist=_to_distribution(who_cur_s),
        where_dist=_to_distribution(where_cur_s),
        when_dist=_to_distribution(when_cur_s),
        op_confidence=op_confidence,
    )

"""
SUBIT-T Core — State, Operator, TransitionResult.

State:  64-state space (6-bit integer)
Op:     4 semantic operators, each mutates exactly one axis
apply:  deterministic transition, 256 entries total
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .canon import (
    WHO, WHERE, WHEN, WHO_I, WHERE_I, WHEN_I,
    WHO_LABEL, WHERE_LABEL, WHEN_LABEL,
    CANON, BY_NAME, _make_bits,
)


# ─────────────────────────────────────────────
# Operator
# ─────────────────────────────────────────────

class Op(str, Enum):
    """
    Four semantic operators — each mutates exactly one axis.

    INIT   → WHEN  = SPRING   restart phase, re-initiate
    EXPAND → WHERE = SOUTH    shift to execution domain
    MERGE  → WHO   = WE       expand scope to collective
    ACT    → WHEN  = AUTUMN   close current phase
    """
    INIT   = "INIT"
    EXPAND = "EXPAND"
    MERGE  = "MERGE"
    ACT    = "ACT"

    @property
    def symbol(self) -> str:
        return {"INIT": "⊕", "EXPAND": "⊗", "MERGE": "⊞", "ACT": "⊖"}[self.value]

    @property
    def axis(self) -> str:
        return {"INIT": "WHEN", "EXPAND": "WHERE", "MERGE": "WHO", "ACT": "WHEN"}[self.value]

    @property
    def target_value(self) -> str:
        return {"INIT": "SPRING", "EXPAND": "SOUTH", "MERGE": "WE", "ACT": "AUTUMN"}[self.value]

    @property
    def description(self) -> str:
        return {
            "INIT":   "restart phase  → WHEN=SPRING",
            "EXPAND": "shift domain   → WHERE=SOUTH",
            "MERGE":  "expand scope   → WHO=WE",
            "ACT":    "close phase    → WHEN=AUTUMN",
        }[self.value]


# ─────────────────────────────────────────────
# State
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class State:
    """
    Immutable 6-bit SUBIT-T state.
    Encodes WHO × WHERE × WHEN as a single integer (0–63).
    """
    bits: int

    def __post_init__(self):
        if not (0 <= self.bits <= 63):
            raise ValueError(f"State bits must be 0–63, got {self.bits}")

    # ── Dimensions ──────────────────────────────

    @property
    def who(self) -> str:   return WHO_I[(self.bits >> 4) & 0b11]
    @property
    def where(self) -> str: return WHERE_I[(self.bits >> 2) & 0b11]
    @property
    def when(self) -> str:  return WHEN_I[self.bits & 0b11]

    @property
    def name(self) -> str:
        e = CANON.get(self.bits)
        return e[3] if e else f"RAW_{self.bits:06b}"

    # ── Core operation ───────────────────────────

    def apply(self, op: Op) -> "TransitionResult":
        """
        Apply operator — mutates exactly one axis.
        Idempotent if axis already at target value.
        """
        who_v, where_v, when_v = self.who, self.where, self.when

        if op == Op.INIT:
            idempotent = (when_v == "SPRING")
            when_v = "SPRING"
        elif op == Op.EXPAND:
            idempotent = (where_v == "SOUTH")
            where_v = "SOUTH"
        elif op == Op.MERGE:
            idempotent = (who_v == "WE")
            who_v = "WE"
        elif op == Op.ACT:
            idempotent = (when_v == "AUTUMN")
            when_v = "AUTUMN"
        else:
            raise ValueError(f"Unknown operator: {op}")

        new_bits = _make_bits(who_v, where_v, when_v)
        return TransitionResult(
            source=self,
            operator=op,
            result=State(new_bits),
            axis_changed=op.axis,
            old_value=getattr(self, op.axis.lower()),
            new_value=op.target_value,
            idempotent=idempotent,
        )

    def apply_chain(self, ops: list[Op]) -> list["TransitionResult"]:
        """Apply a sequence of operators, feeding each result into the next."""
        results, current = [], self
        for op in ops:
            tr = current.apply(op)
            results.append(tr)
            current = tr.result
        return results

    # ── Constructors ─────────────────────────────

    @classmethod
    def from_dims(cls, who: str, where: str, when: str) -> "State":
        return cls(_make_bits(who, where, when))

    @classmethod
    def from_name(cls, name: str) -> "State":
        key = name.upper()
        if key not in BY_NAME:
            raise KeyError(f"Unknown state: '{name}'. Valid names: {list(BY_NAME)[:5]}...")
        return cls(BY_NAME[key])

    @classmethod
    def from_binary(cls, s: str) -> "State":
        clean = s.replace("·", "").replace(" ", "").replace("-", "")
        return cls(int(clean, 2))

    # ── Geometry (v1 XOR — kept for analysis) ────

    def __xor__(self, other: "State") -> "State":
        """XOR as latent geometry tool. Not used for routing in v2."""
        return State(self.bits ^ other.bits)

    # ── Representations ──────────────────────────

    def to_dict(self) -> dict:
        return {
            "name": self.name, "bits": self.bits,
            "binary": f"{self.bits:06b}",
            "who": self.who, "where": self.where, "when": self.when,
            "who_label":   WHO_LABEL[self.who],
            "where_label": WHERE_LABEL[self.where],
            "when_label":  WHEN_LABEL[self.when],
        }

    def __repr__(self) -> str:
        return f"State({self.name} | {self.who}·{self.where}·{self.when} | {self.bits:06b})"
    def __str__(self)  -> str: return self.name
    def __int__(self)  -> int: return self.bits
    def __eq__(self, o) -> bool:
        if isinstance(o, State): return self.bits == o.bits
        if isinstance(o, int):   return self.bits == o
        return NotImplemented
    def __hash__(self) -> int: return hash(self.bits)


# ─────────────────────────────────────────────
# TransitionResult
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class TransitionResult:
    source:       State
    operator:     Op
    result:       State
    axis_changed: str
    old_value:    str
    new_value:    str
    idempotent:   bool

    def __str__(self) -> str:
        tag = " [no-op]" if self.idempotent else ""
        return (
            f"{self.source.name} {self.operator.symbol}({self.operator.value}) "
            f"→ {self.result.name}"
            f"  [{self.axis_changed}: {self.old_value}→{self.new_value}]{tag}"
        )

    def to_dict(self) -> dict:
        return {
            "source":       self.source.to_dict(),
            "operator":     self.operator.value,
            "symbol":       self.operator.symbol,
            "result":       self.result.to_dict(),
            "axis_changed": self.axis_changed,
            "old_value":    self.old_value,
            "new_value":    self.new_value,
            "idempotent":   self.idempotent,
        }


# ─────────────────────────────────────────────
# Prebuilt constants
# ─────────────────────────────────────────────

def _s(name: str) -> State:
    return State.from_name(name)

S_PRIME    = _s("PRIME")
S_SYNC     = _s("SYNC")
S_SCAN     = _s("SCAN")
S_CORE     = _s("CORE")
S_DRIVER   = _s("DRIVER")
S_EXECUTOR = _s("EXECUTOR")
S_MONITOR  = _s("MONITOR")
S_DAEMON   = _s("DAEMON")
S_COUNCIL  = _s("COUNCIL")
S_GHOST    = _s("GHOST")
S_SENTINEL = _s("SENTINEL")


# ─────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────

def validate_all_transitions() -> list[dict]:
    """Verify all 256 transitions are semantically valid. Returns violations."""
    violations = []
    for bits in range(64):
        s = State(bits)
        for op in Op:
            tr = s.apply(op)
            r  = tr.result
            if op == Op.INIT   and r.when  != "SPRING": violations.append({"state": s.name, "op": op.value, "issue": f"WHEN={r.when}, expected SPRING"})
            if op == Op.EXPAND and r.where != "SOUTH":  violations.append({"state": s.name, "op": op.value, "issue": f"WHERE={r.where}, expected SOUTH"})
            if op == Op.MERGE  and r.who   != "WE":     violations.append({"state": s.name, "op": op.value, "issue": f"WHO={r.who}, expected WE"})
            if op == Op.ACT    and r.when  != "AUTUMN": violations.append({"state": s.name, "op": op.value, "issue": f"WHEN={r.when}, expected AUTUMN"})
            if op in (Op.INIT, Op.ACT) and (r.who != s.who or r.where != s.where):
                violations.append({"state": s.name, "op": op.value, "issue": "WHEN-op changed WHO or WHERE"})
            if op == Op.EXPAND and (r.who != s.who or r.when != s.when):
                violations.append({"state": s.name, "op": op.value, "issue": "WHERE-op changed WHO or WHEN"})
            if op == Op.MERGE and (r.where != s.where or r.when != s.when):
                violations.append({"state": s.name, "op": op.value, "issue": "WHO-op changed WHERE or WHEN"})
    return violations

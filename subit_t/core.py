"""
SUBIT-T Core - State, Operator, TransitionResult.

State: 64-state space (6-bit integer)
Op: 4 semantic operators, each mutates exactly one axis
apply: deterministic transition, 256 entries total
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .canon import (
    WHO,
    WHAT,
    WHEN,
    WHO_I,
    WHAT_I,
    WHEN_I,
    WHO_LABEL,
    WHAT_LABEL,
    WHEN_LABEL,
    STATE_TYPE,
    STATE_WEIGHT,
    CANON,
    BY_NAME,
    _make_bits,
)


class Op(str, Enum):
    """
    Four v3 operators in cyclic algebra.

    WHO_SHIFT  -> rotate WHO forward by 1
    WHAT_SHIFT -> rotate WHAT forward by 1
    WHEN_SHIFT -> rotate WHEN forward by 1
    INV        -> rotate all axes backward by 1
    """

    WHO_SHIFT = "WHO_SHIFT"
    WHAT_SHIFT = "WHAT_SHIFT"
    WHEN_SHIFT = "WHEN_SHIFT"
    INV = "INV"

    @property
    def symbol(self) -> str:
        return {
            "WHO_SHIFT": "W",
            "WHAT_SHIFT": "T",
            "WHEN_SHIFT": "N",
            "INV": "I",
        }[self.value]

    @property
    def axis(self) -> str:
        return {
            "WHO_SHIFT": "WHO",
            "WHAT_SHIFT": "WHAT",
            "WHEN_SHIFT": "WHEN",
            "INV": "ALL",
        }[self.value]

    @property
    def target_value(self) -> str:
        return {
            "WHO_SHIFT": "NEXT",
            "WHAT_SHIFT": "NEXT",
            "WHEN_SHIFT": "NEXT",
            "INV": "PREVIOUS_ALL",
        }[self.value]

    @property
    def description(self) -> str:
        return {
            "WHO_SHIFT": "cyclic forward shift on WHO",
            "WHAT_SHIFT": "cyclic forward shift on WHAT",
            "WHEN_SHIFT": "cyclic forward shift on WHEN",
            "INV": "global rollback by one step on all axes",
        }[self.value]


@dataclass(frozen=True)
class State:
    """
    Immutable 6-bit SUBIT-T state.
    Encodes WHO x WHAT x WHEN as a single integer (0-63).
    """

    bits: int

    _WHO_ORDER = ["THEY", "YOU", "ME", "WE"]
    _WHAT_ORDER = ["PRESERVE", "REDUCE", "EXPAND", "TRANSFORM"]
    _WHEN_ORDER = ["RELEASE", "INTEGRATE", "INITIATE", "SUSTAIN"]

    def __post_init__(self):
        if not (0 <= self.bits <= 63):
            raise ValueError(f"State bits must be 0-63, got {self.bits}")

    @property
    def who(self) -> str:
        return WHO_I[(self.bits >> 4) & 0b11]

    @property
    def what(self) -> str:
        return WHAT_I[(self.bits >> 2) & 0b11]

    @property
    def where(self) -> str:
        return self.what

    @property
    def when(self) -> str:
        return WHEN_I[self.bits & 0b11]

    @property
    def name(self) -> str:
        entry = CANON.get(self.bits)
        return entry[3] if entry else f"RAW_{self.bits:06b}"

    @property
    def state_type(self) -> str:
        return STATE_TYPE.get(self.name, "unknown")

    @property
    def state_weight(self) -> float:
        return STATE_WEIGHT.get(self.name, 0.5)

    def apply(self, op: Op) -> "TransitionResult":
        """Apply a v3 operator using cyclic shifts modulo 4."""
        who_v, what_v, when_v = self.who, self.what, self.when

        if op == Op.WHO_SHIFT:
            who_v = self._shift(self._WHO_ORDER, who_v, 1)
            axis_changed = "WHO"
            old_value = self.who
            new_value = who_v
        elif op == Op.WHAT_SHIFT:
            what_v = self._shift(self._WHAT_ORDER, what_v, 1)
            axis_changed = "WHAT"
            old_value = self.what
            new_value = what_v
        elif op == Op.WHEN_SHIFT:
            when_v = self._shift(self._WHEN_ORDER, when_v, 1)
            axis_changed = "WHEN"
            old_value = self.when
            new_value = when_v
        elif op == Op.INV:
            who_v = self._shift(self._WHO_ORDER, who_v, -1)
            what_v = self._shift(self._WHAT_ORDER, what_v, -1)
            when_v = self._shift(self._WHEN_ORDER, when_v, -1)
            axis_changed = "ALL"
            old_value = f"{self.who}.{self.what}.{self.when}"
            new_value = f"{who_v}.{what_v}.{when_v}"
        else:
            raise ValueError(f"Unknown operator: {op}")

        new_bits = _make_bits(who_v, what_v, when_v)
        return TransitionResult(
            source=self,
            operator=op,
            result=State(new_bits),
            axis_changed=axis_changed,
            old_value=old_value,
            new_value=new_value,
            idempotent=False,
        )

    def apply_chain(self, ops: list[Op]) -> list["TransitionResult"]:
        """Apply a sequence of operators, feeding each result into the next."""
        results: list[TransitionResult] = []
        current = self
        for op in ops:
            transition = current.apply(op)
            results.append(transition)
            current = transition.result
        return results

    @classmethod
    def from_dims(cls, who: str, what: str, when: str) -> "State":
        return cls(_make_bits(who, what, when))

    @classmethod
    def from_name(cls, name: str) -> "State":
        key = name.upper()
        if key not in BY_NAME:
            raise KeyError(f"Unknown state: '{name}'. Valid names: {list(BY_NAME)[:5]}...")
        return cls(BY_NAME[key])

    @classmethod
    def from_binary(cls, value: str) -> "State":
        clean = value.replace(".", "").replace(" ", "").replace("-", "")
        return cls(int(clean, 2))

    def __xor__(self, other: "State") -> "State":
        """XOR kept as a latent geometry tool for compatibility analysis."""
        return State(self.bits ^ other.bits)

    @staticmethod
    def _shift(order: list[str], value: str, delta: int) -> str:
        index = order.index(value)
        return order[(index + delta) % len(order)]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "bits": self.bits,
            "binary": f"{self.bits:06b}",
            "who": self.who,
            "what": self.what,
            "when": self.when,
            "where": self.what,
            "who_label": WHO_LABEL[self.who],
            "what_label": WHAT_LABEL[self.what],
            "when_label": WHEN_LABEL[self.when],
            "state_type": self.state_type,
            "state_weight": self.state_weight,
        }

    def __repr__(self) -> str:
        return f"State({self.name} | {self.who}.{self.what}.{self.when} | {self.bits:06b})"

    def __str__(self) -> str:
        return self.name

    def __int__(self) -> int:
        return self.bits

    def __eq__(self, other) -> bool:
        if isinstance(other, State):
            return self.bits == other.bits
        if isinstance(other, int):
            return self.bits == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.bits)


@dataclass(frozen=True)
class TransitionResult:
    source: State
    operator: Op
    result: State
    axis_changed: str
    old_value: str
    new_value: str
    idempotent: bool

    def __str__(self) -> str:
        tag = " [no-op]" if self.idempotent else ""
        return (
            f"{self.source.name} {self.operator.symbol}({self.operator.value}) "
            f"-> {self.result.name} [{self.axis_changed}: {self.old_value}->{self.new_value}]{tag}"
        )

    def to_dict(self) -> dict:
        return {
            "source": self.source.to_dict(),
            "operator": self.operator.value,
            "symbol": self.operator.symbol,
            "result": self.result.to_dict(),
            "axis_changed": self.axis_changed,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "idempotent": self.idempotent,
        }


def _s(name: str) -> State:
    return State.from_name(name)


S_PRIME = _s("PRIME")
S_SYNC = _s("SYNC")
S_SCAN = _s("SCAN")
S_CORE = _s("CORE")
S_DRIVER = _s("DRIVER")
S_EXECUTOR = _s("EXECUTOR")
S_MONITOR = _s("MONITOR")
S_DAEMON = _s("DAEMON")
S_COUNCIL = _s("COUNCIL")
S_GHOST = _s("GHOST")
S_SENTINEL = _s("SENTINEL")


def validate_all_transitions() -> list[dict]:
    """Verify all v3 transitions are semantically valid."""
    violations = []
    for bits in range(64):
        state = State(bits)
        for op in Op:
            transition = state.apply(op)
            result = transition.result
            if transition.idempotent:
                violations.append({"state": state.name, "op": op.value, "issue": "v3 transitions must never be idempotent"})
            if op == Op.WHO_SHIFT and (result.what != state.what or result.when != state.when):
                violations.append({"state": state.name, "op": op.value, "issue": "WHO_SHIFT changed WHAT or WHEN"})
            if op == Op.WHAT_SHIFT and (result.who != state.who or result.when != state.when):
                violations.append({"state": state.name, "op": op.value, "issue": "WHAT_SHIFT changed WHO or WHEN"})
            if op == Op.WHEN_SHIFT and (result.who != state.who or result.what != state.what):
                violations.append({"state": state.name, "op": op.value, "issue": "WHEN_SHIFT changed WHO or WHAT"})
            if op == Op.INV and result == state:
                violations.append({"state": state.name, "op": op.value, "issue": "INV must move the agent"})
    return violations

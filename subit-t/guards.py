"""
SUBIT-T Guards — soft intercepts for semantically invalid transitions.

Three confirmed problem cases where v1 XOR produces incoherent routing:
  DRIVER   ⊕ SYNC  → VOID    (active executor collapses to null)
  EXECUTOR ⊕ SCAN  → SHADOW  (reactive executor becomes hidden threat)
  COUNCIL  ⊕ PRIME → QUEUE   (collective analysis collapses to passive queue)

Root cause: XOR flips WHEN to WINTER (idle) when context demands active phase.

Guards are only relevant when using v1 XOR routing (kept for compatibility).
v2 operator routing does not require guards.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional
from .core import State, Op


@dataclass
class GuardResult:
    triggered:   bool
    original:    State
    replacement: State
    reason:      str


GuardFn = Callable[[State, State, State], Optional[GuardResult]]


def _s(name: str) -> State:
    return State.from_name(name)


# ── Three specific guards ─────────────────────────────────────────────────────

def guard_driver_sync(current: State, impulse: State, result: State) -> Optional[GuardResult]:
    """DRIVER ⊕ SYNC → VOID  →  reroute to COMMIT."""
    if current.name == "DRIVER" and impulse.name == "SYNC":
        return GuardResult(True, result, _s("COMMIT"),
            "DRIVER absorbed by SYNC → VOID prevented; rerouted to COMMIT")
    return None


def guard_executor_scan(current: State, impulse: State, result: State) -> Optional[GuardResult]:
    """EXECUTOR ⊕ SCAN → SHADOW  →  reroute to FILTER."""
    if current.name == "EXECUTOR" and impulse.name == "SCAN":
        return GuardResult(True, result, _s("FILTER"),
            "EXECUTOR critiqued → SHADOW prevented; rerouted to FILTER")
    return None


def guard_council_prime(current: State, impulse: State, result: State) -> Optional[GuardResult]:
    """COUNCIL ⊕ PRIME → QUEUE  →  reroute to SPARK."""
    if current.name == "COUNCIL" and impulse.name == "PRIME":
        return GuardResult(True, result, _s("SPARK"),
            "COUNCIL + PRIME → QUEUE prevented; rerouted to SPARK")
    return None


def guard_winter_collapse(current: State, impulse: State, result: State) -> Optional[GuardResult]:
    """
    General guard: active + active → WINTER is always wrong.
    Exception: self-cancel (A ⊕ A = CORE) is legitimate — do not intercept.
    """
    if current == impulse:  # self-cancel is legitimate
        return None
    active = {"SPRING", "SUMMER"}
    if current.when in active and impulse.when in active and result.when == "WINTER":
        fallback_bits = (current.bits & 0b111100) | 0b11  # keep WHO+WHERE, force WHEN=SUMMER
        return GuardResult(True, result, State(fallback_bits),
            "active+active→WINTER collapse prevented; forced WHEN=SUMMER")
    return None


# ── Default guard chain ───────────────────────────────────────────────────────

DEFAULT_GUARDS: list[GuardFn] = [
    guard_driver_sync,
    guard_executor_scan,
    guard_council_prime,
    guard_winter_collapse,
]


def make_guard(trigger: tuple[str, str], fallback: str, reason: str) -> GuardFn:
    """Factory for simple exact-match guards."""
    cur_name, imp_name = trigger
    replacement = _s(fallback)

    def _guard(current: State, impulse: State, result: State) -> Optional[GuardResult]:
        if current.name == cur_name and impulse.name == imp_name:
            return GuardResult(True, result, replacement, reason)
        return None

    _guard.__name__ = f"guard_{cur_name.lower()}_{imp_name.lower()}"
    return _guard

"""SUBIT-T guards for legacy XOR compatibility analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .core import State


@dataclass
class GuardResult:
    triggered: bool
    original: State
    replacement: State
    reason: str


GuardFn = Callable[[State, State, State], Optional[GuardResult]]


def _s(name: str) -> State:
    return State.from_name(name)


def guard_driver_sync(current: State, impulse: State, result: State) -> Optional[GuardResult]:
    """Prevent DRIVER xor SYNC from collapsing into an unusable latent state."""
    if current.name == "DRIVER" and impulse.name == "SYNC":
        return GuardResult(
            True,
            result,
            _s("COMMIT"),
            "DRIVER absorbed by SYNC prevented; rerouted to COMMIT",
        )
    return None


def guard_executor_scan(current: State, impulse: State, result: State) -> Optional[GuardResult]:
    """Prevent EXECUTOR xor SCAN from collapsing into a hidden threat state."""
    if current.name == "EXECUTOR" and impulse.name == "SCAN":
        return GuardResult(
            True,
            result,
            _s("FILTER"),
            "EXECUTOR critiqued by SCAN prevented; rerouted to FILTER",
        )
    return None


def guard_council_prime(current: State, impulse: State, result: State) -> Optional[GuardResult]:
    """Prevent COUNCIL xor PRIME from collapsing into passive queueing."""
    if current.name == "COUNCIL" and impulse.name == "PRIME":
        return GuardResult(
            True,
            result,
            _s("SPARK"),
            "COUNCIL plus PRIME prevented from collapsing; rerouted to SPARK",
        )
    return None


def guard_winter_collapse(current: State, impulse: State, result: State) -> Optional[GuardResult]:
    """
    General compat guard: active + active -> RELEASE is suspicious in XOR space.

    Self-cancel is legitimate and should not be intercepted.
    """
    if current == impulse:
        return None

    active = {"INITIATE", "SUSTAIN"}
    if current.when in active and impulse.when in active and result.when == "RELEASE":
        fallback_bits = (current.bits & 0b111100) | 0b11
        return GuardResult(
            True,
            result,
            State(fallback_bits),
            "active+active->RELEASE collapse prevented; forced WHEN=SUSTAIN",
        )
    return None


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

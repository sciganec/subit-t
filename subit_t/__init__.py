"""
SUBIT-T — Archetypal routing layer for multi-agent AI systems.

Quick start:
    from subit_t import State, Op, Router, encode, build_prompt

    # Encode text
    result = encode("Review this code — I think there's a memory leak")
    print(result.current_state)  # SCAN
    print(result.operator)       # Op.ACT
    print(result.target_state)   # REFINER

    # Route
    router = Router()

    @router.on(state="REFINER")
    def refiner_agent(state, op, ctx):
        return {"action": "refine", "context": ctx}

    record = router.route_text("Review this code...")

    # Build prompt
    prompt = build_prompt(result.target_state, result.operator)
"""

from .canon import CANON, BY_NAME, WHO_LABEL, WHERE_LABEL, WHEN_LABEL
from .core import (
    State, Op, TransitionResult,
    S_PRIME, S_SYNC, S_SCAN, S_CORE,
    S_DRIVER, S_EXECUTOR, S_MONITOR, S_DAEMON, S_COUNCIL, S_GHOST, S_SENTINEL,
    validate_all_transitions,
)
from .encoder import encode, EncoderResult
from .router import Router
from .injector import build_prompt, build_minimal_prompt
from .guards import (
    guard_driver_sync, guard_executor_scan, guard_council_prime,
    guard_winter_collapse, make_guard, DEFAULT_GUARDS,
)

__version__ = "0.1.0"
__all__ = [
    # Core
    "State", "Op", "TransitionResult",
    # Constants
    "S_PRIME", "S_SYNC", "S_SCAN", "S_CORE",
    "S_DRIVER", "S_EXECUTOR", "S_MONITOR", "S_DAEMON", "S_COUNCIL", "S_GHOST", "S_SENTINEL",
    # Canon
    "CANON", "BY_NAME", "WHO_LABEL", "WHERE_LABEL", "WHEN_LABEL",
    # Encoder
    "encode", "EncoderResult",
    # Router
    "Router",
    # Injector
    "build_prompt", "build_minimal_prompt",
    # Guards
    "guard_driver_sync", "guard_executor_scan", "guard_council_prime",
    "guard_winter_collapse", "make_guard", "DEFAULT_GUARDS",
    # Validation
    "validate_all_transitions",
]

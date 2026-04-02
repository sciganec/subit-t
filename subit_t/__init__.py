"""
SUBIT-T - archetypal routing layer for multi-agent AI systems.

Quick start:
    from subit_t import State, Op, Router, encode, build_prompt

    result = encode("Review this code - I think there is a memory leak")
    router = Router()
"""

from .canon import CANON, BY_NAME, WHO_LABEL, WHAT_LABEL, WHEN_LABEL
from .core import (
    State,
    Op,
    TransitionResult,
    S_PRIME,
    S_SYNC,
    S_SCAN,
    S_CORE,
    S_DRIVER,
    S_EXECUTOR,
    S_MONITOR,
    S_DAEMON,
    S_COUNCIL,
    S_GHOST,
    S_SENTINEL,
    validate_all_transitions,
)
from .encoder import encode, EncoderResult
from .router import Router
from .kernel import Kernel, KernelSession
from .injector import build_prompt, build_minimal_prompt

__version__ = "0.4.0"

__all__ = [
    "State",
    "Op",
    "TransitionResult",
    "S_PRIME",
    "S_SYNC",
    "S_SCAN",
    "S_CORE",
    "S_DRIVER",
    "S_EXECUTOR",
    "S_MONITOR",
    "S_DAEMON",
    "S_COUNCIL",
    "S_GHOST",
    "S_SENTINEL",
    "CANON",
    "BY_NAME",
    "WHO_LABEL",
    "WHAT_LABEL",
    "WHEN_LABEL",
    "encode",
    "EncoderResult",
    "Router",
    "Kernel",
    "KernelSession",
    "build_prompt",
    "build_minimal_prompt",
    "build_minimal_prompt",
    "validate_all_transitions",
]

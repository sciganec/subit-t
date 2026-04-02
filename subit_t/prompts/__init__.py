"""Assistant prompt profiles layered on top of the core injector."""

from .profiles import (
    ASSISTANT_PROFILES,
    DEFAULT_ASSISTANT,
    build_assistant_extra,
    get_assistant_profile,
    list_assistants,
)

__all__ = [
    "ASSISTANT_PROFILES",
    "DEFAULT_ASSISTANT",
    "build_assistant_extra",
    "get_assistant_profile",
    "list_assistants",
]

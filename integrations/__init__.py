"""Integration shims for external agent frameworks."""

from .autogen import SubitGroupChatManager, SubitSpeakerSelector
from .langchain import SubitPromptTemplate, SubitRouter

__all__ = [
    "SubitGroupChatManager",
    "SubitSpeakerSelector",
    "SubitPromptTemplate",
    "SubitRouter",
]

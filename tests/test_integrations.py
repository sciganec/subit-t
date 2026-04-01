"""Smoke tests for integration shims that do not require optional deps."""

from subit_t.core import Op, State
from integrations.autogen import SubitSpeakerSelector
from integrations.langchain import SubitPromptTemplate, SubitRouter


class _StubAgent:
    def __init__(self, archetype: str):
        self.state = State.from_name(archetype)
        self.archetype = self.state.name


def test_langchain_prompt_template_format_returns_chat_messages():
    template = SubitPromptTemplate(minimal=False)
    messages = template.format(State.from_name("SCAN"), Op.WHAT_SHIFT, user_input="Review this code")
    assert messages[0]["role"] == "system"
    assert "ARCHETYPE" in messages[0]["content"]
    assert messages[1] == {"role": "user", "content": "Review this code"}


def test_langchain_router_route_returns_routing_payload():
    router = SubitRouter()
    record = router.route("Review this code and find the bug")
    assert "state" in record
    assert "operator" in record
    assert "prompt" in record
    assert record["operator"] in {op.value for op in Op}


def test_langchain_router_uses_explicit_start_state():
    router = SubitRouter(start_state=State.from_name("PRIME"))
    record = router.route("Review this code and find the bug")
    assert record["source_state"] == "PRIME"
    assert record["encoding"]["routed_from_state"]["name"] == "PRIME"


def test_autogen_selector_falls_back_to_who_what_match():
    agents = [_StubAgent("COUNCIL"), _StubAgent("ADAPTER"), _StubAgent("SCAN")]
    selector = SubitSpeakerSelector(agents)
    chosen = selector.select("Find recent information about the latest Python release and summarize it.")
    assert selector.group_state.name == "FILTER"
    assert chosen.archetype == "SCAN"


def test_autogen_selector_tracks_operator_history():
    agents = [_StubAgent("COUNCIL"), _StubAgent("ADAPTER"), _StubAgent("SCAN")]
    selector = SubitSpeakerSelector(agents)
    selector.select("Find recent information about the latest Python release and summarize it.")
    distribution = selector.op_distribution()
    assert distribution["INV"] == 1

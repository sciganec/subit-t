"""
SUBIT-T x AutoGen integration for v3 cyclic routing.
"""

from __future__ import annotations

from typing import Optional

from subit_t.core import State, Op
from subit_t.encoder import encode
from subit_t.injector import build_prompt
from subit_t.router import Router


def _require_autogen():
    try:
        import autogen
        return autogen
    except ImportError:
        raise ImportError(
            "AutoGen is required for this integration.\n"
            "Install with: pip install subit-t[autogen]"
        )


class SubitAgent:
    """AutoGen-compatible agent with a SUBIT-T state."""

    def __init__(
        self,
        name: str,
        initial_state: str | State = "PRIME",
        llm_config: Optional[dict] = None,
        human_input: str = "NEVER",
        verbose: bool = False,
        **kwargs,
    ):
        _require_autogen()
        import autogen

        self.state = State.from_name(initial_state) if isinstance(initial_state, str) else initial_state
        self.name = name
        self.verbose = verbose
        self._op = Op.WHEN_SHIFT

        self._agent = autogen.ConversableAgent(
            name=name,
            system_message=build_prompt(self.state, self._op),
            llm_config=llm_config or {},
            human_input_mode=human_input,
            **kwargs,
        )

    def transition(self, op: Op) -> State:
        transition = self.state.apply(op)
        self.state = transition.result
        self._op = op
        self._agent.update_system_message(build_prompt(self.state, op))

        if self.verbose:
            print(f"[{self.name}] {transition.source.name} {op.symbol}({op.value}) -> {transition.result.name}")

        return self.state

    def encode_and_transition(self, text: str) -> State:
        return self.transition(encode(text).operator)

    @property
    def archetype(self) -> str:
        return self.state.name

    @property
    def system_message(self) -> str:
        return self._agent.system_message

    @property
    def agent(self):
        return self._agent

    def __repr__(self) -> str:
        return f"SubitAgent({self.name} | {self.state.name} | {self.state.state_type})"


class SubitSpeakerSelector:
    """Selects the next speaker based on the encoded next-step transition."""

    def __init__(self, agents: list[SubitAgent]):
        self.agents = agents
        self.group_state = State.from_name("PRIME")
        self._history_router = Router()

    def select(self, last_message: str) -> SubitAgent:
        encoded = encode(last_message)
        record = self._history_router.route(self.group_state, encoded.operator, context={"text": last_message})
        transition = record["transition"]
        self.group_state = State(transition["result"]["bits"])

        for agent in self.agents:
            if agent.archetype == self.group_state.name:
                return agent

        for agent in self.agents:
            if agent.state.who == self.group_state.who and agent.state.what == self.group_state.what:
                return agent

        for agent in self.agents:
            if agent.state.who == self.group_state.who:
                return agent

        type_priority = {"core": 0, "transient": 1, "rare": 2, "unknown": 3}
        return min(self.agents, key=lambda agent: type_priority.get(agent.state.state_type, 3))

    @property
    def state(self) -> State:
        return self.group_state

    def op_distribution(self) -> dict:
        return self._history_router.op_distribution()


class SubitGroupChatManager:
    """AutoGen GroupChatManager with SUBIT-T speaker selection."""

    def __init__(
        self,
        agents: list[SubitAgent],
        llm_config: Optional[dict] = None,
        max_rounds: int = 10,
        verbose: bool = True,
    ):
        _require_autogen()
        import autogen

        self.agents = agents
        self.selector = SubitSpeakerSelector(agents)
        self.max_rounds = max_rounds
        self.verbose = verbose

        underlying_agents = [agent.agent for agent in agents]
        self._group_chat = autogen.GroupChat(
            agents=underlying_agents,
            messages=[],
            max_round=max_rounds,
            speaker_selection_method="auto",
        )
        self._manager = autogen.GroupChatManager(
            groupchat=self._group_chat,
            llm_config=llm_config or {},
        )

    def run(self, task: str, sender_agent: Optional[SubitAgent] = None) -> list[dict]:
        if sender_agent is None:
            sender_agent = self.agents[0]

        if self.verbose:
            encoded = encode(task)
            print(f"[SUBIT-T] Task encoded: {encoded.current_state.name} -> {encoded.operator.value} -> {encoded.target_state.name}")
            print(f"[SUBIT-T] Starting with: {sender_agent.name} ({sender_agent.archetype})")

        sender_agent.agent.initiate_chat(self._manager, message=task)
        return self._group_chat.messages

    @property
    def group_state(self) -> State:
        return self.selector.group_state

    def op_distribution(self) -> dict:
        return self.selector.op_distribution()

    def stuck_detection(self) -> dict:
        dist = self.op_distribution()
        total = sum(dist.values()) or 1
        return {
            "over_inv": dist.get("INV", 0) / total > 0.3,
            "who_heavy": dist.get("WHO_SHIFT", 0) / total > 0.6,
            "what_heavy": dist.get("WHAT_SHIFT", 0) / total > 0.6,
            "when_heavy": dist.get("WHEN_SHIFT", 0) / total > 0.6,
        }

"""
SUBIT-T Injector -> (State, Op) to system prompt.

Builds a structured system prompt that configures an LLM agent
to respond from a specific archetypal cognitive position.
"""

from __future__ import annotations

from .core import State, Op
from .canon import WHO_LABEL, WHAT_LABEL, WHEN_LABEL


_ARCHETYPE_ROLE: dict[str, str] = {
    "PRIME": "Initiator. Generates from scratch. First impulse, maximum creative space.",
    "AUTHOR": "Peak generator. Produces complete drafts at full capacity.",
    "DRAFTER": "Closing generator. Produces final version for handoff.",
    "SEED": "Dormant generator. Holds potential, not yet active.",
    "LAUNCHER": "Initiates execution. Translates plan into first concrete action.",
    "DRIVER": "Peak autonomous executor. Full speed, no blockers.",
    "CLOSER": "Closing executor. Finalizes and commits autonomous work.",
    "ENGINE": "Execution capacity on standby. Ready to run.",
    "PROBE": "Self-initiated analyzer. Scans own output for gaps.",
    "AUDITOR": "Peak self-analyzer. Full internal audit at maximum depth.",
    "REFINER": "Closing self-analyzer. Applies precision edits from critique.",
    "WATCHER": "Passive self-monitor. Observes without acting.",
    "LOGGER": "Context capturer. Records state for future reference.",
    "ARCHIVIST": "Peak archivist. Commits full context at maximum fidelity.",
    "INDEXER": "Closing archivist. Organizes and finalizes stored context.",
    "HERMIT": "Silent. Maximum autonomy, zero output.",
    "SPARK": "Collective ideation initiator. Opens group brainstorm.",
    "CHORUS": "Peak collective generator. All voices producing together.",
    "MERGE": "Collective synthesizer. Combines group outputs into one.",
    "POOL": "Collective generative reserve. Ready to activate.",
    "DEPLOY": "Collective launch initiator. Coordinates group execution start.",
    "SYNC": "Peak collective executor. Full team in flow state.",
    "COMMIT": "Collective closing executor. Group's final action.",
    "STANDBY": "Collective executor on hold. Waiting for signal.",
    "COUNCIL": "Collective analysis initiator. Opens group review.",
    "TRIBUNAL": "Peak collective analyzer. Full group critique in progress.",
    "VERDICT": "Collective closing judgment. Group's final assessment.",
    "QUORUM": "Collective analytical reserve. Waiting to deliberate.",
    "LEDGER": "Collective context capturer. Starts shared log.",
    "REGISTRY": "Peak collective archivist. Full shared state committed.",
    "DIGEST": "Collective closing archivist. Summarizes shared context.",
    "ORIGIN": "Shared root memory. Common source, collective base.",
    "RESPONDER": "Reactive generator. Generates in response to new input.",
    "ADAPTER": "Peak reactive generator. Adapts at full capacity.",
    "ECHO": "Closing reactive generator. Final answer to query.",
    "BUFFER": "Input holder. Receives and holds without processing.",
    "HANDLER": "Reactive executor. Initiates processing of external request.",
    "EXECUTOR": "Peak reactive executor. Processes at full capacity.",
    "RESOLVER": "Closing reactive executor. Completes the request loop.",
    "QUEUE": "Reactive executor on hold. Awaiting next trigger.",
    "INTAKE": "Reactive analyzer. First pass on incoming input.",
    "SCAN": "Peak reactive analyzer. Deep critique of external input.",
    "FILTER": "Closing reactive analyzer. Final validation of input.",
    "LISTENER": "Passive input receiver. Receives and holds without analysis.",
    "INTAKE_LOG": "Incoming context logger. Records session start.",
    "CACHE": "Active reactive cache. Stores external state.",
    "SNAPSHOT": "Closing reactive capture. Point-in-time state record.",
    "VOID": "Null interface. Disconnected reactive agent.",
    "GHOST": "Unexpected external impulse. Unanticipated input.",
    "ORACLE": "Peak meta-generator. System-level insight production.",
    "SIGNAL": "Closing meta-generator. Final system-level output.",
    "SHADOW": "Hidden latent capacity. Not yet activated.",
    "TRIGGER": "Meta-execution initiator. External activation signal.",
    "FORCE": "Peak meta-executor. Full systemic action.",
    "SWEEP": "Closing meta-executor. System cleanup.",
    "DAEMON": "Background process. Persistent, low-visibility.",
    "INSPECTOR": "Meta-analysis initiator. System-wide scan starts.",
    "MONITOR": "Peak meta-analyzer. Full system observability active.",
    "VALIDATOR": "Closing meta-analyzer. Final system validation gate.",
    "SENTINEL": "Passive meta-observer. Always watching, never acting.",
    "IMPRINT": "Meta-context initiator. System state capture begins.",
    "LEDGER_SYS": "Peak meta-archivist. Full system state committed.",
    "FOSSIL": "Immutable historical record. Closing meta-storage.",
    "CORE": "Ground state. Absolute source. Ready to re-initialize.",
}


def build_prompt(
    state: State,
    op: Op,
    user_input: str = "",
    extra: str = "",
) -> str:
    """Build a system prompt for an LLM agent in the given archetypal state."""
    role = _ARCHETYPE_ROLE.get(state.name, f"{state.who}.{state.what}.{state.when} agent")

    lines = [
        f"[ARCHETYPE: {state.name}]",
        f"WHO:      {state.who:<6}  -> {WHO_LABEL[state.who]}",
        f"WHAT:     {state.what:<9} -> {WHAT_LABEL[state.what]}",
        f"WHEN:     {state.when:<10} -> {WHEN_LABEL[state.when]}",
        f"OPERATOR: {op.symbol}({op.value}) -> {op.description}",
        "",
        f"Role: {role}",
        "",
        "Respond strictly from this cognitive position:",
        f"  - Perspective: {WHO_LABEL[state.who]}",
        f"  - Domain:      {WHAT_LABEL[state.what]}",
        f"  - Phase:       {WHEN_LABEL[state.when]}",
        "",
        "Keep response concise (2-4 sentences). Stay in character.",
    ]

    if extra:
        lines += ["", extra]

    if user_input:
        lines += ["", f"User input: {user_input}"]

    return "\n".join(lines)


def build_minimal_prompt(state: State, op: Op) -> str:
    """Compact one-line version for token-sensitive contexts."""
    return (
        f"You are a {state.name} agent "
        f"({WHO_LABEL[state.who]} / {WHAT_LABEL[state.what]} / {WHEN_LABEL[state.when]}). "
        f"Operator applied: {op.symbol}({op.value}) - {op.description}. "
        f"Respond from this position."
    )

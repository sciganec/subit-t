"""
SUBIT-T Kernel - autonomous execution loop.
Instruction Set Architecture (ISA) for cognitive cycles.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional, Any

from .core import State, Op
from .encoder import encode, EncoderResult
from .router import Router

logger = logging.getLogger(__name__)


@dataclass
class KernelSession:
    """Stateful container for an autonomous execution run."""
    task: str
    current_state: State
    history: list[dict] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    max_steps: int = 10
    step_count: int = 0
    done: bool = False


class Kernel:
    """
    Execution Kernel for SUBIT-T.
    
    This is the 'Engine' that drives transitions through a sequence of states
    to fulfil a task goal.
    """

    def __init__(self, router: Router):
        self.router = router

    def execute(
        self,
        task: str,
        initial_state: Optional[State] = None,
        max_steps: int = 6,
        model_assisted: bool = False,
    ) -> KernelSession:
        """
        Run the autonomous execution loop for a given task.
        
        Algorithm:
        1. Initialize state (via encoding or explicit start)
        2. LOOP:
           a. 'Fetch': Get context and encode current status
           b. 'Decode': Decide next operator toward target_state
           c. 'Execute': Apply operator and dispatch via Router
           d. 'Evaluate': Check if state or agent output signals completion
        """
        # 1. Initialize
        if initial_state:
            current_state = initial_state
        else:
            # Bootstrap via encoding
            res = encode(task, model_assisted=model_assisted)
            current_state = res.current_state

        session = KernelSession(task=task, current_state=current_state, max_steps=max_steps)

        logger.info(f"Kernel starting task: '{task}' | Initial State: {current_state}")

        # 2. The Loop
        while not session.done and session.step_count < session.max_steps:
            session.step_count += 1
            
            # a. Determine current intent/context
            # We use the encoder to determine what operator to apply to move closer to the goal
            context_text = f"Goal: {task}. Current progress: {session.history[-1]['agent_result'] if session.history else 'Just starting'}"
            
            # The encoder looks at the task and the current progress to find the next operator
            result = encode(
                text=task if session.step_count == 1 else context_text,
                model_assisted=model_assisted
            )

            # b. Get Operator (The 'Instruction')
            op = result.operator
            
            # c. Step Execution
            logger.debug(f"Step {session.step_count}: Applying {op} to {session.current_state}")
            
            # The Router handles 'apply' and 'dispatch' to agent
            # We pass session.metadata as the persistent context for the agents
            route_record = self.router.route(session.current_state, op, context=session.metadata)
            
            # d. Post-Step Update
            session.current_state = State(route_record["transition"]["result"]["bits"])
            session.history.append(route_record)
            
            # Merge agent updates into session metadata
            if route_record.get("agent_result") and isinstance(route_record["agent_result"], dict):
                res = route_record["agent_result"]
                # Update persistent session context
                session.metadata.update(res.get("updates", {}))
                
                # Check for completion signals
                if res.get("done") or res.get("task_complete"):
                    session.done = True
                    logger.info("Kernel received completion signal from agent.")
            
            # Heuristic Stop: Reaching Terminal States (e.g., GHOST, SENTINEL)
            if session.current_state.name in {"GHOST", "SENTINEL", "DAEMON"}:
                session.done = True
                logger.info(f"Kernel reached terminal state: {session.current_state.name}")

        if session.step_count >= session.max_steps:
            logger.warning(f"Kernel reached max_steps ({session.max_steps}) without completion.")

        return session

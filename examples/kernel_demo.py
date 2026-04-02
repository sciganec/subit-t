"""
SUBIT-T Execution Kernel Demo.
Shows the 'Cognitive Loop' in action.
"""

import logging
from subit_t import Router, Kernel, State, Op

# Setup logging to see the Kernel's thought process
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    # 1. Initialize the Router and Register 'Agents' (Instruction Handlers)
    router = Router()

    @router.on(state="SCAN")
    def scanner(state, op, ctx):
        print(f"--- [Agent: SCAN] Analyzing problem context...")
        return {"updates": {"analysis_done": True}, "agent_output": "Issue identified: memory leak in session handler."}

    @router.on(state="PRIME")
    def planner(state, op, ctx):
        print(f"--- [Agent: PRIME] Drafting a solution plan...")
        return {"updates": {"plan_ready": True}, "agent_output": "Fix proposed: implement weak references."}

    @router.on(state="DRIVER")
    def executor(state, op, ctx):
        print(f"--- [Agent: DRIVER] Executing the fix...")
        return {"updates": {"fix_applied": True}, "agent_output": "Patch applied successfully."}

    @router.on(state="MONITOR")
    def monitor(state, op, ctx):
        print(f"--- [Agent: MONITOR] Verifying results...")
        return {"done": True, "agent_output": "System stable. Task complete."}

    # 2. Create the Kernel
    kernel = Kernel(router)

    # 3. Define a complex task
    task = "Investigate the memory leak in the production logs, propose a fix, apply it, and verify the outcome."

    print(f"Starting Task: {task}\n")

    # 4. Execute the loop!
    # The kernel will bootstrap from the task text, and then iterate through states.
    session = kernel.execute(task, max_steps=10)

    # 5. Review the execution trace
    print("\n" + "="*40)
    print("Execution History (ISA Trace):")
    for i, step in enumerate(session.history):
        trans = step["transition"]
        print(f"Step {i+1}: {trans['source']['name']} --({trans['operator']})--> {trans['result']['name']}")
    
    print("="*40)
    if session.done:
        print("RESULT: Task completed successfully in autonomous loop.")
    else:
        print("RESULT: Kernel timed out or stopped early.")

if __name__ == "__main__":
    main()

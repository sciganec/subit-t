"""
SUBIT-T Example: Code Review Pipeline

Shows a full PRIME → LAUNCHER → CLOSER → COMMIT cycle
using operator-driven transitions.
"""

from subit_t import State, Op, Router, encode, build_prompt


def main():
    print("=" * 56)
    print("SUBIT-T — Code Review Pipeline Example")
    print("=" * 56)

    router = Router()

    # Register agents
    @router.on(state="LAUNCHER")
    def launcher_agent(state, op, ctx):
        return {"action": "start PR review", "files": ctx.get("files", [])}

    @router.on(state="SCAN")
    def scan_agent(state, op, ctx):
        return {"action": "deep code analysis", "focus": "bugs, perf, style"}

    @router.on(state="REFINER")
    def refiner_agent(state, op, ctx):
        return {"action": "apply fixes", "mode": "precision edits"}

    @router.on(state="COMMIT")
    def commit_agent(state, op, ctx):
        return {"action": "commit changes", "message": "fix: apply review suggestions"}

    # Run pipeline
    print("\n── Text-based routing ────────────────────────────────")
    texts = [
        "Let's start reviewing the authentication PR.",
        "Analyze the code — I see potential issues with the session handling.",
        "Apply the fixes from the review — precision edits only.",
        "Commit all changes and close the PR.",
    ]

    for text in texts:
        record = router.route_text(text, context={"files": ["auth.py", "session.py"]})
        enc = record["encoding"]
        tr  = record["transition"]
        print(f"\n  Input:    {text[:55]}...")
        print(f"  Current:  {enc['current_state']['name']} → Operator: {tr['operator']} → Next: {tr['result']['name']}")
        if record["agent_result"]:
            print(f"  Agent:    {record['agent_result']}")

    # Show operator chain
    print("\n── Operator chain ────────────────────────────────────")
    start = State.from_name("PROBE")
    ops   = [Op.EXPAND, Op.ACT, Op.MERGE]
    chain = router.chain(start, ops)
    print(f"  Start: {start}")
    for rec in chain:
        tr = rec["transition"]
        print(f"  {tr['source']['name']:12} {tr['symbol']}({tr['operator']:6}) → {tr['result']['name']}")

    # Show prompt injection
    print("\n── Prompt injection example ──────────────────────────")
    enc_result = encode("Analyze this code for security vulnerabilities")
    tr = enc_result.current_state.apply(enc_result.operator)
    prompt = build_prompt(tr.result, enc_result.operator, enc_result.current_state.name)
    print(prompt)

    # Observability
    print("\n── Observability ─────────────────────────────────────")
    print(f"  Op distribution: {router.op_distribution()}")
    print(f"  Stuck flags:     {router.stuck_detection()}")
    print(f"  Idempotent rate: {router.idempotent_rate():.1%}")
    print()


if __name__ == "__main__":
    main()

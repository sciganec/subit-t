"""
SUBIT-T example: code review pipeline with Ollama.

Setup:
    1. Install Ollama: https://ollama.com
    2. Run: ollama pull llama3.2
    3. Make sure Ollama is available on http://localhost:11434

Then run:
    python examples/code_review.py
"""

import requests

from subit_t import Router, build_prompt


def call_llm(system_prompt: str, user_input: str, model: str = "llama3.2") -> str:
    """Call a local Ollama model with a SUBIT-T system prompt."""
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        return "[Ollama not running - start it and try again]"
    except Exception as exc:
        return f"[Error: {exc}]"


def make_agent(router: Router, state_name: str) -> None:
    @router.on(state=state_name)
    def agent(state, op, ctx):
        user_input = ctx.get("text", "")
        system_prompt = build_prompt(state, op, user_input)
        response = call_llm(system_prompt, user_input)
        return {"state": state.name, "response": response}


def main():
    print("=" * 60)
    print("SUBIT-T - Code Review Pipeline (Ollama / llama3.2)")
    print("=" * 60)

    router = Router()

    for state_name in [
        "PROBE",
        "SCAN",
        "AUDITOR",
        "REFINER",
        "DRIVER",
        "LAUNCHER",
        "COMMIT",
        "COUNCIL",
        "SPARK",
        "TRIBUNAL",
        "VERDICT",
    ]:
        make_agent(router, state_name)

    def fallback(state, op, ctx):
        user_input = ctx.get("text", "")
        system_prompt = build_prompt(state, op, user_input)
        response = call_llm(system_prompt, user_input)
        return {"state": state.name, "response": response}

    router.register(fallback)

    pipeline = [
        "Let's start reviewing the authentication PR - it touches session handling.",
        "Analyze the code - I see potential issues with the token expiry logic.",
        "Apply the fixes from the review - precision edits only, do not refactor.",
        "Commit all changes and close the PR.",
    ]

    print("\n-- Pipeline ----------------------------------------")
    for text in pipeline:
        print(f"\n  Input:   {text[:60]}...")

        result = router.route_text(text, context={"text": text})
        enc = result["encoding"]
        transition = result["transition"]
        agent_result = result.get("agent_result") or {}

        print(
            f"  State:   {enc['current_state']['name']} "
            f"-> {transition['operator']}({transition['symbol']}) "
            f"-> {transition['result']['name']}"
        )

        response = agent_result.get("response", "")
        if response:
            print(f"\n  Agent [{transition['result']['name']}]:")
            for line in response.strip().split("\n"):
                print(f"    {line}")

    print("\n-- Observability -----------------------------------")
    print(f"  Op distribution: {router.op_distribution()}")
    print(f"  Stuck flags:     {router.stuck_detection()}")
    print(f"  Idempotent rate: {router.idempotent_rate():.1%}")


if __name__ == "__main__":
    main()

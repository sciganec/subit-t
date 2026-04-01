# SUBIT-T

Archetypal routing layer for multi-agent AI systems.

SUBIT-T v3 models the state space as:

`State ~= Z4 x Z4 x Z4`

with 64 states and 4 cyclic operators:

- `WHO_SHIFT`: rotate `THEY -> YOU -> ME -> WE -> THEY`
- `WHAT_SHIFT`: rotate `PRESERVE -> REDUCE -> EXPAND -> TRANSFORM -> PRESERVE`
- `WHEN_SHIFT`: rotate `RELEASE -> INTEGRATE -> INITIATE -> SUSTAIN -> RELEASE`
- `INV`: global rollback by `-1` on all three axes at once

This gives:

- zero idempotent transitions
- closed algebra with no edge states
- composable trajectories
- deterministic rollback

## Quick Start

```python
from subit_t import Router, encode, build_prompt

result = encode("Review this code - there is a memory leak")
print(result.current_state)   # SCAN
print(result.operator)        # Op.WHAT_SHIFT / Op.WHEN_SHIFT / ...
print(result.target_state)    # immediate next state

router = Router()

@router.on(state="SPARK")
def spark(state, op, ctx):
    prompt = build_prompt(state, op, ctx.get("text", ""))
    return {"prompt": prompt}

record = router.route_text("Let's start reviewing the authentication PR")
```

## Installation

```bash
pip install subit-t
```

For local development:

```bash
pip install -e .
```

## Architecture

```text
Text input
  -> Encoder
  -> current_state + next-step operator
  -> apply(state, op) -> next_state
  -> prompt injection
  -> LLM agent response
```

## CLI

Run the local CLI directly from the repo:

```bash
python -m subit_t.cli profile "Review this code"
python -m subit_t.cli ollama "Explain token refresh"
python -m subit_t.cli chat --fetch-pages 2 --show-sources
```

After editable install, the same commands are available through `subit`.

## Runtime Layout

- `subit_t/runtime/ollama.py`: local Ollama transport
- `subit_t/runtime/web.py`: web-search and page-fetch helpers
- `subit_t/runtime/chat.py`: interactive chat session loop

This keeps the algebra and router core separate from assistant-style workflows.

## Evaluation

The repository now includes a lightweight evaluation scaffold:

- `eval/gold.jsonl`: seed gold examples
- `eval/challenge.jsonl`: harder ambiguous prompts
- `eval/runner.py`: encoder evaluation runner

Run it with:

```bash
python eval/runner.py
python eval/runner.py --dataset eval/challenge.jsonl
```

## State Space

`State = WHO x WHAT x WHEN`

| Axis | Values | Meaning |
|------|--------|---------|
| WHO  | THEY / YOU / ME / WE | Orientation of attention |
| WHAT | PRESERVE / REDUCE / EXPAND / TRANSFORM | Operation on information |
| WHEN | RELEASE / INTEGRATE / INITIATE / SUSTAIN | Phase of the cycle |

## Operators

| Op | Axis | Effect |
|----|------|--------|
| `WHO_SHIFT` | WHO | move one step forward on WHO |
| `WHAT_SHIFT` | WHAT | move one step forward on WHAT |
| `WHEN_SHIFT` | WHEN | move one step forward on WHEN |
| `INV` | ALL | move one step backward on all axes |

Examples:

```python
from subit_t import State, Op

State.from_name("DRIVER").apply(Op.WHO_SHIFT).result.name  # SYNC
State.from_name("SYNC").apply(Op.INV).result.name          # PRIME
State.from_name("PRIME").apply(Op.WHAT_SHIFT).result.name  # LAUNCHER
```

## Observability

```python
router.op_distribution()   # {"WHAT_SHIFT": 3, "WHEN_SHIFT": 1}
router.stuck_detection()   # {"over_inv": False, "what_heavy": True, ...}
router.idempotent_rate()   # 0.0
```

## Compatibility

The package still accepts old dimension names in `State.from_dims(...)` for compatibility, but the primary model is `WHO + WHAT + WHEN`.

## License

MIT

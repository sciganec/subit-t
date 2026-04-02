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
- `webapp/`: React frontend for `SUBIT-T AI`, ready for GitHub Pages deployment

This keeps the algebra and router core separate from assistant-style workflows.

## SUBIT-T AI Web App

The repository also includes a React app in `webapp/` that turns `SUBIT-T` into a browser-based assistant UI.

Features:

- chat interface with visible `current_state -> operator -> next_state`
- bring-your-own API key
- OpenAI-compatible chat completion endpoint
- assistant modes: `general`, `review`, `research`, `incident`, `planner`, `coding`
- local settings stored in browser local storage

Run locally:

```bash
cd webapp
npm install
npm run dev
```

Build for production:

```bash
cd webapp
npm install
npm run build
```

Deploy:

- GitHub Pages workflow: `.github/workflows/deploy-webapp.yml`
- push changes under `webapp/` to `main`
- enable Pages in repository settings if needed

## Assistant Modes

`subit-t` can also act as a local assistant runtime over Ollama.

- `subit chat`: interactive multi-turn assistant loop
- `subit ollama "...":` single-shot assistant response
- `--assistant`: select a built-in assistant profile such as `general`, `review`, `research`, `incident`, `planner`, or `coding`

Examples:

```bash
python -m subit_t.cli chat --assistant coding
python -m subit_t.cli ollama "Review this rollout plan" --assistant review
python -m subit_t.cli ollama "What is the latest Python release?" --assistant research --web --fetch-pages 2
```

Assistant profiles are layered on top of the routed state prompt, so the model gets both:

- the `SUBIT-T` state/operator context
- task-specific behavior guidance

## Evaluation

The repository now includes a lightweight evaluation scaffold:

- `eval/gold.jsonl`: seed gold examples
- `eval/challenge.jsonl`: harder ambiguous prompts
- `eval/runner.py`: encoder evaluation runner

Run it with:

```bash
python eval/runner.py
python eval/runner.py --dataset eval/challenge.jsonl
python eval/runner.py --model-assisted --encoder-model llama3.2
```

The encoder also supports an optional hybrid path where local Ollama provides a structured routing hint. If the model hint is missing or malformed, `subit-t` falls back to deterministic heuristics.

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

## License

MIT

# SUBIT-T Technical Specification
Version 0.3.1

## 1. Overview

SUBIT-T is a routing layer for multi-agent systems built on a closed cyclic algebra.

```text
Text input
  -> Encoder
  -> current_state + next-step operator
  -> apply(state, op) -> next_state
  -> prompt injection
  -> LLM agent response
```

The active model is v3:

`State ~= Z4 x Z4 x Z4`

with:
- one 6-bit state
- three orthogonal axes
- four operators
- no idempotent transitions

## 2. State Space

`State = WHO x WHAT x WHEN`

Bit layout:

```text
[ b5 b4 | b3 b2 | b1 b0 ]
  WHO      WHAT    WHEN
```

Axis values:

| Axis | Order | Meaning |
|------|-------|---------|
| WHO | `THEY -> YOU -> ME -> WE` | orientation of attention |
| WHAT | `PRESERVE -> REDUCE -> EXPAND -> TRANSFORM` | operation on information |
| WHEN | `RELEASE -> INTEGRATE -> INITIATE -> SUSTAIN` | phase of the cycle |

## 3. Operators

| Operator | Effect |
|----------|--------|
| `WHO_SHIFT` | move one step forward on WHO |
| `WHAT_SHIFT` | move one step forward on WHAT |
| `WHEN_SHIFT` | move one step forward on WHEN |
| `INV` | move one step backward on all axes |

Examples:

```python
State.from_name("DRIVER").apply(Op.WHO_SHIFT).result.name  # SYNC
State.from_name("PRIME").apply(Op.WHAT_SHIFT).result.name  # LAUNCHER
State.from_name("SYNC").apply(Op.INV).result.name          # PRIME
```

## 4. Algebraic Properties

- Closure: every operation stays inside the 64-state space
- No dead ends: there are no terminal states
- No idempotence: every operator changes the state
- Period 4: four forward moves on one axis return to the origin
- Rollback: `INV` acts as a deterministic global reverse step
- Composability: trajectories can be planned by operator composition

## 5. Encoder

The encoder is a next-step selector, not a full target solver.

It returns:
- `current_state`: inferred current state
- `operator`: one v3 operator for the next move
- `target_state`: the immediate state after applying that operator

The encoder still exposes per-axis distributions for observability.

The default path is deterministic and heuristic-driven. The runtime can also enable an optional model-assisted path where a local Ollama model returns a structured routing hint. Invalid or missing hints do not change the safety contract: the encoder falls back to deterministic scoring.

## 6. Router

Routing remains:

```text
(state + op) -> state -> op -> fallback
```

Execution flow:

```python
enc = encode(text)
tr = enc.current_state.apply(enc.operator)
fn = registry[(tr.result, enc.operator)] or registry[tr.result] or registry[enc.operator] or fallback
```

## 7. Prompt Injection

`build_prompt(state, op, user_input)` produces a system prompt from the resulting state and applied operator.

The prompt layer now uses `WHAT` as the canonical axis name.

Assistant workflows can add a second instruction layer through built-in profiles such as `review`, `research`, `incident`, `planner`, and `coding`.

## 8. Observability

Router observability includes:
- operator distribution
- state distribution
- v3 skew flags such as `who_heavy`, `what_heavy`, `when_heavy`, `over_inv`
- idempotent rate, expected to be `0.0` in v3

The repository also includes an `eval/` harness with seed gold/challenge datasets and a runner for repeatable encoder checks.

## 9. Compatibility Layer

The codebase still keeps a limited compatibility layer:
- `State.from_dims(...)` accepts old `WHERE` and season names
- `state.where` remains as an alias to `state.what`
- XOR guards are preserved only for analysis of legacy behavior

The active routing law is no longer v1 XOR or v2 set-to-target mutation.
